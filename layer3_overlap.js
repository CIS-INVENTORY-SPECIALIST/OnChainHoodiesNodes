const fs = require('fs');
const H = JSON.parse(fs.readFileSync('holdings.json', 'utf8'));
const CUR = new Set(JSON.parse(fs.readFileSync('holders.json','utf8')).map(h=>h.address.toLowerCase()));
const wallets = Object.keys(H).filter(a => CUR.has(a.toLowerCase()));
const N = wallets.length;
console.log('holdings: ' + Object.keys(H).length + ' wallets, ' + N + ' still hold hoodies');

const MIN_COLS = 6, MIN_HOLDERS = 2, MAX_HOLDERS = 300;
const SAME_OP_COS = 0.70, SAME_OP_SHARE = 6;
const MIN_SHARED = 3, MIN_COS = 0.09;

const DENY = new Set([
  '0x57f1887a8bf19b14fc0df6fd9b2acc9af147ea85',
  '0x0635513f179d50a207757e05759cbd106d7dfce8',
  '0xd4416b13d2b3a9abae7acd5d6c2bbdbe25686401'
]);
const DENY_NAME = /^(namewrapper|ens|ethereum name service|ten years of ethereum|mint\.fun|base, introduced|coingecko|youmio x opensea|opensea shared|unidentified|.*airdrop.*|.*free ?mint.*|.*claim.*|.*voucher.*|.*pass$)/i;

const names = new Map();
for (const w of wallets) for (const c of (H[w].cols || [])) if (c.n && !names.has(c.a)) names.set(c.a, c.n);

const vecs = wallets.map(w => {
  const out = new Set();
  for (const c of (H[w].cols || [])) {
    if (!c.a || DENY.has(c.a)) continue;
    if (c.n && DENY_NAME.test(c.n)) continue;
    out.add(c.a);
  }
  return out;
});
const eligible = vecs.map(v => v.size >= MIN_COLS);
console.log(N + ' wallets | ' + eligible.filter(Boolean).length + ' eligible (>=' + MIN_COLS + ' collections)');

const idx = new Map();
vecs.forEach((v, i) => { if (!eligible[i]) return; for (const a of v) { if (!idx.has(a)) idx.set(a, []); idx.get(a).push(i); } });

const idf = new Map();
for (const [a, arr] of idx) { const k = arr.length; if (k >= MIN_HOLDERS && k <= MAX_HOLDERS) idf.set(a, Math.log(N / k)); }
console.log(idx.size + ' collections | ' + idf.size + ' usable for linking');

const norm = new Array(N).fill(0);
for (const [a, arr] of idx) { const w = idf.get(a); if (!w) continue; for (const i of arr) norm[i] += w * w; }
for (let i = 0; i < N; i++) norm[i] = Math.sqrt(norm[i]) || 1;

const raw = new Map();
for (const [a, arr] of idx) {
  const w = idf.get(a); if (!w) continue;
  const w2 = w * w;
  for (let x = 0; x < arr.length; x++) for (let y = x + 1; y < arr.length; y++) {
    const s = arr[x], t = arr[y];
    const key = s < t ? s * 100000 + t : t * 100000 + s;
    const e = raw.get(key);
    if (e) { e.w += w2; e.n++; } else raw.set(key, { w: w2, n: 1 });
  }
}
console.log(raw.size.toLocaleString() + ' candidate pairs');

const parent = Array.from({ length: N }, (_, i) => i);
const find = x => { while (parent[x] !== x) { parent[x] = parent[parent[x]]; x = parent[x]; } return x; };
let sameOp = 0;
for (const [key, e] of raw) {
  const s = Math.floor(key / 100000), t = key % 100000;
  const cos = e.w / (norm[s] * norm[t]);
  if (cos >= SAME_OP_COS && e.n >= SAME_OP_SHARE) {
    const ra = find(s), rb = find(t);
    if (ra !== rb) { parent[ra] = rb; sameOp++; }
  }
}

const groups = new Map();
for (let i = 0; i < N; i++) { if (!eligible[i]) continue; const r = find(i); if (!groups.has(r)) groups.set(r, []); groups.get(r).push(i); }
const multi = [...groups.values()].filter(g => g.length > 1).sort((a, b) => b.length - a.length);
console.log('');
console.log('entity resolution: ' + sameOp + ' same-operator links -> ' + multi.length + ' multi-wallet entities');
multi.slice(0, 8).forEach((c, i) => {
  const h = c.reduce((s, x) => s + (H[wallets[x]].hoodies || 0), 0);
  console.log('  entity ' + (i + 1) + ': ' + c.length + ' wallets, ' + h + ' hoodies');
});
fs.writeFileSync('entities.json', JSON.stringify(multi.map(c => c.map(i => ({ a: wallets[i], hoodies: H[wallets[i]].hoodies, cols: vecs[i].size })))));

