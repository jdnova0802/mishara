# Scorecard zero-tolerance CI

These gates are the floor that keeps Flawless Dimensions 11–14 from regressing.

| Dim | Runner | Term / source list |
|---|---|---|
| 11 | `scripts/scorecard_gates/run_gates.py --dim 11` | Manifests: `gate.json`, `llms.txt`, `commerce.json`, `opportunities.json` |
| 12 | `--dim 12` | [`banned_lab_terms.txt`](./banned_lab_terms.txt) |
| 13 | `--dim 13` | [`borrowed_cred_terms.txt`](./borrowed_cred_terms.txt) |
| 14 | `--dim 14` | Bind Room price cents / label only in `gate/commerce/ladder.json` |

Prove each gate catches a break:

```bash
python scripts/scorecard_gates/run_gates.py --prove-fail 11
python scripts/scorecard_gates/run_gates.py --prove-fail 12
python scripts/scorecard_gates/run_gates.py --prove-fail 13
python scripts/scorecard_gates/run_gates.py --prove-fail 14
```

CI workflow: `.github/workflows/zero-tolerance-gates.yml`
