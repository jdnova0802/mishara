# Patent Counsel Brief — Non-Provisional Conversion (Narrow)

**Status:** **COUNSEL WEEK = Mon Sep 1 – Fri Sep 4, 2026** (written Fri Aug 28).  
**Purpose:** What to send a patent attorney — and **what not to send**.  
**Not for licensing diligence.** For **64/124,027 non-provisional conversion quote only.**

---

## Calendar (next week)

| Day | Date | Do |
|-----|------|----|
| **Fri** | Aug 28 | Optional: shortlist 3 firms + draft email. **Do not** expect replies today. |
| **Mon** | Sep 1 | Send quote request to firm A + B (+ C). Subject line below. Attach **only** two claims + prior-art table. |
| **Tue** | Sep 2 | Follow-up if no ack. Confirm micro-entity ask. Calendar provisional → non-provisional deadline (S1). |
| **Wed** | Sep 3 | Chase outstanding. First written quote in → log S2 / I2. |
| **Thu–Fri** | Sep 4 | Target: **2–3 quotes in writing**. Compare flat fee + gov fees + draft date. S2 done or escalate. |
| **Week of Sep 7** | — | Pick counsel · start conversion · **then** Gate 1 outbound may resume |

| Priority | Item | Status |
|----------|------|--------|
| **1** | **2–3 counsel quotes in writing by Fri Sep 4** (flat-fee conversion ask) | ☐ |
| **2** | Confirm micro-entity eligibility + USPTO fee tier | ☐ |
| **3** | Calendar non-provisional deadline from provisional filing date | ☐ |
| **—** | Gate 1 outbound | **WAIT** until quotes landed |
| **—** | Licensing pack / exhibits / 112 modules to counsel | **FORBIDDEN** |

Miss non-provisional deadline ⇒ patent → **$0** ⇒ term sheet + eleven exhibits + ceiling ladder worthless (`REALITY_CONTRACT_30DAY.md`).

**If cash is the blocker after quotes:** see `CONTINGENT_CAPITAL_CRAWL.md` (SBIR / WY match / staged fee / option-to-license — **not** PAE). Ask each firm for an optional **PCT rider** line item on the same quote.

---

## Practical notes (ask explicitly)

1. **Micro-entity status** — if eligible, USPTO fees drop substantially; ask counsel to confirm qualification (revenue + prior application count) **before** quoting government fees.
2. **Flat-fee non-provisional conversion** — ask for **fixed fee to convert 64/124,027**, not open-ended hourly. Same work varies widely firm to firm.
3. **Get 2–3 quotes** — boutique IP, general tech boutique, one pro-se-friendly flat-fee shop if available.
4. **Timeline in quote** — draft delivery date + filing date assumption; what you must provide by when.

---

## What to send counsel (attach only this)

| Include | Path / artifact |
|---------|-----------------|
| Provisional number | **US 64/124,027** |
| Provisional PDF | As filed (if available) |
| **Two claim families** | Below — copy/paste |
| **Prior-art diff** | Section below (from `COMMIT_AUTH.md`) |
| Reference implementation pointer | `gate-commit-auth-v1` · `/.well-known/commit-auth.json` (URL only — optional) |
| Entity | **Nisaba LLC, Wyoming** |

**Email subject line:** `Quote request — flat-fee non-provisional conversion — 64/124,027 — micro-entity`

---

## Two claim families (only these)

### Claim 1 — Epoch lock (primary)

**Non-resurrecting operator HALT** for a job/epoch identifier that persists until a defined **non-admin** resurrection event (verified CHARGE-class external authority).

**Must exclude in prosecution:** operator-console resurrect, soft-approval bypass, admin override that lifts HALT without the defined event.

**Supporting spec refs (for counsel, not claims):** `override_impossibility.py`, `epoch.py`, `license_fuse.py` — stranger-verifiable forged-path packet.

### Claim 2 — Commit-time single-use bind authorization (secondary)

**Server-side atomic consume** of bind authorization at commit time on an irreversible write path; attestation/signature alone **insufficient** to complete the write; **single-use** per issued authorization bound to spend fingerprint.

**Must exclude in prosecution:** reusable JWT/Biscuit delegation, generic TTL lease revocation, FRE-only receipts, pre-execution proof without epoch lock.

