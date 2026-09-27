# Outbound research — receipt as product + priesthood counterparties

**Date:** 2026-09-15 (amended: first-door = S1/S3)  
**Mode:** Pitch ammo. No new sims. No Z11.  
**Law:** logos-before-actus. Fail-closed. Stranger-verifiable. `their_production: false`.  
**Confirm lab still green:** `python3 -m gate.sims.prove_all`

---

## Why this note (not more sims)

Tonight’s code only becomes real when **one person at one desk** can say yes or no. This note converts proved mouths into something that person can understand on a phone call:

1. **Receipt as product** — answers the honest catch of looking like Vanta/Verisk (another compliance dashboard). The difference is checkable in ~30s: stranger GET + machine `receipt_class` / `decision` / `reason_code` + digest bind — not log prose they must trust.
2. **Desk map** — names the **role**, not the department. Outreach usually dies talking to the wrong person at the right company (“fintech AI BD” instead of CDS MO; “algo desk” instead of CLS settlement ops).

**Landing frame:** the demo exists → next move is a human conversation, not another sim. Pick one desk and run the stranger-GET — **or stop**.

### First door (pinned)

| Priority | Mouth | Why |
|---|---|---|
| **1st cold open** | **S1 or S3** | Reachable desks; current pain (agent/BEC-shaped wire push; e-file integrity / post-file sanctions). Less gatekept than Z priesthoods. |
| **Ammo, not first call** | **Z1 / Z2 / Z3** | Prestige proofs of generality. Highest-stakes, most gatekept cold doors. Use *inside* an S1/S3 conversation (“same grammar already refuses at DC/CLS/root”) — do not lead with cold CLS/ISDA/IANA. |

Practical pick between S1 and S3: whichever warm path exists. If both cold — **S3** still ranks as the strongest institutional wedge (file mouth open; checkers crowded); **S1** if the contact is payments/agent-channel risk.

---

## 1. Receipt as the product

### The cut

Authorization systems already exist. What is still thin: a **stranger can fetch a denial** and branch on it without trusting the actor’s UI, admin console, or reason-string prose.

| Artifact | Who trusts it | Bank/ops can branch? |
|---|---|---|
| Log line / chat “denied” | Actor’s admin | No — narrative |
| JWKS-signed allow for *this* caller | Executor that holds the key path | Partial — caller-local |
| Network “trusted agent” signature | Merchant who verifies TAP | Recognition ≠ actus authorized |
| **Stranger GET receipt** (`receipt_class` + `decision` + digest bind) | Any outsider with the URL | **Yes** — machine fields |

**Bank-branchable** means: an outsider (ops, risk, auditor, counterparty, court clerk, journalist) can `GET` a stable object and switch on **`receipt_class` + `decision` + `reason_code`**, not parse English.

That is the concrete anti-dashboard claim. Vanta/Verisk-class products sell *visibility and attestation theater*. A skeptical ops person does not have to believe a narrative — they hit the URL and branch on machine fields. If the GET does not work without the actor’s login, it is still a log.

### Gate receipt classes (already pinned in lab)

| Class | Question answered | Emitter |
|---|---|---|
| `clearance` | Was *this* actus authorized? | Mouths (S1, S3, Z1–Z10…) |
| `threat` | Is the mouth context compromised? | S9 only |
| `watch_clear` | Sense layer clear for this check? | S9 |
| `preflight` | Does simulated delta match policy? | S10 |
| `epoch` | Is the policy epoch still LIVE? | S16 |

**Scenario X claim (sales):** S9 `watch_clear` + S10 `preflight` DENY alone must both be possible. Sense green ≠ actus authorized. Most stacks conflate these into one “risk score.”

S9 block on S1 → **clearance DENY** with `watch_block: true` + `threat_receipt_id` linking a **separate** threat object. Banks never overload one receipt to mean both “unauthorized” and “session hostile.”

### Competitor surfaces (honest)

