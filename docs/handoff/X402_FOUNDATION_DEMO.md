# x402 Foundation demo — Nov 1 handoff

## What was already built
- Challenge builder: `gate/x402_challenge.py` (402 Payment Required, fail-closed on header-only)
- Facilitator client: `gate/x402_facilitator.py` (CDP verify + settle)
- Prefinality mouth: `POST /v1/prefinality/evaluate` (API key **or** verified x402)
- Free audit + paid wire: `/api/x402/audit`, `/api/x402/wire`
- Catalog: `/.well-known/x402.json`

## Why health shows `x402.configured: false`
`configured` is **only** `GATE_X402_PAYTO` / `GATE_X402_PAY_TO` resolving to a real EVM settlement address.

`facilitator_ready` is separate: CDP key id + secret present.

Dogfood demo works without either. Live USDC settle needs both.

## Flip to configured (ops)
On the public host (Render / env):

```bash
GATE_X402_PAYTO=0x…   # real Base USDC receiver; not 0x0 / burn / < 2^16
CDP_API_KEY_ID=…
CDP_API_KEY_SECRET=…   # PEM EC or base64 Ed25519
# optional:
GATE_X402_FACILITATOR_URL=https://api.cdp.coinbase.com/platform/v2/x402
GATE_X402_AMOUNT_ATOMIC=2000   # $0.002 USDC default on prefinality challenge
```

Then `/health` → `x402.configured: true`, `facilitator_ready: true`, `gaps: []`.

`GATE_X402_DEMO_PAYTO` is intentionally ignored (prevents null-address “demo settles”).

## Working dogfood demo (shipped this pass)
| Surface | Role |
|---------|------|
| `GET /x402-mouth` | Human page for Foundation walkthrough |
| `GET /.well-known/x402-mouth.json` | Machine manifest + config gaps |
| `POST /demo/x402/agent` | Agent attempt → Gate evaluate → receipt |

Flow (AP2-shaped / x402 language):
1. Agent forms scoped mandate + pay intent  
2. Gate would issue HTTP 402 when payto configured  
3. Prefinality evaluate → GO / NO_GO / HOLD  
4. Signed receipt when keys provisioned (`demo: true` never actions a live rail)  
5. Live settle only if configured + facilitator_ready  

```bash
curl -sS -X POST "$ORIGIN/demo/x402/agent" \
  -H 'content-type: application/json' \
  -d '{}' | jq '{decision, halt, x402_config, foundation_pitch}'

curl -sS -X POST "$ORIGIN/demo/x402/agent" \
  -H 'content-type: application/json' \
  -d '{"force_breach":true}' | jq '{decision, evaluation}'
```

## Foundation pitch (door, not cold email)
> An agent hits a paid resource. Gate decides before settle. A stranger verifies the receipt.
> That is the Linux Foundation x402 / AP2-shaped door — Visa/MC/Google/Stripe/Amex/AWS/Circle founding orbit — with a live demo asset, not a PDF.

## Still not this pass
- Setting production secrets from the agent (needs human ops on Render)
- End-to-end live USDC settle on Base (requires those secrets + funded payer)
- Replacing issuing mouth — this is a parallel x402-framed dogfood
