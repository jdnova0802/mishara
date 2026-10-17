# DRAFT — paste into https://www.ycombinator.com/apply

Winter 2027. On-time deadline **2 Nov 2026, 8pm PT**. Not submitted. Demond reviews and submits.

Blanks marked FILL are things only he knows. Do not invent them.

Product link: https://gate.velaru.xyz
Proof link (no login): https://gate.velaru.xyz/v1/issuing/authorization/iauth_1URXhX3b5zsnE0zsR1QikRhn

---

**Company name**
Gate

**Company URL**
https://gate.velaru.xyz

**Describe what your company does in 50 characters or less.**
Fail-closed check before a card charge.

**What is your company going to make?**
Gate answers Stripe Issuing’s real-time authorization webhook. When a card is used, Stripe calls https://gate.velaru.xyz/v1/issuing/authorization and waits about two seconds. Gate returns {"approved": true} only if the charge is inside a spend cap the card already carries. No cap, a bad payload, or an error is a decline.

The receipt of that decision is public. A stranger opens it with the authorization id. No login.

This is for a carrier or program desk that already lets an agent or MGA spend or bind, and needs the halt before the charge rather than a write-up after it.

**Please provide a link to the product, if any.**
https://gate.velaru.xyz

The decision from the one live charge, no login:
https://gate.velaru.xyz/v1/issuing/authorization/iauth_1URXhX3b5zsnE0zsR1QikRhn

**Where do you live now, and where would the company be based after YC?**
FILL: city now. Toledo, Ohio is the operating address on the Nisaba Stripe account. After YC: San Francisco for the batch.

**How far along are you?**
Live on Stripe Issuing. Nisaba’s own card program.

On 17 Oct 2026 a real $1.07 Kindle charge, authorization iauth_1URXhX3b5zsnE0zsR1QikRhn, came back webhook_approved. The card and the $5 float were Nisaba’s. Zero paying customers. Zero stranger dollars collected.

Three attempts earlier that day failed in Stripe’s own log: the webhook had no API version, the reply had no Stripe-Version header, and a $0 placeholder amount was declined instead of approved. Those fixes are on main.

**How long have you been working on this? How much of that has been full-time?**
FILL: months, and whether it has been full-time.

**What tech stack are you using, or planning to use, to build this product? Include AI models and AI coding tools you use.**
Python, Flask, Stripe Issuing, Render, SQLite. I use Cursor to write the code.

**Are people using your product?**
No. One live authorization, on our own card. No outside user.

**Do you have revenue?**
No.

**If you are applying with the same idea as a previous batch, did anything change?**
FILL: no, or what changed. If this is the first application, say no.

**Why did you pick this idea to work on? Do you have domain expertise in this area? How do you know people need what you're making?**
Agents are getting cards. The moment the money can move is the two-second Issuing webhook, not a review after the charge posts.

I know people need a halt there because the public failures are already about treating a document as live before the issuer confirms it: Vesttoo and the CCB letters of credit, and deny-to-defend fights at program desks. I have not yet had a carrier pay for this. The offer in front of them is a free 72-hour look at one public page, then a $1,750 Bind Room if they want the pack.

I built the live webhook myself, including the three failures above. That is the domain expertise I actually have.

**Who are your competitors? What do you understand about your business that they don't?**
HumanLayer (YC F24) is the closest funded company. They do human approval around coding agents. They do not sit on issuing_authorization.request.

The other public projects in this neighborhood (Penholder, AgenticRail, Proofpane, Provenrail, HELM, CoreBase, MandateGuard, Certiv, AgentLock, Kakunin) ship a demo, a library, or an assurance page. None of them has a live Stripe Issuing authorization.

What they treat as optional, I treat as the product: if Gate is unsure, the charge is declined. A missing spend cap is a decline. An expired receipt is not rewritten into a fake approval.

**How do or will you make money? How much could you make?**
A desk pays $1,750 to start the Bind Room. The full assessment is $3,500. A weld inside their system is a separate sale after that, not priced as a collected number because nobody has paid one.

I will not project a market size. Zero has been collected. The first dollar is one of those desks paying the $1,750.

**Who writes code, or does other technical work on your product? Was any of it done by a non-founder?**
I write it. I use Cursor. No other founder. No agency.

**Are you looking for a cofounder?**
FILL: no, unless you are.

**How did the founders meet? / equity**
One founder. Nisaba LLC, single-member. FILL: exact ownership percent if it is not 100%.

**Have you taken any investment yet? Are you currently fundraising?**
FILL: no, unless you have.

**Please tell us in one or two sentences about something impressive that each founder has built or achieved.**
On 17 Oct 2026 I got a live Stripe Issuing webhook to approve a real $1.07 charge after Stripe had rejected the three attempts before it the same day: blank API version, missing Stripe-Version header, and a $0 amount that had to be read off pending_request.

**Please tell us about the time you most successfully hacked some (non-computer) system to your advantage.**
FILL. One true story. Do not borrow one.

**If you had any other ideas you considered applying with, please list them.**
FILL or leave blank.

**Founder video**
One minute. You, on camera. Say: Gate declines a card charge unless it is inside a cap. On 17 Oct Stripe recorded webhook_approved on a real $1.07 Kindle charge on our own card. No customers yet. I built it.
