# ClearanceEscrow — before any real USDC

## Custody framing (must hold)

| Claim | Status after harden |
|-------|---------------------|
| Contract holds USDC; Gate wallet does not | Yes |
| Gate is privileged `msg.sender` on release/liquidate | **No — removed** |
| Pause / upgrade / sweep / setSigner | **Absent by design** |
| Anyone submits EIP-712 Clear / Never | Yes |
| Principal reclaim after expiry without Gate | Yes |
| Gate signature still *authorizes* movement when submitted | Yes — verifier shape; **legal opinion still required** |

Old `gateAttestor` caller role was a partial custody claim. That path is gone.

## Four gates (all required)

1. **Independent audit** — `GATE_ESCROW_AUDIT_PASSED=1` after report  
2. **Key-path human confirm** — `GATE_ESCROW_KEYPATH_REVIEWED=1` after reviewing Sol + `escrow_preflight.key_path_review()`  
3. **Legal sanity** — `GATE_ESCROW_LEGAL_OK=1` after opinion on verifier-not-transmitter  
4. **Testnet full loop** — `GATE_ESCROW_TESTNET_OK=1` after test USDC dogfood  

```bash
curl -s "$GATE/.well-known/escrow-preflight.json" | jq .
```

`real_usdc_allowed` is false until all four pass. Do not treat contract deploy env alone as permission to take third-party funds.

## Flow

1. Principal `lock(escrowId, agent, amount, mandateHash, ttl)`  
2. Clear: anyone `release(escrowId, evidenceHash, deadline, sig)`  
3. Never: anyone `liquidate(escrowId, keeper, evidenceHash, deadline, sig)` — first valid wins  
4. After `expiresAt`: principal `reclaimExpired(escrowId)` — no Gate  

## Env (index only — not a substitute for the four gates)

```
GATE_ESCROW_CHAIN_ID=
GATE_ESCROW_CONTRACT=
GATE_ESCROW_USDC=
GATE_ESCROW_AUDIT_PASSED=
GATE_ESCROW_KEYPATH_REVIEWED=
GATE_ESCROW_LEGAL_OK=
GATE_ESCROW_TESTNET_OK=
```

## Testnet loop

See `testnet_loop.md`.
