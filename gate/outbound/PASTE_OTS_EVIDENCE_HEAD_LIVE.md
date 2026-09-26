# PASTE — OpenTimestamps evidence-head: live proof (not “wired”)

**26 Sep 2026.** Working stamp against production head. Bitcoin confirmation is calendar-batch (hours), not instant — pending is honest.

---

## What was built

| Piece | Path |
|-------|------|
| Anchor module | `gate/ots_anchor.py` |
| Cron/CLI | `gate/anchor_evidence_head.py` (`stamp-url` / `upgrade` / `status`) |
| Head block | `opentimestamps` on `/.well-known/evidence-head.json` |
| Proof routes | `/.well-known/evidence-head.ots`, `evidence-ots-commitment.json`, `evidence-ots.json` |
| Live proof store | `gate/outbound/ots-proofs/` |

Commitment stamped (canonical JSON, then SHA256):

```json
{"root_hash":"8fa9dc80ca24ccd61bc7715c7d20ff000644fb07179db9eb28a7af55052512cf","spec":"gate-ots-commitment-v1","tree_size":0}
```

Pulled from live `https://gate.velaru.xyz/.well-known/evidence-head.json` at stamp time (empty tree — EMPTY_LEAF root; pipeline is real regardless of tree size).

---

## Live result (this session)

```
ok: true
event: stamped
method: python_opentimestamps
stamped: 2 calendars (min 2)
stamped_at: 2026-09-26T14:43:47.929805+00:00
tree_size: 0
root_hash: 8fa9dc80ca24ccd61bc7715c7d20ff000644fb07179db9eb28a7af55052512cf
commitment_digest: f78f31a9a4fedfcfe4437c069a7c187928c8736d9defba58b702eac022f8db16
ots_path: gate/outbound/ots-proofs/proofs/0-8fa9dc80ca24ccd6.ots
ots_bytes: 443
status: pending
```

`ots info` on that file shows `PendingAttestation` from public calendars (Alice/Bob/EternityWall/Catallaxy pool). That **is** a real `.ots` from real calendars — not a mock.

**Bitcoin block height:** not yet — **not** `BitcoinBlockHeaderAttestation`. Progress at upgrade `2026-09-26T15:45:17Z`:

- Alice calendar: tx `97c93db4dd74095022c7c2e9c18289c222c33bcc879a72e98520f105231f5bf4` — waiting for **6 confirmations**
- Bob calendar: tx `900cde0b565449143fe8dd0b601f6cfaf3649a5572d64137be56b041f7fcab49` — waiting for **6 confirmations**

Status remains **pending** until `ots info` shows `BitcoinBlockHeaderAttestation(HEIGHT)` and `ots verify` succeeds. Do not claim block height yet.

Upgrade command:

```bash
export GATE_OTS_DIR=gate/outbound/ots-proofs
python3 gate/anchor_evidence_head.py upgrade \
  --tree-size 0 \
  --root-hash 8fa9dc80ca24ccd61bc7715c7d20ff000644fb07179db9eb28a7af55052512cf
```

When status flips to `bitcoin_confirmed`, meta records `bitcoin.block_height` and `ots verify` is run against the commitment file.

---

## What this closes on the six-property table

**Publication-hard** was the unbuilt gap. Spend map / claim_scope / IN_FLIGHT / witness capacity already existed. OTS makes rewriting the published head as hard as rewriting Bitcoin history after attestation — same mechanism Peter Todd used to carbon-date ~750M Internet Archive files ([petertodd.org, 2017](https://petertodd.org/2017/carbon-dating-the-internet-archive-with-opentimestamps)).

Honest limit (also on the head block): OTS proves **publication time of the commitment**, not that receipts are correct about the world.

---

## Cron (ops, not a SKU)

```bash
# every 6h — stamp current head if new; always try upgrade
0 */6 * * * cd /app && GATE_OTS_DIR=/var/gate-ots \
  python3 gate/anchor_evidence_head.py stamp-url --url https://gate.velaru.xyz
```

---

## Verify locally

```bash
ots info gate/outbound/ots-proofs/proofs/0-8fa9dc80ca24ccd6.ots
ots verify gate/outbound/ots-proofs/proofs/0-8fa9dc80ca24ccd6.ots \
  -f gate/outbound/ots-proofs/commitments/0-8fa9dc80ca24ccd6.json
```

Pending → “Pending confirmation in Bitcoin blockchain.”  
Confirmed → attests a concrete `BitcoinBlockHeaderAttestation(HEIGHT)`.
