# Nisaba — Flawless Scorecard

**Run date:** 2026-09-12 (UTC)  
**Commit audited:** `1e8fbd4` (`cursor/right-to-act-no-go-c1dd`)  
**Surfaces probed live:** `https://gate.velaru.xyz`, `https://velaru.xyz`, `https://mishara.onrender.com`, `https://erra-jf6a.onrender.com`  
**Prior run:** none found in repo — this is the baseline. Diff = N/A (first stamp).

**Method:** live HTTP crawl + repo grep. Audit only — no product fixes in this run.

**Legend:** PASS · PARTIAL · FAIL · DECISION (founder call before code)

---

## Dim 1 — Visual / design — FAIL

| Check | Result | Evidence |
|---|---|---|
| Shared design system across Gate / Velaru / Mishara | FAIL | Gate CSS tokens (`--bg`, `--ink`, …) ≠ Velaru industrial tokens (`--ind-steel`, Space Grotesk / JetBrains Mono). Mishara has no shared token file reachable at `/static/style.css` (404). |
| OG tags for link previews | FAIL | `gate.velaru.xyz/`, `/pricing`, `/bind-room`: `og:title` / `og:image` absent. Same on `velaru.xyz/` and Mishara home. (Some Gate templates like `scanner.html` have OG locally; primary money pages do not.) |
| Mobile viewport | PASS | `viewport` meta present on Gate / Velaru / Mishara homes + pricing. |
| Loading / error states | FAIL | Custom 404s are bare Flask defaults (~160–207 bytes, no nav): e.g. `gate.velaru.xyz/no-such-page-xyz`. |
| a11y (contrast / alt / keyboard) | PARTIAL | Homes have 0 `<img>` so alt N/A; contrast / keyboard not measured this run (no axe/Lighthouse log). |

**Fix type:** mostly engineering. Shared token package is a design decision (who owns the system).

---

## Dim 2 — Copy / voice consistency — FAIL

| Check | Result | Evidence |
|---|---|---|
| One locked pricing ladder everywhere | FAIL | **Gate** `/pricing` + `llms.txt`: Bind Room `$1,750` → Operator `$25,000` + `$5,000/mo` + `10 bps`. **Velaru** `/pricing`: `$149` HOLD / `$249/mo` Monitor. **Velaru** `/instant` + `llms.txt`: also `$25` / `$49` (absent from `/pricing`). **Erra** `/erra/start`: `$7.5k`–`$9.5k` / `$125k` enterprise. **Mishara**: `$99` / `$499`. Cross-brand is fine if intentional; Instant vs Pricing is a same-brand fork. |
| One doctrine line per brand | PARTIAL | Gate `brand_map.py` + `/nisaba` hold roles; live Velaru/Erra chrome does not always pull the same sentences. |
| Do-not-mention list | DECISION | No checked-in do-not-mention list found in this repo; cannot score compliance without the list. |
| Tone (terse / calm / adult) | PARTIAL | Gate buyer chrome is mostly sober; Velaru Instant footer still uses institution-name bait (see Dim 13). |

**Fix type:** Instant↔Pricing = engineering once ladder is decided. Do-not-mention list = founder decision.

---

## Dim 3 — Discoverability / IA — PARTIAL

| Check | Result | Evidence |
|---|---|---|
| sitemap / llms / well-known agree | PARTIAL | Gate has all three live. `/subject`, `/right-to-act`, `/mandate`, `/sinks` appear in `llms.txt`, `sitemap.xml`, and `gate.json` and return **200** (prior “missing four” finding is stale). |
| Orphan risk | PARTIAL | Gate law pages linked from each other; Erra deep SKUs less consistently mapped from Velaru `llms.txt`. |
| Consistent nav/footer | PARTIAL | Gate `/` nav ≠ law-page nav (law pages add `/admittance`, `/finder`, `/physical`; home does not). Velaru has no Privacy/Terms footer links (404). Mishara footer claims Privacy/Terms but those URLs 404. |

**Fix type:** engineering.

---

## Dim 4 — Technical correctness — PARTIAL

| Check | Result | Evidence |
|---|---|---|
| OpenAPI covers live endpoints | PARTIAL | Live `openapi.json` has 45 paths; POST subject/mandate/sinks routes respond (400 validation, not 404). Not proven exhaustive vs every Flask route. |
| Schema matches responses | UNMEASURED | No automated schema-drift job in CI. |
| Fail-closed tested | PARTIAL | Live smokes: empty `POST /v1/right-to-act/evaluate` → `NONEXIST`-class halt; empty PAS bind-check → `bind_allowed:false`. Gate unit tests exist in-repo; **CI workflow only runs Mishara** (`.github/workflows/mishara.yml`), not Gate fail-closed suite. |
| Durable state | PARTIAL | Live `/health` reports durable DB path (not ephemeral). Idempotency table exists in `gate/db.py`. Mandate deaths / finder / signing-key durability not fully proven this run. |

