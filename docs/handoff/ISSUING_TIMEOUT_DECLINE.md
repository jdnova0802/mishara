# Issuing timeout = Decline (operator, not this repo)

Stripe's realtime `issuing_authorization.request` webhook waits **2 seconds**. If Gate does not return a valid `{approved: …}` body in that window, Stripe applies **Dashboard timeout / Autopilot settings**, not Gate's in-process fail-closed.

This repository **cannot** flip that Dashboard control. DENY-as-product is false until a human sets it.

## Set it

1. Stripe Dashboard → **Issuing** → **Real-time authorization**.
2. Webhook timeout behavior → **Decline** (not Approve, not Autopilot).
3. Docs: https://docs.stripe.com/issuing/controls/real-time-authorizations

## Webhooks (two endpoints)

| Event | URL | Why separate |
|---|---|---|
| `issuing_authorization.request` | `POST /v1/issuing/authorization` | Must answer in <2s with `{approved}` + `Stripe-Version` |
| `issuing_authorization.created` | `POST /v1/issuing/events` | Binds `request_history.reason` after the race |
| `issuing_authorization.updated` | `POST /v1/issuing/events` | Same bind on later updates |

Use a **regular** Stripe webhook endpoint for created/updated (not the synchronous auth endpoint). Optional env: `STRIPE_ISSUING_EVENTS_WEBHOOK_SECRET`. Falls back to `STRIPE_ISSUING_WEBHOOK_SECRET`.

## Receipt rule (code)

If `request_history.reason` is `webhook_timeout` or `webhook_error`, the public receipt JWT has `clear: false` and `dec: NO_GO`. `gate_approved` (what Gate's process would have said) and `stripe_approved` (what Stripe recorded) stay distinct. Autopilot-approve + Gate-GO still **must not** say Clear.

## New gap (not closed here)

If Autopilot **approves** on timeout, money may still move on the card network while Gate publishes `clear: false`. That receipt means **Gate did not Clear**, not **the charge did not happen**. No clawback in this change.
