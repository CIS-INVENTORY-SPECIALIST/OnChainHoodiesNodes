import sys
p='layer3_overlap.js'; s=open(p,encoding='utf-8').read(); o=s

anchor = "fs.writeFileSync('graph.json',JSON.stringify({nodes: nodes, edges: edges.slice(0, 15000)}));"
if anchor not in s:
    anchor = "fs.writeFileSync('graph.json',JSON.stringify({nodes:ND,edges:ED.slice(0,15000)}));"
if anchor not in s:
    import re
    m=re.search(r"fs\.writeFileSync\('graph\.json'[^\n]*\n", s)
    if not m: print('graph.json write not found'); sys.exit(1)
    anchor = m.group(0).rstrip('\n')

add = anchor + """

// collection -> entities index, for the collection lens
const colIndex = [];
for (const [addr, arr] of eidx) {
  if (arr.length < 3) continue;
  colIndex.push({ a: addr, n: names.get(addr) || addr.slice(0,10), k: arr.length, e: arr });
}
colIndex.sort((x,y) => y.k - x.k);
fs.writeFileSync('collections.json', JSON.stringify(colIndex));
console.log('collections index: ' + colIndex.length + ' collections held by 3+ entities');"""

s = s.replace(anchor, add, 1)
if s==o: print('NOTHING CHANGED'); sys.exit(1)
open(p,'w',encoding='utf-8').write(s)
print('layer3 now emits collections.json')
