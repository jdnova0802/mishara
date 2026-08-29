# Intelligence Capability Kit — Full Tiers

Version 1.0 — August 2026  
Companions: *Intelligence Capability Tree* · *OSINT Capability Ladder*  
Layer: **volatile** (gear, apps, vendors, prices). Re-check quarterly.  
Footings: **A** open/lawful purchase · **B** written authorization · **C** regulated intercept · **D** human contact  
Default in this kit: **Footing A + no-touch.** Footing B items are marked. C/D are not stocked here.

---

## 0. How to read this

Each tier is a **complete kit snapshot**: what you should physically have, what runs on the phone, what runs on the research machine, which accounts exist, and what the desk/network looks like.

**Inheritance rule:** Tier *N* includes everything in Tier *N−1* unless replaced. Lists below are additive.

**Branch rule:** The core kit is cross-branch (enablers + OSINT spine). Branch add-ons appear after the core tiers. Do not buy SIGINT/HUMINT kits from a blog post — those need their own counsel-backed docs.

**Cost bands** are indicative US retail as of Aug 2026 mindset; confirm on vendor pages before committing.

---

## Tier 0 — Ad hoc

**Capability:** Answer one question once, by hand.  
**Ceiling:** Not repeatable, not preserved, not defensible.  
**Move up when:** Same shape of question twice, or the answer might matter to someone else.

### Devices
| Item | Spec / note |
|------|-------------|
| Whatever phone and laptop you already own | Personal machine — acceptable only at Tier 0 |
| No dedicated research hardware | — |

### Phone (personal — accept the risk)
| App / function | Purpose |
|----------------|---------|
| Stock browser or Firefox Focus | Quick lookups |
| Maps (Google Maps / Apple Maps / Organic Maps) | Rough geo |
| Camera + Files | Screenshots you will probably lose |
| Authenticator you already use | Only if you must; prefer not mixing |

**Do not:** install a pile of “OSINT apps,” create research accounts on your daily phone, or SMS-verify anything investigative to your real number.

### Laptop / desktop
| App | Purpose |
|-----|---------|
| Browser | Search, whois web UIs, archive.today, Wayback |
| Notes app or plain text | Scratch — not a case system |
| PDF reader | Reports you found |

### Accounts
- Personal Google/Microsoft/Apple (contamination accepted at Tier 0 only)
- Optional: free Shodan/Censys/Netlas account for curiosity queries

### Setup look
One browser window, one notes file, no VPN discipline, no evidence hash. Fine for curiosity. Useless for anything you’d stake a claim on.

### Explicitly not in Tier 0
Dedicated machine, Hunchly, Maltego Graph workflows, burner SIM, VPS, proxies, case vault, active scanners against third parties.

---

## Tier 1 — Foundation

**Capability:** Structured, repeatable, compartmented investigation on a single research machine. Every major selector type has a starting playbook.  
**Cost:** roughly $0–100/mo + one-time hardware.  
**Ceiling:** Manual; weak persistence between cases; thin chain of custody.  
**Move up when:** Someone asks “how do you know that?” and you lack a timestamped answer.

### Devices
| Item | Spec / note |
|------|-------------|
| **Dedicated research laptop or desktop** | Not your personal daily driver. Full-disk encryption on (BitLocker / FileVault / LUKS). |
| RAM | **32 GB minimum** if you run VMs seriously; **64 GB** comfortable |
| Storage | Fast NVMe; room for VM snapshots (1 TB+ realistic) |
| Optional: cheap second USB NIC or travel router | Beginnings of traffic separation |
| Optional: hardware security key | YubiKey-class for research account MFA |

### Phone kit (research — physically separate if you can)
Prefer a **dedicated cheap Android** (GrapheneOS on Pixel if you can swing it; stock Android in a work profile if not) over loading research onto your daily phone.

