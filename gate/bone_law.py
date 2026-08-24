"""Bone Law — may that cannot be extracted from the write surface.

Forge / Mandate property (not another L2 throat widget):
  Sidecar may = forged.
  Extraction / bypass = amputation (surface dies) or EXTRACTION_ATTEMPTED.
  Act only exists inside the bonded cycle — outside = forgery.

Under coordinators. Unextractable ≠ unsackable. Never private Omega.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

SPEC = "gate-bone-law-v1"
INVENTION = "Bone Law"
FAMILY = "forge_mandate"
LAYER = "BONE_LAW"
POSTURE = (
    "May welded into the bones of the irreversible surface. "
    "Extract the mouth and the write dies. Outside the cycle: forgery, not an act. "
    "Under coordinators. Unextractable ≠ unsackable."
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def evaluate(
    *,
    mouth_in_bones: bool | None = None,
    sidecar_policy: bool | None = None,
    extraction_attempted: bool | None = None,
    bypass_path: bool | None = None,
    would_irreversible_write: bool | None = None,
    coordinator_bond_live: bool | None = None,
    surface_id: str | None = None,
) -> dict[str, Any]:
    """Judge whether may is unextractable on this surface."""
    bond_id = f"bone_{uuid4().hex[:12]}"
    base = {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "layer": LAYER,
        "bond_id": bond_id,
        "surface_id": surface_id,
        "attested_at": _now_iso(),
        "rule": (
            "Bone Law: may is property of the irreversible surface. "
            "Sidecar = forged. Extract = amputate. Outside cycle = no act."
        ),
        "posture": POSTURE,
    }

    # Sidecar dashboard / switch-off policy pretending to be a mouth
    if sidecar_policy and would_irreversible_write:
        return {
            **base,
            "verdict": "SIDECAR_FORGED",
            "may_proceed": False,
            "unextractable": False,
            "detail": "Sidecar policy on irreversible write — not Bone Law. Switch-off may is forged.",
        }

    # Rip / bypass / route-around while write still attempted
    if (extraction_attempted or bypass_path) and would_irreversible_write:
        if mouth_in_bones is False:
            return {
                **base,
                "verdict": "AMPUTATED",
                "may_proceed": False,
                "unextractable": True,
                "detail": "Mouth extracted/bypassed — irreversible surface amputated. Write impossible.",
                "cycle": "dead",
            }
        return {
            **base,
            "verdict": "EXTRACTION_ATTEMPTED",
            "may_proceed": False,
            "unextractable": True,
            "detail": "Extraction/bypass attempted against bonded mouth — HALT.",
            "cycle": "defended",
        }

    # Mouth gone, surface claimed live — ghost / amputated
    if mouth_in_bones is False and would_irreversible_write:
        return {
            **base,
            "verdict": "AMPUTATED",
            "may_proceed": False,
            "unextractable": True,
            "detail": "No mouth in bones — irreversible write surface dead.",
            "cycle": "dead",
        }

    # Bonded under coordinator
    if mouth_in_bones and coordinator_bond_live is not False:
        return {
            **base,
            "verdict": "BONDED",
            "may_proceed": True,
            "unextractable": True,
            "detail": "Mouth in the bones — write surface live only inside the may cycle.",
            "cycle": "live",
            "stranger_auditable": True,
        }

    # Explicit: act only counts inside cycle
    if would_irreversible_write and not mouth_in_bones:
        return {
            **base,
            "verdict": "CYCLE_ONLY",
            "may_proceed": False,
            "unextractable": True,
            "detail": "Outside bonded cycle the act does not exist — forgery.",
            "cycle": "outside",
        }

    return {
        **base,
        "verdict": "BONE_IDLE",
        "may_proceed": True,
        "unextractable": None,
        "detail": "No Bone Law event.",
        "cycle": "idle",
    }


def attach(plan: dict, *, public_url: str = "") -> dict:
    """Attach Bone Law when extraction/sidecar/bone signals are present."""
    base = (public_url or "").rstrip("/")
    triggers = (
        plan.get("bone_law_check")
        or plan.get("sidecar_policy")
        or plan.get("extraction_attempted")
        or plan.get("bypass_path")
        or plan.get("mouth_in_bones") is not None
        or plan.get("bone_surface_id")
    )
    if not triggers:
        return plan

    result = evaluate(
        mouth_in_bones=plan.get("mouth_in_bones"),
        sidecar_policy=plan.get("sidecar_policy"),
        extraction_attempted=plan.get("extraction_attempted"),
        bypass_path=plan.get("bypass_path") or plan.get("bypass"),
        would_irreversible_write=bool(
            plan.get("would_irreversible_write")
            or plan.get("allow_bind")
            or plan.get("acted")
            or plan.get("would_bind")
            or plan.get("would_mint_mouth")
        ),
        coordinator_bond_live=plan.get("coordinator_bond_live"),
        surface_id=plan.get("bone_surface_id") or plan.get("job_id") or plan.get("mouth_id"),
    )
    if base:
        result["well_known"] = f"{base}/.well-known/bone-law.json"
        result["doc"] = "gate/BONE_LAW.md"
    plan["bone_law"] = result

    if result.get("may_proceed") is False and result.get("verdict") not in ("BONE_IDLE",):
        plan["allow_bind"] = False
        if "bind_allowed" in plan:
            plan["bind_allowed"] = False
        plan["halt"] = True
        if not plan.get("decision") or plan.get("decision") in ("ALLOW", "LIVE"):
            plan["decision"] = "HALT"
        plan["reason"] = plan.get("reason") or f"bone_law:{result.get('verdict')}"
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "layer": LAYER,
        "one_liner": (
            "Bone Law — may in the bones; extract the mouth and the irreversible write dies. "
            "Outside the cycle: forgery."
        ),
        "verdicts": [
            "BONDED",
            "SIDECAR_FORGED",
            "EXTRACTION_ATTEMPTED",
            "AMPUTATED",
            "CYCLE_ONLY",
            "BONE_IDLE",
        ],
        "demo": f"POST {base}/demo/pas/bone-law",
        "well_known": f"{base}/.well-known/bone-law.json",
        "doc": "gate/BONE_LAW.md",
        "stack_doc": "gate/NISABA_STACK.md",
        "invisible_force": True,
        "not_outbound": True,
        "posture": POSTURE,
    }
