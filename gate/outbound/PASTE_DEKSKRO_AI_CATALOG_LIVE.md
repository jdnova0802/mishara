# PASTE — Tell dekskro: make ai-catalog.json alias LIVE

**27 Sep 2026.** Ops only. Closes Claude’s last loose thread on ARD path.

---

## Message (copy below the line)

---

Make live — `/.well-known/ai-catalog.json` (same body as `ard.json`)

**PR:** https://github.com/jdnova0802/mishara/pull/153  
**Why:** ARD v0.91 normative path is `ard.json` (already live). Google announcement + specification.website still name `ai-catalog.json`. Prod currently **404** on that path — confirmed by live curl just now. Alias, not rename. No new env vars.

### Deploy

1. Mark PR **#153** ready for review (undraft) if needed, then **merge into `main`**.
2. Confirm Render **gate-api** (`srv-dai3n0u1egvs73dbd94g`) auto-deploys from `main`. If not → Manual Deploy → latest commit.
3. **No new env vars.**

### Verify (MUST run after deploy green — do not skip)

```bash
curl -sS -o /tmp/ard.json -w 'ard:%{http_code}\n' https://gate.velaru.xyz/.well-known/ard.json
curl -sS -o /tmp/ai-catalog.json -w 'cat:%{http_code}\n' https://gate.velaru.xyz/.well-known/ai-catalog.json
python3 - <<'PY'
import json
a=json.load(open("/tmp/ard.json"))
b=json.load(open("/tmp/ai-catalog.json"))
print(a.get("spec"), len(a.get("entries",[])), "equal", a==b)
assert a.get("spec")=="ard-v0.91" and len(a["entries"])==3 and a==b
print("PASS")
PY
curl -sS https://gate.velaru.xyz/.well-known/gate.json \
  | python3 -c "import sys,json; g=json.load(sys.stdin); print(g.get('ard')); print(g.get('ai_catalog'))"
```

Expect:
- `ard:200` / `cat:200`
- `ard-v0.91 3 equal True` then `PASS`
- both gate.json links under `https://gate.velaru.xyz/.well-known/…`

**Done when:** that script prints `PASS` on production. Until then do **not** mark fully done.

### Optional after PASS

```bash
curl -sS -X POST https://neuronto.com/submit \
  -H 'content-type: application/json' \
  -d '{"domain":"gate.velaru.xyz"}'
```

### Honesty

- Pre-merge prod check (27 Sep): `ai-catalog.json` = **404**; `ard.json` = 200. Gap was real.
- Neuronto listing already real via `ard.json`: https://neuronto.com/ard-publishers/gate.velaru.xyz

---

## File refs

- Cite pastable: `gate/outbound/PASTE_CLAUDE_ARD_PATH_CHECK.md`
- Code: `gate/app.py` (`well_known_ai_catalog`), tests in `gate/test_listings.py`