**Fix type:** engineering (CI + schema drift checks).

---

## Dim 5 — Commercial consistency — FAIL

| Check | Result | Evidence |
|---|---|---|
| One buy ladder on every surface that states prices | FAIL | See Dim 2 Instant `$25`/`$49` vs Pricing omission; Gate operator page also surfaces `$0.10/hop`, `$500`, `5 bps` alongside the public ladder. |
| Advertised rails work or are unpublished | PARTIAL | `gate.json` links `x402`; `/.well-known/x402.json` says USDC rail advertised only when payto configured — honest JSON — but OpenAPI still documents `/api/x402/wire` with a `$497` price field while payto is unset. |

**Fix type:** founder decision on Instant SKUs; engineering to unpublish x402 paths when unconfigured.

---

## Dim 6 — Legal / IP — FAIL

| Check | Result | Evidence |
|---|---|---|
| Patent / entity identical everywhere | FAIL | Velaru home/llms: `Patent #64/124,027`. Gate home fragment/patent citation not the same string set. Entity string **Nisaba LLC** is consistent on probed pages. |
| Privacy / Terms present + footered | FAIL | Gate: `/privacy` + `/terms` **200**, footered. Velaru: `/privacy` + `/terms` **404**. Mishara: footer links Privacy/Terms but URLs **404**. |
| No unearned “production / certified” claims | PARTIAL | Gate health/dev flags look honest (`dev_mode:false`). Not a full claim audit. |

**Fix type:** engineering for missing legal pages; founder confirm patent string SSOT.

---

## Dim 7 — Security — FAIL

| Check | Result | Evidence |
|---|---|---|
| No secrets in client responses | PASS (spot) | No key material seen in probed HTML/JSON this run. |
| HTTPS / no mixed content | PASS (spot) | HTTPS everywhere probed. |
| Custom domain ↔ Render host sync | PASS | `gate.velaru.xyz` vs `gate-api-vsq8.onrender.com` `/pricing`, `gate.json`, `llms.txt` byte-equal after host rewrite. |
| HSTS / CSP / security.txt | FAIL | Gate + Mishara: no `Strict-Transport-Security`, no CSP, `/.well-known/security.txt` **404**. Velaru: HSTS + `X-Frame-Options` present; still no CSP / security.txt. |

**Fix type:** engineering.

---

## Dim 8 — Performance — PARTIAL

| Check | Result | Evidence |
|---|---|---|
| Measured page/API latency | PARTIAL | Rough RTT from audit host: Gate `/` ~38ms, `/health` ~165ms, `right-to-act/evaluate` ~69ms; Velaru `/` ~185ms. **Not** Core Web Vitals (LCP/CLS/INP). |
| Health that means something | PARTIAL | Gate `/health` is rich JSON (not unconditional ok). Erra `/health` still **500**; probe correctly on `/healthz`. No evidence of paging/alerting on failure. |

**Fix type:** engineering to wire CWV + alerts; Erra `/health` fix needs Velaru repo access.

---

## Dim 9 — SEO / machine-readability — PARTIAL

| Check | Result | Evidence |
|---|---|---|
| robots / sitemap / llms | PASS (Gate, Velaru, Mishara) | All three return 200 on each brand home host probed. |
| Mutual consistency | PARTIAL | Gate strong; Instant SKUs in Velaru `llms.txt` not on `/pricing` (content fork). |
| schema.org | PARTIAL | Gate `/` and `/pricing` include JSON-LD. Velaru `/` and `/pricing` do not. |

**Fix type:** engineering.

---

## Dim 10 — Testing / regression — FAIL

| Check | Result | Evidence |
|---|---|---|
| Broken-link / 404 / schema-drift / fail-closed in CI | FAIL | Only `.github/workflows/mishara.yml` (Mishara unit tests). No Gate deploy CI, no link checker, no OpenAPI drift job. |

**Fix type:** engineering.

---

## Dim 11 — Zero-tolerance link liveness — PARTIAL (improved vs prior Claude note)

| Check | Result | Evidence |
|---|---|---|
| Manifest URLs resolve | PARTIAL | Crawl of ~160 Gate manifest URLs: **128 × 200**, **25 × non-200** (mostly **405** on POST-only paths when GETted — acceptable), **1 error** (`https://erra.onrender.com` — dead host still referenced somewhere), plus template skips. |
| Four pages `/subject` `/right-to-act` `/mandate` `/sinks` | PASS (now) | All **200** on Gate and listed in llms/sitemap/gate.json. Prior “confirmed missing” is **obsolete**. |
| Recurring CI link check | FAIL | None. |

**Fix type:** engineering — scrub dead `erra.onrender.com`; add CI link verifier that uses correct methods.

