const fs=require('fs');
const T=JSON.parse(fs.readFileSync('tokens.json','utf8'));
const prev=fs.existsSync('holders.json')?JSON.parse(fs.readFileSync('holders.json','utf8')):[];
const meta=new Map(prev.map(h=>[h.address.toLowerCase(),h]));
const out=[];
for(const a in T.owners){
  const n=T.owners[a].ids.length;
  if(n===0)continue;
  const p=meta.get(a)||{};
  out.push({
    address:a,
    ens:T.farcaster[a]?(p.ens||null):(p.ens||null),
    count:n,
    isContract:p.isContract||false,
    isScam:p.isScam||false
  });
}
out.sort((x,y)=>y.count-x.count);
fs.writeFileSync('holders.json',JSON.stringify(out,null,2));
const total=out.reduce((s,h)=>s+h.count,0);
console.log('holders derived from tokens: '+out.length);
console.log('total hoodies: '+total+' / 6000');
console.log('was '+prev.length+' holders -> now '+out.length);
