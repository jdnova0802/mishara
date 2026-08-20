"""Legal Finality Stamp — technical LIVE is not legal irrevocability.

Oxford OBLB 2026: modernisation barriers are legal, not technological.
Zero-hour / insolvency can unwind a ledger 'complete'. Gate never claims
legal Settlement Finality Directive status for a hop — it stamps technical
regime and leaves legal finality to designated systems.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-legal-finality-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def stamp(
    *,
    technical_live: bool | None = None,
    designated_system: bool | None = None,
    claims_legal_finality: bool | None = None,
) -> dict[str, Any]:
    tech = bool(technical_live)
    designated = bool(designated_system)
    claims = bool(claims_legal_finality)
    if claims and not designated:
        posture = "illegal_finality_claim"
        claim = "reject_court_cosplay"
        ok = False
    elif tech and designated:
        posture = "technical_plus_designated"
        claim = "cite_fmi_finality_not_gate"
        ok = True
    elif tech:
        posture = "technical_regime_only"
        claim = "live_is_not_legal_finality"
        ok = True
    else:
        posture = "dead_or_halt"
        claim = "no_finality_claim"
        ok = True
    return {
        "spec": SPEC,
        "name": "Legal Finality Stamp",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Settlement Finality Directive / designation",
            "Zero-hour rule / insolvency unwind risk",
            "Oxford OBLB 2026 — barriers are legal",
            "Gate possibility finality I/II/III — honest layers",
        ],
        "technical_live": tech,
        "designated_system": designated,
        "claims_legal_finality": claims,
        "posture": posture,
        "claim": claim,
        "passes": ok,
        "thesis": "Technical LIVE ≠ legal irrevocability. Honesty is the bite.",
        "gatekeep": "Proprietary legal-finality honesty doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Legal Finality Stamp",
        "inventor": INVENTOR,
        "example_reject_cosplay": stamp(technical_live=True, claims_legal_finality=True),
        "example_honest": stamp(technical_live=True, designated_system=False),
        "live": f"{base}/.well-known/legal-finality.json",
        "hardest": f"{base}/.well-known/hardest.json",
        "their_production": False,
    }
