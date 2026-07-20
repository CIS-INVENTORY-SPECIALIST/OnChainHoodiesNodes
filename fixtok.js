const fs=require('fs');
const G=JSON.parse(fs.readFileSync('graph.json','utf8'));
const T=JSON.parse(fs.readFileSync('tokens.json','utf8'));
const ents=fs.existsSync('entities.json')?JSON.parse(fs.readFileSync('entities.json','utf8')):[];

// map every wallet in a multi-wallet entity back to its representative
const alt=new Map();
for(const grp of ents){
  const addrs=grp.map(g=>g.a.toLowerCase());
  for(const a of addrs) alt.set(a,addrs);
}

const pool=Object.values(T.owners).flatMap(o=>o.ids||[]).sort((a,b)=>a-b);
let direct=0,viaAlt=0,viaPool=0;

for(const n of G.nodes){
  const a=n.a.toLowerCase();
  let id=null;
  const o=T.owners[a];
  if(o&&o.ids&&o.ids.length){ id=o.ids[0]; direct++; }
  if(id===null&&alt.has(a)){
    for(const b of alt.get(a)){
      const ob=T.owners[b];
      if(ob&&ob.ids&&ob.ids.length){ id=ob.ids[0]; viaAlt++; break; }
    }
  }
  if(id===null&&pool.length){
    id=pool[Math.abs(hash(a))%pool.length]; viaPool++;
  }
  n.token=id;
  n.fc=T.farcaster[a]||null;
}
function hash(s){let h=0;for(let i=0;i<s.length;i++){h=(h*31+s.charCodeAt(i))|0;}return h;}

fs.writeFileSync('graph.json',JSON.stringify(G));
console.log('direct: '+direct+' | via linked wallet: '+viaAlt+' | fallback: '+viaPool);

// make sure every referenced svg is cached
const need=new Set(G.nodes.filter(n=>n.deg>0&&n.token).map(n=>n.token));
const miss=[...need].filter(id=>fs.existsSync('img/'+id+'.svg')===false);
console.log('svgs to fetch: '+miss.length);
const S=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  let g=0;
  for(const id of miss){
    try{const r=await fetch('https://api.onchainhoodies.xyz/images/'+id+'.svg');
        if(r.ok){fs.writeFileSync('img/'+id+'.svg',await r.text());g++;}}catch(e){}
    await S(60);
  }
  console.log('fetched '+g+' new svgs');
})();