| App / function | Purpose | Notes |
|----------------|---------|-------|
| **Firefox** + uBlock Origin | Compartmented browsing | Separate profile; no Google login |
| **Organic Maps** or **OsmAnd** | Offline/map work without wrapping every pin in a Google account |
| **Signal** (research identity only) | Rare; only if a workflow truly needs it | Never link to personal contacts |
| **2FAS / Aegis** (or similar FOSS TOTP) | MFA for research accounts | Not your personal Authy backup |
| **Simple Gallery / Files** | Hold captures offline | Export to encrypted vault ASAP |
| **VPN client** (Mullvad / IVPN / Proton — pick one paid) | Research egress | Always on for research phone |
| SMS: **burner SIM or app number** (TextNow / Hushed / physical prepaid) | Verification | Never your real number or iMessage |
| **Optional:** Camo/secondary cam unused | Do not give biometrics to research accounts | FaceID/TouchID off for research IDs |

**Phone OPSEC rules at Tier 1**
- No personal Apple/Google ID on the research phone  
- No contacts sync, no fingerprint/face enrolled for research apps  
- No payment cards that touch your real identity  
- Screenshots are not evidence yet — they become evidence when hashed/stored on the research machine

### Research machine — OS and environment
| Item | Purpose |
|------|---------|
| Host OS with FDE | Debian/Ubuntu/Fedora/macOS/Windows hardened baseline |
| **Trace Labs OSINT VM** (current default bundle) **or** roll-your-own Debian | Investigation environment |
| Optional: **Tsurugi** or **CSI Linux** | Heavier analysis / forensics-oriented |
| **VirtualBox / VMware / KVM / UTM** | Snapshot discipline |
| Firefox Multi-Account Containers **or** separate Chromium/Brave profiles | Browser compartmentation |
| Host firewall; research VM behind VPN/gateway — not naked home IP | Attribution basics |

**Dead — do not follow guides that recommend:** Buscador (discontinued). Treat the rest of that guide as stale.

### Core software (Tier 1 spine — Footing A)
| Category | Have these |
|----------|------------|
| Notes / case scratch | **Obsidian** (or Logseq) — one vault per case or strict folder hygiene |
| Archive | Browser bookmarks to **Wayback**, **archive.today**; local save-as when needed |
| Infra recon (passive-first) | **subfinder**, **httpx**, **theHarvester**, **Amass** or Sublist3r, **crt.sh** usage, WHOIS/RDAP, dig/drill |
| Still useful | **Nmap** — know when it is active; do not point it at third parties without Footing B |
| Metadata | **ExifTool** |
| Geo / verify | Browser + Bellingcat Online Investigation Toolkit index; **InVID / WeVerify** browser plugin |
| On-chain (light) | Browser: **Breadcrumbs**, **MetaSleuth**, **Arkham** free, standard explorers |
| Link analysis (light) | **Maltego CE** and/or **SpiderFoot** (self-hosted or local) |
| Password manager | **Bitwarden** / KeePassXC — research vault separate from personal |
| VPN | Same provider as phone; kill switch on |

**ProjectDiscovery note:** `subfinder` / passive use = kit OK. **`naabu` / `nuclei` against third parties = Footing B only.** Keep them installed if you do authorized ASM; do not treat them as default OSINT.

### Accounts to open at Tier 1
| Account | Why |
|---------|-----|
| Free tiers: Shodan, Censys, ZoomEye, FOFA, Netlas, Criminal IP | Each covers gaps; free is demo-grade |
| Have I Been Pwned (or equivalent API) | Exposure checks — query, don’t use passwords |
| GitHub (research) | Clone tools; not your personal identity if avoidable |
| Dedicated research email (Proton / Tuta / separate Google under research OPSEC) | Sock/account recovery without personal crossover |
| archive.today / similar — no login required | Cite-after-archive habit |

**If you spend one dollar on scan data:** Shodan’s one-time membership is still usually the best first paid chip (confirm live pricing).

