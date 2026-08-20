"""NMI HALT — non-maskable interrupt: revenue cannot mask fail-closed.

On real silicon, NMI cannot be ignored by the running program. Gate's
HALT on timeout/5xx/missing parent is NMI: 'never block revenue' is not
an interrupt mask. Copycats make HALT maskable. That is not hardware.

Gatekeep only to ourselves: NMI → HALT that software slogans cannot mask.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

SPEC = "gate-nmi-halt-v1"
INVENTOR = "Nisaba LLC / Gate"

NMI_SOURCES = (
    "timeout",
    "http_5xx",
    "unreachable",
    "license_parent_dead",
    "epoch_locked",
    "exclusive_door_missing",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def interrupt(
    *,
    source: str | None = None,
    masked_by_revenue: bool | None = None,
    decision: str | None = None,
) -> dict[str, Any]:
    src = (source or "").strip().lower()
    masked = bool(masked_by_revenue)
    d = (decision or "").upper()
    is_nmi = src in NMI_SOURCES
    if is_nmi and masked and d == "ALLOW":
        posture = "nmi_masked_illegal"
        claim = "revenue_cannot_mask_fail_closed"
    elif is_nmi and d in ("HALT", "BLOCK"):
        posture = "nmi_taken"
        claim = "nonmaskable_halt_honored"
    elif is_nmi:
        posture = "nmi_pending"
        claim = "source_requires_halt"
    else:
        posture = "maskable_or_idle"
        claim = "no_nmi_source"
    return {
        "spec": SPEC,
        "name": "NMI HALT",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Non-maskable interrupt — hardware that software cannot ignore",
            "Gate fail-closed / vacuum integrity",
        ],
        "nmi_sources": list(NMI_SOURCES),
        "source": src or None,
        "masked_by_revenue": masked,
        "decision": d or None,
        "posture": posture,
        "claim": claim,
        "thesis": "If revenue can mask HALT, you shipped a toy PIC, not an NMI.",
        "gatekeep": "Proprietary NMI-HALT doctrine. Ours.",
        "their_production": False,
    }


def attach_to_receipt_payload(payload: Mapping[str, Any], row: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(payload)
    d = str(row.get("decision") or "").upper()
    src = "timeout" if d in ("HALT", "BLOCK") else None
    out["nmi_halt"] = interrupt(source=src, decision=d)
    return out


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "NMI HALT",
        "inventor": INVENTOR,
        "example_taken": interrupt(source="timeout", decision="HALT"),
        "example_masked": interrupt(source="timeout", masked_by_revenue=True, decision="ALLOW"),
        "live": f"{base}/.well-known/nmi-halt.json",
        "vacuum": f"{base}/.well-known/vacuum.json",
        "their_production": False,
    }
