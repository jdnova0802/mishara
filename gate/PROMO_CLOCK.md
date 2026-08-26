# Promo Clock — kill stale site dates

**Spec:** `gate-promo-clock-v1`  
**Cousin:** Stale LIVE Rejector = clearance. Promo Clock = **marketing surface**.

## Rule
If `next_at` ≤ now → **never** headline “Next drill.”  
Show **Last proved** if you have a timestamp, else **hide** the bar.

## Endpoints
| Path | Role |
|------|------|
| `GET /.well-known/promo-clock.json` | State + usage |
| `GET /static/promo-clock.js` | Browser fail-closed rewriter |

Env (optional, for JSON state):
- `GATE_PROMO_NEXT_AT` — ISO datetime of next public drill  
- `GATE_PROMO_LAST_PROVED_AT` — ISO datetime of last public prove  
- `GATE_PROMO_LABEL` — e.g. `AWS Loft SF`  
- `GATE_PROMO_HREF` — link target  

## Drop-in for Check (`velaru.xyz/check`)

Replace hardcoded Aug 18 bar with:

```html
<div class="drill-bar" id="drill-bar" data-promo-clock
     data-next-at="2026-08-18T17:00:00-07:00"
     data-last-proved-at="2026-08-24T06:31:00Z"
     data-label="AWS Loft SF"
     data-href="/fuse/fuse_velaru_drill"></div>
<script src="https://gate.velaru.xyz/static/promo-clock.js" defer></script>
```

Or keep `#drill-bar` text and load the script after `RECENT_BLOCKS` — legacy past calendar dates **hide** or flip using the newest restraint feed timestamp.

## Tests
```bash
python3 -m unittest gate.test_promo_clock
```
