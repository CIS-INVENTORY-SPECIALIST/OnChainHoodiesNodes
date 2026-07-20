import sys, re
p='hood.html'; s=open(p,encoding='utf-8').read(); o=s; hits=[]

BASE='https://cis-inventory-specialist.github.io/OnChainHoodiesNodes'

# ============ 1. HEAD: og tags, favicon, description ============
old_head='<title>THE HOOD · HOLDER GRAPH</title>'
new_head='''<title>Hood Nodes · OnChainHoodies Holder Graph</title>
<meta name="description" content="Every OnChainHoodies holder mapped by what else they collect. Wallet farms resolved into single entities. Refreshed hourly.">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Hood Nodes">
<meta property="og:title" content="Hood Nodes · who collects like you">
<meta property="og:description" content="1,808 wallets resolved into 608 real entities. Every OnChainHoodies holder mapped by shared collections. Built with the OCH API.">
<meta property="og:image" content="''' + BASE + '''/og.png">
<meta property="og:url" content="''' + BASE + '''/">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Hood Nodes · who collects like you">
<meta name="twitter:description" content="Every OnChainHoodies holder mapped by shared collections. Wallet farms resolved. Refreshed hourly.">
<meta name="twitter:image" content="''' + BASE + '''/og.png">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=\\'http://www.w3.org/2000/svg\\' viewBox=\\'0 0 32 32\\'%3E%3Crect width=\\'32\\' height=\\'32\\' fill=\\'%23000\\'/%3E%3Ccircle cx=\\'16\\' cy=\\'16\\' r=\\'6\\' fill=\\'%23ccff00\\'/%3E%3Ccircle cx=\\'6\\' cy=\\'8\\' r=\\'2.5\\' fill=\\'%23ccff00\\'/%3E%3Ccircle cx=\\'26\\' cy=\\'9\\' r=\\'2.5\\' fill=\\'%23ccff00\\'/%3E%3Ccircle cx=\\'7\\' cy=\\'25\\' r=\\'2.5\\' fill=\\'%23ccff00\\'/%3E%3Ccircle cx=\\'25\\' cy=\\'24\\' r=\\'2.5\\' fill=\\'%23ccff00\\'/%3E%3C/svg%3E">'''
if old_head in s: s=s.replace(old_head,new_head,1); hits.append('og tags + favicon')