**Supporting spec refs:** `gate-spend-protocol-v1`, bind ticket redeem path, `COMMIT_AUTH.md` Parakhin scope note (bind ≠ agent mesh).

---

## Prior-art diff (give counsel this table — do not dump the repo)

**Crowded lane — do not claim alone:**

| Prior art | What they do | Why we differ |
|-----------|--------------|---------------|
| **Macaroons / Biscuit / UCAN** | Attenuated delegation, caveats, TTL, spend fingerprint | Reusable credentials; **no non-resurrecting epoch HALT**; **no bind-path single-use redeem-at-commit** |
| **IBCT / Prakash (arXiv:2603.24775)** | Identity + attenuated auth + provenance; MCP mesh benchmarks | Agent-speed **reusable** capability tokens — **not** carrier bind choke + **not** operator HALT that forbids admin resurrect |
| **Authproof Cloud** | Receipt before act; RFC 3161; vertical SaaS | **Attestation lane** — not insurance bind + epoch lock |
| **CertNode / FRE 902** | JWS + timestamp + FRE-shaped receipts | **FRE hero taken** — we do not lead receipts-only |
| **Proof-Carrying Agent Actions (arXiv:2606.04104)** | `non_execution_proof` | Names restraint receipt — **prior art exists** for proof-without-execution |
| **Parakhin (arXiv:2603.09875)** | TTL lease revocation O(v·TTL); proposes execution-count RCC | Applies to **reusable high-velocity agent credentials** — Gate bind ticket is **single-use atomic consume**, not TTL-as-revocation story |
| **ASQAV / IETF compliance-receipts drafts** | Compliance envelope profiles | **Extend, not replace** — our novelty is **epoch lock + bind-commit semantics** atop profile, not owning the draft |

**Patent lane (file narrow):** epoch lock + commit-time single-use bind.  
**GTM lane (do not broaden claims):** insurance bind surface, NAIC, PAS names — **sales**, not claim breadth.

**One sentence for counsel:**  
> Narrow utility conversion on **non-resurrecting HALT until verified external CHARGE** plus **single-use server-side redeem at irreversible commit** — distinguished from macaroon/JWT/IBCT reusable delegation and from attestation-only receipts.

---

## Do NOT send counsel (counsel freeze)

Same discipline as `mouth_ceiling_freeze.json` — **definite baseline, not judgment call.**

| Forbidden attachment | Why |
|---------------------|-----|
| `INTENTIONS.md` / 112 invention module inventory | Invites dependent claims on undemoable mountain |
| `civilizational_deep.py` / `ip_asset_deep.py` / `ip_asset_ceiling.py` catalogs | Positioning, not prosecution |
| Full `PATENT_LICENSE_TERM_SHEET.md` + Exhibits A–K | **Licensing** — irrelevant to conversion quote |
| `IP_ASSET_CEILING.md` / upside ladder | Fantasy scope creep |
| `PATENT_LICENSE_EVENT_POTENTIAL.md` / QIC revenue model | Licensing economics |
| Competitive invention well-known URLs (56+ modules) | Prior-art **magnet** — macaroons, UCAN, IBCT, ASQAV all at once |
| GAAIA letter (unless counsel asks) | Regulatory tail — optional background paragraph only |

**Rule:** If it isn't **provisional PDF + two claims + prior-art diff**, it doesn't go in the first email.

---

## Quote checklist (when quote returns)

☐ Flat fee or capped fee stated  
☐ Micro-entity fee assumption documented  
☐ Government fees itemized separately  
☐ Draft + review rounds included  
☐ Filing deadline vs our calendar (`GATE_PATENT_DEADLINE_AT` / S1)  
☐ Assignment to **Nisaba LLC, Wyoming** confirmed  
☐ Narrow claim scope acknowledged (two families — not 112 modules)  

Log quote: `REALITY_CONTRACT_30DAY.md` S2 · `IP_OWNERSHIP_CHECKLIST.md` I2.

---

## After quotes (not this week unless quote is same-day)

- Gate 1 outbound may resume  
- Licensing term sheet goes to **licensing counsel** separately — not the conversion drafter's first packet  
- Wealth apparatus remains frozen until Gate 1 (`WEALTH_APPARATUS_FREEZE.md`)

---

*Counsel brief v1 · Aug 28, 2026 · Not legal advice · Nisaba LLC · Wyoming*
