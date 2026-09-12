# Verification queue — measured dims (do not skip)

Queued after PR #50 (nav/CTA SSOT + `/pattern`) and the Dim 13 settlement route rename.
**Do not claim a portfolio “8.”** Do not mark these PASS until re-run with fresh artifacts.

| Dim | Work | Standard |
|---|---|---|
| 8 / 16 | Fresh Lighthouse / CWV on Gate home, `/bind-room`, `/pricing`; Mishara home | Store JSON under `docs/cwv/` with run date; LCP/CLS/perf cited |
| 11 | Full-site link crawl | `gate/scripts/check_manifest_links.py` + HTML `<a href>` crawl of stranger pages; 0 dead GETs |
| 12 | Full HTML re-grep for jargon | CI lab-enum bans + live OpenAPI EXIST/NONEXIST/HOLD; stranger HTML free of DTCC/SWIFT/lab enums |
| 19 | Timed human stranger test | See `docs/STRANGER_TEST_DIM19.md` — cold, no context, stopwatch |

## Dim 13 — CLOSED (2026-09-12)

Velaru `/dtcc` and `/api/v1/dtcc/*` removed on `main`, deployed, live **404** (not 302/308).
Mishara CI `velaru-surface` live-probes + `--prove-fail-velaru-live` green:
https://github.com/jdnova0802/mishara/actions/runs/34698634128

```bash
curl -sI https://velaru.xyz/api/v1/dtcc/attest | head -1   # expect 404
curl -sI https://velaru.xyz/dtcc | head -1                  # expect 404
curl -s https://gate.velaru.xyz/.well-known/live.json | jq .their_production  # expect false
```

## BACKLOG — Gate institutional suite (NOT a tonight emergency)

Filed after live check: `their_production` is **`false`** on live
`/.well-known/live.json`, `production-skin.json`, and `scorecard.json`.
CI red is **test isolation / harness**, not a live honesty lie.

Same **18** failures on base `cursor/oligarch-grade-25ad` and on #53
([base](https://github.com/jdnova0802/mishara/actions/runs/34688064114) /
[#53](https://github.com/jdnova0802/mishara/actions/runs/34698634126)):

| Bucket | Fix |
|---|---|
| Missing schema (`bind_events`, `install_orders`, `accounts`, settlement tables) | Call `init_db()` in `BindRoomFlaskTests` / related `setUpClass` |
| Copy drift (`non-entity` on refusal page) | Align assertion to current template copy |
| `their_production` True in suite | Isolate shared SQLite / wipe welds so suite order cannot pollute |
| Prefinality / x402 demo rails | Align receipt/JWKS/RTP expectations with current handlers |

Do **not** reopen Dim 13 for this. Separate fix PR off oligarch-grade base.

## Dim 14 residual purge (this follow-up PR)

Residual list must be empty of hand-typed `$1,750` outside `ladder.json`:

- `bind_room.html` / `index.html` meta → `{{ bind_room_price }}`
- `listings.py` → `commerce.price_label(...)`
- `render.yaml` → no `GATE_BIND_ROOM_PRICE_*` fork
- `deploy_render.py` → reads `commerce`
- OpenAPI summary → f-string from `BIND_ROOM_PRICE_LABEL`
- markdown / hustle board → placeholders or SSOT pointers

Gate: `python -m unittest gate.test_commerce.CommerceSSOTTests.test_residual_bind_room_price_not_hand_typed`
