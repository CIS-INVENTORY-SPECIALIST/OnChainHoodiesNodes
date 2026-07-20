import sys
p='hood.html'; s=open(p,encoding='utf-8').read(); o=s; hits=[]

# global velocityDecay stays at default — dragged node feels crisp again
s2=s.replace("      sim.velocityDecay(0.62);        // sluggish followers = visible trailing\n","",1)
if s2!=s: hits.append('removed global damping'); s=s2
s2=s.replace("      sim.velocityDecay(0.28);\n","",1)
if s2!=s: hits.append('removed damping reset'); s=s2

# mark direct neighbours of the dragged node so only THEY lag
s2=s.replace("      dragStart=Date.now();",
"""      dragStart=Date.now();
      lagSet=new Set();
      for(const l of links){
        if(l.source===e.subject) lagSet.add(l.target);
        else if(l.target===e.subject) lagSet.add(l.source);
      }""",1)
if s2!=s: hits.append('build lag set'); s=s2

s2=s.replace("      cv.style.cursor='grab';\n      // treat a quick press",
"      cv.style.cursor='grab';\n      lagSet=null;\n      // treat a quick press",1)
if s2!=s: hits.append('clear lag set'); s=s2

s2=s.replace("let dragStart=0,lastTap=0,lastNode=null;",
"let dragStart=0,lastTap=0,lastNode=null,lagSet=null;",1)
if s2!=s: hits.append('lagSet state'); s=s2

# per-tick: damp only the followers, leave the held node alone
s2=s.replace("  sim.on('tick',draw);",
"""  sim.on('tick',()=>{
    if(lagSet&&lagSet.size){
      for(const n of lagSet){ n.vx*=0.62; n.vy*=0.62; }   // trail behind
    }
    draw();
  });""",1)
if s2!=s: hits.append('per-node lag on tick'); s=s2

# a touch less global heat so the rest of the graph stays calm
s2=s.replace("sim.alphaTarget(0.55).restart(); // keep chasing the dragged node",
"sim.alphaTarget(0.42).restart();",1)
if s2!=s: hits.append('calmer alpha'); s=s2

if s==o: print('NOTHING CHANGED'); sys.exit(1)
open(p,'w',encoding='utf-8').write(s)
for h in hits: print('  + '+h)
print('patched ('+str(len(hits))+')')
