# Agent Receipt Protocol v0.1

Dated: 2026-11-10 (America/New_York). Status: public draft. Publisher: Nisaba LLC.

This is the checkable object Gate already issues. It is not a promise of a future chain.

## Object

A receipt is a canonical JSON object, SHA-256 hashed, Ed25519-signed. Envelope fields (`receipt_hash`, `receipt_signature`, `dfir`, `created_at` display time on some payloads) are **outside** the hash.

Minimum labeled fields (DFIR envelope on the public payload):

- `event_id`
- `agent_key_id` (signer fingerprint)
- `payload_hash_sha256`
- `prev_receipt_hash` (ledger position)
- `decision` (ALLOW / BLOCK / HALT / HOLD)
- `verify` URL a stranger can open with no login

## Verify

1. Fetch `/.well-known/receipt/<event_id>.json`
2. Canonicalize the signed object (sorted keys, no whitespace)
3. SHA-256 must equal `receipt_hash`
4. Ed25519 verify with the published public key, not a key named inside the receipt

CLI: `python3 gate/offline_verify.py <receipt.json>` (dead-hand: you pass the key).  
HTTP: `GET /badge/verify.svg?event_id=`  
MCP: tool `verify_receipt`

## Not in v0.1

Parametric insurance triggers, zero-knowledge linkage, and computer-vision authenticity.
