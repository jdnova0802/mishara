# Extreme session — remaining when you’re home

Code for listings + public lock is in this repo. **You still do deploy + one human.**

## Already in Gate

- OCSP-strict: timeout/5xx → **503 halt**
- Welded door: `POST /v1/act` and public `POST /demo/act`
- PAS: `POST /v1/pas/bind-check` and public `POST /demo/pas/bind-check`
- MCP door: `POST /mcp` (Kong / TrueFoundry / AWS AgentCore — one endpoint)
- Cloudflare weld: `cloudflare-worker.js` + `wrangler.toml` (refuses localhost GATE_URL)
- Date-all map: `/.well-known/listings.json`
- Paperwork: `/listings/guidewire-partnerconnect.json` + `/listings/duckcreek-partner.json`
- Prod lock: `/health` → **503** if production still advertises localhost
- Auto-lift: Render `RENDER_EXTERNAL_URL` wins over a leftover localhost `GATE_PUBLIC_URL`

CHARGE-only LIVE stays on Velaru. Do not add an admin resurrect.

## You after work (this is the “not local” step)

```bash
# After Render is up:
cd gate
./verify-public.sh https://YOUR_GATE.onrender.com
```

That script **fails** if you pass localhost. Then:

1. Stripe + `GATE_PUBLIC_URL` (or leave unset — Render hostname is used)
2. Paste `https://YOUR_GATE/for/carriers` or `/for/legal` to one human
3. Submit the two PAS packets (forms, not code)
4. Optional: `wrangler secret put GATE_KEY` and attach the worker to **one** origin

## Still a 10 (not tonight)

TPM/HSM staple. Exclusive PAS weld in *their* production. Field hours.

Do not add L12. Date all listings. Marry one write path.
