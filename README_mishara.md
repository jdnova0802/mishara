# Mishara

**When an AI decision already hurt you.**

Consumer door for Nisaba LLC — powered by Velaru. Not Gate. Not Erra.

## Products

| SKU | Price | What you get |
|-----|-------|--------------|
| **Harm Receipt** | Free | Velaru-signed receipt + stranger verify URL + plain-English next step |
| **Demand Pack** | $99 | Receipt + FCRA/ECOA/hiring-tool rights map + demand letter (Exhibit A = receipt hash) |
| **Advocate Bundle** | $499 | Demand Pack + anonymous pattern join/alert email + advocate export (JSON + TXT) |

## Quick start

```bash
pip install -r requirements_mishara.txt
export VELARU_API_URL=https://velaru.onrender.com
export MISHARA_PAYMENTS=dev          # local unlocks without Stripe
export MISHARA_ALLOW_DEV_PAY=1
export OPENAI_API_KEY=...            # optional — demand letters / explanations
python mishara_app.py
```

Open http://localhost:5001

## Deploy (Render)

Live split (do not merge these onto one service again):

| Host | Render service | Service id |
|------|----------------|------------|
| `https://mishara.onrender.com` | `mishara-public` | `srv-d9romc2jnfac7385gn80` |
| `https://gate.velaru.xyz` | `gate-api` | `srv-dai3n0u1egvs73dbd94g` |

Helper: `python3 deploy_mishara_render.py` (needs `RENDER_API_KEY` from Cloud Agent secrets / local `.env`). Gate: `python3 gate/deploy_render.py`.

Use blueprint `render_mishara.yaml` (own web service + 1GB disk). **Do not** point Mishara domains at `gate-api`.

- **Build:** `pip install -r requirements_mishara.txt`
- **Start:** `gunicorn mishara_app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
- **Health:** `/health`
- **Disk:** `/var/data` → `MISHARA_DB_PATH=/var/data/mishara.db`

Env:

- `VELARU_API_URL=https://velaru.onrender.com`
- `MISHARA_PAYMENTS=stripe` (or `dev` / `invoice`)
- `STRIPE_SECRET_KEY` (when stripe)
- `MISHARA_PUBLIC_URL=https://mishara.onrender.com`
- `OPENAI_API_KEY` (optional)
- `MISHARA_CONTACT_EMAIL=hello@velaru.xyz`
- `MISHARA_SECRET_KEY` (session / unlock HMAC)

Cutover checklist:

1. Keep Mishara on `mishara-public` (separate from `gate-api`)
2. Confirm `/health` returns `"service":"mishara"` and product ids
3. Set Stripe keys, then one live Demand Pack checkout
4. Confirm `https://gate.velaru.xyz/health` is still Gate after any Mishara deploy

## API

| Method | Path | Notes |
|--------|------|-------|
| GET | `/` | Product surface + Harm Receipt flow |
| GET | `/products.json` | Machine-readable SKUs |
| POST | `/submit` | Free Harm Receipt via Velaru |
| POST | `/checkout` | Demand Pack / Advocate Bundle |
| GET/POST | `/unlock/<token>` | Paid fulfillment |
| POST | `/demand-letter` | Requires paid unlock token |
| GET | `/pattern` | Anonymous counts |
| POST | `/join-pattern` | Advocate Bundle alerts (email hashed) |
| GET | `/health` | Health |

## Privacy

- Narratives go to Velaru for classify/sign; Mishara pattern DB stores platform, domain, harm type, classification, receipt hash only.
- Alert emails stored as bcrypt hashes.
- `their_production: false` until a recorded third-party production weld elsewhere.

## License

Nisaba LLC · Patent #64/124,027
