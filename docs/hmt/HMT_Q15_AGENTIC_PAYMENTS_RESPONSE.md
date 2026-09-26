# HM Treasury — Modernising Payment Services Regulation  
## Response to Question 15 (agentic payments)

**Status:** Draft for Demond review / edit / submit  
**Consultation:** [Modernising Payment Services Regulation](https://www.gov.uk/government/consultations/modernising-payment-services-regulation) (published 14 July 2026)  
**Deadline (reverified 2026-09-26):** **11:59pm on 6 October 2026**  
**Submit to:** Modernisingpaymentservices@hmtreasury.gov.uk  
**Postal:** Payments & Fintech team, HM Treasury, Horse Guards Road, SW1A 2HQ  
**From:** [Demond Davis / Nisaba LLC — confirm legal name and title before send]  
**Scope of this filing:** Question 15 only (other questions intentionally omitted)

### Question 15 (verbatim)

> How does existing payment services regulation need to adapt to support agentic payments? For example, do provisions relating to authentication and consent of payments transactions, and liability for unauthorised payment transactions, need updating?

---

## Suggested email cover

Subject: Response to Question 15 — Modernising Payment Services Regulation (agentic authentication, consent, liability)

Dear Payments & Fintech team,

Please find attached Nisaba LLC’s response to Question 15 of the Modernising Payment Services Regulation consultation. It addresses authentication, consent, and liability for agent-initiated payments by reference to a live clearance architecture already in production use on card-issuing agent authorizations — not only by naming the regulatory gap.

Respectfully,  
[Demond Davis]  
[Title], Nisaba LLC  
[Phone] · [Email]

---

## Response body

**Organisation:** Nisaba LLC (Gate / Velaru)  
**Date:** [submit on or before 6 October 2026]  
**Question answered:** 15

### 1. Short answer

Yes — authentication, consent, and liability rules written for human-present payment journeys need updating for **agent-initiated** payments. The update should not invent a new marketing taxonomy for “AI agents.” It should require that, before settlement of an irreversible payment instruction initiated by software acting for a payer:

1. **Authentication** binds the instruction to a named agent identity *and* to a contemporaneous control decision (allow / deny / hold), not only to a stored card-on-file or SCA exemption narrative.
2. **Consent** is expressed as a **mandate with enforceable bounds** (amount, counterparty / category, time window, job) that is checked at authorization time — not a one-time UX click months earlier.
3. **Liability** for unauthorised agent payments is allocated by reference to a **stranger-verifiable receipt** of that control decision, so a PSP, payee, payer, or supervisor can see what was checked when the deny or allow happened.

Those three updates are **closeable with existing rails**. Card networks and Issuing platforms already emit realtime authorization webhooks; what has been missing is a fail-closed clearance layer that mints an independently checkable artifact when the agent is outside mandate. Gate’s live Issuing mouth is one such layer. We cite it as evidence the gap is operationally solvable, not as a request to mandate a single vendor.

### 2. What breaks under today’s framing

PSR / SCA concepts assume a human is present at authentication, or that a carefully scoped exemption applies. Agentic payments invert that: the software initiates the irrevocable instruction while the human is absent. Without an update:

- “Authenticated” can mean only that a token once associated with a human was presented by software.
- “Consent” can mean a broad standing permission that does not constrain merchant category, job, or sealed payee at the moment of spend.
- “Unauthorised” disputes become narrative contests — the payer says the agent exceeded intent; the PSP says SCA passed — with no examiner-grade artifact of the control decision.

The Financial Services AI Adoption Plan’s observation that the UK lacks a standardised identity / verification framework for autonomous software agents is correct. Question 15 is the payments-perimeter place to require the **consequence boundary**, even before a full “know your agent” identity regime exists.

### 3. Architecture that already closes the gap (live)

Gate sits on Stripe Issuing `issuing_authorization.request` (sub-2s AUTHORIZE / DECLINE). Two layers:

| Layer | Who | What |
|---|---|---|
| Platform MCC floor | Stripe `spending_controls` | Coarse merchant-category allow/block at the issuer |
| Workflow lock | Gate card metadata `allowed_categories` / job / mandate | Fail-closed before Clear; deny mints signed `claim_scope` |

On every halt, Gate mints a stranger-openable artifact: decision, claim_scope (which logs / bounds were checked), Ed25519 signature, and (once leaves exist) Merkle inclusion against a published evidence-head. OpenTimestamps status for the head is surfaced when deployed; pending is labeled pending.

**Live checks (no login, no API key):**

- Mouth: `https://gate.velaru.xyz/issuing-mouth`
- Manifest: `https://gate.velaru.xyz/.well-known/issuing-mouth.json`
- Dogfood refuse outside allowlist:  
  `POST https://gate.velaru.xyz/demo/issuing/mouth`  
  body `{"allowed_categories":["fuel"],"merchant_category":"software"}`  
  → `approved:false`, `claim_scope.boundary=gate_issuing_workflow_category_lock`
- Regulator mapping + mintable receipt: `https://gate.velaru.xyz/regulator`

Honest limits we state on that page: demo calls set `demo:true`; `money_real` reflects Issuing+Stripe configuration, not that a particular demo moved funds; OTS well-known may still be pending deploy even when an offline Bitcoin attestation exists.

### 4. What we ask HMT / the future perimeter to require

Without prescribing Gate:

1. **Authentication for agent-initiated payments** must include a control-plane decision at authorization time, attributable to a named agent / mandate version — not only a credential that once belonged to a human.
2. **Consent** must be mandate-shaped and **re-checked at spend** (amount, counterparty or category class, purpose/job, expiry). Standing “the user enrolled an agent” is insufficient for irreversible settlement.
3. **Liability** for unauthorised agent payments should prefer PSPs that can produce a **stranger-verifiable allow/deny receipt** for sampled authorizations; absence of such an artifact should weigh against the party that could have required one and did not.
4. **MCC / category locks alone are not cart proof.** Regulation should not treat merchant category as SKU-level consent (IIAS / fleet product-code lesson). Workflow mandates are necessary above the MCC floor.

### 5. Closing

Question 15’s gap is real. It is also **closeable now** on card-issuing agent rails: authenticate the agent at authorization, bind consent to an enforceable mandate, and attach liability to a checkable clearance receipt. We urge HM Treasury to update authentication, consent, and liability provisions along those lines so UK agentic payments grow under exam-ready proof rather than under asserted controls.

Respectfully submitted,  

[Demond Davis]  
[Title]  
Nisaba LLC  
[Email] · [Phone]

---

## Pre-submit checklist

- [ ] Confirm sender legal name / title / contact
- [ ] Confirm deadline still 11:59pm 6 Oct 2026 on GOV.UK page
- [ ] Confirm email still Modernisingpaymentservices@hmtreasury.gov.uk
- [ ] Do not claim HMT endorsement or that Gate is the only acceptable pattern
- [ ] Do not paste Bind Room / pricing CTAs
- [ ] After send: file dated copy under `docs/hmt/submitted/`
