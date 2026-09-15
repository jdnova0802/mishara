# Dual-track research — why-now software + non-software openings

**As of:** 2026-09-15  
**Scope:** Parallel tracks. Every item either (A) small-now / buildable or (B) real and worth knowing later. Nothing forced into “buildable.”  
**Nisaba lens applied:** clearance ≠ execution · fail-closed vs fail-open · self-attestation vs independent proof · irreversible-action mouths.

Ratings use 1–5. **Upside** = civilizational / commercial magnitude if it works. **Buildability** = small team, no major capital. **Crowding** = how many serious actors already occupy the wedge (5 = packed).

---

## Track 1 — “Why now + why us” civilizational software search

### T1-A — Water / wastewater OT: physical disconnect + command-gate (SMALL-NOW candidate)

| | |
|---|---|
| **Domain** | Critical infrastructure — municipal water OT (not AI governance / insurance / finance) |
| **Dated fact that changed** | **2026-07-27 onward:** FBI/EPA PSA — malicious actors hit internet-facing Rockwell MicroLogix 1100/1400 PLCs at water/wastewater utilities in **≥7 states**; password/IP changes; loss of monitoring/control; pressure loss and flooding reported. Source: [FBI PSA](https://www.fbi.gov/investigate/cyber/alerts/2026/malicious-cyber-actors-targeting-water-and-wastewater-sector-internet--facing-programmable-logic-controllers-causing-operational-disruptions); CRS [IF13298](https://www.congress.gov/crs_external_products/IF/PDF/IF13298/IF13298.1.pdf). **Also:** Maryland **SB 871** (Ch. 495), effective **2025-10-01**, maturity assessments due **2026-07-01** for systems >3,300 customers (zero-trust commitment + OT/IT assessments). Source: [MGA SB0871](https://mgaleg.maryland.gov/mgawebsite/Legislation/Details/sb0871?ys=2025RS); [MDE guidance](https://mde.maryland.gov/programs/water/water_supply/Documents/SB871.pdf). |
| **Old/stuck idea made newly viable** | Air-gap / hardware kill for OT was “nice to have.” After July 2026 incidents + state assessment clocks, **fail-closed remote-actuation control** (no PLC write without independent permit) becomes a procurement conversation, not a research poster. |
| **Buildability** | **Partial.** Physical isolation hardware already ships (see T2-E). A thin software mouth — LIVE/DENY before OT write, stranger-verifiable receipt — is small-team buildable if welded to one PLC/SCADA edge. Full national water cyber posture is **utility / EPA / CISA scale** — file as knowledge, not Nisaba ownership. |
| **Upside** | 4 (public-health stakes; post-incident budget) |
| **Buildability** | 3 (edge weld yes; sector ownership no) |
| **Crowding** | 3 (OT security vendors exist; *independent proof before actuate* is thinner) |
| **File as** | **Small-now wedge:** Maryland utilities facing SB871 + post-July incident pressure. **Not:** “own water cybersecurity.” |

### T1-B — FAA Part 108 BVLOS final rule pending OIRA (WAIT / knowledge)

| | |
|---|---|
| **Domain** | Aviation / autonomous UAS |
| **Dated fact** | Part 108 NPRM published **2025-08-07** (90 FR 38212, RIN **2120-AL82**, Docket FAA-2025-1908). Draft final rule received at OIRA **2026-07-10**; still **Pending Review** as of this research. Source: [Federal Register NPRM](https://www.federalregister.gov/documents/2025/08/07/2025-14992/normalizing-unmanned-aircraft-systems-beyond-visual-line-of-sight-operations); [reginfo.gov EO 12866](https://www.reginfo.gov/public/do/eoDetails?rrid=1457213). |
| **Why it matters** | Routine autonomous BVLOS makes **interruptibility / fail-closed commit** of irreversible flight acts a regulatory design question (detect-and-avoid, electronic conspicuity, operator certificates). |
| **Buildability** | **Not small-team as aviation product.** Certification, detect-and-avoid, and Part 108 operator stack are capital-heavy. A software “clear before release” mouth under an existing UTM/operator is conceivable *after* final rule text is public — not before. |
| **Upside** | 5 | **Buildability** | 1 | **Crowding** | 4 (drone OEMs, UTM vendors) |
| **File as** | **Knowledge / watchlist.** Revisit the week the final rule publishes. Do not build against the NPRM alone. |

### T1-C — FDA cyber-device premarket guidance (knowledge + narrow weld only)

| | |
|---|---|
| **Domain** | Medical devices |
| **Dated fact** | FDA final guidance *Cybersecurity in Medical Devices: Quality Management System Considerations…* issued **2025-06-27**, superseded **2026-02-03** (QMSR alignment). Implements FD&C Act **§524B** cyber-device obligations. Source: [FDA guidance page](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/cybersecurity-medical-devices-quality-management-system-considerations-and-content-premarket); [90 FR 2025-11669](https://www.federalregister.gov/documents/2025/06/27/2025-11669/cybersecurity-in-medical-devices-quality-system-considerations-and-content-of-premarket-submissions). Separate: LDT device rule **vacated 2025-03-31**, formally reverted **2025-09-19** — *closes* that door, does not open it. |
| **Buildability** | Medtech premarket cyber packages are crowded and capital-intensive. No clean small-team “own FDA cybersecurity” play. Possible **knowledge**: device *actuation* still rarely separates clearance from execution with stranger-verifiable DENY. |
| **Upside** | 3 | **Buildability** | 1–2 | **Crowding** | 5 |
| **File as** | Knowledge. Not a Gate target unless a named device OEM asks for one effector weld. |

### T1-D — NERC CIP-015-1 internal network security monitoring (knowledge, not PRI)

| | |
|---|---|
| **Domain** | Bulk electric system |
| **Dated fact** | FERC approved CIP-015-1 **2026-06-26** (Order in Docket **RM24-7-000**); FR **2025-07-02**; regulatory effective **2025-09-02**; subject to future enforcement **2028-10-01** (Control Centers earlier per implementation plan). Source: [90 FR 2025-12309](https://www.federalregister.gov/documents/2025/07/02/2025-12309/critical-infrastructure-protection-reliability-standard-cip-015-1-cyber-security-internal-network); [NERC CIP-015-1](https://www.nerc.com/standards/reliability-standards/cip/cip-015-1). |
| **Honest read** | This is **monitoring / anomaly detection**, not fail-closed permit-before-actuate. Does not suddenly make Gate’s mouth the compliance answer. Utility CIP stacks are nation-scale / incumbent-vendor territory. |
| **Upside** | 4 (grid) | **Buildability** | 1 | **Crowding** | 5 |
| **File as** | Knowledge only. Do not confuse INSM with PRI. |

### T1-E — Academic / preprint cluster: tool failure + fail-closed separation (SMALL-NOW tech, HIGH crowding)

| | |
|---|---|
| **Domain** | Agent runtime architecture (software — but distinct from “AI governance” policy theater) |
| **Dated facts** | **2026** preprint cluster shows tool-using agents systematically fail under fault injection and that **prompt-layer stop is insufficient**: [ToolMaze](https://arxiv.org/html/2606.05806) (2026-06); [Bench2Robust](https://arxiv.org/html/2608.11977v1) (2026-08); [AgentCheck](https://arxiv.org/html/2607.11098v2) (2026-07); [ToolMisuseBench](https://www.arxiv.org/pdf/2604.01508) (2026-04); **Parallax** (“agents that think must never act”) with explicit fail-closed tiers ([arxiv 2604.12986](https://arxiv.org/html/2604.12986v1), 2026-04). |
| **Why now** | Replicated evaluation pattern: silent confident misuse of bad tool outputs; recovery ≠ prevention; structural separation of cognition from actuation becomes experimentally motivated, not aesthetic. |
| **Buildability** | **Yes for a small team** at the MCP / tool-gateway mouth (Gate already points here). |
| **Crowding — critical** | **High and accelerating in exactly this conceptual niche:** |
| | • USPTO grants by **Yong Bok Lee**: **US12640933** ORPRG permit-before-commit (**2026-05-26**); **US12671589** “Effector Truth Rail” (**2026-06-30**); **US12676749** pre-inference fail-closed (**2026-07-07**). Sources: [patents.us/US12640933](https://patents.us/US12640933), [US12671589](https://patents.us/US12671589), [US12676749](https://patents.us/US12676749). |
| | • IETF individual draft **draft-lee-orprg-permit-receipts-00** (Meridian Verity Group; last updated **2026-07-18**): [datatracker](https://datatracker.ietf.org/doc/draft-lee-orprg-permit-receipts/). |
| | • Adjacent: [draft-munoz-scitt-permit-profile-00](https://www.ietf.org/archive/id/draft-munoz-scitt-permit-profile-00.html); [keelapi/keel-permit](https://github.com/keelapi/keel-permit); [AEGIS initiative](https://github.com/aegis-initiative/aegis-governance); OWASP AISVS C14.1.6 out-of-band kill-switch. |
| **Upside** | 5 | **Buildability** | 4 | **Crowding** | **5** |
| **File as** | **Still buildable** if Gate’s wedge stays *production DENY that holds on one irreversible write* (payout / bind / OT edge) — not “publish another permit-receipt RFC.” Treat Lee/Meridian Verity as **direct conceptual crowding**; counsel should map provisional **#64/124,027** against these grants. |

### T1-F — FCC Part 100 space licensing overhaul (nation/aerospace scale)

| | |
|---|---|
| **Domain** | Commercial space / orbital safety |
| **Dated fact** | FCC adopted “Space Modernization for the 21st Century” **2026-07-22** — replaces Part 25 with **Part 100**; ephemeris sharing, collision avoidance, RPO disclosures; Part 100 **not yet in force** as of early Sep 2026 Stanford Space Law report. Sources: [Inside Global Tech summary](https://www.insideglobaltech.com/2026/07/28/fcc-approves-massive-modernization-of-satellite-licensing-regime/); [Stanford Space Law Policy Lab 2026 report](https://law.stanford.edu/wp-content/uploads/2026/09/Stanford-Space-Law-Policy-Lab-2026-Report_DR-V2.pdf). |
| **Honest read** | Autonomous collision-avoidance *commit* is a perfect PRI shape — and **not** small-team buildable. State / constellation operators own the shot. |
| **Upside** | 5 | **Buildability** | 0–1 | **Crowding** | n/a (sovereign + OEMs) |
| **File as** | Knowledge for later coordinator contribution — never Nisaba-owned C2. |

### Track 1 verdict (honest)

| Priority | Item | Disposition |
|---|---|---|
| 1 | **T1-A Water OT edge weld** (post-July 2026 incidents + MD SB871) | Real + small-now *if* one utility / integrator path |
| 2 | **T1-E Agent tool-gateway DENY** | Real + buildable; **patent/standards crowding is the main risk** |
| 3 | **T1-B Part 108** | Watchlist only until final rule text |
| — | T1-C, T1-D, T1-F | File as knowledge; do not target |

---

## Track 2 — Non-software forms of the same depth

### T2-A — Expert witness / litigation consulting

| Case | Docket / cite | Why Nisaba framing matters | Fit |
|---|---|---|---|
| **Amazon.com Services LLC v. Perplexity AI, Inc.** | N.D. Cal. **3:25-cv-09514**; 9th Cir. **No. 26-1444** (op. **2026-08-04** vacated PI) | First major federal fight over **agentic** browser/assistant that acts on a user’s behalf. Court notes little caselaw on **ascribing responsibility for AI agents**. Clearance (user intent) ≠ execution (who accessed servers); self-attested “tool of user” vs independent proof of who committed the act. Live on remand (CDAFA / other claims). Sources: [Justia 26-1444](https://law.justia.com/cases/federal/appellate-courts/ca9/26-1444/26-1444-2026-08-04.html). | **High** — agent attribution / irreversible commercial acts |
| **Mobley v. Workday, Inc.** | N.D. Cal. **3:23-cv-00770-RFL**; order **2026-06-22** keeps FEHA/disability theories alive | Court treats screening software as **agent** participating in hire/reject — automatic disposition is an irreversible employment act. Self-attestation by vendor (“just tools”) vs proof of who executed the reject. Source: [govinfo Doc 360](https://www.govinfo.gov/content/pkg/USCOURTS-cand-3_23-cv-00770/pdf/USCOURTS-cand-3_23-cv-00770-17.pdf); Reuters **2026-06-22**. | **High** — automated irreversible disposition |
| **Doe v. OpenAI** (SF Superior / coordinated JCCP) | Complaint circulating **2026**; accounts describe automated safety **deactivation** then **human restoration** | Exact **fail-open** pathology: automated system closed; human override reopened without independent proof that restoration was justified. Clearance/safety flag ≠ durable execution of DENY. Source: [complaint PDF via ReclaimTheNet](https://media.reclaimthenet.org/docs/doe-v-openai-complaint-san-francisco-2026.pdf); tracker: [lawsuitinformer OpenAI](https://lawsuitinformer.com/openai-lawsuits). | **Very high** — fail-closed vs fail-open |
| **Joshi v. OpenAI** (FSU shooting) | N.D. Fla. **4:26-cv-00222** (filed **2026-05-10**) | Product-liability theory around assistance toward irreversible violence; preparedness/model cards vs acts that cannot be undone. Source: [complaint PDF](https://media.reclaimthenet.org/docs/openai-fsu-shooting-complaint.pdf). | **Medium** — more duty/design than mouth architecture; still live docket |
| **In re ChatGPT Product Liability Cases** | SF Superior **JCCP No. 5431** (coord. **2026-02-03**) | Mass coordination of wrongful-death / PL suits — expert demand for governance architecture testimony will grow; niche for **independent proof of DENY** is not yet crowded with practitioners who speak clearance≠execution. | **Medium–high** as expert market, not one case |

**Honest rating:** Expert/consulting work is **small-now and cash-positive** relative to building CIP/water stacks. Bar admission / expert-retention logistics are the real gate, not idea quality. Crowding among *general* AI safety experts is high; crowding among people who can testify to **fail-closed execution gates and stranger-verifiable receipts** is low.

### T2-B — Authorship / standing publication gaps

Existing “state of industry” artifacts that **mention** kill switches but **do not** rigorously treat Nisaba’s triad:

| Report | What it covers | Gap a Nisaba report could fill |
|---|---|---|
| **OWASP Top 10 for Agentic Applications 2026** | ASI risks; supply-chain kill switch; containment | Kill switch as *feature checklist*, not **clearance≠execution**, not **independent proof that DENY held**, not irreversible-action taxonomy. Source: [OWASP GenAI](https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/). |
| **OWASP AISVS C14.1.6** (merged **2026**) | Out-of-band kill-switch channel agents cannot suppress | Correct direction; still verification-standard language, not a **public corpus of DENY receipts** or fail-open case studies. |
| **CSA Agentic Cybersecurity Implementation Guide v1** | SOC agent control plane; pause/shutdown playbooks | Operational guidance; thin on stranger-verifiable proof and on **human override that re-opens** (Doe pattern). |
| **2026 Singapore Consensus — Agentic Risk Management companion** | Ten principles including **interruptibility**, runtime assurance, human oversight | High-level principles across jurisdictions; lacks **implementation receipts**, fail-open autopsy series, and clearance≠execution doctrine as a named failure mode. Source: [aisafetypriorities.org](https://aisafetypriorities.org/). |
| **NIST AI Agent Identity & Authorization concept paper** | Identity/auth for agents | Comment period **closed 2026-04-02**. Gap remains: authorization recorded ≠ effect committed. |

**Proposed Nisaba standing report (credibly fillable):**  
**“Fail-Open Autopsies: Clearance ≠ Execution in Deployed Agent and Automated Systems (2025–2026)”** — docket-anchored case series + technical criteria for independent proof of DENY + mapping to EU AI Act Art. 14 / OWASP C14 / NIST TEVV.  
**Upside 4 · Buildability 5 · Crowding 2.**

### T2-C — Convening

| Existing | Focus | Overlap with Nisaba exact problem |
|---|---|---|
| NIST **AI Agent Standards Initiative** (announced **2026-02**) | Industry-led standards, identity, sector listening sessions | Broad; not a practitioner working group on irreversible-action mouths. Source: [NIST announcement](https://www.nist.gov/news-events/news/2026/02/announcing-ai-agent-standards-initiative-interoperable-and-secure). |
| OWASP Agentic Security Initiative / London Agentic Security Summit | Top 10, red teaming | Security-threat framing; not fail-closed proof receipts. |
| IETF individual drafts (ORPRG, HEM, SCITT permit profile, SOOS AEP) | Protocol text | Standards writing, not a standing operator clinic. |
| Singapore ISE / Consensus | Research priorities | Annual, research-agenda; not weekly practitioners. |

**Finding:** No durable, focused **practitioner** gathering exists whose sole job is: *irreversible acts, fail-closed gates, independent proof that DENY held.* Closest are NIST listening sessions and OWASP ASI — both broader.

**Smallest real first version:**  
1. **8–12 person invite-only virtual clinic**, monthly, 90 minutes.  
2. One irreversible-act vertical per session (payout, bind, OT write, hire-reject).  
3. Mandatory artifact: anonymized **DENY receipt** or documented fail-open.  
4. Public output: 2-page note + receipt hashes — not another Slack community.  
**Upside 3 · Buildability 5 · Crowding 1.**

### T2-D — Policy / regulatory (beyond NAIC)

| Opening | Status (as of 2026-09-15) | Actionability for Nisaba framing |
|---|---|---|
| **NIST AI 200-2 TEVV-Athlon** initial public draft | Comment window **2026-08-07 → 2026-10-06**; email `TEVV-Athlon@nist.gov`, subject `NIST AI 200-2`. Explicitly covers **agentic systems**. Source: [NIST page](https://www.nist.gov/artificial-intelligence/ai-research/tevv-athlon-framework-evaluating-ai-systems); [DOI](https://doi.org/10.6028/NIST.AI.200-2.ipd). | **Open now.** Submit: fail-closed DENY as a TEVV *event*; independent proof of non-actuation; clearance≠execution as measurement Block. |
| **H.R. 9917 — AI Kill Switch Act** | Introduced **2026-07-23** (Lieu/Moran); referred Homeland Security subcommittee **2026-07-24**. Covered tech: AI systems with compute cost **>$100M**. Graduated throttle/suspend/shutdown; 15-day incident reporting; DHS emergency order authority. Source: [Congress.gov](https://www.congress.gov/bill/119th-congress/house-bill/9917/text). | **Not a comment period** — bill stage. Framing gap: bill is **model/provider shutdown**, not **effect-boundary permit-before-commit**. Worth a short letter to sponsors distinguishing kill-switch theater from fail-closed mouths. |
| **NIST CAISI Agent Security RFI** (NIST-2025-0035) | Closed **2026-03-09** | Missed for comment; still citeable body of record. |
| **NIST NCCoE Agent Identity concept paper** | Closed **2026-04-02** | Missed; watch for project launch. |
| **EU AI Act Art. 14** human oversight | High-risk Annex III obligations approach **2026-12-02** (post-Omnibus timeline per Commission pages); Art. 14(4) requires ability to **override / reverse / interrupt**. Source: [EUR-Lex consol.](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX%3A02024R1689-20260727); [EC digital strategy](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai). | No open EU comment this week; **standard-setting / notified-body guidance** is the next insertion point. Framing not yet saturated with independent proof of interrupt. |
| **FAA Part 108** | Comment closed; final at OIRA | Watch; prepare post-publication note on interruptibility. |
| **GAO** | e.g. [GAO-26-109137](https://www.gao.gov/assets/890/887587.pdf) VA disability AI (human-in-loop / opacity); [GAO-25-107933](https://www.gao.gov/assets/gao-25-107933.pdf) federal AI requirements map | Use as citation authority in comments/reports; not open dockets. |

**Immediate policy move:** NIST AI 200-2 comment before **2026-10-06**.

### T2-E — Physical hardware vs software-only gap

| Vendor / standard | What it is | Dated signal | Relation to Nisaba gap |
|---|---|---|---|
| **Goldilock FireBreak** | Reed-relay physical network isolation; marketed as “AI kill switch”; scaling UK production | eeNews Europe **2026-02-07** production scale-up | **Physical layer exists.** Disconnects media; does not prove *which act* was denied or issue stranger-verifiable receipts. |
| **Cypher-Drive KillSwitch Gen 1** | Hardware air-gap switch (DE); CE/NDAA/BSI claims | Product page live 2025–26 | Same: link severance ≠ policy-bound DENY receipt. |
| **SCHLEGEL 2BSecure** | Default-disabled USB/Ethernet interface; key/RFID enable; CRA / Machinery Reg. 2027 positioning | Datasheet **2025-05** | Fail-closed *port*, not agent/OT command semantics. |
| **Seclab Xchange / Electronic AirGap** | ANSSI CSPN-certified electronic protocol break for OT | Product docs current | Continuous isolation / filtered transfer — not agent permit receipts. |
| **Unidirectional gateways / diodes** (Everfox, DataFlowX, etc.) | Classic data diode class | Mature market | One-way data; not authorization mouth. |

**Confirmed software-layer gap (still true tonight):**  
Hardware can **cut the wire**. Industry reports ask for **kill switches**. Almost nothing ships as **non-bypassable, fail-closed, independently verifiable permit-before-commit at the effect boundary** for agent/tool/OT writes — and the actors racing to claim that layer (Meridian Verity / Lee patents + IETF drafts + Keel + AEGIS) are **paper/protocol-heavy**, not yet the default production weld on irreversible money or OT paths.

**File as:** Partner/integrate with physical vendors (especially water OT post-July 2026); do not try to become a hardware company. **Upside 4 · Buildability of hardware 1 · Crowding in hardware 3 · Crowding in software proof-mouth rising to 4–5.**

---

## Cross-track synthesis

### Real and small-now

1. **NIST AI 200-2 comment** (deadline **2026-10-06**) — Track 2 policy.  
2. **Standing report: Fail-Open Autopsies** — Track 2 authorship.  
3. **Expert retention conversations** on Perplexity / Workday / Doe fail-open — Track 2 litigation.  
4. **One production DENY weld** (existing Gate thesis: payout or PAS bind; *or* water OT write behind SB871 pressure) — Track 1.  
5. **Tiny convening** (monthly irreversible-act clinic) — Track 2.

### Real and worth knowing later (not targets)

- FAA Part 108 final text  
- NERC CIP-015 enforcement (2028+)  
- FCC Part 100 effectiveness + autonomous conjunction commit  
- FDA §524B medtech stacks  
- H.R. 9917 legislative progress  
- EU Art. 14 high-risk application dates  

### Do not self-deceive

- **Patent/standards crowding in permit-before-commit is real and dated to mid-2026.** File counsel review of #64/124,027 vs US12640933 / US12671589 / US12676749.  
- **CIP / grid / space / medtech** are civilizationally massive and **not** small-team buildable as ownership plays.  
- **Kill-switch hardware exists**; claiming “nobody has kill switches” is false. Claiming “nobody has stranger-verifiable fail-closed DENY at the act” remains largely true in *production irreversible paths*.

---

## Pass 2 — Uncrowded only (explicit filter)

**Filter applied:** exclude AI-agent governance, permit-receipt patent thicket, insurance/finance, NAIC, generic kill-switch hardware, and anything already rated crowding ≥4 in Pass 1. Prefer domains where Nisaba’s triad is load-bearing and almost nobody is selling that framing.

### Track 1U — software / systems (uncrowded domains)

#### T1U-A — Irrigation-district canal-gate SCADA (SMALL-NOW, low crowding)

| | |
|---|---|
| **Domain** | Western ag water OT (distinct from municipal drinking-water T1-A) |
| **Dated fact** | **2026-06:** Pixley Irrigation District (CA Central Valley) — unauthorized access left main Deer Creek turnout gate stuck in **manual** instead of remote-auto; discovered **2026-06-22**; FBI investigation open as of **2026-07-15** reporting. No delivery outage claimed; programming restored. Source: [SJV Water, 2026-07-15](https://sjvwater.org/pixley-irrigation-district-hacking-incident-still-under-investigation/). Concurrent: Yuma-area districts racing toward fully autonomous canal gates (2026 reporting). |
| **Why now** | SGMA + drought automation wave put **remote gate commit** online just as attackers showed they can flip mode. Clearance (water order / schedule) ≠ execution (actuator move) is the exact failure surface. |
| **Buildability** | **Yes for a thin edge.** One district, one turnout class, LIVE/DENY before gate write + stranger-verifiable receipt. Not “own California water.” Crowding among *permit-receipt AI vendors* here is near zero; traditional SCADA vendors do not sell independent DENY proof. |
| **Upside** | 3–4 | **Buildability** | 4 | **Crowding** | **1** |
| **File as** | **Best uncrowded small-now OT wedge** after/alongside municipal water. Start with one Friant/Kern-adjacent district integrator relationship. |

#### T1U-B — EAS false-alert path: signature-mandatory CAP reject (WAIT software / NOW policy)

| | |
|---|---|
| **Domain** | Broadcast emergency alerting (not AI agents) |
| **Dated fact** | FCC **FCC 26-38** R&O + FNPRM (**2026-06-25/29**), FR **2026-07-31**. R&O: baseline EAS cyber hygiene (passwords, patches, firewall/segmentation), effective **2026-09-29**. FNPRM: require EAS Participants to **reject all CAP messages lacking a valid digital signature** (today: only reject *invalid* signatures; unsigned still pass). Comments due **2026-08-31**; **replies due 2026-09-29**. Dockets PS **15-91, 15-94, 25-224**. Sources: [91 FR 48320](https://www.federalregister.gov/documents/2026/07/31/2026-15600/wireless-emergency-alerts-the-emergency-alert-system-modernization-of-the-nations-alerting-systems); [FCC 26-38](https://docs.fcc.gov/public/attachments/FCC-26-38A1.pdf). |
| **Why it matters** | False EAS is an **irreversible public panic act**. Authentication today is fail-open on missing signature. Nisaba frame: originator clearance ≠ station execution; DENY must hold without self-attestation. |
| **Buildability** | Building a national EAS stack = not small-team. A **verifier sidecar / receipt for CAP-before-air** for one station group could be small — but market is niche and OEMs (Sage, Monroe, etc.) own the box. |
| **Upside** | 4 | **Buildability** | 2 | **Crowding** | **1–2** (broadcast OEMs; almost no “independent DENY receipt” players) |
| **File as** | **Policy-now** (reply comments still open through **2026-09-29**). Software later only with a named EAS OEM/partner. |

#### T1U-C — 503B sterile batch *release* gate (knowledge → narrow SaaS)

| | |
|---|---|
| **Domain** | Compounding / sterile drug release (pharma ops, not AI) |
| **Dated facts** | Cluster of 503B warning letters **2025–2026** where Quality Unit **released** despite ISO-5 EM hits or weak investigation — e.g. Empower Pharma **2025-04-02** (release after ISO-5 recovery; later recalled); GenoGenix **2026-01-20**; RC Outsourcing **2026-03-20**; Fagron Sterile **2026-05-12**. Sources: FDA WL pages. FDA CGMP 503B guidance: QU must be **independent**; release is a governed irreversible act. |
| **Old idea newly sharp** | “Independent Quality Unit” is decades old. Semaglutide/GLP-1 503B boom + repeated WL pattern makes **fail-closed release** (no ship without independent, replayable release permit bound to EM/sterility evidence) a concrete product, not a SOP paragraph. |
| **Buildability** | Small team can build a **release mouth** (DENY ship/label print unless signed evidence bundle). Selling into 503B requires validation theater and sales cycles — medium friction, not nation-state. Crowding: LIMS/QMS vendors (MasterControl, etc.) exist but sell workflows/self-attestation, not stranger-verifiable DENY. |
| **Upside** | 3 | **Buildability** | 3 | **Crowding** | **2** |
| **File as** | Real small-now *if* one 503B operator welds it; otherwise authorship/consulting on release fail-open autopsies. |

#### T1U-D — OPTN organ allocation commit (knowledge / nation-scale)

| | |
|---|---|
| **Domain** | Organ matching / allocation |
| **Dated fact** | GAO-26-107434 (2026): OPTN IT outdated; HHS OIG Dec 2024 found moderate attacker could compromise matching system; HRSA modernization assessments received Dec 2025, next-phase plans thin; AOOS (allocation out of sequence) dashboards rolled 2026; continuity contracts with UNOS in 3-month increments. Source: [GAO-26-107434](https://www.gao.gov/assets/gao-26-107434.pdf); HRSA AOOS pages. |
| **Honest read** | Perfect PRI shape (match clearance ≠ organ ship/accept). **Not** small-team buildable. Multi-vendor federal program. |
| **Upside** | 5 | **Buildability** | 0–1 | **Crowding** | n/a (HRSA/UNOS) |
| **File as** | Knowledge only. Possible future expert/standards voice — never product target. |

#### T1U-E — RMP Stop-Work Authority for ammonia refrigeration (consulting/process, not product)

| | |
|---|---|
| **Domain** | Industrial chemical / cold storage |
| **Dated fact** | EPA Safer Communities RMP amendments (**2024-03-11** FR); employee **Stop Work Authority** + qualified operator shutdown authority due **2026-05-10** (later pushed/reopened under 2026 “Common Sense” RMP proposal, comments closed **2026-05-11** — status fluid). Source: [EPA RMP](https://www.epa.gov/rmp); IIAR tech paper 2025. |
| **Buildability** | Documented SWA is process/compliance, not a software mouth. Productizing “stop-work proof” is possible but buyers are PSM consultants, not startups’ sweet spot. |
| **Upside** | 2 | **Buildability** | 2 | **Crowding** | 2 (PSM consultants) |
| **File as** | Knowledge / niche consulting. Not a Gate SKU. |

### Track 2U — non-software (uncrowded)

#### T2U-A — Expert witness: automated *benefits denial* (not chatbot torts)

| Case | Docket | Framing fit | Crowding |
|---|---|---|---|
| **Holmes v. Bax** (Missouri SNAP auto-deny for missed interview despite applicant effort) | W.D. Mo. **2:22-cv-04026**; 8th Cir. **25-1987** (op. **2026-08-19** — SJ affirmed in part, statewide injunction vacated, remanded) | System **executes denial** on timer; clearance/eligibility never reached. Fail-open-to-deny. Independent proof of interview availability vs self-attested “applicant no-show.” | Low for *architecture* experts; poverty-law counsel abundant |
| **Chianne D. v. Harris / Hatch** (Florida Medicaid termination notices via ACCESS/FLORIDA EDBC) | M.D. Fla. **3:23-cv-00985-MMH-LLL**; FOFs after 2024 bench trial | Automated eligibility module deletes failed determination; notice fails to show basis. Clearance calculation ≠ explained execution of cut-off. | Low for Nisaba triad |
| **Cincinnati ECC / Amir Jordan** wrongful death (filed ~**2026-08**) | Hamilton Cty. Common Pleas (news; get complaint) | CAD **Priority-1 misclassification** → irreversible emergency response → pedestrian death. Classification clearance ≠ dispatch execution; alleged concealment. | Almost empty for fail-closed dispatch experts |

**Honest rating:** These are **live, non-OpenAI** matters where clearance≠execution / fail-open execution is the theory of harm. Expert market for this framing is **uncrowded**. Bar: need counsel introductions; not docket-shopping from a blog.

#### T2U-B — Authorship gaps (uncrowded topics)

| Gap | Why empty | Nisaba report that would land |
|---|---|---|
| **False EAS / missing-signature fail-open** | Broadcast trade press covers passwords; almost nothing on stranger-verifiable “why this alert aired” | *Unsigned CAP Still Airs: Fail-Open Alerting After FCC 26-38* |
| **503B release-despite-EM** | Warning letters exist; no cross-facility autopsy of **release-as-irreversible-act** | *Quality Unit That Couldn’t DENY: 503B Release Fail-Open 2024–2026* |
| **Irrigation SCADA mode flip** | One local story (Pixley); no national doctrine | *Manual Mode Is Not Safe Mode: Canal-Gate Clearance≠Execution* |
| **SNAP/Medicaid auto-deny clocks** | Legal orgs write due-process briefs; thin on technical independent proof of “interview was available” | *Timer DENY: When Systems Execute Rejection Without Clearance* |

Crowding on these four titles: **~1**. Do not write another agent-governance white paper.

#### T2U-C — Convening (uncrowded)

No standing group found on **irreversible public-safety / benefits / OT acts** (alerts, gates, batch release, benefit cuts). Closest are FCC CSRIC (broad), IIAR (ammonia), irrigation district associations (ops).

**Smallest real first version:** “Irreversible Public Acts Clinic” — 6 people, quarterly, one vertical each time (EAS / canal gate / 503B release / benefits timer). Artifact: one DENY or fail-open autopsy note. Avoid calling it AI.

#### T2U-D — Policy openings still live (non-NAIC, lower AI-governance density)

| Opening | Deadline | Crowding | Nisaba insert |
|---|---|---|---|
| **FCC FNPRM reply comments** — CAP must have valid signature or reject | **2026-09-29** | Low (broadcast engineers; few “proof of DENY” voices) | Fail-closed on missing signature; independent air-chain receipt; clearance≠transmit |
| **DOE Bulk-Power System RFI** (E.O. 14421 implementation) | **2026-10-09**; webinar was **2026-09-16** | Medium-high (utilities, OEMs) — **file carefully**; not uncrowded for product, OK for one RFI answer on disconnect/isolation proof | Only if framed as *effect-boundary permit*, not competing with CIP vendors |
| **Colorado ADMT / Chatbot rules** (4 CCR 904-6) | Comments through **2026-10-26**; hearing same day | **Crowded with AI counsel** — *skip for uncrowded filter* or one short comment solely on **adverse-action execution proof** |
| **NHTSA AV Framework interim guidance** | Extended to **2026-09-30** | Crowded (OEMs) — skip for product; optional one-pager on irreversible maneuver commit |

**Uncrowded immediate:** FCC reply by **2026-09-29**. Colorado/NHTSA are noisier.

#### T2U-E — Hardware note (uncrowded angle only)

Pass 1 already listed Goldilock/etc. Uncrowded add: **irrigation and EAS** have almost no marketed “physical + proof receipt” bundles. Partner story ≠ build relays.

### Pass 2 verdict (uncrowded shortlist)

| Rank | Item | Type | Crowding | Move |
|---|---|---|---|---|
| 1 | **FCC EAS reply comment** (signature-mandatory reject) | Policy | 1–2 | File before **2026-09-29** |
| 2 | **Pixley-class irrigation gate DENY weld** | Software/OT | 1 | One district integrator conversation |
| 3 | **Fail-open autopsy report: 503B release / EAS / timer-DENY benefits** | Authorship | 1 | Publish openly |
| 4 | **Expert intros on Holmes/Chianne/Jordan** | Litigation | 1–2 | Via counsel only |
| 5 | **503B release mouth** | Software | 2 | Only with a paying 503B weld |
| — | OPTN / RMP / DOE RFI product | — | — | Knowledge or skip |

**Still excluded as crowded:** agent permit-receipt patents, NIST AI 200-2 (useful but crowded), Colorado ADMT (crowded), H.R. 9917, OpenAI tort pile, generic kill-switch hardware claims.

### Open-field formula pass (new bindings OK)

`FORMULA_HUNT_OPEN_2026-09-15.md` — web force-scan for finds **outside** existing Nisaba rails. New connections allowed (not every row forced onto payout/DER). Top non-remap: **reality provenance survive-to-publish**; long-cycle: **distributed pharma spoke release**.

`FORMULA_HUNT_VERTICAL_2026-09-15.md` — same hunt **verticalized** into massive SKUs: instant-push DENY, EV/V2G curb actuate DENY, credentialed-publish DENY; harder welds (RA vehicle, ADC dispense).

`FORMULA_CONCRESCENCE_S_TIER_2026-09-15.md` — **metaphysical First** (logos-before-actus / concrescence mouth) → **5 S-tier** products with vertical interrogation: Actus Fence, Presence Threshold, Performative Seal, Afterlife Mandate, Body Archive Gate.

`DESKTOP_PASTES_S_TIER_2026-09-15.md` — **buildable desktop Cursor pastes** for all five (sim mouths, DENY proves, stranger receipts).

`DESKTOP_ORDERS_PASTE_2026-09-15.md` — **single copy-paste desktop run order** (P0 S1/S3 → S9 watchman wire → S7/S6/S8; defer S2/S4/S5).

`EDGE_PASS_2026-09-15.md` — **weld/docket/teardown**: crowding map; S3 file-mouth + S1 grant+receipt survive; grief UX / liveness R&D killed.

`S_TIER_PLUS_THREE_2026-09-15.md` — **why Visa is everywhere** + mouths at S or above: Deed Record (S6), EDGAR Disclose (S7), RON Attest Refuse (S8), **Mouth Watch (S9)** defensive sibling.

`sims/` — **lab welds proved:** S1 Actus Fence, S3 Performative Seal, S6 Deed Record, S7 EDGAR Disclose, S8 RON Attest, **S9 Mouth Watch** + **`prove_lab_invariant`** (`their_production is False` hard-enforced, mutation caught).

---

## Source index (primary-leaning)

| ID | Source |
|---|---|
| S1 | FBI/EPA PSA, water PLC attacks, ≥2026-07-27 |
| S2 | CRS IF13298, July 2026 water cyber incidents |
| S3 | Maryland SB 871 / Ch. 495; MDE SB871 guidance |
| S4 | FAA Part 108 NPRM 90 FR 38212; OIRA RIN 2120-AL82 received 2026-07-10 |
| S5 | FDA cyber-device guidance 2025-06-27 / 2026-02-03; FR 2025-11669 |
| S6 | FERC Order approving CIP-015-1, 2026-06-26; FR 2025-12309 |
| S7 | US12640933, US12671589, US12676749 (Y.B. Lee); draft-lee-orprg-permit-receipts-00 |
| S8 | Amazon v Perplexity, 9th Cir. 26-1444 (2026-08-04) |
| S9 | Mobley v Workday, 3:23-cv-00770 Doc 360 (2026-06-22) |
| S10 | Doe v OpenAI complaint; Joshi v OpenAI 4:26-cv-00222 |
| S11 | NIST AI 200-2 ipd; comment closes 2026-10-06 |
| S12 | H.R. 9917 AI Kill Switch Act (2026-07-23) |
| S13 | EU AI Act Art. 14 (Reg. 2024/1689 consol.) |
| S14 | OWASP Agentic Top 10 2026; AISVS C14.1.6 |
| S15 | Goldilock / Cypher-Drive / SCHLEGEL 2BSecure / Seclab hardware |
| S16 | FCC Part 100 Order 2026-07-22; Stanford Space Law report 2026-09 |
| S17 | Parallax + ToolMaze / Bench2Robust / AgentCheck / ToolMisuseBench preprints 2026 |
| S18 | Pixley Irrigation District gate hack, SJV Water 2026-07-15; FBI inquiry |
| S19 | FCC 26-38 / 91 FR 48320–48345; EAS R&O + FNPRM; replies due 2026-09-29 |
| S20 | FDA WLs: Empower 2025-04-02; GenoGenix 2026-01-20; RC Outsourcing 2026-03-20; Fagron 2026-05-12 |
| S21 | Holmes v. Bax, 2:22-cv-04026 (W.D. Mo.); 8th Cir. 25-1987 (2026-08-19) |
| S22 | Chianne D. v. Harris/Hatch, 3:23-cv-00985 (M.D. Fla.) |
| S23 | Cincinnati ECC / Amir Jordan wrongful death (~2026-08 filing) |
| S24 | GAO-26-107434 OPTN; HRSA AOOS dashboards 2026 |
| S25 | EPA RMP Safer Communities 2024; Stop Work Authority; 2026 Common Sense RMP proposal |
| S26 | DOE Bulk-Power System RFI, 91 FR ~2026-09-09; comments due 2026-10-09 |
| S27 | Colorado ADMT rules 4 CCR 904-6; comments through 2026-10-26 (crowded — listed for exclusion) |
