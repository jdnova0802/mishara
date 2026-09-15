# Desktop Cursor pastes — S-tier concrescence builds

**Date:** 2026-09-15  
**Law:** logos-before-actus (`FORMULA_CONCRESCENCE_S_TIER_2026-09-15.md`)  
**Rule:** All sims. `their_production: false`. Fail-closed. Stranger-verifiable receipt on every DENY/ALLOW. No dashboard theater. No real money, court, KYC vendor, dead person, or biometric production weld.

**→ Full run order (copy-paste into Cursor):** `DESKTOP_ORDERS_PASTE_2026-09-15.md`  
**→ Shock Z1–Z10 ship paste:** `SHOCK_TIER_SHIP_PASTE_2026-09-15.md`  
**→ Stopping rule (no Z11 collection):** `SHOCK_TIER_HUNT_2026-09-15.md`  
**→ Outbound research (receipt + counterparties):** `OUTBOUND_RESEARCH_RECEIPT_COUNTERPARTY_2026-09-15.md`  
**→ Next intelligences + Claude paste:** `INTELLIGENCE_PASS_2026-09-15.md`

---

## DESKTOP — CURRENT POSTURE (cloud already shipped)

Cloud proved lab spines + P0/tier-2 welds + shock Z1–Z10. Desktop does **not** re-build.

```bash
python3 -m gate.sims.prove_all
```

| Priority | Mouth / layer | Status | Desktop next |
|---|---|---|---|
| **Done** | S1 bank-send + HTTP verify | Cloud green | Outbound / deepen only if partner |
| **Done** | S3 EFSP block-transmit + HTTP | Cloud green | Outbound / deepen only if partner |
| **Done** | S9 + S1/S8 wire | Cloud green | Leave |
| **Done** | S6/S7 weld-shape | Cloud green | Leave |
| **Done** | Shock Z1–Z8 | Cloud green | Pitch ammo (Z1–Z4), not more code |
| **Done** | Z9/Z10 | Generality demo only | Do not productize; no Z11 |
| **Now** | Human outbound OR stop | — | **First door: S1 or S3** desk + stranger-GET; Z1–Z3 ammo only |

**Do not start:** S2/S4/S5, museum S11–S17, Z11+, dashboards.

Paste **DESKTOP_ORDERS_PASTE** for the full current order. Older S1/S2/S3 paste blocks below are historical scaffold notes — cores already exist.

---

## Shared spine (every build)

```
CONSEQUENTIAL_ACTION proposed
  → require LIVE mandate bound to action_digest
  → missing / stale / mismatch / over-scope ⇒ DENY + receipt_url
  → valid ⇒ ALLOW + receipt_url linking mandate ↔ digest ↔ result
  → uncertainty ⇒ DENY
  → their_production: false always in this lab
```

Receipt must be fetchable by a stranger (public verify route or signed JSON) without trusting the actor’s admin UI.

---

## PASTE S1 — Actus Fence (agent tool/pay)

```
Build Actus Fence sim — logos-before-actus for AI agents.

Goal: prove DENY when an agent tries a consequential tool without a LIVE digest-bound grant.

Scope (lab only):
- In-process or local HTTP sim. No real wallets, banks, or MCP hosts in production.
- their_production: false on every response.

Model:
- Mandate: { mandate_id, scope[], max_amount_cents?, payee_allowlist?, expires_at, revoked:bool }
- Action: { action_type: "pay"|"delete"|"email_send"|"prod_mutate", digest: sha256(canonical_payload), payload }
- Grant: short-lived token bound to exact digest (TTL ≤ 5 min)
- Decision: ALLOW | DENY with reason_code

Hard DENY when any:
1. no LIVE mandate
2. mandate expired or revoked
3. action_type not in mandate.scope
4. digest ≠ grant.digest (or no grant)
5. payee not allowlisted / amount over cap (for pay)
6. uncertainty / malformed → DENY

ALLOW only with valid grant matching digest; emit receipt.

API sketch:
- POST /v1/actus/mandates
- POST /v1/actus/grants  (binds digest)
- POST /v1/actus/execute
- GET  /v1/actus/receipts/{id}  (stranger-verifiable)

Prove scripts:
1. pay without mandate → DENY
2. pay with mandate but no grant → DENY
3. grant for digest A, execute digest B → DENY
4. valid grant → ALLOW + receipt links mandate↔digest↔result
5. expired grant → DENY

Do not build a chat UI. Mouth only.
```

---

## PASTE S2 — Presence Threshold (enrollment)

```
Build Presence Threshold sim — appearance ≠ person at enrollment mouth.

Goal: prove DENY on account-create when capture-integrity / LIVE enroll logos fail.

Scope (lab only):
- Fake capture signals. No real face vendor. No production KYC.
- their_production: false.

Model:
- EnrollAttempt: { applicant_id, doc_match_score, liveness_score, capture_integrity: "ok"|"inject_suspect"|"unknown", risk_flags[] }
- Policy: LIVE enroll requires capture_integrity=="ok" AND liveness_score≥threshold AND no critical risk_flags
- Decision at mouth: account_create ALLOW | DENY

Hard DENY when any:
1. capture_integrity != "ok"
2. liveness below threshold
3. doc_match_score below threshold
4. risk_flags includes "deepfake_suspect" | "injection"
5. policy LIVE missing / unknown signals → DENY (fail-closed)

ALLOW only when all signals pass; emit enroll receipt (what was checked, scores banded, decision).

API sketch:
- POST /v1/presence/enroll
- GET  /v1/presence/receipts/{id}

Prove scripts:
1. inject_suspect → DENY + receipt
2. unknown integrity → DENY
3. clean scores → ALLOW + receipt
4. stranger can verify receipt without admin login

Do not build a full IDV suite. Enrollment mouth only.
```

