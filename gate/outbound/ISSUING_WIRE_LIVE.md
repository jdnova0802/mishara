# Issuing wire — live (Nisaba / Gate)

**Done by agent (you fund cards):**

1. Stripe webhook created  
   - Endpoint: `https://gate.velaru.xyz/v1/issuing/authorization`  
   - Event: `issuing_authorization.request` only  
   - ID: `we_1UJhYV3b5zsnE0zsiM0wXobr`

2. Render `gate-api` env set + redeploy  
   - `GATE_ISSUING_ENABLED=1`  
   - `STRIPE_ISSUING_WEBHOOK_SECRET=whsec_…` (dashboard secret; not in git)

3. Verify after deploy  
   ```bash
   curl -s https://gate.velaru.xyz/.well-known/issuing-mouth.json | jq .config
   ```
   Expect: `issuing_enabled: true`, `money_real: true`, `webhook_secret_configured: true`

**You do:**

1. Stripe Issuing → **Add funds** (small float)  
2. Create **cardholder** + **virtual card**  
3. Optional card metadata for Clear/Never: `agent_id`, `max_amount`, `expected_merchant`, `daily_cap`  
4. One tiny real auth → should hit Gate mouth (&lt;2s AUTHORIZE/DECLINE)  
5. Dogfood without card: `POST https://gate.velaru.xyz/demo/issuing/mouth`

**Do not** paste webhook secrets into chat or commits.
