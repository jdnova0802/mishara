# PASTABLE — Atomize the financial rail (gaps + what to build)

**26 Sep 2026.** No glaze. Map atoms → who owns them → Gate status → build vs buy-sponsor.

---

## 1. Money lifecycle atoms (the whole rail)

| # | Atom | Question |
|---|------|----------|
| A | **Identity / link** | Who is the bank account / cardholder? |
| B | **Fund (inbound float)** | How does spend capacity get onto the platform? |
| C | **Hold / ledger** | Where does float sit before spend? |
| D | **Authorize (outbound spend)** | May this pay proceed *now*? |
| E | **Capture / settle** | When is money actually moved / final? |
| F | **Receive (inbound push)** | Can others push money *to* you? |
| G | **Payout (non-card out)** | ACH/wire/RTP/FedNow to a vendor/person? |
| H | **Recall / dispute** | Can it unwind; who eats loss? |
| I | **Proof** | Can a stranger verify the decision? |

That’s the full financial side. Everything else is packaging.

---

## 2. Who owns each atom today (US)

| Atom | Typical owners | Surprise |
|------|----------------|----------|
| A Link | **Plaid** / MX / bank OAuth | Not a money rail — identity pipe only |
| B Fund | ACH pull, wire push, Stripe balance transfer | **No default instant personal→Issuing** |
| C Hold | Stripe Issuing balance / Treasury FA / bank | Split products, not one ledger API |
| D Auth (card) | Visa/MC + **Stripe Issuing** webhook | Gate can sit here — **wired** |
| E Settle | Networks + banks + Stripe | Finality ≠ “authorized” |
| F Receive to card | Visa **OCT / Fast Funds** → **receiving BIN** | **Stripe Issuing ≠ OCT sink** |
| G Non-card out | ACH / FedNow / RTP / wire / Stripe Treasury outbound | Issuing doesn’t do this |
| H Loss | Nacha / UCC 4A / card chargeback regimes | Different eater per rail (`rail-truth`) |
| I Proof | Almost nobody ships stranger-verify receipts | Gate doctrine |

---

## 3. Gate coverage vs gap

| Atom | Gate now | Missing |
|------|----------|---------|
| A | — | Don’t build Plaid; use Stripe/Mercury link |
| B | — | **Funding UX / status** (“pending vs spendable”) — thin |
| C | — | Stripe holds; Gate must not custody |
| D card | **Issuing mouth live** (`money_real: true`) | Needs funded card for *real* auth |
| D policy | Prefinality / Clear / Never | Multi-party mandate bind *before* 2s window |
| E | `rail-truth` finality labels | Not a settlement operator |
| F OCT sink | `/sink-mouth` soft (`money_real` false until BIN) | **Biggest hole** — receive rail |
| G RTP/FedNow/wire | Go/Never UI + adapters (soft / FI-dependent) | Real FI webhook + money_real |
| H | `rail-truth` loss labels | Not insurance; labels only |
| I | Receipts / stranger verify | Keep; don’t dilute |

Live checks: Issuing mouth **on**; sink-mouth **page up / meter off**; Go/Never **up**; `/oct` **404** (no public oct page).

---

## 4. What’s actually missing (ranked)

### M1 — **Receive-to-card (OCT / Fast Funds sink)**
- Industry: push-to-debit pays receiving FI ~$0.29–$0.60 (Visa IRF)
- Stripe Issuing: **spend out**, not “be the sink”
- Gate: soft sink mouth only
- **Build?** Mouth + product yes. **Meter?** Needs sponsor/BIN (Column-class). Can’t code the network side alone.

### M2 — **Non-card outbound mouth (Treasury / ACH / wire / RTP)**
- Same Clear/Never shape on `OutboundPayment` / FedNow accept — **not built as live money_real**
- **Build:** webhook mouths per product (same doctrine as Issuing)
- **Blocker:** Stripe Treasury enablement +/or bank partner for FedNow/RTP

### M3 — **Fund→spendable truth**
- User pain you just hit: Mercury ACH → Stripe pull → “am I live?”
- **Build (cheap, high leverage):** status surface — linked bank, top-up pending/available, card issued?, last auth GO/NO, webhook health
- No new rail. Removes “dashboard vs live” confusion.

### M4 — **Policy bind before 2s auth**
- Issuing forbids multi-human inside auth timeout
- **Build:** mandate/policy Clear as its own write (agent_id, caps, merchant allow) → auth mouth only evaluates pre-bound policy
- Partially exists via card metadata; not a first-class sold SKU

### M5 — **Cross-rail single contract**
- One evaluate: `{rail, amount, counterparty, mandate}` → GO/NO + receipt
- Prefinality points at this; **not** uniformly welded to every Stripe/bank write event
- **Build:** thin adapters, don’t invent a new religion

### Not missing (don’t chase)
- Cross-border *card spend* (network FX exists)
- “Another Issuing brand” (Marqeta/Column = sponsor shopping, not doctrine)
- Plaid replacement

---

## 5. What to build (order that isn’t glaze)

| Priority | Build | Needs institution? | Cash link |
|----------|-------|----------------------|-----------|
| **Now** | Issuing: fund when $ clears → card → one real auth | No (already approved) | Proof / Never demo |
| **Now** | **Fund/spendable status page** (pending vs live) | No | Trust / less confusion |
| **Next** | Treasury/outbound **auth mouth** (same Clear/Never) | Stripe Treasury on | Agent vendor pay |
| **Next** | Mandate-bind SKU (pre-2s policy) | No | Never Pack adjacent |
| **Later** | OCT sink **money_real** | **Yes — BIN/sponsor** | Receive fees |
| **Later** | FedNow/RTP money_real | **Yes — FI** | Instant payout halt |

Monday diligence stays the **cash** path. This list is the **rail** path — don’t conflate.

---

## 6. One-line atomization

**Link (Plaid) → Fund (ACH) → Hold (Stripe) → Auth (Issuing + Gate) → Settle (network) → [GAP: receive OCT] → [GAP: non-card out] → Proof (Gate).**

Fulfillment = mouth every irreversible write; **don’t pretend** you can fill OCT/FedNow without a bank/BIN. Fill M3 + real Issuing auth first; M2 when Treasury is on; M1 only after sponsor.
