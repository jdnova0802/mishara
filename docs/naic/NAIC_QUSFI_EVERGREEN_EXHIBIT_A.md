# Technical submission — QUSFI membership, the evergreen clock, Exhibit A

**Status:** Draft. Not filed. Do not describe this file as a submitted comment.  
**To:** Scott Sobel (ssobel@naic.org), AI Policy Advisor  
**Cc:** Miguel Romero (mromero@naic.org), Director of Innovation, Cybersecurity and Technology  
**From:** Nisaba LLC  
**Re:** Big Data and AI (H) Working Group priorities — GLMs, direct consumer impact, materiality, Exhibit A design  
**Date:** 27 October 2026

This note answers those four labels with one mechanism that already runs in public code. It is not a request to adopt a vendor. The mechanism is a dated set-membership check plus one clock. A company can show the check to an examiner without treating it as a model score.

Public object, no login: `https://gate.velaru.xyz/.well-known/finding/ccb-svo.json`  
List head: `https://gate.velaru.xyz/.well-known/qusfi.json`  
Check: `POST /v1/qusfi/check`

---

## 1. GLMs

Qualified U.S. financial institution status is not a generalized linear model and should not be stored as one.

The Securities Valuation Office publishes a list of institutions whose letters of credit may support credit for reinsurance under Model Law #785, sections 3C(1) and 4A. Membership is a row on a dated PDF. Gate stores two editions and their SHA-256 hashes:

- 31 December 2025, archive on content.naic.org
- 30 September 2026, the list the SVO is still serving

A lookup answers on-list or off-list for one ABA or LEI, against those hashes. It does not estimate a probability, assign a rating, or produce a factor an insurer should drop into a GLM. The list’s own footer says it is not for other uses. Putting “CCB off list” into a pricing or underwriting GLM would be that other use.

What belongs in a model inventory, if a company uses this check at all, is the check itself: inputs (ABA, confirmation channel, event), the list edition, and the word returned (HALT, HOLD, or CLEAR). Not a coefficient.

## 2. Direct consumer impact

The consumer holds the policy the fronting carrier bound. The carrier remains liable for the claim whether or not the reinsurer’s collateral is admissible.

Guidewire’s Cloud API documents a single call that creates that obligation before the policy is issued:

`POST /job/v1/jobs/{jobId}/bind-only`

No body. The submission status becomes Bound. Issuance, which produces documents, is a later call. Wrapping only bind-and-issue leaves this write open. The contract already exists.

The consumer-facing failure mode is not an unexplained score. It is a bound policy whose unauthorized reinsurance stops supporting surplus at the next collateral event, while the issuing carrier is still the one the consumer can sue. SSAP No. 62R charges the unauthorized-reinsurance provision directly to surplus, dollar for dollar, to the extent acceptable collateral is missing.

The intercept that matches the write is `POST /job/v1/jobs/{jobId}/bind-only` and no other Cloud API spend. bind-and-issue and `POST /policy/v1/policies/{policyId}/issue` are refused and not forwarded. A bind proceeds only after a one-time ticket for that exact path redeems, and only if a PolicyCenter base URL is configured. If that host times out, the response is halt and `bound: false`. `their_production` stays false until a third party records a production weld. A laboratory forward is not that record.

Phone or email confirmation of the letter is halt. That channel is the one Corinthian reported it had already used on the China Construction Bank letters, as covered by Artemis, and the one AIRROC describes as a spoofed bank line. The allowed channel in this check is an MT760 advised through the beneficiary’s own bank. The channel is still not a substitute for list membership at the next renewal.

## 3. Materiality

The material event is already in Model Regulation #786 §11A(3). A letter that was acceptable when issued stays acceptable until expiration, extension, renewal, modification, or amendment, whichever happens first. A later list does not, by itself, void that paper.

That is the materiality rule. A company-chosen percentage is a different question and a weaker one. The check encodes the statute’s event, not a threshold:

- `event=evergreen` (or renewal, extension, modification, amendment, new issuance) and the issuer is off the current list → HALT. The next evergreen cannot support surplus credit.
- `event=grandfathered` and the issuer is off the current list → HOLD. The letter may still be security. The next evergreen cannot.
- Issuer on the current list, and confirmation is advised MT760 through the beneficiary’s own bank → CLEAR. CLEAR is not a production weld and not a bank-quality score.

Worked example, read from the two hashed lists, not from a narrative: ABA `26014685`, China Construction Bank Corporation, New York, is on the 31 December 2025 list and is not on the 30 September 2026 list. The finding states that fact, the grandfather sentence, and the negative: absence from the later list is not itself a finding that the letters were forged. Institutions also leave the list for not paying the annual fee.

Lloyd’s bulletin Y5410 (3 October 2023) is a separate six-month issuing-bank confirm for Funds at Lloyd’s. If that confirm is missing or older than six months, a Funds-at-Lloyd’s check halts. Y5410 does not decide Model 785 surplus credit. The public object says so.

## 4. Exhibit A design

An Exhibit A row that an examiner can test has five fields. Nicknames fail the test.

| Field | This mechanism |
|---|---|
| Decision | Bind, or refuse to bind |
| Write | `POST /job/v1/jobs/{jobId}/bind-only` |
| Inputs | Issuer ABA or LEI, confirmation channel, event (evergreen or grandfathered) |
| Source edition | List as-of date and PDF SHA-256, both on `/.well-known/qusfi.json` |
| Output | HALT, HOLD, or CLEAR, plus the finding hash at `/.well-known/finding/ccb-svo.json` |

The finding is canonical JSON. Its SHA-256 and Ed25519 signature are on the object. A stranger drops the signature fields, recomputes the hash, and checks the signature. No account is required. If any claim in the body changes, the hash moves.

The same row should name the third party that would perform the write (the PolicyCenter host) and state whether that host has been connected. Unset is an honest state. A spreadsheet that says “collateral AI” and does not name the write is not an inventory of this decision.

---

## What this submission does not ask

- It does not ask the Working Group to treat list membership as a GLM feature.
- It does not ask examiners to treat a vendor CLEAR as credit for reinsurance. The domiciliary commissioner remains the authority. A confirming bank that is itself qualified is a different path from an issuer that is on the list.
- It does not ask NAIC to file this draft. Status remains draft until a sent copy is stored under `docs/naic/submitted/`.