| Player | What the outsider gets | Gap vs Gate-shaped receipt |
|---|---|---|
| **Fidacy** | Mandate → Ed25519 grant; executor redeems before pay; hash-chained audit | Strongest *payment* fence. Audit trail ≠ first-class stranger URL for non-pay actus. MCP install ≠ host-wide intercept. |
| **IntentFence** | ES256 JWS receipt (short TTL); JWKS at `/.well-known/jwks.json`; caller verifies digest then runs callback | Receipty and fail-closed for the *caller*. Service never holds keys and **does not enforce** downstream. Stranger verify of DENY is secondary to SDK local check. Payment-shaped (x402 / Base). |
| **Visa TAP / Intelligent Commerce** | RFC9421 HTTP Message Signatures; merchant recognizes approved agent + commerce intent; consumer/payment objects | **Recognize** layer. Network-scale ocean. Does not answer “may this bank push / file / publish?” — wrong priesthood. |
| **AgentPay-class MCP** | Caps + human approve + local sign | Ops wallet. No institutional stranger proof. |
| **Gate lab** | `receipt_url` → localhost stranger GET; `receipt_class` machine field; logos digest bind; clearance↔threat link; `their_production: false` stamped | Grammar + receipt across **pay and non-pay** mouths + priesthood demos. **Not** production rails. Not Fidacy/Visa replacement. |

### What makes a DENY bank-branchable (checklist)

A receipt is pitch-ready when **all** hold:

1. **Stable id + URL** — outsider fetches without actor login  
2. **Machine class** — `receipt_class` ∈ {clearance, threat, …}, not free text  
3. **Decision enum** — `ALLOW` | `DENY` (not “maybe” / score)  
4. **Reason code** — stable string (`no_live_grant`, `efsp_block_no_seal`, `headline_only`, …)  
5. **Digest bind** — logos/mandate/seal/resolution bound to the exact proposed actus  
6. **Link, don’t overload** — clearance may point at threat; never merge classes  
7. **Lab honesty flag** — `their_production: false` until a real weld exists  

IntentFence and Fidacy already clear several of these for *payment* callers. Gate’s differentiation for outbound:

- **Same grammar** on bank-send, EFSP transmit, DC Resolution, CLS settle, root-zone write  
- **Stranger GET as the demo** (show the fetch, not the dashboard)  
- **Class separation** (Scenario X) as a one-sentence claim competitors rarely make  

### Talking points (paste into pitch)

> We don’t invent agent recognition — Visa owns that ocean. We don’t claim we invented payment grants — Fidacy/IntentFence exist.  
> We refuse at irreversible edges, and a stranger can GET the receipt.  
> Clearance answers “may this actus?” Threat answers “is the mouth compromised?” Preflight answers “does the delta match?” Different objects. Banks branch on class, not prose.

### Demo order (human) — S1/S3 first

1. **Lead:** S1 `bank_send` DENY (no LIVE grant) → fetch clearance URL  
   — or S3 `efsp_block_no_seal` → fetch transmit/seal receipt (pick the warm desk)  
2. Optional: S9 hostile → clearance DENY + fetch linked threat (Scenario X setup)  
3. **Ammo only if asked / if rapport:** Z1 headline-only or Z2 unmatched settle → fetch  
   — proves the grammar is not accidentally finance-agent shaped; not the cold-open

No dashboard. The product surface in the room is the **GET**.

---

## 2. Priesthood counterparty map

Named owners > “banks.” Lab fixtures only — we do **not** claim production access. This map is for **who to talk to** and **who fetches the stranger receipt**.

### Z1 — ISDA Credit Derivatives Determinations Committee (publish)

