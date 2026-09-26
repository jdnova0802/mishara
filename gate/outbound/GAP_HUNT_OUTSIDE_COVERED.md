# Real gap hunt — outside insurance / payments / agent verify / attestation

Bar: dated, primary-source-backed, no vendor already occupying, solo + $0 can act *now*.

## Verdict

**One micro-gap clears.** Bigger “obvious” 2026 duties mostly fail (stayed, deferred, vacated, or already productized).

---

## CLEARS (narrow): DOJ Data Security Program — rejected prohibited data-brokerage report

**Duty (live):** Any U.S. person that, on or after **October 6, 2025**, receives and **affirmatively rejects** (including **automatically rejected by software**) an offer to engage in a **prohibited transaction involving data brokerage** must file a report with DOJ NSD **within 14 days**.

**Primary sources**
- 28 C.F.R. § 202.1104 — [eCFR](https://www.ecfr.gov/current/title-28/chapter-I/part-202/subpart-K/section-202.1104)
- Final rule effective Apr 8, 2025; § 202.1104 operative Oct 6, 2025 — 90 Fed. Reg. 1636 (Jan 8, 2025) — [Federal Register](https://www.federalregister.gov/documents/2025/01/08/2024-31486/preventing-access-to-us-sensitive-personal-data-and-government-related-data-by-countries-of-concern)
- DOJ NSD Compliance Guide (Apr 11, 2025) — [justice.gov PDF](https://www.justice.gov/opa/media/1396356/dl)
- Filing: Subpart L → email `NSD.FIRS.datasecurity@usdoj.gov` (or official electronic option) — 28 C.F.R. § 202.1201 — [eCFR](https://www.ecfr.gov/current/title-28/chapter-I/part-202/subpart-L/section-202.1201)
- FAQs updated Sep 24, 2025 — [justice.gov](https://www.justice.gov/nsd/data-security)

**Why it’s structurally weird (and open)**
- The regulated act is not “do the deal” — it’s **rejecting** a prohibited offer, then still owing a timed federal report.
- The rule text itself contemplates **automated rejection tooling** as a trigger.
- Broader DSP “data compliance program” GRC has vendors (e.g. Tandem blog content). **No product found that markets the narrow § 202.1104 reject→14-day→NSD packager / classifier.** Searches on `202.1104` / “rejected prohibited” return statute + DOJ PDF only.

**$0 act-now shape (not a new bank, not float)**
1. Public mouth: “Was this inbound offer a prohibited data-brokerage covered-data transaction?” → GO / NEVER / HOLD with **claim_scope** = which DSP elements checked.
2. If NEVER (rejected): pack § 202.1104(c) fields + **14-day clock** + mailto / draft to NSD.
3. Explicit IN_FLIGHT: clock running after reject, before email sent.

**Honesty limits (do not oversell)**
- Event volume is unknown — possibly rare. A real duty ≠ a warm buyer list.
- Broader DSP compliance is *not* empty; only this **reject-report mouth** looks empty.
- Wrong classification is legal risk — fail closed; don’t file for the user without them owning the send.
- Covered Persons List is **non-exhaustive** for § 202.211(a)(1)–(4) (DOJ FAQ) — any tool must say so in signed scope.

---

## DOES NOT CLEAR (checked, with why)

| Candidate | Dates / primary | Why it fails the bar |
|---|---|---|
| CA Delete Act / DROP | Civ. Code 1798.99.80–.86; broker process from **Aug 1, 2026** (45-day cycle); CPPA registry | Occupied (privacy SaaS). Brokers owe **$6k** fee — not $0 for the regulated party. |
| CA SB 261 climate risk | H&S Code 38533; statutory **Jan 1, 2026**; 9th Cir. injunction **Nov 18, 2025**; CARB won’t enforce pending appeal | Stayed. Crowded ESG disclosure stack. |
| FSMA 204 food traceability | Original compliance **Jan 20, 2026**; Congress: no enforce before **Jul 20, 2028** (FDA page + CRS) | Deferred. Food-tech vendors already selling KDEs/CTEs. |
| CIRCIA cyber reporting | NPRM Apr 4, 2024; **final rule not effective** (CISA) | No live mandatory duty to productize yet. |
| CMS-0057 prior-auth APIs | Ops ~2026; APIs generally **Jan 1, 2027** (CMS-0057-F) | Heavy vendor occupancy (Firely, Onyx, …). Not $0→payer. |
| HIPAA reproductive privacy attestation | Vacated **Jun 18, 2025** (*Purl v. HHS*); HHS did not appeal | Duty removed. Remaining Part 2 NPP was **Feb 16, 2026** — HHS published free model notices. |
| FCC TCPA one-to-one consent | Vacated by 11th Cir.; FR **Aug 29, 2025** restored prior text | Vacated duty — not a gap to occupy. |
| CFPB § 1033 open banking | Final rule; E.D. Ky. injunction **Oct 29, 2025** blocking enforcement during reconsideration | Enjoined / being rewritten. Also payments-adjacent. |
| SEC climate disclosure | Stayed; SEC proposing rescission (91 Fed. Reg. 33296, Jun 3, 2026) | Never effective; exiting. |
| CFPB data-broker Reg V | Withdrawn **May 15, 2025** (90 Fed. Reg. 20568) | No rule. |

---

## Bottom line for Claude / founder

- **Real, dated, primary, shippable at $0:** DSP § 202.1104 reject-report mouth.
- **Not proven as cash:** event rate unknown; don’t treat as Monday diligence substitute.
- **If the bar is “extremely open *and* already warm demand”:** nothing else in this pass cleared. Say that plainly rather than invent a second wedge.
