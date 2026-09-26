# NAIC BDAIWG — Oct 8, 2026 verbal comment (2–3 minutes)

**Status:** Draft for Demond — speak only after re-confirming the Webex on the Working Group page  
**Session (reverified 2026-09-26):** Thursday, October 8, 2026, **11:00 a.m. ET** — BDAIWG public Webex to discuss AI Risk Evaluation Supplement v5.0 comments  
**Sources:** Aug 31 BDAIWG materials timeline (“BDAIWG Mtg. for comment on v. 5.0” in October); secondary reporting (AI Guardian, InsureAI Wire) naming Oct 8 11:00 a.m. ET  
**Confirm before dialing:** https://content.naic.org/committees/h/big-data-artificial-intelligence-wg — Webex link / agenda may post late  
**Anchor:** Same four asks as the written comment draft (`NAIC_AI_RISK_EVAL_SUPPLEMENT_V5_COMMENT_DRAFT.md`, COB Sept 29). **There is no Sept 14 filed letter in this repository** — do not invent one on the call. If a written letter was sent under a different date, cite the sent copy under `docs/naic/submitted/`.

**Live proof (after deploy):** https://gate.velaru.xyz/regulator

---

## Spoken script (~450 words / ~2.5 min)

Good morning, Chair, members, and staff. Demond Davis, Nisaba LLC.

I’m here on the same four points as our written comment on Supplement version 5.0 — not a new ask, a second appearance on the same door.

**First — agentic AI.** Keep the definition tied to **irreversible action authority**, not architecture labels. The exam-useful question is: can this system initiate or materially influence a payment, denial, bind, account freeze, or coverage determination without a contemporaneous, attributable control record? If “agentic” means chatbots, inventories will miss the write-paths that create consumer harm.

**Second — Exhibit B, 3p.** Third-party AI oversight must be **provable artifacts**, not vendor reassurance. A satisfactory answer names licensee accountability, the write-path the third party can trigger, and an attestation trail a stranger to the vendor relationship can check — signed clearance receipts, deny logs with policy versions, independent verify URLs. Vendor SOC summaries alone are not oversight.

**Third — materiality.** Self-specified thresholds are realistic only if they are **enforceable**. Disclose the value and effective date, show which systems sit above it, show a control that changes behavior at the threshold, and show that the threshold in force at decision time matches what was disclosed.

**Fourth — Exhibit A.** Inventories should be **exportable and linked to real decision paths** — tagged agentic / non-agentic under the Supplement’s definition, reconciled to 3p vendors, mapped to irreversible consumer outcomes — not a spreadsheet of nicknames.

We are not asking NAIC to endorse a vendor. We built Gate so those four asks are testable today: agent card authorizations hit a fail-closed Clear mouth before settlement; refusals mint a signed claim_scope; a stranger can open a receipt, check Merkle inclusion against the published evidence-head, and read OpenTimestamps status — no login. That surface is at gate.velaru.xyz/regulator, separate from any commercial page. Anything still pending — empty tree before first sample, OTS well-known not yet on prod — is labeled pending, not dressed as confirmed.

Thank you. Happy to take questions.

---

## Timing marks

| Mark | Line |
|---|---|
| 0:00 | Intro + “same four points” |
| 0:25 | Agentic / irreversible |
| 0:55 | Exhibit B 3p artifacts |
| 1:25 | Materiality enforceable |
| 1:50 | Exhibit A decision-linked |
| 2:15 | Live verify URL + honest limits |
| 2:40 | Close |

## Pre-call checklist

- [ ] Re-open NAIC BDAIWG page; confirm Oct 8 still listed and grab Webex URL
- [ ] Confirm written comment was actually sent; if yes, file under `docs/naic/submitted/` and cite that date on the call
- [ ] Do **not** say “our September 14 letter” unless a submitted copy with that date exists
- [ ] Open `/regulator` and mint one sample so a staffer can click during Q&A
- [ ] No pricing, Bind Room, or diligence pitch on this call
