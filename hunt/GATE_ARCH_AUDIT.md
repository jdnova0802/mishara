# Gate architecture audit (Sept 2026 agent-governance patterns)

Verdict on Claude’s checklist. Check against code, not slides.

## 1. Identity — agree, was a real gap, now closed on the hop token

Mandate already split `human_principal_id` and `agent_id` (living authority). The **hop receipt** did not: Right-to-Act / Prefinality JWTs used a single `sub` (the agent). A stranger opening that token could not see the delegator independently.

Now the signed receipt carries both: `agt` (agent) and `prn` (human principal). TTL on the hop remains minutes (`DEFAULT_TTL_SECONDS = 300`). Mandate TTL staying longer is intentional — reconstruct-at-consequence is the live check, not a day-long access token.

## 2. Policy order — agree, order was wrong

Fail-closed as a slogan was already true for missing fields / unknown sinks / unsigned prod. The **engine order** was not deny → require_approval → allow → default-deny. Allow-list ran first; empty policy defaulted to EXIST.

Right-to-Act now enforces: explicit deny, then HOLD (`hold_actions` / `require_approval`), then allow-list, then default-deny. Living mandate (`require_mandate`) is the allow surface when no list is given. `policy_cases.yaml` locks the order.

## 3. Audit log — partly already Gate, partly tightened

Already: bind receipts are Ed25519-signed and hash-chained (`prev_receipt_hash`). Gate does not execute the irreversible write (`write_executed: false`); the exclusive door does.

Tightened: authorization JWT is signed **before** the EXIST ticket is inserted (audit-first). RTA decisions chain `prev_decision_hash`. Credential-bearing args are SHA-256 redacted in the public summary; `args_hash` stays correlatable.

## 4. Policy-as-code tests — agree, was missing, now a CI gate

`gate/policy_cases.yaml` + `gate/test_policy_as_code.py`. Expected deny / hold / allow / default-deny run against the real engine. Wired into `.github/workflows/gate.yml`.

## 5. Gateway-as-mouth — agree, already the product, no new build

Gate is clearance-only. The agent does not hold the downstream write. The exclusive door is the only mouth. Check, not a SKU.

## 6. Trust scoring — agree it is a decision, and the decision is **no**

Do not build a behavioral trust score that auto-revokes or auto-allows. A moving score is not stranger-recomputable. It fights the write-stop thesis (static fail-closed + living reconstruct). Mandate death / continuity already kill a lineage on purpose. That is enough.

## 7. Vocabulary — translate outward, do not rename the object

Buyers already say: PEP/PDP, deny-overrides, short-lived tokens, agent vs user identity, tool gateway. Map, don’t rebrand:

| They say | Gate is |
| --- | --- |
| PEP (enforcement) | the mouth / exclusive door |
| PDP (decision) | Right-to-Act + Prefinality evaluate |
| deny-overrides | policy precedence above |
| agent identity | `agt` / `agent_id` |
| user / delegator | `prn` / `human_principal_id` |
| short-lived token | RTA ticket + JWT, minutes |
| require approval | HOLD |
| allow / deny | EXIST / NONEXIST |

Keep EXIST/NONEXIST internally. That is the distinctive object. Outbound copy may say GO / NO-GO / HOLD where the rail already does.

Claude’s paste cut off mid-sentence on (7). If the rest was “OPA/Cedar/MCP gateway,” same rule: speak those words at the door; do not become those products.
