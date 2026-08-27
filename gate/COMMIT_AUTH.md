# Commit-time authorization — Claude pressure test

**Not mountain.** Honest answers on Bind Ticket / epoch / exclusion before public pitch.  
**Spec:** `gate-commit-auth-v1` · `/.well-known/commit-auth.json`

## Front-page sentence (keep)

> Signatures prove a hop occurred. Tickets prove the hop is still allowed to spend, right now, once, for this job and this write.

Ed25519 is still the **ink**. Tickets / epoch are **authorization** (stranger-grade today). We do **not** claim better crypto than Ed25519.

JSON key: `authorization_vs_attestation` (was `greater_than_ed25519` — renamed so security readers don't hear "we beat Ed25519").

---

## Claim grades (do not mix voices)

| Primitive | Grade today | Buyer / stranger voice? |
|-----------|-------------|-------------------------|
| Bind Ticket | **stranger** | Yes |
| Epoch lock | **stranger** | Yes |
| Exclusion | **map honesty** | **No** — internal-consistency until TSA/root anchored |

**Verbatim hold:** *Map honesty today, not stranger-grade absence.*  
Keep the feature. Refuse the claim it can't support. If exclusion ships on the same page in the same voice as ticket/epoch, the weakest claim sets credibility of the other two.

---

## Five pressure tests

### 1. Naming — **fixed**
`greater_than_ed25519` → `authorization_vs_attestation`.

### 2. Exclusion proofs need a committed root — **gap named**
Today: sorted Merkle neighbors + signed tree head over Gate's redeemed-ticket map.  
**Missing for stranger-grade absence:** TSA / RFC 3161 root fixed at a time. Until then: **map honesty today, not stranger-grade absence.**

### 3. Whose clock enforces TTL — **server + skew**
Redeem uses **server UTC**. Client must present `now`; skew fails closed. TSA-anchored TTL optional later.

### 4. Single-use — **verbatim policy**
> Burn on success only, failed redeem retryable, post-burn fail re-issues from fresh LIVE.

Do not resurrect consumed tickets. Semantic replay ≠ new grant.

### 5. Prior art — **precise novelty**
Shape overlaps macaroons / Biscuit / UCAN / ZCAP-LD.  
**Pitch the epoch lock:** HALT no admin can lift without real CHARGE — same trust class as BYOK co-sign.

---

## Pitch + outbound

**Pitch order:** epoch lock → ticket vs signature → BYOK.

**Outbound:** costume stays AI governance + commit control — but **lead with commit control / the moment**, not the crowded category.  
Subject-line shape: *what can't run once the ticket's gone* — not "AI governance platform."

---

## Public check (ship day)

```bash
curl -sS https://gate.velaru.xyz/.well-known/commit-auth.json | jq .
# expect: authorization_vs_attestation, bind_ticket.claim_grade=stranger,
#         exclusion.claim_grade=map_honesty, their_production=false
```
