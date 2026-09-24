# Wedge candidate — Vendor bank-change halt (agentic + verify)

**Rank:** #2 cash-this-month after insurance Diligence/Bind. Outranks agentic chargebacks for near-term money. Outranks Bounded Autonomy.

**One line:** Before AP updates vendor bank details or releases ACH/wire, prove who authorized the change, what the agent/human was allowed to do, that out-of-band callback happened, and that a stranger can verify the receipt — or the write is NEVER.

---

## Why it fits Nisaba (architecture)

Identical Clear / Seal / Go / Never mouth:

| Mouth | Vendor-bank change |
|-------|-------------------|
| **Clear** | What was requested (old → new routing/account) |
| **Seal** | Stranger-verifiable receipt: callback to *on-file* number, dual approve, hold |
| **Go** | Prefinality — may the ERP write / payment run proceed |
| **Never** | Agent must not write bank details or release payment |

Industry is deploying **AI agents that screen** bank-change requests — and explicitly must **not** approve, write ERP, or pay (Gatekeeper LuminIQ, Vorp, Jovis, 2026 AP guides). That’s a control gap Gate already answers: ticket bound to one write fingerprint (`spend_protocol`), fail-closed on irreversible hop.

Also crosses **crime-policy / BEC insurance**: carriers deny social-engineering claims when callback / written agreement wasn’t followed. Same diligence buyer energy as Vesttoo LOC — “prove the verify step before the money moved.”

---

## Why cash this month (not 18 months)

| Lever | Fit |
|-------|-----|
| Offer | Same free 72h REVIEW → paid Diligence ($2.5k–$8k) — **no new SKU** |
| Buyer | Mid-market Controller / AP lead / community-bank ops — shorter cycle than Visa networks |
| Urgency | BEC + vendor redirect still the #1 cash loss; AI agents in AP make “who may write” acute *now* |
| Proof | Public pages + callback policy + one named change path — Plan B depth enough |

**Not** inventing chargeback product for Chargeflow. **Reuse** `/diligence` + spend-protocol language.

---

## Buyers to hit (after insurance Tue 10 — don’t hijack)

Plan B style, one pain line:

1. Mid-market Controllers (LinkedIn / AP forums) — vendor redirect loss stories  
2. Community / regional bank treasury ops — crime-bond callback denials (ABA Insurance Services posture)  
3. AP automation vendors selling bank-change *agents* — they need a halt receipt, not another screener  
4. Crime / cyber brokers placing social-engineering endorsements — diligence on verify-before-pay

---

## Do / don’t

**Do:** park as Wedge #2; after Tue insurance 10 + any REVIEW chase, draft 3–4 Plan B REVIEW emails using this mouth.  
**Don’t:** build a new surface, MCP gateway, or Visa dispute product this month.  
**Architecture win when sold:** first live who-may-spend / NEVER on a non-insurance write — hardens Gate for chargebacks later.

---

## One-sentence pitch (REVIEW)

> Free 72-hour review of one vendor bank-change / pay path: where an agent or email can still update routing or release ACH before sealed callback + dual approve exists as a stranger-verifiable receipt.
