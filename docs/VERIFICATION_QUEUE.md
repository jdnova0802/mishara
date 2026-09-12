# Verification queue — measured dims (do not skip)

Queued after PR #50 (nav/CTA SSOT + `/pattern`) and the Dim 13 settlement route rename.
**Do not claim a portfolio “8.”** Do not mark these PASS until re-run with fresh artifacts.

| Dim | Work | Standard |
|---|---|---|
| 8 / 16 | Fresh Lighthouse / CWV on Gate home, `/bind-room`, `/pricing`; Mishara home | Store JSON under `docs/cwv/` with run date; LCP/CLS/perf cited |
| 11 | Full-site link crawl | `gate/scripts/check_manifest_links.py` + HTML `<a href>` crawl of stranger pages; 0 dead GETs |
| 12 | Full HTML re-grep for jargon | CI lab-enum bans + live OpenAPI EXIST/NONEXIST/HOLD; stranger HTML free of DTCC/SWIFT/lab enums |
| 19 | Timed human stranger test | See `docs/STRANGER_TEST_DIM19.md` — cold, no context, stopwatch |

## Partial runs this agent turn (not a close)

| Dim | Status | Note |
|---|---|---|
| 11 | Manifest crawl **OK 131 URLs** against live Gate (`gate/scripts/check_manifest_links.py`) | Full HTML `<a href>` stranger crawl still outstanding |
| 12 | Gate `templates/*.html` grep: **0** DTCC/SWIFT/Fedwire hits | Full live HTML re-grep + OpenAPI EXIST vocabulary check still outstanding |
| 8/16 | Not re-run | Need fresh Lighthouse JSON under `docs/cwv/` |
| 19 | Protocol filed | Human timer not yet executed |

## Dim 13 evidence (route rename — already live)

```bash
curl -sI https://velaru.xyz/api/v1/settlement/attest | head -5
curl -sI https://velaru.xyz/api/v1/dtcc/attest | head -8   # expect 308 → /api/v1/settlement/attest
curl -s https://velaru.xyz/openapi.json | python3 -c "import sys,json; p=json.load(sys.stdin).get('paths',{}); print([k for k in p if 'dtcc' in k.lower()])"
```

Canonical paths: `/api/v1/settlement/{events.json,attest,attest/<id>,production/...}`. OpenAPI must list **zero** `/api/v1/dtcc/*` paths.

## Dim 14 residual purge (this follow-up PR)

Residual list must be empty of hand-typed `$1,750` outside `ladder.json`:

- `bind_room.html` / `index.html` meta → `{{ bind_room_price }}`
- `listings.py` → `commerce.price_label(...)`
- `render.yaml` → no `GATE_BIND_ROOM_PRICE_*` fork
- `deploy_render.py` → reads `commerce`
- OpenAPI summary → f-string from `BIND_ROOM_PRICE_LABEL`
- markdown / hustle board → placeholders or SSOT pointers

Gate: `python -m unittest gate.test_commerce.CommerceSSOTTests.test_residual_bind_room_price_not_hand_typed`