### Network / desk look at Tier 1
```
[Home ISP]
    └── optional travel router / guest VLAN
            └── Research laptop (FDE)
                    ├── Host VPN
                    └── TL OSINT VM (snapshots)
                            ├── Firefox containers (case A / case B / sock)
                            └── Tool CLI + Obsidian vault (encrypted disk)
[Research phone + burner SIM] —— VPN —— never shares Apple/Google ID with daily phone
[Daily phone / daily laptop] —— air gap in habits; no research logins
```

### Playbook stubs you must write (even if short)
Domain · IP · email · username · phone · image · wallet — one page each: first five moves, stop rule, what to archive.

### Explicitly not required yet
Hunchly paid, second attribution machine, residential proxy pool, always-on collectors, MISP/OpenCTI, commercial SOCMINT suites, team QA.

---

## Tier 2 — Defensible practitioner

**Capability:** Evidence discipline. Timestamped hashed capture; case system; source log; confidence-graded reports; graphs bigger than working memory.  
**Cost:** roughly $200–1,000/mo all-in for a serious solo.  
**Ceiling:** Point-in-time; weak “when did this change?”; each case still starts cold.  
**Move up when:** The product shifts from investigation to monitoring.

### Devices (add)
| Item | Spec / note |
|------|-------------|
| **Second physical machine** (or strictly isolated mini-PC) | Attribution-sensitive browsing; VM isolation ≠ fingerprint isolation |
| **Encrypted external SSD** | Evidence retention with a *written* retention period |
| Dedicated burner phone **with physical prepaid SIM** | Prefer physical over app-numbers for longevity |
| Hardware keys (2+) | Research admin + evidence vault MFA |
| Optional: Faraday pouch | Phone storage when OPSEC moments matter |

### Phone kit (add)
| App / function | Purpose |
|----------------|---------|
| Separate research APKs only via F-Droid / Aurora where sane | Reduce Play Services tether |
| Secure camera app that does not auto-cloud | Field photos of documents/scenes you are allowed to shoot |
| Offline password vault client | Bitwarden/KeePass sync to research vault only |
| Optional: session-isolation browsers (Falcon / Mulvad browser if available on your platform) | Extra compartment |

Still **no** personal banking apps, personal social apps, or real-name SIM on this device.

### Research software (add — highest leverage first)
| Item | Why it earns Tier 2 |
|------|---------------------|
| **Hunchly** (or equivalent capture-as-you-browse with hashing) | Single highest-leverage purchase — browsing becomes evidence |
| Maltego **paid** transforms if CE is choking you | Interactive link analysis at real volume |
| SpiderFoot automation sweeps | Breadth-first collection into a DB |
| **reNgine** or Faraday | Consolidation UI / aggregation |
| Local WARC tooling (wget/wget2 WARC, browser export discipline) | Archive you control |
| Report template | Confidence grading (Admiralty or equivalent) baked in |
| Optional: Multilogin / GoLogin / AdsPower | Fingerprint-isolated browser profiles for research identities — still prefer logged-out; no engagement |

### Sock-puppet / research-identity stack (minimum viable — all required together)
Only for identities you need; default remains logged-out Footing A.

1. Dedicated browser profile or antidetect profile  
2. Dedicated VPN **or** residential proxy egress (different geo if the legend needs it)  
3. Dedicated email  
4. Dedicated phone number  
5. Distinct fingerprint (UA, resolution, TZ, language)  
6. No biometric / payment crossover  
7. **Age the account** before it matters — fresh accounts burn fast  

**Legal tension:** fake accounts + accepted ToS sank hiQ even when CFAA scraping held. Prefer logged-out. If you must log in, treat it as regulated tradecraft, not a default toggle.

### Accounts / data (add)
| Spend | Role |
|-------|------|
| Shodan membership / Monitor if you need alerting lite | Scan data that isn’t demo-grade |
| Censys starter if cert-heavy workflows dominate | Precision over bulk |
| Netlas cheap paid if budget is tight | Fresh scan data |
| VirusTotal / urlscan.io API keys as needed | File/URL pivots |
| Sanctions / company-data credits where your CORPINT lane needs them | Jurisdiction-dependent |

