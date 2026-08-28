# Licensed Events vs Contracted Events — Revenue Potential

**Purpose:** model patent-license cash from **QIC** (Qualified Irreversible Commit) metering.  
**Not a forecast.** Assumptions labeled; cartoon scale ($300B/yr) shown as structural limit, not GTM plan.  
**Related:** `PATENT_LICENSE_TERM_SHEET.md` §7 · `PATENT_LICENSE_EXHIBIT_REDACTED.md`

---

## Definitions

| Term | Meaning |
|------|---------|
| **QIC** | One counted licensed event: server-side atomic redeem consume + irreversible bind write in Licensed Field |
| **CAQ** | **Contracted** annual QIC — volume commitment in the license (tier pricing, overage rules) |
| **LAQ** | **Licensed** (actual) annual QIC — metered usage reported quarterly |
| **MAR** | Minimum annual royalty — floor; creditable against LAQ × rate |
| **Billable royalty** | `max(MAR, LAQ × per_QIC_rate)` (+ platform fee if any) |

**What is not a QIC:** quotes, rating, UW triage, failed redeem attempts, read-only hops, dashboard greens without irreversible write.

**Renewals:** count **1 QIC per renewal bind** only if renewal path uses commit-time single-use redeem + irreversible stick (batch renewal bind = 1 QIC per policy in batch).

---

## Revenue formula

```
annual_patent_cash ≈ platform_fee + max(MAR, LAQ × rate) + upfront_amortization (deal-dependent)
```

**Dual-stream (ARM analog):** upfront/platform = access; recurring = `max(MAR, LAQ × rate)`.

**Sublicense (PAS OEM):** Parent Licensee reports **aggregate LAQ** across carrier customers; each sublicense inherits fuse cascade (Parent not LIVE → sublicense void).

---

## Addressable event universe (US P&C — order of magnitude)

| Pool | Rough scale | Notes |
|------|-------------|-------|
| Policies in force (all P&C) | ~300M+ | Auto + HO + commercial lines; multiple carriers |
| New business binds / yr | ~40–80M | LexisNexis Demand Meter: NB growth ~7% YoY on large base |
| Renewal / remarket binds / yr | ~200M+ | Most PIF renews; not all paths are "bind" writes |
| **Full US bind-path QIC ceiling** | **~100–300M / yr** | If every stick used epoch lock + commit-time redeem |

**Gate Licensed Field today:** PAS/MGA **bind-and-issue** + **renewal batch bind** — not whole P&C (no payment rails, no generic IAM).

**Realistic penetration:** patent license follows **conformance adoption**, not total market. Year 1–3 target is **thousands to low millions** of LAQ, not hundreds of millions.

---

## Scenario table — single licensee

Per-QIC rates from term sheet §17 anchors. **Billable = max(MAR, LAQ × rate).**

### MGA / single carrier (Field A)

| Profile | LAQ / yr | Rate | Variable | MAR | **Billable / yr** |
|---------|----------|------|----------|-----|-------------------|
| Pilot MGA | 10,000 | $0.75 | $7,500 | $50k | **$50,000** |
| Growth MGA | 100,000 | $0.50 | $50,000 | $50k | **$50,000** |
| Scale MGA | 500,000 | $0.50 | $250,000 | $50k | **$250,000** |
| Large program | 2,000,000 | $0.35 | $700,000 | $50k | **$700,000** |

*American Integrity–class reference: ~460k PIF, ~170k+ NB policies/yr — full renewal counting could push LAQ toward **600k–1M** if every stick is QIC-metered.*

### PAS OEM (Field B — one platform parent + sublicenses)

| Profile | LAQ / yr (ecosystem) | Rate | Variable | MAR | **Billable / yr** |
|---------|---------------------|------|----------|-----|-------------------|
| Early embed | 1,000,000 | $0.25 | $250,000 | $250k | **$250,000** |
| Regional PAS | 10,000,000 | $0.20 | $2,000,000 | $250k | **$2,000,000** |
| Tier-1 footprint | 50,000,000 | $0.15 | $7,500,000 | $250k | **$7,500,000** |
| Tier-1 @ upper rate | 50,000,000 | $0.50 | $25,000,000 | $250k | **$25,000,000** |

*Celent-scale single PAS implementation cited **~3.8M endorsements/yr** workload — bind+renewal QIC for one carrier often **1–5M/yr**; OEM multiplies by carrier count on platform.*

