# PASTE TO CLAUDE — Counterparty / agent-auth mouth hunt

**26 Sep 2026.** Same bar as DSP. Monday untouched.

## Asked
Mouth: was **counterparty identity / agent-authentication verification** actually performed and attested before the write cleared (human or authorized agent, not synthetic). **Not** deepfake ML.

## Verdict: **EMPTY — do not build**

No live primary mandate clears the bar for that classifier.

## Context ≠ mandate
- BioCatch Jun 2026 survey (~80% FIs report agentic-AI attacks) — vendor survey
- INTERPOL 2026 Global Financial Fraud Threat Assessment — threat intel, not attestation rule

## Near-misses (fail)
| Candidate | Why fail |
|-----------|----------|
| US “AI agent auth before pay” | **No CFR / final rule found** |
| FinCEN AML NPRM Apr 2026 | Encourages tech; not per-write agent-auth attest |
| NYDFS AI Industry Letter Oct 2024 | **Guidance**; 500.12 = system MFA not counterparty |
| PSD2/3 SCA | Payer auth, not counterparty-is-real; agent silence |
| EU VoP Reg 2024/886 Art 5c (euro VoP by **9 Oct 2025**) | **Real** but name↔IBAN, EU, occupied |
| UK CoP PSR SD17 | **Real**, largely done, occupied, same shape |
| Nacha False Pretenses Mar/Jun 2026 | Risk-based monitoring — **already** `/nacha-false-pretenses` |
| FedNow payee sealed | **Already** `/fednow-prepush` |
| CIP/CDD | Account opening, wrong moment |

## Already on Gate
`/nacha-false-pretenses` · `/fednow-prepush` — payee/FP seals, **not** agent-auth.

## One-liner
**Threat is real; the regulatory mouth isn’t. EMPTY — same honesty as the cross-domain gap hunt. Don’t invent VERIFIED/NOT ATTESTED without a citation.**

Full write-up: `gate/outbound/GAP_HUNT_COUNTERPARTY_AGENT_AUTH.md`
