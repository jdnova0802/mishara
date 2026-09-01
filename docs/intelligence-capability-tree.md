# Intelligence Capability Tree

Version 1.1 — August 2026  
Companions: *OSINT Capability Ladder* v1.0 · *Intelligence Capability Kit* (devices / apps / setup by tier)  
Review cadence: quarterly (next: November 2026)

---

## 0. How to use this document

The OSINT ladder is one branch. This document is the **trunk and the rest of the canopy**.

**Stable layer** — what each branch *is*, what question it answers, what legal footing it sits on, and how it connects to the others. Sections 1–4 and 7. Multi-year timescale.

**Volatile layer** — tools, vendors, prices, case law that currently deliver each branch. Section 5–6 and 8. Months-scale staleness. When you update, touch volatile only unless the field genuinely shifted.

**Rule of depth:** this tree maps *where you are* and *what you are not yet doing*. For a branch that has its own ladder (OSINT today), go to that ladder for tiering, cost bands, and playbooks. For **what to own and run at each tier** (devices, phone apps, software, desk/network layout), use the *Intelligence Capability Kit*. Do not duplicate gear lists here.

**The stop rule still applies everywhere.** Every engagement gets a written question and a written definition of done before collection starts. If a further pivot would not change a decision, stop pivoting.

---

## 1. Scope and the four legal footings

Not every branch of this tree is “open source.” Mixing them without naming the footing is how people walk into criminal exposure while thinking they are doing research.

| Footing | What it covers | Default posture |
|---------|----------------|-----------------|
| **A — Open / lawful purchase** | Published, publicly accessible, or lawfully purchasable data | Default for civilian practitioners; defendable if purpose and retention are written |
| **B — Authorized access** | Systems, networks, accounts, or premises you own or have *written* authorization for | Required for active scanning, forensics on third-party systems, nuclei/naabu against live targets |
| **C — Regulated interception** | RF/wireless capture, wiretap-class SIGINT, IMSI work | Statute-gated; no “research purposes” carve-out in major jurisdictions |
| **D — Human contact** | Interview, pretext, sock-puppet engagement that creates a relationship with the subject | ToS + fraud + privacy risk; Trace Labs “no-touch” is the safe default for A-footing work |

**Hard exclusions (own document + counsel, never improvisation):**
- Authentication bypass / CFAA-class unauthorized access
- Device or account takeover, credential use, password resets on systems you don’t own
- Active exploitation without written authorization
- Interception without statutory authority
- Contact with minors in any investigative pretext framing

If a technique needs Footing B, C, or D, it is **not** an OSINT technique that got aggressive. It is a different branch.

---

## 2. The tree — stable layer

```
INTELLIGENCE & INVESTIGATION CAPABILITY
│
├── 1. COLLECTION (how information enters)
│   ├── 1.1 OSINT .............. open published sources          [Footing A]
│   ├── 1.2 SOCMINT ............ social platforms & graphs       [A; D if engaged]
│   ├── 1.3 GEOINT / IMINT ..... place, imagery, verification    [A; B for tasked]
│   ├── 1.4 FININT ............. money, filings, on-chain         [A; B for bank]
│   ├── 1.5 CORPINT ............ registries, ownership, filings   [A]
│   ├── 1.6 BREACH / EXPOSURE .. already-leaked credentials       [A; careful use]
│   ├── 1.7 CYBINT ............. adversary infra, malware, logs  [A/B]
│   ├── 1.8 SIGINT ............. signals / RF / intercept         [C]
│   ├── 1.9 HUMINT ............. human sources & contact          [D]
│   ├── 1.10 MASINT ............ measurement & signatures        [B/C]
│   └── 1.11 TECHINT ........... captured materiel / firmware    [B]
│
├── 2. ANALYSIS (what you do after collection)
│   ├── 2.1 Identity / entity resolution
│   ├── 2.2 Link / network analysis
│   ├── 2.3 Temporal / change analysis
│   ├── 2.4 Geospatial fusion
│   ├── 2.5 Credibility & structured analytic techniques
│   ├── 2.6 Targeting & prioritization
│   └── 2.7 All-source fusion & product writing
│
├── 3. MISSION SURFACES (where the tree is applied)
│   ├── 3.1 Cyber threat intelligence (CTI)
│   ├── 3.2 Digital forensics & incident response (DFIR)
│   ├── 3.3 Attack surface / authorized recon (ASM)
│   ├── 3.4 Corporate due diligence & risk
│   ├── 3.5 Fraud / insurance / civil investigation
│   ├── 3.6 Missing persons / humanitarian (no-touch default)
│   ├── 3.7 Journalism / accountability reporting
│   ├── 3.8 Litigation support / e-discovery adjacent
│   └── 3.9 Protective / OPSEC / counter-collection
│
├── 4. ENABLERS (load-bearing under every branch)
│   ├── 4.1 Evidence discipline & chain of custody
│   ├── 4.2 Case management & source logging
│   ├── 4.3 Collection engineering & pipelines
│   ├── 4.4 Research OPSEC & compartmentation
│   ├── 4.5 Legal / compliance / retention
│   ├── 4.6 Training, review, accreditation
│   └── 4.7 AI orchestration (assistive only)
│
└── 5. ALTITUDE (cross-cutting maturity — same idea as OSINT tiers)
    Tier 0 Ad hoc → 1 Foundation → 2 Defensible → 3 Continuous
    → 4 Team → 5 Institutional
```

