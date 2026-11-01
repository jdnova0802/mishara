# Paste — x402 Foundation door (demo asset)

**Live dogfood (no USDC moved):**
- Page: `https://gate.velaru.xyz/x402-mouth` (or current origin)
- POST: `/demo/x402/agent` → agent attempt → Gate evaluate → receipt
- Breach: `{"force_breach":true}` → expect NO_GO

**What “configured” means on /health:**
- `x402.configured` = `GATE_X402_PAYTO` set to a real settlement address
- `x402.facilitator_ready` = CDP API key + secret present
- `x402.gaps` = human-readable missing pieces
- Dogfood works with both false; live settle needs both true

**One-liner for Foundation / AP2 orbit:**
An agent hits a paid resource. Gate decides before settle. A stranger verifies the receipt. That’s the door — not a cold email.
