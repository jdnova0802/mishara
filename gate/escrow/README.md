# ClearanceEscrow

On-chain foreign vault for clearance keepers. **Gate does not hold these funds.**

## Flow

1. Principal `lock(escrowId, agent, amount, mandateHash, ttl)` — USDC pulled into contract  
2. Gate Clear → attestor `release` → principal gets USDC  
3. Breach → attestor `liquidate(escrowId, keeper, evidenceHash)` → keeper bounty + residual to principal  

## Env (Gate index)

```
GATE_ESCROW_CHAIN_ID=
GATE_ESCROW_CONTRACT=
GATE_ESCROW_USDC=
```

Until set: `money_can_enter=false` for on-chain venue.

## Deploy note

Audit before mainnet. `gateAttestor` should be a narrow verifier (EIP-712 / Ed25519 adapter), not a hot EOA with discretionary withdraw. Contract has no owner sweep of user locks.