### Evidence & case look at Tier 2
```
CaseID/
  00_question_and_done.md      # stop rule
  01_source_log.csv            # URL, UTC time, hash, tool, note
  02_entities/                 # one note per entity
  03_captures/                 # Hunchly export + WARC + screenshots
  04_graphs/                   # Maltego / exports
  05_report.md                 # graded confidence
Evidence SSD ← hashed exports; retention clock started
```

### Network / desk look at Tier 2
```
[ISP] → router with guest/research VLAN
          ├── Research primary (tools, Obsidian, Hunchly, VMs)
          ├── Attribution box (browser-only, separate fingerprint world)
          ├── Evidence SSD (plugged in only when sealing)
          └── Research phone + prepaid SIM
Proxies/VPN egress documented per case in source log
Daily life devices never join the research VLAN
```

### Explicitly not required yet
Always-on collectors, multi-VPS fleet, TIP (MISP/OpenCTI), commercial SOCMINT platform seats, second analyst review as a role.

---

## Tier 3 — Continuous collection

**Capability:** Standing pipelines; owned collection infrastructure; persistent datastore with history; alerting on change. Longitudinal archive ≠ investigation service.  
**Cost:** roughly $1,000–10,000/mo — increasingly infra, not licenses.  
**Ceiling:** Solo breaks. Pipelines need care whether or not a client is active. Gaps cannot be backfilled.  
**Move up when:** Maintenance > ~1 day/week, or you-as-SPOF is unacceptable.

### Devices / infra (add)
| Item | Spec / note |
|------|-------------|
| **Always-on collection hosts** | Small **VPS fleet** preferred over home lab (home IP = attribution + uptime tax) |
| Object storage or dedicated backup box | Archive durability; versioned |
| Monitoring for collectors | Uptime + “last successful run” alerts to you |
| Residential / mobile proxy pool (paid) | When targets or platforms demand non-DC egress — document legality per use |
| Optional: colocation / mini-PC in a site you control | Only if you understand the attribution story |

### Software / platforms (add)
| Item | Purpose |
|------|---------|
| Schedulers | cron / systemd timers / GitHub Actions self-hosted / Prefect-class — pick one and standardize |
| Datastore | Postgres + object store, or equivalent; **history tables**, not overwrite |
| Alerting | Change detect on domains, certs, selected social surfaces, watchlists |
| Passive DNS / CT monitoring | Continuous, not one-shot |
| Optional: OpenCTI or MISP | Only if you will spend 1–4 h/week keeping it honest; else wire feeds into what you already run |
| Optional: commercial SOCMINT (ShadowDragon, Social Links, Skopenow, Babel Street, …) | Expensive; vendor dependency; Tier 3+ budget |

### CTI feed kit (small shop)
Wire **2–3** high-signal free feeds before buying a TIP: abuse.ch (URLhaus, MalwareBazaar, ThreatFox), CISA KEV; then OTX/Spamhaus/CIRCL as needed.

### Phone / laptop changes at Tier 3
- Phone stays a field/2FA/capture device — **collectors do not run on phones**  
- Primary laptop becomes an **admin terminal** for the fleet more than a collector  
- MFA hardware keys everywhere; no SMS MFA on infra

### Desk / architecture look at Tier 3
```
                    ┌─ Collector VPS (certs/DNS/watchlists)
[Proxy/VPN mesh] ───┼─ Collector VPS (SOCMINT logged-out scrapers you can defend)
                    └─ Collector VPS (feed ingest)
                              ↓
                     Datastore + object archive
                              ↓
                     Alert → Analyst laptop (Tier 2 evidence workflow)
                              ↓
                     Case reports (still human-sealed)
```

### Ops habits that are now part of the kit
- Runbook per collector; who restarts it; how to detect silent failure  
- Backup restore tested quarterly  
- Written retention/deletion on the archive  
- Footing tag on every collector (A vs B)

### Explicitly not required yet
Named QA role, accreditation, enterprise Chainalysis/TRM seats, 24/7 shift roster.

