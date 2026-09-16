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

## After send — stop vs keep going (decided before the 9am paste)

The question is **did this land as a business email**, not **did they pay**. D3/D5 deposit nudges stay dead. No same-day follow-up. No “still the same ask.”

**Clock (business days, US Eastern):**

| When | What you are allowed to conclude |
|------|----------------------------------|
| Same day / next morning | Nothing. Auto-acks and “we’ll get back to you” are not a yes or a no. |
| Through **3 business days** | Slow is the default. A REVIEW-shaped reply, a forward, or “looping in ops” is **pending**, not a win. Sit. Do not send names 4+. |
| End of day **3** with **no human** on all three | Read as **silence**. Stop. Do not scale the remaining 22. |
| End of day **5** on a thread that forwarded internally with still no named ops owner | Read that name as **no decision**. Do not chase. Do not expand the list on the hope they’ll come back. |

**Stop that name immediately (do not wait 3 days):**

- “Filed with security,” VDP, PSIRT, Bugcrowd, responsible disclosure
- Reply from `security@` / `psirt@` / `vdp@` / `soc@` even if a real first name is on it (Arnav rule: functional inbox ≠ business contact)
- “Please do not contact us” / bounce to the disclosure queue

If **any** of the three dies that way, do **not** treat the other two as permission to spray the rest of the 25. Finish sitting the ones that are still pending. Then stop.

**Keep going (add more names, same form: public object + business To: + REVIEW, never security@)** only if:

- A **named payments / payouts / transfer / bank-ops person** answers as a vendor: REVIEW, “send the memo,” or an intro to that desk
- Not a ticket bot, not a security alias, not “I forwarded it” with no owner

One such reply is enough to justify **the next small batch** (same size: three, not the leftover 22). Zero such replies after the 3-day silence read = the categorization fix failed or did not get a chance. Either way, **do not scale**.

**Middle cases, decided now:**

| What happens | Call |
|--------------|------|
| REVIEW-shaped but slow (“next week,” “after quarter close”) | Pending. Wait. Do not send more names while you wait. |
| “Forwarded to the right team” / internal CC, no yes/no | Pending vendor landing. Sit **5 business days**. If no named owner appears, that name is done. |
| Contact/info auto-ack only | Not a human. Still silence until day 3. |
| Asks a real question about the memo or the public path | Vendor. Write the 72h memo. Default next ask is **paid diligence**, not Bind Room (see conversion below). |
| Asks to talk to security | Stop that name. Do not “correct” them into ops. |

**Conversion after a liked free memo (T1–T3 and any later diligence-framed send)**

The free 72h review is the **mouth / finality diligence** lane: paid review **$5,000–$8,000**, then retainer **$10,000–$40,000/mo**. Same Prefinality/Clear doctrine as Gate, **different SKU**. It does **not** map to Bind Room (**$1,750**).

When they like the memo and want to continue, the ask is: convert the free review into the **paid diligence review**, or the **retainer** if they want it ongoing. Deposit/charge only after they want to keep that work. Do not pitch Bind Room as the default next step.

Bind Room stays a separate, lower-friction motion (GC / compliance / carrier / broker). Mention it only if that desk is actually who answered and the memo is a bind/officer-pack fit. If they answered on payouts, custody, RTP, book transfer, or mass pay, stay on diligence.

Mark SENT on this file when the three actually go out. Quit trigger for **this test** is the table above, not paid-clear.
