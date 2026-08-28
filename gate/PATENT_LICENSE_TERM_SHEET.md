# Field-Limited Patent License — Term Sheet Skeleton

**Status:** draft skeleton for counsel review — **not legal advice**, not a binding offer.  
**Licensor (fill):** Nisaba LLC · Wyoming · `[ADDRESS]`  
**Patent:** US Provisional **64/124,027** (convert to non-provisional before signature — see §2)  
**Product spec:** `gate-commit-auth-v1` · `/.well-known/commit-auth.json`  
**Related:** `COMMIT_AUTH.md` · `license_fuse.py` · `override_impossibility.py` · `licensing_pack.py` · `/.well-known/licensing-pack.json`

---

## Counsel note (read first)

This skeleton maps **patent lane** claims from `COMMIT_AUTH.md`:

| Claim family | Patent lane | Licensed in default template? |
|--------------|-------------|-------------------------------|
| **Epoch lock** — non-resurrecting HALT until verified CHARGE; `not_admin_charge` | **Primary** | Yes |
| **Commit-time authorization** — single-use redeem at bind; LIVE hop ≠ bind grant | **Secondary** | Yes |
| Insurance bind surface / NAIC / PAS product names | GTM foothill only | **No** (unless Field A carved into Exhibit B) |
| BYOK twin / dual-control | Supporting | Optional exhibit |
| 88 invention module names / civilizational + IP catalog positioning | Positioning | **No** (112 modules — names not licensed) |

**Do not** grant trademark, copyright, or **may authority** (CHARGE / epoch resurrection) in a patent license. Those stay in separate weld / operator agreements.

---

## 1. Parties

| Role | Entity | Notice |
|------|--------|--------|
| **Licensor** | Nisaba LLC | Patent owner / exclusive licensee of record |
| **Licensee** | `[LEGAL NAME]` | `[JURISDICTION]` |
| **Affiliates** | Included / excluded | `[DEFINE — default: controlled subsidiaries only with written notice]` |

---

## 2. Licensed patents

**2.1 Covered applications**

- US Provisional Application No. **64/124,027**, filed `[PROVISIONAL FILING DATE]`, title `[AS FILED]`
- Continuations, divisionals, and non-provisionals claiming priority to 64/124,027
- Any US patents issuing therefrom (**Licensed Patents**)

**2.2 Condition precedent**

Licensee acknowledges signature is contingent on Licensor filing a **non-provisional** application before `[NON-PROVISIONAL DEADLINE]` (or substitute date in amendment). If not filed, Licensee may terminate without penalty or renegotiate for provisional-only know-how license.

**2.3 Licensed claims (Exhibit A — claim chart)**

Counsel to attach claim chart limited to:

1. **Epoch lock** — persisting HALT/BLOCK state for a job/epoch identifier until a defined non-admin resurrection event (verified CHARGE-class authority), excluding operator-console resurrect and soft-approval bypass.
2. **Commit-time single-use authorization** — server-side atomic consume of bind authorization at commit time; attestation/signature alone insufficient to complete irreversible write.

Excludes: generic TTL tokens, reusable JWT/Biscuit delegation, FRE-only receipts, pre-execution proof without epoch lock.

---

## 3. Licensed field (Exhibit B — field definition)

**Canonical spec:** `/.well-known/licensed-field.json` · `gate-licensed-field-v1`

**3.0 Default (template)**

Unless Exhibit B amendment narrows further, the default **Licensed Field** is **Option B (platform)** — irreversible **delegated-write** control planes across verticals. Insurance PAS/MGA (Option A) is a **field carve-in**, not the default grant. PAS/MGA is the current **GTM foothill** only (`STRONGEST_START` vertical lock).

**3.1 Licensed Field (grant)**

Use of Licensed Patents **only** within:

