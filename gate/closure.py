"""Permission Autopoiesis — operational closure of the mouth.

Maturana/Varela → Luhmann: organizations reproduce decisions from decisions;
operationally closed, cognitively open.

Gate: the permission system reproduces LIVE/DEAD/HALT/ALLOW only from its own
operations (hop → ticket → redeem → CHARGE → weld). External 'looks live'
signals cannot enter the decision network. Fail-closed is the engineering
face of operational closure.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-closure-v1"
INVENTOR = "Nisaba LLC / Gate"

# Operations that are *inside* the permission autopoiesis.
INTERNAL_OPS = (
    "fuse_hop",
    "bind_ticket_print",
    "bind_ticket_redeem",
    "epoch_lock",
    "license_parent_charge",
    "license_parent_blow",
    "operator_weld",
    "settlement_window_close",
    "restraint_halt",
)

# Signals that must NOT enter as if they were internal decisions.
EXTERNAL_REJECTED = (
    "uw_approve_without_charge",
    "carrier_email_ok",
    "dashboard_green",
    "model_confidence_score",
    "counterparty_assurance",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def classify_operation(op: str | None) -> dict[str, Any]:
    name = (op or "").strip()
    if name in INTERNAL_OPS:
        return {
            "operation": name,
            "side": "internal",
            "enters_decision_network": True,
            "claim": "autopoietic_reproduction",
        }
    if name in EXTERNAL_REJECTED or name.startswith("external_"):
        return {
            "operation": name,
            "side": "environment",
            "enters_decision_network": False,
            "claim": "cognitively_observable_operationally_excluded",
        }
    return {
        "operation": name or None,
        "side": "unknown",
        "enters_decision_network": False,
        "claim": "fail_closed_unknown_op",
    }


def closure_report(
    *,
    last_op: str | None = None,
    fail_closed: bool = True,
    their_production: bool = False,
) -> dict[str, Any]:
    classified = classify_operation(last_op)
    return {
        "spec": SPEC,
        "name": "Permission Autopoiesis",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Maturana & Varela — autopoiesis / operational closure",
            "Luhmann — organizations as decision-reproducing systems; double closure",
            "Gate — fail-closed mouth; external soft-yes cannot enter permission network",
        ],
        "operational_closure": {
            "meaning": "Permission decisions reproduce only from Gate/Velaru internal ops",
            "fail_closed": fail_closed,
            "internal_operations": list(INTERNAL_OPS),
        },
        "cognitive_openness": {
            "meaning": "Mouth may observe environment (risk, hop body) but observation ≠ decision entry",
            "external_rejected_as_decisions": list(EXTERNAL_REJECTED),
        },
        "double_closure": {
            "operations": "decisions from hops/tickets/CHARGE only",
            "structures": "epoch, license fuse, spend protocol — premises also internal",
        },
        "last_operation": classified,
        "their_production": their_production,
        "thesis": "Fail-closed is operational closure with teeth.",
        "gatekeep": "Proprietary autopoietic framing of the permission mouth. Ours.",
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    body = closure_report(last_op="restraint_halt", fail_closed=True)
    body["live"] = f"{base}/.well-known/closure.json"
    body["license_fuse"] = f"{base}/.well-known/license-fuse.json"
    body["epoch_note"] = "Epoch lock is structural closure: prior HALT remains until CHARGE witness."
    return body
