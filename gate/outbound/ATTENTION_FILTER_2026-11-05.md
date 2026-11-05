# Attention-economy filter pass — 5 November 2026

Standing filter, all four required: (1) named, checkable facts; (2) an exciting ledger joined to a boring one that is not already connected in public; (3) a person feels it today and an institution has a reason to move fast today; (4) say who is paid to handle the gap by hand, and flag it when that buyer makes money from the gap.

Surfaces checked tonight: Content Rewards creator terms on the live site (last updated 4 October 2026) against the Wayback capture of 30 August 2026 (page itself dated 19 August 2026); the Content Rewards help article on flagged submissions; the privacy policy’s Bot Score section; organization terms §§4 and 8; Google patents on influencer detection and reach; Apify actors and the 12 September 2026 DEV.to ledger post; FTC warning letters of 6 and 13 November 2023; Google’s prediction-markets ad policy.

Nothing in this pass clears all four. Three partials are real. They are scored below so a later pass does not re-try them as if they were empty.

## 1. Creator fee, rewritten between 19 August and 4 October 2026

Exciting ledger: the public campaign card (rate per 1,000 views, views, paid-out cents). Boring ledger: the creator-fee schedule, which is not a field in that card.

Wayback `https://web.archive.org/web/20260830234819/https://contentrewards.com/terms` (capture 30 August 2026, 7:48 PM ET; terms “Last updated: August 19, 2026”), §5.1, CPM fee by lifetime platform earnings:

- under $1,000: 25%
- $1,000 and above: 20%
- $2,500 and above: 12.5%
- $5,000 and above: 7%

§5.2 then: per-post and retainer, 7% when the campaign budget is under $5,000, and 0% (“Premium”) at $5,000 or more.

Live terms, last updated 4 October 2026, `https://contentrewards.com/terms`:

- §5.1: flat 10% on every CPM and Pool payout. “The rate does not vary with your lifetime platform earnings, the Campaign budget, or the size of the payout.”
- §5.2: per-post and retainer, 10% under a $5,000 budget, still 0% at $5,000 or more.

Who is worse off on a payout settling now: a CPM clipper whose lifetime credited earnings are already $5,000 or more (7% to 10%), and every clipper on a per-post or retainer campaign budgeted under $5,000 (7% to 10%). Clippers under $2,500 lifetime on CPM are paying less than in August (25% or 20%, now 10%). The $2,500–$5,000 CPM band moved from 12.5% to 10%.

The September Apify actors (tactful_anvil Whop Content Rewards Scraper; fayoussef whop-clipping-campaigns-scraper) and the 12 September 2026 DEV.to ledger of 658 campaigns publish `paidOut` against headline CPM. They do not publish this fee schedule or the August-to-October change. `paidOut / views` mixes the cap, rejections, holds, and the fee into one ratio. The fee is a separate contract number.

Filter: (1) pass. (2) pass as a public join; the card and the scrapers still omit it. (3) fail. The person on the worse tier feels it on the next settlement. No institution is moving on it today. Content Rewards already rewrote the clause on 4 October. Brands do not pay this fee. (4) nobody bills by the hour to compute it; it is automatic. The party who gains if a $5,000-plus CPM clipper does not notice is Content Rewards. That is the platform’s own margin, not a reviewer protecting a timesheet. Flag it. A page that prints “10% since 4 October, was 7% at this tier on 19 August” serves the person who loses the three points. The platform is the wrong customer.

Brand-side platform fee, live organization terms §4.1: 10% standard, 8% if the organization is Verified. Whop’s processing fee is passed through and called out as not CR revenue (§4.2). Those numbers were not the diff above.

## 2. Bot Score freezes the payout the creator cannot see

Exciting ledger: views and a payout that stops moving. Boring ledger: a 0–100 Bot Score and a campaign threshold.

Live creator terms §9 and organization terms §8 (both last updated 4 October 2026): the score is produced with a third-party fraud-detection provider; signals and weights are proprietary and may change without notice; it is shown to brand moderators; crossing the threshold may flag the submission and pause the payout; a person decides; the score itself does not approve or reject. Privacy policy §6 repeats that moderators see it. Help Center, “Flagged and botted submissions” (`https://help.contentrewards.com/en/articles/15319803-flagged-and-botted-submissions`): “you do not see the number itself.” The brand UI label is “Bot likelihood.” A flag is not shown on the clip. What the creator sees is the Earnings row stopping past its expected date. One appeal. Creator terms §10.3: “We aim to respond within 10 business days.” The help article says the terms “commit” to that response. The clause says “aim.”