---

## Dim 12 — Institutional tone (no lab jargon in stranger-visible API/UI) — PASS (live Gate)

| Check | Result | Evidence |
|---|---|---|
| Lab enums in live OpenAPI / pages | PASS | Grep of live `openapi.json` + key Gate/Velaru pages: **0** hits for `HAUNTED`, `CHOKE`, `ghost-bind`, `stick-meter`, `charge-bride`, `hop-tattoo`, `soft-yes-snare`. Live right-to-act vocabulary is `EXIST` / `NONEXIST` / `HOLD` (institutional). |
| Repo-internal commentary | N/A for stranger test | Internal modules may still use metaphor in comments; not stranger-visible if not rendered. |

**Note:** Claude’s earlier enum complaint does **not** match current live Gate contract. Keep the grep in CI so it cannot regress.

**Fix type:** none for live Gate; add CI greps.

---

## Dim 13 — No borrowed credibility — FAIL (zero-tolerance)

| Check | Result | Evidence |
|---|---|---|
| Real institution names on stranger surfaces | FAIL | `https://velaru.xyz/instant` footer link text **“DTCC integration”** → `/dtcc`. Page title is **“NAIC Exhibit D Decision-Point Pack”** — using DTCC as the link label borrows clearinghouse gravitas. `/dtcc` and `/enterprise` also mention **NAIC** (regulation cite vs endorsement — founder call, but DTCC-as-label is not a cite). |
| Gate `/positioning` live HTML | PASS | No DTCC/SWIFT strings in rendered positioning HTML this run (module text may still exist in repo). |
| Fake seals / certification theater | PASS (spot) | None seen on probed pages. |

**Fix type:** **quick fix** — rename Instant footer link (e.g. “NAIC Exhibit D pack”) or remove. Broader institution-name policy = founder decision.

---

## Dim 14 — Single source of truth — FAIL (highest-leverage architecture)

**Current state (hand-typed prices in multiple places):**

- `gate/app.py` env defaults: `GATE_BIND_ROOM_PRICE_LABEL=$1,750`, weld/floor via operator module
- `gate/operator_invoice.py`: `WELD_PRICE_LABEL="$25,000"`, `FLOOR_PRICE_LABEL="$5,000/mo"`
- `gate/bind_room.py`: `"price": "$1,750"`
- `gate/audiences.py`: repeated `$1,750` / `$25,000` strings per audience
- `gate/brand_map.py`: money notes as prose
- Velaru Instant / Pricing / Erra SKUs: **not in this repo** (private Velaru) — separate hand-typed surfaces

**Proposed SSOT (do not implement until approved):**

```
commerce/
  ladder.json      # every public price, id, stripe_price_id, bps, when_to_show
  doctrine.json    # one question + one sentence per brand
  entities.json    # legal name, patent string, support email, response SLA
  hosts.json       # canonical URLs + do_not_advertise
```

Rules:

1. HTML, `llms.txt`, `gate.json`, OpenAPI descriptions, outbound generators **import** these files — never retype.
2. CI fails if a `$` amount appears outside `commerce/` + generated artifacts.
3. Unconfigured rails (x402) are omitted by generator when `configured:false`.

**Fix type:** DECISION on schema ownership, then engineering.

---

## Dim 15 — Copyedit — PARTIAL

Not a full human copyedit. Automated inconsistencies found: `$249 /mo` vs `$249/mo`; Erra `$8.5k` vs `$8500`; Instant SKUs missing from Pricing. Product-name capitalization not fully audited.

**Fix type:** engineering + short human pass.

---

## Dim 16 — Measured performance (CWV) — FAIL

No LCP/CLS/INP logs in repo or CI. Only rough server RTT above.

**Fix type:** engineering (Lighthouse CI / CrUX).

---

## Dim 17 — Security posture visible — FAIL

No `/.well-known/security.txt` on Gate, Velaru, or Mishara. No CSP on Gate. TLS org / cert subject not inspected beyond HTTPS working.

**Fix type:** engineering; cert org display may need custom cert (founder/DNS).

---

## Dim 18 — Legal/corporate transparency — PARTIAL

| Check | Result | Evidence |
|---|---|---|
| “Nisaba LLC” consistency | PASS (probed) | Gate / Velaru / Mishara footers. |
| Registered address | FAIL | Not found on Gate privacy/terms skim this run. |
| Support contact + response expectation | PARTIAL | `hello@velaru.xyz` on Gate terms/privacy + Velaru/Mishara homes. **No stated response-time SLA** found. |

**Fix type:** founder supply address + SLA text; engineering to publish.

---

## Dim 19 — 10-second stranger test — DECISION / UNMEASURED

Not run with a zero-context human this session. Gate Bind Room headline is concrete dollars; Prefinality / Admittance vocabulary still dense on law pages. Needs a real stranger timer.

