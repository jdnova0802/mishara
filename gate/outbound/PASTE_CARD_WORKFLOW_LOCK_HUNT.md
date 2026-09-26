# PASTE — Non-mainstream card-issuing angles (workflow-locked spend)

**26 Sep 2026.** Adjacent to Stripe Issuing. Not another listicle of the same ten processors.

---

## Verdict (plain)

**No secret eleventh issuer clears the bar.** The underused angle is not “find someone cooler than Lithic.” It is:

> **MCC-lock ≠ workflow-lock.**  
> Platforms already hard-lock MCC. Fleet/IIAS/SNAP prove that *provable purpose* requires a second layer (product code / SKU / eligible-item list) at authorization — exactly where Gate’s Issuing mouth already sits.

Gate should **not** rebuild MCC allowlists. Gate should treat platform MCC as the floor and supply the **claim_scope / job / sealed-payee / NEVER** layer that MCC cannot express — the agent analog of IIAS or Visa Fleet product restrictions.

If that framing is wrong for a given prospect, there is no cleaner non-mainstream BIN partner hiding in plain sight from this pass.

---

## 1. Live programs that already do category / purpose lock (primary sources)

Not generic “virtual cards with limits.” Purpose-restricted at auth.

| Program | What is locked | Primary source |
|---------|----------------|----------------|
| **WEX fleet — “Fuel Only”** | Product / authorization profile: fuel-only vs fuel+maintenance; declines outside profile | State of Arkansas WEX setup form (Fuel Only default); GA DOAS *Fuel Card Standards and Guidelines* (Authorization Controls in WEX Online — non-fuel, days/times, $ limits); WEX Motorpass product controls |
| **Visa Fleet 2.0** | **Product category** beyond MCC (e.g. diesel-only, EV charging); chip + **host-based** restrictions in auth response | Visa *U.S. Fleet Program Enhancements* (Visa Rules update); Visa Fleet 2.0 Implementation Guide (product category controls; dynamic host restrictions) |
| **Health FSA / HRA debit cards + IIAS** | Healthcare MCCs **plus** SKU/UPC inventory check for §213(d) eligible items; decline if merchant lacks IIAS (with 90% pharmacy exception) | IRS **Rev. Rul. 2003-43**; IRS **Notice 2006-69** (IIAS); IRS **Notice 2007-2**; SIGIS IIAS standard |
| **SNAP EBT** | Benefits redeemable only for “eligible foods” | **7 CFR §274.7**; eligible foods defined **7 CFR §271.2** |

These are not under-marketed startups. They are the **working civilization precedents** for “card that structurally cannot buy the wrong thing.” Mainstream Issuing APIs stop at MCC/country/MID. The deep lock (SKU / fuel product code / eligible-food set) lives in **fleet networks and benefit programs**.

**Honest:** WEX / Visa Fleet / FSA / SNAP are not “new mouths.” Citing them is the point — Gate’s specialized-card idea already has legal and rail cousins; none of them are the Marqeta-list companies.

---

## 2. Do Lithic / Highnote / Stripe already expose hard MCC lock?

**Yes. Do not build that yourself.**

| Platform | Primitive | Primary docs |
|----------|-----------|--------------|
| **Lithic** | Auth Rules `CONDITIONAL_ACTION`: attribute `MCC`, `IS_ONE_OF` / `IS_NOT_ONE_OF`, action `DECLINE`; also `VELOCITY_LIMIT` with `include_mccs` | https://docs.lithic.com/docs/authorization-rules-v2 · https://docs.lithic.com/docs/conditional-action-rules |
| **Highnote** | GraphQL `createMerchantCategorySpendRule` (allowed/blocked MCC); attach to card product / account / card | https://docs.highnote.com/docs/issuing/spend-controls/spend-rules |
| **Stripe Issuing** (already Gate’s mouth) | `spending_controls.allowed_categories` **or** `blocked_categories` (not both); category strings map from MCC | https://docs.stripe.com/issuing/controls/spending-controls · https://docs.stripe.com/issuing/categories |

**What they do not give you (and where Gate still earns its keep):**

