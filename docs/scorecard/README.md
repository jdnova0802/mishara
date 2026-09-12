# Scorecard zero-tolerance CI

These gates are the floor that keeps Flawless Dimensions 11–14 from regressing.

| Dim | Runner | Term / source list |
|---|---|---|
| 11 | `scripts/scorecard_gates/run_gates.py --dim 11` | Manifests: `gate.json`, `llms.txt`, `commerce.json`, `opportunities.json`. Pages require final **200**. API under `/v1`/`/api`/`/demo` is live only on documented responses: GET **200 / 401 / 403 / 405**, or GET 404 + POST in **{200,400,401,403,405,415,422}**. Bare “not 404” does **not** pass (5xx / connection errors fail). |
| 12 | `--dim 12` | [`banned_lab_terms.txt`](./banned_lab_terms.txt) |
| 13 | `--dim 13` | [`borrowed_cred_terms.txt`](./borrowed_cred_terms.txt) + no `/dtcc` routes on Gate/Mishara. Velaru: source floor in Velaru CI; Mishara job `velaru-surface` live-probes `velaru.xyz` for **404** on `/dtcc` paths (**no token**). |
| 14 | `--dim 14` | Bind Room price cents / label only in `gate/commerce/ladder.json` |

Prove each gate catches a break:

```bash
python scripts/scorecard_gates/run_gates.py --prove-fail 11
python scripts/scorecard_gates/run_gates.py --prove-fail 12
python scripts/scorecard_gates/run_gates.py --prove-fail 13
python scripts/scorecard_gates/run_gates.py --prove-fail 14
```

CI workflow: `.github/workflows/zero-tolerance-gates.yml`

## Post-merge verify (x402)

After Gate deploy: `/health` must show x402 demo vs treasury distinction in the JSON itself, and `POST /demo/x402/agent-pay` must return a live response — same standard as `their_production: false`.
