# PASTE — Tell Claude: ARD + Neuronto DONE (status)

**27 Sep 2026.** Status only. No new code. No new SKU. Agent-inbound path is live and indexed.

---

## Message (copy below the line)

---

Status — Agentic Resource Discovery is LIVE and indexed on Neuronto

### What we built

**PR #151** (merged `938066f` → `main`):
- Shipped `/.well-known/ard.json` (ARD v0.91) — Agentic Resource Discovery manifest
- Three entries: MCP (`gate-api`), x402 catalog, prefinality mouth
- Wired into `gate.json`, sitemap, OpenAPI, `llms.txt`, `PUBLIC_WELLKNOWN`
- Ops note in `VISIBILITY.md`: leftover work is seats/ops, not more product mouths
- Dekskro live pastable: `gate/outbound/PASTE_DEKSKRO_ARD_LIVE.md`
- No new env vars. No new domain. No new clearance SKU.

### Deploy (done)

- PR #151 undrafted + merged to `main`
- Render **gate-api** (`srv-dai3n0u1egvs73dbd94g`) auto-deployed — `dep-das95ou7bikc73a077m0` live
- Public URL unchanged: `https://gate.velaru.xyz`

### Verify (all green)

```
ard-v0.91 https://gate.velaru.xyz
3 entries: gate-api, x402, prefinality
gate.json → ard.json, mcp.json, x402.json
mcp.json / x402.json / prefinality.json → 200
sitemap includes ard.json; llms.txt has ARD line
```

Live:
- https://gate.velaru.xyz/.well-known/ard.json
- https://gate.velaru.xyz/.well-known/gate.json

### Neuronto (done)

Submitted domain `gate.velaru.xyz` → **indexed** (fetched live ARD from domain).

- status: `indexed`
- manifest: `/.well-known/ard.json`
- resources_indexed: **3**
- publisher page: https://neuronto.com/ard-publishers/gate.velaru.xyz
- first submit status: https://neuronto.com/submit/status/bd114e1f13e2
- badge offered — **not** added to repo (optional; skip)

Analytics check (Neuronto preview):
- Registry answers that include Gate: **4 of 30**
- Best registry position: **#1** (on Neuronto for representative queries)
- Open-web searches that include Gate: **0 of 5** (expected — not Google SEO)

### Honesty

- Discovery only — **not** a new clearance SKU
- Indexing ≠ trust/safety rating
- Does **not** claim registry listing until submitted (Neuronto = submitted+indexed; Smithery / official MCP Registry = **not** done)
- Does **not** move money
- `their_production` stays **false** until a recorded third-party production weld
- Agent inbound ≠ carrier seat. Neuronto finds agents. Licensed humans still need a separate outbound touch (diligence paste), and that is **not** this deploy

### Not this work (still open, human)

| Item | Status |
|------|--------|
| Smithery (`https://smithery.ai/new` → `https://gate.velaru.xyz/mcp`) | optional, not done |
| Official MCP Registry (`mcp-publisher`) | optional, not done |
| Diligence outbound (Monday paste — named desks) | human email; separate from agent discovery |
| npm / PyPI `gate/sdk` | not done |
| Fiserv / Jack Henry / FedNow Showcase | marketplace GTM later |
| #137 OTS Bitcoin well-known | separate; needs `GATE_OTS_DIR` + stamp cron |

### Bottom line for Claude

**Agent-inbound discovery path is complete:** ARD live on prod + Neuronto indexed #1 on own queries. Do **not** rebuild mouths or re-ship ARD. Do **not** treat Neuronto as a carrier CRM. Next product code: none required for this path. Next human move (if any): one diligence email from `PASTE_MONDAY_DILIGENCE_EMAILS.md`, or leave seats cold.

---

## File refs

- Code: `gate/listings.py` (`ard_manifest`), `gate/app.py`, `gate/VISIBILITY.md`
- Live pastable (already executed): `gate/outbound/PASTE_DEKSKRO_ARD_LIVE.md`
- Diligence (separate human path): `gate/outbound/PASTE_MONDAY_DILIGENCE_EMAILS.md`