const ents = [];
for (const [root, members] of groups) {
  const cols = new Set(); let hoodies = 0, ens = null;
  for (const i of members) { for (const a of vecs[i]) cols.add(a); hoodies += H[wallets[i]].hoodies || 0; if (!ens && H[wallets[i]].ens) ens = H[wallets[i]].ens; }
  ents.push({ id: ents.length, ens, a: wallets[members[0]], wallets: members.length, hoodies, cols: [...cols] });
}
console.log('collapsed ' + eligible.filter(Boolean).length + ' wallets -> ' + ents.length + ' entities');

const eidx = new Map();
ents.forEach(e => { for (const a of e.cols) { if (!eidx.has(a)) eidx.set(a, []); eidx.get(a).push(e.id); } });
const eidf = new Map();
for (const [a, arr] of eidx) { const k = arr.length; if (k >= MIN_HOLDERS && k <= MAX_HOLDERS) eidf.set(a, Math.log(ents.length / k)); }
const enorm = new Array(ents.length).fill(0);
for (const [a, arr] of eidx) { const w = eidf.get(a); if (!w) continue; for (const i of arr) enorm[i] += w * w; }
for (let i = 0; i < ents.length; i++) enorm[i] = Math.sqrt(enorm[i]) || 1;

const eraw = new Map();
for (const [a, arr] of eidx) {
  const w = eidf.get(a); if (!w) continue;
  const w2 = w * w;
  for (let x = 0; x < arr.length; x++) for (let y = x + 1; y < arr.length; y++) {
    const s = arr[x], t = arr[y];
    const key = s < t ? s * 100000 + t : t * 100000 + s;
    const e = eraw.get(key);
    if (e) { e.w += w2; e.n++; } else eraw.set(key, { w: w2, n: 1 });
  }
}

const edges = [];
for (const [key, e] of eraw) {
  if (e.n < MIN_SHARED) continue;
  const s = Math.floor(key / 100000), t = key % 100000;
  const cos = e.w / (enorm[s] * enorm[t]);
  if (cos < MIN_COS) continue;
  edges.push({ s: s, t: t, w: +cos.toFixed(4), n: e.n });
}
edges.sort((a, b) => b.w - a.w);
console.log(edges.length.toLocaleString() + ' entity edges');

const deg = new Array(ents.length).fill(0), str = new Array(ents.length).fill(0);
for (const e of edges) { deg[e.s]++; deg[e.t]++; str[e.s] += e.w; str[e.t] += e.w; }

const tribe = new Array(ents.length).fill(null);
ents.forEach(e => {
  let best = null, bw = 0;
  for (const a of e.cols) { const w = eidf.get(a); if (w && eidx.get(a).length >= 6 && w > bw) { bw = w; best = a; } }
  tribe[e.id] = best ? (names.get(best) || best.slice(0, 10)) : null;
});

const nodes = ents.map(e => ({ i: e.id, a: e.a, ens: e.ens, wallets: e.wallets, hoodies: e.hoodies, cols: e.cols.length, deg: deg[e.id], str: +str[e.id].toFixed(3), tribe: tribe[e.id] }));
fs.writeFileSync('graph.json', JSON.stringify({ nodes: nodes, edges: edges.slice(0, 15000) }));

console.log('');
console.log('connected entities: ' + nodes.filter(n => n.deg > 0).length + ' / ' + nodes.length);
console.log('');
console.log('most connected entities:');
for (const n of [...nodes].sort((a, b) => b.deg - a.deg).slice(0, 12))
  console.log('  ' + String(n.deg).padStart(4) + ' links  ' + String(n.ens || n.a).slice(0, 28).padEnd(28) + ' ' + n.hoodies + 'h ' + String(n.cols).padStart(4) + 'c  ' + (n.tribe || ''));

const tc = {};
nodes.forEach(n => { if (n.tribe && n.deg > 0) tc[n.tribe] = (tc[n.tribe] || 0) + 1; });
console.log('');
console.log('largest tribes:');
Object.entries(tc).sort((a, b) => b[1] - a[1]).slice(0, 12).forEach(x => console.log('  ' + String(x[1]).padStart(3) + '  ' + x[0]));
console.log('');
console.log('saved -> graph.json, entities.json');
