# Scenario 3 live gate — shipped runtime (not packaging)

**Invented / made live:** exclusive door before vendor bank-detail write.

## Mouth

May this vendor bank-detail **write** proceed — only after sealed out-of-band callback + dual approve, bound to account **fingerprints** (no raw account numbers).

FinCEN FIN-2016-A003 Scenario 3 typology → Clear / Seal / Go / Never on the ERP master-data write.

## Live endpoints

| Method | Path | Role |
|--------|------|------|
| GET | `/.well-known/scenario-3-gate.json` | Manifest |
| POST | `/demo/scenario-3/pre-change` | Evaluate → HALT or ALLOW + bind ticket |
| POST | `/v1/scenario-3/pre-change` | Same (non-demo) |
| POST | `/demo/scenario-3/apply` | Consume ticket at apply door (`clearance_only`) |
| GET | `/v1/seal?event_id=` | Stranger Seal on the pre-change event |
| POST | `/v1/pas/bind-ticket/redeem` | Also works with `spend_kind=vendor_bank_change` |

## Fail closed when

- `callback_confirmed` false → `callback_not_confirmed`
- `dual_approve` false → `dual_approve_required`
- missing `callback_channel`
- old/new account fp missing or not sha256 hex
- old_fp == new_fp
- raw `account_number` / `routing_number` → 400 `no_pii` / `no_raw_bank`
- ticket replay → HALT

## Married write

`POST /v1/scenario-3/apply/{change_id}` · `spend_kind=vendor_bank_change` · `job_id=s3:{vendor_id}:{change_id}`

Gate does **not** execute QuickBooks/NetSuite — `write_executed: false`, `clearance_only: true`.

## Code

- `gate/scenario_3_gate.py`
- `spend_protocol.intended_vendor_bank`
- routes in `app.py`
- page `/scenario-3` shows live curl

## Tests

`test_scenario_3_live_halt_without_callback` · `test_scenario_3_live_go_ticket_and_apply` · `test_scenario_3_rejects_raw_account_number`
