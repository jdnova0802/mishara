# Lab sims — S1 Actus Fence + S3 Performative Seal

**Status:** Lab only. `their_production: false` always.  
**Edge pass context:** `../EDGE_PASS_2026-09-15.md`

## What these are

| Sim | Mouth | Prove |
|---|---|---|
| `actus_fence.py` | Agent tool/pay needs LIVE mandate + digest-bound grant | `python3 -m gate.sims.prove_actus_fence` |
| `performative_seal.py` | Brief needs seal before file; ungrounded cite DENY | `python3 -m gate.sims.prove_performative_seal` |

## Crowding honesty (do not forget)

### S1 — not competing with
- **Fidacy / IntentFence** — already ship grants/receipts for agent pay
- **Visa Intelligent Commerce / Trusted Agent Protocol** — network-scale agent commerce

**Our lab claim:** digest-bound DENY + stranger receipt grammar, including **non-pay** actus (`prod_mutate`). Differentiation later = bank-send weld + public verify URL — not “invented grants.”

### S3 — not competing with
- **Westlaw Quick Check / Lexis Brief Analysis / PelAIkan** — citation *checkers*

**Our lab claim:** **file mouth** — no LIVE seal ⇒ cannot file. Check ≠ speech-act.

## Run

```bash
cd /path/to/repo
python3 -m gate.sims.prove_actus_fence
python3 -m gate.sims.prove_performative_seal
```

Both must print `*_PROVE_OK`.

## Out of scope here

Real wallets, CM/ECF, KYC vendors, grief UX, biometric capture.
