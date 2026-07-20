const fs=require('fs');
const C='0x9ec6c5b9f572a9b02138e553bc5f5882da735f45';
const B='https://robinhoodchain.blockscout.com/api/v2/tokens/'+C+'/instances';
const S=ms=>new Promise(r=>setTimeout(r,ms));
let out={},far={},seen=new Set();
if(fs.existsSync('tokens.json')){
 const p=JSON.parse(fs.readFileSync('tokens.json','utf8'));
 out=p.owners||{}; far=p.farcaster||{};
 for(const a in out)for(const id of out[a].ids)seen.add(id);
 console.log('resuming with '+seen.size+' tokens');
}
const save=()=>fs.writeFileSync('tokens.json',JSON.stringify({owners:out,farcaster:far}));
(async()=>{
let np=null,pages=0,fails=0;
while(true){
 const u=np?B+'?'+new URLSearchParams(np):B;
 let r=null;
 for(let a=0;a<5;a++){
  try{ r=await fetch(u); if(r.ok)break;
       if(r.status>=500){await S(1200*Math.pow(2,a));r=null;continue;}
       break; }
  catch(e){ await S(1000*Math.pow(2,a)); r=null; }
 }
 if(!r||!r.ok){ fails++; console.log('page failed, stopping'); break; }
 const d=await r.json();
 for(const it of (d.items||[])){
  const id=+it.id,o=it.owner; if(!o||!o.hash)continue;
  const a=o.hash.toLowerCase();
  if(!out[a])out[a]={ids:[]};
  if(!seen.has(id)){out[a].ids.push(id);seen.add(id);}
  const tags=((o.metadata||{}).tags)||[];
  const fc=tags.find(t=>t.slug==='warpcast-account');
  if(fc&&fc.meta&&fc.meta.warpcastHandle)far[a]=fc.meta.warpcastHandle;
 }
 pages++;
 if(pages%5===0){save();console.log('  '+seen.size+' tokens, '+Object.keys(out).length+' owners, '+Object.keys(far).length+' farcaster');}
 np=d.next_page_params; if(!np)break;
 await S(220);
}
for(const a in out)out[a].ids.sort((x,y)=>x-y);
save();
console.log('\ntokens: '+seen.size+' | owners: '+Object.keys(out).length+' | farcaster: '+Object.keys(far).length);
console.log('saved -> tokens.json');
})();
