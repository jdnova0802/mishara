# DRAFT — YC Winter 2027 (review only, not submitted)

On-time deadline published by YC: **2 Nov 2026, 8pm PT**. Decisions for on-time apps by **11 Dec 2026**. Batch January–March 2027, San Francisco. Source: https://www.ycombinator.com/apply/ (checked 17 Oct 2026).

**Do not submit this.** Demond decides. Nothing below was entered on the YC form.

Honest traction line, use it as written: one real authorization through a live Stripe Issuing webhook, zero paying customers yet.

---

## Company

**Name:** Gate (Nisaba LLC)

**One-liner:** Fail-closed clearance on a live card authorization, with a receipt a stranger can check.

**Company URL:** https://gate.velaru.xyz

**Where:** United States. Solo founder.

## What does Gate do?

Gate is a hop that runs before a card charge becomes irreversible. Stripe Issuing calls `POST https://gate.velaru.xyz/v1/issuing/authorization` on `issuing_authorization.request` and waits about two seconds. Gate returns `{"approved": true}` only on a GO. Anything else, including a bad payload, a missing spend cap, or an exception, is a decline.

The buyer this is written for is a carrier or program desk that already lets an agent or MGA bind or spend, and needs a halt plus a receipt their examiner can open without a login.

## Why now?

Agents are being given cards. The moment money can move is the Issuing authorization webhook, not a chat approval after the charge. The funded company in the same neighborhood, HumanLayer (YC F24), ships human-in-the-loop on coding agents. It does not sit on `issuing_authorization.request`. Neither do the other public agent-clearance projects we compared (Penholder, AgenticRail, Proofpane, Provenrail, HELM, CoreBase, MandateGuard, Certiv, AgentLock, Kakunin).

## How far along?

Live in production on Stripe Issuing, Nisaba’s own program (Cross River, Mastercard, debit, own financial account).

On 17 Oct 2026 a real $1.07 Kindle authorization, `iauth_1URXhX3b5zsnE0zsR1QikRhn`, came back `webhook_approved`. The card was Nisaba’s. The $5 float was Nisaba’s. Status at approval was pending (authorized, not captured). The card ending 5440 was later canceled. No second live authorization.

Three earlier attempts the same day failed in Stripe’s log, and each failure is why the path is fail-closed rather than a demo: blank API version on the endpoint, missing `Stripe-Version` on the reply, and a $0 placeholder amount that Gate declined instead of approving. Those fixes are on `main`.

Public decision, no card number: https://gate.velaru.xyz/v1/issuing/authorization/iauth_1URXhX3b5zsnE0zsR1QikRhn

The signed receipt’s 120-second TTL has expired. The stored decision is still GO. Expiry is not a decline. The JWT was not re-minted.

## Traction / revenue

- Paying customers: **0**
- Stranger dollars collected: **0**
- Revenue: **0**
- Published prices, not collected: Bind Room **$1,750**. Full assessment **$3,500**.
- One live card authorization: **$1.07**, own funds.

Do not write “customers,” “volume,” or “in production with insurers.”

## How will you make money?

A desk pays for the assessment and the Bind Room before any production weld. The published start is $1,750. The full assessment is $3,500. A weld inside their system is a separate operator sale after the pack. The Issuing mouth is the proof that the hop can sit on a real authorization, not a second SKU.

## Who is the user, and how do you get them?

Named insurance and fronting desks that already had a public collateral or defend failure (Vesttoo / CCB LOC pattern, deny-to-defend, primary defend handoff). The offer already written is a free 72-hour memo on their public pages, reply token REVIEW. Ten drafts exist. Four desks were emailed on 23 Sep 2026 (Buckle, SteadPoint, 1970, Everspan). The 29 Sep batch of ten is not logged as sent. No replies are logged.

## Competitors

HumanLayer is the closest funded company: YC F24, human approval around coding agents. Gate’s difference is the card rail and the fail-closed default. The others are demos, libraries, or enterprise assurance pages. None has a live Stripe Issuing authorization webhook. Do not claim Gate is ahead of them on funding, team, or customers.

## Team

Demond Davis. Solo founder. Writes the product. No second engineer. No cofounder. Bus factor is one. Say that on the form. Do not invent advisors.

## Why you?

He is the person who got Nisaba’s own Issuing program live and stayed on the webhook until Stripe recorded `webhook_approved` on a real $1.07 charge, after three recorded failures the same day. That is the specific fact. Do not add a résumé that is not already in the application packet he wants to use.

## Something you’ve built

The live mouth: signature-checked webhook, `Stripe-Version` on the reply, spend judged on `pending_request.amount` because Stripe sends `0` in the top-level amount during the request, fail-closed without a spend cap, and a public GET of the stored decision by authorization id.

## What you want from YC

A batch where the next proof is a stranger desk paying the $1,750, not another mouth. Company wall already set: one cleared stranger dollar into the Nisaba account by Friday 14 Nov 2026, or Nisaba stops. YC’s on-time decision date is 11 Dec 2026, which is after that wall. Say the wall. Do not pretend the batch timeline replaces it.

## Leave blank or “no” unless Demond fills them

- Equity breakdown beyond 100% founder
- Prior employers, schools, and ships not already chosen by him
- Users, growth rate, MRR
- Cofounder search
- Incorporation state details beyond Nisaba LLC
- Anything about the canceled card’s number, CVC, or webhook secret
