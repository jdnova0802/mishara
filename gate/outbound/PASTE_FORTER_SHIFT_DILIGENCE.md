# Forter + Shift Technology — diligence paste

**Status: READY FOR YOU TO SCHEDULE. Agent does not send.**

Checked 12 Oct 2026. Only these two. Alloy, Sardine, Unit21, Feedzai, Cohere Health, Gradient AI, Tractable, Anterior, and Rialtic stay parked.

| Field | Value |
| --- | --- |
| From | `hello@velaru.xyz` |
| Firm | Nisaba LLC |
| Ask | Reply **DEPOSIT** or pay. Deposit **$2,500**. Review band $5,000–$8,000. Find 72h after the deposit clears. |
| D1 | Tue 13 Oct 2026. Ready for you to schedule. Not sent from here. |
| D3 | Thu 15 Oct 2026, only if D1 actually went. |
| D5 | Mon 19 Oct 2026, only if D1 actually went. Not Friday 16 Oct (that day is the VAMP bump). |
| SLOT_DATE | **Mon 19 Oct 2026 23:59 ET** |

## Gating — Friday pack rule

| URL | Result |
| --- | --- |
| `https://gate.velaru.xyz/diligence` | **200** |
| `https://gate.velaru.xyz/diligence/one-pager.txt` | **200** |
| `https://gate.velaru.xyz/diligence/offer.json` | **200** |
| Third link in both emails | `https://gate.velaru.xyz/diligence#deposit` — the deposit form on the page that returns **200**. |
| `GET https://gate.velaru.xyz/diligence/checkout` on the live host | Still **405** until this branch is deployed. The emails do not use that URL. |
| `POST /diligence/checkout` | **303** to Stripe from the form. That is the pay path. |

A click in either email lands on the form. It does not land on the 405 page.

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
https://gate.velaru.xyz/diligence#deposit

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
https://gate.velaru.xyz/diligence#deposit

Reply DEPOSIT or pay.
```

## D3 (only after that name's D1 has gone)

Usable as written. The only link is `https://gate.velaru.xyz/diligence`, which returns 200. No checkout URL.

**Subject:** Re: [original subject]

Forter:

```
Still the same ask.

Where can the decline that cancels before authorize complete without may on your path?

Deposit $2,500 — starts 72h clock.
https://gate.velaru.xyz/diligence

Reply DEPOSIT or close the thread.
```

Shift Technology:

```
Still the same ask.

Where can the final deny inside the straight-through share complete without may on your path?

Deposit $2,500 — starts 72h clock.
https://gate.velaru.xyz/diligence

Reply DEPOSIT or close the thread.
```

## D5 (only after that name's D1 has gone)

**Subject:** Re: [original subject]

SLOT_DATE is Mon 19 Oct 2026 23:59 ET. Same body for both.

```
Last note from me on this seat.

Two diligence slots held through Mon 19 Oct 2026 23:59 ET.
After that I roll the list.

https://gate.velaru.xyz/diligence
Reply DEPOSIT if you want the find.
```
