# NAIC AI Risk Evaluation Supplement v5.0 — Written Comment Draft

**Status:** Draft for Demond review / edit / submit  
**Deadline:** Close of business **Tuesday, Sept 29, 2026**  
**To:** Scott Sobel (ssobel@naic.org), AI Policy Advisor  
**Cc:** Miguel Romero (mromero@naic.org), Director of Innovation, Cybersecurity and Technology  
**From:** [Demond Davis / Nisaba LLC — confirm legal name and title before send]  
**Re:** Written comment on AI Risk Evaluation Supplement version 5.0  
**Public follow-up:** Big Data and AI (H) Working Group Webex, Oct 8, 2026, 11:00 a.m. ET

> Do not paste product marketing into this letter. The value of the comment is that it answers the Supplement’s own new questions with operational language regulators can reuse. Edit freely. Submit before Sept 29 even if other roadmap items are unfinished.

---

## Suggested email cover (short)

Subject: Written comment — AI Risk Evaluation Supplement v5.0 (agentic AI definition; Exhibit B 3p; materiality threshold; Exhibit A inventory)

Dear Mr. Sobel and Mr. Romero,

Please accept the attached written comment on AI Risk Evaluation Supplement version 5.0. It focuses on four additions in this draft that will determine whether market-conduct exams produce **provable** AI oversight or **asserted** AI oversight:

1. the first formal definition of “agentic AI,”
2. Exhibit B question 3p (third-party AI model oversight),
3. company-specified materiality thresholds, and
4. the Exhibit A Model Inventory.

I would welcome the chance to discuss at the Oct 8 public Webex if useful.

Respectfully,  
[Demond Davis]  
[Title], Nisaba LLC  
[Phone] · [Email]

---

## Suggested comment letter (body)

**Written Comment of Nisaba LLC**  
**AI Risk Evaluation Supplement, Version 5.0**  
**National Association of Insurance Commissioners — Big Data and AI (H) Working Group**  
**Date:** [submit date, on or before Sept 29, 2026]

### I. Interest of the commenter

Nisaba LLC builds Gate and Velaru: systems that clear high-stakes automated actions only when a fail-closed control path can produce a **stranger-verifiable receipt** — a signed record naming what was attempted, who authorized it, what policy applied, and whether clearance was granted or denied. We submit this comment because version 5.0 of the Supplement moves the exam framework onto the exact terrain those systems already occupy: agentic AI, third-party model oversight, disclosed materiality, and inventoryable model populations.

We are not asking NAIC to endorse a vendor. We are asking the Working Group to write the Supplement so that a company can **prove** the answers it will soon be required to give, rather than only assert them.

### II. Support for scoping “agentic AI” — and one request for exam operability

Version 5.0’s formal definition of “agentic AI” is the right move. Market-conduct work that stops at generative chatbots will miss the irreversible actions already occurring in claims, underwriting referral, utilization management, tenant-adjacent insurance products, and payment initiation.

**Request:** Keep the definition tied to **action authority and irreversibility**, not to model architecture labels. For exam purposes, the useful question is not “does the vendor call this an agent?” It is:

> Can this system initiate or materially influence an irreversible outcome (payment, denial, binding decision, account restriction, coverage determination) without a contemporaneous, attributable control record?

If the Supplement’s definition of agentic AI is read that way, Exhibit A inventories and Exhibit B oversight answers become testable. If it is read as marketing taxonomy, companies will inventory chat features and miss the write-paths that create consumer harm.

### III. Exhibit B, question 3p — third-party AI oversight must be provable, not promissory

Exhibit B’s new question 3p asks how a company oversees third-party AI models. That is the right question. The default industry answer today — “we reviewed the vendor’s documentation and rely on their controls” — is not oversight. It is **delegation without evidence**.

For 3p to function in a market-conduct exam, the Supplement should make clear that a satisfactory answer identifies **artifacts**, not assurances. Minimally, a company should be able to produce, for each in-scope third-party model or agentic service:

1. **Named accountability inside the licensee** — a natural person (or named role with a sitting occupant) responsible for the third-party use, not a vendor contact.
2. **A control environment description that is specific to the write-path** — what irreversible actions the third party can trigger in the licensee’s book of business.
3. **An attestation trail a stranger to the vendor relationship can check** — for example, signed clearance receipts, deny/allow logs with policy versions, or independent verification URLs — not only a SOC report summary controlled by the vendor.
4. **Fail-closed behavior when oversight inputs are missing** — if inventory metadata, policy version, or attestation channel is unavailable, the high-stakes action does not proceed by default.

**Concrete answer to the practical question 3p raises:**

> How would a company prove third-party oversight rather than assert it?

By retaining, for sampled transactions, a receipt that a regulator or independent examiner can verify without trusting the vendor’s dashboard: what action was requested, which third-party model or agent was in path, which licensee policy version applied, who/what authorized clearance, the allow/deny outcome, and a cryptographic or otherwise independently checkable signature bound to that record. Oversight is the ability to produce that trail under exam. Anything less is narrative.

