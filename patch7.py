import sys
p='hood.html'; s=open(p,encoding='utf-8').read(); o=s; hits=[]

# ---------- 1. sidebar section ----------
old_sb = """  <div class="sec">
    <div class="sl"><i>03</i> / SAME OPERATOR</div>"""
new_sb = """  <div class="sec">
    <div class="sl"><i>03</i> / COLLECTIONS <span id="cct" style="float:right;color:#4a4a4a"></span></div>
    <input id="cq" placeholder="creep kids, pudgy, punks…" autocomplete="off">
    <div id="ch">click a collection to light up its holders</div>
    <div id="cols" style="max-height:250px;overflow-y:auto;margin-top:8px"></div>
  </div>

  <div class="sec">
    <div class="sl"><i>04</i> / SAME OPERATOR</div>"""
if old_sb in s: s=s.replace(old_sb,new_sb,1); hits.append('sidebar section')

# style the second input + hint like the first
s2=s.replace("#q{width:calc(100% - 32px);margin:0 16px;","#q,#cq{width:calc(100% - 32px);margin:0 16px;",1)
if s2!=s: hits.append('input style'); s=s2
s2=s.replace("#q:focus{border-color:var(--lime)}","#q:focus,#cq:focus{border-color:var(--lime)}",1)
if s2!=s: hits.append('focus style'); s=s2
s2=s.replace("#qh{padding:10px 16px 0;font-size:10px;color:var(--grey);line-height:1.7}",
"#qh,#ch{padding:10px 16px 0;font-size:10px;color:var(--grey);line-height:1.7}\n#cols::-webkit-scrollbar{width:4px}\n#cols::-webkit-scrollbar-thumb{background:#2a2a2a}\n.cl{display:flex;align-items:center;gap:8px;padding:5px 16px;cursor:pointer;font-size:10px}\n.cl:hover{background:#0c0c0c}\n.cl.on{background:#131600}\n.cl .cn{flex:1;color:#b8b8b8;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}\n.cl.on .cn{color:var(--lime)}\n.cl .ck{color:var(--grey);font-size:9px}",1)
if s2!=s: hits.append('list styles'); s=s2

# ---------- 2. load collections.json ----------
s2=s.replace("""Promise.all([
  fetch('graph.json').then(r=>r.json()),
  fetch('tokens.json').then(r=>r.json()).catch(()=>({owners:{},farcaster:{}}))
]).then(([G,T])=>{""",
"""Promise.all([
  fetch('graph.json').then(r=>r.json()),
  fetch('tokens.json').then(r=>r.json()).catch(()=>({owners:{},farcaster:{}})),
  fetch('collections.json').then(r=>r.json()).catch(()=>[])
]).then(([G,T,COLS])=>{""",1)
if s2!=s: hits.append('load collections'); s=s2

# ---------- 3. selection state + dim logic ----------
s2=s.replace("let dragStart=0,lastTap=0,lastNode=null,lagSet=null;",
"let dragStart=0,lastTap=0,lastNode=null,lagSet=null;\n  let selCol=null, colSet=new Set();",1)
if s2!=s: hits.append('selection state'); s=s2

s2=s.replace("""  function dim(n){
    if(selTribe&&n.tribe!==selTribe)return true;
    if(neigh.size&&!neigh.has(n.i)&&hi!==n)return true;
    return false;
  }""",
"""  function dim(n){
    if(colSet.size)return colSet.has(n.i)===false && hi!==n;
    if(selTribe&&n.tribe!==selTribe)return true;
    if(neigh.size&&!neigh.has(n.i)&&hi!==n)return true;
    return false;
  }""",1)
if s2!=s: hits.append('dim logic'); s=s2

# ---------- 4. render the list + search ----------
s2=s.replace("""  const farms=G.nodes.filter(n=>n.wallets>1)""",
"""  // ---- collection lens ----
  const cw=document.getElementById('cols'), chh=document.getElementById('ch');
  document.getElementById('cct').textContent=COLS.length.toLocaleString();
  const idOn=new Set(nodes.map(n=>n.i));

  function renderCols(list){
    cw.innerHTML='';
    list.slice(0,120).forEach(c=>{
      const d=document.createElement('div');
      d.className='cl'+(selCol===c.a?' on':'');
      const shown=c.e.filter(i=>idOn.has(i)).length;
      d.innerHTML='<span class="cn">'+c.n+'</span><span class="ck">'+shown+'</span>';
      d.onclick=()=>{
        if(selCol===c.a){ selCol=null; colSet=new Set();
          chh.textContent='click a collection to light up its holders'; }
        else {
          selCol=c.a; colSet=new Set(c.e.filter(i=>idOn.has(i)));
          chh.innerHTML='<span style="color:#ccff00">'+c.n+'</span> · '+
            colSet.size+' holders in the graph';
          selTribe=null; neigh=new Set();
          [...tw.children].forEach(x=>x.classList.remove('on'));
        }
        renderCols(list); draw();
      };
      cw.appendChild(d);
    });
  }
  renderCols(COLS);

  document.getElementById('cq').addEventListener('input',e=>{
    const q=e.target.value.toLowerCase().trim();
    renderCols(q?COLS.filter(c=>String(c.n).toLowerCase().includes(q)):COLS);
  });

  const farms=G.nodes.filter(n=>n.wallets>1)""",1)
if s2!=s: hits.append('collection lens'); s=s2

# ---------- 5. tribe click clears collection ----------
s2=s.replace("""    d.onclick=()=>{selTribe=selTribe===t?null:t;""",
"""    d.onclick=()=>{selCol=null;colSet=new Set();renderCols(COLS);
      chh.textContent='click a collection to light up its holders';
      selTribe=selTribe===t?null:t;""",1)
if s2!=s: hits.append('tribe clears collection'); s=s2

# tw must exist before renderCols references it — move tribe block ahead is already the case
if s==o: print('NOTHING CHANGED'); sys.exit(1)
open(p,'w',encoding='utf-8').write(s)
for h in hits: print('  + '+h)
print('patched hood.html ('+str(len(hits))+' changes)')
