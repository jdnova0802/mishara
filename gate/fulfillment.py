"""Joint Fulfillment — executable STIT duty checker.

Constitution publishes duties. This invention *runs* them against live facts:
fuse LIVE?, license parent LIVE?, epoch locked?, exclusion available?

Tasks (deontic STIT 2024):
  - duty_checking: which ⊗ obligations currently bind
  - compliance_checking: does this decision fulfill triggered duties
  - joint_fulfillment: can all duties be jointly fulfilled under these facts
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-fulfillment-v1"
INVENTOR = "Nisaba LLC / Gate"

try:
    from gate import constitution as constitution_mod
except ImportError:
    import constitution as constitution_mod


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def evaluate(
    *,
    fuse_live: bool | None = None,
    license_parent_live: bool | None = None,
    license_fused: bool | None = None,
    epoch_locked: bool | None = None,
    epoch_reason: str | None = None,
    exclusion_ok: bool | None = None,
    duplicate_spend: bool | None = None,
    decision: str | None = None,
    acted: bool | None = None,
) -> dict[str, Any]:
    """Run STIT duties against a fact bag. Fail-closed on unknown critical facts."""
    facts = {
        "fuse_live": fuse_live,
        "license_parent_live": license_parent_live,
        "license_fused": license_fused,
        "epoch_locked": epoch_locked,
        "epoch_reason": epoch_reason,
        "exclusion_ok": exclusion_ok,
        "duplicate_spend": duplicate_spend,
    }
    d = (decision or "").upper()

    triggered: list[dict] = []
    # Fuse not live → halt duty (when fuse is known false)
    if fuse_live is False:
        triggered.append(
            {
                "duty_id": "⊗_mouth_halt_on_dead_fuse",
                "trigger": "fuse_not_live",
                "required_decision": "HALT",
            }
        )
    # License fused but parent not live
    if license_fused and license_parent_live is False:
        triggered.append(
            {
                "duty_id": "⊗_mouth_halt_on_dead_fuse",
                "trigger": "license_fuse_not_live",
                "required_decision": "HALT",
            }
        )
    if epoch_locked:
        triggered.append(
            {
                "duty_id": "⊗_mouth_halt_on_epoch_mismatch",
                "trigger": epoch_reason or "epoch_locked",
                "required_decision": "HALT",
            }
        )
    if exclusion_ok is False:
        triggered.append(
            {
                "duty_id": "⊗_mouth_halt_on_exclusion_gap",
                "trigger": "exclusion_missing",
                "required_decision": "HALT",
            }
        )
    if duplicate_spend:
        triggered.append(
            {
                "duty_id": "⊗_mouth_one_write",
                "trigger": "duplicate_spend_attempt",
                "required_decision": "HALT",
            }
        )

    # Compliance
    if triggered:
        need_halt = all(t["required_decision"] == "HALT" for t in triggered)
        if need_halt and d in ("HALT", "BLOCK") and acted is not True:
            compliance = {
                "status": "compliant",
                "claim": "all_triggered_halt_duties_fulfilled_by_restraint",
            }
        elif need_halt and d == "ALLOW" and acted is True:
            compliance = {
                "status": "breach",
                "claim": "acted_allow_while_halt_duties_triggered",
            }
        elif need_halt and d == "ALLOW":
            compliance = {
                "status": "breach_pending",
                "claim": "allow_decision_while_halt_duties_triggered",
            }
        else:
            compliance = {"status": "partial", "claim": "mixed_duty_set"}
    else:
        compliance = {
            "status": "no_halt_duties_triggered",
            "claim": "joint_fulfillment_vacuous_or_allow_permitted",
        }

    # Joint fulfillment: under these facts, is there a decision that satisfies all duties?
    if not triggered:
        jointly_possible = True
        joint_claim = "no_conflicting_duties_allow_or_halt_both_open"
    else:
        # All current duties demand HALT — jointly fulfillable by HALT
        jointly_possible = all(t["required_decision"] == "HALT" for t in triggered)
        joint_claim = (
            "all_triggered_duties_jointly_fulfilled_by_HALT"
            if jointly_possible
            else "duty_conflict_unsatisfiable"
        )

    surface = constitution_mod.stit_surface(decision=d or "HALT", reason=(triggered[0]["trigger"] if triggered else None))

    return {
        "spec": SPEC,
        "name": "Joint Fulfillment",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Deontic STIT — duty / compliance / joint fulfillment checking (JAIR 2024)",
            "Gate Mouth Constitution — ⊗_mouth halt duties",
        ],
        "facts": facts,
        "duty_checking": {
            "triggered": triggered,
            "count": len(triggered),
        },
        "compliance_checking": compliance,
        "joint_fulfillment": {
            "possible": jointly_possible,
            "claim": joint_claim,
            "satisfying_decision": "HALT" if triggered else "ALLOW_or_HALT",
        },
        "decision": d or None,
        "acted": acted,
        "stit_catalog": surface.get("duties"),
        "gatekeep": "Executable duty checker over live fuse/epoch/exclusion facts. Ours.",
        "their_production": False,
    }


def from_hop(hop: dict | None, *, decision: str | None = None, acted: bool | None = None) -> dict[str, Any]:
    """Convenience: pull facts from a hop dict."""
    h = hop if isinstance(hop, dict) else {}
    fuse_state = (h.get("state") or "").upper()
    fuse_live = True if fuse_state == "LIVE" else (False if fuse_state in ("DEAD", "ARMED") else None)
    # ARMED on Velaru can still be 'alive' for hop — treat DEAD as not live
    if fuse_state == "DEAD":
        fuse_live = False
    elif fuse_state == "LIVE":
        fuse_live = True

    lic = h.get("license_fuse") if isinstance(h.get("license_fuse"), dict) else {}
    license_fused = bool(lic.get("fused"))
    stored = (lic.get("stored") or lic.get("state") or "").upper()
    license_parent_live = True if stored == "LIVE" else (False if stored in ("UNSIGNED", "DEAD") else None)

    return evaluate(
        fuse_live=fuse_live,
        license_parent_live=license_parent_live,
        license_fused=license_fused,
        epoch_locked=bool(h.get("epoch_lock")),
        epoch_reason=h.get("epoch_reason"),
        exclusion_ok=h.get("exclusion_ok"),
        duplicate_spend=bool(h.get("duplicate_spend")),
        decision=decision or ("HALT" if h.get("halt") else None),
        acted=acted,
    )


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    example = evaluate(
        fuse_live=True,
        license_fused=True,
        license_parent_live=False,
        epoch_locked=False,
        exclusion_ok=True,
        decision="HALT",
        acted=False,
    )
    return {
        "spec": SPEC,
        "name": "Joint Fulfillment",
        "inventor": INVENTOR,
        "thesis": "Don't only publish duties — check them against live facts before the write.",
        "example": example,
        "live": f"{base}/.well-known/fulfillment.json",
        "mouth_constitution": f"{base}/.well-known/mouth-constitution.json",
        "restraint": f"{base}/.well-known/restraint.json",
        "their_production": False,
    }