We encourage NAIC to state explicitly in 3p guidance or examiner notes that **vendor self-attestation alone is insufficient** for material third-party agentic uses, and that companies should expect sample-based testing of oversight artifacts.

### IV. Self-specified materiality thresholds — disclose, then bind

Requiring companies to specify and disclose their own materiality threshold is realistic. It also creates a visible integrity gap: a firm can set a convenient threshold, disclose it, and never prove that production systems actually enforce it.

**Request:** Pair disclosure with an exam expectation that the disclosed threshold is **operational**, not ornamental. A company should be able to show:

- the threshold value and effective date,
- the systems and third parties in scope above that threshold,
- at least one control that changes behavior at the threshold (review, dual control, deny-by-default, escalation), and
- a timestamped record that the threshold in force at decision time matches the disclosed threshold.

Without that binding, “self-specified materiality” becomes a paper control. With it, the Supplement creates a fair, company-specific bar that still supports examination.

### V. Exhibit A Model Inventory — make it exportable and decision-linked

A Model Inventory requirement is only as strong as its freshness and its link to real decisions. We support Exhibit A and ask that examiner guidance prefer inventories that are:

- **exportable** in a machine-readable form,
- **mapped to business write-paths** (not only to model names),
- **tagged for agentic / non-agentic uses** using the Supplement’s new definition, and
- **reconciled to third-party entries that feed question 3p**.

An inventory that cannot explain which irreversible consumer outcomes a listed model can influence will not help an examiner. An inventory that can will.

### VI. Alignment with the Model Bulletin’s accountability direction

We note separately that staff work converting the 2023 AI Model Bulletin into disclosure components — including board/senior-management attestation naming an executive responsible for AI governance — points in the same direction as Sections III–V above: **named accountability**, **documented controls**, **verifiable attestation**. Version 5.0 of the Supplement is the exam-facing place to make those ideas operational for agentic and third-party systems. We support that trajectory.

### VII. Closing

Version 5.0 correctly expands the frame to agentic AI, third-party oversight, disclosed materiality, and model inventory. The Working Group’s remaining drafting choice is whether those additions produce **exam-ready proof** or **exam-ready prose**.

We urge the Working Group to:

1. keep the agentic-AI definition centered on irreversible action authority,
2. treat Exhibit B 3p as a demand for oversight artifacts, not vendor reassurance,
3. require self-specified materiality thresholds to be enforceable and reconcilable to production records, and
4. expect Exhibit A inventories to be exportable and linked to real decision paths.

Thank you for the opportunity to comment. I am available for questions before or during the Oct 8, 2026 public discussion.

Respectfully submitted,  

[Demond Davis]  
[Title]  
Nisaba LLC  
[Address — founder-supplied if required]  
[Email] · [Phone]

---

## Examiner-note addendum (optional attachment; keep short)

If useful as a one-page appendix, these are sample “show me” probes consistent with the comment:

| Supplement hook | Examiner probe | Weak answer | Strong answer |
|---|---|---|---|
| Agentic AI definition | Show one production path that can deny, bind, pay, or freeze without a human click | “We use GenAI for summaries only” | Named write-path + allow/deny receipt for a sampled case |
| Exhibit B 3p | For a third-party model, show oversight evidence independent of the vendor UI | “Vendor SOC 2 / questionnaire” | Licensee-held receipt/log with policy version + accountable owner |
| Materiality threshold | Show the disclosed threshold and a control that fires at/above it | Threshold on a policy PDF only | Threshold ID on decision records + behavior change evidence |
| Exhibit A inventory | Export inventory and map two entries to consumer outcomes | Spreadsheet of model nicknames | Machine-readable inventory linked to write-paths + 3p vendors |

---

## Pre-submit checklist (Demond)

- [ ] Confirm sender legal name / title / contact block
- [ ] Confirm whether to send as email body, PDF attachment, or both
- [ ] Do **not** claim NAIC endorsement, partnership, or borrowed institutional authority
- [ ] Do **not** paste pricing, Bind Room CTA, or product landing-page copy
- [ ] Optional: attach one **redacted** stranger-verifiable receipt as illustration of an oversight artifact (only if counsel is comfortable)
- [ ] Send to ssobel@naic.org and mromero@naic.org before COB Sept 29, 2026
- [ ] Calendar Oct 8, 2026 11:00 a.m. ET public Webex
- [ ] After submit: file a dated copy under `docs/naic/submitted/` with timestamp

## What this draft deliberately does not do

- It does not lobby for a proprietary standard by name as a regulatory mandate
- It does not attack carriers or vendors
- It does not claim Gate/Velaru are the only acceptable control pattern
- It does answer 3p with a concrete “prove it” test an examiner could run
