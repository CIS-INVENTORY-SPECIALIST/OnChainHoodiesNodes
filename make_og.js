// make_og.js — regenerate the social card from live graph data
// run after layer3/fixtok/cache_svgs so graph.json + img/ are current
const fs = require('fs');
const { chromium } = require('playwright');

const G = JSON.parse(fs.readFileSync('graph.json', 'utf8'));
const COLS = fs.existsSync('collections.json')
  ? JSON.parse(fs.readFileSync('collections.json', 'utf8')) : [];

// ---- live numbers ----
const wallets  = fs.existsSync('holders.json')
  ? JSON.parse(fs.readFileSync('holders.json','utf8')).length
  : G.nodes.reduce((a, n) => a + (n.wallets || 1), 0);
const entities = G.nodes.length;
const farms    = G.nodes.filter(n => n.wallets > 1).length;
const nf = n => n.toLocaleString('en-US');

// ---- hero: the logo hoodie ----
const heroSvg = fs.existsSync('logo.svg') ? fs.readFileSync('logo.svg', 'utf8') : null;

// ---- satellites: real hoodies from the most connected holders ----
const top = [...G.nodes]
  .filter(n => n.deg > 0 && n.token && fs.existsSync('img/' + n.token + '.svg'))
  .sort((a, b) => b.deg - a.deg)
  .slice(0, 60);

// deterministic golden-angle layout, kept clear of the copy column
function layout() {
  const out = [];
  let i = 0;
  for (const n of top) {
    const ring = out.length < 10 ? 0 : (out.length < 22 ? 1 : 2);
    const baseR = [210, 296, 380][ring];
    const ang = (i * 137.508) * Math.PI / 180;
    i++;
    const r = baseR + ((i * 37) % 60) - 30;
    const x = 380 + Math.cos(ang) * r * 1.30;
    const y = 315 + Math.sin(ang) * r * 0.86;
    if (x < 34 || x > 632 || y < 34 || y > 596) continue;   // 632 keeps copy clear
    out.push({
      x: +x.toFixed(1), y: +y.toFixed(1),
      s: +(12 + (n.hoodies > 4 ? 16 : n.hoodies * 3)).toFixed(1),
      o: +(0.45 + Math.min(n.deg, 60) / 90).toFixed(2),
      svg: fs.readFileSync('img/' + n.token + '.svg', 'utf8')
    });
    if (out.length >= 24) break;
  }
  return out;
}
const sats = layout();

const enc = s => 'data:image/svg+xml;base64,' + Buffer.from(s).toString('base64');

const satTags = sats.map(s =>
  `<img class="sat" src="${enc(s.svg)}" style="left:${s.x}px;top:${s.y}px;` +
  `width:${s.s}px;height:${s.s}px;opacity:${s.o};transform:translate(-50%,-50%)">`
).join('');

const html = `<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1200px;height:630px;background:#000;font-family:'Space Mono',monospace;
 color:#e8e8e8;overflow:hidden;position:relative}
canvas{position:absolute;inset:0}
.hero{position:absolute;left:380px;top:315px;transform:translate(-50%,-50%);
 width:172px;height:172px;image-rendering:pixelated;z-index:3;
 box-shadow:0 0 0 3px #ccff00, 0 0 60px rgba(204,255,0,.34)}
.sat{position:absolute;image-rendering:pixelated;z-index:2}
.txt{position:absolute;right:52px;top:0;bottom:0;width:470px;z-index:5;
 display:flex;flex-direction:column;justify-content:center;text-align:right}
.tag{font-size:11px;letter-spacing:4.5px;color:#6b7a1f}
h1{font-size:56px;line-height:.96;letter-spacing:-2.4px;color:#ccff00;font-weight:700;margin-top:12px}
h1 em{font-style:normal;color:#fff;display:block;font-size:27px;letter-spacing:-.6px;
 margin-top:12px;font-weight:400}
.sub{font-size:13px;color:#7d7d7d;margin-top:18px;line-height:1.75}
.stats{display:flex;gap:26px;justify-content:flex-end;margin-top:26px;
 border-top:1px solid #1c1c1c;padding-top:18px}
.st .n{font-size:26px;color:#ccff00;font-weight:700;letter-spacing:-1px}
.st .l{font-size:8.5px;letter-spacing:1.8px;color:#4f4f4f;margin-top:4px}
.foot{position:absolute;left:44px;bottom:30px;font-size:10px;letter-spacing:2.4px;
 color:#3d3d3d;z-index:5}
.foot b{color:#6b7a1f;font-weight:400}
</style></head><body>
<canvas id="c" width="1200" height="630"></canvas>
${heroSvg ? `<img class="hero" src="${enc(heroSvg)}">` : ''}
${satTags}
<div class="txt">
  <div class="tag">BUILT IN THE HOOD</div>
  <h1>HOOD NODES<em>who collects like you</em></h1>
  <div class="sub">every onchainhoodies holder mapped by what else they<br>
  collect. wallet farms resolved into single people.<br>refreshed hourly, straight from chain.</div>
  <div class="stats">
    <div class="st"><div class="n">${nf(wallets)}</div><div class="l">WALLETS</div></div>
    <div class="st"><div class="n">${nf(entities)}</div><div class="l">REAL ENTITIES</div></div>
    <div class="st"><div class="n">${farms}</div><div class="l">OPERATORS</div></div>
  </div>
</div>
<div class="foot">ONCHAINHOODIES <b>· HOLDER GRAPH</b></div>
<script>
const SATS=${JSON.stringify(sats.map(s => ({ x: s.x, y: s.y })))};
const c=document.getElementById('c'),x=c.getContext('2d');
const HX=380,HY=315;
x.lineCap='round';
for(const s of SATS){
  const g=x.createLinearGradient(HX,HY,s.x,s.y);
  g.addColorStop(0,'rgba(204,255,0,.66)');
  g.addColorStop(1,'rgba(204,255,0,.07)');
  x.strokeStyle=g; x.lineWidth=1.5;
  x.beginPath(); x.moveTo(HX,HY); x.lineTo(s.x,s.y); x.stroke();
}
x.strokeStyle='rgba(150,180,90,.20)'; x.lineWidth=.75;
for(let i=0;i<SATS.length;i++)for(let j=i+1;j<SATS.length;j++){
  const d=Math.hypot(SATS[i].x-SATS[j].x,SATS[i].y-SATS[j].y);
  if(d<125){x.beginPath();x.moveTo(SATS[i].x,SATS[i].y);x.lineTo(SATS[j].x,SATS[j].y);x.stroke();}
}
const v=x.createLinearGradient(480,0,720,0);
v.addColorStop(0,'rgba(0,0,0,0)'); v.addColorStop(.7,'rgba(0,0,0,.94)'); v.addColorStop(1,'#000');
x.fillStyle=v; x.fillRect(440,0,760,630);
</script></body></html>`;

fs.writeFileSync('.og.tmp.html', html);

(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 2 });
  await pg.goto('file://' + require('path').resolve('.og.tmp.html'));
  await pg.waitForTimeout(2200);
  await pg.screenshot({ path: 'og.png' });
  await b.close();
  fs.unlinkSync('.og.tmp.html');
  console.log(`og.png rebuilt — ${nf(wallets)} wallets / ${nf(entities)} entities / ${farms} operators / ${sats.length} real hoodies`);
})();
