# PASTABLE — Status (25 Sep 2026 night)

**Decision:** Skip Issuing float for now (Mercury empty / ACH days). **Monday = 10 diligence emails.**

---

## Stripe Issuing — DONE (no float yet)

| Item | Status |
|------|--------|
| Nisaba LLC Issuing access | **Approved** (Dashboard Issuing Overview live) |
| Gate mouth code on prod | **Live** |
| `GATE_ISSUING_ENABLED` | **1** (Render gate-api) |
| Webhook secret on Render | **Set** |
| Stripe webhook | **`we_1UJhYV3b5zsnE0zsiM0wXobr`** — enabled |
| Webhook URL | `https://gate.velaru.xyz/v1/issuing/authorization` |
| Event | `issuing_authorization.request` only |
| Live config | `issuing_enabled: true` · `money_real: true` · `webhook_secret_configured: true` |
| Dogfood | `POST /demo/issuing/mouth` → **GO / approved** verified |
| Issuing balance / cards | **$0** · **0 cards** — intentionally skipped until spare $ clears |
| Real card auth | **Not yet** (waiting on bank float — not blocking Monday) |

Pages:
- https://gate.velaru.xyz/issuing-mouth
- https://gate.velaru.xyz/.well-known/issuing-mouth.json

---

## Gate cash surfaces — LIVE

| Surface | Status | URL |
|---------|--------|-----|
| Diligence (free 72h REVIEW → deposit path) | **200** | https://gate.velaru.xyz/diligence |
| Bind Room | **200** | https://gate.velaru.xyz/bind-room |
| Monday outbound pack | Ready on incline/complaint branches | Plan A 4 + Plan B 6 = **10** |
| Complaint-language quote pack | Shipped | `gate/outbound/COMPLAINT_LANGUAGE_QUOTE_PACK.md` |
| Warm replies | **None right now** | — |

---

## Monday plan (locked)

1. Send **10** diligence touches (Plan A: Porch → Incline → Clear Blue → Gallagher; Plan B six).
2. Offer = free **72h REVIEW** → written halt-gap ID (not paid deposit cold).
3. Mirror complaint words: collateral letter vs LOC · refused to adjust · replace LOC · never issued.
4. Log in `SENT_TALLY.md`.
5. Issuing float / virtual card = **later**, when Mercury has spare $ without stacking ACH waits.

---

## Not blocking Monday

- Issuing $5 top-up  
- Personal bank link  
- Real card swipe proof  
- Subro / Reg 114 / LPT bigger on-ramps (upsell after logos answer)

---

## PRs / branches (ref)

- Issuing wire doc: `cursor/issuing-wire-live-ce84` — https://github.com/jdnova0802/mishara/pull/125  
- Quote pack + deep on-ramp: `cursor/complaint-language-pack-ce84` — https://github.com/jdnova0802/mishara/pull/124  
- Drafts live on: `cursor/incline-docket-confirm-ce84` (`BACKUP_WAVE_72H_DILIGENCE.md` + `PLAN_B_FAST_6.md`)
