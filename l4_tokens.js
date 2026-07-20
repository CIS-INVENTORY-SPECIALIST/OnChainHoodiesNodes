const fs=require('fs');
const C='0x9ec6c5b9f572a9b02138e553bc5f5882da735f45';
const B='https://robinhoodchain.blockscout.com/api/v2/tokens/'+C+'/instances';
(async()=>{
let np=null,out={},far={},n=0,pages=0;
while(true){
 const u=np?B+'?'+new URLSearchParams(np):B;
 const r=await fetch(u); if(!r.ok){console.log('HTTP',r.status);break;}
 const d=await r.json();
 for(const it of (d.items||[])){
  const id=it.id, o=it.owner; if(!o||!o.hash)continue;
  const a=o.hash.toLowerCase();
  let arch=null;
  const m=it.metadata;
  if(m&&Array.isArray(m.attributes)){
   const t=m.attributes.find(x=>/hoodie|type|archetype|character/i.test(x.trait_type||''));
   if(t)arch=t.value;
  }
  if(!out[a])out[a]={ids:[],arch:{}};
  out[a].ids.push(+id);
  if(arch)out[a].arch[arch]=(out[a].arch[arch]||0)+1;
  const tags=((o.metadata||{}).tags)||[];
  const fc=tags.find(t=>t.slug==='warpcast-account'||/farcaster/i.test(t.name||''));
  if(fc&&fc.meta&&fc.meta.warpcastHandle)far[a]=fc.meta.warpcastHandle;
  n++;
 }
 pages++;
 if(pages%2===0)console.log('  '+n+' tokens, '+Object.keys(out).length+' owners');
 np=d.next_page_params; if(!np)break;
 await new Promise(r=>setTimeout(r,180));
}
for(const a in out)out[a].ids.sort((x,y)=>x-y);
fs.writeFileSync('tokens.json',JSON.stringify({owners:out,farcaster:far}));
const archTotals={};
for(const a in out)for(const k in out[a].arch)archTotals[k]=(archTotals[k]||0)+out[a].arch[k];
console.log('\ntokens: '+n+' | owners: '+Object.keys(out).length+' | farcaster: '+Object.keys(far).length);
console.log('archetypes:',archTotals);
console.log('saved -> tokens.json');
})();
