# Doctrine memo: Studco v. 1st Advantage (4th Cir. 2025)

**Status:** Draft for source-or-cut · not legal advice  
**Entity:** Nisaba LLC  
**Author surface:** none (faceless doctrine)  
**Primary source:** *Studco Building Systems US, LLC v. 1st Advantage Federal Credit Union*, 133 F.4th 264 (4th Cir. 2025) (amended Apr. 2, 2025; decided Mar. 26, 2025), *cert. denied*, No. 25-80 (U.S. Oct. 6, 2025)  
**Opinion PDF (local copy):** `gate/doctrine/sources/studco-231148.P.pdf`  
**Opinion PDF (court host):** https://www.ca4.uscourts.gov/opinions/231148.P.pdf  
**Dockets:** 4th Cir. Nos. 23-1148 & 23-1766; E.D. Va. No. 2:20-cv-00417-RAJ-LRL  

---

## Scope and non-scope (read first)

| In scope (what this opinion decides) | Out of scope (do not read in) |
|---|---|
| ACH funds transfers under UCC Article 4A as adopted in Virginia | FedNow |
| Beneficiary-bank liability under Va. Code Ann. § 8.4A-207 when name and account number conflict | RTP / The Clearing House Real-Time Payments |
| Actual-knowledge standard for “know” / “knowledge” | Wire systems treated as if this holding automatically applies |
| Rejection of negligence / “commercially reasonable routines” as a substitute for actual knowledge under § 8.4A-207(b) | A holding that unread alerts always equal knowledge (majority: they did not, on this record) |
| Originator-side fact pattern: spoofed bank-change emails Studco did not verify | Any separate “Ocean Frost” holding (not this case; see note below) |

**Hard line:** This case is about **ACH**. The Fourth Circuit’s opinion opens by describing the ACH system and applies Virginia’s Article 4A rules to ACH payment orders. It does **not** hold that UCC § 4A-207 governs FedNow or RTP, and this memo does **not** extend the holding to those rails.

---

## Procedural result

- **No. 23-1148:** District court judgment for Studco **reversed**; remanded with instructions to enter judgment for 1st Advantage. (*Studco*, 133 F.4th at disposition; opinion closing paragraph.)
- **No. 23-1766:** Denial of Studco’s punitive-damages request **affirmed** (no compensatory predicate after reversal). (*Id.* Part V.)
- **Supreme Court:** Petition for certiorari **denied**, No. 25-80 (Oct. 6, 2025). (U.S. Supreme Court docket / Oct. 6, 2025 Order List.)

---

## Facts material to the doctrine (from Part I)

1. Studco regularly paid Olympic Steel by **ACH** from Studco’s JPMorgan Chase account to Olympic’s bank. (Op. Part I.)
2. In October 2018 Studco received emails **purportedly** from Olympic directing ACH payments to a “new” account at **1st Advantage Federal Credit Union**, with account and routing numbers. (*Id.*)
3. The emails were **fraudulent** (business-email compromise / impostor bank-change instruction). Indicators of inauthenticity appear in the opinion (wrong domain `Olysteel.net` vs `Olysteel.com`, mismatched From vs signature addresses, grammar errors, inconsistent phone/address, local Virginia credit union for an Ohio payee). Studco **did not verify** the bank-change instruction. (*Id.*)
4. Studco ordered **four ACH payments** totaling **$558,868.71** to account number xxx4713 labeled as “Olympic Steel Inc.” That number belonged to **Lesa Taylor**, not Olympic. Funds deposited automatically into xxx4713. (*Id.*)
5. 1st Advantage’s DataSafe system generated mismatch warnings (“Tape name does not contain file last name TAYLOR”). Warnings were stored automatically; **no person at 1st Advantage read them** before Studco’s president contacted the credit union on November 21, 2018. Hundreds to thousands of mismatch warnings occurred daily; review was not 1st Advantage’s custom. (*Id.*)
6. Scammers were not identified; Studco paid Olympic again and sued 1st Advantage. (*Id.*)

---

## Holding: beneficiary bank may rely on the account number absent actual knowledge

### Statutory text applied

Virginia Code § 8.4A-207(b)(1) (UCC § 4A-207(b)(1)): if a payment order identifies the beneficiary by **both name and account number** and those identify **different persons**, and the beneficiary’s bank **does not know** that the name and number refer to different persons, the bank **“may rely on the number as the proper identification of the beneficiary of the order”** and **“need not determine whether the name and number refer to the same person.”** (Op. Part II, quoting Va. Code Ann. § 8.4A-207(b)(1).)

### Knowledge = actual knowledge

- In this context, **“‘[k]nowledge’ means actual knowledge,”** not imputed or constructive knowledge. (Op. Part II, citing Va. Code Ann. § 8.1A-202(b).)
- The court rejected the district court’s use of organizational “due diligence” under § 8.1A-202(f) to redefine “actual knowledge” as knowledge the bank *should have had*. § 8.1A-202(f) addresses *when* notice/knowledge is effective for an organization; it **does not redefine** knowledge away from actual knowledge under § 8.1A-202(b). (Op. Part II.)

### Unread automated fraud / mismatch alerts ≠ actual knowledge (on this record)

