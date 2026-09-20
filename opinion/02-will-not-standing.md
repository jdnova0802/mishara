# Will-not-release: what the signed receipt actually stands for

**Opinion SKU:** evidentiary standing of a machine-signed “will not release” / NONEXIST record in a live misdelivery, arrest, or eBL-control file.

**Not:** proof that a human never spoke. Not delivery. Not an arrest that starts a suit.

## Holding in one sentence

A signed will-not receipt proves that **this process, at this time, with this key, emitted NONEXIST (or HOLD)**. It does not prove a legal negative about the principal, and it is not “suit.”

## Primary authorities

1. **R v Shephard** [1993] AC 380 (HL).
   Computer records are admissible as real evidence of what the machine recorded. After repeal of PACE 1984 s.69, the objection is not “computers are hearsay,” it is the ordinary questions: what was the system, was it working, who controlled the key. The receipt is that class of evidence.

2. **United States v. Lizarraga-Tirado**, 789 F.3d 1107 (9th Cir. 2015).
   A machine-generated Google Earth pin, without a human assertion tacked on, is not hearsay. A JWT whose claims are `decision`, `reason`, `instrument_hash`, `authority_hash` is the same: the machine’s output, not a witness’s story. Human captions (“the principal never authorised release”) would be hearsay; the signed decision field is not.

3. **The Taikoo Brilliance** [2025] EWHC 1878 (Comm) (Knowles J, 22 July 2025).
   Arrest is not suit. A process that will not open the gate is not the commencement of proceedings, not a Hague-Visby Art. III r.6 “suit,” and not a US COGSA complaint. The receipt records a machine halt. It does not file a claim.

4. **The Houda** [1994] 2 Lloyd’s Rep 541 (CA) — *standard citation; used here as the known telex-release holding, not as a newly pulled original HTML.*
   A master is not obliged to deliver against a telex “release” in place of the bill. An eBL control message that the platform labels `released` is Houda’s telex in a new jacket unless the bill (or the statute recognising the electronic document) actually confers control. Opinion 01 (mouth vs hand) is the authenticity half of the same file; this page is the **standing** half.

## Method (what the opinion actually tests)

Separate four propositions that litigators routinely fuse:

| Proposition | Standing |
|---|---|
| The process emitted `NONEXIST` / `HOLD` at time *t* under key *k* | **Proved** by verifying the Ed25519 JWT against the published public key, checking `exp`, and matching hashes to the submitted file |
| The named principal never spoke | **Not proved.** Absence of a writing in *this* file is HOLD, not a negative about the world |
| Cargo did not leave the terminal | **Not proved.** EXIST means the file *may* open the gate; NONEXIST means the machine will not. Neither is delivery |
| Time bar / “suit” has started | **Not proved.** Taikoo: arrest ≠ suit. A halt receipt is not a complaint |

## Exhibit (working code, not a pitch)

`rel/receipt.py`, SPEC `rel-v1`. Ed25519 JWT, keys in `REL_RECEIPT_*` (separate from any other product). Claims include `decision`, `reason`, `instrument_hash`, `authority_hash`, `instrument_state`, `control_platform`. Default TTL 300 seconds. Verification is a signature check, not a narrative. Tests in `rel/test_rel.py` mint and verify the receipt; they do not assert a legal negative.

## What an opinion will and will not say

**Will:** whether the JWT verifies; whether the hashes bind to the file that was submitted; whether the decision field is machine output under Shephard / Lizarraga-Tirado; whether treating the halt as “suit” survives Taikoo.

**Will not:** that the principal is silent forever; that an arrest has started Hague-Visby time; that IG cover is prejudiced or preserved; that Houda is “overruled” by an eBL rulebook.

## Price (this SKU)

Written opinion **$15,000–$75,000** by dispute size. Hourly **$650–$900**. Workshop/speaking day **$5,000–$15,000**.
