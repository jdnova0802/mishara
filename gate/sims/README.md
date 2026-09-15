# Lab sims — concrescence mouths (S1/S3 + S6/S7/S8 + S9 watchman)

**Status:** Lab only. `their_production: false` always — **enforced**, not aspirational (`lab_invariant.py`, `prove_lab_invariant`).  
**Edge pass:** `../EDGE_PASS_2026-09-15.md`  
**S-tier+:** `../S_TIER_PLUS_THREE_2026-09-15.md`  
**Prove template:** `PROVE_SEQUENCE.md` — `prove_mouth_watch` + `prove_lab_invariant` required for every mouth

## Receipt classes (bank-branchable — not reason-string parsing)

| `receipt_class` | Emitter | Meaning |
|---|---|---|
| `clearance` | Mouths (S1…) | This actus authorized or not |
| `threat` | S9 Mouth Watch only | Canary / session integrity / trajectory compromise |
| `watch_clear` | S9 | Sense layer clear for this check |

S9 block on S1 → clearance DENY (`watch_block: true`, `threat_receipt_id`, `threat_class`) **linking** to a separate threat object.

## S9 trip effect (pinned)

DENY **this** proposed actus + emit threat receipt. **No** session lockout, alert fanout, or quarantine. Machine field: `effect` on every threat receipt.

## What these are

| Sim | Mouth | Prove |
|---|---|---|
| `actus_fence.py` | Agent tool/pay needs LIVE mandate + digest-bound grant | `python3 -m gate.sims.prove_actus_fence` |
| `performative_seal.py` | Brief needs seal before file; ungrounded cite DENY | `python3 -m gate.sims.prove_performative_seal` |
| `edgar_disclose_seal.py` | Filing needs seal before EDGAR-shaped submit | `python3 -m gate.sims.prove_edgar_disclose_seal` |
| `deed_record_gate.py` | Instrument needs LIVE logos before record | `python3 -m gate.sims.prove_deed_record_gate` |
| `ron_attest_refuse.py` | Remote appearance ≠ notarial act; refuse + receipt | `python3 -m gate.sims.prove_ron_attest_refuse` |
| `mouth_watch.py` | Authorized-looking trajectory ≠ trusted mouth context | `python3 -m gate.sims.prove_mouth_watch` |
| S1↔S9 wire | Canary vs hostile-session as **separate** scenarios | `python3 -m gate.sims.prove_actus_s9_wire` |
| `lab_invariant.py` | `their_production is False` on every stamp + stored receipt | `python3 -m gate.sims.prove_lab_invariant` |

## Crowding honesty

### S1 — not Fidacy / Visa TAP
Digest-bound DENY + stranger receipt incl. non-pay actus. Weld later = bank-send + verify URL.

### S3 — not Westlaw/Lexis checkers
**File mouth** — no LIVE seal ⇒ cannot file.

### S7 — not Workiva
**Submit mouth** — ungrounded quantity ⇒ cannot submit.

### S6 — not title insurance / post-record alerts
**Record accept** mouth.

### S8 — not notary marketplace
**Refuse** mouth + stranger receipt.

### S9 — not Visa TAP / not SOC dashboard
**Watchman** — threat receipts feeding mouths. DENY-this-actus only.

## Run (standard sequence — required)

```bash
python3 -m gate.sims.prove_all
# always includes:
#   prove_mouth_watch
#   prove_lab_invariant
```

See `PROVE_SEQUENCE.md` for the template every future mouth must follow.

## Out of scope

Real wallets, CM/ECF, EDGAR, county recorders, KYC, grief UX, biometrics, notary commissions, SOC dashboards, session lockout fanout.
