# Standard prove sequence (required template)

Every mouth ships with this sequence. **Do not bolt on later.**

```bash
python3 -m gate.sims.prove_<mouth>       # mouth-specific DENYs
python3 -m gate.sims.prove_mouth_watch   # REQUIRED — always
python3 -m gate.sims.prove_lab_invariant # REQUIRED — always (mutation + all receipts)
```

Or run the whole suite:

```bash
python3 -m gate.sims.prove_all
```

`prove_all` currently runs:

1. `prove_actus_fence`
2. `prove_performative_seal`
3. `prove_mouth_watch` ← required
4. `prove_actus_s9_wire` ← S1↔S9 canary **and** hostile-session as separate scenarios
5. `prove_edgar_disclose_seal`
6. `prove_deed_record_gate`
7. `prove_ron_attest_refuse`
8. `prove_lab_invariant` ← required last

When adding S10+: add `prove_<new>` into `STANDARD_SEQUENCE` in `prove_all.py` **before** `prove_lab_invariant`, and keep `prove_mouth_watch` + `prove_lab_invariant` in place.

## Receipt classes (bank-branchable)

| `receipt_class` | Who emits | Meaning |
|---|---|---|
| `clearance` | Actus Fence / other mouths | This action authorized or not (`decision` + `reason_code`) |
| `threat` | Mouth Watch only | Compromised context / canary / trajectory — **different object** |
| `watch_clear` | Mouth Watch | Sense layer clear for this check |

On S9 block, S1 returns **clearance** DENY with `watch_block: true`, `threat_receipt_id`, `threat_class` linking to a separate **threat** receipt. Bank code: branch on `receipt_class` / `threat_class`, not reason text.

## S9 trip effect (pinned)

```json
{
  "deny_this_actus": true,
  "session_lockout": false,
  "alert_fanout": false,
  "quarantine": false
}
```

DENY this proposed actus + stranger threat receipt. No SOC. No lockout. Broader only if a later actus re-queries Watch.