**Fix type:** founder process (recruit stranger); copy DECISION after.

---

## Dim 20 — Claims earn inline proof — PARTIAL

Gate Bind Room links officer-pack JSON + verify paths near the offer. Not every “fail-closed / stranger-verifiable” claim is adjacent to a curl/manifest on every page.

**Fix type:** engineering after claim inventory.

---

## Dim 21 — Email/outbound integrity — PARTIAL

| Check | Result | Evidence |
|---|---|---|
| SPF | PASS | `velaru.xyz` TXT: `v=spf1 include:zohomail.com ~all` |
| DMARC | PARTIAL | `_dmarc.velaru.xyz`: `p=none` (monitor only — not enforce) |
| DKIM | UNMEASURED | Selector records not fully enumerated this run. |

**Fix type:** founder/DNS to raise DMARC; verify DKIM selectors.

---

## Dim 22 — Idempotency / abuse protection — PARTIAL

| Check | Result | Evidence |
|---|---|---|
| Rate limit code | PARTIAL | `gate/app.py` returns `rate_limited` in several paths; no `RateLimit-*` headers observed on evaluate POSTs this run. |
| Idempotency | PARTIAL | Operator weld checkout uses `Idempotency-Key` + SQLite `idempotency_keys`. Not proven on every billable/clearance endpoint. |

**Fix type:** engineering to standardize.

---

## Dim 23 — Accountability trail — FAIL

`hello@velaru.xyz` present; **no** published response-time expectation; **no** named dispute contact on probed pages.

**Fix type:** founder decision (name + SLA), then engineering.

---

## Dim 24 — API versioning / deprecation — FAIL

Endpoints are `/v1/*` but no published deprecation / v2 policy page or manifest field found. `gate.json` has `version` only.

**Fix type:** founder decision on support window; engineering to publish.

---

## Scorecard meta

| Item | Status |
|---|---|
| Date-stamped | Yes — 2026-09-12, commit `1e8fbd4` |
| Diff vs prior | No prior run in repo |
| Dimension changelog | Dims 1–24 from Claude “Flawless” bar (2026-09-12). Dims 11–13 marked zero-tolerance per prompt. Dim 14 flagged highest-leverage architecture. |

---

## Diff vs baseline — institutional pass (founder: professionalism)

Founder answers to decisions 1–5: **institutional grade**. Implemented on Gate + Mishara in this branch:

| Area | Status |
|---|---|
| Dim 14 commerce SSOT | **DONE** — `gate/commerce/{ladder,doctrine,entities,hosts}.json` + `commerce.py`; `/.well-known/commerce.json` |
| Dim 1 OG + 404 | **DONE (Gate)** — OG/Twitter tags, `og-gate.png`, designed 404 |
| Dim 6 Mishara legal | **DONE** — `/privacy` + `/terms` live in Mishara app |
| Dim 7 / 17 security | **DONE (Gate + Mishara)** — HSTS, CSP, `/.well-known/security.txt` |
| Dim 18 / 23 / 24 | **DONE (Gate)** — patent string, support SLA, accountability, API deprecation in entities + footer |
| Dim 10 / 12 CI | **DONE** — `.github/workflows/gate.yml` runs commerce + listings + borrowed-cred / jargon greps |
| Dim 13 Gate buyer chrome | **DONE** — no DTCC/SWIFT on stranger templates (CI-enforced) |
| Shared design system | **OPEN** — Velaru private |
| Velaru Instant DTCC link / Instant↔Pricing fork / Velaru legal | **BLOCKED** — needs Velaru repo access |
| Erra `/health` 500 | **BLOCKED** — probe on `/healthz`; source fix needs Velaru repo |

---

## Priority queue (remaining)

1. **BLOCKED (Velaru repo):** Instant “DTCC integration” link; Instant `$25`/`$49` vs Pricing; Velaru Privacy/Terms; Erra `/health` crash.
2. **ENG:** Shared design tokens across Gate / Velaru / Mishara (Dim 1).
3. **ENG:** Full manifest link crawler in CI (Dim 11).
4. **FOUNDER:** Registered address for legal pages (Dim 18).
5. **FOUNDER/DNS:** Raise DMARC; CWV measurement (Dims 16, 21).

---

## What improved vs the conversation’s earlier Claude surface note

- `/subject`, `/right-to-act`, `/mandate`, `/sinks` are **live 200** and listed in manifests (no longer missing).
- Lab enums (`HAUNTED_CRITICAL`, `CHOKE`, …) are **not** in the live Gate OpenAPI contract.
- Erra dedicated host is up on `/healthz`; Gate brand map `/nisaba` documents host honesty.
- Gate/Mishara now ship commerce SSOT, OG, security.txt, HSTS/CSP, support SLA, patent string, and Gate CI.