You can be **Tier 3 on OSINT infrastructure** and **Tier 1 on GEOINT verification**. That is normal. Being deliberate about which branch you are climbing is the point.

---

## 3. Collection branches — what each buys you

### 1.1 OSINT — Open-source intelligence
**Answers:** What is already published or lawfully purchasable about X?  
**Ceiling without other branches:** Point-in-time public record; weak on private intent, encrypted comms, and anything behind auth.  
**Depth doc:** *OSINT Capability Ladder* (stable tiers, tool stack, training, legal map).  
**Do not smuggle in:** nuclei/naabu against third parties, logged-in scraping that violates accepted ToS, RF capture.

### 1.2 SOCMINT — Social media intelligence
**Answers:** What do people and groups say, show, and connect to in public social spaces?  
**Structural fact:** the open-API era is over. Unauthenticated surface is shrinking; commercial platforms and brokers filled the gap with vendor lock-in and legal exposure.  
**Split from OSINT on purpose:** platform ToS, sock-puppet pressure, and biometrics make the footing unstable even when the content looks “public.”  
**Safe default:** logged-out, archive-before-cite, no liking/commenting/friending/joining closed groups.  
**Move carefully:** dedicated research accounts with OPSEC are Footing-D-adjacent the moment they interact; hiQ’s sequel loss was contract + fake accounts, not CFAA.

### 1.3 GEOINT / IMINT
**Answers:** Where and when did this happen, and is the media real?  
**Core moves:** geolocation from visual cues, satellite/aerial correlation, shadow/sun analysis, metadata (when present), reverse image search, synthetic-media detection as *lead not finding*.  
**Ceiling:** rural/indoor scenes, depleted EXIF, adversarial degradation of deepfake detectors. Corroborate; never single-source a location from a model score.

### 1.4 FININT
**Answers:** Where did the money go; who controls the purse?  
**Public layer:** corporate filings, sanctions lists, procurement, charity registers, on-chain explorers and clustering.  
**Closed layer:** bank records, SAR/CTR, exchange KYC — Footing B / legal process.  
**Discipline:** on-chain txs are immutable; **entity labels are not**. Timestamp every query and record the label you saw.

### 1.5 CORPINT — Corporate / registry
**Answers:** Who owns this entity, who controls it, what has it filed, where does it nest?  
**Spine:** company registers, beneficial ownership where available, annual accounts, trademarks, patents, domain/WHOIS adjacency, officer cross-links.  
**Ceiling:** nominee directors, offshore opacity, and jurisdictions that sell access slowly or not at all. Tier jumps here are often data-budget jumps, not skill jumps.

### 1.6 Breach and credential exposure
**Answers:** What identifiers are already in leaked corpora?  
**Use rule:** treat as *exposure intelligence*, not a password stash. Checking whether an email appears in a breach ≠ using a recovered password. The second is account access (excluded).  
**Operational hygiene:** query through reputable brokers/HIBP-class APIs; do not hoard raw breach dumps you have no lawful basis to hold.

### 1.7 CYBINT — Cyber collection
**Answers:** What infrastructure, malware, tooling, and victimology describe this actor or campaign?  
**Overlaps OSINT** on passive DNS, CT logs, scan-data platforms, public sandboxes.  
**Crosses into Footing B** the moment you actively probe, detonate against third-party infra, or pull telemetry you are not entitled to.  
**Keep the line visible:** passive CTI feeds and public reports = A; your own honeypot/telemetry and authorized response = B.

### 1.8 SIGINT
**Answers:** What was transmitted, by whom, on what channel?  
**Not OSINT.** RF, wifi capture, IMSI, uplink intercept sit on Footing C.  
**Civilian-adjacent edges that still need care:** openly published signal databases, ADS-B/AIS aggregators, amateur radio logs — often A if you only consume published feeds; collecting from the air yourself is a different act.  
**Own document required** before any collection design.

