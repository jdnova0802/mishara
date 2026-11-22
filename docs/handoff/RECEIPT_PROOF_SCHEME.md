# Receipt proof scheme (domain separation, shared links)

Merkle hashing changed in PR #305: new leaves are `SHA-256(0x00 || data)`, inner nodes `SHA-256(0x01 || left || right)`. Tree shape is still pairwise with odd-leaf duplication. That is **RFC 9162-style domain separation**, not RFC 9162.

## Shared Issuing URL

The only Bind Room / outreach / pitch URL that names a specific authorization is:

https://gate.velaru.xyz/v1/issuing/authorization/iauth_1URXhX3b5zsnE0zsR1QikRhn

in `gate/outbound/PASTE_CLAUDE_ISSUING_PROOF.md` (2026-10-17 Kindle Svcs, `webhook_approved`).

That GET is a **JWT receipt**. JWT verify does not depend on Merkle prefixes. If the row is still in the live DB, the token still verifies.

Other `iauth_*` ids in that paste (`iauth_1URXFd…`, `iauth_1URXSz…`, `iauth_1URXYU…`) are **failed** wire attempts, not published receipts.

No other customer, Bind Room, or pitch file in this repo cites a specific `/v1/issuing/authorization/<id>` or a saved `/.well-known/receipt/<event_id>/proof.json` from before the prefix change.

## What can break

A **saved inclusion proof** (sibling list + root) computed under the old pairwise `SHA-256(left||right)` scheme will not match a **new** published evidence-head. Cached `root_hash` from `/.well-known/evidence-head.json` taken before the change will not equal the live head over the same leaves.

## Fallback (not silent)

`verify_inclusion` / `POST /v1/evidence/verify-inclusion` and `POST /v1/prefinality/verify` (when an inclusion body is sent) try:

1. Current RFC 9162-style prefixes
2. Pre-2026-11-22 pairwise hashing (`gate-sha256-pairwise-v0`)

If (2) matches, `predates_current_proof_scheme: true` and `proof_scheme_plain` names the old tree.

If neither matches, the response is **not** a bare failure: `proof_scheme_plain` says the receipt predates the current proof scheme or the path matches neither tree.

`GET /.well-known/receipt/<event_id>/proof.json` for an existing bind event with no current leaf returns **409** with the same sentence, not an empty 404 page.
