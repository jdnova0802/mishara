# PASTE — FinCEN / IRS whistleblower reward × Gate evidence-head

**Hunt date:** 27 Sep 2026  
**Verdict:** **Does not fit as a Gate product / bounty path.** Programs are real. Incidental tip-from-Never is a category error. Do not build a whistleblower SKU.

---

## Programs (real, cited)

| Program | Award | Threshold / form | Status |
|---|---|---|---|
| **FinCEN** AML / sanctions whistleblower — 31 U.S.C. § 5323 (AML Act 2020 + **AML Whistleblower Improvement Act 2022**) | **10–30%** of collected monetary sanctions | Covered action sanctions **>$1M**; BSA, IEEPA, TWEA, Kingpin | Tips accepted via FinCEN portal; **NPRM** *Whistleblower Incentives and Protections*, **91 Fed. Reg. 16328** (Apr 1, 2026). Awards not paid until rule final. |
| **IRS** Whistleblower Office — IRC **§ 7623** | **15–30%** of collected proceeds | Mandatory §7623(b): proceeds in dispute **>$2M** (+ individual GI >$200k); else discretionary §7623(a) | **Form 211** — specific, timely, credible original information |

FinCEN NPRM (proposed 31 CFR 1010.930): whistleblower = **natural person(s)** only. Corporations / LLCs / trusts **ineligible**. Tip must be **original information** (independent knowledge or independent analysis) relating to a **covered-statute violation**, submitted on Form TCR, leading to successful enforcement.

Sources:  
https://www.federalregister.gov/documents/2026/04/01/2026-06271/whistleblower-incentives-and-protections  
https://www.fincen.gov/news/news-releases/fincen-proposes-rule-pay-whistleblowers  
https://www.irs.gov/help/submit-a-whistleblower-claim-for-award  
https://uscode.house.gov/view.xhtml?req=(title:31%20section:5323%20edition:prelim)

---

## Key distinction (do not blur)

| Lane | What it is | Gate today |
|---|---|---|
| **Prevention at write-time** | Fail-closed Clear / Never / deny before irreversible payout | **This is Gate** |
| **Detective / tip / bounty** | Someone who *knows* a BSA/sanctions/tax violation reports it for an award | **Not Gate** |

Turning Gate into a bounty-hunting operation would invent a SKU we do not have and that the statutes are not written for.

---

## What Gate Never / HOLD / evidence-head actually are

| Word / surface | Operational meaning | Keyed by | AML/sanctions finding? |
|---|---|---|---|
| **NEVER** | No redeemed bind-ticket leaf on the **spend map** for this `job_id` (Laurie–Kasper exclusion). May be ABSENT or weaker IN_FLIGHT. | `job_id` | **No** |
| **SPENT** | Redeemed leaf present for that job | `job_id` | **No** |
| **HOLD** | Prefinality: wait — a person must look | transfer fingerprint / mandate | **No** (uncertainty, not accusation) |
| **NO_GO** | Prefinality / Issuing / workflow refuse | mandate, category, cap, etc. | **No** — clearance deny, not “this payee is a mule” |
| **deny_registry** | Append-only **payout_hash** (sha256 of rail/amount/currency/destination…) | hash only, **no PII** | **No** |
| **evidence-head** | Merkle head over **receipt_hash** leaves | bind event receipts | Custody of clearance, not a tip file |
| **counterpart** | Optional fingerprint on ticket | `counterpart_id` (+ kind/path) | Identity binding for redeem — not OFAC/BSA adjudication |

Code anchors: `gate/never_ui.py`, `gate/exclusion.py`, `gate/deny_registry.py`, `gate/counterpart.py`, `gate/go_ui.py`, `gate/claim_scope.py`.

**There is no cross-customer “same counterparty → NEVER” radar today.** NEVER is not counterparty-keyed. Even if you built one over Issuing merchant strings or deny destinations, a cluster of Gate refusals still proves only that **welded writes were refused** — not that a covered statute was violated.

---

## The hypothetical, answered

> If the same counterparty triggers NEVER across unrelated Gate customers, is that pattern itself a legitimate FinCEN/IRS tip?

**No — not by itself.**

