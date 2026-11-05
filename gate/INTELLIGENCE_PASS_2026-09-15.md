# Intelligence pass — what to build next vs museum

**Date:** 2026-09-15  
**Companions:** `DESKTOP_ORDERS_PASTE_2026-09-15.md`, `S_TIER_PLUS_THREE_2026-09-15.md`, `EDGE_PASS_2026-09-15.md`, `sims/PROVE_SEQUENCE.md`  
**Law:** logos-before-actus. Fail-closed. Stranger-verifiable. `their_production: false`. Not a SOC. Not Visa TAP.

Hunt question: beyond mouths (S1–S8) + Mouth Watch (S9), which *intelligences* level Nisaba?

---

## Already owned (do not re-hunt)

| Layer | What | Status |
|---|---|---|
| Recognize | Visa TAP / bot identity | **Not our fight** |
| Gate | S1–S8 fail-closed mouths | Lab spines proved |
| Sense | S9 Mouth Watch (threat ≠ clearance) | Proved; wire S1 A/B separate |

---

## Immediate (add to build queue now)

After P0 S1/S3 extend + S9 wire stay green (`prove_all` / `prove_actus_s9_wire`).

| ID | Product | Ontological cut | Why now | First prove |
|---|---|---|---|---|
| **S10** | **Preflight Diff** | Proposed actus ≠ simulated world-delta | Dry-run before grant binds. Watchman = “hostile?”; preflight = “what breaks if ALLOW?” Lab-provable. | No sim delta / hostile delta / uncertainty → DENY + **clearance** receipt linking optional threat; stranger-fetchable preflight object |
| **S16** | **Epoch / Decay** | LIVE mandate ≠ fresh policy epoch | Mandate + policy digest expire together. Almost free weld on S1/S9. | Stale epoch / mismatched policy_digest → DENY; fresh → ALLOW |
| **S13** | **Deny Federation** *(lab stub only)* | Local DENY ≠ stranger-known DENY | Cross-mouth multiplier. Stub receipt grammar — **do not** build the network yet. | Foreign DENY for same digest → this mouth DENY + linked foreign threat/clearance id |

**Rank:** S10 ≥ S16 ≫ S13-stub.

---

## Museum (name and refuse — do not start)

| ID | Idea | Why museum |
|---|---|---|
| **S11** Continuity Binder | Preserve security context across agent hops | Research/ACS-adjacent; premature before real mouth welds |
| **S12** Ancestry / Edge Revoke | Authority-preserving delegation revoke | Needed for fleet closings; wait until S8↔S6↔bank is one path |
| **S14** Silence Intel | Expected actus absent ≠ safe | Thesis gold; no product shape without institutional expected-actus schedules |
| **S15** Context-C Router | Auto-pick court vs EDGAR vs deed | Dashboard risk; mouths *are* the C |
| **S17** Compensator Bind | ALLOW requires undo path | Domain ops theater; attach per vertical later |

---

## Claude confirmation gate (locked in)

Before calling S10 done, `prove_preflight_diff` **must** include **Scenario X**:

> S9 trust check passes cleanly (no threat) **and** preflight still DENYs solely because simulated delta ≠ actual delta.

Proved: `scenario_x.s9_clear=true`, `preflight_deny_reason=preflight_delta_mismatch`, `independent_of_threat=true`.

S13 stub proved `in_process_only=true` (no network imports in module).

S16 proved epoch rotate → prior grant DENY at actus time (`epoch_decayed`).


---

## Desktop pastes (S10 / S16 / S13)

### PASTE S10 — Preflight Diff

```
Build Preflight Diff sim — simulate-before-actus intelligence feeding mouths.

Goal: prove DENY when proposed actus lacks a LIVE preflight delta, or delta is hostile/uncertain.

Lab only. their_production: false. No real twins/prod dry-run rails.

Model:
- Action: { action_type, digest, payload }
- Preflight: { preflight_id, digest, projected_delta, invariants_ok: bool|null, expires_at }
- Decision: ALLOW preflight | DENY

Hard DENY when any:
1. no preflight bound to exact digest
2. preflight expired / stale
3. invariants_ok is False or null (uncertainty → DENY)
4. projected_delta marked hostile / over_cap / out_of_scope
5. digest mismatch

ALLOW only with LIVE preflight matching digest; emit stranger-fetchable preflight receipt.
receipt_class: "preflight" (distinct from clearance and threat).

Wire (optional lab): Actus Fence execute may require preflight_id; missing → DENY reason preflight_required.

Prove: no preflight DENY; stale DENY; hostile delta DENY; clean LIVE ALLOW + receipt.
Not a SOC. Not S9. Preflight asks "what breaks if ALLOW?"
Keep prove_mouth_watch + prove_lab_invariant in sequence.
```

### PASTE S16 — Epoch / Decay

