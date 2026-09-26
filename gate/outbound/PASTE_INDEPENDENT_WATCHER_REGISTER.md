# PASTE — Independent watcher self-register (build, not a SKU)

**26 Sep 2026.** Door for condition 2. Gate does not recruit; outsiders show up.

---

## What shipped

| Piece | Path |
|-------|------|
| Module | `gate/independent_watch.py` |
| Register | `POST /v1/evidence-watch/register` (GET = manifest) |
| Roster | `/.well-known/evidence-watch.json` → `independent_watchers` from DB |
| Script | `watch_evidence_head.py --register --handle NAME` |

Rules:
- Must match **live** `tree_size` + `root_hash` at submit time (proves fetch)
- No API key, no partner desk, `paid_by_gate: false`
- Fresh for **14 days**; re-POST to refresh or drop from roster
- Optional Ed25519 bind of handle → key for later refreshes

---

## How a stranger joins (unpaid)

```bash
python3 gate/watch_evidence_head.py \
  --url https://gate.velaru.xyz \
  --register --handle your-handle \
  --homepage https://your.site/watch-note
```

Or:

```bash
HEAD=$(curl -sS https://gate.velaru.xyz/.well-known/evidence-head.json)
curl -sS -X POST https://gate.velaru.xyz/v1/evidence-watch/register \
  -H 'content-type: application/json' \
  -d "$(python3 - <<'PY'
import json,os,urllib.request
h=json.load(urllib.request.urlopen('https://gate.velaru.xyz/.well-known/evidence-head.json'))
print(json.dumps({
  'handle':'your-handle',
  'tree_size':h['tree_size'],
  'root_hash':h['root_hash'],
}))
PY
)"
```

---

## Honesty

This does **not** create an independent watcher. It removes the excuse that there was no door. Roster stays empty until someone outside Gate runs the cron.

First-party `gate-watch.yml` still does not count.