| Gap | Why it matters |
|-----|----------------|
| MCC ≠ cart contents | Fuel MCC 5541/5542 still sells snacks; drug MCC sells candy — IRS invented **IIAS** because MCC was insufficient |
| No job_id / workflow claim | Platform rules don’t know “this auth is for *this* bind / agent mandate / sealed payee” |
| No apophatic exhibit | Decline is a network code, not a scoped NEVER with claim_scope + evidence-head |
| Fleet product codes / host restrictions | Visa Fleet 2.0 host-based product restrictions are a **different rail** than Stripe/Lithic generic Issuing MCC enums |

**Architecture fit (already partly shipped):**  
Gate `POST /v1/issuing/authorization` on `issuing_authorization.request` runs Clear and fail-closes on HOLD/NO_GO (`gate/issuing_mouth.py`). That is the correct insertion point for **workflow** proof. Pair with Stripe `allowed_categories` as the coarse floor — do not reimplement Lithic’s MCC engine.

---

## 3. Regulatory / industry precedent for “provably restricted spend” → agent commerce

Same standard as DSP/NAIC: cite or silence.

| Precedent | What it proves | Citation |
|-----------|----------------|----------|
| **FSA/HRA cards** | Federal tax treatment requires **MCC lock +** (for non-healthcare merchants) **real-time inventory substantiation**; otherwise decline | Rev. Rul. 2003-43; Notice 2006-69; Notice 2007-2 |
| **SNAP EBT** | Statute/regulation: benefits **only** for eligible foods; redemption rules at authorized retailers | 7 CFR 274.7; 7 CFR 271.2 |
| **State fleet fuel cards** | Government programs mandate Authorization Controls so out-of-profile purchases **decline at POS**, not after the fact | GA DOAS Fuel Card Standards; NY OGS / AR WEX program materials |
| **Visa Fleet 2.0** | Network rules push **product-category** restrictions (not MCC-only) for fleet | Visa U.S. Fleet Program Enhancements PDF |

**Agent commerce specifically:**  
No statute found that says “agent cards must be IIAS-like.” Closest policy architecture is IMF 2026/004 Layer 2 (deterministic authorization between probabilistic intent and settlement) — already used in the ≥-BTC pastable — plus H.R. 9917 shutdown capability (separate mouth). **Do not invent an agent-fleet regulation that does not exist.**

The honest extension path:

1. **Platform MCC allowlist** = floor (Stripe/Lithic/Highnote primitive).  
2. **Gate auth webhook** = workflow layer (mandate / job / claim_scope / NEVER).  
3. If a vertical needs **SKU-grade** proof (like FSA), that requires merchant-side inventory participation (IIAS-shaped) — Gate alone cannot invent SKU data the merchant never sends. Same limit fleet faces without product-code terminals.

---

## 4. What would look like a “find” but fails tonight’s bar

| Temptation | Why it fails |
|------------|--------------|
| Another BIN/processor listicle (Adyen, Checkout, Galileo, i2c…) | Same MCC-control class as Lithic/Highnote; not workflow-lock |
| “Ramp/Brex have controls” | Spend-management UX on issued cards — not a new restricted-purpose rail Gate can sit under |
| Claiming Gate should become a fleet issuer | Occupied by WEX/Comdata/Visa Fleet; wrong mouth |
| Claiming MCC allowlist is novel | Already on Stripe Issuing docs Gate already uses |

---

## 5. Build implication (not a new SKU)

| Do | Don’t |
|----|-------|
| Keep Issuing mouth as workflow Clear on auth | Rebuild MCC engines |
| Document pairing: Stripe `allowed_categories` + Gate claim_scope metadata (`agent_id`, sealed payee, job) | Sell “fuel-card for agents” without merchant product-code path |
| Cite IIAS/Fleet when explaining why MCC alone is weak | Pretend there’s a stealth issuer nobody named |

---

## One-liner

**The non-mainstream angle isn’t a new issuer — it’s that purpose-locked spend already exists as FSA IIAS, SNAP, and Visa Fleet product controls, while Lithic/Highnote/Stripe only hard-lock MCC. Gate’s Issuing mouth should stay the workflow/substantiation layer on top of those MCC floors, not become another MCC product.**