- DataSafe reports warned of the name/number mismatch, but **no individual at 1st Advantage read them** before the relevant deposits. (Op. Parts I–II.)
- Because there was **no evidence of actual knowledge** at the time of deposit, 1st Advantage incurred **no § 8.4A-207 liability** for depositing to the numbered account. (Op. Part II, reverse of misdescription claim.)
- The beneficiary’s bank has **“no duty to determine whether there is a conflict”** between name and number, and therefore **no duty to adopt “reasonable routines”** to catch conflicts as a path to § 4A-207 liability. (Op. Part II, quoting § 8.4A-207 cmt. 2; citing *Peter E. Shapiro, P.A. v. Wells Fargo Bank, N.A.*, 795 F. App’x 741, 749 (11th Cir. 2019).)

### Policy stated by the court

Automated processing by account number (comparable to automated check payment) is the design of § 4A-207; requiring human review of every name discrepancy would undermine speed and efficiency. (Op. Part II, quoting Official Commentary and *First Sec. Bank of N.M., N.A. v. Pan Am. Bank*, 215 F.3d 1147, 1152 (10th Cir. 2000).)

### Risk allocation when the bank lacks actual knowledge

Where the beneficiary’s bank deposits to the designated number without knowledge of misdescription, Article 4A places the **risk of loss** on the person who dealt with the thief—here Studco—with remedies aimed at the recipient, the thieves, or potentially the originator’s bank (Chase), not a free skip to the beneficiary’s bank. (Op. Part II, citing Va. Code Ann. § 8.4A-207(c)(2) & cmt. 3; *Grain Traders, Inc. v. Citibank, N.A.*, 160 F.3d 97, 102 (2d Cir. 1998).)

### Bailment claim also reversed

A general bank deposit is not a bailment under Virginia law; ACH transfers alter fungible account balances rather than delivering a chattel. Bailment judgment reversed. (Op. Part III.)

### Concurrence (limited)

Judge Wynn concurred in the UCC interpretation (actual knowledge by an individual at deposit) but wrote separately that the record might support actual knowledge before the **final two** deposits (OFAC/wire investigation facts). He concurred in the judgment. (Wynn, J., concurring in part.) **This memo’s core doctrine statement follows the majority holding on the § 4A-207 standard;** the concurrence does not change the statutory rule the majority announces.

---

## Originator-side takeaway (from this opinion’s facts — not a FedNow rule)

The opinion’s own narrative places the **initiating failure upstream of 1st Advantage’s deposit decision**:

- Studco accepted **spoofed bank-change emails** and **ordered ACH payments** to the attacker-supplied account number without verifying the instruction. (Op. Part I.)
- The court states the scammers “duped Studco by posing as Olympic,” that “**it was Studco who dealt with the thieves**,” and that Studco “**could have avoided the loss if it had not used an account number that it was not sure was that of**” the intended beneficiary. (Op. Part II, quoting Official Commentary.)

**Doctrine split (keep these separate):**

| Issue | What Studco decides |
|---|---|
| Beneficiary-bank side | No § 4A-207 liability without **actual knowledge** of name/number mismatch at deposit; unread automated alerts insufficient on this record. |
| Originator / instruction side | Loss followed acceptance of a **fraudulent payment instruction** (impostor “new bank” emails). That is a **spoofed-instruction / authentication** fact pattern in Part I—not a holding that 1st Advantage should have blocked the ACH under a negligence standard. |

**“Ocean Frost-shaped” label:** Informal shorthand for the **spoofed payment-instruction** pattern described in Studco Part I. **Ocean Frost is not this case and is not analyzed or held here.** Do not cite Studco as Ocean Frost authority.

---

## One-sentence doctrine (safe to quote)

Under Virginia UCC § 8.4A-207(b)(1), as applied by the Fourth Circuit in *Studco*, a beneficiary bank processing an **ACH** payment order that lists conflicting beneficiary name and account number may rely on the **account number** and is not liable for the misdescription deposit unless it had **actual knowledge** of the mismatch at the time of deposit; **unread automated mismatch alerts do not supply that actual knowledge** on the *Studco* record, and the case **does not** decide FedNow or RTP.

---

## Source map (claim → opinion locus)

| Claim in this memo | Where in the opinion |
|---|---|
| Case is ACH Article 4A | Opening paragraphs; Part I (ACH payments); Part II (Article 4A / § 8.4A-207) |
| § 8.4A-207(b)(1) rely-on-number rule | Part II (statutory quotation) |
| Knowledge = actual knowledge | Part II (Va. Code § 8.1A-202(b)) |
| Due diligence / routines cannot redefine actual knowledge for § 4A-207 | Part II (rejection of district court’s § 8.1A-202(f) use) |
| No duty to check name/number conflict | Part II (§ 8.4A-207 cmt. 2) |
| Unread DataSafe warnings; no human read before contact | Parts I–II |
| Risk on party who dealt with impostor / supplied wrong number | Part II (§ 8.4A-207(c)(2) & cmt. 3) |
| Spoofed Olympic emails; Studco did not verify | Part I |
| Bailment reversed | Part III |
| Punitive affirmance | Part V |
| Disposition reverse / remand for 1st Advantage | Closing disposition |

---

## Disclaimer

This memorandum is **not legal advice**. It is a faceless, sourced doctrine note for Nisaba LLC internal clarity and public documentation. It does not create an attorney-client relationship. For advice about a specific transfer, rail, or dispute, consult qualified counsel and the primary materials linked above.
