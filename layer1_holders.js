// layer1_holders.js — fetch all OnChainHoodies holders from Blockscout
const CONTRACT = '0x9ec6c5b9f572a9b02138e553bc5f5882da735f45';
const BASE = `https://robinhoodchain.blockscout.com/api/v2/tokens/${CONTRACT}/holders`;

async function getAllHolders() {
  const holders = [];
  let nextParams = null;
  let page = 0;

  while (true) {
    const url = nextParams
      ? `${BASE}?${new URLSearchParams(nextParams)}`
      : BASE;
    const res = await fetch(url);
    if (!res.ok) { console.error('HTTP', res.status, await res.text()); break; }
    const data = await res.json();

    for (const item of (data.items || [])) {
      holders.push({
        address: item.address.hash,
        ens: item.address.ens_domain_name || null,
        count: parseInt(item.value, 10) || 0,
        isContract: item.address.is_contract || false,
        isScam: item.address.is_scam || false,
      });
    }
    page++;
    console.log(`page ${page}: ${holders.length} holders so far`);

    if (data.next_page_params) {
      nextParams = data.next_page_params;
    } else {
      break;
    }
    await new Promise(r => setTimeout(r, 250)); // be polite to the API
  }
  return holders;
}

(async () => {
  const holders = await getAllHolders();
  const fs = require('fs');
  fs.writeFileSync('holders.json', JSON.stringify(holders, null, 2));
  console.log(`\nDone. ${holders.length} holders saved to holders.json`);
  const real = holders.filter(h => !h.isContract);
  console.log(`Real wallets (non-contract): ${real.length}`);
  console.log(`Total Hoodies held: ${holders.reduce((s,h) => s + h.count, 0)}`);
})();
