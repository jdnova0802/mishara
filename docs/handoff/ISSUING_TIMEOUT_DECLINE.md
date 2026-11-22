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

## Residual structural limit (not a todo)

Once Stripe Autopilot **approves** an authorization during a timeout, that is a **live card-network transaction**. The Issuing platform has **no force-reversal** in that moment. Later tools are refund, merchant expiry, or dispute — after the fact.

Even after the Dashboard timeout→Decline setting is flipped, there is still a race between Stripe's 2-second timer firing and Gate's process noticing (`issuing_authorization.created` / `.updated`). If Autopilot approved in that window, Gate's later `approved: false` cannot unwind the network auth. That race is a **permanent residual risk**. Further mouth code cannot close it to zero.

The public receipt's job in that window is honesty: `clear: false` / `disputed_clearance` means **Gate did not Clear**, not **the charge did not happen**.

## Compensating control checked (not implemented)

`POST /v1/issuing/authorizations/{id}/reverse` exists in Stripe's API. **Test mode only.** Live Issuing authorizations are not force-reversed by the issuer; capture, merchant expiry, refund, or dispute are the production paths.

An automated refund/reversal the moment Gate sees a `webhook_timeout` approval it disagrees with is **not a feasible compensating control** on live cards. Wiring test-mode reverse on every timeout would also fire against merchants who already have a valid approval — wrong default. Do not add that loop.
