# PASTE — Closest to Bitcoin’s property (real scoping)

**26 Sep 2026.** Not hype. Not “we’re almost there.”

---

## The property (named carefully)

Bitcoin’s defining trait is not “Merkle trees” or “hard to rewrite.” Those are mechanisms.

The property is:

> **Value and security accrued without permission or trust from any single counterparty** — the protocol paid anyone who ran it (block subsidy), and adoption compounded without a sales team. (Nakamoto 2008; permissionless entry is architectural, not a policy.)

Tonight’s Gate work does **not** have that property. Mouths, evidence-head, witness *capacity*, OTS stamp — all useful — still sit inside a **permissioned adoption loop**: someone must choose Gate, weld Gate, watch Gate, or cite Gate.

Three conditions would make the Bitcoin-shaped property *possible*. None can be forced. Tonight enables at most the *preconditions* of one of them — and even that is thinner than it looks.

---

## Live facts (do not glaze)

| Surface | Live state (gate.velaru.xyz) |
|---------|------------------------------|
| `/.well-known/evidence-head.json` | Public, signed; `tree_size: 0` |
| `witness.configured` | **false** |
| `independent_watchers` | **`[]`** (published empty on purpose) |
| First-party watch | GitHub Action `gate-watch.yml` every 15m — **not independent** |
| Watch script | Stdlib-only, public at `/watch/evidence-head.py` |
| OTS (tonight, PR #137) | Real calendar `.ots` on empty-tree root — **pending** Bitcoin attestation; calendars accepted digests without a sales call |

---

## Condition 1 — Automatic consumption (CT-browser shape)

**Target:** Another system consumes Gate receipts **by default**, without a human integrating each time — the way Chrome evaluates SCTs under CT policy during TLS validation ([Chrome CT Policy](https://googlechrome.github.io/CertificateTransparency/ct_policy.html)).

| Tonight | Verdict |
|---------|---------|
| Public JSON + inclusion proofs | **Necessary but nowhere near sufficient** |
| MCP `/.well-known/mcp.json` discovery | Discovery ≠ auto-verify; agents do not fail-closed on missing Gate receipts |
| OTS calendars accepting digests | **Borrowed Bitcoin’s property**, did not create Gate’s |

**Honest:** We are **not structurally close.** CT auto-consume exists because a **choke point with market power** (browser vendors) made non-CT certs fail. Gate has no equivalent choke point. No payment rail, agent runtime, or browser defaults to “require Gate NEVER/CLEAR.”

**What would need to exist first:**
1. A **mandatory failure mode** somewhere high-volume: e.g. agent runtime / card processor / escrow that **refuses the write** unless a scoped Gate (or compatible) halt/clear artifact verifies — default on, not opt-in weld.
2. Or: Gate artifacts become a **standard field** inside someone else’s protocol (UCP-like documentary credit for agents; MCP trust frameworks that *require* evidence-pack verify) — Gate as format, not as vendor call.

Until a choke point *other than Gate’s sales motion* enforces consumption, condition 1 is fantasy.

**Closest enabling surface tonight (still not the condition):**  
`evidence-head.json` + proof routes are shaped like a CT STH — strangers *can* poll them. That is the CT *log* side, not the *browser enforcement* side. Logs without browsers stay optional.

---

## Condition 2 — Voluntary unpaid independent witness

**Target:** A truly independent third party runs witness-cosign / head-watch **on their own initiative, unpaid** — `independent_watchers` stops being empty because *they* decided it was worth doing. Analogs: [transparency-dev witnesses](https://github.com/transparency-dev/witness), [Witness Network](https://witness-network.org/), mosskeys “we don’t pay for witnessing.”

| Tonight | Verdict |
|---------|---------|
| `witness` block always present | Capacity — honest `configured: false` |
| `independent_watchers: []` | **Empty. Condition unmet.** |
| Stdlib watch script + invite note | Makes pickup *cheap* if someone wants it |
| First-party GHA watch | Proves Gate cares; **counts against** independence if mistaken for the real thing |

**Honest:** We are **not close.** Capacity ≠ network. Publishing an empty roster is correct hygiene; it is not progress toward a cloud of witnesses.

**What would need to exist first:**
1. At least **one** named outsider caching heads / cosigning, with their own key, unpaid, listed in `independent_watchers` after *they* submit proof of watch — not after Gate “onboards” them as a partner.
2. Preferably: speak **C2SP `tlog-witness`** (or equivalent) so OmniWitness-class operators can add Gate’s origin the way they add other logs — **configuration, not a sales cycle**.
3. A reason for *them*: they rely on Gate-shaped artifacts in *their* supply chain (not charity to Velaru).

**Closest enabling surface tonight:**  
The watch protocol is deliberately boring and stdlib-only — lowest friction invite in the stack. Still an **invite**. Bitcoin did not invite miners; the subsidy pulled them.

---

## Condition 3 — Stranger citation (court / regulator / journalist)

**Target:** Someone Gate never talked to cites a Gate receipt as evidence on its own — the way a Bitcoin txid is pasted into a filing without Satoshi’s permission.

| Tonight | Verdict |
|---------|---------|
| Signed receipts + claim_scope + NEVER | *Citable in form* if a dispute existed |
| OTS-anchored head (pending) | Strengthens “existed by block H” — still not a citation |
| Actual citations | **None known** |
| Tree size 0 | Nothing consequential yet for a stranger to cite |

**Honest:** We are **not close.** Form of an exhibit ≠ presence in the canon. Theology’s “cloud of witnesses” and literature’s canon both require *others* to repeat the work; Gate has not been repeated outside Gate.

**What would need to exist first:**
1. A **real irreversible-write dispute** (chargeback, LC discrepancy, agent over-spend, kill-switch audit) where a third party finds the scoped NEVER/CLEAR packet useful **without** Gate pitching.
2. Preferable: the artifact appears in an **opinion, exam memo, news piece, or docket** with Gate as source-of-bytes, not as interviewee.
3. Until then, Kill Switch Act one-pagers and diligence emails are still *Gate talking* — the opposite of condition 3.

---

## Cross-lens (why forcing “close” would be false)

| Lens | Read |
|------|------|
| **Physics / cosmology** | Bitcoin had an **energy gradient** (subsidy → hashrate → security). Gate has no equivalent thermodynamic pull on outsiders. |
| **Neuroscience** | CT is a **reflex** in the browser stack. Gate checks are still **deliberate** acts (weld, cron, curl). Reflex ≠ brochure. |
| **Theology** | Witness capacity without witnesses is an empty pew. Publishing the empty pew is honest liturgy; it is not a congregation. |
| **Art / canon** | A work enters the canon when strangers quote it. Zero external quotes → not in the canon, however finished the manuscript. |
| **Depth psychology** | Wanting the Bitcoin property can produce **inflation of proximity** (“we built CT-shaped JSON so we’re almost Chrome”). Resist. |

---

## Ranking: what tonight actually moved

| Rank | Surface | Moves which condition? | How much? |
|------|---------|------------------------|-----------|
| 1 | Public evidence-watch + stdlib script | 2 (enables pickup) | Makes unpaid watch *possible*; does not create a watcher |
| 2 | OTS calendar stamp | 1 (weak) / 3 (weak) | Proves digests can enter a permissionless calendar **without sales** — but the value accrues to **Bitcoin’s** property, which Gate *uses*, not *has* |
| 3 | Witness block / claim_scope / NEVER | 2–3 (form only) | Necessary grammar for later citation/cosign; zero instances |
| — | Mouths, Bind Room, DSP, Column RFQ | — | Commercial / regulatory paths — **sales-shaped**, not Bitcoin-shaped |

---

## Plain answer

**We are not structurally close to any of the three yet.**

Tonight’s closest enabling piece is the **public evidence-head + watch protocol** (and OTS as a hitch onto Bitcoin’s existing permissionless calendars). That makes outsider pickup *cheaper*. It does not make outsider pickup *happen*, and it does not create a choke point that consumes Gate by default.

**What would need to exist first (minimum):**

1. **For auto-consume:** A non-Gate choke point that fail-closes without a verified Gate-class artifact.  
2. **For independent witness:** ≥1 unpaid outsider in `independent_watchers` + ideally tlog-witness compatibility.  
3. **For stranger citation:** ≥1 court/regulator/journalist use of a Gate artifact without Gate in the room.

Until one of those three exists as *fact*, claiming Bitcoin-property proximity is glaze. Keep building the enabling surfaces. Do not narrate the network that is not there.
