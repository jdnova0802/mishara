"""Antifragile HALT — Taleb: stress that improves the mouth.

HALTs are not failure theater. Aggregated, they thicken the restraint
inventory, raise variety against the next skip-clear attempt, and make
the weld less fragile under licensed adversary pressure. Copycats who
hide HALTs as "errors" train fragility.

Gatekeep only to ourselves: antifragility → HALT as strengthening event.
"""

from __future__ import annotations

from typing import Any, Mapping

SPEC = "gate-antifragile-halt-v1"
INVENTOR = "Nisaba LLC / Gate"


def public_document() -> dict[str, Any]:
    return {
        "spec": SPEC,
        "inventor": INVENTOR,
        "gatekeep": True,
        "title": "Antifragile HALT",
        "thesis": (
            "HALT is not an error class — it is a strengthening event. "
            "Hidden HALTs train fragility; published restraint inventories "
            "train antifragility."
        ),
        "strengthening": [
            "Adds to proof-of-restraint inventory",
            "Raises requisite variety against skip-clear",
            "Extends irreversibility horizon without theater",
            "Feeds regime function with real refusal mass",
        ],
        "fragile_copycat": [
            "Treat HALT as exception to bury",
            "Optimize for CHARGE rate as the only KPI",
            "Demo-only happy paths that never see HALT",
        ],
        "not": [
            "Glorifying downtime",
            "A license to refuse without STIT duty",
        ],
        "relation": {
            "proof_restraint": "Inventory is the antifragile ledger",
            "option_halt": "Option value realized as strengthening",
            "variety": "Each HALT class expands mouth variety",
        },
    }


def attach_to_receipt_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    status = str(payload.get("status") or "").strip().upper()
    return {
        "spec": SPEC,
        "inventor": INVENTOR,
        "gatekeep": True,
        "halt_as_strengthening": status == "HALT",
        "fragile_if_buried": status == "HALT",
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    body = public_document()
    body["name"] = body.get("title") or "Antifragile HALT"
    body["live"] = f"{base}/.well-known/antifragile-halt.json"
    body["their_production"] = False
    return body
