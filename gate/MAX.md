# What code maxes Gate — vs what doesn't

Product (plates, meter, hop, install, demo) is done. Remaining **code** is production plumbing so money doesn't evaporate.

## Must have before live payments (this commit)

| Item | Why |
|------|-----|
| Persistent disk (`/var/data/gate.db`) | `/tmp` wipes API keys + paid orders on every Render restart |
| Stripe webhook notify | You know the second cash hits |
| `/ops/orders?token=` | See who paid without SSH |
| Secure cookies on HTTPS | Session hijack on public URL |

## Harden (not inventing — soft-door + honesty)

| Item | Why |
|------|-----|
| `/health` probes real routes (`probes_ok`) | Flags lied while paths 500'd. Bind Room must not convert into silence. |
| `SENTRY_DSN` / `GATE_SENTRY_DSN` | Optional. `sentry_configured` in `/health` when set. |
| External uptime → your phone | Point UptimeRobot / Better Stack at `https://gate.velaru.xyz/health` and alert if `status` ≠ `ok` or `probes_ok` is false. |
| Sep 1 chain audit | `GET /ops/chain-continuity?token=` writes `/trust/corrections` if needed. Broken `prev_receipt_hash` = hole. Sparse quiet ≠ hole. |

**Not code:** Render account, Stripe products, Discord webhook URL, sending `/for/legal` to a human.

## Do not build (zero personal cash)

- More audience plates
- More Velaru museum pages
- Mobile app
- SSO / SOC2 / SSO until a whale asks
- Postgres (disk is enough at this scale)
- Marketing site redesign
- Mishara features

## After first payment (only if buyer asks)

- Invoice PDF
- SSO
- Custom SLA
- On-prem

Until then: deploy + Stripe + notify webhook + send plates.
