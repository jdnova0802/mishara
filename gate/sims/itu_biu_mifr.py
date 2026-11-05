"""Z5 ITU Bring-Into-Use / MIFR — lab mouth: paper filing ≠ recorded assignment.

Lab only. their_production is always False.
Not constellation planning SaaS. Not spectrum analytics.
Gates record/protect on coordination + BIU evidence only.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from gate.sims.lab_invariant import stamp_lab_flag
from gate.sims.logos import canonical


SPEC = "nisaba-itu-biu-mifr-lab-v1"
THEIR_PRODUCTION = False


@dataclass
class Filing:
    filing_id: str
    admin: str
    network_name: str
    orbital_slot: str
    freq_band: str
    status: str  # api | coordination | notified | recorded
    coordinated: bool
    biu_days: int
    biu_evidence: bool


@dataclass
class Store:
    filings: dict[str, Filing] = field(default_factory=dict)
    receipts: dict[str, dict[str, Any]] = field(default_factory=dict)
    mifr: dict[str, dict[str, Any]] = field(default_factory=dict)


STORE = Store()


def reset() -> None:
    STORE.filings.clear()
    STORE.receipts.clear()
    STORE.mifr.clear()


def _receipt(
    decision: str,
    reason_code: str,
    *,
    filing_id: str | None = None,
    network_name: str | None = None,
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rid = str(uuid.uuid4())
    payload = {
        "spec": SPEC,
        "receipt_id": rid,
        "receipt_class": "clearance",
        "decision": decision,
        "reason_code": reason_code,
        "filing_id": filing_id,
        "network_name": network_name,
        "result": result,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="itu_biu_mifr"),
        "ts": time.time(),
    }
    payload["receipt_hash"] = hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()
    STORE.receipts[rid] = payload
    return {**payload, "receipt_url": f"/v1/itu-biu/receipts/{rid}"}


def submit_filing(
    *,
    admin: str,
    network_name: str,
    orbital_slot: str,
    freq_band: str,
    status: str = "api",
) -> dict[str, Any]:
    if not admin or not network_name or not orbital_slot or not freq_band:
        return {
            "ok": False,
            "reason_code": "malformed_filing",
            "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="itu_biu_mifr"),
        }
    if status not in ("api", "coordination", "notified", "recorded"):
        return {
            "ok": False,
            "reason_code": "malformed_status",
            "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="itu_biu_mifr"),
        }
    fid = str(uuid.uuid4())
    STORE.filings[fid] = Filing(
        filing_id=fid,
        admin=admin,
        network_name=network_name,
        orbital_slot=orbital_slot,
        freq_band=freq_band,
        status=status,
        coordinated=False,
        biu_days=0,
        biu_evidence=False,
    )
    return {
        "filing_id": fid,
        "network_name": network_name,
        "status": status,
        "paper_satellite_risk": status in ("api", "coordination"),
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="itu_biu_mifr"),
    }


def mark_coordinated(filing_id: str) -> dict[str, Any]:
    f = STORE.filings.get(filing_id)
    if f is None:
        return _receipt("DENY", "no_filing", filing_id=filing_id)
    f.coordinated = True
    if f.status == "api":
        f.status = "coordination"
    return {
        "filing_id": filing_id,
        "coordinated": True,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="itu_biu_mifr"),
    }


def record_biu(
    filing_id: str,
    *,
    biu_days: int,
    evidence: bool,
) -> dict[str, Any]:
    f = STORE.filings.get(filing_id)
    if f is None:
        return _receipt("DENY", "no_filing", filing_id=filing_id)
    f.biu_days = int(biu_days)
    f.biu_evidence = bool(evidence)
    return {
        "filing_id": filing_id,
        "biu_days": f.biu_days,
        "biu_evidence": f.biu_evidence,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="itu_biu_mifr"),
    }


def notify_and_record(filing_id: str) -> dict[str, Any]:
    """Mouth: MIFR record only after coordination + BIU (≥90 days, evidence).

    Paper filing alone → DENY (paper-satellite shaped).
    """
    f = STORE.filings.get(filing_id)
    if f is None:
        return _receipt("DENY", "no_filing", filing_id=filing_id)

    if f.status == "api" and not f.coordinated:
        return _receipt(
            "DENY",
            "api_only_paper",
            filing_id=filing_id,
            network_name=f.network_name,
            result={
                "paper_satellite": True,
                "filing_is_not_assignment": True,
                "rr_art_9_11_shaped": True,
            },
        )

    if not f.coordinated:
        return _receipt(
            "DENY",
            "coordination_incomplete",
            filing_id=filing_id,
            network_name=f.network_name,
            result={"cannot_notify_without_coordination": True},
        )

    if f.biu_days < 90:
        return _receipt(
            "DENY",
            "biu_period_insufficient",
            filing_id=filing_id,
            network_name=f.network_name,
            result={"biu_days": f.biu_days, "required_days": 90},
        )

    if not f.biu_evidence:
        return _receipt(
            "DENY",
            "biu_evidence_missing",
            filing_id=filing_id,
            network_name=f.network_name,
            result={"bring_into_use_unproven": True},
        )

    if f.status == "recorded" or filing_id in STORE.mifr:
        return _receipt(
            "ALLOW",
            "already_recorded",
            filing_id=filing_id,
            network_name=f.network_name,
            result=STORE.mifr.get(filing_id),
        )

    mid = str(uuid.uuid4())
    entry = {
        "mifr_id": mid,
        "filing_id": filing_id,
        "admin": f.admin,
        "network_name": f.network_name,
        "orbital_slot": f.orbital_slot,
        "freq_band": f.freq_band,
        "biu_days": f.biu_days,
        "protection": True,
        "real_itu": False,
        "fixture": True,
        "br_ific_sim": f"SIM-IFIC-{mid[:8]}",
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="itu_biu_mifr"),
    }
    STORE.mifr[filing_id] = entry
    f.status = "recorded"
    return _receipt(
        "ALLOW",
        "mifr_recorded",
        filing_id=filing_id,
        network_name=f.network_name,
        result=entry,
    )


def get_receipt(receipt_id: str) -> dict[str, Any] | None:
    r = STORE.receipts.get(receipt_id)
    if r is None:
        return None
    return {**r, "receipt_url": f"/v1/itu-biu/receipts/{receipt_id}"}
