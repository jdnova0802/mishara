# Two public attention datasets that do not meet (5 Nov 2026)

A join, not a feature. Both shapes are real. Neither one is the Polymarket lawsuit glued onto a different campaign.

Pulled live from Content Rewards around 6:10 PM America/New_York on 5 Nov 2026. The page is public. No login.

---

## The two lists

**List A. The clipping ledger.** Content Rewards publishes, in the page JSON, per campaign: headline rate, per-clip cap, budget spent, cash actually paid out, approved submissions, creator count, total views, and a leaderboard of submission rows. Each leaderboard row has `submissionId`, `postUrl`, `platform`, `rank`, `totalViews`, and the clipper’s username.

One campaign, fetched tonight:

[FR Yomi Denzel Campagne Principale](https://contentrewards.com/discover/14f743b2-c5ca-4f3e-8c0d-3010c485005d), id `14f743b2-c5ca-4f3e-8c0d-3010c485005d`, organization Yomi Denzel Clipping, listed 1 Dec 2025.

| Field in the JSON | Value tonight |
|---|---|
| `rateCents` on TikTok, Instagram, and YouTube | 70, i.e. $0.70 per 1,000 views. The board shows $0.70/1K. |
| `maxPayoutCents` / `minPayoutCents` | 10000 / 2000, i.e. a $100 cap and a $20 floor per submission |
| `budgetSpentCents` | 33,190,394 ($331,903.94) |
| `paidOutCents` | 4,705,871 ($47,058.71) |
| `totalViews` | 674,743,836 |
| `approvedSubmissionCount` | 58,530 |
| `creatorCount` | 349 |
| Leaderboard rows embedded in the HTML | 10 ranks, duplicated in the payload. The top ones are below. |

At the card rate with no cap, 674,743,836 views would be about $472,321. Cash paid out is $47,058.71, which is 10.0% of that. A prior public pass already saw this shape in aggregate: on 12 Sep 2026 a scraper of 658 active campaigns reported $3.52 million of advertised budget, $510,929 paid out (14.5%), and a median effective rate of 12% of the headline CPM among campaigns that had paid anything. Same Yomi campaign, that day: $47,059 paid on 1.357 billion views. [DEV, 11 Sep 2026](https://dev.to/tactful_anvil/i-pulled-the-payout-ledger-of-658-clipping-campaigns-the-median-one-pays-12-of-its-advertised-cpm-5g0k). That pass did not put the per-clip cap next to a per-clip view count, and it did not look at disclosure.

**List B. The disclosure libraries.** These are a different public dataset, keyed by post and brand, not by campaign.

- TikTok Commercial Content Library, and `POST /v2/research/adlib/commercial_content/query/` (scope `research.adlib.basic`). A row has `label` (the example value is “Paid partnership”), `brand_names`, `creator.username`, and `videos[].url`. TikTok’s own help center says the “other commercial content” library only includes posts the creator disclosed through the content disclosure setting. The library the help center describes covers the EEA, Switzerland, and the UK. The API’s creator-country filter is EEA only. Docs last updated 1 Sep 2026. [Query docs](https://developers.tiktok.com/doc/commercial-content-api-query-commercial-content/), [help center](https://support.tiktok.com/en/account-and-privacy/personalized-ads-and-data/commercial-content-library).
- Meta `branded_content_search` (Graph API v26). Returns branded-content posts, stories, videos, and reels created on or after 17 Aug 2023 that are still up. Fields include `creator`, `partners`, `type`, `url`, `creation_date`. Search is by `ig_username` or `page_url`. [Docs](https://developers.facebook.com/docs/graph-api/reference/branded_content_search/).
- YouTube Data API `paidProductPlacementDetails.hasPaidProductPlacement` is a boolean, and the API reference says this part can only be retrieved by the video owner. [Reference](https://googleapis.dev/dotnet/Google.Apis.YouTube.v3/latest/api/Google.Apis.YouTube.v3.Data.VideoPaidProductPlacementDetails.html).

The campaign JSON has the post URL and the view count. It does not have a disclosure field. The disclosure libraries have the label and the brand. They do not have a Content Rewards `submissionId`. That is the unmade join.

## Shape 1. The small fact

The cap and the view count are already in the same payload, and the board does not put them in one sentence.

The rank-1 row tonight is a YouTube Short, `https://youtube.com/shorts/D9GO9S0FvQ4`, 2,593,042 views, clipper username `bakaryismael`. At $0.70 per 1,000 that Short is worth $1,815 on the card. `maxPayoutCents` on the same campaign is $100. The cap is reached at about 142,857 views. Every row in the published top 10 is past 1.5 million views, so every one of them is an order of magnitude past the only number the campaign will pay.

The rank-3 row is a TikTok, `https://www.tiktok.com/@notyomi.edit/video/7690867948025597217`, 2,200,000 views, submission id `51a42bd0-1dfe-464d-a778-4106a1e494f9`. Same arithmetic: about $1,540 on the card, $100 on the cap.

This is not a hidden fee and it is not the Polymarket complaint. Yomi Denzel Clipping is paying a French creator’s own clips out to other people, and the cap is sitting in the public payout object. The consequence is for the person deciding where to put a week of posting: the headline CPM is the rate only until 142,857 views, and the clips that actually rank are far past that. The September aggregate (median 12% of headline) is what you get when that cap, plus rejections and payout lag, is left off the card. The September author already said the gap is not proof that views were stolen. Tonight’s per-clip numbers agree with the cap as a sufficient explanation for the top of the board.

## Shape 2. The cheap object with reach

A single page, rebuilt from the public HTML, one campaign at a time:

- the card rate and the cap
- the ten `postUrl`s with their view counts
- the card-rate dollars next to the capped dollars
- a disclosure column filled from TikTok’s library or Meta’s branded-content search where the URL is in those libraries, and “owner-only” where the URL is a YouTube video

No login on the Content Rewards side. The TikTok research call needs a developer token; the Meta call needs a Graph token; the YouTube boolean cannot be read for someone else’s video. The page is still postable without those tokens, because the cap column is complete from list A alone, and the disclosure column is honest about which rows it cannot see.

That page is the reach object. The numbers are checkable by opening the campaign and opening the video. People share a table when the top line is “2.6 million views, $100.”

## Where a receipt fits, without forcing it

The row nobody publishes is `(submissionId, postUrl, label, observed_at)`. List A has the first two. List B has the label only if the creator turned the disclosure on, and only on the platforms and countries that library covers. YouTube’s bit is not available to a stranger at all. Content Rewards stores a downloaded copy of the video (`videoUrl` on their CDN is in the same leaderboard object) and still does not publish whether the post carried a paid-partnership label.

A signed observation of that URL at a time, recording whether the label was on the public page, is the join record. It is useful here because the FTC’s endorsement guides treat a material connection, including pay, as something the viewer has to be able to see, and because the one clipping campaign that has actually been sued was accused of instructing the opposite. That case is NACA v. Polymarket and others, D.C. Superior Court 2026-CAB-004388. Kelley Drye’s summary says the brief told clippers not to make the videos feel like ads. Those are allegations, and they are a different campaign from Yomi. The join is how a later case, or a brand, would not have to screenshot a marketplace graphic to know which paid URL carried a label.

I did not open the ten videos tonight, so this note does not say whether any of them is missing a label.

## What was not the join

- Scraping the board and sorting by effective CPM. Already done, in public, on 12 Sep 2026.
- Treating Yomi’s cap as the Polymarket fact pattern. Different parties, different conduct alleged.
- YouTube’s paid-promotion boolean as a public field. The reference says the owner.
