# Commit-time authorization — Claude pressure test

**Not mountain.** Honest answers on Bind Ticket / epoch / exclusion before public pitch.  
**Spec:** `gate-commit-auth-v1` · `/.well-known/commit-auth.json`

## Front-page sentence (keep)

> Signatures prove a hop occurred. Tickets prove the hop is still allowed to spend, right now, once, for this job and this write.

Ed25519 is still the **ink**. Tickets / epoch / exclusion are **authorization**. We do **not** claim better crypto than Ed25519.

JSON key: `authorization_vs_attestation` (was `greater_than_ed25519` — renamed so security readers don't hear "we beat Ed25519").

---

## Five pressure tests

### 1. Naming — **fixed**
`greater_than_ed25519` → `authorization_vs_attestation`. Crank signal removed.

### 2. Exclusion proofs need a committed root — **gap named**
Today: sorted Merkle neighbors + signed tree head over Gate's redeemed-ticket map (`exclusion.py` → `evidence_log.signed_tree_head`).  
**Missing for stranger-grade absence:** TSA / RFC 3161 (or CT-style) **root fixed at a time** so "no leaf" is falsifiable later. Until that anchor ships, exclusion is **Gate-map honesty**, not global non-existence.  
`their_production: false` stays. RFC 3161 earn-keep is the upgrade path.

### 3. Whose clock enforces TTL — **server + skew (good enough); TSA optional later**
Redeem uses **server UTC** (`ticket.redeem` → `datetime.now(timezone.utc)`). Client must present `now`; `command_radiation.check_now` fails closed on missing / invalid / skew.  
Client clock alone cannot extend `not_after`. TSA-anchored TTL is nicer later; not required for seed honesty.

### 4. Single-use failure mode — **pick and document**
**Pick:** burn on successful redeem only (atomic `consume_bind_ticket`). Failed redeem (skew, mismatch, dead parent) → ticket **not** burned → retry with same ticket while inside TTL.  
Replay after successful consume → HALT.  
If write fails **after** burn → **re-issue** a new ticket from a fresh LIVE hop (semantic replay ≠ new grant). Do not resurrect consumed tickets. Carrier ask: document this on the call.

### 5. Prior art — **precise novelty**
Shape overlaps: macaroons, Biscuit, UCAN, ZCAP-LD (TTL + single-use + request fingerprint).  
**Pitch the epoch lock / no-admin-CHARGE:** HALT that Gate cannot quietly lift without a real CHARGE — same trust class as BYOK co-sign ("we can't forge alone / undo alone"). Patent: don't claim "capability token" alone.

---

## Pitch order (Claude-aligned)

1. **Epoch lock** — you can't quietly undo the block either  
2. **Ticket vs signature** — attestation + authorization  
3. **BYOK / stranger verify** — Velaru cannot forge alone  

Outbound still: AI governance + commit control. Not CIC mythology.
