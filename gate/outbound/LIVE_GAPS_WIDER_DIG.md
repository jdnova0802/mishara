# Live gaps / loopholes — Gate verification candidates (wider dig)

**Date:** 2026-09-24  
**Ask:** Adjacent to Bounded Autonomy insurance · vendor bank-change/BEC · agentic chargebacks.  
**Filter:** 2025–26 recency · named buyer · no seated accredited verifier for *this* proof · stranger-verifiable fail-closed · fits Gate without new eng.  
**Ruled out (do not re-surface):** litigation funding / court disclosure · crypto custody.

---

## Already parked (tonight’s three)

| # | Gap | Cash-this-month |
|---|-----|-----------------|
| A | Insurance Bind / Diligence (running) | **1 — finish Fri/Tue** |
| B | Vendor bank-change / BEC halt | **2** |
| C | Agentic chargeback / dispute receipt | 3 (mouth best, cash slower) |

---

## New candidates (ranked)

### 1) FedNow / RTP irrevocable push — “authorized but fraudulently induced”

**Gap:** Instant credit-push is final. Faster Payments Council (May 15, 2026) *Instant Payments Fraud Dispute Resolution* principles: unauthorized fraud has rules; **APP / fraudulently induced authorized payments fall into regulatory gaps**; dispute handling varies. Control is **verify before the push**, not chargeback after.

**Gate shape:** Clear (what was authorized) · Seal (callback / account-validation receipt) · Go / Never before the RTP/FedNow send. Same mouth as vendor-bank + wire; `rail_truth` already distinguishes irreversible rails.

**Buyer:** Community / regional banks rolling FedNow · mid-market AP / treasury · payment processors receiving RfP.  
**Why no verifier seated:** Networks don’t sell stranger-verifiable pre-push mandate receipts; crime-bond still argues procedure, not sealed hop.  
**Cash fit:** High — same Diligence REVIEW SKU; banks already feel BEC pain.  
**Recency:** May 2026 FPC principles · RTP rules refresh June 2026.

---

### 2) CA SB 1120 — AI in health-plan utilization review (statutory clock)

**Gap:** California SB 1120 (eff. ~Jan 2026) regulates AI/algorithms in UR/UM for health plans & disability insurers (and vendors). Disclosure + human accountability for approve/modify/delay/deny. Plans must be able to show *how* AI was used and that process meets fairness/non-discrimination — industry still scrambling on operational proof.

**Gate shape:** Seal that a **licensed clinician review** occurred before non-affirmation · Go only if human review ticket bound to that request · Never for AI-alone deny. Diligence memo on one UR path.

**Buyer:** CA health plans · specialty UR vendors · DMHC/DOI-facing compliance.  
**Why no verifier seated:** Law creates duty; no accredited “UR AI receipt” product.  
**Cash fit:** Medium-high — compliance budget, Diligence-sized; regulated but not 18-month weld.  
**Recency:** Active 2026 clock.

---

### 3) CMS WISeR — Medicare AI prior-auth model (live 2026)

**Gap:** WISeR AI-assisted prior auth live in multiple states (portals ~Jan 2026). CMS requires human clinical review on non-affirmations + audits; EFF FOIA (Sep 2026) shows delayed determinations, incomplete vendor testing, auto-affirm workarounds — **proof that human review + clock actually held** is the missing stranger artifact under CMS audit pressure.

**Gate shape:** Same as SB 1120 — bound review ticket · Seal before non-affirm · Never for silent AI deny.  
**Buyer:** WISeR participants / vendors (Innovaccer-class) · provider groups fighting delayed care.  
**Cash fit:** Medium — federal model = slower procurement; vendor diligence packs possible.  
**Recency:** Model live 2026; EFF records Sep 2026.

---

### 4) UFLPA / CBP Forced Labor Guidance (June 2026) — one-gap deny

**Gap:** CBP Publication 5560-0526 (Jun 2026): for UFLPA exception / applicability, **failure to document even one supplier at any tier → entire submission insufficient**; 30-day detention response clock; affidavits/redactions/untranslated docs fail. Admissibility is a **proof package** race.

**Gate shape:** Seal = Merkle’d, stranger-verifiable evidence pack tied to one entry/shipment · Never release claim without complete chain. Slightly more “document staple” than act-halt — still fail-closed on the **customs response write**.

**Buyer:** Importers of record in priority sectors · customs brokers · trade counsel.  
**Cash fit:** Medium — acute when detained ($); less recurring than AP/banks unless retainer on every entry.  
**Recency:** June 2026 operational guidance.

---

### 5) CA SB 7 / CCPA ADMT — employment / significant automated decisions

**Gap:** Notice + accountability when ADS materially affects employment (and CCPA ADMT significant decisions → 2027). Employers need prove-what-the-system-decided + notice given — still almost no stranger-verifiable decision receipt.

**Gate shape:** Seal decision + notice receipt; weaker irreversible-money hop.  
**Buyer:** CA employers using hiring/comp ADS · HR tech vendors.  
**Cash fit:** Lower than 1–2 for Gate (policy/notice product overlaps HRIS vendors).  
**Park unless** a named employer asks for Diligence on one ADS path.

---

### 6) SNAP / benefits synthetic identity (park)

**Gap:** USDA FNS integrity work — dummy SSNs / duplication = $B risk; NIST-aligned ID proofing still uneven across assistance programs.  
**Buyer:** State agencies / EBT processors — **institutional**, not cash-this-month.  
**Park** with crypto / litigation funding.

---

## Recommended stack (do not hijack insurance week)

| Priority | Move |
|----------|------|
| Now | Insurance Fri bumps → Tue 10 |
| Next Plan B list | **FedNow/RTP pre-push verify** (extends vendor-bank mouth) |
| Parallel Diligence packs | **SB 1120 UR** (CA health plans) |
| Later / detention heat | UFLPA evidence Seal |
| Architecture later | WISeR if a WISeR vendor pays for REVIEW |

**Architecture note:** #1 (instant payments) + vendor-bank = same who-may-spend atom on irreversible money. Shipping that atom once serves both. Chargebacks stay third. Health UR (#2–3) is the clean **non-money** statutory-clock analog to AB 316.

---

## Explicit non-candidates tonight

- Litigation funding / court disclosure (ruled out)  
- Crypto custody (ruled out)  
- Generic “AI governance” / SOC2 theater (accredited monitors already seated)  
- Full MCP enterprise gateway (build war with Stacklok/Obot — not Diligence-shaped)
