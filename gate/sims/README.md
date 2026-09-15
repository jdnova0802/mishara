# Lab sims — concrescence mouths (S1/S3 + S6/S7/S8 + S9 watchman)

**Status:** Lab only. `their_production: false` always — **enforced**, not aspirational (`lab_invariant.py`, `prove_lab_invariant`).  
**Edge pass:** `../EDGE_PASS_2026-09-15.md`  
**S-tier+ three:** `../S_TIER_PLUS_THREE_2026-09-15.md`

## What these are

| Sim | Mouth | Prove |
|---|---|---|
| `actus_fence.py` | Agent tool/pay needs LIVE mandate + digest-bound grant | `python3 -m gate.sims.prove_actus_fence` |
| `performative_seal.py` | Brief needs seal before file; ungrounded cite DENY | `python3 -m gate.sims.prove_performative_seal` |
| `edgar_disclose_seal.py` | Filing needs seal before EDGAR-shaped submit | `python3 -m gate.sims.prove_edgar_disclose_seal` |
| `deed_record_gate.py` | Instrument needs LIVE logos before record | `python3 -m gate.sims.prove_deed_record_gate` |
| `ron_attest_refuse.py` | Remote appearance ≠ notarial act; refuse + receipt | `python3 -m gate.sims.prove_ron_attest_refuse` |
| `mouth_watch.py` | Authorized-looking trajectory ≠ trusted mouth context (canary / session / drift) | `python3 -m gate.sims.prove_mouth_watch` |
| `lab_invariant.py` | `their_production is False` on every stamp + stored receipt | `python3 -m gate.sims.prove_lab_invariant` |

## Crowding honesty (do not forget)

### S1 — not competing with
- **Fidacy / IntentFence** — already ship grants/receipts for agent pay
- **Visa Intelligent Commerce / Trusted Agent Protocol** — network-scale agent commerce

**Our lab claim:** digest-bound DENY + stranger receipt grammar, including **non-pay** actus (`prod_mutate`). Differentiation later = bank-send weld + public verify URL — not “invented grants.”

### S3 — not competing with
- **Westlaw Quick Check / Lexis Brief Analysis / PelAIkan** — citation *checkers*

**Our lab claim:** **file mouth** — no LIVE seal ⇒ cannot file. Check ≠ speech-act.

### S7 — not competing with
- **Workiva / disclosure workstations / XBRL validators** — format & workflow

**Our lab claim:** **submit mouth** — ungrounded quantity ⇒ no seal ⇒ cannot submit.

### S6 — not competing with
- **Post-record property alerts / title insurance UIs**

**Our lab claim:** **record accept** — inject/lock/notary fail ⇒ DENY before title remade.

### S8 — not competing with
- **RON marketplaces / commission platforms**

**Our lab claim:** **refuse mouth** — synthetic/unknown appearance ⇒ REFUSE + stranger receipt.

### S9 — not competing with
- **Visa TAP / bot recognition** — “is this an approved agent?”
- **SOC / agent-security dashboards / raw deepfake ML vendors**

**Our lab claim:** **watchman** — canary + trajectory + session score that stamps stranger **threat receipts** and feeds DENY into S1/S8 (and later S6/S7). Sense layer beside the lock — not a monitoring UI.

## Run

```bash
cd /path/to/repo
python3 -m gate.sims.prove_actus_fence
python3 -m gate.sims.prove_performative_seal
python3 -m gate.sims.prove_mouth_watch
python3 -m gate.sims.prove_edgar_disclose_seal
python3 -m gate.sims.prove_deed_record_gate
python3 -m gate.sims.prove_ron_attest_refuse
python3 -m gate.sims.prove_lab_invariant
```

All must print `*_PROVE_OK` / `LAB_INVARIANT_PROVE_OK`.

## Out of scope here

Real wallets, CM/ECF, EDGAR, county recorders, KYC vendors, grief UX, biometric capture, notary commissions.
