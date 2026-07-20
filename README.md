# Hood Nodes

**Live:** https://cis-inventory-specialist.github.io/OnChainHoodiesNodes/

A holder affinity graph for [OnChainHoodies](https://www.onchainhoodies.xyz). Every holder is placed
next to the people who collect like they do, based on what else they own across Ethereum.

Built with the [OnChainHoodies API](https://www.onchainhoodies.xyz/api). Refreshes hourly.

## What it does

**Maps taste, not just ownership.** Two holders are linked when they share collections, weighted by
how rare that overlap is. Sharing an obscure 200-piece collection means far more than both holding ENS,
so the graph clusters by genuine affinity rather than by who owns the most things.

**Resolves wallet farms.** A large share of "holders" are one person running many wallets. Any wallets
with near-identical portfolios are collapsed into a single entity, so the graph shows people rather
than addresses — and the count of multi-wallet operators is surfaced directly.

**Three lenses.** Search yourself to see your closest neighbors ranked by overlap. Click a tribe to
isolate a cluster. Click a collection to light up everyone in the Hood who holds it.

## Pipeline

| Step | Script | Source |
|---|---|---|
| Tokens, owners, socials | `l4b.js` | Blockscout (Robinhood Chain) |
| Holder list | `l1b.js` | derived from tokens |
| Cross-chain holdings | `layer2_holdings.js` | Alchemy (Ethereum mainnet) |
| Entity resolution + graph | `layer3_overlap.js` | local |
| Hoodie assignment | `fixtok.js` | local |
| Artwork cache | `cache_svgs.js` | OnChainHoodies API |

Holders live on Robinhood Chain; their other collections live on Ethereum mainnet. EVM addresses are
identical across chains, so the same address is looked up on both.

## Method

Each entity is a vector over the collections it holds. Collections are weighted by inverse frequency
(`log(N/k)`), and similarity between two entities is the cosine of their weighted vectors. Wallets
holding fewer than six collections are excluded — you can't measure taste from two data points.
Pairs above 0.70 similarity sharing six or more collections are treated as the same operator and merged.

## Running locally

```bash
echo "YOUR_ALCHEMY_KEY" > key.txt
node l4b.js && node l1b.js && node layer2_holdings.js
node layer3_overlap.js && node fixtok.js && node cache_svgs.js
python3 -m http.server 8080
```

Refresh runs automatically via GitHub Actions; `ALCHEMY_KEY` is stored as a repository secret.

## Notes

Read-only. No wallet connection, no transactions, nothing written on-chain. All data is public.

CC0, same as the collection.
