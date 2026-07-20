const fs=require('fs');
const G=JSON.parse(fs.readFileSync('graph.json','utf8'));
const T=JSON.parse(fs.readFileSync('tokens.json','utf8'));
if(!fs.existsSync('img'))fs.mkdirSync('img');
const need=new Set();
for(const n of G.nodes){
  const o=T.owners[n.a.toLowerCase()];
  if(o&&o.ids&&o.ids.length)need.add(o.ids[0]);
}
const S=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  let got=0,skip=0;
  for(const id of need){
    const p='img/'+id+'.svg';
    if(fs.existsSync(p)){skip++;continue;}
    try{
      const r=await fetch('https://api.onchainhoodies.xyz/images/'+id+'.svg');
      if(r.ok){fs.writeFileSync(p,await r.text());got++;}
    }catch(e){}
    if((got+skip)%50===0)console.log('  '+(got+skip)+'/'+need.size);
    await S(60);
  }
  console.log('cached '+got+' new, '+skip+' existing, '+need.size+' total');
})();
