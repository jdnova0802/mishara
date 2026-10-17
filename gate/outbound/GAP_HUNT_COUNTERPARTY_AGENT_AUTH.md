# GAP HUNT — Counterparty identity / agent-authentication mouth

**26 Sep 2026.** Same bar as DSP / cross-domain EMPTY: real, dated, primary mandate → build; else say nothing.

**Asked concept:** A mouth that checks whether **counterparty identity / agent-authentication verification was actually performed and attested** before a write cleared — i.e. the counterparty is a genuine human or authorized agent, not synthetic/fraudulent. Explicitly **not** BioCatch-class deepfake detection.

---

## Verdict: EMPTY

**No live primary mandate clears the bar for that mouth.** Threat reports ≠ regulation. Do not ship.

---

## Context checked (not mandates)

| Claim | Status |
|-------|--------|
| BioCatch Jun 2026 survey — ~80% of FIs report agentic-AI attacks | **Vendor survey** (press 10 Jun 2026) — real as market signal, **not a duty** |
| INTERPOL 2026 Global Financial Fraud Threat Assessment — deepfake / agentic AI fraud | **Threat assessment** — https://www.interpol.int/ — **not a filing/attestation rule** |

---

## Candidates that look close — why they fail

| Candidate | Primary | Why it fails *this* mouth |
|-----------|---------|---------------------------|
| **“AI agent authentication before payment” (US)** | No CFR / FR final rule found requiring discrete agent-identity attestation before a write | **Does not exist.** BSA/CIP attaches to the **legal-entity customer**, not the software agent (GENIUS/PPSI CIP NPRMs treat issuers as FIs with ordinary CIP — no agent category). |
| **FinCEN AML/CFT modernization NPRM** (91 FR / Apr 10 2026) | Encourages GenAI / digital identity as tools | **Proposed + risk-based encouragement** — not “attest agent auth before this write.” |
| **NYDFS Industry Letter IL20241016** (AI cyber risks) | Recommends deepfake-resistant MFA, liveness, verify unusual wires | **Nonbinding guidance.** Part 500.12 MFA is **access to systems**, not counterparty-of-payment attestation. |
| **PSD2/PSD3 SCA / agentic payments commentary** | SCA for payer; PSD3/PSR texts largely silent on AI agents; apply ~2028 | **Wrong object** (payer SCA ≠ counterparty-is-real). Not in force as agent-auth duty. |
| **EU Verification of Payee — Reg (EU) 2024/886 Art. 5c** | Euro-area PSP must offer name↔IBAN verification **before** payer can authorise credit transfer; euro-area deadline **9 Oct 2025** (ECB IPR table) | **Real mandate — wrong shape + wrong geography + occupied.** It is payee **account-name match**, not “is this an AI agent / not synthetic.” Banks + EPC VoP scheme + Eurosystem VoP already productize. Gate is US/Nisaba stack. |
| **UK Confirmation of Payee — PSR Specific Direction 17** | Directed PSPs must send/respond CoP (Group 1 by 31 Oct 2023; Group 2 by 31 Oct 2024) | **Real — already largely implemented.** Same shape as VoP (name check), not agent-auth. Occupied. |
| **Nacha False Pretenses / fraud monitoring** (Phase 1 **Mar 20 2026** / Phase 2 **Jun 19 2026**) | Risk-based procedures to identify entries unauthorized or authorized under False Pretenses (identity / authority / account-ownership misrep) | **Already shipped on Gate** as advisory mouth `/nacha-false-pretenses`. Risk-based **monitoring** framework — **not** a per-write “agent authentication verified” attestation rule. |
| **FedNow / RTP pre-push (FPC-style payee sealed)** | Industry control language; Gate advisory `/fednow-prepush` | **Already shipped.** Sealed payee / first-time payee — not agent-auth / liveness / synthetic-ID mandate. |
| **CIP / CDD / BOI** (31 CFR 1020.220, 1010.230, etc.) | Identity at **account opening** / beneficial ownership | **Wrong moment.** Not “before this irreversible write, attest counterparty agent-auth.” |

---

## What Gate already covers (so we don’t fake a duplicate)

| Mouth | What it attests | Not what it is |
|-------|-----------------|----------------|
| `/nacha-false-pretenses` | FP suspected? + who/what/payee sealed? | Not “AI agent authenticated” |
| `/fednow-prepush` | Payee sealed? first-time? fraud suspected? | Not deepfake / agent identity |
| Scenario 3 / trusted-contact / etc. | Other advisory seals | Not agent-auth |

Building “VERIFIED / NOT ATTESTED / HOLD” for agent-auth **without** a primary would be inventing a product on BioCatch/Interpol *threat* framing — fails DSP discipline.

---

## If a real mandate appears later (watchlist — do not build now)

| Watch | Why it might become a mouth |
|-------|------------------------------|
| Final US rule that **names agent / delegated initiator credentials** as a required pre-payment check | Would match asked shape |
| Binding US “Confirmation of Payee” / account-name verification **per credit** (not just Nacha risk-based monitoring) | Would be VoP-class; still different from agent-auth |
| PSD3/PSR RTS that explicitly binds **agent mandate + auth** with an attestation/report duty | EU; only if Gate expands geography |

Until one of those is **final + dated + primary**, answer stays EMPTY.

---

## One-liner for Claude

**EMPTY.** BioCatch/Interpol prove the *threat*; they are not a duty. No US (or binding agent-auth) primary requires “counterparty identity / agent-authentication verification attested before this write.” Closest real duties are EU VoP / UK CoP (name↔account, occupied, wrong geo) and Nacha/FedNow seals (**already on Gate**). Don’t force a mouth.
