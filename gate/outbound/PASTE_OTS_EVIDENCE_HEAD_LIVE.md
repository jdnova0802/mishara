# PASTE — OpenTimestamps evidence-head: **Bitcoin-confirmed**

**26 Sep 2026.** Live stamp → upgrade → `BitcoinBlockHeaderAttestation(968706)`.

---

## Confirmed

| Field | Value |
|-------|-------|
| Status | **`bitcoin_confirmed`** |
| Bitcoin block height | **968706** |
| Block hash | `000000000000000000013eabe1a4ee7f7571cae27404ef2d4433a3aee50db399` |
| Merkle root (OTS + block) | `e379eb7e41789ddb47411b0db1861bf23b7524ade7c5f1880aee5db615bd8662` |
| Commitment root_hash | `8fa9dc80ca24ccd61bc7715c7d20ff000644fb07179db9eb28a7af55052512cf` |
| tree_size | 0 (EMPTY_LEAF — pipeline real) |
| stamped_at | 2026-09-26T14:43:47Z |
| upgraded_at | 2026-09-26T17:46:13Z |
| `.ots` | `gate/outbound/ots-proofs/proofs/0-8fa9dc80ca24ccd6.ots` |

`ots info` excerpt:

```
verify BitcoinBlockHeaderAttestation(968706)
# Bitcoin block merkle root e379eb7e41789ddb47411b0db1861bf23b7524ade7c5f1880aee5db615bd8662
```

Upgrade calendars reported: `Success! Timestamp complete` (Alice + Bob attestations).

---

## Verify

```bash
export GATE_OTS_DIR=gate/outbound/ots-proofs
ots info $GATE_OTS_DIR/proofs/0-8fa9dc80ca24ccd6.ots
# Expect: BitcoinBlockHeaderAttestation(968706)

ots verify $GATE_OTS_DIR/proofs/0-8fa9dc80ca24ccd6.ots \
  -f $GATE_OTS_DIR/commitments/0-8fa9dc80ca24ccd6.json
# Needs local bitcoind RPC cookie. This cloud box has none —
# so CLI verify exits non-zero. Independent check below.
```

**Independent header check (Blockstream API):** block `968706` merkle root equals the OTS attestation merkle root above → **match**.

```bash
curl -sS https://blockstream.info/api/block-height/968706
# → 000000000000000000013eabe1a4ee7f7571cae27404ef2d4433a3aee50db399
curl -sS https://blockstream.info/api/block/000000000000000000013eabe1a4ee7f7571cae27404ef2d4433a3aee50db399 \
  | python3 -c "import sys,json; b=json.load(sys.stdin); print(b['height'], b['merkle_root'])"
# → 968706 e379eb7e41789ddb47411b0db1861bf23b7524ade7c5f1880aee5db615bd8662
```

---

## Commitment stamped

```json
{"root_hash":"8fa9dc80ca24ccd61bc7715c7d20ff000644fb07179db9eb28a7af55052512cf","spec":"gate-ots-commitment-v1","tree_size":0}
```

From live `https://gate.velaru.xyz/.well-known/evidence-head.json` at stamp time.

---

## What this closes

**Publication-hard** on the six-property table: rewriting the published head is as hard as rewriting Bitcoin history after attestation. OTS proves **publication time of the commitment**, not that receipts are correct about the world.

Kill Switch Act positioning remains separate (same PR branch) — not claimed as Bitcoin proof.

---

## Cron (ops)

```bash
0 */6 * * * cd /app && GATE_OTS_DIR=/var/gate-ots \
  python3 gate/anchor_evidence_head.py stamp-url --url https://gate.velaru.xyz
```
