# PASTE — Crime programs × Gate fit map

**Hunt date:** 27 Sep 2026  
**Question:** Which real crime / fraud / tip / reward programs does Gate actually fit?  
**Method:** Cite the program → score against Gate’s live lane (fail-closed clearance + stranger-verifiable receipts) → FIT / STRETCH / EMPTY.  
**Rule:** Tip-bounty programs pay people who *know* something. Gate *prevents* irreversible writes. Do not blur those. Prior FinCEN/IRS hunt (#146) stands.

Gate lane (what we actually ship): Clear / Never / NO_GO / HOLD before payout or bind; Issuing auth mouth; claim_scope + evidence-head; advisory mouths (Scenario 3, Nacha FP, FedNow, UAPA, DSP § 202.1104). Not a detective agency. Not a relator.

---

## Scoreboard (honest)

| Program | What it pays / does | Gate fit | Why |
|---|---|---|---|
| **FinCEN whistleblower** (31 U.S.C. § 5323; NPRM 91 FR 16328) | 10–30% of collected sanctions >$1M (BSA / IEEPA / TWEA / Kingpin) | **EMPTY** (bounty) | LLC ineligible; Never ≠ covered-statute tip. See `PASTE_FINCEN_IRS_WHISTLEBLOWER_HUNT.md`. |
| **IRS Form 211** (§ 7623) | 15–30% tax proceeds | **EMPTY** (bounty) | Same category error; no TIN / underpayment narrative in evidence-head. |
| **SEC whistleblower** (Dodd-Frank) | 10–30% if sanctions >$1M | **EMPTY** (bounty) | Securities violations + original information from a natural person. Gate receipts aren’t Form TCR/WB tips. |
| **CFTC whistleblower** | 10–30% CEA sanctions >$1M | **EMPTY** (bounty) | Commodity fraud tip program — not clearance custody. |
| **DOJ Corporate Whistleblower Awards Pilot** | Discretionary % of forfeiture (fininst / sanctions / cartel / contracting / healthcare / …) | **EMPTY** (bounty) | Same: individual original tip → forfeiture. Gate LLC / Never-pattern ≠ tip. |
| **False Claims Act qui tam** (31 U.S.C. § 3730) | Relator 15–25% (DOJ intervenes) / 25–30% (declines) | **EMPTY** as Gate product; **STRETCH** as exhibit | Requires a person who files a sealed qui tam about false claims on the U.S. Gate does not invent false claims. A customer SIU officer *with* independent FCA knowledge could attach Gate deny receipts as exhibits — Gate is not the relator. |
| **CA Ins. Code § 1871.7** (insurance fraud qui tam) | Relator ~30–40% (DA proceeds) / higher if DA declines | **EMPTY** as Gate product; **STRETCH** as exhibit | Carrier-adjacent; still a private qui tam by a natural person who knows insurance fraud. Gate spend-map Never ≠ fraud proof. |
| **NICB Speak Up / tip lines** | Tip intake; **no reliable public reward SKU** | **EMPTY** (bounty); **STRETCH** (export) | Hotline/online tips for insurance crime. Gate is not an NICB member SIU. Optional later: customer-owned receipt pack for *their* SIU tip — not a Gate reward. |
| **Rewards for Justice / ransomware CFAA** (State / up to $10M) | Tips locating foreign cyber actors | **EMPTY** | Needs human intelligence on actors — not payment clearance logs. |
| **FBI IC3 / tips.fbi.gov / FTC ReportFraud** | Complaint intake; **not** award programs | **EMPTY** (bounty); **STRETCH** (victim/bank export) | Reporting channels. Gate could help a *customer* attach sealed-payee / NO_GO receipts to *their* IC3/FTC packet — still not a Gate crime-reward product. |
| **OVC National Elder Fraud Hotline** | Victim help / referrals; grants to MDTs — **not** tip awards | **EMPTY** (bounty); **STRETCH** (prevention) | Gate FedNow sealed-payee / first-time-payee Never can *prevent* elder BEC payouts — that is product fit to the *crime problem*, not to a reward program. |
| **FinCEN Advisory FIN-2016-A003 Scenario 3** | Advisory typology (supplier impersonation) | **FIT** (already live) | Mouth `/scenario-3` classifies flags as FinCEN wrote them. Prevention/advisory — not a bounty. |
| **Nacha False Pretenses** (RM rules Phase 1/2 2026) | Risk-management obligation on ACH | **FIT** (already live) | Mouth `/nacha-false-pretenses`. Gate Never before credit — prevention. |
| **TCH UAPA / FedNow–RTP pre-push** | Rail reason codes / irrevocable push risk | **FIT** (already live) | Mouths `/uapa-seal`, `/fednow-prepush`. Crime-adjacent payment fraud prevention. |
| **DOJ Data Security Program 28 CFR § 202.1104** | **Mandatory** report on rejected prohibited data-brokerage (14-day) | **FIT** (already live) | Mouth `/dsp-reject` packs fields; Gate does **not** email NSD. Obligation tooling — opposite of bounty. |
| **Issuing agent-card auth (Stripe)** | Industry control; not a gov reward | **FIT** (already live) | Workflow lock + claim_scope before settlement — stops agent/BEC-shaped card crime at write-time. |

---

## Where Gate actually fits (crime-adjacent)

These are **not** “Gate collects a reward.” They are programs / rules where Gate’s **prevention or obligation** function is the honest product:

### 1. Payment-fraud prevention rails — **FIT, live**
- FinCEN Scenario 3 supplier impersonation  
- Nacha False Pretenses  
- FedNow / RTP sealed-payee pre-push + UAPA post-send classify  
- Issuing mouth: agent auth fail-closed  

**Crime problem:** BEC / impersonation / false-pretense payouts.  
**Gate job:** refuse the write; mint stranger-verifiable Never/NO_GO.  
**Reward:** none from government — commercial weld + clearance fees.

### 2. Mandatory reject reporting — **FIT, live**
- DSP § 202.1104 rejected prohibited transaction report pack  

**Crime / national-security problem:** prohibited data brokerage with countries of concern.  
**Gate job:** pack the statutory fields; customer/covered person files.  
**Reward:** none — compliance obligation.

### 3. Evidence as *someone else’s* tip exhibit — **STRETCH only**
If a natural person (customer compliance / SIU / employee) already has independent knowledge for FinCEN TCR, IRS 211, SEC WB, DOJ CWA, FCA, or CA 1871.7, Gate signed claim_scope / deny receipts from **that customer’s** welded path can be appendices.

| Build? | Only if separately asked |
|---|---|
| What | Customer-owned export pack (event_ids they control) labeled “exhibits for counsel — Gate is not the whistleblower / relator” |
| What not | Cross-tenant tip radar, Gate-as-relator, award share, auto-file |

This is the same adjacency noted in the FinCEN/IRS hunt — still **not** a crime-reward SKU.

---

## Programs that look shiny but do not fit

| Tempting hook | Why empty for Gate |
|---|---|
| “Multi-customer Never → FinCEN tip → 10–30%” | NEVER is job spend-map, `counterparties=None`; LLC can’t claim; refuse ≠ BSA violation (#146). |
| “Evidence-head is a tip file” | Merkle of receipt hashes — custody, not Form TCR. |
| “Rewards for Justice crypto payout” | Needs actor identity intel, not clearance logs. |
| “NICB reward millions” | Tip line real; public bounty SKU unreliable / not Gate’s. |
| “Qui tam on Vesttoo-shaped LOC fraud using Gate” | Diligence narrative ≠ Gate product; qui tam needs a relator with original fraud knowledge about false claims. |

---

## Bottom line

| Ask | Answer |
|---|---|
| Any **crime reward** program where Gate (the company) collects? | **No.** |
| Any **crime program** where Gate’s product fits? | **Yes — prevention + obligation mouths already live** (Scenario 3, Nacha FP, FedNow/UAPA, DSP 1104, Issuing). |
| Anything new to build for rewards? | **No.** |
| Only stretch worth remembering | Customer-owned receipt export for *their* counsel’s tip/qui tam — separate ask, honest labels. |

**Fit is prevention of crime-shaped payouts and packing of mandatory reject reports — not hunting bounties.**

---

## Sources (programs)

- FinCEN whistleblower NPRM: https://www.federalregister.gov/documents/2026/04/01/2026-06271/whistleblower-incentives-and-protections  
- IRS Form 211: https://www.irs.gov/help/submit-a-whistleblower-claim-for-award  
- SEC WB: https://www.sec.gov/enforcement-litigation/whistleblower-program  
- CFTC WB: https://www.whistleblower.gov/overview  
- DOJ CWA Pilot: https://www.justice.gov/criminal/criminal-division-corporate-whistleblower-awards-pilot-program  
- FCA § 3730: https://www.law.cornell.edu/uscode/text/31/3730  
- CA Ins. § 1871.7: https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=INS&sectionNum=1871.7  
- NICB report fraud: https://nicb.org/how-we-help/report-fraud  
- Rewards for Justice cyber: https://rewardsforjustice.net/rewards/foreign-malicious-cyber-activity-against-u-s-critical-infrastructure/  
- FinCEN FIN-2016-A003: https://www.fincen.gov/resources/advisories/fincen-advisory-fin-2016-a003  
- DSP 28 CFR Part 202 / § 202.1104 (mouth cites in `gate/mouths.py`)  
- Prior empty: `gate/outbound/PASTE_FINCEN_IRS_WHISTLEBLOWER_HUNT.md`
