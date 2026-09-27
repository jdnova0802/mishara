# Nisaba Flawless Scorecard

Operator: **Nisaba LLC** · Patent application No. **64/124,027**  
Scope this pass: **Velaru-blocked dims only** (2 / 5 / 6 / 7 / 13 / 17 / 8-Erra).  
Proven live: **2026-09-12T03:18Z** against `velaru.xyz` and Render peers.  
Velaru ship: `jdnova0802/velaru` `main` @ `1e708c47a8f4264dd044e1893538e8b24a0d13ea`.

| Dim | Surface | Gate | Status | Live evidence |
|---|---|---|---|---|
| 2 | `velaru.xyz/instant` | No DTCC/SWIFT marketing labels | **PASS** | HTTP 200 · tunnel is “NAIC Exhibit D pack” |
| 5 | Instant $25/$49 vs `/pricing` | One self-serve ladder only | **PASS** | HTTP 200 · $25/$49/$149/$249 on both + `llms.txt` |
| 6 | `/privacy` | Nisaba LLC + patent + support SLA | **PASS** | HTTP 200 |
| 7 | `/terms` | Nisaba LLC + patent + support SLA | **PASS** | HTTP 200 |
| 13 | Velaru CSP | `Content-Security-Policy` present | **PASS** | Header on `/instant` and `/privacy` |
| 17 | `/.well-known/security.txt` | RFC 9116 Contact + Expires | **PASS** | HTTP 200 |
| 8-Erra | Erra `/health` | 200; keep `/healthz`; no dead `erra.onrender.com` | **PASS** | 200 on peer + `/erra/health`; dead host 404 |

No mid-ladder Gate SKUs were invented. Gate Bind Room / operator weld stay on Gate.

---

## Dim 2 — Instant DTCC label — PASS

**Block:** Instant tunnel/footer said **“DTCC integration”**. Zero tolerance. DTCC/SWIFT are not marketing labels.

**Live (2026-09-12):** `curl -s https://velaru.xyz/instant` → **HTTP 200**. Match:

```
57:  <a href="/scan/exhibit-d">NAIC Exhibit D pack</a>
```

`DTCC integration` and `SWIFT` are absent from `/instant` HTML.

---

## Dim 5 — One pricing ladder — PASS

**Block:** Instant sold $25 GAM / $49 fuse while `/pricing` started at $149.

**Live:** `https://velaru.xyz/pricing` **HTTP 200** and `https://velaru.xyz/instant` **HTTP 200** share one self-serve list:

| SKU | Price | `/pricing` | `/instant` | `llms.txt` |
|---|---|---|---|---|
| GAM Starter | $25 | yes | yes | yes |
| Fuse Receipt | $49 | yes | yes | yes |
| HOLD packet | $149 | yes | yes | yes |
| Proof Relay Monitor | $249/mo | yes | yes | yes |

`llms.txt` heading: `Self-serve ladder (one list — /pricing and /instant)`.  
Gate $1,750 / $25k weld were **not** added to `/pricing`.

---

## Dim 6 — `/privacy` — PASS

**Block:** `https://velaru.xyz/privacy` was 404.

**Live:** **HTTP 200**. Body includes `Nisaba LLC`, `Patent application No. 64/124,027`, `Support SLA` (liveness `/healthz`, Instant fulfillment ≤1 business day, security ack ≤2 business days, enterprise SLA in DPA/SOW only). Same page also live at `https://velaru.onrender.com/privacy` (HTTP 200).

---

## Dim 7 — `/terms` — PASS

**Block:** `https://velaru.xyz/terms` was 404.

**Live:** **HTTP 200**. Same operator, patent application number, and support SLA. Instant ladder cited; Gate paths called out as not mid-ladder SKUs.

---

## Dim 13 — CSP — PASS

**Block:** No `Content-Security-Policy`.

**Live** `curl -sI https://velaru.xyz/instant`:

```
HTTP/2 200
content-security-policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data: https:; connect-src 'self' https:; object-src 'none'; base-uri 'self'; form-action 'self' https://buy.stripe.com https://checkout.stripe.com; frame-ancestors 'none'
```

Same header on `/privacy`.

---

## Dim 17 — `security.txt` — PASS

**Block:** `https://velaru.xyz/.well-known/security.txt` was 404.

**Live:** **HTTP 200**

```
Contact: mailto:hello@velaru.xyz
Contact: mailto:demond@velaru.xyz
Expires: 2027-09-12T00:00:00.000Z
Preferred-Languages: en
Canonical: https://velaru.xyz/.well-known/security.txt
Policy: https://velaru.xyz/privacy
Acknowledgments: https://velaru.xyz/trust
```

---

## Dim 8-Erra — `/health` + no dead host — PASS

**Block:** Erra `/health` 500 (`NameError: get_institutional_research_record`). `/healthz` already 200. `erra.onrender.com` is dead and must not be advertised.

**Live (2026-09-12):**

| URL | Status | Body |
|---|---|---|
| `https://velaru.xyz/healthz` | **200** | `{"ok":true,"rail":"velaru"}` |
| `https://velaru.xyz/health` | **200** | Velaru status JSON |
| `https://velaru.xyz/erra/health` | **200** | `{"status":"ok","rail":"erra"}` |
| `https://velaru-erra.onrender.com/healthz` | **200** | `{"ok":true,"rail":"erra"}` |
| `https://velaru-erra.onrender.com/health` | **200** | `{"status":"ok","rail":"erra"}` |
| `https://erra-jf6a.onrender.com/healthz` | **200** | `{"ok":true,"rail":"erra"}` |
| `https://erra-jf6a.onrender.com/health` | **200** | `{"status":"ok","rail":"erra"}` |
| `https://erra.onrender.com/healthz` | **404** | dead host — not linked from `llms.txt` |

`llms.txt` says peer rail lives at `velaru-erra.onrender.com` **(not erra.onrender.com)**.  
Shared crash also 500’d `/diligence/nisaba-llc`; that URL is **200** after the import.

---

## Deploy

| Service | Render id | Public URL | Deploy | Commit |
|---|---|---|---|---|
| velaru | `srv-d9rir92jnfac73fqdtf0` | https://velaru.xyz · https://velaru.onrender.com | `dep-daic6v86gcjs7380gamg` live | `1e708c4` |
| erra | `srv-d9vph0rl550s738sdeag` | https://erra-jf6a.onrender.com | `dep-daic7106gcjs7380gckg` live | `1e708c4` |
| velaru-erra | `srv-d9vpjsdbedkc73etj67g` | https://velaru-erra.onrender.com | `dep-daic712q185c73a33780` live | `1e708c4` |

## Out of scope this pass

Other Flawless dims (Gate weld, Mishara consumer products) were not opened. This file is the Velaru-blocked slice only.
