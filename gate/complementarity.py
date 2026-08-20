"""Complementarity Mouth — Bohr: CHARGE and HALT are conjugate observables.

You cannot simultaneously optimize for both "maximum flow" and "maximum
restraint" on the same welded channel. Measurement (a CHARGE) collapses
the HALT option; measurement (a HALT) preserves optionality at the cost of
flow. Gate's mouth is the apparatus that forces the conjugate choice —
not a dashboard that pretends both exist at once.

Gatekeep only to ourselves: Bohr complementarity → conjugate CHARGE/HALT.
"""

from __future__ import annotations

from typing import Any, Mapping

SPEC = "gate-complementarity-v1"
INVENTOR = "Nisaba LLC / Gate"


def public_document() -> dict[str, Any]:
    return {
        "spec": SPEC,
        "inventor": INVENTOR,
        "gatekeep": True,
        "title": "Complementarity Mouth",
        "thesis": (
            "CHARGE and HALT are conjugate observables on the same weld. "
            "You cannot maximize both flow and restraint simultaneously; "
            "the mouth forces the conjugate choice."
        ),
        "conjugates": [
            {
                "observable": "CHARGE",
                "measures": "cleared irreversible flow",
                "destroys": "HALT optionality on that weld",
            },
            {
                "observable": "HALT",
                "measures": "preserved optionality",
                "destroys": "realized flow on that weld",
            },
        ],
        "not": [
            "A KPI dashboard claiming both max throughput and max safety",
            "Quantum woo on money rails",
        ],
        "relation": {
            "option_halt": "HALT as real option is the conjugate of CHARGE",
            "regime_function": "regime chooses which conjugate is active",
        },
    }


def attach_to_receipt_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    status = str(payload.get("status") or "").strip().upper()
    return {
        "spec": SPEC,
        "inventor": INVENTOR,
        "gatekeep": True,
        "measured": status if status in {"CHARGE", "HALT"} else "none",
        "conjugate_destroyed": (
            "HALT_optionality" if status == "CHARGE"
            else "flow" if status == "HALT"
            else "n/a"
        ),
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    body = public_document()
    body["name"] = body.get("title") or "Complementarity Mouth"
    body["live"] = f"{base}/.well-known/complementarity.json"
    body["their_production"] = False
    return body
