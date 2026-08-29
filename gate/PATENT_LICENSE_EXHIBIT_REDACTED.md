# Patent License — Redacted One-Page Exhibits (sendable)

**Status:** draft for external diligence — **remove § internal anchors before sending.**  
**Patent:** US Provisional 64/124,027 · **Licensor:** Nisaba LLC  
**Full skeleton:** `PATENT_LICENSE_TERM_SHEET.md` · **Pack index:** `/.well-known/licensing-pack.json` · **Licensed Field (default):** `/.well-known/licensed-field.json` · **Spec:** `gate-commit-auth-v1`

---

## Exhibit G-0 — Platform (Field B default)

**Licensee profile:** `[REDACTED]` · irreversible delegated-write platform · `[JURISDICTION]`  
**Licensed Field:** **Option B (platform)** — agent commits, payout/withdraw clearance, enterprise org-root spend, defense release, hiring stick, and other irreversible writes where strangers can verify HALT + receipt  
**Grant tier:** Tier 1 or Tier 2 · **non-exclusive** unless Exhibit B amended  
**Claims licensed:** epoch lock (primary) · commit-time single-use authorization (secondary)

| Term | Redacted offer |
|------|----------------|
| **Conformance access (one-time)** | `$[REDACTED]` |
| **Annual platform fee** | `$[REDACTED] / yr` |
| **Minimum annual royalty (MAR)** | `$[REDACTED] / yr` |
| **Per QIC royalty** | `$[0.03 – 0.50]` per Qualified Irreversible Commit |
| **Cleared-flow bps (Exhibit I)** | `[5 – 25] bps` on volume through conformant path |
| **Contracted annual QIC (CAQ)** | `[10,000,000]` events/yr (platform volume commitment) |
| **Sublicense** | Per Exhibit F when SI/OEM distributes in Licensed Field |
| **No-may** | No CHARGE/resurrect resale; fail-closed redeem; no admin override |

**QIC definition:** one atomic redeem consume + irreversible write — **any vertical** in Licensed Field (see `/.well-known/qic-meter.json`).

**Illustrative:** 10B QIC × $0.10 = **$1B/yr** variable → bill **`max(MAR, variable)`**; or 10 bps × $200B cleared flow = **$200M/yr** (Exhibit I).

---

## Exhibit G-1 — PAS OEM (Field A insurance carve-in + Field B embed)

**Licensee profile:** `[REDACTED]` · Tier-1 PAS / policy-admin platform OEM · `[JURISDICTION]`  
**Licensed Field:** **Option A carve-in** (insurance) within Option B — irreversible **bind-and-issue** and **renewal batch bind** embedded in OEM core for P&C carriers in `[NAMED REGIONS]`  
**Grant tier:** Tier 2 (implementation + optional hosted redeem SDK) · **non-exclusive** in Field  
**Claims licensed:** epoch lock (primary) · commit-time single-use bind (secondary)

| Term | Redacted offer |
|------|----------------|
| **Conformance access (one-time)** | `$[REDACTED]` |
| **Annual platform fee** | `$[REDACTED] / yr` |
| **Minimum annual royalty (MAR)** | `$[REDACTED] / yr` (creditable against per-event) |
| **Per QIC royalty** | `$[0.10 – 0.50]` per Qualified Irreversible Commit |
| **Contracted annual QIC (CAQ)** | `[50,000,000]` events/yr (tier-1 volume commitment) |
| **Overage** | Same rate; quarterly true-up within 30 days |
| **Exclusivity** | None (field-limited non-exclusive) |
| **Sublicense** | Permitted to carrier end-customers in Licensed Field only — Exhibit F cascade required |
| **No-may** | No CHARGE/resurrect resale; no fail-open redeem; no admin override on bind path |
| **Conformance** | Annual attestation + `/.well-known/commit-auth.json` subset; audit rights §9 |

**QIC definition (meter):** one server-side atomic redeem consume + irreversible bind write in Licensed Field (not quotes, not failed redeem attempts).

**Illustrative annual royalty at CAQ** (not a quote): 50M QIC × $0.25 = **$12.5M/yr** variable → bill **`max(MAR, variable)`**.

**Stranger verify (no pricing):** `/.well-known/licensing-pack.json` · `/.well-known/epoch-lock-patent-asset.json`

**Formal schedules:** Exhibit I `/.well-known/premium-bps-schedule.json` · Exhibit K `/.well-known/qic-meter.json`

---

## Exhibit G-2 — MGA / single carrier (Field A insurance carve-in)

**Licensee profile:** `[REDACTED MGA]` · delegated-authority P&C · `[STATE LIST]`  
**Licensed Field:** **Option A carve-in** — PAS **pre-bind + bind-only** for `[PROGRAM NAME]` in `[STATE LIST]` only (subset of platform field)  
**Grant tier:** Tier 1 (architecture / conformance — Licensee hosts redeem) · **non-exclusive**  
**Claims licensed:** same as G-1

| Term | Redacted offer |
|------|----------------|
| **Conformance access (one-time)** | `$[REDACTED]` |
| **Annual platform fee** | `$[REDACTED] / yr` (optional Tier 1 — may fold into MAR) |
| **Minimum annual royalty (MAR)** | `$[50,000] / yr` |
| **Per QIC royalty** | `$[0.25 – 1.00]` per QIC |
| **Contracted annual QIC (CAQ)** | `[100,000]` events/yr (new business + counted renewal binds) |
| **Overage** | `[same rate]` · true-up quarterly |
| **Exclusivity** | None |
| **Sublicense** | **Prohibited** (single entity; no ghost sublicensing) |
| **No-may** | Same as G-1 |
| **Term** | 3 yr initial · auto-renew 1 yr · 90-day non-renew |

**Illustrative annual royalty at CAQ:** 100k QIC × $0.50 = **$50k/yr** → equals MAR floor (typical first MGA deal sits at MAR until volume grows).

**Growth path:** at 500k QIC × $0.50 = **$250k/yr** before platform fee; at 2M QIC × $0.35 = **$700k/yr**.

**Condition precedent:** non-provisional filed before `[DATE]` (see term sheet §2.2).

**Formal schedules:** Exhibit I (premium bps) · Exhibit J (conformant mark) · Exhibit K (QIC meter) — via `/.well-known/licensing-pack.json`

---

## What to redact before PDF export

- All `[REDACTED]` fee numbers until term sheet is negotiated  
- Licensee legal name until NDA / counsel loop  
- Exact CAQ until meter baseline audit (90-day shadow count recommended)  
- Remove "Illustrative" rows if sending as binding term sheet — move to cover email only

---

*Redacted exhibits v1 · Aug 28, 2026 · Counsel must review before execution.*