> **Default — Option B (platform):** irreversible **delegated write** control planes where a third party can verify epoch HALT + stranger-grade receipt without admin resurrect — including without limitation: agent tool commits, payout/withdraw clearance, enterprise org-root spend, defense release, hiring decision stick, and (when carved in) insurance bind paths.
>
> **Option A (insurance carve-in):** policy administration systems (PAS) **bind-and-issue** and **renewal batch bind** for P&C or MGA carriers in `[LIST STATES / COUNTRIES]` — **subset of Option B**
>
> **Option C (field-limited OEM):** `[LICENSEE PRODUCT LINE]` embedded in `[CUSTOMER SEGMENT]` only

**Audience plates** (`/for/<slug>` — developers, agents, operators, carriers, defense, etc.) are **GTM surfaces**, not separate patent fields unless named in Exhibit B.

**3.2 Excluded fields (reservation of rights)**

Licensor reserves all rights outside Licensed Field, including without limitation:

- Consumer payments, card networks, general identity/IAM unrelated to irreversible commit
- Military / C2 / nuclear / weapons systems (Tier Z)
- `[LICENSEE COMPETITOR PRODUCT LINES]`
- **May authority resale** — Licensee may not sell CHARGE-equivalent resurrection or operator override as a SKU

**3.3 Non-compete scope**

Field-limited **only** — no broad industry non-compete. Licensor may license others in non-overlapping fields.

---

## 4. Grant type (pick tier)

### Tier 1 — Architecture / conformance license (**no may**)

| Grant | Scope |
|-------|--------|
| **Right** | Implement methods **substantially conforming** to Exhibit C (Gate Bind Commit Profile) |
| **No grant** | Velaru CHARGE keys, Licensor hosted redeem, trademark, source code (unless Exhibit D) |
| **Conformance** | Pass `[ANNUAL / ON-DEMAND]` conformance tests; publish `/.well-known/commit-auth.json` subset |

**Use when:** SI, PAS vendor, cloud runtime — they host; you keep may.

### Tier 2 — Implementation + hosted redeem (optional)

| Grant | Scope |
|-------|--------|
| **Right** | Tier 1 + `[API / worker / SDK]` binary or SaaS embed |
| **No grant** | White-label Velaru; sublicense without §8 cascade |

**Use when:** OEM pays platform fee + per-event royalty.

### Tier 3 — Exclusive in Licensed Field (premium)

| Element | Typical terms |
|---------|----------------|
| **Exclusivity** | Licensed Field only, for `[TERM]` |
| **Minimums** | 2–3× non-exclusive minimums |
| **Performance** | Lose exclusivity if `[UNIT THRESHOLD]` not met in rolling 12 mo |

---

## 5. No-may carve-out (non-negotiable default)

Licensee **shall not**:

1. Implement **admin resurrect**, **console override**, or **UW-approve-without-CHARGE** paths that lift epoch lock on the bind/write path (see `override_impossibility.py` forged paths).
2. Represent conformance while operating **fail-open** redeem (must match `redeem.fail_closed: true` in `gate-spend-protocol-v1`).
3. Use Licensor marks except as permitted in Exhibit E (trademark license separate).

**May authority** (epoch resurrection, license parent LIVE/DEAD) remains **Velaru / Licensor operator agreement** unless separate **Operator / Weld** contract signed.

---

## 6. License fuse cascade (sublicense — Exhibit F)

Pattern from `license_fuse.py` + `epoch_lock_patent_asset`:

| Rule | Term |
|------|------|
| **Parent** | Licensee is **Parent Licensee** under this agreement |
| **Sublicense** | Permitted only to end customers **in Licensed Field** under written sublicense |
| **Cascade** | Sublicense **terminates automatically** if Parent Licensee’s license terminates or Parent is not **LIVE** (paid current on annual minimum + not in material breach) |
| **No ghost licensing** | Sublicense may not grant rights to expired copyright/patent scope or outside Licensed Field |
| **Audit pass-through** | Sublicense must include audit and reporting obligations **no weaker** than §9 |

Licensor may publish **Parent License ID** in `[REGISTRY URL]` for stranger verification.

---

