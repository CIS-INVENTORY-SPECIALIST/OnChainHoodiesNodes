const fs=require('fs');
const E=JSON.parse(fs.readFileSync('entities.json','utf8'));
const B='https://robinhoodchain.blockscout.com/api/v2/addresses/';
const S=ms=>new Promise(r=>setTimeout(r,ms));

async function funders(addr){
  const src=new Set();
  for(let a=0;a<4;a++){
    try{
      const r=await fetch(B+addr+'/transactions?filter=to');
      if(r.status>=500){await S(900*Math.pow(2,a));continue;}
      if(!r.ok)return src;
      const d=await r.json();
      for(const t of (d.items||[])){
        if(t.from&&t.from.hash&&t.value&&t.value!=='0')
          src.add(t.from.hash.toLowerCase());
      }
      return src;
    }catch(e){await S(800*Math.pow(2,a));}
  }
  return src;
}

(async()=>{
  console.log('checking '+E.length+' clusters for shared funding\n');
  const out=[];
  for(let i=0;i<E.length;i++){
    const grp=E[i];
    const seen=new Map();
    const sample=grp.slice(0,12);          // cap per cluster to stay polite
    for(const m of sample){
      const f=await funders(m.a);
      for(const s of f) seen.set(s,(seen.get(s)||0)+1);
      await S(240);
    }
    const shared=[...seen.entries()].filter(x=>x[1]>=2).sort((a,b)=>b[1]-a[1]);
    const top=shared[0];
    const conf = top ? Math.round(100*top[1]/sample.length) : 0;
    out.push({size:grp.length,checked:sample.length,funder:top?top[0]:null,hits:top?top[1]:0,conf:conf});
    console.log('cluster '+(i+1)+' ('+grp.length+' wallets, checked '+sample.length+'): '+
      (top ? conf+'% share funder '+top[0].slice(0,12)+'…' : 'no shared funder found'));
  }
  fs.writeFileSync('funding.json',JSON.stringify(out,null,2));
  const confirmed=out.filter(x=>x.conf>=50).length;
  console.log('\n'+confirmed+' of '+out.length+' clusters have a majority-shared funding source');
  console.log('saved -> funding.json');
})();
