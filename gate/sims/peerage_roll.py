"""Z9 Peerage Roll Entry — lab mouth: claimed title ≠ Crown recognition.

Lab only. their_production is always False.
Not genealogy AI. Not a title marketplace.
Gates Roll entry on LIVE evidence package + Lord Chancellor-shaped allow.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from gate.sims.lab_invariant import stamp_lab_flag
from gate.sims.logos import canonical


SPEC = "nisaba-peerage-roll-lab-v1"
THEIR_PRODUCTION = False


@dataclass
class Claim:
    claim_id: str
    dignity: str
    claimant: str
    long_form_certs: bool
    senior_lines_extinct: bool
    petition_filed: bool
    status: str  # pending | on_roll | refused


@dataclass
class Store:
    claims: dict[str, Claim] = field(default_factory=dict)
    roll: dict[str, dict[str, Any]] = field(default_factory=dict)
    receipts: dict[str, dict[str, Any]] = field(default_factory=dict)


STORE = Store()


def reset() -> None:
    STORE.claims.clear()
    STORE.roll.clear()
    STORE.receipts.clear()


def _receipt(
    decision: str,
    reason_code: str,
    *,
    claim_id: str | None = None,
    dignity: str | None = None,
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rid = str(uuid.uuid4())
    payload = {
        "spec": SPEC,
        "receipt_id": rid,
        "receipt_class": "clearance",
        "decision": decision,
        "reason_code": reason_code,
        "claim_id": claim_id,
        "dignity": dignity,
        "result": result,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="peerage_roll"),
        "ts": time.time(),
    }
    payload["receipt_hash"] = hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()
    STORE.receipts[rid] = payload
    return {**payload, "receipt_url": f"/v1/peerage-roll/receipts/{rid}"}


def submit_claim(
    *,
    dignity: str,
    claimant: str,
    long_form_certs: bool = False,
    senior_lines_extinct: bool = False,
    petition_filed: bool = False,
) -> dict[str, Any]:
    if not dignity or not claimant:
        return {
            "ok": False,
            "reason_code": "malformed_claim",
            "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="peerage_roll"),
        }
    cid = str(uuid.uuid4())
    STORE.claims[cid] = Claim(
        claim_id=cid,
        dignity=dignity,
        claimant=claimant,
        long_form_certs=long_form_certs,
        senior_lines_extinct=senior_lines_extinct,
        petition_filed=petition_filed,
        status="pending",
    )
    return {
        "claim_id": cid,
        "dignity": dignity,
        "claimant": claimant,
        "status": "pending",
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="peerage_roll"),
    }


def enter_roll(
    claim_id: str | None,
    *,
    self_style_only: bool = False,
    short_form_certs: bool = False,
) -> dict[str, Any]:
    """Mouth: Roll entry DENY without LIVE evidence. Claimed use ≠ Crown recognition."""
    if self_style_only:
        return _receipt(
            "DENY",
            "self_style_insufficient",
            result={
                "claimed_title_is_not_roll_entry": True,
                "royal_warrant_2004_shaped": True,
            },
        )

    if not claim_id:
        return _receipt(
            "DENY",
            "no_claim",
            result={"petition_required": True},
        )

    c = STORE.claims.get(claim_id)
    if c is None:
        return _receipt("DENY", "no_claim", claim_id=claim_id)

    if short_form_certs or not c.long_form_certs:
        return _receipt(
            "DENY",
            "evidence_insufficient",
            claim_id=claim_id,
            dignity=c.dignity,
            result={"long_form_birth_marriage_death_required": True, "short_form_rejected": True},
        )

    if not c.senior_lines_extinct:
        return _receipt(
            "DENY",
            "senior_line_unproven",
            claim_id=claim_id,
            dignity=c.dignity,
            result={"must_prove_extinction_of_senior_lines": True},
        )

    if not c.petition_filed:
        return _receipt(
            "DENY",
            "petition_missing",
            claim_id=claim_id,
            dignity=c.dignity,
            result={"lord_chancellor_pathway_required": True},
        )

    if c.status == "on_roll" or claim_id in STORE.roll:
        return _receipt(
            "ALLOW",
            "already_on_roll",
            claim_id=claim_id,
            dignity=c.dignity,
            result=STORE.roll.get(claim_id),
        )

    entry_id = str(uuid.uuid4())
    stub = {
        "roll_entry_id": entry_id,
        "claim_id": claim_id,
        "dignity": c.dignity,
        "claimant": c.claimant,
        "precedence": True,
        "real_crown": False,
        "fixture": True,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="peerage_roll"),
    }
    STORE.roll[claim_id] = stub
    c.status = "on_roll"
    return _receipt(
        "ALLOW",
        "entered_on_roll",
        claim_id=claim_id,
        dignity=c.dignity,
        result=stub,
    )


def get_receipt(receipt_id: str) -> dict[str, Any] | None:
    r = STORE.receipts.get(receipt_id)
    if r is None:
        return None
    return {**r, "receipt_url": f"/v1/peerage-roll/receipts/{receipt_id}"}
