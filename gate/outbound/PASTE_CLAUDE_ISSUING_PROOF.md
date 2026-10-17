# PASTE — Tell Claude: Issuing proof (17 Oct 2026)

Status. One real Stripe Issuing authorization hit the live Gate mouth and came back approved. Do not build another mouth. Do not re-run the swipe on the canceled card.

---

## Message (copy below the line)

---

Issuing — the live mouth approved one real $1.07 Kindle authorization. Stop there.

### What we decided

- The proof was one real `issuing_authorization.request` against `https://gate.velaru.xyz/v1/issuing/authorization`, inside Stripe’s window, with a stored decision a stranger can open. Not a new product, not a new rail, not a pitch change.
- Competitive set (Penholder, AgenticRail, Proofpane, Provenrail, HELM, CoreBase, HumanLayer, MandateGuard, Certiv, AgentLock, Kakunin) does not have this webhook. Do not invent a second clearance product because they exist. Do not email that crowd.
- Insurance-desk emails stay a separate human send. This swipe does not replace them.
- Fail closed. Only a Gate `GO` returns `{"approved": true}`. No `max_amount` and no `daily_cap` on the card means `mandate_required` and decline.
- This card’s mandate is `agent_id=nisaba_issuing_proof` and `max_amount=5.00`. No `expected_merchant`, no category allowlist, no `daily_cap`. A merchant under $5.00 is a GO. Over $5.00 is `amount_exceeds_cap`.
- Cardholder legal name on the form is the person’s name. Name on card is `Nisaba LLC`. Billing address is the Toledo operating address, not the Sheridan registered-agent address.
- Do not paste PAN, CVC, SSN, or `whsec_` into chat or git.

### What actually happened (17 Oct 2026)

Account `acct_1U56yR3b5zsnE0zs`, Nisaba LLC. Program: debit, self, v2 financial account, ancillary, Cross River, Mastercard BIN 53493302. Float is the $5.00 business-account balance (inbound transfer posted 30 Sep 2026). That $5 is Nisaba’s own money.

Cardholder `ich_1URWhf3b5zsnE0zsn0SIdyWn`, name Nisaba LLC, status active, type individual.

Card `ic_1URWkh3b5zsnE0zsWLHqUVhn`, virtual Mastercard, last4 5440, exp 10/2029. Metadata: `agent_id=nisaba_issuing_proof`, `max_amount=5.00`. Financial account `fa_65VRFiy7zwm7wcU5oH116VEUvnCmSQK4VCo1SLfODkuS8G`.

**The card is now `canceled`.** No replacement. No cancellation reason on the object. The approval below still stands. Do not try another purchase on 5440.

Four Kindle Svcs attempts, all 107 cents, category `digital_goods_large_volume`, card last4 5440:

| Authorization | Stripe reason | What it was |
|---|---|---|
| `iauth_1URXFd3b5zsnE0zsRVEaaEEG` | `webhook_error` `Invalid Stripe API version:` (blank) | Endpoint `we_1UJhYV3b5zsnE0zsiM0wXobr` had `api_version` null. Deleted. |
| `iauth_1URXSz3b5zsnE0zsUi7YhWXX` | same `webhook_error`, blank version | Endpoint was already pinned. The HTTP reply had no `Stripe-Version` header, so Stripe discarded the body. |
| `iauth_1URXYU3b5zsnE0zscgJngDuf` | `webhook_declined` | Gate answered. On `issuing_authorization.request` top-level `amount` is `0`. The $1.07 is `pending_request.amount`. Gate judged the zero hold as `invalid_amount` and returned `approved: false`. |
| `iauth_1URXhX3b5zsnE0zsR1QikRhn` | **`webhook_approved`** | Gate returned `approved: true`. Amount 107. Status **pending** (authorized hold, not captured). Decision stored `GO` at `2026-10-17T13:31:08+00:00`. Signals empty. `demo: false`. |

Public decision (no PAN):

https://gate.velaru.xyz/v1/issuing/authorization/iauth_1URXhX3b5zsnE0zsR1QikRhn

The signed receipt on that row was minted with `ttl_seconds: 120`. A verify call now returns `expired`. The stored decision is still GO. Do not treat `expired` as a decline of the swipe. Do not re-mint a replacement JWT and call it the original receipt.

### Live wire (do not recreate)

- One synchronous endpoint only: `we_1URXLh3b5zsnE0zsL12oWMS4`
- URL: `https://gate.velaru.xyz/v1/issuing/authorization`
- Event: `issuing_authorization.request` only
- `api_version`: `2025-02-24.acacia` (set at create; Stripe will not patch it onto an existing endpoint)
- Response header required: `Stripe-Version: 2025-02-24.acacia`
- Response body to Stripe: `{"approved": true}` or `{"approved": false}` only
- Judge `pending_request.amount` while `pending_request` is present. After close, `pending_request` is null and top-level `amount` is the final figure.
- `GATE_ISSUING_ENABLED=1` on Render `gate-api` `srv-dai3n0u1egvs73dbd94g`
- Signing secret is `STRIPE_ISSUING_WEBHOOK_SECRET` on that service. Not in git.

### Code vs what is running

PR **#167** (`cursor/issuing-api-version-ce84`) has the header, the pending-amount read, and `GET /v1/issuing/authorization/<iauth_id>`. It is **not merged**.

Production was deployed by hand from that branch (`f747234`, Render deploy `dep-db9ni9e1egvs73fufl50`). The service’s tracked branch is still `main`. The next auto-deploy of `main` drops the header, the pending-amount read, and the public decision URL. Merge #167 before any other `main` deploy, or the next swipe fails the same three ways again.

### Honesty

- This is Nisaba spending its own $5 float on its own card. It is not a cleared stranger dollar. The company wall (one stranger dollar into the Nisaba account, or stop) is unchanged.
- `money_real` on `/.well-known/issuing-mouth.json` means the mouth env flags are set. It does not mean a stranger paid.
- Authorization status `pending` is not settlement.
- A physical Amazon order placed earlier (Gushers) can still authorize at ship. The card is canceled, so that auth should not succeed. Do not chase it.
- Abandoned Checkout sessions from the headless attempt are not this proof. Ignore verification codes from those.

### Do not

- Build another mouth, rail, or SKU off this result.
- Create a second webhook on `issuing_authorization.request`.
- Ship an Issuing reply without `Stripe-Version`.
- Read top-level `amount` on the request event.
- Spend on card 5440. It is canceled.
- Call this the stranger dollar.
