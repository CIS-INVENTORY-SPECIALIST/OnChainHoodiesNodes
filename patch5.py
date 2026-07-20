import sys
p='hood.html'; s=open(p,encoding='utf-8').read(); o=s
s=s.replace("""  cv.addEventListener('mousemove',ev=>{
    if(dragging){draw();return;}""",
"""  cv.addEventListener('mousemove',ev=>{
    if(dragging){
      tip.style.left=Math.min(ev.clientX+14,W-210)+'px';
      tip.style.top=Math.min(ev.clientY+14,H-160)+'px';
      draw();return;
    }""",1)
if s==o: print('no match'); sys.exit(1)
open(p,'w',encoding='utf-8').write(s)
print('tooltip now follows the drag')
