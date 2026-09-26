# Theory-floor hardening — three engineering gaps (Claude)

Not new products. Hardening the theoretical floor under mouths already shipped.

---

## 1. SCOPE FIELD ON EVERY NEGATIVE CLAIM

**Fix shipped:** `gate/claim_scope.py` — structured `claim_scope` (boundary, logs, time_window, counterparties, keys_checked, not_global) serialized into a signed envelope (`signed_claim`) or into the prefinality JWT (`scope` claim).

| Mouth | Negative word(s) | Scope boundary | In signed payload? | Finding |
|---|---|---|---|---|
| **Never** | NEVER / SPENT / BROKEN | `gate_redeemed_ticket_spend_map` + IN_FLIGHT probe | Yes — `signed_claim` over claim_scope | **Fixed.** Was prose `not_global` only. |
| **Clear (deny)** | DENIED / NOT DENIED | `gate_deny_registry` | Yes — `signed_claim` | **Fixed.** |
| **Clear (rail)** | REVERSIBLE / FINAL / … | N/A (label, not absence claim) | write_state surfaces window | **Already handled** for liminal window via rail_truth; write_state now explicit. |
| **Seal** | MISSING / BROKEN / UNSIGNED | `gate_bind_events_evidence_log` | Yes when not HOLDS | **Fixed** for absence/degraded. HOLDS already has receipt sig. |
| **Go / Prefinality** | NO_GO / HOLD | `gate_prefinality_evaluate` | Yes — JWT `scope` + `signed_claim` | **Fixed.** |
| **Positive Clear** | NO / HOLD | `gate_mouth_positive_clear` | Yes — via `mouths.evaluate` seal | **Fixed.** |
| **Scenario 3** | DOES NOT MATCH / HOLD | `gate_mouth_scenario_3` | Yes | **Fixed.** |
| **FedNow pre-push** | NEVER / HOLD | `gate_mouth_fednow_prepush` | Yes | **Fixed.** |
| **Nacha False Pretenses** | NEVER / HOLD | `gate_mouth_nacha_false_pretenses` | Yes | **Fixed.** |
| **CL7 handoff** | NEVER / HOLD | `gate_mouth_cl7_handoff` | Yes | **Fixed.** |
| **Issuing / Sink** | NO_GO | inherits prefinality scope | Yes — JWT + mouth passthrough | **Fixed** (via Go path). |

A stranger verifying a Never/DENIED can now read the boundary of the claim without trusting the endpoint name.

---

## 2. WITNESS-COSIGNING CAPACITY ON THE EVIDENCE-HEAD

**Fix shipped:** `evidence_log.signed_tree_head` always emits a `witness` block:

```json
{
  "spec": "gate-evidence-witness-v1",
  "configured": true|false,
  "signed": true|false,
  "distinct_from_gate_key": true|false,
  "public_key_fingerprint": "...",
  "signature": "...",
  "required": false
}
```

Env (air-gap from `GATE_RECEIPT_*`):
- `GATE_WITNESS_PRIVATE_KEY`
- `GATE_WITNESS_PUBLIC_KEY`

Co-signs the same `head_hash` as Gate's primary `head_signature`. No consortium partner required yet — capacity exists. When unconfigured, strangers see `configured: false` rather than an implied single-party forever.

---

## 3. EXPLICIT IN_FLIGHT / PENDING ON EVERY MOUTH

**Module:** `gate/write_state.py` — phases `ABSENT | IN_FLIGHT | SPENT | CLEARANCE | N_A`.

| Mouth | Finding | Action |
|---|---|---|
| **Never / spend map** | **Gap.** Ticket issued but unconsumed was collapsed into binary NEVER (= ABSENT). A Never during IN_FLIGHT is weaker — ticket may still redeem. | **Fixed.** `db.unconsumed_tickets_for_job` + `spend_phase` / `write_state`. Plain text distinguishes IN_FLIGHT Never. |
| **Clear (rail)** | **Already handled.** Rail truth encodes return/dispute windows (`treat_as_reversible_until_…`). | Surfaced as `write_state.phase=IN_FLIGHT` with `already_handled: true`. |
| **Clear (deny)** | Registry presence/absence — no write path to collapse. | Explicit `N_A` + scoped NOT DENIED meaning. |
| **Seal** | Verify-only; no write window. | **Already handled** — `write_state` = N_A seal_verify. |
| **Go / Prefinality** | HOLD is liminal at *decision*; `write_executed:false` / `clearance_only` already correct. | **Already handled** — tagged `CLEARANCE`. |
| **Issuing mouth** | Approve ≠ capture. Risk of treating AUTHORIZE as final. | **Fixed explicitly** — `stripe_auth_after_approve: PENDING_CAPTURE_OR_EXPIRY` in write_state detail. |
| **Sink mouth** | Accept ≠ settle; money_real false. | **Already mostly correct** — made explicit `CLEARANCE_NOT_SETTLEMENT`. |
| **Positive Clear / Scenario 3 / FedNow / Nacha / CL7 / UAPA / ADMT / Stair** | Advisory flag mouths — no Gate spend-map write. | **Already handled** — `write_state.phase=N_A`, advisory. No forced state-machine invention. |
| **Bind ticket consume** | Race was the spend-map case (BEGIN IMMEDIATE + `job_already_spent`). | **Already handled** (PR #103). IN_FLIGHT is the pre-consume sibling of that fix. |

---

## Verify

```bash
cd gate && python3 test_theory_floor.py -v
```

Keys for witness dogfood (generate separately; do not reuse receipt key):

```bash
# GATE_WITNESS_PRIVATE_KEY / GATE_WITNESS_PUBLIC_KEY — Ed25519 raw base64
```

Then `GET /.well-known/evidence-head.json` → `witness.signed: true`.
