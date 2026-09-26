# PASTE — Tell dekskro: make Issuing workflow lock LIVE

**26 Sep 2026.** Ops only. No new SKU. No new secrets.

---

## Message (copy below the line)

---

Make live — Issuing workflow category lock

**PR:** https://github.com/jdnova0802/mishara/pull/142  
**What:** Gate workflow lock on Stripe Issuing auth. Stripe `spending_controls` stays MCC floor. Card metadata `allowed_categories` enforced **before** Clear; deny mints signed `claim_scope`. MCC ≠ cart.

### Deploy

1. Mark PR **#142** ready for review (undraft) if needed, then **merge into `main`**.
2. Confirm Render **gate-api** (`srv-dai3n0u1egvs73dbd94g`) auto-deploys from `main`. If not → Manual Deploy → latest commit.
3. **No new env vars.** Existing `GATE_ISSUING_ENABLED` / webhook secret / Stripe key stay as-is.

### Verify (after deploy green)

```bash
curl -sS https://gate.velaru.xyz/.well-known/issuing-mouth.json \
  | python3 -c "import sys,json; m=json.load(sys.stdin); print(m.get('workflow_lock',{}).get('spec')); print(list((m.get('config') or {}).get('layers') or {}))"
```

Expect:
- `gate-issuing-workflow-lock-v1`
- layers include `platform_mcc_floor` and `gate_workflow_lock`

```bash
# Deny: restaurant vs fuel-only allowlist
curl -sS -X POST https://gate.velaru.xyz/demo/issuing/mouth \
  -H 'content-type: application/json' \
  -d '{"merchant_category":"eating_places_restaurants","allowed_categories":["automated_fuel_dispensers"],"max_amount":"50.00"}' \
  | python3 -c "import sys,json; b=json.load(sys.stdin); print(b['approved'], b['workflow_lock']['signal'], b['claim_scope']['boundary'])"
```

Expect: `False workflow_category_denied gate_issuing_workflow_category_lock`

```bash
# Allow: category inside allowlist
curl -sS -X POST https://gate.velaru.xyz/demo/issuing/mouth \
  -H 'content-type: application/json' \
  -d '{"merchant_category":"computer_software_stores","allowed_categories":["computer_software_stores"],"max_amount":"50.00"}' \
  | python3 -c "import sys,json; b=json.load(sys.stdin); print(b['approved'], b['decision'], b['workflow_lock']['ok'])"
```

Expect: `True GO True`

**Done when:** deny curl returns `approved: false` + `workflow_category_denied` + claim_scope boundary `gate_issuing_workflow_category_lock`.

### Real cards (after dogfood green)

Optional — not required for “live”:
- Stripe Dashboard → card → **spending_controls** = MCC floor
- Same card **metadata** `allowed_categories` = comma-list (Gate workflow lock; ≤ floor)
- Real auth still hits `https://gate.velaru.xyz/v1/issuing/authorization` (&lt;2s)

### Honesty

- Does **not** invent SKU/IIAS/Fleet product-code lock — MCC ≠ cart.
- Does **not** rebuild Stripe MCC engines.
- Does **not** move Monday diligence cash.

### Not this deploy

- **#141** hunt pastable only (already answered by #142)
- **#137** OTS Bitcoin anchor — separate merge; needs `GATE_OTS_DIR` + stamp cron

---

## File refs

- Code: `gate/issuing_mouth.py` (`WORKFLOW_SPEC`, `workflow_category_check`, `decide`)
- Demo: `POST /demo/issuing/mouth`
- Detail: `gate/outbound/PASTE_ISSUING_WORKFLOW_LOCK.md`
- Hunt: `gate/outbound/PASTE_CARD_WORKFLOW_LOCK_HUNT.md`
