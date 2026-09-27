# PASTE — Tell dekskro: make ARD discovery LIVE

**27 Sep 2026.** Ops only. No new SKU. No new secrets. Last inbound discovery mile — not another mouth.

---

## Message (copy below the line)

---

Make live — Agentic Resource Discovery (`/.well-known/ard.json`)

**PR:** https://github.com/jdnova0802/mishara/pull/151  
**What:** Publish ARD v0.91 at `/.well-known/ard.json` so agent registries can crawl Gate (MCP + x402 + prefinality) without email outreach. Linked from `gate.json`, sitemap, OpenAPI, `llms.txt`. No new env vars. No new mouths.

### Deploy

1. Mark PR **#151** ready for review (undraft) if needed, then **merge into `main`**.
2. Confirm Render **gate-api** (`srv-dai3n0u1egvs73dbd94g`) auto-deploys from `main`. If not → Manual Deploy → latest commit.
3. **No new env vars.** `GATE_PUBLIC_URL` stays `https://gate.velaru.xyz`. Custom domain already attached — do **not** buy another domain.

### Verify (after deploy green)

```bash
curl -sS https://gate.velaru.xyz/.well-known/ard.json \
  | python3 -c "import sys,json; m=json.load(sys.stdin); print(m['spec'], m['publisher']); print(len(m['entries'])); print([e['identifier'].split(':')[-1] for e in m['entries']])"
```

Expect:
- `ard-v0.91 https://gate.velaru.xyz`
- `3`
- identifiers end with `gate-api`, `x402`, `prefinality`

```bash
curl -sS https://gate.velaru.xyz/.well-known/gate.json \
  | python3 -c "import sys,json; g=json.load(sys.stdin); print(g.get('ard')); print(g.get('mcp_discovery')); print(g.get('x402'))"
```

Expect all three URLs under `https://gate.velaru.xyz/.well-known/…`

```bash
# Entries resolve (200)
for p in mcp.json x402.json prefinality.json; do
  code=$(curl -sS -o /dev/null -w '%{http_code}' "https://gate.velaru.xyz/.well-known/$p")
  echo "$p $code"
done
```

Expect: `200` for each.

```bash
curl -sS https://gate.velaru.xyz/sitemap.xml | grep -o 'ard\.json' | head -1
curl -sS https://gate.velaru.xyz/llms.txt | grep -i ard | head -2
```

Expect: sitemap mentions `ard.json`; llms.txt has an ARD line.

**Done when:** `ard.json` returns `spec: ard-v0.91` with 3 entries, and each entry URL returns 200.

### After green (human / optional — not Render)

1. Submit `https://gate.velaru.xyz` (or `/.well-known/ard.json`) to neuronto / MCP registry / Smithery.
2. Paste `https://gate.velaru.xyz/operator` to **one** licensed payout/carrier human.

### Honesty

- Discovery only — does **not** invent a new clearance SKU.
- Does **not** claim registry listing until submitted.
- Does **not** move money; crawlers get manifests, not welds.
- `their_production` stays false until a recorded third-party production weld.

### Not this deploy

- npm / PyPI publish of `gate/sdk` — separate
- Fiserv / Jack Henry / FedNow Showcase — marketplace GTM later
- OTS Bitcoin well-known (#137) — separate; needs `GATE_OTS_DIR` + stamp cron

---

## File refs

- Code: `gate/listings.py` (`ard_manifest`), route in `gate/app.py`
- Ops note: `gate/VISIBILITY.md`
- Tests: `gate/test_listings.py` (`test_ard_manifest_*`, `test_well_known_ard_route`)