---

## Portfolio potential — contracted vs licensed (stacked deals)

Assume **non-exclusive** field licenses; no double-count across overlapping fields.

| Phase | Licensees | Avg CAQ | Avg rate | **Contracted floor** | **At-full-LAQ** |
|-------|-----------|---------|----------|----------------------|-----------------|
| **Gate 1 proof** | 1 MGA | 100k | $0.50 | MAR $50k | **$50k/yr** |
| **Year 1–2** | 5 MGA + 1 PAS | 200k + 5M | blended $0.40 | ~$350k MAR sum | **~$2.5M/yr** |
| **Year 3–5** | 20 MGA + 3 PAS | 300k + 15M | blended $0.30 | ~$1.5M MAR sum | **~$15M/yr** |
| **Mature niche** | 50 MGA + 5 PAS | 500k + 30M | blended $0.25 | ~$4M MAR sum | **~$50M/yr** |
| **Category king (insurance field only)** | 1 exclusive PAS + 200 carriers | 100M | $0.10 | MAR negot. | **~$10M/yr** at dime; **~$50M/yr** at $0.50 |

**Contracted vs licensed gap:** if LAQ < CAQ, Licensee may still owe **MAR** (and sometimes **take-or-pay** on CAQ tier — counsel to add in definitive agreement). If LAQ > CAQ, overage bills at tier rate.

---

## Upside levers (same event count)

| Lever | Effect |
|-------|--------|
| **Raise rate** on exclusive Field A | Linear on LAQ |
| **Count renewal batch binds** | 2–5× LAQ vs new-business-only |
| **Tier 2 hosted redeem** | Platform fee + higher MAR |
| **bps on premium bound** (Qualcomm analog) | $971B US P&C NPW × 1 bp = **$97M/yr** — needs huge adoption |
| **Expand Licensed Field** (platform OEM outside insurance) | New CAQ pools — separate license |

---

## Structural ceiling — why $300B/yr is not this spreadsheet

| Target | Required at $0.50/QIC | Required at $0.05/QIC | Verdict |
|--------|----------------------|----------------------|---------|
| **$1M/yr** | 2M QIC | 20M QIC | Achievable niche |
| **$10M/yr** | 20M QIC | 200M QIC | Mature insurance stack |
| **$100M/yr** | 200M QIC | 2B QIC | Needs multi-field + PAS at scale |
| **$1B/yr** | 2B QIC | 20B QIC | Beyond US bind path alone |
| **$300B/yr** | 600B QIC | 6T QIC | **Planet-scale unit tax** — ARM/Visa/consumer-IP class, not MGA meter |

**Cartoon recurring ($300B/yr)** requires one or more of:

1. **Mandatory global unit** with **billions** of daily irreversible commits outside insurance  
2. **Standard-essential choke** (FRAND at scale) on delegated-write control planes  
3. **Premium / ASP tax** at tens of bps on **trillions** of flow — still needs adoption >> US P&C  
4. **M&A / balance-sheet** revaluation of patent + conformance ecosystem — not royalty line alone

**Honest near-term patent asset worth:** first **field-limited paid license** with auditable LAQ → external proof; stack **$50k–$25M/yr** royalty depending on licensee type and volume — not $300B until the **unit of account** is planetary.

---

## Meter design recommendations

1. **Shadow count 90 days** before CAQ signature — baseline LAQ from bind logs  
2. **Split counters:** `new_business_qic`, `renewal_qic`, `endorsement_qic` (only if in Licensed Field)  
3. **Publish aggregate LAQ band** at `/.well-known/epoch-lock-patent-asset.json` (no customer PII, no pricing)  
4. **Audit hook:** align with `royalty_audit_clawback` module — underpayment >5% → deficiency + interest  

---

## Paste-ready diligence lines

- **Contracted events (CAQ)** = what they commit to buy; **licensed events (LAQ)** = what the meter counts; you bill **`max(MAR, LAQ × rate)`**.  
- **First deal:** one MGA at 100k CAQ / $50k MAR = proof of worth, not category royalty.  
- **PAS OEM at 50M LAQ × $0.25** = **$12.5M/yr** — realistic category ceiling **inside insurance** before multi-field expansion.  
- **$300B/yr** = different product class (global mandatory commit primitive), not an extrapolation of today's bind-room SKUs.

---

*Event potential v1 · Aug 28, 2026 · Model only — not legal or financial advice.*
