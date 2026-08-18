# Extreme session — remaining when you’re home

Code for 9.5 is in this repo. **You still do deploy + one human.**

## Already in Gate (this session)

- OCSP-strict: timeout/5xx → **503 halt**, never LIVE (`/v1/ocsp`)
- Welded door: `POST /v1/act` — hop first, DEAD never acts
- PAS: `POST /v1/pas/bind-check`
- Agents: `/.well-known/mcp.json` + `/.well-known/x402.json`
- Cloudflare weld: `cloudflare-worker.js`

CHARGE-only LIVE stays on Velaru. Do not add an admin resurrect.

## You after work (makes it 9.5 not 7.5)

1. Render deploy (`gate/`, disk `/var/data`)
2. Stripe + `GATE_PUBLIC_URL`
3. Confirm:
   - `/.well-known/mcp.json`
   - `POST /v1/act` on `fuse_velaru_drill` → `acted: false`
   - `POST /v1/pas/bind-check` → BLOCK + receipt
4. Paste `https://YOUR_GATE/for/carriers` or `/for/legal` to one human
5. Optional: attach `cloudflare-worker.js` to one origin

## Still a 10 (not tonight)

TPM/HSM staple. Exclusive PAS weld in *their* production. Field hours.

Do not add L12.
