"""Monolith Interface — one shape, one function, no dashboard fauna.

Alien hardware often presents a single inscrutable face that does one
thing perfectly. Gate's public face is the exclusive door + CHARGE port.
Everything else is telemetry. Copycats grow fauna of settings until the
monolith is optional.

Gatekeep only to ourselves: monolith / 2001 interface → one welded face.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-monolith-v1"
INVENTOR = "Nisaba LLC / Gate"

FACES = ("exclusive_door", "charge_port")
FAUNA = (
    "permission_dashboard",
    "ai_governance_console",
    "soft_yes_inbox",
    "admin_live_panel",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def face(*, extra_faces: int | None = None, fauna: str | None = None) -> dict[str, Any]:
    extra = int(extra_faces) if extra_faces is not None else 0
    f = (fauna or "").strip().lower()
    if f in FAUNA or extra >= 3:
        posture = "fauna_overgrowth"
        claim = "monolith_dissolved_into_settings"
    elif extra == 0 and not f:
        posture = "monolith_intact"
        claim = "one_shape_one_function"
    else:
        posture = "stress"
        claim = "additional_face_pressure"
    return {
        "spec": SPEC,
        "name": "Monolith Interface",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Clarke/Kubrick monolith — one artifact, one encounter protocol",
            "Gate via negativa — subtract faces; keep door + CHARGE",
        ],
        "required_faces": list(FACES),
        "rejected_fauna": list(FAUNA),
        "extra_faces": extra,
        "fauna": f or None,
        "posture": posture,
        "claim": claim,
        "thesis": "The product is two ports. The rest is not the encounter.",
        "gatekeep": "Proprietary monolith-interface doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Monolith Interface",
        "inventor": INVENTOR,
        "example_intact": face(),
        "example_fauna": face(fauna="admin_live_panel"),
        "live": f"{base}/.well-known/monolith.json",
        "xenohardware": f"{base}/.well-known/xenohardware.json",
        "their_production": False,
    }
