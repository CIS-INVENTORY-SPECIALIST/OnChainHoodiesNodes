import sys

p = 'hood.html'
s = open(p, encoding='utf-8').read()
orig = s
hits = []

# ---------------- 1. slower, trailing cluster follow ----------------
s2 = s.replace(""".on('start',e=>{
      if(!e.subject)return;
      dragging=true;
      sim.alphaTarget(0.34).restart();""",
""".on('start',e=>{
      if(!e.subject)return;
      dragging=true;
      sim.velocityDecay(0.62);        // sluggish followers = visible trailing
      sim.alphaTarget(0.55).restart(); // keep chasing the dragged node
      dragStart=Date.now();""",1)
if s2!=s: hits.append('drag lag'); s=s2

s2 = s.replace(""".on('end',e=>{
      if(!e.subject)return;
      dragging=false;
      sim.alphaTarget(0.012);
      e.subject.fx=null;
      e.subject.fy=null;
      cv.style.cursor='grab';
    }));""",
""".on('end',e=>{
      if(!e.subject)return;
      dragging=false;
      sim.velocityDecay(0.28);
      sim.alphaTarget(0.012);
      e.subject.fx=null;
      e.subject.fy=null;
      cv.style.cursor='grab';
      // treat a quick press with no movement as a click
      if(Date.now()-dragStart<260){
        const now=Date.now();
        if(now-lastTap<340 && lastNode===e.subject){
          window.open(e.subject.fc?'https://warpcast.com/'+e.subject.fc
                                  :'https://opensea.io/'+e.subject.a,'_blank');
          lastTap=0; lastNode=null;
        } else { lastTap=now; lastNode=e.subject; }
      }
    }));""",1)
if s2!=s: hits.append('dblclick via drag-end'); s=s2

# state vars for tap tracking
s2 = s.replace("let tf=d3.zoomIdentity.translate(110,0),hi=null,neigh=new Set(),dragging=false;",
"let tf=d3.zoomIdentity.translate(110,0),hi=null,neigh=new Set(),dragging=false;\n  let dragStart=0,lastTap=0,lastNode=null;",1)
if s2!=s: hits.append('tap state'); s=s2

# kill d3's own dblclick-zoom, and the old broken listeners
s2 = s.replace("  d3.select(cv).call(zoom);",
"  d3.select(cv).call(zoom).on('dblclick.zoom',null);",1)
if s2!=s: hits.append('disable dblclick-zoom'); s=s2

s2 = s.replace("""  cv.addEventListener('dblclick',ev=>{
    ev.preventDefault();
    const b=pick(ev);if(!b)return;
    window.open(b.fc?'https://warpcast.com/'+b.fc:'https://opensea.io/'+b.a,'_blank');
  });
  cv.addEventListener('dblclick',e=>e.stopPropagation(),true);""",
"""  cv.addEventListener('dblclick',e=>e.preventDefault());""",1)
if s2!=s: hits.append('remove old dblclick'); s=s2

# ---------------- 2. zoom floor so sprites never degrade to circles ----------------
s2 = s.replace("const zoom=d3.zoom().scaleExtent([.12,9])","const zoom=d3.zoom().scaleExtent([.58,9])",1)
if s2!=s: hits.append('zoom floor 0.58'); s=s2

# ---------------- 3. full scrollable tribe list ----------------
s2 = s.replace("const tribes=Object.entries(tc).sort((a,b)=>b[1]-a[1]).slice(0,18).map(x=>x[0]);",
"const tribes=Object.entries(tc).sort((a,b)=>b[1]-a[1]).map(x=>x[0]);",1)
if s2!=s: hits.append('all tribes'); s=s2

s2 = s.replace("const pal=d3.quantize(d3.interpolateRainbow,Math.max(3,tribes.length));",
"const pal=d3.quantize(d3.interpolateRainbow,Math.max(3,Math.min(tribes.length,32)));",1)
if s2!=s: hits.append('palette cap'); s=s2

s2 = s.replace("const cOf=n=>{const i=tribes.indexOf(n.tribe);return i<0?'#333':pal[i];};",
"const cOf=n=>{const i=tribes.indexOf(n.tribe);return i<0?'#333':pal[i%pal.length];};",1)
if s2!=s: hits.append('color wrap'); s=s2

s2 = s.replace("d.innerHTML='<span class=\"dot\" style=\"background:'+pal[i]+'\"></span>'+",
"d.innerHTML='<span class=\"dot\" style=\"background:'+pal[i%pal.length]+'\"></span>'+",1)
if s2!=s: hits.append('swatch wrap'); s=s2

# scrollable tribe container + count in the header
s2 = s.replace("""    <div class="sl"><i>02</i> / TRIBES</div>
    <div id="tribes"></div>""",
"""    <div class="sl"><i>02</i> / TRIBES <span id="tct" style="float:right;color:#4a4a4a"></span></div>
    <div id="tribes" style="max-height:290px;overflow-y:auto"></div>""",1)
if s2!=s: hits.append('scrollable tribes'); s=s2

s2 = s.replace("""  const tw=document.getElementById('tribes');""",
"""  const tw=document.getElementById('tribes');
  document.getElementById('tct').textContent=tribes.length;""",1)
if s2!=s: hits.append('tribe count'); s=s2

# scrollbar styling for the inner list
s2 = s.replace(".sb::-webkit-scrollbar{width:5px}",
"#tribes::-webkit-scrollbar{width:4px}\n#tribes::-webkit-scrollbar-thumb{background:#2a2a2a}\n.sb::-webkit-scrollbar{width:5px}",1)
if s2!=s: hits.append('scrollbar style'); s=s2

# ---------------- 4. legend copy ----------------
s = s.replace('DOUBLE-CLICK <b>= OPEN PROFILE</b>','DOUBLE-TAP A NODE <b>= OPEN PROFILE</b>')

if s == orig:
    print('NOTHING CHANGED'); sys.exit(1)

open(p,'w',encoding='utf-8').write(s)
for h in hits: print('  + '+h)
print('patched hood.html ('+str(len(hits))+' changes)')
