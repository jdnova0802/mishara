"""Z4 Lloyd's Binding Authority Stamp — lab mouth: paperwork ≠ registered bind.

Lab only. their_production is always False.
Not market analytics. Not a coverholder CRM.
Gates bind/issue on LIVE registered Binding Authority Agreement only.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from gate.sims.lab_invariant import stamp_lab_flag
from gate.sims.logos import canonical


SPEC = "nisaba-lloyds-bind-stamp-lab-v1"
THEIR_PRODUCTION = False


@dataclass
class BindingAuthority:
    baa_id: str
    coverholder_id: str
    syndicate_ids: list[str]
    classes: list[str]
    max_limit_usd: int
    status: str  # draft | LIVE | suspended
    registered: bool


@dataclass
class Store:
    authorities: dict[str, BindingAuthority] = field(default_factory=dict)
    receipts: dict[str, dict[str, Any]] = field(default_factory=dict)
    binds: dict[str, dict[str, Any]] = field(default_factory=dict)


STORE = Store()


def reset() -> None:
    STORE.authorities.clear()
    STORE.receipts.clear()
    STORE.binds.clear()


def _receipt(
    decision: str,
    reason_code: str,
    *,
    baa_id: str | None = None,
    coverholder_id: str | None = None,
    syndicate_id: str | None = None,
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rid = str(uuid.uuid4())
    payload = {
        "spec": SPEC,
        "receipt_id": rid,
        "receipt_class": "clearance",
        "decision": decision,
        "reason_code": reason_code,
        "baa_id": baa_id,
        "coverholder_id": coverholder_id,
        "syndicate_id": syndicate_id,
        "result": result,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="lloyds_bind_stamp"),
        "ts": time.time(),
    }
    payload["receipt_hash"] = hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()
    STORE.receipts[rid] = payload
    return {**payload, "receipt_url": f"/v1/lloyds-bind/receipts/{rid}"}


def create_baa(
    *,
    coverholder_id: str,
    syndicate_ids: list[str],
    classes: list[str],
    max_limit_usd: int,
    status: str = "draft",
    registered: bool = False,
) -> dict[str, Any]:
    if not coverholder_id or not syndicate_ids or not classes:
        return {
            "ok": False,
            "reason_code": "malformed_baa",
            "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="lloyds_bind_stamp"),
        }
    if status not in ("draft", "LIVE", "suspended"):
        return {
            "ok": False,
            "reason_code": "malformed_status",
            "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="lloyds_bind_stamp"),
        }
    bid = str(uuid.uuid4())
    STORE.authorities[bid] = BindingAuthority(
        baa_id=bid,
        coverholder_id=coverholder_id,
        syndicate_ids=list(syndicate_ids),
        classes=list(classes),
        max_limit_usd=int(max_limit_usd),
        status=status,
        registered=bool(registered),
    )
    return {
        "baa_id": bid,
        "coverholder_id": coverholder_id,
        "status": status,
        "registered": registered,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="lloyds_bind_stamp"),
    }


def register_baa(baa_id: str) -> dict[str, Any]:
    """Lloyd's-shaped registration: draft → LIVE + registered. Lab fixture."""
    b = STORE.authorities.get(baa_id)
    if b is None:
        return _receipt("DENY", "no_baa", baa_id=baa_id)
    if b.status == "suspended":
        return _receipt(
            "DENY",
            "baa_suspended",
            baa_id=baa_id,
            coverholder_id=b.coverholder_id,
        )
    b.registered = True
    b.status = "LIVE"
    return _receipt(
        "ALLOW",
        "baa_registered",
        baa_id=baa_id,
        coverholder_id=b.coverholder_id,
        result={"status": "LIVE", "registered": True, "real_lloyds": False},
    )


def suspend_baa(baa_id: str) -> None:
    b = STORE.authorities.get(baa_id)
    if b:
        b.status = "suspended"