Wayback of the 19 August terms is stricter on the trigger: the score crossing the threshold “is” automatically flagged. The 4 October text says “may be.”

Filter: (1) pass. (2) pass in public. The join exists inside the brand UI and is described in the help article. It is not in the public campaign JSON, and a stranger cannot attach a score to a post URL. (3) fail on the institution. A clipper with a frozen row feels it today, and the appeal clock is 10 business days. The brand already sees the number and can set the threshold per campaign. They are not a buyer. The fraud vendor is already under contract and unnamed. (4) red flag. The vendor’s product is the hidden weight. Studios that review flags (RUCKUS’s twice-a-day queue is the published example) bill for looking at the pause. Selling either of them a public score is a request to shrink the thing they charge for. The person who loses the frozen payout is the clipper, and the clipper cannot see the input the appeal is about.

## 3. Disclosure receipt, rescored after RUCKUS

Unchanged facts, new filter. Content Rewards FTC terms, last updated 12 February 2025, §§2.2 and 2.4: no duty to verify, and no monitoring of individual submissions. Creator terms §12.9 (4 October 2026) match. Brands have a “reasonable obligation to monitor” (FTC terms §7.3). YouTube Data API documents `paidProductPlacementDetails` as retrievable by the video owner. Public campaign JSON has submission id, post URL, views, rate, and max payout, and no disclosure field.

RUCKUS (`https://ruckusclipping.com/pricing`, `https://ruckusclipping.com/blog/disclosure-on-paid-clips`) sells the check inside a 20% studio fee on the campaign budget, invoice separate, verification report included on the first campaign. They write that Content Rewards does not monitor disclosure after approval, and they re-check at approval, day 7, day 14, day 30, and a day-90 sample.

Patents reviewed do not claim this join: US20150199727A1 (sponsoring brands in user-generated content), WO2020227562A1 (influence via tracked payments), US11810148B1 (keyword scoring of old posts), EP3649603B1 (true reach). None connect a payout cap or an FTC label to a view row.

GitHub code search did not surface a `paidOutCents` parser. The public parsers are Apify actors, in market since the 12 September 2026 DEV.to post by tactful_anvil: 658 campaigns, $510,929 paid out of $3.52M advertised (14.5%), median effective CPM 12% of headline among campaigns that had paid. That product connects views to paid-out. It does not connect either number to a disclosure label. The per-clip “views versus the published cap” reading is a narrower cut of the same card, not a new ledger.

FTC letters, not a 2026 clock: warning letter to Andrea Miller, 6 November 2023, and to Mary Ellen Phipps, 13 November 2023, both on ftc.gov, putting the recipient on notice of civil penalties up to $50,120 per violation. Kelley Drye’s writeup of that batch says staff asked for a response in 15 business days and said a Reels description and the platform “Paid partnership” tool alone were not enough.

Filter: (1) pass. (2) pass; the label is still not on the payout row. (3) fail. No brand, platform, or agency was found moving today to buy a signed observation. (4) red flag, the one this filter was added for. RUCKUS is paid a percentage of budget to do the check by hand. A sale to them is a sale to cut the review time inside a fee they already quote. CreatorCompli’s published brand price ($399 a month, 25 creators, 1,500 scans) is card-speed and does not join submission ids. The platform’s terms say the miss is not their liability, so they do not lose money when a label is absent.

## What did not become a lead

Google’s prediction-markets advertising policy prohibits those ads in Ohio effective 2 June 2026 (`https://support.google.com/adspolicy/answer/17109636`). Pages dated 5 November 2026 describe a YouTube gambling-ad expansion that still excludes Connecticut, Michigan, Nevada, New York, and Ohio for prediction markets. That policy is an ads policy. It does not mention organic paid-per-view clips. No new enforcement filing dated today turned up in this pass.

No FOIA release from 2024–2026 was found that prices disclosure monitoring. The 2023 letters above are the newest primary FTC documents this search returned.

## Do not build from this pass

The fee diff is a one-screen fact a clipper can check against the August capture and the live §5. It is not an institution buying today. The Bot Score is urgent for the person and already visible to the only institution in the workflow. The disclosure join remains the open product hole, and the buyer who would feel it first is paid to keep checking it by hand.