# ============ 2. MOBILE + new UI css ============
old_css='#ld{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;\n  background:#000;z-index:50;color:var(--lime);font-size:11px;letter-spacing:3px}'
new_css='''#ld{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;
  background:#000;z-index:50;color:var(--lime);font-size:11px;letter-spacing:3px}

/* attribution */
.credit{position:fixed;bottom:14px;left:252px;font-size:9px;color:#3a3a3a;z-index:12;
  letter-spacing:.6px;line-height:1.9}
.credit a{color:#6b7a1f;text-decoration:none}
.credit a:hover{color:var(--lime)}
.stamp{color:#2e2e2e}

/* stats strip under the header */
.strip{position:fixed;top:52px;left:236px;right:0;height:34px;display:flex;align-items:center;
  gap:26px;padding:0 18px;background:rgba(0,0,0,.82);border-bottom:1px solid var(--line);
  z-index:14;font-size:10px;letter-spacing:1.2px;color:#4a4a4a;text-transform:uppercase;
  overflow-x:auto;white-space:nowrap}
.strip b{color:var(--lime);font-weight:400}
.strip .warn b{color:#ff5555}

/* neighbors modal */
.mask{position:fixed;inset:0;background:rgba(0,0,0,.86);z-index:60;display:none}
.mask.on{display:block}
.panel{position:fixed;top:6vh;left:50%;transform:translateX(-50%);width:min(920px,94vw);
  height:88vh;background:#050505;border:1px solid var(--lime);z-index:61;display:none;
  flex-direction:column}
.panel.on{display:flex}
.ph{display:flex;align-items:center;justify-content:space-between;padding:14px 18px;
  border-bottom:1px solid #1a1a1a;flex:none}
.ph h2{font-size:13px;color:var(--lime);letter-spacing:2px;font-weight:700}
.ph .who{font-size:10px;color:#5a5a5a;margin-top:4px;letter-spacing:.5px}
.px{background:none;border:1px solid #222;color:#777;padding:5px 12px;cursor:pointer;
  font-family:inherit;font-size:10px;letter-spacing:1px}
.px:hover{border-color:var(--lime);color:var(--lime)}
.pf{display:flex;gap:8px;padding:10px 18px;border-bottom:1px solid #131313;flex:none;
  align-items:center;flex-wrap:wrap}
.pf input{flex:1;min-width:150px;background:#0a0a0a;border:1px solid #1e1e1e;color:#e8e8e8;
  padding:7px 10px;font-family:inherit;font-size:10px;outline:none}
.pf input:focus{border-color:var(--lime)}
.chip{background:#0a0a0a;border:1px solid #1e1e1e;color:#666;padding:6px 10px;cursor:pointer;
  font-size:9px;letter-spacing:1px;text-transform:uppercase}
.chip.on{border-color:var(--lime);color:var(--lime);background:#131600}
.pt{flex:1;overflow-y:auto}
.pt::-webkit-scrollbar{width:6px}
.pt::-webkit-scrollbar-thumb{background:#222}
table{width:100%;border-collapse:collapse;font-size:10px}
thead th{position:sticky;top:0;background:#080808;color:#5a5a5a;text-align:left;
  padding:9px 10px;font-weight:400;letter-spacing:1px;text-transform:uppercase;
  border-bottom:1px solid #1a1a1a;cursor:pointer;user-select:none;font-size:9px}
thead th:hover{color:var(--lime)}
thead th.s{color:var(--lime)}
tbody td{padding:8px 10px;border-bottom:1px solid #0f0f0f;color:#b0b0b0}
tbody tr{cursor:pointer}
tbody tr:hover{background:#0c0c0c}
tbody tr:hover td{color:#e8e8e8}
td.id{color:var(--lime)}
td.n{text-align:right;font-variant-numeric:tabular-nums}
.hz{width:22px;height:22px;image-rendering:pixelated;display:block;background:#000}
.bar{display:inline-block;height:4px;background:var(--lime);vertical-align:middle;
  margin-right:6px;min-width:2px}
.fcb{color:#8a63d2}
.pfoot{padding:9px 18px;border-top:1px solid #1a1a1a;font-size:9px;color:#3a3a3a;
  letter-spacing:1px;flex:none;display:flex;justify-content:space-between}

/* mobile */
#mtog{display:none;position:fixed;bottom:16px;left:16px;z-index:30;background:var(--lime);
  color:#000;border:none;padding:11px 16px;font-family:inherit;font-size:11px;font-weight:700;
  letter-spacing:1px;cursor:pointer}
@media (max-width:760px){
  .sb{transform:translateX(-100%);transition:transform .22s ease;width:88vw;max-width:300px;
    box-shadow:0 0 40px rgba(0,0,0,.9)}
  .sb.open{transform:translateX(0)}
  .strip{left:0;gap:16px;font-size:9px}
  .credit{left:16px;bottom:56px}
  .lgd{display:none}
  #mtog{display:block}
  .hd .rt{display:none}
  .hd .lg{font-size:13px}
  .panel{top:0;left:0;transform:none;width:100vw;height:100vh}
}'''
if old_css in s: s=s.replace(old_css,new_css,1); hits.append('mobile + panel css')

# ============ 3. MARKUP: strip, credit, toggle, modal ============
old_m='<div id="tip"></div>'
new_m='''<div id="tip"></div>

<div class="strip">
  <div><b id="k1">—</b> WALLETS</div>
  <div><b id="k2">—</b> REAL ENTITIES</div>
  <div class="warn"><b id="k3">—</b> MULTI-WALLET OPERATORS</div>
  <div><b id="k4">—</b> COLLECTIONS MAPPED</div>
  <div><b id="k5">—</b> AFFINITY LINKS</div>
</div>

<div class="credit">
  BUILT BY <a href="https://x.com/Tenfin9erz" target="_blank">@Tenfin9erz</a>
  &nbsp;·&nbsp; DATA FROM <a href="https://www.onchainhoodies.xyz/api" target="_blank">ONCHAINHOODIES API</a>
  &nbsp;·&nbsp; <a href="https://github.com/CIS-INVENTORY-SPECIALIST/OnChainHoodiesNodes" target="_blank">SOURCE</a>
  <br><span class="stamp" id="stamp"></span>
</div>

<button id="mtog">☰ PANEL</button>

<div class="mask" id="mask"></div>
<div class="panel" id="panel">
  <div class="ph">
    <div><h2>YOUR NEIGHBORS</h2><div class="who" id="pwho"></div></div>
    <button class="px" id="pclose">CLOSE</button>
  </div>
  <div class="pf">
    <input id="pq" placeholder="filter by ens, address, tribe…">
    <button class="chip" id="cfc">HAS FARCASTER</button>
    <button class="chip" id="cwh">2+ HOODIES</button>
  </div>
  <div class="pt"><table>
    <thead><tr>
      <th style="width:34px"></th>
      <th data-k="name">HOLDER</th>
      <th data-k="w" class="n">MATCH</th>
      <th data-k="n" class="n">SHARED</th>
      <th data-k="hoodies" class="n">HOODIES</th>
      <th data-k="cols" class="n">COLLECTIONS</th>
      <th data-k="tribe">TRIBE</th>
      <th style="width:70px">LINK</th>
    </tr></thead>
    <tbody id="ptb"></tbody>
  </table></div>
  <div class="pfoot"><span id="pcount"></span><span>CLICK A ROW TO OPEN THEIR PROFILE</span></div>
</div>'''
if old_m in s: s=s.replace(old_m,new_m,1); hits.append('strip + credit + modal markup')

