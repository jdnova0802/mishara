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

Use `render_mishara.yaml` or:

- **Build:** `pip install -r requirements_mishara.txt`
- **Start:** `gunicorn mishara_app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
- **Health:** `/health`

Env:

- `VELARU_API_URL=https://velaru.onrender.com`
- `MISHARA_PAYMENTS=stripe` (or `dev` / `invoice`)
- `STRIPE_SECRET_KEY` (when stripe)
- `MISHARA_PUBLIC_URL=https://mishara.onrender.com`
- `OPENAI_API_KEY` (optional)
- `MISHARA_CONTACT_EMAIL=hello@velaru.xyz`

Point **mishara.app** / Render service at this app — not Gate.

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
