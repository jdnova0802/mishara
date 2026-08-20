"""Irreversibility Horizon — the distance from now to the irreversible act.

Gate does not sell "governance." It sells a measured horizon: how many
ticks, signatures, and status transitions stand between intention and
wire/bind/withdraw/list. Shorten the horizon only with CHARGE. Lengthen
it with HALT. Copycats who put a policy PDF in that gap have no horizon.

Gatekeep only to ourselves: thermodynamic/time-to-irreversible → horizon.
"""

from __future__ import annotations

from typing import Any, Mapping

SPEC = "gate-irreversibility-horizon-v1"
INVENTOR = "Nisaba LLC / Gate"


def public_document() -> dict[str, Any]:
    return {
        "spec": SPEC,
        "inventor": INVENTOR,
        "gatekeep": True,
        "title": "Irreversibility Horizon",
        "thesis": (
            "The product is the measured distance from intention to the "
            "irreversible act. CHARGE shortens it; HALT lengthens it; "
            "PDFs do neither."
        ),
        "horizon_axes": [
            {"axis": "status", "unit": "DEAD|LIVE transitions", "gate_control": "CHARGE-only LIVE"},
            {"axis": "temporal", "unit": "weld clock ticks", "gate_control": "temporal_weld"},
            {"axis": "evidential", "unit": "binding strength", "gate_control": "bayesian_binding"},
            {"axis": "cost", "unit": "unforgeable costliness", "gate_control": "costliness"},
        ],
        "not": [
            "A compliance calendar",
            "A risk score without a mouth",
        ],
        "relation": {
            "temporal_weld": "Ticks on the weld are one horizon axis",
            "option_halt": "HALT buys horizon length",
            "possibility_finality": "Finality is horizon collapse to zero optionality",
        },
    }


def attach_to_receipt_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    status = str(payload.get("status") or "").strip().upper()
    return {
        "spec": SPEC,
        "inventor": INVENTOR,
        "gatekeep": True,
        "horizon_state": (
            "collapsed" if status == "CHARGE"
            else "extended" if status == "HALT"
            else "open"
        ),
        "irreversible_act_distance": (
            "zero" if status == "CHARGE" else "positive"
        ),
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    body = public_document()
    body["name"] = body.get("title") or "Irreversibility Horizon"
    body["live"] = f"{base}/.well-known/irreversibility-horizon.json"
    body["their_production"] = False
    return body
