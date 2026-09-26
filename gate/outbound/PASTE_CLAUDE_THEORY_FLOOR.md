# PASTE TO CLAUDE — theory floor (three gaps) just shipped

Branch: `cursor/theory-floor-harden-ce84`
Report: `gate/outbound/THEORY_FLOOR_THREE_GAPS.md`

## What we did (not new products)

### 1. Signed `claim_scope` on every Never/DENIED
Every negative claim now carries a structured boundary (which logs, time window, counterparties/keys) **inside** the signed payload — not implied by the endpoint.

- Never / exclusion: signed envelope + spend-map boundary
- Clear DENIED/NOT DENIED: deny-registry boundary signed
- Seal MISSING/BROKEN/UNSIGNED: bind_events + evidence-log boundary
- Go/Prefinality NO_GO/HOLD: `scope` **inside the Ed25519 JWT** + signed_claim
- Positive Clear / Scenario 3 / FedNow / Nacha / CL7 (and sibling advisory mouths): signed via `mouths.evaluate` wrapper
- Issuing + Sink: inherit prefinality JWT scope

### 2. Witness co-sign capacity on evidence-head
`/.well-known/evidence-head.json` now always has a `witness` block. Set `GATE_WITNESS_PRIVATE_KEY` + `GATE_WITNESS_PUBLIC_KEY` (air-gapped from receipt key). No consortium partner required yet — infrastructure exists. Unconfigured → `configured: false` (honest), not silent single-party forever.

### 3. Explicit IN_FLIGHT / PENDING (honest per-mouth)
- **Fixed gap:** Never used to treat “no redeemed leaf” as ABSENT even when an unconsumed ticket was live. Now `spend_phase`: ABSENT | IN_FLIGHT | SPENT. Never during IN_FLIGHT ≠ Never during ABSENT (plain text + write_state).
- **Already handled (no fake fix):** Clear rail windows; Seal verify-only; Go HOLD + clearance_only; advisory mouths (N_A); bind-ticket race (BEGIN IMMEDIATE / job_already_spent).
- **Issuing/Sink:** explicit that approve/accept ≠ capture/settle.

## Tests
`python3 gate/test_theory_floor.py -v` — 13 ok.

## Ask Claude
Does this close the three gaps as stated, or is anything still only prose / still collapsed?
