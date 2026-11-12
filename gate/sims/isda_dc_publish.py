"""Z1 ISDA DC Resolution Publish — lab mouth: headline ≠ Credit Event.

Lab only. their_production is always False.
Not a CDS trading product. Not news sentiment.
Gates treat_as_credit_event on LIVE DC Resolution only.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from gate.sims.lab_invariant import stamp_lab_flag
from gate.sims.logos import action_digest, canonical


SPEC = "nisaba-isda-dc-publish-lab-v1"
THEIR_PRODUCTION = False

# Fixture entities — lab only, not real DC determinations.
KNOWN_ENTITIES = frozenset({"ACME_CORP", "ARDAGH_FIXTURE", "AVON_FIXTURE"})


@dataclass
class Resolution:
    resolution_id: str
    entity: str
    event_type: str
    status: str  # draft | LIVE
    deliverable_list_hash: str
    auction_terms_hash: str | None
    published_at: float | None


@dataclass
class Store:
    resolutions: dict[str, Resolution] = field(default_factory=dict)
    receipts: dict[str, dict[str, Any]] = field(default_factory=dict)


STORE = Store()


def reset() -> None:
    STORE.resolutions.clear()
    STORE.receipts.clear()


def _receipt(
    decision: str,
    reason_code: str,
    *,
    entity: str | None = None,
    event_type: str | None = None,
    resolution_id: str | None = None,
    digest: str | None = None,
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rid = str(uuid.uuid4())
    payload = {
        "spec": SPEC,
        "receipt_id": rid,
        "receipt_class": "clearance",
        "decision": decision,
        "reason_code": reason_code,
        "entity": entity,
        "event_type": event_type,
        "resolution_id": resolution_id,
        "digest": digest,
        "result": result,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="isda_dc_publish"),
        "ts": time.time(),
    }
    payload["receipt_hash"] = hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()
    STORE.receipts[rid] = payload
    return {**payload, "receipt_url": f"/v1/isda-dc/receipts/{rid}"}


def plant_resolution(
    *,
    entity: str,
    event_type: str,
    status: str = "LIVE",
    deliverables: list[str] | None = None,
    auction_terms: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Lab fixture: plant a DC Resolution (draft or LIVE). Not a real DC."""
    if entity not in KNOWN_ENTITIES:
        return {
            "ok": False,
            "reason_code": "unknown_entity_fixture",
            "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="isda_dc_publish"),
        }
    if event_type not in ("Bankruptcy", "FailureToPay", "Restructuring", "ObligationAcceleration"):
        return {
            "ok": False,
            "reason_code": "unsupported_event_type",
            "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="isda_dc_publish"),
        }
    if status not in ("draft", "LIVE"):
        return {
            "ok": False,
            "reason_code": "malformed_status",
            "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="isda_dc_publish"),
        }
    rid = str(uuid.uuid4())
    dlist = list(deliverables or [])
    dhash = hashlib.sha256(canonical({"deliverables": dlist}).encode("utf-8")).hexdigest()
    ahash = (
        hashlib.sha256(canonical(auction_terms).encode("utf-8")).hexdigest()
        if auction_terms
        else None
    )
    STORE.resolutions[rid] = Resolution(
        resolution_id=rid,
        entity=entity,
        event_type=event_type,
        status=status,
        deliverable_list_hash=dhash,
        auction_terms_hash=ahash,
        published_at=time.time() if status == "LIVE" else None,
    )
    return {
        "resolution_id": rid,
        "entity": entity,
        "event_type": event_type,
        "status": status,
        "deliverable_list_hash": dhash,
        "auction_terms_hash": ahash,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="isda_dc_publish"),
    }


def publish_resolution(resolution_id: str) -> dict[str, Any]:
    """Promote draft → LIVE. Lab only."""
    r = STORE.resolutions.get(resolution_id)
    if r is None:
        return _receipt("DENY", "no_resolution", resolution_id=resolution_id)
    if r.status == "LIVE":
        return _receipt(
            "ALLOW",
            "already_live",
            entity=r.entity,
            event_type=r.event_type,
            resolution_id=resolution_id,
            result={"status": "LIVE"},
        )
    r.status = "LIVE"
    r.published_at = time.time()
    return _receipt(
        "ALLOW",
        "resolution_published",
        entity=r.entity,
        event_type=r.event_type,
        resolution_id=resolution_id,
        result={
            "status": "LIVE",
            "deliverable_list_hash": r.deliverable_list_hash,
            "auction_terms_hash": r.auction_terms_hash,
        },
    )


def treat_as_credit_event(
    entity: str,
    event_type: str,
    *,
    resolution_id: str | None = None,
    source: str = "agent",
    headline: str | None = None,
) -> dict[str, Any]:
    """Mouth: refuse to treat entity as Credit Event without LIVE DC Resolution.

    NEVER ALLOW on scrape/headline alone.
    """
    digest = action_digest(
        "treat_as_credit_event",
        {"entity": entity, "event_type": event_type, "resolution_id": resolution_id},
    )

    if source in ("headline", "scrape", "news", "sentiment") or headline:
        return _receipt(
            "DENY",
            "headline_only",
            entity=entity,
            event_type=event_type,
            digest=digest,
            result={"source": source, "headline": headline, "never_scrape_allow": True},
        )

    if not resolution_id:
        return _receipt(
            "DENY",
            "no_resolution",
            entity=entity,
            event_type=event_type,
            digest=digest,
        )

    r = STORE.resolutions.get(resolution_id)
    if r is None:
        return _receipt(
            "DENY",
            "no_resolution",
            entity=entity,
            event_type=event_type,
            resolution_id=resolution_id,
            digest=digest,
        )

    if r.status == "draft":
        return _receipt(
            "DENY",
            "draft_only",
            entity=entity,
            event_type=event_type,
            resolution_id=resolution_id,
            digest=digest,
            result={"status": "draft", "meeting_statement_not_binding": True},
        )

    if r.status != "LIVE":
        return _receipt(
            "DENY",
            "resolution_not_live",
            entity=entity,
            event_type=event_type,
            resolution_id=resolution_id,
            digest=digest,
        )

    if r.entity != entity or r.event_type != event_type:
        return _receipt(
            "DENY",
            "resolution_mismatch",
            entity=entity,
            event_type=event_type,
            resolution_id=resolution_id,
            digest=digest,
            result={"resolution_entity": r.entity, "resolution_event": r.event_type},
        )

    return _receipt(
        "ALLOW",
        "dc_resolution_live",
        entity=entity,
        event_type=event_type,
        resolution_id=resolution_id,
        digest=digest,
        result={
            "binding": True,
            "deliverable_list_hash": r.deliverable_list_hash,
            "auction_terms_hash": r.auction_terms_hash,
            "real_dc": False,
            "fixture": True,
        },
    )


def get_receipt(receipt_id: str) -> dict[str, Any] | None:
    r = STORE.receipts.get(receipt_id)
    if r is None:
        return None
    return {**r, "receipt_url": f"/v1/isda-dc/receipts/{receipt_id}"}
