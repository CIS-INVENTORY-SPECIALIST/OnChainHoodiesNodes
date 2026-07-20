import re, sys, io

p = 'hood.html'
s = open(p, encoding='utf-8').read()
orig = s

# ---------- 1. simulation: bouncier collide + never fully settle ----------
old_sim = """  const sim=d3.forceSimulation(nodes)
    .force('link',d3.forceLink(links).distance(d=>40*(1-d.w)+10).strength(d=>Math.min(d.w*1.7,.9)))
    .force('charge',d3.forceManyBody().strength(-34).distanceMax(380))
    .force('center',d3.forceCenter(W/2+110,H/2))
    .force('collide',d3.forceCollide(d=>rad(d)+2))
    .alphaDecay(0.015);"""

new_sim = """  const sim=d3.forceSimulation(nodes)
    .force('link',d3.forceLink(links).distance(d=>40*(1-d.w)+10).strength(d=>Math.min(d.w*1.7,.9)))
    .force('charge',d3.forceManyBody().strength(-34).distanceMax(380))
    .force('center',d3.forceCenter(W/2+110,H/2).strength(0.045))
    .force('collide',d3.forceCollide(d=>rad(d)+2.5).strength(1).iterations(3))
    .alphaDecay(0.015)
    .velocityDecay(0.28);

  // ambient float — never fully settles, gentle organic drift
  let drifting=true;
  sim.on('end',()=>{ if(drifting) sim.alphaTarget(0.012).restart(); });
  setTimeout(()=>{ sim.alphaTarget(0.012).restart(); },2600);
  setInterval(()=>{
    if(!drifting||dragging)return;
    for(const n of nodes){
      n.vx += (Math.random()-0.5)*0.22;
      n.vy += (Math.random()-0.5)*0.22;
    }
    sim.alpha(Math.max(sim.alpha(),0.02));
  },1400);"""

if old_sim in s:
    s = s.replace(old_sim, new_sim, 1)
    print('  + float + bounce')
else:
    print('  ! sim block not matched')

# ---------- 2. drag state var ----------
old_state = """  let tf=d3.zoomIdentity.translate(110,0),hi=null,neigh=new Set();
  d3.select(cv).call(d3.zoom().scaleExtent([.12,9]).on('zoom',e=>{tf=e.transform;draw();}));"""

new_state = """  let tf=d3.zoomIdentity.translate(110,0),hi=null,neigh=new Set(),dragging=false;

  function nodeAt(cx,cy){
    const x=(cx-tf.x)/tf.k, y=(cy-tf.y)/tf.k;
    let b=null,bd=1e9;
    for(const n of nodes){
      const dx=n.x-x, dy=n.y-y, d=dx*dx+dy*dy;
      if(d<bd && d<Math.pow(rad(n)+7,2)){bd=d;b=n;}
    }
    return b;
  }

  // zoom, but let drag win when the pointer is over a node
  const zoom=d3.zoom().scaleExtent([.12,9])
    .filter(e=>{
      if(e.type==='wheel')return true;
      return nodeAt(e.clientX,e.clientY)===null;
    })
    .on('zoom',e=>{tf=e.transform;draw();});
  d3.select(cv).call(zoom);

  // drag a node — its cluster lags behind and follows
  d3.select(cv).call(d3.drag()
    .subject(e=>nodeAt(e.sourceEvent.clientX,e.sourceEvent.clientY))
    .on('start',e=>{
      if(!e.subject)return;
      dragging=true;
      sim.alphaTarget(0.34).restart();
      e.subject.fx=e.subject.x;
      e.subject.fy=e.subject.y;
      cv.style.cursor='grabbing';
    })
    .on('drag',e=>{
      if(!e.subject)return;
      e.subject.fx=(e.x-tf.x)/tf.k;
      e.subject.fy=(e.y-tf.y)/tf.k;
    })
    .on('end',e=>{
      if(!e.subject)return;
      dragging=false;
      sim.alphaTarget(0.012);
      e.subject.fx=null;
      e.subject.fy=null;
      cv.style.cursor='grab';
    }));"""

if old_state in s:
    s = s.replace(old_state, new_state, 1)
    print('  + drag with cluster lag')
else:
    print('  ! state block not matched')

# ---------- 3. reuse nodeAt for hover; dblclick to open ----------
old_pick = """  function pick(ev){
    const x=(ev.clientX-tf.x)/tf.k,y=(ev.clientY-tf.y)/tf.k;
    let b=null,bd=1e9;
    for(const n of nodes){const dx=n.x-x,dy=n.y-y,d=dx*dx+dy*dy;
      if(d<bd&&d<Math.pow(rad(n)+6,2)){bd=d;b=n;}}
    return b;
  }"""
new_pick = """  const pick=ev=>nodeAt(ev.clientX,ev.clientY);"""

if old_pick in s:
    s = s.replace(old_pick, new_pick, 1)
    print('  + unified hit detection')
else:
    print('  ! pick block not matched')

old_click = """  cv.addEventListener('click',ev=>{
    const b=pick(ev);if(!b)return;
    window.open(b.fc?'https://warpcast.com/'+b.fc:'https://opensea.io/'+b.a,'_blank');
  });"""
new_click = """  cv.addEventListener('dblclick',ev=>{
    ev.preventDefault();
    const b=pick(ev);if(!b)return;
    window.open(b.fc?'https://warpcast.com/'+b.fc:'https://opensea.io/'+b.a,'_blank');
  });
  cv.addEventListener('dblclick',e=>e.stopPropagation(),true);"""

if old_click in s:
    s = s.replace(old_click, new_click, 1)
    print('  + dblclick to open profile')
else:
    print('  ! click block not matched')

# ---------- 4. don't fight the drag on hover ----------
s = s.replace("""  cv.addEventListener('mousemove',ev=>{
    const b=pick(ev);hi=b;""",
"""  cv.addEventListener('mousemove',ev=>{
    if(dragging){draw();return;}
    const b=pick(ev);hi=b;""",1)

# ---------- 5. legend copy ----------
s = s.replace('CLICK A NODE <b>= OPEN PROFILE</b>',
              'DRAG A NODE <b>= MOVE THE CLUSTER</b><br>DOUBLE-CLICK <b>= OPEN PROFILE</b>')

if s == orig:
    print('NOTHING CHANGED'); sys.exit(1)

open(p,'w',encoding='utf-8').write(s)
print('patched hood.html')