---

## Tier 4 — Team

**Capability:** Parallel casework, specialization, review. Governance becomes the product.  
**Cost:** Headcount-dominated; tooling is a rounding error.  
**What actually changes:** Access control, audit logs, retention, legal review, written tradecraft standard, second reader before anything leaves.

### Devices / identity (add)
| Item | Spec / note |
|------|-------------|
| Standard analyst build image | Same VM/golden image for every hire |
| Central image management | Packer/Ansible/MDM — reproducible environments |
| Hardware token MFA on **everything** | No exceptions for “just Slack” |
| Separate roles’ access | Collectors ≠ analysts ≠ admin break-glass |
| Shared evidence locker with ACLs | Not a shared Google Drive free-for-all |

### Apps / collaboration (add)
| Item | Purpose |
|------|---------|
| Case management that supports roles | Even if it’s still Obsidian + git + review PR discipline at small scale |
| Ticketing | Jira/Linear/etc. — engagement → question → done |
| Comms | Tiered: open ops chat vs case-restricted channels |
| Secrets manager | Team vault; no secrets in Discord |
| Code/config repo for collectors | Review required to change a scraper |

### Process artifacts that count as “kit”
- Written tradecraft manual (the doc becomes a manual, not notes)  
- Confidence standard + report template enforced  
- Second-reader checklist  
- Named counsel / legal escalation path  
- Engagement acceptance & decline criteria  
- Onboarding kit clone of Tier 2 desk in &lt;1 week  

### Desk look at Tier 4
```
Analyst A ─┐
Analyst B ─┼─ SSO / MDM / golden image ─ Case ACLs ─ Evidence locker
Collect Eng─┘              │
                           ├─ QA / review gate
                           └─ Legal on-call path
Infra runs Tier 3 fleet with on-call rotation (even if small)
```

---

## Tier 5 — Institutional

**Capability:** Platform-class tooling, licensed commercial feeds, formal standards, accreditation, work that requires them (gov, regulated finance, litigation support).  
**Reality:** Procurement and compliance posture as much as tech. Many enterprise forensic/intel platforms **are not sold to individuals.**

### What appears in the kit (examples — vendor landscape moves)
| Lane | Institutional-class examples |
|------|------------------------------|
| On-chain | Chainalysis, TRM Labs, Elliptic, Crystal |
| SOCMINT / fused intel | Babel Street, ShadowDragon enterprise, equivalent |
| Forensic platforms | EnCase/Magnet/Cellebrite-class where DFIR is in-scope (**Footing B / lawful possession**) |
| TIP / fusion | Enterprise OpenCTI/MISP deployments, commercial TIPs |
| Accreditation | GIAC/GOSI as ticket items; org policies, audits, clearances as required |
| Facilities | Badge access, visitor rules, classified/controlled handling if applicable |

### What “setup looks like”
Less like a hacker desk, more like: controlled endpoints, DLP, audit, vendor contracts, DPIA/legitimate-interest records, retention legal holds, insurer questionnaires answered with evidence.

---

## Branch add-ons (bolt onto the core tier)

Buy these only when that branch is in your active build order (see Capability Tree §8).

### OSINT / infra (A)
Already in core Tier 1–2. Depth: OSINT Capability Ladder §4.

### SOCMINT (A default; D if you engage)
| Tier | Add |
|------|-----|
| 1 | Logged-out browser discipline; archive-before-cite; toolkit bookmarks |
| 2 | Research identities + antidetect **if required**; Hunchly on social captures |
| 3+ | Commercial SOCMINT platform or defended custom collectors |

### GEOINT / imagery (A)
| Tier | Add |
|------|-----|
| 1 | InVID/WeVerify, ExifTool, Google Earth Pro, Sentinel Hub / OSM, Bellingcat toolkit |
| 2 | Offline map packs on research phone; structured geolocation notes (cues → candidate → confirm) |
| 3 | Watchlists on areas/sensors you actually revisit |

