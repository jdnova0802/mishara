# Ops Guards — foothill automation

**Not doctrine.** Auto checks that protect strongest-start honesty.

```bash
python3 -m gate.ops_guards          # local: patent, stripe, lint, gate1
python3 -m gate.ops_guards --live   # + curl prod HTML for stale copy
```

| Guard | What |
|-------|------|
| **patent** | Days to non-provisional (`GATE_PATENT_FILED_AT` / `GATE_PATENT_DEADLINE_AT`) |
| **stripe** | Bind Room price ID present |
| **buyer_lint** | Local templates: Bind Room lead, no “Two artifacts” |
| **gate1** | Paid stranger artifact count |
| **last_proved** | Feeds Promo Clock from latest bind event |
| **live_smoke** | Prod HTML ≠ stale hero / Aug 18 drill (`--live` or `GATE_OPS_LIVE_SMOKE=1`) |

Also on:
- `GET /health` → `guards`
- `GET /.well-known/ops-guards.json`
- `GET /.well-known/gate1.json`
- Promo Clock auto last-proved when env unset

Exit codes: `0` ok · `1` warn · `2` fail
