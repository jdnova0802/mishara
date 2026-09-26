# PASTE — Issuing workflow lock (built from card hunt)

Branch: `cursor/issuing-workflow-lock-ce84`  
Hunt: `PASTE_CARD_WORKFLOW_LOCK_HUNT.md` (MCC floor ≠ purpose lock)

---

## Verdict

**Yes — buildable.** Not a new issuer. Pair Stripe’s MCC floor with a Gate workflow category lock on the Issuing auth mouth.

| Layer | Who | What |
|-------|-----|------|
| 1. Platform MCC floor | Stripe `spending_controls.allowed_categories` | Hard MCC at Stripe — **do not rebuild** |
| 2. Gate workflow lock | Card metadata `allowed_categories` + `job_id` / mandate | Fail-closed before Clear; signed `claim_scope` |

MCC ≠ cart (IRS Notice 2006-69 IIAS; Visa Fleet product codes). Gate cannot invent SKU-grade proof.

---

## What shipped

- `WORKFLOW_SPEC = gate-issuing-workflow-lock-v1`
- `workflow_category_check` — allow / deny / missing (fail closed)
- `decide()` runs lock **before** Clear; deny skips evaluate
- Deny mints signed `claim_scope` (`boundary=gate_issuing_workflow_category_lock`, `mcc_is_not_cart`)
- Dogfood + demo accept `allowed_categories` / `merchant_category` / `job_id`
- Manifest documents the two layers + why not SKU-grade

## Dogfood

```bash
curl -sX POST "$GATE/demo/issuing/mouth" -H 'content-type: application/json' \
  -d '{"merchant_category":"eating_places_restaurants","allowed_categories":["automated_fuel_dispensers"],"max_amount":"50.00"}'
# → approved:false, workflow_lock.signal=workflow_category_denied, claim_scope present
```

## Not

- Not another BIN/processor
- Not rebuilt Lithic/Highnote/Stripe MCC engines
- Not FSA IIAS / SNAP / Fleet SKU lock (needs merchant participation Gate doesn’t have)
- Not Monday diligence cash

## Primary

- https://docs.stripe.com/issuing/controls/spending-controls
- IRS Notice 2006-69 (IIAS); Visa Fleet 2.0 product category controls
