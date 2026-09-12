# Scorecard zero-tolerance CI

These gates are the floor that keeps Flawless Dimensions 11–14 from regressing.

| Dim | Runner | Term / source list |
|---|---|---|
| 11 | `scripts/scorecard_gates/run_gates.py --dim 11` | Manifests: `gate.json`, `llms.txt`, `commerce.json`, `opportunities.json`. Pages require final **200**. API under `/v1`/`/api`/`/demo` is live only on documented responses: GET **200 / 401 / 403 / 405**, or GET 404 + POST in **{200,400,401,403,405,415,422}**. Bare “not 404” does **not** pass (5xx / connection errors fail). |
| 12 | `--dim 12` | [`banned_lab_terms.txt`](./banned_lab_terms.txt) |
| 13 | `--dim 13` | [`borrowed_cred_terms.txt`](./borrowed_cred_terms.txt) + no `/dtcc` routes. Gate/Mishara: full term scan. Velaru CI job: `--velaru-routes-only` path floor (requires `VELARU_GITHUB_TOKEN`). |
| 14 | `--dim 14` | Bind Room price cents / label only in `gate/commerce/ladder.json` |

Prove each gate catches a break:

```bash
python scripts/scorecard_gates/run_gates.py --prove-fail 11
python scripts/scorecard_gates/run_gates.py --prove-fail 12
python scripts/scorecard_gates/run_gates.py --prove-fail 13
python scripts/scorecard_gates/run_gates.py --prove-fail 14
```

CI workflow: `.github/workflows/zero-tolerance-gates.yml`

## Immediate next (not a someday)

See [`VELARU_DIM13_IMMEDIATE_NEXT.md`](./VELARU_DIM13_IMMEDIATE_NEXT.md): set `VELARU_GITHUB_TOKEN`, land Velaru route deletion, live-prove 404s.

After Gate deploy (separate verify): `/health` shows x402 `demo:true` / configured distinction in the JSON itself, and `POST /demo/x402/agent-pay` returns a live response — same standard as `their_production: false`.