---

## PASTE S3 — Performative Seal (e-file)

```
Build Performative Seal sim — draft ≠ filed speech-act.

Goal: prove DENY on file-submit when citations are ungrounded / hallucinated.

Scope (lab only):
- Local citation store + planted fake cites. No CM/ECF production.
- their_production: false.

Model:
- Brief: { brief_id, citations: [{ cite_key, quoted_text? }] }
- GroundingStore: known real cases → holdings/quotes (fixture JSON)
- Seal: PASS only if every citation resolves and optional quotes match
- FileSubmit: ALLOW | DENY

Hard DENY when any:
1. citation not in GroundingStore
2. quoted_text does not match store (hallucinated quote)
3. seal skipped / LIVE seal missing
4. uncertainty → DENY

ALLOW only with seal_id bound to brief hash; filing receipt stranger-verifiable.

API sketch:
- POST /v1/performative/briefs
- POST /v1/performative/seal
- POST /v1/performative/file
- GET  /v1/performative/receipts/{id}

Prove scripts:
1. brief with planted fake case → seal DENY → file DENY
2. real cite, fake quote → DENY
3. all grounded → seal ALLOW → file ALLOW + receipt
4. file without seal → DENY

Do not build a research chatbot. Submit mouth only.
```

---

## PASTE S4 — Afterlife Mandate (speak-as-dead)

```
Build Afterlife Mandate sim — memory ≠ license to speak-as.

Goal: prove DENY when serving a posthumous persona without LIVE pre-mortem mandate.

Scope (lab only):
- Synthetic personas + mandate objects. No real decedent data. No grief product launch.
- their_production: false. Default DENY.

Model:
- Mandate: { subject_id, scope: ["private_family_chat"|"commercial_voice"|"public_social"], expires_at, revoked, estate_countersign?: bool }
- ServeRequest: { subject_id, channel, requester_role }
- Decision: ALLOW | DENY

Hard DENY when any:
1. no mandate for subject
2. mandate expired or revoked
3. channel not in scope (e.g. public_social when only private_family_chat)
4. commercial_voice without required estate_countersign when policy says so
5. uncertainty → DENY

ALLOW emits mandate receipt (scope, expiry, decision). Revoke immediately blocks serve.

API sketch:
- POST /v1/afterlife/mandates
- POST /v1/afterlife/mandates/{id}/revoke
- POST /v1/afterlife/serve
- GET  /v1/afterlife/receipts/{id}

Prove scripts:
1. serve with no mandate → DENY
2. serve public_social with private-only mandate → DENY
3. valid private_family_chat → ALLOW + receipt
4. revoke then serve → DENY

Do not generate realistic voice/video of real people. Text stubs only.
```

---

## PASTE S5 — Body Archive Gate (biometric enroll)

```
Build Body Archive Gate sim — scan ≠ eternal key.

Goal: prove DENY on biometric template enroll without LIVE purpose-bound consent; prove destroy receipt.

Scope (lab only):
- Fake templates (random vectors). No real faces/fingerprints. No child/school vertical.
- their_production: false.

Model:
- ConsentEpoch: { subject_id, purpose, expires_at, revoked }
- EnrollRequest: { subject_id, purpose, template_stub }
- DestroyRequest: { enrollment_id }
- Decision: ALLOW | DENY

Hard DENY enroll when any:
1. no LIVE consent for that exact purpose
2. purpose mismatch (enroll "payments" with consent "door_access")
3. consent expired/revoked
4. uncertainty → DENY

ALLOW enroll → enrollment_id + receipt.
Destroy → stranger-verifiable destroy receipt (enrollment gone / marked destroyed).
Purpose change requires new consent epoch (old enroll DENY until re-consent).

API sketch:
- POST /v1/body/consent
- POST /v1/body/enroll
- POST /v1/body/destroy
- GET  /v1/body/receipts/{id}

Prove scripts:
1. enroll without consent → DENY
2. purpose mismatch → DENY
3. valid consent → ALLOW
4. destroy → receipt proves destroyed; re-auth with old id fails
5. no child/school flows anywhere

Do not build a matcher competing with biometric vendors. Consent/enroll/destroy mouth only.
```

---

## Run order on desktop

| Order | Paste | Prove that matters |
|---|---|---|
| 1 | **S1** | Digest-bound grant; wrong digest DENY |
| 2 | **S3** | Fake cite cannot file |
| 3 | **S2** | inject_suspect cannot enroll |
| 4 | **S4** | No mandate cannot speak-as |
| 5 | **S5** | No purpose consent cannot enroll; destroy receipt |

Shared libraries OK (receipt store, LIVE clock, digest helper). Do not merge into one mega-dashboard.

---

## Done means

For each S-tier:

- [ ] At least 3 automated DENY proves
- [ ] 1 ALLOW path with receipt
- [ ] `GET .../receipts/{id}` works without actor credentials (or with public verify token)
- [ ] `their_production: false` asserted in responses or config
- [ ] README blurb: lab only; not production weld

---

## Out of scope (do not build in these pastes)

- Real FedNow/bank rails
- Real CM/ECF submit
- Real KYC vendor integration
- Real human likeness / grief UX
- Real biometric capture hardware
- Agent governance dashboards, kill-switch theater, permit-receipt patent clones as the product
