# Mishara

**The first place to go when an AI decision harmed you.**

Mishara is a consumer AI rights enforcement app powered entirely by [Velaru](https://velaru.onrender.com) audit infrastructure. It does not run its own classification engine, crypto layer, or audit chain — Velaru handles all of that.

## What Mishara does

1. **Receipt** — Document what happened; get a cryptographic Velaru-signed record
2. **Action** — Plain-English rights guidance + demand letter generation
3. **Pattern** — Anonymous aggregation by platform to surface systemic harm

## Quick start (local)

```bash
cd mishara
pip install -r requirements_mishara.txt
export VELARU_API_URL=https://velaru.onrender.com
export ANTHROPIC_API_KEY=your_key   # optional — for demand letters & explanations
python mishara_app.py
```

Open http://localhost:5001

## Deploy to Render

1. Push this repo to GitHub (`jdnova0802/mishara`)
2. Create a new **Web Service** on Render
3. Connect the repo and use `render_mishara.yaml` (Blueprint) or set:
   - **Build:** `pip install -r requirements_mishara.txt`
   - **Start:** `gunicorn mishara_app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
   - **Health check:** `/health`
4. Set environment variables:
   - `VELARU_API_URL=https://velaru.onrender.com`
   - `ANTHROPIC_API_KEY` (optional, for Claude-powered letters)
5. Add custom domain **mishara.app** in Render → Settings → Custom Domains

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Main flow (mobile-first) |
| POST | `/submit` | Classify via Velaru + store anonymized pattern |
| POST | `/demand-letter` | Generate demand letter (Claude or template) |
| GET | `/pattern?platform=X&domain=Y` | Pattern count for platform |
| POST | `/join-pattern` | Email signup for class-action alerts (bcrypt hash only) |
| GET | `/health` | Service health |

## Velaru endpoints used

- `POST https://velaru.onrender.com/classify`
- `GET https://velaru.onrender.com/verify` (link for users)
- `GET https://velaru.onrender.com/domains` (domain mapping reference)

## Privacy

- User descriptions are sent to Velaru for classification (same as Velaru product)
- Mishara SQLite stores **no PII** in pattern data: platform, domain, classification, receipt hash, timestamp only
- Notification emails stored as bcrypt hashes only

## License

Nisaba LLC · Patent #64/124,027