1. **Category error.** NEVER across customers (even if you redefined it around a payee) is a **clearance pattern**. Whistleblower awards require information about a **violation of BSA / sanctions / Kingpin (FinCEN) or internal revenue laws (IRS)**. “Three carriers’ agents got NO_GO paying Acme” ≠ “Acme laundered money / evaded sanctions / underpaid tax” without independent facts about the underlying offense.
2. **Wrong whistleblower.** Nisaba LLC / Gate **cannot** be the award claimant (entity ineligible). The whistleblower would have to be a **named natural person** with independent knowledge/analysis — typically a customer compliance officer or other individual, not “the platform.”
3. **Original information bar.** Aggregation of Gate logs may be *analysis*, but only if it yields **material insight into a covered violation**. Bare multi-tenant refuse counts do not clear that bar.
4. **Consent / confidentiality.** Cross-customer pattern disclosure without each customer’s control would be a data-product we do not have and should not invent under a bounty banner.
5. **IRS mismatch.** Evidence-head / Never are not tax books, TINs, or underpayment narratives Form 211 expects.

### Who would be the whistleblower if anything were ever submitted?

| Actor | Eligible? | Notes |
|---|---|---|
| Gate / Nisaba LLC | **No** | Entity |
| Gate employee acting as individual | Theoretically possible; often **120-day internal wait** if officer/compliance/auditor under NPRM; employer duties + privilege exclusions | Not a product path |
| **Customer’s** natural-person compliance officer | Yes *if* they have independent knowledge of a covered violation | Gate receipts could be **supporting exhibits**, not the tip itself |
| Automated Gate “tip bot” | **No** | Not a natural person; not original knowledge |

---

## Does claim_scope / evidence already contain what the programs require?

| Required for a serious tip | In Gate today? |
|---|---|
| Specific alleged **covered-statute violation** | **No** — mouths record clearance outcomes |
| Subject identity usable for enforcement (name, TIN, SDN nexus, etc.) | **Mostly no** by design (hashes, job_ids, optional counterpart fingerprints; deny registry strips PII) |
| How/when tipster learned it; relationship to subject | **No** — Form TCR / Form 211 narrative fields |
| Signed allow/deny receipt for a write attempt | **Yes** — useful as **appendix**, not as the tip |
| Cross-customer payee clustering | **Not built**; NEVER can’t do it; deny hashes would need shared destination encoding + legal basis |

So: existing artifacts are **supporting custody**, not whistleblower-complete packages. Filling the gap would mean building an AML investigative product — outside Gate’s prevention lane.

---

## Closest *legitimate* adjacency (still not a bounty SKU)

If a welded customer’s **own** compliance person already believes Vendor X violated the BSA/sanctions/tax law, they may want a pack of **their** signed NO_GO / deny / claim_scope receipts naming that counterpart fingerprint as exhibits for counsel → Form TCR / Form 211 / SAR.

That is:

- **Customer-owned export of their own clearance history**
- Explicit labels: Gate is not the whistleblower; Gate does not file tips; no award share; no cross-tenant fusion
- Adjacent to existing FinCEN Scenario 3 mouth language (`gate/mouths.py` FIN-2016-A003) — scenario match ≠ tip filing

**We do not build that in this hunt** unless separately asked. It is not the FinCEN/IRS reward mechanism; mislabeling it as “whistleblower product” would recreate the blur this hunt forbids.

Related **obligation** lane (also not bounty): SAR filing duties of BSA-covered customers. Gate may eventually help *their* SAR narrative with receipts. That is compliance tooling, not 10–30% awards.

---

## What we will not build

- Cross-customer bounty radar / “tip from Never”
- Gate-as-whistleblower or award-sharing SKU
- Auto-submit to FinCEN / IRS
- Any claim that HOLD/NEVER/NO_GO = money-laundering finding

---

## Bottom line

| Question | Answer |
|---|---|
| Are FinCEN 10–30% / IRS 15–30% real? | **Yes** — cited above; FinCEN awards await final rule |
| Do Gate Never/HOLD/evidence-head incidentally mint reportable tips? | **No clean fit** — wrong semantics, wrong claimant, missing violation facts |
| Build something for the reward programs? | **No** — honest empty, same standard as other “doesn’t fit” hunts |
| Any small real build? | **Not for whistleblower rewards.** Optional later: customer-owned receipt export for *their* counsel — separate ask, not this SKU |

Prevention stays Gate. Detection bounties stay individuals who know something specific.
