import re,sys
p='hood.html'; s=open(p,encoding='utf-8').read(); o=s

start=s.find("  d3.select(cv).call(d3.drag()")
if start==-1: print('drag block not found'); sys.exit(1)
end=s.find("}));",start)
if end==-1: print('drag end not found'); sys.exit(1)
end+=4

new = """  d3.select(cv).call(d3.drag()
    .subject(e=>{
      const n=nodeAt(e.sourceEvent.clientX,e.sourceEvent.clientY);
      if(!n)return null;
      // hand d3 the node's position in SCREEN space so the cursor stays glued to it
      return {x:tf.applyX(n.x), y:tf.applyY(n.y), node:n};
    })
    .on('start',e=>{
      if(!e.subject)return;
      const n=e.subject.node;
      dragging=true; dragStart=Date.now();
      lagSet=new Set();
      for(const l of links){
        if(l.source===n) lagSet.add(l.target);
        else if(l.target===n) lagSet.add(l.source);
      }
      sim.alphaTarget(0.4).restart();
      n.fx=n.x; n.fy=n.y;
      cv.style.cursor='grabbing';
    })
    .on('drag',e=>{
      if(!e.subject)return;
      const n=e.subject.node;
      n.fx=tf.invertX(e.x);
      n.fy=tf.invertY(e.y);
    })
    .on('end',e=>{
      if(!e.subject)return;
      const n=e.subject.node;
      dragging=false; lagSet=null;
      sim.alphaTarget(0.012);
      n.fx=null; n.fy=null;
      cv.style.cursor='grab';
      if(Date.now()-dragStart<260){
        const now=Date.now();
        if(now-lastTap<340 && lastNode===n){
          window.open(n.fc?'https://warpcast.com/'+n.fc:'https://opensea.io/'+n.a,'_blank');
          lastTap=0; lastNode=null;
        } else { lastTap=now; lastNode=n; }
      }
    }));"""

s = s[:start] + new + s[end:]

# gentler trail on neighbours
s = s.replace("for(const n of lagSet){ n.vx*=0.62; n.vy*=0.62; }","for(const n of lagSet){ n.vx*=0.72; n.vy*=0.72; }",1)

if s==o: print('NOTHING CHANGED'); sys.exit(1)
open(p,'w',encoding='utf-8').write(s)
print('drag rewritten with screen-space subject + coordinate inversion')
