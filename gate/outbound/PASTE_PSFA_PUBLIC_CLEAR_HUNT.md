# PASTE — PSFA / public-disbursement Clear hunt (NAO £55–81bn)

**26 Sep 2026.** Hungry follow-on from `PASTE_GDP_ROI_OPEN_HUNT.md` #3.  
Same bar: primary for a Gate-shaped mouth, or empty. **Do not invent a public-sector SKU.**

---

## Verdict (plain)

**Empty for a mandatory third-party Clear webhook on public money.**

The **loss stack is real** (NAO £55–81bn). The **prevention-before-payment doctrine is real** (Managing Public Money, GovS 013/015, PSFA mandate, COVID grant pre-payment checks). The **new statute is real** (Public Authorities (Fraud, Error and Recovery) Act 2025).

None of that creates a DSP-shaped insertion point where every public disbursement must hit an external Clear API and mint a stranger-verifiable receipt. PSFA / PAFER / DWP own the write-path. Occupied tools already do bank/company pre-checks.

**Do not ship a “PSFA mouth” that pretends Gate is the payment gate.**

---

## What is real (cite or silence)

| Fact | Primary |
|------|---------|
| Fraud & error cost taxpayer **£55–81bn** in 2023–24 | NAO *Impact of fraud and error on public funds 2023-24* (PSFA methodology) |
| ~£40bn tax / ~£10bn welfare / £5–31bn other | PAC report citing PSFA/NAO breakdown |
| PSFA mandate: IFIA on major new spend; FRA; preventative controls; quarterly fraud data; Prevention Panel | [PSFA Mandate](https://www.gov.uk/government/publications/public-sector-fraud-authority-mandate/public-sector-fraud-authority-mandate-html) |
| Departments **must** follow Functional Standard + Managing Public Money on fraud response | Mandate §§44–46 |
| **PAFER Act 2025** s.1 core functions (in force 1 Apr 2026 via SI 2026/371): **(a) investigate** suspected fraud, **(b) recover**, **(c) enforce**, **(d) support** public authorities on prevention | [ukpga/2025/28 s.1](https://www.legislation.gov.uk/ukpga/2025/28/section/1) |
| Statutory PSFA body / function transfer still **prospective** (s.73 / Sch.2) | legislation.gov.uk |
| Recovery DDOs / DEOs — regulations 2026 | SI 2026/668 |
| Grants: every scheme needs proportionate FRA + due diligence (GovS 015) | [GovS 015 Risk/Controls](https://www.gov.uk/government/publications/government-functional-standard-govs-015-grants/7-risk-controls-and-assurance-html) |
| COVID grant schemes: **explicit pre-payment checks** (company + bank) **before any payment**; retain evidence; Spotlight / NFI / Experian BAV / equiv. | e.g. Omicron Hospitality & Leisure Grant LA guidance §§58–66 |
| DWP Eligibility Verification Notices: banks return matches; **no automatic suspension**; trained decision-maker + hardship rules | PAFER DWP Codes of Practice / gov response |

---

## What is **not** found (bar fails)

| Temptation | Reality |
|------------|---------|
| “PAFER requires Gate Clear before BACS” | s.1 is investigate / recover / enforce / **support** — not a payment authorization webhook |
| “PSFA is a Stripe Issuing-style auth timeout” | Mandate is IFIA/FRA/analytics/standards — tailored services, not one-size realtime Clear |
| “DWP EVN = auto NEVER on benefit” | Explicitly **not** automatic; human entitlement decision |
| “Third party must file prevented-fraud pack to PSFA within N days” | No DSP-analogue clock for external vendors |
| Soft Power / GDP sector for “public Clear” | Loss avoidance, not Gate GVA |

---

## Occupied (don’t rebuild)

| Tool / actor | Role |
|--------------|------|
| **Spotlight** (Cabinet Office Grants) | Pre-award digital due diligence |
| **NFI** + Experian bank-account verification | Pre/post payment company + account checks |
| Companies House / Cifas / NAFN / TransUnion / Equifax | Pre-payment check menu in grant guidance |
| **PSFA** Network Analytics Platform / data pilots | Find + prevent inside government |
| DWP / HMRC RTI + EVN | Eligibility data inside welfare/tax |
| Accounting Officers under **Managing Public Money** | Decide CoP-type / payee validation — not outsourced to Gate |

Rebuilding Spotlight/NFI as “Gate Clear” = same mistake as rebuilding Stripe MCC.

---

## Closest Gate-shaped wedge (honest, optional, weak vs DSP)

| DSP (shipped) | Public disbursement (tonight) |
|---------------|-------------------------------|
| Hard cite: 28 CFR § 202.1104 | Soft stack: MPM + GovS 015 + scheme pre-pay guidance + PSFA prevention language |
| Clock: 14-day NSD report | **No external filing clock** |
| Gate classifies + packs; never files | Gate could classify + pack **pre-payment check completeness**; **never pays** |
| Clear regulatory face | Occupied by Spotlight/NFI; AO decision |

If ever built (only as advisory theory-floor mouth, not “£55bn product”):

- **Input:** scheme_id, amount, payee, account fingerprint, flags: `company_check`, `bank_check`, `fra_documented`, `spotlight_or_equiv`, `ao_approved`
- **Words:** `CLEAR` (required checks present) \| `HOLD` (incomplete) \| `NOT THIS` (not a pre-pay scheme face)
- **claim_scope:** presented flags only — not a scan of government ledgers
- **write_state:** clearance advisory; `write_executed=false`; BACS/FPS untouched
- **Never** claim PSFA endorsement or prevented-loss £ against NAO totals

That is **aspirational productization of existing standards**, not a found mandatory mouth. Prefer leave unbuilt until a department actually asks for an evidence-pack API.

---

## Build implication

| Do | Don’t |
|----|-------|
| Keep Issuing / FS-PBS as the GDP-mass attach | Ship “PSFA Clear” SKU |
| Cite NAO £55–81bn as **loss-ROI context** when pitching prevention doctrine | Claim Gate recovers or prevents that stack |
| If a public body RFPs pre-pay evidence packs, then consider advisory mouth | Rebuild Spotlight / NFI / EVN |
| Watch PAFER commencement + PSFA Sch.2 regs for real APIs | Pretend s.1(d) “support” = webhook auth |

---

## One-liner

**Hungry hunt: loss real, doctrine real, statute real — mandatory Gate Clear on public disbursement not found; PAFER investigates/recovers/supports, Spotlight/NFI already pre-check; do not invent the mouth.**