# ============ 4. loading screen waits for real data ============
s2=s.replace("  setTimeout(()=>document.getElementById('ld').style.display='none',900);",
"  document.getElementById('ld').style.display='none';",1)
if s2!=s: hits.append('loading tied to data'); s=s2

# ============ 5. populate the strip ============
s2=s.replace("""  document.getElementById('s1').textContent='1,699';""",
"""  const totalWallets=G.nodes.reduce((a,n)=>a+(n.wallets||1),0);
  document.getElementById('k1').textContent=totalWallets.toLocaleString();
  document.getElementById('k2').textContent=G.nodes.length.toLocaleString();
  document.getElementById('k3').textContent=G.nodes.filter(n=>n.wallets>1).length;
  document.getElementById('k4').textContent=(COLS.length||0).toLocaleString();
  document.getElementById('k5').textContent=links.length.toLocaleString();
  if(G.built){
    const mins=Math.round((Date.now()-G.built)/60000);
    document.getElementById('stamp').textContent=
      'UPDATED '+(mins<60?mins+'M AGO':Math.round(mins/60)+'H AGO')+' · REFRESHES HOURLY';
  } else {
    document.getElementById('stamp').textContent='REFRESHES HOURLY';
  }
  document.getElementById('s1').textContent=totalWallets.toLocaleString();""",1)
if s2!=s: hits.append('stats strip'); s=s2

# ============ 6. mobile sidebar toggle ============
s2=s.replace("  sim.on('tick',()=>{",
"""  const sbEl=document.querySelector('.sb');
  document.getElementById('mtog').onclick=()=>sbEl.classList.toggle('open');
  cv.addEventListener('touchstart',()=>sbEl.classList.remove('open'));

  sim.on('tick',()=>{""",1)
if s2!=s: hits.append('mobile toggle'); s=s2