### FININT / on-chain (A public layer)
| Tier | Add |
|------|-----|
| 1 | Explorers + Breadcrumbs/MetaSleuth/Arkham free; label timestamp discipline |
| 2 | Maltego crypto entities; graph exports into case file |
| 5 | Chainalysis/TRM/Elliptic-class |

### CORPINT (A)
| Tier | Add |
|------|-----|
| 1 | Register bookmarks per jurisdiction you touch; OpenCorporates-class; PDF account dumps into vault |
| 2 | Paid credits for stubborn jurisdictions; officer graph in Maltego/Obsidian |

### Breach exposure (A — query only)
| Tier | Add |
|------|-----|
| 1 | HIBP / reputable broker queries |
| 2 | Written rule: never attempt login with recovered credentials |

### CTI / CYBINT passive (A)
| Tier | Add |
|------|-----|
| 1–2 | abuse.ch + KEV + VT/urlscan as needed |
| 3 | TIP only with a maintainer |

### ASM / authorized recon (**Footing B**)
| Tier | Add |
|------|-----|
| B-kit | Written RoE + scope file; `naabu`/`nuclei`/Burp/etc. allowed **only** in-scope; separate “authorized” browser/VM profile; engagement letter in the case root |

### DFIR (**Footing B** — lawful possession)
| Tier | Add |
|------|-----|
| B-kit | Write blockers, imaging tools, volatility order cheatsheet, evidence bags/labels, isolated analysis VM (Tsurugi-class), counsel on seizure/privacy |

### SIGINT / HUMINT / TECHINT intercept & contact
**Not stocked in this kit.** Different legal footing (C/D). No phone-app list here on purpose.

---

## One-page shopping lists

### Buy / set up for Tier 1
1. Dedicated research computer + FDE + 32–64 GB RAM + NVMe  
2. Trace Labs OSINT VM (or roll-your-own) + snapshot habit  
3. VPN (paid) + Obsidian + Bitwarden/KeePassXC research vault  
4. Firefox containers / separate profiles  
5. ExifTool, InVID, passive CLI recon tools  
6. Research email + free scan-platform accounts  
7. Optional: cheap research phone + prepaid SIM + TOTP app  

### Upgrade package for Tier 2
1. Hunchly  
2. Encrypted evidence SSD + retention policy written  
3. Second attribution machine or strict antidetect profiles  
4. Physical burner SIM discipline  
5. Case folder template + source log + graded report template  
6. First paid scan membership (often Shodan)  
7. Maltego/SpiderFoot workflow you can repeat  

### Upgrade package for Tier 3
1. VPS fleet + object storage + scheduler  
2. Change-alerting on your real watchlists  
3. Proxy strategy documented  
4. Backup/restore drill  
5. Feed ingest; TIP only if staffed  

### Upgrade package for Tier 4
1. Golden analyst image + MDM/SSO  
2. ACL’d evidence locker + audit logging  
3. Second-reader gate + tradecraft manual  
4. On-call for collectors  
5. Named legal path  

### Tier 5
Procurement, accreditations, enterprise contracts — not a shopping cart.

---

## AI layer (any tier — bolt-on rules)

| Do | Don’t |
|----|-------|
| Use LLMs to structure tool output, draft timelines, suggest pivots | Let model output enter a report unverified |
| Sandbox tool execution (containers, timeouts, rate limits) | Give an agent untrusted page content **and** consequential actions in one loop |
| Treat output as junior-analyst first draft | Autonomously run active scanners |

---

## Relationship table

| Concern | Document |
|---------|----------|
| Branch map & legal footings | *Intelligence Capability Tree* |
| OSINT tier philosophy & deep tool/legal notes | *OSINT Capability Ladder* |
| **What to own/run at each tier (this file)** | *Intelligence Capability Kit* |
| SIGINT / HUMINT / exploit inventories | Counsel-backed docs only |

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Aug 2026 | Initial full Tier 0–5 kits: devices, phone apps, software, accounts, desk diagrams, branch add-ons, shopping lists |
