"""Semiotics of the Mouth — Peirce: icon, index, symbol of clearance.

A CHARGE receipt is not a metaphor. It is an index (causal link to the
weld), an icon (structural map of the married write), and a symbol
(licensed meaning of LIVE). Competitors who ship "AI approved" badges
have symbols without indices — empty semiotics. Gate refuses that.

Gatekeep only to ourselves: Peircean triad → receipt as real sign.
"""

from __future__ import annotations

from typing import Any, Mapping

SPEC = "gate-semiotics-v1"
INVENTOR = "Nisaba LLC / Gate"


def public_document() -> dict[str, Any]:
    return {
        "spec": SPEC,
        "inventor": INVENTOR,
        "gatekeep": True,
        "title": "Semiotics of the Mouth",
        "thesis": (
            "A CHARGE is icon + index + symbol of clearance. Badges without "
            "a causal weld are symbols with no index — empty semiotics."
        ),
        "triad": {
            "icon": "Receipt structure mirrors the married write",
            "index": "Causal link from CHARGE to DEAD→LIVE on the weld",
            "symbol": "Licensed meaning of LIVE in the operator regime",
        },
        "empty_semiotics": [
            "AI-approved stickers with no weld",
            "Policy PDFs that never touch the irreversible path",
            "Dashboard greens without CHARGE costliness",
        ],
        "not": [
            "Literary theory cosplay on the homepage",
            "A replacement for cryptographic binding",
        ],
        "relation": {
            "performative": "Austin/Searle speech-act layer; this is the sign layer",
            "nonrepudiation": "Indexical chain makes repudiation costly",
            "bayesian_binding": "Evidential strength of the index",
        },
    }


def attach_to_receipt_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    status = str(payload.get("status") or "").strip().upper()
    has_charge = status == "CHARGE"
    return {
        "spec": SPEC,
        "inventor": INVENTOR,
        "gatekeep": True,
        "icon": True,
        "index": has_charge,
        "symbol": has_charge,
        "empty_semiotics": not has_charge and status not in {"HALT", "DEAD"},
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    body = public_document()
    body["name"] = body.get("title") or "Semiotics of the Mouth"
    body["live"] = f"{base}/.well-known/semiotics.json"
    body["their_production"] = False
    return body
