"""Temporal Weld — intentional/causal binding of act and consequence.

Haggard intentional binding: voluntary action and outcome compress in time.
Gate: the irreversible act and its evidence consequence are welded into one
citeable event — receipt hash + verify URL + decision — so agency over the
write is not a vibe; it is a temporal/evidentiary bind.

Also: cryptographic commitment binding (commit now, open later) maps to
ticket print → redeem, and hop → stranger verify.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-temporal-weld-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def weld(
    *,
    decision: str | None,
    acted: bool | None,
    event_id: str | None = None,
    created_at: str | None = None,
    receipt_hash: str | None = None,
    verify_url: str | None = None,
    job_id: str | None = None,
) -> dict[str, Any]:
    """Bind action-side and consequence-side into one evidence event."""
    d = (decision or "").upper()
    action_side = {
        "kind": "mouth_decision",
        "decision": d or None,
        "acted": acted,
        "job_id": job_id,
        "at": created_at,
    }
    consequence_side = {
        "kind": "evidence_consequence",
        "event_id": event_id,
        "receipt_hash": receipt_hash,
        "verify_url": verify_url,
        "stranger_verifiable": bool(verify_url),
    }
    bound = bool(event_id) and bool(d)
    compression = {
        "claim": "action_and_consequence_welded_into_one_citeable_event",
        "not_mere_log_line": True,
        "intentional_binding_analog": (
            "Subjective compression ↔ institutional compression: "
            "act and outcome are not separable museum objects."
        ),
    }
    return {
        "spec": SPEC,
        "name": "Temporal Weld",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Haggard intentional binding — action and outcome temporally compressed",
            "Causal binding — related events bound in experienced time",
            "Cryptographic commitment — bind now, open/verify later",
            "Gate receipts — decision + hash + verify URL as one event",
        ],
        "action_side": action_side,
        "consequence_side": consequence_side,
        "welded": bound,
        "compression": compression,
        "commitment_phases": {
            "commit": "hop / ticket print (value fixed, not yet spent)",
            "reveal": "redeem / stranger verify / receipt fetch",
            "binding_property": "cannot reinterpret HALT as ALLOW without CHARGE witness",
        },
        "thesis": "Agency over irreversible spend is a weld between act and evidence, not a feeling.",
        "gatekeep": "Proprietary temporal/evidentiary weld for mouth decisions. Ours.",
        "their_production": False,
    }


def attach_to_receipt_payload(payload: dict, row: dict) -> dict:
    payload["temporal_weld"] = weld(
        decision=row.get("decision"),
        acted=row.get("acted"),
        event_id=row.get("id"),
        created_at=row.get("created_at"),
        receipt_hash=row.get("receipt_hash"),
        verify_url=row.get("verify_url"),
        job_id=row.get("job_id"),
    )
    return payload


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Temporal Weld",
        "inventor": INVENTOR,
        "thesis": (
            "Action and consequence are welded: receipt + verify + decision "
            "are one citeable event — intentional binding for infrastructure."
        ),
        "example": weld(
            decision="HALT",
            acted=False,
            event_id="evt_example",
            created_at=_now(),
            receipt_hash="0" * 64,
            verify_url="https://velaru.xyz/verify",
            job_id="pc:EXAMPLE",
        ),
        "live": f"{base}/.well-known/temporal-weld.json",
        "receipt": f"{base}/.well-known/receipt/{{event_id}}.json",
        "their_production": False,
    }
