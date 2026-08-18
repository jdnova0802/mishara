# Extreme session — remaining when you’re on desktop

Bind Room + PolicyCenter/MGA weld + no-PII contract are in this repo. **You still do deploy + Stripe price IDs + one human.** Do not hunt more listings. Do not add L12, TPM, admin CHARGE, or an email drip.

## Already in Gate

- OCSP-strict: timeout/5xx → **503 halt**
- Welded door: `POST /v1/act` and public `POST /demo/act`
- PAS: `POST /v1/pas/bind-check` and public `POST /demo/pas/bind-check`
- PolicyCenter weld: `POST /v1/pas/policycenter/pre-bind` (+ `/demo/...`)
  - LIVE + verdict true → next is `POST /job/v1/jobs/{jobId}/bind-and-issue`
  - DEAD/halt → raise Manual UW issue. Do **not** call bind-and-issue.
  - UW approve without CHARGE ≠ resurrect
- MGA authority: `POST /v1/pas/mga-authority` (premium / line / state)
- Duck Creek wrap: `POST /v1/pas/duckcreek/pre-bind`
- Appendix: `GET /v1/pas/bind-appendix` (on-request; not the SERFF body)
- Bound answer: `/bound` · `/.well-known/bound-answer.json` · hop/act/pre-bind include `bound_answer.holds`
- Exclusive timing: `/only` · `exclusive_timing.museum` on demo hops. `/v1/act` is Gate’s only door. `their_production` is never claimed from Gate.
- Bind Room: `/bind-room` · officer-pack.json · appendix.schema.json · Exhibit C HITL · `$1,750`
- No PII: PAS paths reject SSN / ACORD / named insured / ECDIS with `400 no_pii`
- Contract: `/listings/control-not-model.json`
- Bind-only Cloudflare worker: `/listings/cloudflare-worker-bind.js`
- MCP tools: `policycenter_pre_bind`, `mga_authority` (MCP never wins a weld slot)
- Date-all map: `/.well-known/listings.json`
- Prod lock: `/health` → **503** if production still advertises localhost

CHARGE-only LIVE stays on Velaru. Do not add an admin resurrect.

## You after work (this is the “not local” step)

```bash
# After Render is up:
cd gate
./verify-public.sh https://YOUR_GATE.onrender.com
```

That script **fails** if you pass localhost. Then:

1. Stripe: Pro `$99`, install `$2,500`, Bind Room `$1,750` → `STRIPE_PRICE_ID`, `STRIPE_INSTALL_PRICE_ID`, `STRIPE_BIND_ROOM_PRICE_ID`
2. `GATE_PUBLIC_URL` (or leave unset — Render hostname is used). Disk `/var/data`.
3. Paste `https://YOUR_GATE/for/carriers` or `/bind-room` to **one** human
4. Optional paperwork: Guidewire + Duck Creek packets (forms, not a weld)
5. Optional: `wrangler secret put GATE_KEY` and attach **one** origin (`cloudflare-worker-bind.js` for bind-and-issue only)

## Still later (not tonight)

TPM/HSM staple. Exclusive PAS weld in *their* production. Field hours.

Do not add L12. Date all listings. Marry one write path.