```
Build Epoch/Decay sim — LIVE logos must carry fresh policy epoch.

Goal: prove DENY when mandate/grant epoch ≠ current policy_digest epoch.

Lab only. their_production: false.

Model:
- PolicyEpoch: { epoch_id, policy_digest, live: bool }
- Mandate/Grant bound to epoch_id + policy_digest at create
- On execute: require epoch live AND digests match current

Hard DENY: epoch revoked/rotated; policy_digest mismatch; missing epoch; uncertainty.

ALLOW only with matching LIVE epoch; stranger receipt includes epoch_id + policy_digest.

Wire into Actus Fence + Mouth Watch stamps.
Prove: rotate epoch → prior grant DENY; fresh epoch ALLOW.
Not a dashboard. Decay only.
Keep prove_mouth_watch + prove_lab_invariant in sequence.
```

### PASTE S13 — Deny Federation (stub)

```
Build Deny Federation STUB — local mouth consults foreign DENY for same digest.

Goal: prove DENY when a stranger-verifiable foreign DENY exists for action_digest.

Lab only. their_production: false. No real network. In-process ForeignDenyStore fixture only.

Model:
- ForeignDeny: { digest, source_mouth, foreign_receipt_id, receipt_class, ts }
- Before ALLOW at local mouth: lookup digest; if hit → DENY

Hard DENY on foreign hit; link foreign_receipt_id on local clearance DENY (same pattern as S9 threat_receipt_id).

Prove: plant foreign DENY → local execute DENY with link; no foreign → pass to normal clearance.
Do NOT build gossip/ledger/product network.
Keep prove_mouth_watch + prove_lab_invariant in sequence.
```

---

## Updated run order (intelligence layer)

| Order | Item | Status |
|---|---|---|
| 1–2 | P0 S1 + S3 extend | Desktop |
| 3 | S9 wire (A canary ≠ B hostile) | Cloud proved (`prove_actus_s9_wire`) |
| 4 | **S10 Preflight Diff** lab | **Next cloud/desktop** |
| 5 | **S16 Epoch/Decay** lab | **Next** |
| 6 | **S13 Deny Federation stub** | **Next (stub only)** |
| 7+ | S7→S6→S8 weld-shape | After / parallel careful |
| — | S11/S12/S14/S15/S17 | **Museum** |
| — | S2/S4/S5 | Defer (edge pass) |

---

## PASTE FOR CLAUDE (copy everything in the fence)

```
You are continuing Nisaba Gate work in-repo under gate/.

Context already done (do not re-discover):
- Logos-before-actus mouths S1/S3/S6/S7/S8 lab spines
- S9 Mouth Watch: threat receipts distinct from clearance (receipt_class)
- Trip effect: deny_this_actus only; no session lockout/SOC
- prove_actus_s9_wire: Scenario A canary alone ≠ Scenario B hostile session alone
- Standard prove: prove_all includes prove_mouth_watch + prove_lab_invariant (required always)
- their_production: false hard-enforced (stamp_lab_flag + mutation catch)

Read first:
- gate/DESKTOP_ORDERS_PASTE_2026-09-15.md
- gate/INTELLIGENCE_PASS_2026-09-15.md   ← this pass
- gate/sims/PROVE_SEQUENCE.md
- gate/EDGE_PASS_2026-09-15.md

Confirm green:
  python3 -m gate.sims.prove_all

=== IMMEDIATE BUILD (in order) ===

1) S10 Preflight Diff (gate/sims/)
   - Proposed actus ≠ simulated world-delta
   - receipt_class: "preflight" (NOT clearance, NOT threat)
   - DENY: missing/stale/hostile/uncertain preflight bound to digest
   - Prove module + wire optional require into actus_fence
   - Paste details in INTELLIGENCE_PASS_2026-09-15.md

2) S16 Epoch/Decay
   - LIVE mandate ≠ fresh policy epoch
   - DENY on epoch rotate / policy_digest mismatch
   - Wire into actus_fence (+ mouth_watch stamps if natural)
   - Prove DENY after rotate; ALLOW on fresh epoch

3) S13 Deny Federation STUB only
   - In-process ForeignDenyStore
   - Same digest foreign DENY → local clearance DENY linking foreign_receipt_id
   - NO network/ledger product
   - Prove plant-foreign → local DENY

After each: prove_mouth_watch + prove_lab_invariant still green (or prove_all).

=== MUSEUM (do not build) ===
S11 Continuity Binder, S12 Ancestry/Edge Revoke, S14 Silence Intel,
S15 Context-C Router, S17 Compensator Bind.
Also still deferred: S2 liveness R&D, S4 grief UX, S5 biometric matcher.

=== HARD TRAPS ===
- Not a SOC dashboard
- Not Visa TAP recognition
- Do not conflate S10 preflight with S9 threat
- Do not grow S13 stub into a shared ledger yet
- Fail-closed; stranger-verifiable; their_production: false

=== DONE WHEN ===
prove_preflight_diff / prove_epoch_decay / prove_deny_federation_stub print *_PROVE_OK
and python3 -m gate.sims.prove_all still green.
```
