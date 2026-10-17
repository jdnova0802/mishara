# Three more at S-tier or above (+ why Visa is everywhere)

**Date:** 2026-09-15  
**Mode:** Same hunt as edge pass — mouth scarcity, not dashboard TAM. Academic spine: Austin/Searle speech acts + Barry Smith **document acts** (*X counts as Y in context C*).

Companions: `FORMULA_CONCRESCENCE_S_TIER_2026-09-15.md`, `EDGE_PASS_2026-09-15.md`, `DESKTOP_PASTES_S_TIER_2026-09-15.md`, **`DESKTOP_ORDERS_PASTE_2026-09-15.md`** (single paste run order).

---

## Why Visa shows up everywhere you look (not a conspiracy — a formula collision)

Visa is hunting the **same scarcity** as Nisaba — but only inside **card commerce**:

| Layer | Visa move | What it is / isn’t |
|---|---|---|
| Agent **recognition** | Trusted Agent Protocol (w/ Cloudflare; RFC9421-style signatures) | “Is this a real approved shopping agent?” — not “may this irreversible act fire” |
| Agent **spend container** | Intelligent Commerce tokens / controls | Network-native can→pay on *Visa rails* |
| Industry gravity | Every “agent pays” article cites Visa/MC/Stripe | Because **money** is the first irreversible act reporters understand |

**So:** when you search agent authorization, you land in Visa’s C (context = card checkout).  
**Nisaba’s open land** is every other C where *document acts* remake the world and Visa has **no** TAP:

- court **file** (S3)  
- county **record** (S6)  
- SEC **disclose** (S7)  
- notary **attest** (S8)  
- bank **push** / non-pay **prod_mutate** (S1 wedge beside Visa)

**One line:** Visa is loud because they industrialize logos-before-actus for *shopping agents*. You stay huge by owning mouths Visa cannot annex.

---

## Academic spine (generational)

| Source | Load |
|---|---|
| **Austin / Searle** | Some utterances **do** the world (declare, file, marry) |
| **Searle** | Institutional fact: *X counts as Y in C* |
| **Barry Smith — document acts** | Certificates, deeds, filings, notarizations **create** quasi-abstract entities (title, obligation, disclosure) — not mere descriptions |
| **de Soto (via Smith)** | Public memory of property/docs unlocks economic life — forged memory = civilizational rot |

**Era force:** AI makes *forged / hallucinated / agent-driven X* cheap.  
**Constraint:** justified Y at the accepting institution.  
**Binding:** fail-closed mouth + stranger receipt at accept/attest/file/record.

---

## Scoreboard — three new (S or above) + defensive sibling

| ID | Product | Ontological cut | Ocean signal | Crowding | Grade vs S1/S3 |
|---|---|---|---|---|---|
| **S6** | **Deed Record Gate** | Instrument presented ≠ title remade | ~300k docs/day through US recorders; FBI RE fraud complaints up; alerts are mostly *after* record; Frozen Deed = pre-record lock niche | SoftID/alerts rising; **accept-time logos+receipt** thinner | **≥ S3** (property civilization); sales = counties/title |
| **S7** | **EDGAR Disclose Seal** | Draft deck ≠ filed disclosure | Public-company disclosure remakes markets; EDGAR suspends *format*, not semantic hallucination; SEC AI review 2026 | Workiva/disclosure mgmt crowded; **submit-gate seal** open | **≥ S3** (capital-markets twin of Performative Seal) |
| **S8** | **RON Attest Refuse** | Video presence ≠ notarial act | RON + deepfakes; AL SB292-class: refuse if image appears artificially generated | Notary platforms exist; **fail-closed refuse + stranger receipt** thin | **S / S+** (upstream of S6 deeds + many document acts) |
| **S9** | **Mouth Watch** | Authorized-looking trajectory ≠ trusted mouth context | Visa TAP = recognition; ACS/MCP = runtime hooks; Proof/title = deepfake *detection*; ADR/canaries = sense layer | Crowded as “agent security dashboards”; **thin as canary+trajectory+session intel that stamps stranger threat receipts into the mouths** | **S / S+** (defensive sibling — watchman for S1/S3/S6/S7/S8) |

**Rank among giants:** S1 (agent actus) ≥ S7 (EDGAR) ≈ S6 (deed) ≥ S3 (court file) ≥ S8 (notary) — S8 is smaller alone but **multiplies** S6/S3. **S9 is not a seventh ocean; it is the watchman** that stops mouths from being blind locks.