| Role | Who | Notes |
|---|---|---|
| **Doctrine** | ISDA (2014 Credit Derivatives Definitions; DC Rules) | Standard terms the market incorporates |
| **Publish admin** | DC Administration Services, Inc. (DC secretary on behalf of ISDA) | Compiles questions, runs meetings, **publishes DC decisions** — does not vote |
| **Voters** | Regional DCs (Americas, EMEA, Asia ex-Japan, Australia-NZ, Japan) | 10 sell-side + 5 buy-side (+ consultative / CCP observers). Supermajority for Credit Event without external review |
| **Public surface** | [cdsdeterminationscommittees.org](https://www.cdsdeterminationscommittees.org/) | Resolutions, meeting statements, auction lists |
| **Outsider who cares** | CDS desk ops / middle office; CCP risk; buy-side compliance; journalists covering Credit Events | They need **Resolution LIVE**, not headline scrape |
| **Gate cut** | Headline ≠ Credit Event. DENY until LIVE Resolution + digest bind | Pitch: “agents that detect defaults are worthless next to refuse-until-DC” |

**Outbound desk shape:** ISDA / DC secretary contacts; sell-side CDS documentation or credit-derivatives middle office at DC member firms; CCP CDS risk. Not “fintech AI” BD.

---

### Z2 — CLS FX settlement (matched ≠ settled PvP)

| Role | Who | Notes |
|---|---|---|
| **Operator** | **CLS Bank International** (Edge Act corp., NY) | CLSSettlement PvP service |
| **Parent** | CLS Group Holdings AG (Swiss); CLS UK Intermediate Holdings | Shareholder club ≈ settlement members |
| **Oversight** | Fed (lead) + **CLS Oversight Committee** (central banks of eligible currencies) | Not a startup settlement network |
| **Club** | ~75+ **settlement members**; ~38k+ third-party users via members | Third parties submit through a member; member funds pay-in |
| **Finality** | Settlement of instructions + associated payments on CLS books = **final & irrevocable** | Herstatt-risk religion |
| **Scale** | ~USD 8T average day; 18 currencies | |
| **Outsider who cares** | Settlement-member **FX settlement ops / nostro / liquidity**; third-party bank ops who only see member rejects | They fetch settle/reject proof, not trade blotter |
| **Gate cut** | Matched trade ≠ admitted/settled PvP. DENY on unmatched / risk-test / pay-in shortage / suspended | Pitch: adjacent to FedNow but different priesthood |

**Outbound desk shape:** CLS relationship managers; settlement-member FX settlement operations (not the algo trading desk). Ask who owns **instruction admit / pay-in fail** tickets.

---

### Z3 — IANA root-zone change (intent ≠ write)

| Role | Who | Notes |
|---|---|---|
| **Root Zone Manager / IANA Naming** | **PTI** (Public Technical Identifiers), ICANN affiliate | Accepts & validates TLD manager change requests |
| **Root Zone Maintainer** | **Verisign** | Implements validated changes; generates/signs/distributes root zone |
| **Requestors** | TLD managers (ccTLD / gTLD operators) via RZMS | Authorizers must confirm; tech checks can fail closed |
| **Distribution** | 13 root server operator orgs | Consume the maintained zone — not the change mouth |
| **Public process** | [iana.org/help/root-zone-process](https://www.iana.org/help/root-zone-process) | Pre-review → tech test → contact confirm → manual review → implement |
| **Outsider who cares** | TLD technical contacts; DNSSEC ops; security researchers; registry compliance | Stranger receipt = change-request id / DENY reason |
| **Gate cut** | Operator intent ≠ root-zone write. Tech-check / authorizer NACK ⇒ DENY | Pitch: civilization-scale write, not DNS monitoring SaaS |

**Outbound desk shape:** PTI/IANA naming ops; large registry technical policy; Verisign root-maintainer liaison. Not “DNS product” AEs.

---

### S1 — Bank send / FedNow / RTP (grant ≠ push)

| Role | Who | Notes |
|---|---|---|
| **Rail — Fed** | **Federal Reserve FedNow Service** | Settles in FI master accounts; Operating Circular 8; service providers as agents |
| **Rail — private** | **The Clearing House RTP®** | Prefunded model; large-bank consortium ownership |
| **Participant** | Insured depository FI (FedNow participant / RTP participant) | Owns customer push decision |
| **Connectivity agents** | Core processors, payment hubs, aggregators (Temenos-class, etc.) | Send/receive messages as authorized service provider — still not the mandate mouth |
| **Agent commerce ocean** | Visa Intelligent Commerce + TAP; Mastercard-class | Recognition / token — **not** bank push clearance |
| **Payment fences** | Fidacy, IntentFence, AgentPay-class | Grants/receipts for *pay* — weld adjacent, not enemies |
| **Outsider who cares** | Bank **payments ops / fraud / agent-channel risk**; FI service-provider integration | Fetch clearance (+ linked threat) when agent requests push |
| **Gate cut** | LIVE mandate+grant bound to digest before `bank_send` / `fednow_push` / `rtp_push`. No grant ⇒ DENY + stranger clearance | Pitch under Fidacy/Visa, not against |

**Outbound desk shape:** FI real-time payments product + ops; core/payment-hub partner who implements FedNow/RTP send; risk that owns **agent-initiated credit push**. One lead > ten abstract “bank” emails.

---

### S3 — Performative seal / EFSP transmit (check ≠ file)

| Role | Who | Notes |
|---|---|---|
| **Federal file mouth** | **CM/ECF** (U.S. Courts) via PACER-authorized filers | Docket remade on accept — sanctions often *after* file |
| **State EFM** | Court **Electronic Filing Manager** (often **Tyler Odyssey** eFile & Serve) | Court-side accept/reject |
| **EFSP** | **Electronic Filing Service Provider** (certified intermediaries) | Assembles/transmits to EFM; many states require EFSP |
| **Firm side** | AmLaw DMS / litigation support / GC risk | Soft if lawyers can bypass the gate |
| **Crowded check layer** | Westlaw Quick Check, Lexis Brief Analysis, PelAIkan | Citation check ≠ transmit block |
| **Demand proof** | Charlotin AI hallucination cases corpus (~2k decisions) | Pain is post-file |
| **Outsider who cares** | Court e-file admin; EFSP compliance; firm risk / GC | Stranger seal + transmit receipt |
| **Gate cut** | No LIVE seal ⇒ cannot `transmit_efsp`. Fake cite ⇒ seal DENY ⇒ file DENY | Pitch: **file mouth open**; checkers are not competitors |

**Outbound desk shape:** One EFSP product/compliance lead **or** one court e-file / EFM contact **or** AmLaw litigation risk / IT who can hard-gate submit. Edge pass still ranks S3 as strongest institutional wedge.

---

## Who fetches the stranger receipt (summary)

| Mouth | Priesthood commit | Outsider fetcher | Cold-open? |
|---|---|---|---|
| **S1** | FedNow/RTP push | Bank payments ops / agent-channel risk | **Yes — first door** |
| **S3** | EFSP/CM-ECF transmit | Court e-file admin / EFSP / firm GC risk | **Yes — first door** |
| Z1 | DC Resolution publish | CDS MO / CCP risk / eligible market participant ops | No — ammo / warm intro only |
| Z2 | CLS PvP settle | Settlement-member FX settlement ops | No — ammo / warm intro only |
| Z3 | Root-zone write | TLD tech contact / registry compliance | No — ammo / warm intro only |

Gate is not the club. Gate is the **fetchable refusal surface** the club’s outsiders hit.

Role discipline (where outreach dies): talk to **CDS MO**, not “fintech AI”; **CLS settlement ops**, not the algo desk; **EFSP compliance / firm risk who can block transmit**, not “legal tech BD”; **payments ops who own agent push**, not “digital innovation.”

---

## What this note does / does not authorize

**Do:** Use for outbound scripts, desk targeting, S1/S3-first demo order.  
**Do not:** Build Z11+, pretend production DC/CLS/IANA/FedNow/EFSP, start museum S11–S17, conflate TAP recognition with clearance, cold-call Z1–Z3 as the first conversation.

**Next after this note:** human picks **one S1 or S3 desk** and runs the stranger-GET demo — **or stops**. Z ammo stays in the briefcase. More shippable wedges (S7 / escrow / credentialed-publish) live in `INSTITUTIONAL_WEDGES_SHIPPABLE_2026-09-15.md` — build only if outbound needs them or a named partner asks.

---

## Pointers

| Doc | Role |
|---|---|
| `EDGE_PASS_2026-09-15.md` | Crowding teardown |
| `SHOCK_TIER_HUNT_2026-09-15.md` | Stopping rule |
| `DESKTOP_ORDERS_PASTE_2026-09-15.md` | Current desktop posture |
| `sims/README.md` | Receipt classes + honesty |
| `sims/verify_http.py` | Lab stranger GET |
