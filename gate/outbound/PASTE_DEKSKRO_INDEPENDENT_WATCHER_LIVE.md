# PASTE — Tell dekskro: make independent watcher register LIVE

**26 Sep 2026.** Ops only. No new SKU. No new secrets.

---

## Message (copy below the line)

---

Make live — independent watcher self-register

**PR:** https://github.com/jdnova0802/mishara/pull/140  
**What:** `POST /v1/evidence-watch/register` — outsiders match live evidence-head and appear on `independent_watchers`. No API key. No partner desk. 14-day freshness.

### Deploy

1. Merge PR **#140** into `main`.
2. Confirm Render **gate-api** (`srv-dai3n0u1egvs73dbd94g`) auto-deploys from `main`. If not → Manual Deploy → latest commit.
3. **No new env vars.** Uses existing sqlite disk.

### Verify (after deploy green)

```bash
curl -sS https://gate.velaru.xyz/.well-known/evidence-watch.json | python3 -m json.tool | head -40
```

Expect:
- `"register": "https://gate.velaru.xyz/v1/evidence-watch/register"` (or same path)
- `"independent_watchers": []` until someone registers — empty is correct

```bash
curl -sS https://gate.velaru.xyz/v1/evidence-watch/register | python3 -m json.tool | head -30
```

Smoke register:

```bash
python3 - <<'PY'
import json, urllib.request
from datetime import datetime, timezone
origin = "https://gate.velaru.xyz"
h = json.load(urllib.request.urlopen(origin + "/.well-known/evidence-head.json"))
body = json.dumps({
    "handle": "dekskro-smoke",
    "tree_size": h["tree_size"],
    "root_hash": h["root_hash"],
    "sampled_at": datetime.now(timezone.utc).isoformat(),
    "note": "deploy smoke — unpaid",
}).encode()
req = urllib.request.Request(
    origin + "/v1/evidence-watch/register",
    data=body,
    headers={"Content-Type": "application/json"},
    method="POST",
)
print(urllib.request.urlopen(req).read().decode())
PY
```

```bash
curl -sS https://gate.velaru.xyz/.well-known/evidence-watch.json \
  | python3 -c "import sys,json; w=json.load(sys.stdin); print([x['handle'] for x in w.get('independent_watchers') or []])"
```

**Done when:** register returns `"ok": true` and `dekskro-smoke` is on the roster.

### Honesty

This does not create a real independent watcher. It opens the door. First-party `gate-watch.yml` still does not count.

### Optional (not this deploy)

PR **#137** (OTS Bitcoin anchor) — separate merge; needs writable `GATE_OTS_DIR` + stamp/upgrade cron. Do after #140 is live if you want it.

---

## File refs

- Code: `gate/independent_watch.py`, `POST /v1/evidence-watch/register`
- Script: `python3 gate/watch_evidence_head.py --register --handle NAME`
- Detail: `gate/outbound/PASTE_INDEPENDENT_WATCHER_REGISTER.md`
