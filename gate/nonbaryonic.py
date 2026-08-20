"""Non-Baryonic Skip-Clear — dashboards do not couple to it. The mouth is the detector.

Skip-clear is dark to Earth instruments: KPIs, greens, AI badges. It has
mass (irreversible spend happens) but almost no cross-section with
reporting light. The exclusive door is a weak-interaction detector. If
you only look at dashboards, you will swear nothing is wrong while the
halo binds.

Not Earth-side: not a 'blind spot' essay. A coupling law.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-nonbaryonic-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def couple(
    *,
    dashboard_only: bool | None = None,
    mouth_on_path: bool | None = None,
    spend_happened: bool | None = None,
) -> dict[str, Any]:
    dash = bool(dashboard_only)
    mouth = bool(mouth_on_path)
    spent = bool(spend_happened)
    if spent and dash and not mouth:
        posture = "dark_halo"
        claim = "spend_massive_dashboard_photon_blind"
    elif mouth:
        posture = "weak_detection"
        claim = "mouth_couples_to_skip_clear"
    else:
        posture = "no_halo_assay"
        claim = "insufficient_coupling_data"
    return {
        "spec": SPEC,
        "name": "Non-Baryonic Skip-Clear",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "dashboard_only": dash,
        "mouth_on_path": mouth,
        "spend_happened": spent,
        "posture": posture,
        "claim": claim,
        "thesis": "If light (dashboards) does not scatter off it, look with the mouth.",
        "gatekeep": "Proprietary non-baryonic skip-clear law. Ours.",
        "earth_side": False,
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Non-Baryonic Skip-Clear",
        "inventor": INVENTOR,
        "example_halo": couple(dashboard_only=True, spend_happened=True, mouth_on_path=False),
        "example_detect": couple(mouth_on_path=True),
        "live": f"{base}/.well-known/nonbaryonic.json",
        "posiwid": f"{base}/.well-known/posiwid.json",
        "their_production": False,
    }
