# Lab sims — concrescence mouths (S1/S3 + S6/S7/S8 + S9 watchman)

**Status:** Lab only. `their_production: false` always — **enforced**, not aspirational (`lab_invariant.py`, `prove_lab_invariant`).  
**P0 weld-shape:** S1 bank-send + stranger HTTP verify; S3 EFSP block-transmit — green in `prove_all`.  
**Edge pass:** `../EDGE_PASS_2026-09-15.md`  
**S-tier+:** `../S_TIER_PLUS_THREE_2026-09-15.md`  
**Prove template:** `PROVE_SEQUENCE.md` — `prove_mouth_watch` + `prove_lab_invariant` required for every mouth

## Shared unlocks (not intelligences)

| Module | Role |
|---|---|
| `logos.py` | Shared mandate → grant → digest grammar (amount/rail-bound actus) |
| `verify_http.py` | Local stranger GET — actus, performative, edgar, deed, ron, mouth-watch |

## Receipt classes (bank-branchable — not reason-string parsing)

| `receipt_class` | Emitter | Meaning |
|---|---|---|
| `clearance` | Mouths (S1, S3…) | This actus authorized or not |
| `threat` | S9 Mouth Watch only | Canary / session integrity / trajectory compromise |
| `watch_clear` | S9 | Sense layer clear for this check |
| `preflight` | S10 | Simulated delta match? |
| `epoch` | S16 | Policy epoch fresh? |

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
| `isda_dc_publish.py` | Headline ≠ LIVE DC Resolution (Z1) | `python3 -m gate.sims.prove_isda_dc_publish` |
| `cls_settle.py` | Matched FX ≠ settled PvP (Z2) | `python3 -m gate.sims.prove_cls_settle` |
| `iana_root_change.py` | Intent ≠ root-zone write (Z3) | `python3 -m gate.sims.prove_iana_root_change` |
| `lloyds_bind_stamp.py` | Paperwork ≠ registered BAA bind (Z4) | `python3 -m gate.sims.prove_lloyds_bind_stamp` |
| `itu_biu_mifr.py` | Paper filing ≠ MIFR record (Z5) | `python3 -m gate.sims.prove_itu_biu_mifr` |
| S1↔S9 wire | Canary vs hostile-session as **separate** scenarios | `python3 -m gate.sims.prove_actus_s9_wire` |
| S8↔S9 wire | Hostile watch vs local synthetic appearance | `python3 -m gate.sims.prove_ron_s9_wire` |
| `lab_invariant.py` | `their_production is False` on every stamp + stored receipt | `python3 -m gate.sims.prove_lab_invariant` |

## Crowding honesty

### S1 — not Fidacy / Visa TAP
Digest-bound DENY + stranger receipt incl. non-pay actus. **P0:** FedNow/RTP-*shaped* `bank_send` / `fednow_push` / `rtp_push` DENY fixtures + HTTP verify of clearance **and** linked threat.

### S3 — not Westlaw/Lexis checkers
**File mouth** — no LIVE seal ⇒ cannot file. **P0:** `transmit_efsp` block-transmit (`efsp_block_no_seal`); fake cite cannot seal ⇒ cannot transmit; stranger HTTP seal/file/transmit receipts.

### S7 — not Workiva
**Submit mouth** — ungrounded quantity ⇒ cannot submit.

### S6 — not title insurance / post-record alerts
**Record accept** mouth.

### S8 — not notary marketplace
**Refuse** mouth + stranger receipt.

### S9 — not Visa TAP / not SOC dashboard
**Watchman** — threat receipts feeding mouths. DENY-this-actus only.

### Z1 — not CDS trading / not news AI
**DC Resolution publish mouth** — headline ≠ Credit Event.

### Z2 — not FX risk dashboard
**CLS-shaped settle mouth** — matched ≠ PvP settled.

### Z3 — not DNSSEC monitoring SaaS
**Root-zone change mouth** — intent ≠ applied DS/NS write.

### Z4 — not Lloyd's market analytics
**Registered bind stamp** — paperwork ≠ LIVE BAA bind.

### Z5 — not constellation planning SaaS
**ITU BIU/MIFR mouth** — API filing ≠ recorded assignment.

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
