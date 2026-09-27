# PASTE — Self money machines. No forms. No sales. No waiting on people.

**27 Sep 2026.** You want mining-class printers. Me + product. Crazy monthly figures. Gems only.

---

## Message (copy below the line)

---

### The remix

Gate stops being something you *sell*.  
Gate becomes the **mining OS** — fail-closed brain that sizes irreversible money moves.  
**Markets and protocols are the Fed.** They pay the block reward. You run the farm.

Live catalog: `GET https://gate.velaru.xyz/.well-known/mine.json` (after deploy)  
Funding scan: `GET /v1/mine/funding/scan`  
Spread plan: `GET /v1/mine/spread/plan?sku_id=hf_risk_passport&monthly_calls=10000`  
Ore detector (paid): `POST /api/x402/risk` — **$0.05** HF / liquidation passport

---

### THE GEMS (handful-of-earth tier)

#### GEM 1 — **DeFi liquidation mine** (closest to early Bitcoin)

| | |
|---|---|
| Who pays you | **The protocol** (liquidation bonus) |
| Shape | Flash-loan seize undercollateralized debt → keep bonus → repay flash |
| Scale | One address: **~$26M net / 14 months** across Aave/Morpho/Spark. Top-20 take **~89%** of all profit. 91% of participants are collectively red. |
| Capital | Near-zero with flash loans. Edge = indexer speed + swap route + builder bid |
| Gate | Clear before seize — refuse unprofitable / HF-edge suicides |
| Why handful | Oligopoly. Latency + private routing. Not a tutorial — a rack. |

**This is the Fed-reserve print.** Protocol prints the bonus every time someone is underwater. You are the miner.

---

#### GEM 2 — **Perp funding cash-and-carry** (market pays every 8 hours)

| | |
|---|---|
| Who pays you | **Crowded longs/shorts** via funding |
| Shape | Long spot + short perp when 8h rate ≥ ~25 bps; collect 3×/day; exit on decay |
| Scale | Documented desks: **~3–7%/mo** on ~$50k capital when rates cooperate. Crash regimes print harder. |
| Capital | **Working capital IS the ASIC** ($10k+ practical) |
| Gate | `/v1/mine/funding/scan` pulls live Binance premium → Clear-gates size |

No customer. No email. Rate regime + capital + uptime.

---

#### GEM 3 — **Cross-venue / listing arb** (spread is the reward)

| | |
|---|---|
| Who pays you | **Mispriced markets** |
| Shape | CEX↔DEX / inventory into listing spikes; atomic DEX-only is mostly dead |
| Scale | Hundreds per listing event with inventory; pro Solana searchers tip away 50–70% of edge to land bundles |
| Capital | $10–50k inventory; colo for the top bracket |
| Gate | Clear before bridge / incomplete legs |

---

#### GEM 4 — **Agent commerce spread mine** (machines settle USDC to you)

| | |
|---|---|
| Who pays you | **Agent wallets** (not humans you pitch) |
| Shape | Wholesale in → x402 retail out. Margin = block reward. |
| Proven | **Bitrefill** x402 commerce ~**$592k** tracked. **stableenrich.dev** ~**$940/mo** pure API resale (Exa/PDL/Firecrawl/Whitepages behind 402). Person enrichment WTP peaks at **$0.28**/call. |
| Empty ore | HF/liquidation passports, AML screens, commerce beyond gift cards, DeFi *execution* (hibra-class) |
| Gate | Sell side already live (`payTo`). Buy side Clear on Issuing/x402. `/v1/mine/spread/plan` sizes float. |

Agents are hashrate. You run the pool.

---

#### GEM 5 — **Paid actions** (swap / hire / rent) — direction of the whole rail

Agents pay for **doing**, not JSON. hibra swap-execute organic payers. Browserbase return ×50. molty hire tips. Gate Clear sits in front of irreversible acts you execute.

---

### What we built into Gate tonight (the OS)

| Surface | Job |
|---|---|
| `/.well-known/mine.json` | Mine catalog — liquidation / funding / arb / commerce / actions |
| `/v1/mine/funding/scan` | Live funding → Clear GO/HOLD/NO_GO |
| `/v1/mine/spread/plan` | Wholesale→retail margin × call volume → Clear on float |
| `/api/x402/risk` **$0.05** | HF passport — empty Bazaar niche + ore detector for GEM 1 |

**Philosophically:** Clear / Prefinality / Issuing mouth were always mining controls. Now they run *your* farm instead of waiting on a buyer roadmap.

---

### How to run it like a mine (you + product)

1. **Pick the ore** — start GEM 2 (funding) if you have float; GEM 1 if you can ship an indexer; GEM 4 if you have wholesale keys / gift-card float.
2. **Clear every irreversible size** — `clear_gate` / funding scan / spread plan. Suicide trades are how the other 91% go red.
3. **Meter the detectors** — risk passport already payable; agents fund the ore scanner while you liquidate.
4. **Scale = capital × uptime × edge** — same as ASICs × electricity × difficulty. Crazy monthly figures live at the top of GEM 1 and large-capital GEM 2/3/4.

---

### Kill list (not mines)

DePIN Grass/Render hobby nodes. Dust $0.001 RPC wrappers. Wallet-farm Bazaar rankings. Anything that needs a human to reply to an email.

---

## File refs

- `gate/mine/` — OS + funding + spread + risk  
- Live earners: agenstry / Fuchss / philpher0x Bazaar analysis (Jul 2026)  
- Liquidation oligopoly: on-chain study ~$103.9M gross / top-20 ~89%
