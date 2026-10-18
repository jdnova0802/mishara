# SUNDAY → MONDAY PASS (start now)

## Sunday (build — do before sleep)

```bash
cd money-rail-demo
node server.mjs
# other terminal:
npm run demo
```

1. Leave server running. Record **60s Loom**: run `npm run demo`, show allow vs deny + `receipt.signature`.
2. Second Loom (optional tonight / morning): open [n8n.cloud](https://n8n.cloud) or local n8n → one flow Form/Webhook → Google Sheet → Slack/email. 60s screen record.
3. Draft Upwork title: **Stripe webhooks & payment automations (setup + monthly care)**
4. Overview = offer line below + Loom links.
5. List **20** warm targets (local biz / friends with a site or Stripe).

## Offer line
I fix and build Stripe webhooks & payment automations for founders — setup fee + monthly care if APIs break.

## Monday (pitch)
- Profile **public**
- **15** Upwork proposals
- **5** warm pings from the list
- Price opener: **$250–500 setup + $150–300/mo care** (raise after 2 wins)

## Upwork search queries (bid these)
1. Stripe webhook  
2. Stripe integration  
3. Zapier Stripe  
4. Make.com automation  
5. n8n automation  
6. payment webhook  
7. Stripe Connect  
8. API integration webhook  
9. Stripe not receiving webhooks  
10. automate invoicing Stripe  

## Proposal skeleton (paste / edit)
```
Saw you need [Stripe webhook / automation] working reliably.

I build payment webhooks + automations with signed decision logs so you can see allow/deny why — not just "hope Stripe fired."

Fixed scope: $___ setup. Optional $___/mo care (API breaks, small changes).

60s proof: [Loom]
First deliverable in 48–72h if scope is clear.
```

## Quit rule (unchanged)
One month ≥ ~$2.5–3k **in bank** + ≥ ~$500/mo retainers sold → leave ABM.

## Sunday run (2026-10-18)

Demos fired locally against `http://127.0.0.1:8787`:

- webhook `approved: true`, `receipt.signature` present, verify `valid: true`
- issuing fuel `approved: true`
- issuing software `approved: false`, reason `mcc_not_in_allowlist`

Screen recording (no audio): https://cursor.com/agents/bc-01a0c434-e2d1-7a91-b100-1c79c69bce84/artifacts?path=%2Fopt%2Fcursor%2Fartifacts%2Fmoney-rail-allow-deny-signature.mp4

Upwork text and Monday proposal: `PITCH_MONDAY.md` (paste-ready, not posted).

Warm list: `WARM20.md` — 20 rows, all `NEED_NAME`. No contacts were invented.
