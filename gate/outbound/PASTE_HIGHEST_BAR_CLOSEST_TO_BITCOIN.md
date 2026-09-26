# PASTE — Highest bar closest to Bitcoin (for Gate)

**26 Sep 2026.** Not “become Bitcoin.” Closest structural trust bar Gate can honestly chase.

---

## What Bitcoin actually is (the bar)

From Nakamoto (2008): replace a **trusted mint** with (1) public announcement of all spends, (2) a single ordered history, (3) proof that rewriting history is **computationally expensive** if honest majority hashpower holds.

| Property | Bitcoin | Meaning for Gate |
|----------|---------|------------------|
| No trusted third party for *ledger truth* | Yes (full nodes) | Gate is not a currency ledger — don’t fake this |
| Anyone verifies without asking the operator | Yes | Target for **receipts** |
| Double-spend / equivocation hard | PoW cost | Target for **history of claims** |
| Open participation | Permissionless mining | Gate won’t match; witnesses can diversify |
| Probabilistic finality | Confirmations | Tree-head anchors inherit this if Bitcoin-anchored |

**Honest ceiling:** Gate can get **Bitcoin-adjacent finality for “this claim existed / this tree head was published”** — not Bitcoin’s property of **who owns the coins**.

---

## Ladder — highest bar → what Gate has

| Rank | Bar | How close to Bitcoin | Gate today | Gap |
|------|-----|----------------------|------------|-----|
| **0** | **Be Bitcoin / run a money consensus** | Identity | No — wrong product | Don’t |
| **1 — HIGHEST useful** | **Anchor Gate Merkle tree heads in Bitcoin** (OpenTimestamps / SCITT time-anchor profile) | Inherits PoW rewrite cost for *timestamps of claims*; verifier needs only block headers + Merkle path; calendar is convenience not authority ([opentimestamps.org](https://opentimestamps.org/); draft-fassbender-scitt-time-anchor) | **Not done** | Periodic OTS of `evidence-head` / signed tree head |
| **2** | **Proactive multi-witness cosign** (“Honest or Bust” / CoSi) | Authority can still sign, but **cannot forge privately** — witnesses force detection; no PoW (Syta et al.; draft-ford-trans-witness; draft-ford-cfrg-cosi) | **Partial** — `evidence_log.py` already supports independent `GATE_WITNESS_*` cosign of tree head | Need **many unaffiliated** witnesses + client policy (accept only if ≥k of published set) |
| **3** | **CT-class public Merkle log + inclusion/consistency proofs** | Detectable history; single log still a trust point unless gossip/witnessed (RFC 6962/9162) | **Mostly yes** — append-only receipt hash log, inclusion proofs, signed tree head (`.well-known/receipt/.../proof.json`) | Multi-log / gossip; don’t let one DB be the only view |
| **4** | **Stranger-verifiable signed claim_scope + fail-closed** | Attestation-class (TPM/SNARK verify rhyme) | **Yes** | Doesn’t stop operator from soft NEVER→HOLD before signing |
| **5** | **Issuer-pays opinion stamp** | Moody’s — **opposite** of Bitcoin | Diligence/Bind Room risk if framed as rating | Keep as ops revenue, not truth |

**Highest bar Gate can get closest to Bitcoin without becoming it: Rank 1 (Bitcoin-anchor the evidence heads) stacked on Rank 2–4.**

That is the max: **PoW-backed “this scoped receipt / tree existed by block height H”** + **multi-witness so Gate can’t show two histories** + **claim_scope so the leaf means something**.

---

## What that bar buys (and does not)

### Buys (Bitcoin-like for evidence)

- Stranger verifies inclusion without trusting Gate’s API (Merkle path + published head).
- After OTS upgrade: stranger verifies **time-binding** against Bitcoin headers — rewriting the claim history costs **Bitcoin-scale** work (same security model as OTS, not “Gate is Bitcoin”).
- Multi-witness: split-view / secret equivocation becomes **detectable** (CT + CoSi lesson).

### Does not buy

- Proof the underlying facts were true (only that the claim was published).
- Censorship-resistant *issuance* of CLEAR (Gate or witnesses can still refuse to sign).
- Double-spend prevention for dollars (still bank/network rails).
- Permissionless mining of verdicts.

---

## Concrete “highest bar” build order (for real)

1. **Keep** fail-closed + signed `claim_scope` + stranger verify (floor).  
2. **Harden** evidence log: publish signed tree heads on a schedule; consistency proofs vs prior heads (already CT-shaped in code).  
3. **Diversify witnesses:** ≥3 independent cosigners (not same corp as Gate receipt key); clients require quorum.  
4. **Bitcoin-anchor:** OpenTimestamps (or equivalent) each tree head → portable `.ots` proof on the evidence head.  
5. **Doctrine:** market the stack as **PoW-timestamped clearance evidence**, never as “decentralized money” or “Gate replaces Bitcoin.”

---

## One-liner

**Closest to Bitcoin Gate can honestly reach = OpenTimestamps-style Bitcoin anchoring of Gate’s Merkle evidence heads + multi-witness cosign (Honest-or-Bust) on top of today’s claim_scope / fail-closed / stranger-verify.** That borrows Bitcoin’s rewrite cost for *when a claim was published* — it does not make Gate Bitcoin, and it does not prove the world behind the claim.