### 1.9 HUMINT
**Answers:** What will a person tell you, show you, or introduce you to?  
**Not OSINT.** Includes interviews, cultivating sources, pretext, and most sock-puppet *engagement*.  
**No-touch rule** (Trace Labs and peers): correct default for work you may later have to defend under Footing A.  
**Own document + ethical/legal review** for any contact path.

### 1.10 MASINT
**Answers:** What does measurement of physical phenomena reveal (radar signature, chemical, spectral, acoustic)?  
**Mostly state / lab / industrial.** Practitioners meet thin edges via open scientific datasets and remote-sensing products — usually better filed under GEOINT until you have actual MASINT instrumentation and authority.

### 1.11 TECHINT
**Answers:** What does this device, firmware, or captured system reveal about capability and origin?  
**Footing B** almost always (you need lawful possession). Overlaps DFIR and malware analysis; distinct when the object is materiel rather than a live case disk.

---

## 4. Analysis, mission surfaces, enablers

### 4.1 Analysis branches
| Branch | Failure mode if skipped |
|--------|-------------------------|
| Identity resolution | You collect forever and never collapse selectors into entities |
| Link analysis | Relationships stay in your head; graphs > working memory break you |
| Temporal / change | Point-in-time answers; cannot say “when did this change” |
| Geospatial fusion | Photos and claims never meet a map |
| Credibility (Admiralty / CRAAP / ACH) | Confident wrong; no graded confidence in the product |
| Targeting | Everything is interesting; nothing is decided |
| All-source fusion & writing | Collection theater with no decision-useful product |

Analysis maturity usually lags collection. Tier 2 in the OSINT ladder sense (“defensible practitioner”) is mostly an **analysis + evidence** upgrade, not a tool upgrade.

### 4.2 Mission surfaces
Same branches, different acceptance criteria:

| Surface | Dominant branches | Non-negotiable |
|---------|-------------------|----------------|
| CTI | CYBINT, OSINT, FININT (ransom), analysis | IOC hygiene, ATT&CK mapping, feed discipline |
| DFIR | TECHINT/CYBINT, evidence, temporal | Chain of custody, volatility order, legal hold |
| ASM / authorized recon | OSINT + active tooling | **Written authorization**; scope file; no scope creep |
| Due diligence | CORPINT, FININT, OSINT, SOCMINT | Source log, confidence grades, retention limits |
| Fraud / insurance / civil | FININT, OSINT, SOCMINT, evidence | Defensible capture; counsel early |
| Humanitarian / missing persons | OSINT, SOCMINT, GEOINT | No-touch; welfare over scoop |
| Journalism | OSINT, GEOINT, HUMINT (on record) | Verification culture; source protection |
| Litigation support | Evidence, CORPINT, DFIR-adjacent | Discovery rules; privilege; vendor accreditation |
| Protective / OPSEC | Counter-collection across all | Assume your research traffic is visible |

### 4.3 Enablers (steal these from the OSINT ladder; they are not OSINT-specific)
- **Evidence:** timestamped, hashed capture (Hunchly-class or WARC); archive before cite.
- **Case system:** source log, entity files, report format with confidence grading.
- **OPSEC:** separate machine/VLAN, compartmented browsers, no personal IP/payment crossover on research identities.
- **Pipelines:** Tier 3+ standing collectors; gaps cannot be backfilled.
- **Governance (Tier 4+):** access control, retention/deletion, second reader, named legal escalation, written decline criteria.
- **AI:** orchestration and draft only. Hallucination is the dominant failure mode. Never give an agent untrusted page content *and* consequential actions in one loop.

---

## 5. How branches force each other (volatile intuitions, stable pattern)

These edges are why a single-branch ladder is not enough:

| You are strong in… | You hit a wall that requires… |
|--------------------|-------------------------------|
| OSINT domains/IPs | CYBINT / CTI to interpret adversary use |
| SOCMINT claims | GEOINT to verify place/time; FININT if money is asserted |
| On-chain FININT | CORPINT + OSINT to land identities off-chain |
| ASM actives | Evidence + authorization theater the moment findings matter |
| DFIR disk | OSINT/CTI to contextualize tooling and infra |
| Continuous OSINT archive | Collection engineering + Tier 4 staffing (solo breaks) |
| Any public graph | Legal/compliance when personal data (GDPR) or ToS bind |

**Promotion rule:** do not “upgrade tools” inside one branch when the ceiling is a **missing branch**. Buy or train the adjacent branch, or rewrite the question.

---

## 6. Legal map (tree-level — not advice)

Four fences that apply across branches (detail and citations live in the OSINT ladder §6 and counsel memos):

1. **Authentication** — bypass is criminal in kind (CFAA / CMA / equivalents).  
2. **Personal data** — public ≠ free to process without purpose (GDPR and kin).  
3. **Copyright** — extract facts, not creative expression.  
4. **Rate / harm** — volume that impairs a service invites civil theories even when content is public.