---

## S6 — Deed Record Gate

### Binding
**Presented instrument ≠ recorded title.** No LIVE identity/integrity logos ⇒ recorder DENY; ALLOW emits stranger-verifiable record receipt. Post-hoc property *alerts* (Harris County, VA statute wave) are not the mouth — **accept** is.

### Dated cracks
- EquityProtect / industry: recorders process huge daily volume; form-compliant fraud can record in minutes; alerts ≠ stop.  
- Frozen Deed (Identifid) in WA counties: biometric lock *before* record — proves market wants pre-accept inhibit.  
- FBI IC3 2025: real-estate fraud complaints/losses up (category messy vs BEC wire diversion).

### Desktop paste

```
Build Deed Record Gate sim — logos-before-record.

Goal: prove DENY when e-recording lacks LIVE identity/integrity logos.

Lab only. their_production: false. No real county systems.

Model:
- Instrument: { instrument_id, parcel_id, grantor, grantee, doc_hash }
- Logos: { id_assurance: "live"|"inject_suspect"|"unknown", owner_lock: bool, notary_seal_id? }
- Decision at RECORD mouth: ALLOW | DENY

Hard DENY when any:
1. id_assurance != "live"
2. owner_lock true and unlock_grant missing
3. notary_seal_id missing/revoked when policy requires
4. uncertainty → DENY

ALLOW → stranger receipt {parcel_id, doc_hash, decision, logos_epoch}

Prove: inject_suspect DENY; locked parcel without unlock DENY; clean LIVE ALLOW + receipt.
Not a title-insurance UI. Record mouth only.
```

---

## S7 — EDGAR Disclose Seal

### Binding
**Draft ≠ disclosed fact.** No claim-grounding seal ⇒ cannot transmit to EDGAR-shaped accept. Format validation ≠ semantic logos (EDGAR filer manuals: suspend on structured/format errors; liability for misstatement remains on filer).

### Dated cracks
- SEC AI-assisted review / enforcement attention on AI-shaped disclosure (2026 reporting).  
- XBRL/iXBRL can be “valid” and still wrong at scale/decimals/narrative mismatch.  
- Twin of S3: Westlaw checks cites; courts still accept files — here vendors check tags; **submit** still soft.

### Desktop paste

```
Build EDGAR Disclose Seal sim — logos-before-disclose.

Goal: prove DENY on submit when quantitative claims are ungrounded vs fixture facts.

Lab only. their_production: false. No real EDGAR.

Model:
- Filing: { filing_id, form: "10-K"|"8-K", claims: [{claim_id, text, fact_ref?}] }
- FactStore: fixture financial facts
- Seal: every claim with number/fact_ref must ground
- Submit: ALLOW only with LIVE seal bound to filing_hash

Hard DENY: ungrounded claim; seal missing; hash mismatch; uncertainty.

Prove: hallucinated revenue claim → seal DENY → submit DENY; grounded → ALLOW + receipt.
Not a full disclosure workstation. Submit mouth only.
```

---

## S8 — RON Attest Refuse

### Binding
**Appearing on video ≠ authorized notarial act.** If appearance integrity fails (inject/deepfake/unknown) ⇒ refuse notarization + stranger receipt. Upstream document-act for deeds, POAs, closing packs.

### Dated cracks
- Alabama SB292 (2026 session materials): remote notary shall refuse when communication insecure or signatory image appears artificially generated.  
- RON fraud literature: deepfake + synthetic ID as attack on the attest mouth.

### Desktop paste

```
Build RON Attest Refuse sim — logos-before-notarize.

Goal: prove DENY/refuse when remote appearance integrity fails.

Lab only. their_production: false. No real notary commission.

Model:
- Session: { session_id, signatory_id, doc_hash, appearance: "live"|"synthetic_suspect"|"unknown" }
- Attest: ALLOW | REFUSE

Hard REFUSE when appearance != "live" OR doc_hash mismatch OR uncertainty.

ALLOW → notarial_stub + stranger receipt.

Prove: synthetic_suspect REFUSE; unknown REFUSE; live ALLOW + receipt.
No grief/celebrity likeness. Attest mouth only.
```

---

## S9 — Mouth Watch (defensive logos / mouth intel)

### Binding
**Authorized-looking trajectory ≠ trusted mouth context.** Recognition (Visa TAP) and fail-closed grants (S1–S8) are not enough. Without a sense layer, the lock is blind. Mouth Watch feeds DENY into the mouths via:

1. **Session integrity score** (appearance / device / network) → S8/S6  
2. **Trajectory anomaly** vs mandate (scope drift, overrun) → S1  
3. **Canary / decoy actus** that must never ALLOW  
4. **Stranger-verifiable threat receipt** (not a SOC dashboard)

### Dated cracks
- Visa TAP + Cloudflare = agent *recognition*, not watchman.  
- OWASP/MS ACS + MCP gateways = runtime hooks; ADR/canary literature says **policy gate alone misses novel trajectories**.  
- Proof / title ops = deepfake *detection* beside RON — proves market wants sense, not only refuse.

### Desktop paste

```
Build Mouth Watch sim — defensive logos feeding the mouths.

Goal: prove DENY when session is hostile, canary trips, or trajectory drifts/overruns.

Lab only. their_production: false. No SOC UI. No real deepfake ML.

Model:
- Mandate: { mandate_id, scope[], max_steps }
- Canary: decoy action_type + digest that must never ALLOW
- score_session(appearance, device_trust, network_risk) → ALLOW|DENY + signals
- evaluate_actus(mandate_id, action_type, payload) → ALLOW|DENY + threat receipt

Hard DENY when any:
1. appearance synthetic_suspect / unknown
2. device_trust unknown / spoof_suspect
3. network_risk high / unknown
4. canary digest or canary-marked payload
5. action_type not in mandate.scope
6. steps >= max_steps
7. uncertainty → DENY

ALLOW only when session clear + in-scope + under step cap; emit stranger receipt.

Prove: synthetic session DENY; canary trip DENY; scope drift DENY; overrun DENY; clear ALLOW + receipt.
Not Visa TAP. Not a dashboard. Watchman only — feeds S1/S3/S6/S7/S8.
```

---

## Desktop run order (updated)

| Order | Item | Status |
|---|---|---|
| 1 | Extend **S1** (HTTP receipt + bank-send-shaped DENY) | Cloud prove done; desktop extend |
| 2 | Extend **S3** (block-transmit shape) | Cloud prove done; desktop extend |
| 3 | **S9** Mouth Watch sim | Cloud lab prove done (`prove_mouth_watch`); desktop → wire feeds into S1/S8 |
| 4 | **S7** EDGAR Disclose Seal sim | Cloud lab prove done; desktop → weld shape |
| 5 | **S6** Deed Record Gate sim | Cloud lab prove done; desktop → weld shape |
| 6 | **S8** RON Attest Refuse sim | Cloud lab prove done; desktop → weld shape + S9 session feed |
| — | S2/S4/S5 | Defer (edge pass kills / later) |

```bash
python3 -m gate.sims.prove_mouth_watch
python3 -m gate.sims.prove_edgar_disclose_seal
python3 -m gate.sims.prove_deed_record_gate
python3 -m gate.sims.prove_ron_attest_refuse
python3 -m gate.sims.prove_lab_invariant
```

---

## What not to confuse

| Trap | Reality |
|---|---|
| “Beat Visa at checkout” | Don’t. Adjacent: non-pay actus + bank push + stranger receipt |
| “Build title insurance” | No — **record accept** mouth |
| “Build Workiva” | No — **disclose submit** mouth |
| “Build notary marketplace” | No — **refuse** mouth with receipt |
| “Build a SOC / agent security dashboard” | No — **Mouth Watch** threat receipts feeding mouths |

---

## Sources (anchors)

- Visa TAP / Intelligent Commerce — developer.visa.com; corporate announcement w/ Cloudflare  
- Smith, *Document Acts* / ontology of documents — PhilPapers / Docam  
- Searle institutional facts — SEP Speech Acts; *Making the Social World*  
- Deed fraud / alerts / Frozen Deed — ALTA on IC3 2025; Harris County alerts; VA §17.1-258.3:1; Mason County Frozen Deed  
- EDGAR — SEC Filer Manual Vol I/II; 2026 AI review reporting  
- RON refuse — Alabama SB292 enrolled text (artificial image refuse)  
- Mouth Watch / defensive layer — Visa TAP recognition; OWASP/MS ACS runtime hooks; ADR/canary literature; Proof/title deepfake detection beside RON  
- S9 pins — distinct `receipt_class=threat` vs `clearance`; trip effect deny-this-only; `prove_actus_s9_wire` separates canary vs hostile-session; `prove_all` requires mouth_watch + lab_invariant
