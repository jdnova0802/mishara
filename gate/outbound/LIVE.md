# x402 LIVE — public host (gate.velaru.xyz)

Stamp: 2026-11-01 ~9:35 AM America/New_York.
Host: Render `gate-api` (`srv-dai3n0u1egvs73dbd94g`), custom domain `gate.velaru.xyz`.
Code: `1f6ce94` (#223 merged) live as `dep-dbjjv1ll015s738l5o70`.

**money_real: not claimed.** No USDC moved. Challenge + CDP JWT + fail-closed are live. A real `Payment-Signature` settle still needs a funded Base payer.

## Env keys set (no values)

On `gate-api` (service + env group `gate-x402` now linked):

| Key | Present | Notes |
|---|---|---|
| `GATE_X402_PAYTO` | yes | 42-char Base address, not `< 2^16` / 0x0 / demo burn. Public payTo in 402: `0x86e20794ef024a023d52b55542dca45ee0d1be40` |
| `GATE_X402_AMOUNT_ATOMIC` | yes | `2000` ($0.002 USDC) |
| `CDP_API_KEY_ID` | yes | already on service |
| `CDP_API_KEY_SECRET` | yes | already on service (not PEM; Ed25519-shaped) |
| `GATE_X402_FACILITATOR_URL` | no | default `https://api.cdp.coinbase.com/platform/v2/x402` |
| `GATE_X402_DEMO` | yes | `0` |
| `GATE_X402_DEMO_PAYTO` | yes | empty — ignored by `payto()` |

Not used for production settlement: `GATE_X402_DEMO_PAYTO`.

## `/health` x402 (live)

```json
{
  "configured": true,
  "dogfood": "https://gate.velaru.xyz/demo/x402/agent",
  "facilitator_ready": true,
  "gaps": [],
  "mouth": "https://gate.velaru.xyz/x402-mouth",
  "placeholder_rejected": false
}
```

CDP `/verify` with a dummy payload (this VM, Render creds, no secrets logged): HTTP **400** `invalid_request` (schema), not 401. JWT auth works.

## Curl transcript

Unauthenticated challenge:

```bash
curl -sS -D - -o /tmp/eval.body https://gate.velaru.xyz/v1/prefinality/evaluate
# HTTP/2 402
# payment-required: <base64 x402 v2>
# x-gate-x402: gate-x402-challenge-v1
# accepts[0].payTo = 0x86e20794ef024a023d52b55542dca45ee0d1be40
# amount=2000 asset=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 network=eip155:8453
```

POST unauth → **402**.

Fail-closed (header alone never unlocks):

```bash
curl -sS -o /tmp/p2.json -w "%{http_code}\n" -X POST https://gate.velaru.xyz/v1/prefinality/evaluate \
  -H "Content-Type: application/json" \
  -H "Payment-Signature: not-a-real-payment" \
  -d '{"rail":"x402","transfer":{"amount":"0.002","currency":"USDC","counterparty":"0x0000000000000000000000000000000000000001"}}'
# 402  x402_verify.reason=payment_payload_invalid
```

JSON-shaped `X-Payment` (still forged) → **402** `x402_verify.reason=invalid_request` (CDP reject, `paid` absent).

`GET /x402-mouth` → **200**. `POST /demo/x402/agent` → **200** `money_real: false` (dogfood; not a settle).

## Blockers — human actions for real USDC settle

This agent has **no payer wallet** and will not mint a fake `Payment-Signature`.

1. From a wallet that holds **Base USDC**, build an x402 **v2** `paymentPayload` that CDP accepts (`x402V2PaymentPayload` includes `accepted`) matching the live challenge: payTo `0x86e20794ef024a023d52b55542dca45ee0d1be40`, amount `2000`, asset Base USDC, network `eip155:8453`.
2. `POST https://gate.velaru.xyz/v1/prefinality/evaluate` with that value in `Payment-Signature` (or `X-Payment`) **and** a normal evaluate JSON body (`rail` + `transfer`).
3. Expect decision + Gate receipt only after CDP **verify + settle** succeed.
4. On Basescan, confirm USDC actually arrived at `0x86e20794ef024a023d52b55542dca45ee0d1be40` before anyone says `money_real`.

Until step 4, keep `money_real` false.
