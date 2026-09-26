# UCC § 4A-207 actual knowledge (beneficiary-side ACH / wire)

**Opinion SKU:** whether a beneficiary bank had **actual, subjective knowledge** of a name/account-number misdescription at the moment of deposit, after *Studco*.

**Not:** FedNow doctrine. Not a toss-up. Not an originator-side BEC / Ocean Frost case. Not Quincecare.

## Holding in one sentence

If the beneficiary’s bank credits the account number in the payment order and no individual employee actually knew of the mismatch at deposit, § 4A-207 does not shift the loss to that bank. Unread AML alerts are not knowledge.

## Primary authorities

1. **Studco Building Systems US, LLC v. 1st Advantage Federal Credit Union**, 133 F.4th 264 (4th Cir. 2025), *cert. denied*, No. 25-80 (U.S. Oct. 6, 2025).
   Knowledge under § 4A-207 is actual, subjective knowledge of an individual, not constructive knowledge pieced together across an institution, and not “should have known” from unreviewed DataSafe / AML alerts generated in volume. The bank may credit by account number. Official Comment 2’s efficiency point is the holding, not a gloss.

2. **UCC § 4A-207** (Va. Code Ann. § 8.4A-207 as applied in *Studco*; enacted in 49 states).
   Misdescription of beneficiary: if the bank does not know that the name and number identify different persons, it may rely on the number. “Knows” is UCC § 1-202: actual knowledge, not due diligence.

3. **Eleventh Circuit line** relied on by the Fourth Circuit in *Studco* (beneficiary bank has no duty to detect name/number conflict for automated credits). Use the Fourth Circuit’s statement of that line; do not treat district-court *Studco* (E.D. Va. 2023) as good law.

4. **Privity.** Judge Wynn’s concurrence: even if later transfers might have involved knowledge, § 4A-207’s recovery path is originator → originator’s bank → beneficiary’s bank, not a direct action by the defrauded originator against the beneficiary institution. Clearing House / Nacha amicus took the same point. A live-file opinion must say which mouth is suing.

## What this is not

| Confusion | Correction |
|---|---|
| “FedNow / RTP case” | *Studco* is ACH credits under 4A-207. Instant rails inherit later; they are not this holding |
| “Originator bank should have caught the spoofed invoice” | Different statute and different mouth: § 4A-202 / 4A-203 (commercially reasonable security procedure) and, in England, Ocean Frost / Philipp. See Opinion 01 |
| “AML alerts = knowledge” | *Studco* reversed that. Unread alerts are not an individual’s actual knowledge at deposit |
| District court *Studco* still citable for liability | Reversed. Certiorari denied 6 Oct 2025. The toss-up is over |

## Method (what the opinion actually tests)

1. **Which mouth.** Originator, originator’s bank, or beneficiary’s bank? Direct 4A-207 against the beneficiary bank is the *Studco* posture and may fail on knowledge *and* privity.
2. **What did an identified employee know, and when?** Names, timestamps, whether the credit had already posted. Knowledge after deposit does not unwind an already-accepted number match.
3. **What the monitoring system actually did.** Generated an unread report ≠ notified a person ≠ that person knew of *this* mismatch.
4. **Do not import originator-side facts** (grammar in the spoofed email, failure to call the vendor) into the beneficiary-bank knowledge inquiry. Those facts go to Opinion 01.

## Exhibit (working code, not a pitch)

The exhibit for this SKU is the same discipline as Opinions 01–02: the machine must not be allowed to wear knowledge. `rel/` refuses stuffed hashes and mouth booleans; it does not impute `telex_ok` from surrounding fields. That is the operational analogue of *Studco*’s refusal to impute unread alerts. It is not a payments product and is not offered as 4A compliance software.

## What an opinion will and will not say

**Will:** whether the record shows individual actual knowledge at deposit; whether unread alerts change that; whether the plaintiff is in the 4A recovery chain.

**Will not:** that the originator was not negligent; that 4A-202 security procedures were commercially reasonable (separate SKU); that FedNow has a decided 4A-207 analogue; that Nacha rules displace 4A.

## Price (this SKU)

Written opinion **$15,000–$75,000** by dispute size. Hourly **$650–$900**. Workshop/speaking day **$5,000–$15,000**.
