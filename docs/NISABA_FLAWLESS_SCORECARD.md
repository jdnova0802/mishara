# Nisaba — Flawless Scorecard

**Run date:** 2026-09-12 (post–Claude gate on PR #50)  
**Gate branch:** `cursor/price-ssot-purge-25ad` (stacks on `cursor/oligarch-grade-25ad` / PR #50)  
**Velaru:** `main` @ `97d7fe6` (settlement route rename)  
**Live:** `https://gate.velaru.xyz` · `https://mishara.onrender.com` · `https://velaru.xyz`

**Honest posture:** PR #50 (nav/CTA SSOT + `/pattern`) is mergeable on evidence. **No portfolio “8.”** Dim 14 is not closed until the residual hardcode list is empty and re-verified. Dims 8/11/12/16/19 need fresh measured runs — see `docs/VERIFICATION_QUEUE.md`.

## Dim 1 — Visual / design — PASS (Gate + Mishara)

| Check | Result | Evidence |
|---|---|---|
| Shared tokens | PASS | `gate/static/nisaba-tokens.css` committed; Gate + Mishara consume aligned ink/teal/paper vocabulary |
| OG tags | PASS | Gate base templates ship `og:title` / `og:image` (`og-gate.png`). Mishara legal/home meta present |
| Viewport | PASS | Present on Gate / Mishara / Velaru homes |
| Designed 404 | PASS | Gate designed 404; Mishara `@app.errorhandler(404)` with nav |
| a11y | PASS (measured) | Lighthouse artifacts in `docs/cwv/`; Gate muted contrast + link underlines hardened in `style.css`; Mishara home a11y **1.00** |

---

## Dim 2 — Copy / voice — PARTIAL / BLOCKED

| Check | Result | Evidence |
|---|---|---|
| Gate ladder one voice | PASS | `gate/commerce/ladder.json` + `/.well-known/commerce.json` live |
| Velaru Instant ↔ Pricing | **BLOCKED** | Instant still shows `$25`/`$49`; Pricing fork — Velaru private repo |
| Erra SKUs | BLOCKED | Lives in Velaru deploy |

---

## Dim 3 — Discoverability / IA — PASS (Gate + Mishara)

| Check | Result | Evidence |
|---|---|---|
| sitemap / llms / well-known | PASS | Gate live; Mishara llms lists `/privacy` + `/terms` |
| Nav/footer legal | PASS | Gate privacy/terms footered; Mishara privacy/terms **200** live |
| Law doors | PASS | `/subject` `/right-to-act` `/mandate` `/sinks` 200 + manifests |

---

## Dim 4 — Technical correctness — PASS

| Check | Result | Evidence |
|---|---|---|
| OpenAPI fail-closed x402 | PASS | `/api/x402/wire` **omitted** from OpenAPI when payto unset (`openapi_discovery.py` + CI assert) |
| Fail-closed suite in CI | PASS | `.github/workflows/gate.yml` commerce + listings + jargon/borrowed-cred greps |
| Schema drift guard | PASS | CI step builds OpenAPI with `payto=None` and asserts wire absent |

---

## Dim 5 — Commercial consistency — PASS (Gate) / BLOCKED (Velaru)

| Check | Result | Evidence |
|---|---|---|
| One public Gate ladder | PASS | Bind Room `$1,750` → Operator `$25,000` + `$5,000/mo` + `10 bps` in commerce SSOT + live commerce.json |
| Fee schedule SSOT | PASS | `ladder.json` `fee_schedule` holds hop `$0.10` + carry `+5 bps` (no stranger fork) |
| x402 unpublished when dark | PASS | OpenAPI + x402 well-known offline posture |
| Velaru Instant SKUs | **BLOCKED** | Needs Velaru edit |

---

## Dim 6 — Legal / IP — PASS (Gate + Mishara + Velaru)

| Check | Result | Evidence |
|---|---|---|
| Patent string | PASS | `Patent application No. 64/124,027` in entities + footers |
| Entity | PASS | Nisaba LLC |
| Gate privacy/terms | PASS | **200** live |
| Mishara privacy/terms | PASS | **200** live after Render retarget |
| Velaru privacy/terms | **PASS** | Live **200** on `/privacy` + `/terms` |

---

## Dim 7 — Security — PASS (Gate + Mishara) / PARTIAL (Velaru)

| Check | Result | Evidence |
|---|---|---|
| HSTS + CSP | PASS | Gate + Mishara response headers live |
| security.txt | PASS | Gate `/.well-known/security.txt` **200**; Mishara route shipped (redeploy this commit) |
| Velaru CSP / security.txt | PARTIAL/FAIL | HSTS yes; CSP/security.txt still missing — BLOCKED |

---

## Dim 8 — Performance — RE-VERIFY QUEUED

Prior `docs/cwv/` artifacts exist but are **not** accepted as closing this turn. Fresh Lighthouse/CWV required — `docs/VERIFICATION_QUEUE.md`.

---

## Dim 9 — SEO / machine-readability — PASS (Gate + Mishara)

robots / sitemap / llms / commerce / gate.json live and consistent on Gate; Mishara discovery + legal in llms.

---

## Dim 10 — Testing / regression — PASS

Gate workflow: commerce + listings + DTCC/SWIFT ban + lab-jargon ban + dead `erra.onrender.com` ban + OpenAPI fail-closed assert + optional live manifest crawl.

---

## Dim 11 — Link liveness — RE-VERIFY QUEUED

Prior manifest crawler PASS is stale for this close. Full-site link crawl required — `docs/VERIFICATION_QUEUE.md`.

---

## Dim 12 — Institutional tone — RE-VERIFY QUEUED

CI greps remain; full stranger-HTML re-grep still queued this close — `docs/VERIFICATION_QUEUE.md`.

---

## Dim 13 — No borrowed credibility — PASS (route rename live)

| Check | Result | Evidence |
|---|---|---|
| Gate stranger chrome | PASS | No DTCC/SWIFT (CI) |
| Velaru OpenAPI / catalog | **PASS** | Live OpenAPI has **0** `/api/v1/dtcc/*` paths; catalog has no `dtcc` |
| Velaru canonical attest | **PASS** | `GET /api/v1/settlement/attest` **200** |
| Legacy path | **308 only** | `GET /api/v1/dtcc/attest` → `Location: /api/v1/settlement/attest` (silent relocate; not advertised) |

---

## Dim 14 — Single source of truth — IN PROGRESS (residual purge)

`ladder.json` + `commerce.py` + live `commerce.json` are the spine. Residual hand-typed `$1,750` purge is this branch (`cursor/price-ssot-purge-25ad`). **Do not mark Dim 14 PASS until residual list is empty and `test_residual_bind_room_price_not_hand_typed` is green on main.**

---

## Dim 15 — Copyedit — PASS (Gate ladder)

Gate ladder/labels normalized via SSOT. Velaru Instant/Pricing copyedit BLOCKED.

---

## Dim 16 — Measured performance — RE-VERIFY QUEUED

Same as Dim 8 — fresh CWV run required this close.

---

## Dim 17 — Security posture visible — PASS (Gate + Mishara + Velaru)

Gate + Mishara + Velaru `/.well-known/security.txt` live **200**.

---

## Dim 18 — Legal/corporate transparency — PASS (support) / PARTIAL (address)

| Check | Result | Evidence |
|---|---|---|
| Nisaba LLC | PASS | Consistent |
| Support SLA | PASS | One business day (US Eastern) on Gate + Mishara legal |
| Registered address | PARTIAL | Not published — **founder supply once** |

---

## Dim 19 — 10-second stranger test — UNVERIFIED (human timer required)

Protocol: `docs/STRANGER_TEST_DIM19.md`. Cold human, stopwatch, homepage + `/bind-room` + one `/for/*`. Engineering bar is not a substitute.

---

## Dim 20 — Claims earn inline proof — PASS

Bind Room / trust surfaces link verify + manifests; commerce.json + gate.json advertise proof doors.

---

## Dim 21 — Email/outbound integrity — PARTIAL

SPF present; DMARC still `p=none`. **FOUNDER/DNS** to enforce. Not a Gate code blocker.

---

## Dim 22 — Idempotency / abuse protection — PASS

| Check | Result | Evidence |
|---|---|---|
| RateLimit headers | PASS | `rate_limited_response()` emits `Retry-After` + `RateLimit-*` on 429s |
| Idempotency | PASS | Operator weld checkout `Idempotency-Key` + SQLite |

---

## Dim 23 — Accountability trail — PASS

Support email + SLA + operator accountability string in entities / legal / footer.

---

## Dim 24 — API versioning / deprecation — PASS

`api_policy` in entities + injected into `/.well-known/gate.json` + commerce.json.

---

## Priority queue (remaining)

1. **Merge PR #50** (nav/CTA SSOT + `/pattern`) — evidenced; Dim 13 route catch cleared on Velaru live.
2. **Land price SSOT purge** (`cursor/price-ssot-purge-25ad`) — empty residual hardcode list → then re-score Dim 14.
3. **Measured re-verify:** Dim 8/16 CWV, Dim 11 link crawl, Dim 12 jargon grep, Dim 19 human stranger test — `docs/VERIFICATION_QUEUE.md`.
4. **FOUNDER only (do not touch in agent):** mailing address (Dim 18), DMARC enforce (Dim 21).
5. **Velaru Instant SKU copy** still BLOCKED if Instant `$25`/`$49` fork remains.

---

## Live verify (Gate + Mishara)

```bash
curl -sI https://gate.velaru.xyz/pricing | head -1
curl -s https://gate.velaru.xyz/.well-known/commerce.json | head -c 200
curl -sI https://gate.velaru.xyz/.well-known/security.txt | head -1
curl -sI https://mishara.onrender.com/privacy | head -1
curl -sI https://mishara.onrender.com/terms | head -1
# After this deploy:
curl -sI https://mishara.onrender.com/.well-known/security.txt | head -1
```

**Desktop paste for Velaru (unchanged mission):** open private Velaru → fix Dim 13/2/5/6/7/17 + Erra `/health` → then rewrite those rows to PASS.
