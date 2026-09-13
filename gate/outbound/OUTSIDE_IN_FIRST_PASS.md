# Outside-in first pass — mouth diligence checklist

**Use:** before deposit clears, or first 60–90 min after it clears.  
**Access:** public docs + reasonable inference only. No internal systems.  
**Goal:** name the irreversible write path and whether clearance looks married to commit — or check-once.

**Target:** _______________________ **Date:** _______ **Pass owner:** _______

---

## 0) Find the API surface — fastest path (5–10 min)

Tick the first hit that works; stop hunting once you have OpenAPI/reference + auth model.

| Try | URL / query | Hit? |
|-----|-------------|------|
| `docs.` / `developer.` / `api.` subdomain | | ☐ |
| Site footer → Developers / API / Docs | | ☐ |
| Google: `"{company}" API reference` · `site:{domain} idempotency` · `site:{domain} webhook` | | ☐ |
| Status/changelog page (often links the real docs) | | ☐ |
| GitHub org: `openapi.yaml` / `swagger` / SDKs | | ☐ |
| Postman public workspace / Softledger-style portal | | ☐ |

**API docs URL:** ________________________________  
**Auth model (API key / OAuth / mTLS / signed):** ________________________________

If no public write API → note partner/portal-only and jump to §5 inference.

---

## 1) Write path — what can actually leave / bind / pay (10–15 min)

Name **one** irreversible mouth (prefer the leave path: payout, withdraw, transfer, bind, issue, settle).

| Question | Notes |
|----------|-------|
| Endpoint / RPC / dashboard action that commits? | |
| Request fields that define *this* write (amount, destination, job/id)? | |
| Async? (202 + webhook / status poll) or sync 200 = done? | |
| What does “success” mean in their words (posted / submitted / settled)? | |
| Can a second product path skip this door (UI, batch CSV, partner SFTP)? | |

**Mouth one-liner:**  
`{entity} can complete {write} via {path} when {condition}.`

---

## 2) Retry / timeout / partial failure (10–15 min)

Search docs for: `idempotency`, `Idempotency-Key`, `replay`, `dedupe`, `client_token`, `request_id`, `exactly once`, `at least once`.

| Signal | Y / N / ? | Where |
|--------|-----------|-------|
| Client-supplied idempotency key documented? | | |
| Key scope + TTL stated? | | |
| Timeout guidance (“retry safe” vs “check status first”)? | | |
| Duplicate webhook / event delivery acknowledged? | | |
| Partial batch behavior documented (some rows commit)? | | |

**Inference if silent:** treat as **at-least-once + check-once** until proven otherwise. Write that as a gap, not a fact.

---

## 3) Clearance → write — married or check-once? (10–15 min)

Looking for a **re-check at commit**, not “we validated earlier.”

| Pattern in docs | Looks like | Mark |
|-----------------|------------|------|
| Authz / approval / risk check, then later “submit/execute” with no fresh check | Check-once | ☐ |
| Token / intent / quote expires; execute must present same bound request | Married / short TTL | ☐ |
| Status machine: `authorized` → `capturable` → capture is separate call | Possible gap between may and write | ☐ |
| Webhook “approved” then partner pushes funds on their own schedule | Clearance ≠ execution | ☐ |
| Explicit “revalidate before settle” / “authorization must be live at capture” | Commit-time check | ☐ |

**Call (one box):** ☐ Married-looking ☐ Check-once-looking ☐ Unclear (docs thin)

**Evidence line (quote or URL §):** ________________________________

---

## 4) Stranger-openable halt? (5 min — inference only)

From public material only: if an allowed write is in flight, is there a **documented** kill/freeze that a non-insider path can’t bypass?

| | Y / N / ? |
|--|-----------|
| Account/API key freeze stops in-flight writes? | |
| Dashboard cancel after “submitted”? | |
| Support-only halt (no self-serve)? | |

**Halt gap one-liner:** ________________________________

---

## 5) Pass output — paste into working notes (2 min)

```
TARGET:
MOUTH:
DOCS:
WRITE PATH:
IDEMPOTENCY: yes / no / unknown —
CLEARANCE→WRITE: married / check-once / unclear —
HALT GAP:
OPEN QUESTIONS (max 3):
1.
2.
3.
ENOUGH TO SCOPE DEPOSIT DELIVERABLE? yes / no
```

---

## Time box

| Pass | Clock | Stop when |
|------|-------|-----------|
| **First pass (this checklist)** | **45–75 min** | Mouth named + idempotency/clearance call + 3 questions |
| Hard cap | **90 min** | Docs thin → mark “portal/partner-only” and stop |
| Not in first pass | — | Live probes, accounts, scrape-behind-login, legal review |

Under a **72h** delivery clock: run this once at kickoff; deepen only the named mouth. Don’t boil the ocean on every endpoint.
