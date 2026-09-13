# Atomic authority at the durability boundary

Standing design rule (Nisaba / Gate):

**Any consequence-bearing endpoint — spend, bind, unlock, receipt issue — must
perform the authorization check and the durable effect inside one atomic
transaction, not as two separate calls with a window between them.**

## Why

CommitGuard / Temporary Authority, Permanent Effects (arXiv:2607.10487):
authority that was valid earlier in a hop is not authority at commit time.
Gate measured this on licensed bind tickets: `require_live()` then later
`consume_bind_ticket()` allowed mid-flight parent DEAD to still consume.
Fixed by re-checking LIVE inside the same `BEGIN IMMEDIATE` transaction as
the consume UPDATE (`gate/db.py`).

## Rule

1. Prefer: check + write in one DB transaction (`BEGIN IMMEDIATE` / equivalent).
2. If the durable write is external (e.g. PolicyCenter bind-only), call
   `license_fuse.require_live_at_effect()` (or equivalent) in the same moment
   as that write — never trust a prior `allow_bind` bit alone.
3. Gate itself remains clearance-only: `write_executed` is always false from
   Gate; the irreversible write is the exclusive door’s job.

## Tests

- `gate/test_commitguard_race.py` — mid-flight DEAD between require_live and consume
- `gate/test_post_redeem_surface.py` — no Gate-owned bind write; effect-time recheck
