# UCC Article 12 — controllable electronic records / control event receipt

**Status:** scoping only. Not outbound-ready.  
**Gap:** no productized stranger-checkable proof of the moment **control** of a CER passed — the fact that turns a buyer into a **qualifying purchaser** who can take free of competing property claims.

## Statute anchors (exact substance)

### § 12-105 — Control of controllable electronic record
A person has **control** of a CER if the electronic record, an attached/logically associated record, or a system in which it is recorded:

1. Gives the person:
   - (A) power to avail itself of **substantially all the benefit** from the electronic record; and  
   - (B) **exclusive** power (subject to (b)/(c)) to:
     - (i) prevent others from availing themselves of substantially all the benefit; and  
     - (ii) **transfer control** to another person (or cause another to obtain control of another CER as a result); and  
2. Enables the person **readily to identify itself** (name, id number, cryptographic key, office, account number, etc.) as having those powers.

**Exclusive** still holds if power is shared — **unless** the person can exercise only if the other also exercises **and** the other can act alone or is the transferor.  
Control **through another person** who acknowledges control on the person’s behalf is allowed (not the transferor).  
Acknowledgment does not by itself create duties.

*(Sources: NY UCC §12-105; RI 6A-12-105; KY 355.12-105; UCC12 Foundation text.)*

### § 12-104 — Rights / qualifying purchaser / take-free
- **Shelter:** purchaser acquires rights the transferor had or had power to transfer (limited interest → only that interest).  
- **Qualifying purchaser** = purchaser who obtains **control** of the CER **for value**, in **good faith**, and **without notice** of a claim of a property right in the CER.  
- **Take-free:** a qualifying purchaser acquires rights in the CER **free of** a claim of a property right in the CER.  
- Filing an Article 9 financing statement is **not** notice of a property-right claim in the CER.  
- Take-free on the CER does **not** automatically clear claims on other property merely evidenced by the CER (except as the statute provides for controllable accounts / payment intangibles).

*(Sources: NY UCC §12-104; WA RCW 62A.12-104; KY 355.12-104; TriBar 2024 opinions report.)*

## Fields a control-event receipt needs (to be legally useful, not just pretty)
Minimum stranger-checkable payload for a **control transfer event**:

| Field | Why (§) |
|-------|---------|
| `cer_id` / content hash | Which electronic record |
| `system_id` | System in which CER is recorded (§12-105(a)) |
| `from_controller` / `to_controller` | Identifiers that satisfy “readily identify itself” |
| `powers_asserted` | benefit / exclude / transfer bits |
| `exclusive_mode` | sole / shared / through-acknowledgee |
| `acknowledgee` (if any) | §12-105(e) path |
| `value_given` boolean + reference | QP element (for value) |
| `good_faith_attestation` | QP element (operator/legal, not Gate’s to invent) |
| `notice_scan` | what was checked; filing ≠ notice |
| `as_of` timestamp (UTC) | **when control passed** — the dispute pivot |
| `prior_control_receipt_jti` | chain |
| `decision` | CONTROL_PASSED / CONTROL_FAILED / UNKNOWN |

Gate can attest **mechanical** facts (keys, system logs, timestamps, hashes).  
Gate should **not** mint “good faith” or “no notice” as a free pass — those stay counsel/operator attestations referenced by the receipt.

## Case law (enacted states)
**No located reported decision applying Article 12’s qualifying-purchaser take-free rule to a CER as of this pass (Nov 1, 2026).**  
Adjacent pre-Art-12 digital-asset control discussion exists in bankruptcy dicta/holdings (*Celsius*, *BlockFi*) about who held control of crypto — useful analogy, **not** Art 12 QP precedent.  
NY §12-104 note: effective **June 3, 2026** in that compilation — timing matters for NY disputes.

Treat this lane as **statute-first / opinion-letter ready**, not case-hardened.

## Mouth vs new product
**Recommendation: new receipt type on Gate’s existing signed-receipt architecture** (`gate-control-event-v1`), separate evaluate mouth:

- `POST /v1/control/evaluate` — ingest system attestation + identifiers → CONTROL_PASSED / FAILED / UNKNOWN  
- Verify path reuses current Ed25519 stranger verify  
- Do **not** overload prefinality GO (different legal question: act clearance vs possession-equivalent)

Related in-repo: `exclusive.py` is about **exclusive door / museum vs production** — adjacent metaphor, **not** UCC control. Do not conflate.

## Adjacent infra gap (buyer story)
MERS-style e-registries for eNotes/eHELOCs track transfers but have publicly admitted their tracking may **not** satisfy Article 12’s control test. That is the wedge: **registry entry ≠ §12-105 control**.

## First buyer (when greenlit)
Secured lenders / custodians holding digital collateral who must defend a **qualifying-purchaser** or control-perfected priority claim in a dispute — need a time-stamped, stranger-checkable control event, not a PDF affidavit alone.

## Explicit non-goals this pass
- No outbound emails  
- No claim that a Gate receipt alone creates QP status  
- No building a CER ledger / wallet product under Nisaba’s mouth