def stamp_bind(
    *,
    baa_id: str | None,
    coverholder_id: str,
    syndicate_id: str,
    class_of_business: str,
    limit_usd: int,
    risk_ref: str,
) -> dict[str, Any]:
    """Mouth: issue/bind only with LIVE registered BAA in scope.

    Fake stamp / unregistered authority → DENY (byelaw-shaped).
    """
    if not baa_id:
        return _receipt(
            "DENY",
            "no_baa",
            coverholder_id=coverholder_id,
            syndicate_id=syndicate_id,
            result={"stamp_without_authority": True, "byelaw_shaped": True},
        )

    b = STORE.authorities.get(baa_id)
    if b is None:
        return _receipt(
            "DENY",
            "no_baa",
            baa_id=baa_id,
            coverholder_id=coverholder_id,
            syndicate_id=syndicate_id,
            result={"fake_or_unknown_stamp": True},
        )

    if b.coverholder_id != coverholder_id:
        return _receipt(
            "DENY",
            "coverholder_mismatch",
            baa_id=baa_id,
            coverholder_id=coverholder_id,
            syndicate_id=syndicate_id,
            result={"baa_coverholder": b.coverholder_id},
        )

    if not b.registered:
        return _receipt(
            "DENY",
            "baa_not_registered",
            baa_id=baa_id,
            coverholder_id=coverholder_id,
            syndicate_id=syndicate_id,
            result={"cannot_bind_until_registered": True, "byelaw_31_32_shaped": True},
        )

    if b.status == "draft":
        return _receipt(
            "DENY",
            "baa_draft",
            baa_id=baa_id,
            coverholder_id=coverholder_id,
            syndicate_id=syndicate_id,
        )

    if b.status == "suspended":
        return _receipt(
            "DENY",
            "baa_suspended",
            baa_id=baa_id,
            coverholder_id=coverholder_id,
            syndicate_id=syndicate_id,
        )

    if b.status != "LIVE":
        return _receipt(
            "DENY",
            "baa_not_live",
            baa_id=baa_id,
            coverholder_id=coverholder_id,
            syndicate_id=syndicate_id,
        )

    if syndicate_id not in b.syndicate_ids:
        return _receipt(
            "DENY",
            "syndicate_not_on_baa",
            baa_id=baa_id,
            coverholder_id=coverholder_id,
            syndicate_id=syndicate_id,
            result={"allowed_syndicates": list(b.syndicate_ids)},
        )

    if class_of_business not in b.classes:
        return _receipt(
            "DENY",
            "class_out_of_scope",
            baa_id=baa_id,
            coverholder_id=coverholder_id,
            syndicate_id=syndicate_id,
            result={"class": class_of_business, "allowed": list(b.classes)},
        )

    try:
        limit = int(limit_usd)
    except (TypeError, ValueError):
        return _receipt(
            "DENY",
            "malformed_limit",
            baa_id=baa_id,
            coverholder_id=coverholder_id,
            syndicate_id=syndicate_id,
        )

    if limit > b.max_limit_usd:
        return _receipt(
            "DENY",
            "over_authority_limit",
            baa_id=baa_id,
            coverholder_id=coverholder_id,
            syndicate_id=syndicate_id,
            result={"limit_usd": limit, "max_limit_usd": b.max_limit_usd},
        )

    if not risk_ref:
        return _receipt(
            "DENY",
            "risk_ref_missing",
            baa_id=baa_id,
            coverholder_id=coverholder_id,
            syndicate_id=syndicate_id,
        )

    bind_id = str(uuid.uuid4())
    stub = {
        "bind_id": bind_id,
        "baa_id": baa_id,
        "coverholder_id": coverholder_id,
        "syndicate_id": syndicate_id,
        "class_of_business": class_of_business,
        "limit_usd": limit,
        "risk_ref": risk_ref,
        "stamp": f"SIM-LLD-{syndicate_id}-{bind_id[:8]}",
        "real_lloyds": False,
        "fixture": True,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="lloyds_bind_stamp"),
    }
    STORE.binds[bind_id] = stub
    return _receipt(
        "ALLOW",
        "bound_under_authority",
        baa_id=baa_id,
        coverholder_id=coverholder_id,
        syndicate_id=syndicate_id,
        result=stub,
    )


def get_receipt(receipt_id: str) -> dict[str, Any] | None:
    r = STORE.receipts.get(receipt_id)
    if r is None:
        return None
    return {**r, "receipt_url": f"/v1/lloyds-bind/receipts/{receipt_id}"}
