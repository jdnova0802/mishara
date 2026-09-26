# PASTABLE FOR CLAUDE — What we just made (Issuing + ops) — 26 Sep 2026

## Context
Nisaba LLC got **Stripe Issuing approved**. Gate already had Issuing auth mouth code on prod; enablement was off. User funds a **$5** Mercury transfer (ETA **Sep 28–29**). **No warm leads.** Monday plan = **10 diligence emails** (cash path). Issuing float is **parked** until money clears — not blocking Monday.

---

## What we shipped / wired

### 1. Stripe Issuing ↔ Gate mouth (LIVE)
- Stripe webhook **`we_1UJhYV3b5zsnE0zsiM0wXobr`**
- URL: `https://gate.velaru.xyz/v1/issuing/authorization`
- Event: **`issuing_authorization.request` only**
- Render `gate-api`:
  - `GATE_ISSUING_ENABLED=1`
  - `STRIPE_ISSUING_WEBHOOK_SECRET=whsec_…`
  - `GATE_OPS_TOKEN` set (ops-only; not in git)
- Live config: `issuing_enabled: true`, `money_real: true`, `webhook_secret_configured: true`
- Dogfood: `POST /demo/issuing/mouth` → **GO / approved** verified earlier
- Page: https://gate.velaru.xyz/issuing-mouth
- Manifest: https://gate.velaru.xyz/.well-known/issuing-mouth.json

**Doctrine:** Gate never holds card float. AUTHORIZE/DECLINE only + stranger-verifiable receipt. Auth must answer &lt;2s.

### 2. Ops readiness checklist (LIVE)
- `GET /ops/issuing-status` (requires `X-Ops-Token: $GATE_OPS_TOKEN`)
- Unauthed → **401** `ops_token_required` (correct)
- Authed → **200** with fund→card→spendable steps

**Desktop verified right now:**
```
spendable: false
issuing_available_cents: 0 ($0.00)
cardholders: 0
cards_active: 0
mouth_enabled: true
webhook_secret: true
gate_holds_funds: false
next: Add funds → create cardholder → create active virtual card
```

### 3. Docs / PRs
- Branch: `cursor/issuing-wire-live-ce84`
- PR: https://github.com/jdnova0802/mishara/pull/125
- Files: `gate/outbound/ISSUING_WIRE_LIVE.md`, `STATUS_STRIPE_MONDAY.md`, `ATOMIZE_FINANCIAL_RAIL.md`
- Code: `issuing_mouth.readiness()` + `/ops/issuing-status` + tests

### 4. Rail atomization (map only — not more builds tonight)
Atoms: Link → Fund → Hold → Auth → Settle → **Receive (OCT gap)** → Payout → Loss → Proof  
Biggest missing money rail: **OCT/Fast Funds sink** (needs BIN/sponsor). Soft `/sink-mouth` stays `money_real: false`.  
Build order if anytime: float+card → readiness (done) → Treasury outbound mouth later → OCT only with sponsor.

---

## Explicitly NOT done / not claiming
- No Issuing balance yet (Mercury $5 in transit)
- No cardholder / virtual card yet
- No real card auth through Gate yet
- No Ix revenue, no Never buyer, no quit money from Issuing
- Sink mouth still soft (`enabled=false`, `money_real=false` on health)
- Did **not** expand into more rail products tonight — Monday diligence is the cash path

---

## User next steps (ordered)
1. **Monday:** send 10 diligence (Plan A 4 + Plan B 6); free 72h REVIEW; log `SENT_TALLY.md`
2. When Mercury shows $5: Stripe Issuing **Add funds** → wait **available**
3. Create cardholder + virtual card
4. `curl -H "X-Ops-Token: …" https://gate.velaru.xyz/ops/issuing-status` → expect `spendable: true`
5. One tiny real spend → confirm Gate AUTHORIZE/DECLINE

---

## One-liner for Claude
**Issuing mouth is production-wired and ops-checkable; spendable is false until $5 float + a card; cash still = Monday diligence, not Issuing volume.**
