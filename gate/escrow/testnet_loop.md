# Testnet loop — gate #4

Run **before** mainnet. Use test USDC only.

## Steps

1. Deploy `ClearanceEscrow` to a testnet (Base Sepolia / Eth Sepolia) with test USDC + Gate ECDSA signer address (immutable).
2. Set Gate index env: `GATE_ESCROW_CHAIN_ID`, `GATE_ESCROW_CONTRACT`, `GATE_ESCROW_USDC` (testnet values).
3. Principal approves + `lock` with known `mandateHash`.
4. Index the position in Gate keepers with `custody.venue=onchain_usdc` and matching `escrow_id` / `venue_ref`.
5. Observe a mandate-breaking transfer (or simulate).
6. Gate produces EIP-712 **Never** signature bound to `escrowId`, `keeper`, `evidenceHash`, `deadline`.
7. Keeper (or anyone) submits `liquidate(...)` on-chain.
8. Assert: keeper received bounty USDC; principal received residual; position status Liquidated.
9. Separate drill: Clear path `release` returns full amount to principal.
10. Separate drill: let TTL expire → `reclaimExpired` works **without** Gate signature.

## Pass criteria

All three paths succeed on testnet with test USDC balances changing as expected. Then set `GATE_ESCROW_TESTNET_OK=1`.

## Fail closed

Any path that moves funds without a valid sig (except principal expiry reclaim) = **do not** set the flag. Fix contract; re-audit if logic changed.
