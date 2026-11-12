# Instruction authenticity (mouth vs hand)

**Opinion SKU:** written expert opinion on whether a payment order, telex/email “release,” or eBL control message can be treated as the named principal’s instruction.

**Not:** a product, a platform, cover, or a finding that cargo moved.

## Holding in one sentence

The machine (or the telex mouth, or a stuffed hash) is not the principal. Apparent authority is proved by what the principal did, not by what a channel asserted.

## Primary authorities

1. **Armagas Ltd v Mundogas SA (The Ocean Frost)** [1986] AC 717, [1985] UKHL 11.
   Apparent authority is not created by the agent’s own representation of authority. The representor must be the principal (or someone the principal actually authorised to speak). A telex, email, or “authorized=true” flag that wears the agent mouth is the Ocean Frost fact pattern, not a shortcut around it.

2. **Ruben v Great Fingall Consolidated** [1906] AC 439 (HL).
   A forged instrument is a nullity. The company is not bound because a document looks like the company’s deed. A caller-supplied `instruction_hash` is the same species of self-authenticating paper.

3. **Philipp v Barclays Bank UK PLC** [2023] UKSC 25.
   Quincecare does not convert the bank into a mind-reader of the customer’s best interests where the customer’s own authorised instruction is what the bank executed. The originator-side BEC case is agency and instruction authenticity, not a duty to second-guess a genuine mandate. (Beneficiary-side ACH misdescription is a different statute: see Opinion 03.)

4. **Mehta v J Pereira Fernandes SA** [2006] EWHC 813 (Ch).
   An email header is not a signature of the named person. The “from” field is not the hand. Instruction authenticity requires a named human principal plus a written body attributable to that principal, not a mailbox.

## Method (what the opinion actually tests)

For any disputed instruction, ask three questions. Do not collapse them.

| Question | If missing | Legal analogue |
|---|---|---|
| Is there a **named human principal** (not a role, not a mailbox)? | HOLD — no one whose mouth can bind | Ocean Frost / Mehta |
| Is there a **written body** (not a boolean, not a telex_ok flag)? | HOLD — no writing | Ruben / Mehta |
| Did the caller **stuff a hash** (`instruction_hash` / `hash` / `written_hash`) instead of submitting principal + writing? | NONEXIST — mouth substitution | Ruben (self-authenticating instrument) |

The digest, if any, is computed from `{spec, human_principal_id, written}`. It is never taken from the caller. A stuffed hash is treated as the machine wearing the telex mouth.

## Exhibit (working code, not a pitch)

`rel/` in this repository, SPEC `rel-v1`. `authority_hash()` hashes named principal + written body only. Stuffed hash keys and mouth keys (`telex_ok`, `authorized`, `may_release`, …) return `decision=NONEXIST`, `reason=mouth_substitution`. Missing principal or writing returns `HOLD`. Tests: `rel/test_rel.py` (adversary fixtures: independent telex without principal; stuffed hash; mouth keys).

## What an opinion will and will not say

**Will:** whether the file as presented contains a named principal and a writing; whether a purported hash was caller-supplied; whether a channel message can be treated as the principal’s representation under Ocean Frost.

**Will not:** that cargo was or was not delivered; that P&I cover responds; that an eBL platform is IG-approved; that the originator’s bank had a Quincecare duty to refuse a genuine mandate.

## Price (this SKU)

Written opinion **$15,000–$75,000** by dispute size. Hourly **$650–$900**. Workshop/speaking day **$5,000–$15,000**.
