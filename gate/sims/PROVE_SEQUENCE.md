# Standard prove sequence (required template)

Every mouth / intelligence ships with this sequence. **Do not bolt on later.**

```bash
python3 -m gate.sims.prove_all
```

Current `prove_all` order:

1. `prove_actus_fence`
2. `prove_performative_seal`
3. `prove_mouth_watch` ← **required always**
4. `prove_actus_s9_wire` ← canary ≠ hostile session
5. `prove_preflight_diff` ← **Scenario X: S9 clear + S10 DENY alone**
6. `prove_epoch_decay`
7. `prove_deny_federation_stub` ← in-process only
8. `prove_edgar_disclose_seal`
9. `prove_deed_record_gate`
10. `prove_ron_attest_refuse`
11. `prove_lab_invariant` ← **required last**

## Receipt classes

| `receipt_class` | Emitter | Meaning |
|---|---|---|
| `clearance` | Mouths | This actus authorized? |
| `threat` | S9 | Canary / session / trajectory compromise |
| `watch_clear` | S9 | Sense clear |
| `preflight` | S10 | Simulated delta match? |
| `epoch` | S16 | Policy epoch fresh? |

## S10 vs S9 (do not entangle)

| | S9 Mouth Watch | S10 Preflight Diff |
|---|---|---|
| Question | Is session trustworthy? | Does actus match simulated delta? |
| DENY object | `threat` | `preflight` |
| Prove gate | A canary ≠ B hostile | **Scenario X: S9 ALLOW + S10 DENY** |

## S9 trip effect

`deny_this_actus: true` only. No lockout / alert fanout / quarantine.
