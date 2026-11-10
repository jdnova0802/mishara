# Agent registration v0.1

Dated: 2026-11-10 (America/New_York). Status: draft. Publisher: Nisaba LLC.

This is an identity primitive Gate will accept. **Adopters: none.** A standard nobody else joins is not a standard (item 55).

## DID

`did:gate:<sha256-hex-40>` of the agent’s public key (base64 string as submitted). Session cookies are not an identity.

Register: `POST /v1/agents/register` `{public_key_b64, fuse_id?, label?}`

Lookup: `GET /v1/trust-record?did=` or `?fuse_id=`

## Not in v0.1

Cross-company zero-knowledge score proofs (item 51). Other issuers minting `did:gate`.
