# Forter + Shift Technology — diligence paste

**Status: DRAFT. Do not schedule. Do not send.**

Checked 12 Oct 2026. Only these two. Alloy, Sardine, Unit21, Feedzai, Cohere Health, Gradient AI, Tractable, Anterior, and Rialtic stay parked.

| Field | Value |
| --- | --- |
| From | `hello@velaru.xyz` |
| Firm | Nisaba LLC |
| Ask | Reply **DEPOSIT** or pay. Deposit **$2,500**. Review band $5,000–$8,000. Find 72h after the deposit clears. |
| D1 | Not armed. Earliest after a go-ahead: Tue 13 Oct 2026. |
| D3 | Thu 15 Oct 2026, only if D1 actually went. |
| D5 | Mon 19 Oct 2026, only if D1 actually went. Not Friday 16 Oct (that day is the VAMP bump). |
| SLOT_DATE | Unset. Do not put a calendar date in a body until this table is filled. |

## Gating — Friday pack rule

| URL | Result |
| --- | --- |
| `https://gate.velaru.xyz/diligence` | **200** |
| `https://gate.velaru.xyz/diligence/one-pager.txt` | **200** |
| `https://gate.velaru.xyz/diligence/offer.json` | **200** |
| `GET https://gate.velaru.xyz/diligence/checkout` | **405** Method Not Allowed. Checkout is POST-only. A click on that link does not open Stripe. |
| `POST /diligence/checkout` with a valid email | **303** to a live Stripe Checkout session. The form on `/diligence` is the pay path that works. |

The Friday rule says checkout must return 200 before send. It does not. This paste stays unscheduled until that GET is a 200, or until the third link is a URL that opens the pay page on a click.

One unpaid probe was posted to confirm the 303. It was not paid.

## D1 — Forter — `sales@forter.com`

**Subject:** DEPOSIT — Forter decline before authorize

93 words.

```
Sales — Forter

On 21 Oct 2024 you published that Forter's decision logics drive the approval or the decline. On 8 Dec 2025 you published that a declined transaction carries the fraud scenarios Forter identified. Your checkout integration says Decline means do not authorize, and cancel the transaction. That cancel is the mouth.

Can ≠ may on that decline.

Mouth diligence from Nisaba LLC. One path: the decline that cancels before authorize. Deposit $2,500 now. Written find 72 hours after the deposit clears. Review band $5,000–$8,000.

https://gate.velaru.xyz/diligence
https://gate.velaru.xyz/diligence/one-pager.txt
https://gate.velaru.xyz/diligence/checkout

Reply DEPOSIT or pay.
```

## D1 — Shift Technology — `partners@shift-technology.com`

**Subject:** DEPOSIT — Shift final deny inside straight-through

95 words.

`marketing@shift-technology.com` is Press & Media. Do not use it.

```
Partnerships — Shift Technology

Your 13 Sep 2024 travel case study says the model reads the policy, the medical report, and the invoices, then writes a final decision and passes it to the insurer. Straight-through automation reached 57%. Inside that share, 46% are pay decisions and 11% are denies. The deny is the mouth.

Can ≠ may on that deny.

Mouth diligence from Nisaba LLC. One path: the final deny inside that straight-through share. Deposit $2,500 now. Written find 72 hours after the deposit clears. Review band $5,000–$8,000.

https://gate.velaru.xyz/diligence
https://gate.velaru.xyz/diligence/one-pager.txt
https://gate.velaru.xyz/diligence/checkout

Reply DEPOSIT or pay.
```

## D3 (only after that name's D1 has gone)

**Subject:** Re: [original subject]

```
Still the same ask.

Where can [MOUTH] complete without may on your path?

Deposit $2,500 — starts 72h clock.
https://gate.velaru.xyz/diligence

Reply DEPOSIT or close the thread.
```

Forter mouth token: the decline that cancels before authorize.
Shift mouth token: the final deny inside the straight-through share.

## D5 (only after that name's D1 has gone)

**Subject:** Re: [original subject]

```
Last note from me on this seat.

Two diligence slots held through `SLOT_DATE`.
After that I roll the list.

https://gate.velaru.xyz/diligence
Reply DEPOSIT if you want the find.
```

`SLOT_DATE` is empty. Do not send D5 with the token still in the body.
