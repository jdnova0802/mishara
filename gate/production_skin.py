"""Production skin — honesty gate for their_production.

Lite skin for the Action OS branch: env flag only until a real weld
is recorded. Never claim production from demo hops or manifesto text.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

SPEC = "gate-production-skin-v1"
INVENTOR = "Nisaba LLC / Gate"

CANONICAL = (
    "Own permission on irreversible acts for any power that needs it — "
    "scarcity is the DENY, not the narrative."
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def their_production() -> bool:
    """True only when a real production weld is acknowledged."""
    flag = os.getenv("GATE_PRODUCTION_WELDED", "").strip().lower()
    if flag in ("1", "true", "yes", "on"):
        return True
    try:
        from gate import db as gate_db
    except ImportError:
        import db as gate_db  # type: ignore[no-redef]
    checker = getattr(gate_db, "has_gate_production_weld", None)
    if callable(checker):
        return bool(checker())
    return False


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    prod = their_production()
    return {
        "spec": SPEC,
        "name": "Production skin",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "canonical": CANONICAL,
        "their_production": prod,
        "shipped_now": [
            "POST /v1/act · POST /demo/hop",
            "CHARGE-only resurrection doctrine",
            "Register + operator weld checkout",
            "Action OS formula + family map",
            "Stranger verify via Velaru",
            "License fuse · restraint · settlement windows",
        ],
        "not_yet": [
            "Third-party production weld on their write",
            "Force/battlefield door (category only)",
            "Erra/Verra site voice rewrite (Gate-hosted doctrine only)",
        ],
        "force_production_weld": False,
        "links": {
            "scorecard": f"{base}/.well-known/scorecard.json",
            "action_os": f"{base}/.well-known/action-os.json",
            "register": f"{base}/register",
            "operator": f"{base}/operator",
        },
        "page": f"{base}/production-skin",
        "gatekeep": "Honesty skin. Ours.",
    }