**Case-shaped lessons to keep at tree level:**
- Public scraping ≠ CFAA “unauthorized access” in the hiQ line — **and** contracts you accepted still bind; fake accounts change the animal.
- Logged-out public pages ≠ logged-in collection.
- Circumventing anti-bot / rate controls is a live dispute surface (watch pending theories under DMCA §1201-style claims).
- EU AI Act pressure on untargeted facial-image scraping and training-data provenance matters if corpora feed models.

**Operating posture:** default logged out; default stricter jurisdiction; per-field personal-data decision; separate collection from use; robots.txt as good-faith evidence, not magic law.

---

## 7. Governance triggers (any branch, Tier 3→4)

Before a second person touches the work, in writing:

1. Access control and audit logging on the case store  
2. Retention and deletion policy with default expiry  
3. Chain of custody for anything that could become evidence  
4. Confidence grading standard applied consistently  
5. Second-reader requirement on assessments that leave the building  
6. Named legal escalation path  
7. Engagement acceptance criteria, including what you decline  
8. **Branch footing register** — each live technique tagged A/B/C/D so nobody “accidentally” runs Footing-C work under an OSINT SOW

---

## 8. Build order (practical sequencing)

Not a moral ranking — a dependency ranking for a civilian practitioner building toward defensible work:

| Step | Build | Why this order |
|------|-------|----------------|
| 1 | Enablers 4.1–4.4 + OSINT Tier 1 | Without evidence/OPSEC, other branches just create liability faster |
| 2 | CORPINT + FININT (public) + GEOINT verification | Highest decision value per legal risk |
| 3 | SOCMINT logged-out + breach exposure (query, don’t use) | Powerful; ToS/privacy landmines |
| 4 | CTI feeds + passive CYBINT | Natural extension of infra OSINT |
| 5 | OSINT Tier 2 (Hunchly-class, case system, Maltego/SpiderFoot) | Makes all of the above defensible |
| 6 | Continuous collection (Tier 3) only on branches you will maintain | Archive gaps are permanent |
| 7 | Footing B surfaces (ASM, DFIR) only with written auth and separate playbooks | Different legal animal |
| 8 | Never “pick up” SIGINT/HUMINT/TECHINT casually | Own docs, own counsel, or leave closed |

Certifications (GOSI, GSOA, SANS SEC497/587, etc.) signal procurement readiness; Trace Labs CTFs and Bellingcat-grade verification practice signal actual skill. Buy credentials when a contract requires them.

---

## 9. Relationship to the OSINT Capability Ladder

| Concern | Lives in |
|---------|----------|
| OSINT tiers 0–5, cost bands, move-up triggers | OSINT ladder §2 |
| OSINT tool stack (PD, Shodan, Maltego, Hunchly, …) | OSINT ladder §4 |
| OSINT training path | OSINT ladder §5 |
| Full branch map, footings, mission surfaces | **This tree** |
| Devices, phone apps, software, accounts, desk layout by tier | **Capability Kit** |
| Passive vs active / A vs B line for recon tools | Tree for footing; ladder + kit for tools |
| SIGINT / HUMINT / exploitation playbooks | **Not here** — separate counsel-backed docs |

When the OSINT ladder’s volatile layer updates, update §5–6 pointers here only if a branch boundary moved (e.g. a platform shift that turns SOCMINT from A-default to D-required).

---

## 10. Update protocol

Quarterly, in order:

1. **Boundary drift** — did any platform, statute, or case move a technique across footings A→B/D?  
2. **Branch coverage** — new mission surface or analysis method worth a stable node?  
3. **Companion sync** — pull tier/tool/legal changes from the OSINT ladder changelog; refresh kit gear lists from vendor pages.  
4. **Closed branches** — confirm SIGINT/HUMINT/exploitation still explicitly out of improvisation scope.  
5. **AI layer** — rewrite, don’t edit, anything about agentic collection.

**Standing sources:** Bellingcat toolkit, Trace Labs Field Manual/CTFs, ProjectDiscovery release notes (passive vs active discipline), SANS SEC497/587 syllabi as practice-signal, primary case texts over aggregator blogs.

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Aug 2026 | Initial tree: collection × analysis × mission × enablers × altitude; four footings; companion to OSINT ladder v1.0 |
| 1.1 | Aug 2026 | Link *Intelligence Capability Kit* for full tier gear / phone / setup inventories |

---

## Source posture

Prices, vendor tiers, and case dockets belong in the OSINT ladder’s source appendix and vendor pages — not duplicated here. This document’s claims are structural. If a structural claim depends on a volatile fact (e.g. “open-API era is over”), re-verify at review cadence against primary platform developer docs and the ladder changelog.
