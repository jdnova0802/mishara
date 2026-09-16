# Re-approach v3 — payment-ops review (not disclosure)

**Decision: (b), smaller than the 12.** Do not rebuild the remaining 25. Do not re-spray the 12 S-tier `security@` / `psirt@` / `vdp@` / `soc@` / `responsibledisclosure@` inboxes. Those addresses **are** the disclosure queue. New copy on the same To: still gets the playbook.

**Test set: T1–T3 only (Tipalti, Fireblocks, Anchorage).** Stop after those three unless a human answers as a vendor, not as a VDP.

**T4 Increase is dead.** Arnav mailed from the security alias, not as a named business contact. No named human at Increase. Do not invent a To:. Do not mail `security@increase.com` again.

## SEND LOCK — **GO** (checked 16 Sep 2026 after gate-api deploy)

`python3 gate/outbound/check_live_diligence.py` printed **GO**.

- `https://gate.velaru.xyz/diligence/offer.json` → `spec=gate-ops-review-v2`, ask **Reply REVIEW — no invoice until after the free review.**
- HTML has **Free 72-hour review**. No `Reply DEPOSIT`.

T1–T3 may paste from `hello@velaru.xyz`. Agent has no SMTP. **T4 stays dead** (Arnav = security alias, not a business decision-maker).

Render `gate-api` tracks `cursor/oligarch-grade-25ad` again, with v2 on that branch (PR #64 fast-forwarded). Switching the service back will not restore DEPOSIT-now.

---

## Gut-check (the open questions)

**(a) vs (b).** (b). Research time per target is real; burning it on 25 names before the *inbox class* is fixed just reprints the same miss. Wave A already used the generic line. Scaling research on unsent names while S-tier sits in SOC queues teaches nothing.

**Free review vs funnel math.** The $2,500 was never the objection. Categorization was. Price does not get read once the ticket is a disclosure. Free 72h is cheaper than another 25 researched deposits that never leave the vuln queue. Deposit/retainer after a memo they asked for.

**Faster specificity than a full research pass.** One **public named object** per company (a documented API or status, with a URL). Not a private write-path map. Not “where a stranger can complete the write.” That second thing is how the first batch got filed.

**Do not send to:** `security@`, `psirt@`, `vdp@`, `soc@`, `responsibledisclosure@`, `privacy@`. Privacy and SOC are still intake queues.

**Do not:** D3/D5 “still the same ask / reply DEPOSIT.” Kill those templates.

---

## Banned vocabulary (body, subject, page)

`DEPOSIT` as a reply token · due now · pay the page · vulnerability / vuln · irreversible write complete without may · stranger-openable · halt gap a stranger can open · Security / Product Ops · bounty · pentest-as-pitch · can ≠ may

---

## #T1 — Tipalti — `contact@tipalti.com`

**Why this inbox:** `contact@`, not Security. Wave A name; same generic line if they already got it — this is a replacement, not a second deposit ask.

**Public object:** Mass Payments / payout API: create payee → confirm payable (`Get list of payees`) → create payment batch. Docs: https://documentation.tipalti.com/reference/onboard-payees-and-create-payments and https://tipalti.com/mass-payments/

**To:** `contact@tipalti.com`  
**Subject:** Free 72-hour review of Tipalti payment-batch vs payee payable

```
Payments / payouts ops — Tipalti

Nisaba LLC. Vendor review of one named payout path.

Your public payout flow is: create the payee, confirm they are payable, then create a payment batch (Tipalti REST: onboard payees and create payments). We will spend 72 hours writing a short memo on where that payable check is supposed to sit relative to batch create — from those docs plus anything you want to send.

No charge. No invoice. No obligation. If the memo is useless, delete it.

Reply REVIEW with the right ops owner if this should not sit with Contact, or ignore.

Page: https://gate.velaru.xyz/diligence
```

---

## #T2 — Fireblocks — `info@fireblocks.com`

**Why this inbox:** `info@`, not PSIRT.

**Public object:** Fireblocks is a digital-asset transfer / wallet-ops platform (product pages at fireblocks.com). Keep the ask on **transfer approval before broadcast**, which they already sell as a product, not a missing halt.

**To:** `info@fireblocks.com`  
**Subject:** Free 72-hour ops review of transfer approval before broadcast

```
Payments / transfer ops — Fireblocks

Nisaba LLC. Vendor review of one named transfer path.

You already productize approval before a transfer is broadcast. We will spend 72 hours writing a short memo on how that approval is supposed to sit relative to broadcast, from your public product pages plus anything you send.

No charge. No invoice. If it should go to a named transfer-ops owner, forward once.

Reply REVIEW or ignore.

https://gate.velaru.xyz/diligence
```

---

## #T3 — Anchorage Digital — `contact@anchorage.com`

**Why this inbox:** `contact@`. Federally chartered digital-asset bank — talk to **bank ops / payments**, never Security.

**Public object:** Anchorage Digital Bank N.A. — qualified custodian; settlement / withdrawal is the commercial object on anchorage.com.

**To:** `contact@anchorage.com`  
**Subject:** Free 72-hour review of withdrawal vs settlement ops

```
Bank / payments ops — Anchorage Digital

Nisaba LLC. Vendor review of withdrawal versus settlement.

You are a qualified custodian. The path we would read in 72 hours is withdrawal versus settlement: where permission is supposed to sit before assets leave, from your public bank/custody pages plus anything you send.

No charge. No invoice. No obligation.

If Contact is the wrong desk, one forward to payments ops is enough. Reply REVIEW or ignore.

https://gate.velaru.xyz/diligence
```

---

## #T4 — Increase — **DEAD**

Arnav’s mail came from the **security alias**, not a named person who engaged as a business contact. Cursor’s own rule was: if Increase never produced a named human, skip T4. That is the case.

- Do not send T4.
- Do not address Arnav.
- Do not mail `security@increase.com` again with nicer copy.
- RTP `require_approval` remains a public object for later **if** a real payments-ops To: appears. It is not a send.

---

## Explicitly parked

| Slot | Why parked |
|------|------------|
| S-tier #1–13 `security@` / `psirt@` / `vdp@` / `soc@` / `responsibledisclosure@` | Inbox class is the bug. |
| Remaining unsent of the 25 | Do not research 20 more until T1–T3 teach whether Contact/Info replies as vendors. |
| Column book-transfer hold/clear | Strong public object (`hold=true` then `POST /transfers/book/{id}/clear`, docs.column.com) — **no business To:** on the sheet. Do not send `security@column.com`. |
| Modern Treasury `needs_approval` → `completed` (posted) | Strong public object — To: was `privacy@`. Do not send. |
| D3/D5 DEPOSIT templates | Dead. |
| **T4 Increase** | Arnav = security alias, not a named business contact. **DEAD.** |

---

## After send

Mark SENT on this file only. **T1–T3, after the live page check passes.** Quit trigger = **one human treating it as a vendor**, not paid-clear. If all three are silence or “we filed this with security,” stop. Do not scale.
