# Gate API — External commercial layer

Metered dev API wrapping the Velaru fuse engine. Identity, billing, docs, 402 on limit.

**One question:** Can this agent still act right now?

## On your laptop (2 commands)

After git pull:

```bash
cd gate
chmod +x setup.sh start.sh
./setup.sh && ./start.sh
```

Opens **http://localhost:5001** — full site + install page + signup. Dev mode skips Stripe (install checkout works instantly for testing).

## Deploy (Render)

1. New Web Service → connect this repo
2. Root directory: `gate`
3. Copy env from `.env.example`
4. `GATE_PUBLIC_URL` = `https://YOUR_SERVICE.onrender.com` (if you leave it localhost, Gate lifts `RENDER_EXTERNAL_URL` automatically)
5. Disk: `/var/data` with `GATE_DB_PATH=/var/data/gate.db`
6. Stripe Dashboard → Product $99/mo → `STRIPE_PRICE_ID` + install `$2,500` + Bind Room `$1,750`
7. Stripe Webhook → `https://YOUR_URL/billing/webhook`

Then **prove it is not local**:

```bash
./verify-public.sh https://YOUR_GATE.onrender.com
```

If that command is given `localhost`, it exits 1 on purpose.

## Bind Room + PAS weld

Officer pack examiners take (Colorado 10-1-1 SERFF shape) + on-request appendix of `verify_url`s. Not a fuse hash in SERFF.

```
# Public (no key). fuse_id + job_id only.
curl -s -X POST "$GATE/demo/pas/policycenter/pre-bind" \
  -H "Content-Type: application/json" \
  -d '{"fuse_id":"fuse_velaru_drill","job_id":"pc:DEMO"}'

# Metered
curl -s -X POST "$GATE/v1/pas/policycenter/pre-bind" \
  -H "Authorization: Bearer $GATE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"fuse_id":"YOUR_FUSE","job_id":"pc:JOB"}'
```

DEAD → `allow_bind: false` + `raise_uw_issue` body. Do not call `bind-and-issue`. UW approve is not CHARGE.

MGA: `POST /v1/pas/mga-authority`. Appendix: `GET /v1/pas/bind-appendix`. Page: `/bind-room`. Contract: `/listings/control-not-model.json`.

## Local dev

```bash
cd gate
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set GATE_DEV_MODE=1 to skip Stripe
export PYTHONPATH=..
python app.py
# → http://localhost:5001
```

## Launch checklist

- [ ] Deploy to Render with env vars
- [ ] Sign up → verify dashboard + API key
- [ ] Run three acceptance curls (see `/docs`)
- [ ] Stripe test checkout → Pro upgrade
- [ ] Post Show HN (copy below)

---

## Show HN post (copy-paste)

**Title:** Show HN: Gate API – metered fuse hop for agents (can this agent still act?)

**Body:**

I built Velaru (prepaid public mortality fuse — LIVE/ARMED/DEAD/UNSIGNED) and realized the internal architecture was 9/10 but external reward was ~0 because public hop had no meter.

Gate API is the commercial layer: self-serve API keys, Stripe Pro tier, HTTP 402 when you hit the free wall. Proxies to the Velaru fuse engine.

Three curls:

```
# Lookup
curl -s "https://YOUR_GATE_URL/v1/fuse/lookup?fuse_id=fuse_velaru_drill" \
  -H "Authorization: Bearer gate_sk_live_..."

# Hop (DEAD → verdict:false + receipt)
curl -s -X POST "https://YOUR_GATE_URL/v1/fuse/hop" \
  -H "Authorization: Bearer gate_sk_live_..." \
  -H "Content-Type: application/json" \
  -d '{"fuse_id":"fuse_velaru_drill"}'

# Execute gate demo
curl -s -X POST "https://YOUR_GATE_URL/v1/execute-gate/demo" \
  -H "Authorization: Bearer gate_sk_live_..." \
  -H "Content-Type: application/json" \
  -d '{}'
```

Free: 1,000 hops/mo. Pro: $99/mo for 1M hops.

Docs: https://YOUR_GATE_URL/docs  
Engine: https://velaru.xyz  
Patent #64/124,027 · Nisaba LLC

Would love feedback from anyone wiring pre-exec gates into agent loops.

---

## Product Hunt one-liner

Gate API — metered "can this agent still act?" fuse hop for AI agents. Free tier + Stripe Pro.

## Twitter/X

Shipped Gate API: self-serve metered wrapper on Velaru fuse hop. 1k free hops/mo, $99 Pro. No more infinite public labor. Docs + 3 curls → [YOUR_URL]

---

## Honest revenue math

| Milestone | What it takes |
|-----------|---------------|
| First $ | Week 2–4 post-launch if HN/listings hit |
| $1K MRR | ~10 Pro subs or mix of usage |
| $10K MRR | ~100 Pro subs + dev word-of-mouth |
| Quit day job | $10K+ stable MRR for 3+ months (your expenses vary) |

Traffic × meter × price. Architecture alone doesn't pay rent — this layer adds the meter.