## 7. Fees (Exhibit G — royalty schedule)

**Choose structure — dual stream (ARM analog):**

### 7.1 Upfront / access

| Fee | Default range (negotiate) |
|-----|---------------------------|
| **Conformance access fee** (one-time) | `$[50,000] – [250,000]` |
| **Annual platform fee** | `$[25,000] – [150,000]/yr` |

### 7.2 Per-event royalty (recurring)

| Event | Definition | Rate (pick one) |
|-------|------------|-----------------|
| **Qualified irreversible commit (QIC)** | Server-side atomic consume + irreversible write in Licensed Field | `$[0.05] – [2.00] per QIC` |
| **OR % of ASP analog** | `[X] bps of premium bound` or `[Y]% of Licensee product ASP on shipped units containing method` | Qualcomm-style — cap at FRAND if §10 invoked |

**Minimum annual royalty (MAR):** `$[50,000] – [500,000]/yr`, creditable against per-event royalties.

**True-up:** Quarterly report + payment within `[30]` days.

### 7.3 Escalators

| Trigger | Effect |
|---------|--------|
| Volume > `[N]` QIC/yr | Step-down rate tier or renegotiation |
| Armv9-class **major version** conformance breaking change | One-time re-cert fee |
| Exclusivity | MAR × `[2–3]` |

---

## 8. Reporting

Licensee shall deliver **within 30 days after quarter end**:

1. QIC count by product line and geography  
2. Gross revenue attributable to Licensed Field products (if bps model)  
3. List of active sublicenses (Parent License IDs)  
4. Conformance attestation signed by `[OFFICER TITLE]`  
5. Material security incidents affecting epoch lock or redeem path (48 hr notice)

**Stranger-grade metric:** optional publication of aggregate QIC + HALT depth band (no customer PII) at `[URL]` for diligence.

---

## 9. Audit and clawback (royalty_audit_clawback)

| Term | Detail |
|------|--------|
| **Frequency** | Annual; Licensor may request **one extra audit/yr** on 30 days notice |
| **Scope** | Books, logs, QIC counters, sublicense registry |
| **Underpayment** | Pay deficiency + **interest `[1.5%/mo]`** + audit costs if underpayment > `[5]%` |
| **Clawback window** | `[3]` years (or statute max) |
| **Remediation** | Material breach of §5 (no-may) → **immediate terminate** + injunctive relief |

---

## 10. FRAND / standard-essential fallback (optional — Exhibit H)

**If** Licensed Patents are declared **essential** to a `[STANDARD NAME — e.g. IETF Gate Bind Commit Profile]`:

| Element | Term |
|---------|------|
| **FRAND commitment** | License terms remain fair, reasonable, non-discriminatory among similarly situated implementers |
| **Cap** | Per-event royalty capped at `[LOWER OF SCHEDULE OR FRAND RATE]` during essential period |
| **Non-essential reversion** | If claims withdrawn from essential pool, Exhibit G rates apply |

Until essential declaration, **no FRAND obligation** — field-limited commercial license only.

---

## 11. Conformance (Exhibit C — technical schedule)

Minimum implementation requirements for **patent exhaustion defense avoided / branding “Gate Conformant”**:

1. **Epoch lock** persisted per `job_id` (or equivalent) until CHARGE-class event  
2. **Single-use** server redeem; `single_use: true`  
3. **Fail-closed redeem** — outage blocks bind; ticket not consumed on failure  
4. **Override impossibility** — no forged resurrection paths in production build (reference `/.well-known/override-impossibility.json`)  
5. **Stranger verify** — third party can open receipt URL without operator narration  
6. **License fuse** — if sublicensing, parent/child lifecycle enforced  

**Conformance test:** `[TEST SUITE URL / POST /demo/pas/bind-check]` + written attestation.

---

## 12. Term and termination