# ============ 7. neighbors panel logic ============
s2=s.replace("""  const nbs=document.getElementById('nbs'),qh=document.getElementById('qh');""",
"""  // ---------- neighbors panel ----------
  const mask=document.getElementById('mask'),panel=document.getElementById('panel'),
        ptb=document.getElementById('ptb'),pwho=document.getElementById('pwho'),
        pq=document.getElementById('pq'),pcount=document.getElementById('pcount');
  let panelRows=[],sortK='w',sortDir=-1,fFc=false,fWh=false;

  function openPanel(me){
    const rows=links.filter(l=>l.source===me||l.target===me).map(l=>{
      const o=l.source===me?l.target:l.source;
      return {o:o,w:l.w,n:l.n,name:(o.ens||o.a),hoodies:o.hoodies,cols:o.cols,tribe:o.tribe||''};
    });
    panelRows=rows;
    pwho.innerHTML=(me.ens||me.a.slice(0,14)+'…'+me.a.slice(-4))+
      ' · '+me.hoodies+' hoodies · '+me.cols+' collections · '+rows.length+' neighbors';
    renderPanel();
    mask.classList.add('on');panel.classList.add('on');
  }
  function closePanel(){mask.classList.remove('on');panel.classList.remove('on');}
  document.getElementById('pclose').onclick=closePanel;
  mask.onclick=closePanel;
  addEventListener('keydown',e=>{if(e.key==='Escape')closePanel();});

  function renderPanel(){
    const q=pq.value.toLowerCase().trim();
    let rows=panelRows.filter(r=>{
      if(fFc&&!r.o.fc)return false;
      if(fWh&&r.hoodies<2)return false;
      if(!q)return true;
      return String(r.name).toLowerCase().includes(q)||
             String(r.tribe).toLowerCase().includes(q)||
             r.o.a.toLowerCase().includes(q);
    });
    rows.sort((a,b)=>{
      const A=sortK==='name'||sortK==='tribe'?String(a[sortK]).toLowerCase():a[sortK];
      const B=sortK==='name'||sortK==='tribe'?String(b[sortK]).toLowerCase():b[sortK];
      return A<B?sortDir:A>B?-sortDir:0;
    });
    ptb.innerHTML=rows.map(r=>{
      const img=r.o.token?'<img class="hz" src="img/'+r.o.token+'.svg">':'';
      const nm=r.o.ens?r.o.ens:(r.o.a.slice(0,10)+'…'+r.o.a.slice(-4));
      const pct=Math.round(r.w*100);
      return '<tr data-a="'+r.o.a+'" data-fc="'+(r.o.fc||'')+'">'+
        '<td>'+img+'</td>'+
        '<td class="id">'+nm+'</td>'+
        '<td class="n"><span class="bar" style="width:'+Math.max(2,pct*0.5)+'px"></span>'+pct+'%</td>'+
        '<td class="n">'+r.n+'</td>'+
        '<td class="n">'+r.hoodies+'</td>'+
        '<td class="n">'+r.cols+'</td>'+
        '<td>'+(r.tribe||'—')+'</td>'+
        '<td>'+(r.o.fc?'<span class="fcb">farcaster</span>':'opensea')+'</td>'+
      '</tr>';
    }).join('');
    pcount.textContent=rows.length+' OF '+panelRows.length+' NEIGHBORS';
    [...ptb.querySelectorAll('tr')].forEach(tr=>{
      tr.onclick=()=>{const fc=tr.dataset.fc;
        window.open(fc?'https://warpcast.com/'+fc:'https://opensea.io/'+tr.dataset.a,'_blank');};
    });
  }
  pq.addEventListener('input',renderPanel);
  document.getElementById('cfc').onclick=function(){fFc=!fFc;this.classList.toggle('on');renderPanel();};
  document.getElementById('cwh').onclick=function(){fWh=!fWh;this.classList.toggle('on');renderPanel();};
  [...document.querySelectorAll('thead th[data-k]')].forEach(th=>{
    th.onclick=()=>{
      const k=th.dataset.k;
      if(sortK===k)sortDir=-sortDir;else{sortK=k;sortDir=-1;}
      document.querySelectorAll('thead th').forEach(x=>x.classList.remove('s'));
      th.classList.add('s');
      renderPanel();
    };
  });

  const nbs=document.getElementById('nbs'),qh=document.getElementById('qh');""",1)
if s2!=s: hits.append('neighbors panel'); s=s2

# ============ 8. "view all" button after a search ============
s2=s.replace("""    qh.innerHTML='<span style="color:#ccff00">'+(me.ens||me.a.slice(0,10)+'…')+'</span> · '+
      me.hoodies+' hoodies · '+me.deg+' neighbors';""",
"""    qh.innerHTML='<span style="color:#ccff00">'+(me.ens||me.a.slice(0,10)+'…')+'</span> · '+
      me.hoodies+' hoodies · '+me.deg+' neighbors'+
      '<br><span id="viewall" style="color:#ccff00;cursor:pointer;text-decoration:underline">'+
      'open full neighbor list →</span>';
    setTimeout(()=>{const va=document.getElementById('viewall');
      if(va)va.onclick=()=>openPanel(me);},0);""",1)
if s2!=s: hits.append('view-all trigger'); s=s2

# ============ 9. legend copy ============
s=s.replace('DOUBLE-TAP A NODE <b>= OPEN PROFILE</b>','DOUBLE-TAP A NODE <b>= OPEN PROFILE</b><br>SEARCH YOURSELF <b>= FULL NEIGHBOR LIST</b>')

if s==o: print('NOTHING CHANGED'); sys.exit(1)
open(p,'w',encoding='utf-8').write(s)
for h in hits: print('  + '+h)
print('patched hood.html ('+str(len(hits))+' changes)')
