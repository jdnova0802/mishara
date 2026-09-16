# Re-approach v3 — payment-ops review (not disclosure)

**Decision: (b), smaller than the 12.** Do not rebuild the remaining 25. Do not re-spray the 12 S-tier `security@` / `psirt@` / `vdp@` / `soc@` / `responsibledisclosure@` inboxes. Those addresses **are** the disclosure queue. New copy on the same To: still gets the playbook.

**Test set: 3 business inboxes + 1 named-human correction if Increase already replied.** Stop after those four unless a human answers as a vendor, not as a VDP.

**Page must ship first.** Old emails pointed at `/diligence` with DEPOSIT-now. If that URL still looks like a shakedown, the new email fails even when the body is clean.

Agent has no SMTP. Human sends from `hello@velaru.xyz` after the page is live.

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

Nisaba LLC. Vendor review, not a security report.

Your public payout flow is: create the payee, confirm they are payable, then create a payment batch (Tipalti REST: onboard payees and create payments). We will spend 72 hours writing a short memo on where that payable check is supposed to sit relative to batch create — from those docs plus anything you want to send.

No deposit. No invoice. No obligation. If the memo is useless, delete it.

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

Nisaba LLC. This is a vendor review of one named path, not a disclosure.

You already productize approval before a transfer is broadcast. We will spend 72 hours writing a short memo on how that approval is supposed to sit relative to broadcast, from your public product pages plus anything you send.

No deposit. No invoice. If it should go to a named transfer-ops owner, forward once.

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

Nisaba LLC. Vendor review, not a security filing.

You are a qualified custodian. The path we would read in 72 hours is withdrawal versus settlement: where permission is supposed to sit before assets leave, from your public bank/custody pages plus anything you send.

No deposit. No invoice. No obligation.

If Contact is the wrong desk, one forward to payments ops is enough. Reply REVIEW or ignore.

https://gate.velaru.xyz/diligence
```

---

## #T4 — Increase — **only if a named human already answered** (do not mail `security@increase.com` again)

**Public object:** Real-Time Payments: `POST /real_time_payments_transfers` → `pending_submission` → `submitted` → `complete` after The Clearing House ack. `require_approval` is optional. Docs: https://www.increase.com/documentation/sending-real-time-payments and https://increase.com/documentation/api/real-time-payments-transfers

**To:** the named person (e.g. the ops owner who replied). **Never** `security@increase.com` a second time.

**Subject:** Sorry — that was a vendor review, not a disclosure

```
[Name] —

The last note used the wrong inbox and the wrong shape (deposit token, “without may”). That was on us. It was meant as a payment-ops review, not a vulnerability report.

The object is public: RTP transfers go pending_submission → submitted → complete after The Clearing House ack, and require_approval is optional on create (Increase RTP docs).

Offer: 72-hour written memo on where approval is supposed to sit before TCH sees the payment. Free. No deposit. No obligation. If you want it, reply REVIEW. If not, this is the last note.

Nisaba LLC
https://gate.velaru.xyz/diligence
```

If Increase never produced a named human, **skip T4**. Do not invent `arnav@` or any other person.

---

## Explicitly parked

| Slot | Why parked |
|------|------------|
| S-tier #1–13 `security@` / `psirt@` / `vdp@` / `soc@` / `responsibledisclosure@` | Inbox class is the bug. |
| Remaining unsent of the 25 | Do not research 20 more until T1–T3 teach whether Contact/Info replies as vendors. |
| Column book-transfer hold/clear | Strong public object (`hold=true` then `POST /transfers/book/{id}/clear`, docs.column.com) — **no business To:** on the sheet. Do not send `security@column.com`. |
| Modern Treasury `needs_approval` → `completed` (posted) | Strong public object — To: was `privacy@`. Do not send. |
| D3/D5 DEPOSIT templates | Dead. |

---

## After send

Mark SENT on this file only. Quit trigger for this test = **one human treating it as a vendor**, not paid-clear. If all four are silence or “we filed this with security,” stop. Do not scale.
