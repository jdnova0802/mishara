"""ISO Surface — well-known JSON as the ISO-20022 instinct without pretending to be SWIFT.

DTCC's 2026–2027 migration wants machine-readable, harmonised instruction
surfaces. Gate already publishes structured manifests at /.well-known/* —
same interoperability move as ISO 20022, different layer: pre-settlement
mouth semantics, not payment message replacement.

Not cliche 'we are ISO certified'. Same architectural instinct, our layer.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-iso-surface-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def surface(*, pdf_only: bool | None = None, well_known_fetchable: bool | None = None) -> dict[str, Any]:
    pdf = bool(pdf_only)
    wk = bool(well_known_fetchable)
    if pdf and not wk:
        posture = "human_only"
        claim = "not_interoperable_with_modern_post_trade"
    elif wk:
        posture = "iso_instinct"
        claim = "machine_readable_manifest_layer"
    else:
        posture = "unevaluated"
        claim = "no_surface"
    return {
        "spec": SPEC,
        "name": "ISO Surface",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "ISO 20022 migration · DTCC distributed platform — harmonised data elements",
            "Gate .well-known manifests — structured public instruction surfaces",
        ],
        "pdf_only": pdf,
        "well_known_fetchable": wk,
        "posture": posture,
        "claim": claim,
        "thesis": "Your CSD migrates messages. We migrate permission semantics to fetch.",
        "gatekeep": "Proprietary ISO-surface doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "ISO Surface",
        "inventor": INVENTOR,
        "example_ok": surface(well_known_fetchable=True),
        "example_bad": surface(pdf_only=True),
        "live": f"{base}/.well-known/iso-surface.json",
        "gate_json": f"{base}/.well-known/gate.json",
        "their_production": False,
    }
