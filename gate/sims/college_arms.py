"""Z10 College of Arms Grant — lab mouth: petition ≠ letters patent under Crown.

Lab only. their_production is always False.
Not a generative crest shop. Not heraldry marketplace.
Gates grant on Kings of Arms approval + distinctiveness vs prior arms.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from gate.sims.lab_invariant import stamp_lab_flag
from gate.sims.logos import canonical


SPEC = "nisaba-college-arms-lab-v1"
THEIR_PRODUCTION = False


@dataclass
class Petition:
    petition_id: str
    petitioner: str
    blazon_digest: str
    eligible: bool
    honorary: bool
    pedigree_recorded: bool
    status: str  # pending | granted | refused


@dataclass
class Store:
    petitions: dict[str, Petition] = field(default_factory=dict)
    prior_blazons: set[str] = field(default_factory=set)
    grants: dict[str, dict[str, Any]] = field(default_factory=dict)
    receipts: dict[str, dict[str, Any]] = field(default_factory=dict)


STORE = Store()


def reset() -> None:
    STORE.petitions.clear()
    STORE.prior_blazons.clear()
    STORE.grants.clear()
    STORE.receipts.clear()
    # Seed prior arms so collision DENY is real in lab (same digest path as petitions)
    for seed in ("Azure lion rampant or", "Gules three lions passant"):
        STORE.prior_blazons.add(_blazon_digest(seed))


def _blazon_digest(blazon: str) -> str:
    return hashlib.sha256(blazon.strip().lower().encode("utf-8")).hexdigest()


def _receipt(
    decision: str,
    reason_code: str,
    *,
    petition_id: str | None = None,
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rid = str(uuid.uuid4())
    payload = {
        "spec": SPEC,
        "receipt_id": rid,
        "receipt_class": "clearance",
        "decision": decision,
        "reason_code": reason_code,
        "petition_id": petition_id,
        "result": result,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="college_arms"),
        "ts": time.time(),
    }
    payload["receipt_hash"] = hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()
    STORE.receipts[rid] = payload
    return {**payload, "receipt_url": f"/v1/college-arms/receipts/{rid}"}


def submit_petition(
    *,
    petitioner: str,
    blazon: str,
    eligible: bool = True,
    honorary: bool = False,
    pedigree_recorded: bool = True,
) -> dict[str, Any]:
    if not petitioner or not blazon:
        return {
            "ok": False,
            "reason_code": "malformed_petition",
            "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="college_arms"),
        }
    pid = str(uuid.uuid4())
    digest = _blazon_digest(blazon)
    STORE.petitions[pid] = Petition(
        petition_id=pid,
        petitioner=petitioner,
        blazon_digest=digest,
        eligible=eligible,
        honorary=honorary,
        pedigree_recorded=pedigree_recorded,
        status="pending",
    )
    return {
        "petition_id": pid,
        "blazon_digest": digest,
        "status": "pending",
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="college_arms"),
    }


def grant_arms(
    petition_id: str | None,
    *,
    generative_spam: bool = False,
    kings_of_arms_approve: bool = True,
) -> dict[str, Any]:
    """Mouth: letters patent DENY without LIVE petition + distinctiveness + eligibility."""
    if generative_spam:
        return _receipt(
            "DENY",
            "generative_crest_refused",
            result={
                "ai_crest_is_not_letters_patent": True,
                "kings_of_arms_required": True,
            },
        )

    if not petition_id:
        return _receipt(
            "DENY",
            "no_petition",
            result={"memorial_to_earl_marshal_required": True},
        )

    p = STORE.petitions.get(petition_id)
    if p is None:
        return _receipt("DENY", "no_petition", petition_id=petition_id)

    if not p.eligible:
        return _receipt(
            "DENY",
            "ineligible_petitioner",
            petition_id=petition_id,
            result={"crown_criteria_not_met": True},
        )

    if p.honorary and not p.pedigree_recorded:
        return _receipt(
            "DENY",
            "honorary_pedigree_missing",
            petition_id=petition_id,
            result={"descent_from_crown_subject_required": True},
        )

    if p.blazon_digest in STORE.prior_blazons:
        return _receipt(
            "DENY",
            "arms_not_distinct",
            petition_id=petition_id,
            result={"collision_with_prior_grant": True, "blazon_digest": p.blazon_digest},
        )

    if not kings_of_arms_approve:
        return _receipt(
            "DENY",
            "kings_of_arms_refused",
            petition_id=petition_id,
            result={"approval_required": True},
        )

    if p.status == "granted" or petition_id in STORE.grants:
        return _receipt(
            "ALLOW",
            "already_granted",
            petition_id=petition_id,
            result=STORE.grants.get(petition_id),
        )

    gid = str(uuid.uuid4())
    stub = {
        "grant_id": gid,
        "petition_id": petition_id,
        "petitioner": p.petitioner,
        "blazon_digest": p.blazon_digest,
        "letters_patent": f"SIM-LP-{gid[:8]}",
        "sealed": True,
        "real_college": False,
        "fixture": True,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="college_arms"),
    }
    STORE.grants[petition_id] = stub
    STORE.prior_blazons.add(p.blazon_digest)
    p.status = "granted"
    return _receipt(
        "ALLOW",
        "letters_patent_sealed",
        petition_id=petition_id,
        result=stub,
    )


def get_receipt(receipt_id: str) -> dict[str, Any] | None:
    r = STORE.receipts.get(receipt_id)
    if r is None:
        return None
    return {**r, "receipt_url": f"/v1/college-arms/receipts/{receipt_id}"}
