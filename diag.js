const fs=require('fs');
const G=JSON.parse(fs.readFileSync('graph.json','utf8'));
const T=JSON.parse(fs.readFileSync('tokens.json','utf8'));
let has=0,no=0,missing=0,sample=[];
for(const n of G.nodes){
  if(n.deg===0)continue;
  const o=T.owners[n.a.toLowerCase()];
  if(o&&o.ids&&o.ids.length){
    has++;
    if(fs.existsSync('img/'+o.ids[0]+'.svg')===false)missing++;
  }else{
    no++;
    if(sample.length<5)sample.push(n.a);
  }
}
console.log('connected nodes WITH token: '+has);
console.log('connected nodes NO token:   '+no);
console.log('svg file missing:           '+missing);
sample.forEach(a=>console.log('  no-token: '+a));
