const fs = require('fs');
const KEY = fs.readFileSync('key.txt', 'utf8').trim();
const BASE = `https://eth-mainnet.g.alchemy.com/nft/v3/${KEY}/getContractsForOwner`;
const OUT = 'holdings.json';
const CONCURRENCY = 3, DELAY_MS = 120, MAX_RETRY = 4;

const holders = JSON.parse(fs.readFileSync('holders.json', 'utf8'));
const targets = holders.filter(h => !h.isContract && !h.isScam);

let done = {};
if (fs.existsSync(OUT)) {
  try { done = JSON.parse(fs.readFileSync(OUT,'utf8'));
        console.log(`resuming — ${Object.keys(done).length} already fetched`); } catch(e){ done={}; }
}
const todo = targets.filter(h => !done[h.address.toLowerCase()]);
console.log(`${targets.length} real wallets | ${todo.length} left to fetch\n`);

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function fetchWallet(addr) {
  let out = [], pageKey = null;
  for (let page = 0; page < 10; page++) {
    let url = `${BASE}?owner=${addr}&pageSize=100&withMetadata=true`;
    if (pageKey) url += `&pageKey=${encodeURIComponent(pageKey)}`;
    let res, attempt = 0;
    while (attempt < MAX_RETRY) {
      try {
        res = await fetch(url);
        if (res.status === 429) { await sleep(700 * Math.pow(2, attempt)); attempt++; continue; }
        break;
      } catch (e) { await sleep(600 * Math.pow(2, attempt)); attempt++; }
    }
    if (!res || !res.ok) return out;
    const data = await res.json();
    for (const c of (data.contracts || [])) {
      out.push({ a:(c.address||'').toLowerCase(), n:c.name||c.symbol||null,
                 b:parseInt(c.totalBalance||c.numDistinctTokensOwned||1,10)||1 });
    }
    pageKey = data.pageKey;
    if (!pageKey) break;
  }
  return out;
}

let completed = 0, failed = 0;
const started = Date.now();
const saveNow = () => fs.writeFileSync(OUT, JSON.stringify(done));

async function worker(queue) {
  while (queue.length) {
    const h = queue.shift();
    const addr = h.address.toLowerCase();
    try {
      const cols = await fetchWallet(h.address);
      done[addr] = { ens:h.ens, hoodies:h.count, cols };
    } catch(e) { done[addr] = { ens:h.ens, hoodies:h.count, cols:[], err:true }; failed++; }
    completed++;
    if (completed % 25 === 0) {
      saveNow();
      const el = (Date.now()-started)/1000, rate = completed/el;
      const left = Math.round((todo.length-completed)/rate);
      console.log(`  ${completed}/${todo.length}  (${rate.toFixed(1)}/s, ~${Math.floor(left/60)}m ${left%60}s left)`);
    }
    await sleep(DELAY_MS);
  }
}

(async () => {
  const queue = [...todo];
  await Promise.all(Array.from({length:CONCURRENCY}, () => worker(queue)));
  saveNow();
  const wallets = Object.keys(done);
  const counts = {}; let totalCols = 0;
  for (const w of wallets) for (const c of (done[w].cols||[])) {
    counts[c.a] = counts[c.a] || { n:c.n, holders:0 };
    counts[c.a].holders++; totalCols++;
  }
  const top = Object.entries(counts).sort((a,b)=>b[1].holders-a[1].holders).slice(0,15);
  console.log(`\n=== done ===`);
  console.log(`wallets fetched : ${wallets.length}`);
  console.log(`failed          : ${failed}`);
  console.log(`unique collections: ${Object.keys(counts).length}`);
  console.log(`total holdings rows: ${totalCols}`);
  console.log(`\nmost common (these get low weight — everyone has them):`);
  for (const [addr,v] of top) console.log(`  ${String(v.holders).padStart(4)}  ${(v.n||addr).slice(0,44)}`);
  console.log(`\nsaved -> ${OUT}`);
})();