| Event | Effect |
|-------|--------|
| **Term** | `[3]` years initial; auto-renew `[1]` yr unless `[90]` day notice |
| **Termination for convenience** | Either party on `[180]` days notice after year `[1]` |
| **Termination for cause** | Material breach uncured `[30]` days; immediate for §5 violation |
| **Insolvency** | Licensor may terminate on insolvency filing |
| **Patent invalidity** | If **all** Licensed Patents invalidated, royalty reduces `[50]%` or terminate (negotiate) |

**Survival:** §§5, 7 (accrued), 9, 11 (records), 13, 14, 15.

**Post-termination:** wind-down `[90]` days; no new QIC; pay accrued royalties; destroy/confine non-conforming code per counsel.

---

## 13. IP ownership

| Item | Owner |
|------|-------|
| Licensed Patents | Licensor |
| Licensee improvements | `[LICENSEE]` with **narrow patent license back** to Licensor for `[FIELD]` only |
| Gate marks / Velaru | Licensor — separate TM license |
| Feedback | Licensor may use without royalty; no assignment of Licensee trade secrets |

---

## 14. Indemnity and liability

| Party | Scope |
|-------|--------|
| **Licensee indemnifies** | Third-party claims from Licensee products **outside** conformance or outside Licensed Field |
| **Licensor indemnifies** | Third-party claims that **Licensed Patents** as granted infringe (subject to carve-outs) |
| **Cap** | `[12]` months fees paid; **exclude** willful breach, §5 violations |
| **No consequential** | Standard mutual exclusion (counsel to tune) |

---

## 15. General

| Term | Fill |
|------|------|
| **Governing law** | `[Wyoming / New York]` |
| **Dispute** | `[Arbitration AAA / state courts]` |
| **Assignment** | Licensor may assign with patent; Licensee needs consent |
| **Export / compliance** | Licensee complies with US export and sanctions |
| **Entire agreement** | Supersedes term sheet; definitive agreement controls |

---

## 16. Exhibit checklist

| Exhibit | Contents |
|---------|----------|
| **A** | Claim chart (epoch lock + commit-time only) |
| **B** | Licensed Field + exclusions — `/.well-known/licensed-field.json` (default Option B platform) |
| **C** | Conformance spec (`commit-auth`, spend-protocol, override packet) |
| **D** | Source/SDK deliverables (if Tier 2) |
| **E** | Trademark guidelines (if any) |
| **F** | Sublicense template (license fuse cascade) |
| **G** | Fee schedule (upfront + MAR + per-QIC) — see also `PATENT_LICENSE_EXHIBIT_REDACTED.md` |
| **H** | FRAND letter (if standards path) |
| **I** | Premium / cleared-flow bps schedule — `/.well-known/premium-bps-schedule.json` |
| **J** | Gate Conformant™ mark spec — `/.well-known/gate-conformant-mark-spec.json` |
| **K** | QIC meter definitions — `/.well-known/qic-meter.json` |

**Pack index:** `/.well-known/licensing-pack.json` (canonical entry point)

---

## 17. Negotiation anchors (internal — remove before sending)

| Licensee type | Upfront | MAR | Per QIC | Notes |
|---------------|---------|-----|---------|-------|
| PAS OEM (Guidewire-class) | $150k+ | $250k+ | $0.10–0.50 | Field B platform; audit critical |
| MGA / carrier (single) | $25k | $50k | $0.25–1.00 | Field A insurance; narrow geography |
| SI / distributor | $50k | $75k | rev-share pass-through | Sublicense §8 required |
| Cloud agent runtime | $250k+ | $500k+ | bps on volume | Tier 1 architecture first |

**First deal target:** one **field-limited** paid license → external proof of patent worth before scaling FRAND story.

---

## 18. Stranger verification (optional public schedule)

If parties agree, attach redacted summary at:

`https://gate.velaru.xyz/.well-known/epoch-lock-patent-asset.json`

Fields: `patent_id`, `licensed_field_hash`, `conformance_spec_url`, **no** licensee pricing.

---

*Skeleton v1 · Aug 28, 2026 · Nisaba LLC / Gate · Counsel must review before execution.*
