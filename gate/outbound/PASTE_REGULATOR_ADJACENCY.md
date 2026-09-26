# PASTE — Regulator adjacency (Track 1 + Track 2)

Branch: `cursor/regulator-adjacency-ce84`

## Track 1 — repeated presence (drafts ready; not auto-sent)

| Door | When | Artifact | Status |
|---|---|---|---|
| NAIC BDAIWG Webex | **Oct 8, 2026 11:00 a.m. ET** (reverify Webex on NAIC page) | `docs/naic/NAIC_OCT8_2026_VERBAL_COMMENT.md` | Draft — same four asks as written comment |
| HMT Modernising PSR | **closes 11:59pm 6 Oct 2026** → Modernisingpaymentservices@hmtreasury.gov.uk | `docs/hmt/HMT_Q15_AGENTIC_PAYMENTS_RESPONSE.md` | Draft — Q15 only, cites live Issuing mouth |

Honest: no Sept 14 filed NAIC letter in repo (written draft deadline COB Sept 29). No GAAIA filed copy in repo (channel `GAAIA@mail.house.gov` open).

## Track 2 — regulator verify page

Public, non-commercial: `/regulator` · `/.well-known/regulator.json`

- Maps NAIC four asks + HMT Q15 → live Issuing / claim_scope / evidence-head / seal
- **Mint checkable receipt** → signed NO_GO in evidence log → stranger checks signature + Merkle inclusion + OTS probe (no login)
- Docket links with honest draft/filed/open labels

```bash
# after deploy
curl -s https://gate.velaru.xyz/.well-known/regulator.json | jq '.naic_asks|length,.hmt_q15.submit_email,.live'
curl -sX POST https://gate.velaru.xyz/demo/regulator/mint -H 'content-type: application/json' -d '{}'
# → event_id; open /regulator?event_id=… or /v1/regulator/verify?event_id=…
```

## Live vs open (as of this PR)

| Item | State |
|---|---|
| Issuing workflow lock + claim_scope dogfood | **Live** on prod (#142) |
| evidence-head.json | **Live** (tree_size may be 0 until first mint on that origin) |
| `/regulator` mint + verify | **Ships in this PR** — live after deploy |
| OTS `/.well-known/evidence-ots.json` | **Not on prod** — PR #137 open; offline BTC height 968706 |
| NAIC written comment filed | **Open** until Demond sends + `docs/naic/submitted/` |
| NAIC Oct 8 verbal delivered | **Open** — confirm Webex, then speak |
| HMT Q15 submitted | **Open** — send before 6 Oct 23:59 |
| GAAIA letter | **Open** — no filed copy in repo |
