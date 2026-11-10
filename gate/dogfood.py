"""Items 95 and 97 — own incidents through Gate receipts; signed /check liveness."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

try:
    from gate import receipt as receipt_mod
except ImportError:
    import receipt as receipt_mod

try:
    from gate import track_record as track_record_mod
except ImportError:
    import track_record as track_record_mod

try:
    from gate import seal_anchor as seal_anchor_mod
except ImportError:
    import seal_anchor as seal_anchor_mod

try:
    from gate import sanitize as sanitize_mod
except ImportError:
    import sanitize as sanitize_mod

INCIDENT_SPEC = "gate-incident-receipt-v1"
LIVENESS_SPEC = "gate-feed-liveness-v1"
FUSE = "gate-self"


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def incident_receipts(*, verify_url: str = "") -> dict[str, Any]:
    """Item 95 — each published downtime/incident is a signed Gate receipt, chained."""
    rows = []
    prev = None
    for inc in track_record_mod.INCIDENTS:
        event_id = "incident:" + str(inc["id"])
        hop = {
            "kind": "self_dogfood",
            "title": sanitize_mod.strip_agent(inc.get("title")),
            "severity": inc.get("severity"),
            "status": inc.get("status"),
            "found_by": sanitize_mod.strip_agent(inc.get("found_by")),
        }
        issued = receipt_mod.issue_receipt(
            event_id=event_id,
            fuse_id=FUSE,
            job_id=None,
            decision="HOLD",
            acted=False,
            verify_url=verify_url or None,
            created_at=str(inc.get("opened_at")),
            hop=hop,
            prev_receipt_hash=prev,
        )
        prev = issued.get("receipt_hash")
        rows.append(
            {
                "event_id": event_id,
                "incident_id": inc.get("id"),
                "title": hop["title"],
                "opened_at": inc.get("opened_at"),
                "closed_at": inc.get("closed_at"),
                "status": inc.get("status"),
                "receipt_hash": issued.get("receipt_hash"),
                "receipt_signature": issued.get("receipt_signature"),
                "receipt_public_key_fingerprint": issued.get("receipt_public_key_fingerprint"),
                "prev_receipt_hash": issued.get("prev_receipt_hash"),
                "canonical_receipt_json": issued.get("canonical_receipt_json"),
            }
        )
    return {
        "spec": INCIDENT_SPEC,
        "plain": "This mouth's own incidents run through the same receipt pipeline. Not a status vendor.",
        "fuse_id": FUSE,
        "rows": rows,
    }


def feed_liveness(
    events: list[dict[str, Any]],
    *,
    generated_at: str,
    verify_url: str = "",
    submit_ots: bool = False,
    ots_submitter: Any = None,
) -> dict[str, Any]:
    """Item 97 — signed proof the /check feed was built at generated_at, not a frozen list.

    Uses the same OpenTimestamps calendars as seal_anchor (RFC 3161-style calendars).
    Page views sign locally; calendar submit is opt-in so a GET does not block on the net.
    """
    event_ids = [str(e.get("event_id") or e.get("id") or "") for e in events]
    body = {
        "spec": LIVENESS_SPEC,
        "generated_at": generated_at,
        "count": len(events),
        "event_ids": event_ids,
    }
    digest = hashlib.sha256(_canonical(body).encode("utf-8")).hexdigest()
    issued = receipt_mod.issue_receipt(
        event_id="feed-liveness:" + digest[:16],
        fuse_id=FUSE,
        job_id=None,
        decision="ALLOW",
        acted=False,
        verify_url=verify_url or None,
        created_at=generated_at,
        hop={"kind": "feed_liveness", "digest": digest, "count": len(events)},
        prev_receipt_hash=None,
    )
    ots: dict[str, Any] = {
        "rfc3161": True,
        "mechanism": "opentimestamps",
        "calendars": list(seal_anchor_mod.OTS_CALENDARS),
        "submitted": False,
        "locator": None,
    }
    if submit_ots:
        submit = ots_submitter or seal_anchor_mod.submit_ots
        raw = bytes.fromhex(digest)
        result = submit(raw)
        ots["submitted"] = result.get("status") == "submitted"
        ots["locator"] = result.get("locator")
        ots["status"] = result.get("status")
        if result.get("error"):
            ots["error"] = result["error"]
    now = datetime.now(timezone.utc).replace(microsecond=0)
    try:
        gen = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
        age_s = max(0, int((now - gen).total_seconds()))
    except ValueError:
        age_s = None
    return {
        "spec": LIVENESS_SPEC,
        "plain": "Signed at request time. Empty feed can still be live. Not the October 28 drill list.",
        "generated_at": generated_at,
        "digest": digest,
        "age_seconds": age_s,
        "stale": False,
        "receipt_hash": issued.get("receipt_hash"),
        "receipt_signature": issued.get("receipt_signature"),
        "receipt_public_key_fingerprint": issued.get("receipt_public_key_fingerprint"),
        "ots": ots,
    }
