"""Mandate Layer (L3) — stack above may, ahead of time.

Nisaba Stack:
  L0 Can (not ours) → L1 Sight (not ours) → L2 May (Gate) → L3 Mandate (this)

Pillars:
  1. Meta-Sheath License — who may mint/ship mouths
  2. Restraint Clearing — ρ settles as clearing mass
  3. Principal Continuity — may handoff / death kills hooks
  4. Mouth Registry — attested mouth directory

Under coordinators. Meta-may is de-licensable. Never private Omega.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

SPEC_PACK = "gate-mandate-layer-v1"
INVENTION = "Mandate Layer"
FAMILY = "stack_l3"
LAYER = "L3_MANDATE"
POSTURE = (
    "Under coordinators. L3 Mandate sits above L2 May — "
    "licenses mouths, clears restraint mass, holds principal continuity. "
    "Never private Omega. Nisaba's own mandate is revocable under flag."
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def meta_sheath_license_evaluate(
    *,
    issuer_id: str | None = None,
    licensee_id: str | None = None,
    license_live: bool | None = None,
    expired: bool | None = None,
    revoked: bool | None = None,
    coordinator_attested: bool | None = None,
    would_mint_mouth: bool | None = None,
) -> dict[str, Any]:
    """Who may manufacture / mint mouths — forge-of-forges gate."""
    if would_mint_mouth and (revoked or expired or license_live is False):
        return {
            "spec": "gate-meta-sheath-license-v1",
            "invention": "Meta-Sheath License",
            "pillar": "meta_sheath",
            "verdict": "LICENSE_DENY",
            "may_proceed": False,
            "issuer_id": issuer_id,
            "licensee_id": licensee_id,
            "detail": "Mouth-mint blocked — license dead/expired/revoked.",
            "rule": "Only attested, live meta-sheath licensees may mint mouths. Capture ⇒ revoke under coordinator.",
        }
    if would_mint_mouth and not coordinator_attested:
        return {
            "spec": "gate-meta-sheath-license-v1",
            "invention": "Meta-Sheath License",
            "pillar": "meta_sheath",
            "verdict": "LICENSE_CHOKE",
            "may_proceed": False,
            "detail": "Mint without coordinator attestation — CHOKE.",
            "rule": "Only attested, live meta-sheath licensees may mint mouths. Capture ⇒ revoke under coordinator.",
        }
    if would_mint_mouth and license_live and coordinator_attested:
        return {
            "spec": "gate-meta-sheath-license-v1",
            "invention": "Meta-Sheath License",
            "pillar": "meta_sheath",
            "verdict": "LICENSE_LIVE",
            "may_proceed": True,
            "issuer_id": issuer_id,
            "licensee_id": licensee_id,
            "detail": "Meta-sheath license LIVE — mouth mint permitted under flag.",
            "rule": "Only attested, live meta-sheath licensees may mint mouths. Capture ⇒ revoke under coordinator.",
        }
    return {
        "spec": "gate-meta-sheath-license-v1",
        "invention": "Meta-Sheath License",
        "pillar": "meta_sheath",
        "verdict": "LICENSE_IDLE",
        "may_proceed": True,
        "detail": "No mint attempted.",
        "rule": "Only attested, live meta-sheath licensees may mint mouths. Capture ⇒ revoke under coordinator.",
    }


def restraint_clearing_evaluate(
    *,
    rho_mass: float | int | None = None,
    window_id: str | None = None,
    desk_id: str | None = None,
    counterparty_desk: str | None = None,
    settle: bool | None = None,
) -> dict[str, Any]:
    """ρ as clearing mass — non-fire settles across desks/windows."""
    mass = float(rho_mass or 0)
    if settle and mass <= 0:
        return {
            "spec": "gate-restraint-clearing-v1",
            "invention": "Restraint Clearing",
            "pillar": "restraint_clearing",
            "verdict": "CLEARING_EMPTY",
            "may_proceed": False,
            "rho_mass": mass,
            "detail": "Cannot settle — no ρ mass in window.",
            "rule": "Restraint clearing turns ρ into settlement mass across desks — Bloomberg-seed of non-fire.",
        }
    if settle and mass > 0:
        clearing_id = f"clr_{uuid4().hex[:12]}"
        return {
            "spec": "gate-restraint-clearing-v1",
            "invention": "Restraint Clearing",
            "pillar": "restraint_clearing",
            "verdict": "CLEARING_SETTLED",
            "may_proceed": True,
            "clearing_id": clearing_id,
            "rho_mass": mass,
            "window_id": window_id,
            "desk_id": desk_id,
            "counterparty_desk": counterparty_desk,
            "settled_at": _now_iso(),
            "detail": f"Cleared {mass} ρ mass — restraint settled.",
            "rule": "Restraint clearing turns ρ into settlement mass across desks — Bloomberg-seed of non-fire.",
        }
    return {
        "spec": "gate-restraint-clearing-v1",
        "invention": "Restraint Clearing",
        "pillar": "restraint_clearing",
        "verdict": "CLEARING_IDLE",
        "may_proceed": True,
        "rho_mass": mass,
        "detail": "No settlement requested.",
        "rule": "Restraint clearing turns ρ into settlement mass across desks — Bloomberg-seed of non-fire.",
    }


def principal_continuity_evaluate(
    *,
    handoff: bool | None = None,
    stranger_attested: bool | None = None,
    principal_dead: bool | None = None,
    substrate_swap: bool | None = None,
    may_hooks_live: bool | None = None,
    from_principal: str | None = None,
    to_principal: str | None = None,
) -> dict[str, Any]:
    """May survives substrate/death only with stranger-attested handoff; else hooks die."""
    if principal_dead and may_hooks_live:
        return {
            "spec": "gate-principal-continuity-v1",
            "invention": "Principal Continuity",
            "pillar": "principal_continuity",
            "verdict": "GHOST_MAY",
            "may_proceed": False,
            "detail": "Principal dead but may-hooks live — ghost may (Filter). Funeral required.",
            "rule": "May does not silently survive death or substrate swap. Stranger handoff or hooks die.",
        }
    if (handoff or substrate_swap) and not stranger_attested:
        return {
            "spec": "gate-principal-continuity-v1",
            "invention": "Principal Continuity",
            "pillar": "principal_continuity",
            "verdict": "HANDOFF_FORGED",
            "may_proceed": False,
            "from_principal": from_principal,
            "to_principal": to_principal,
            "detail": "Handoff/substrate swap without stranger attest — forged continuity.",
            "rule": "May does not silently survive death or substrate swap. Stranger handoff or hooks die.",
        }
    if handoff and stranger_attested:
        cont_id = f"cont_{uuid4().hex[:12]}"
        return {
            "spec": "gate-principal-continuity-v1",
            "invention": "Principal Continuity",
            "pillar": "principal_continuity",
            "verdict": "CONTINUITY_LIVE",
            "may_proceed": True,
            "continuity_id": cont_id,
            "from_principal": from_principal,
            "to_principal": to_principal,
            "detail": "Stranger-attested continuity — may may move.",
            "rule": "May does not silently survive death or substrate swap. Stranger handoff or hooks die.",
        }
    if principal_dead and not may_hooks_live:
        return {
            "spec": "gate-principal-continuity-v1",
            "invention": "Principal Continuity",
            "pillar": "principal_continuity",
            "verdict": "MAY_BURIED",
            "may_proceed": False,
            "detail": "Principal dead; may-hooks buried — continuity closed.",
            "rule": "May does not silently survive death or substrate swap. Stranger handoff or hooks die.",
        }
    return {
        "spec": "gate-principal-continuity-v1",
        "invention": "Principal Continuity",
        "pillar": "principal_continuity",
        "verdict": "CONTINUITY_IDLE",
        "may_proceed": True,
        "detail": "No continuity event.",
        "rule": "May does not silently survive death or substrate swap. Stranger handoff or hooks die.",
    }


def mouth_registry_stamp(
    *,
    mouth_id: str | None = None,
    semver: str | None = None,
    meta_license_id: str | None = None,
    funeral_state: str | None = None,
    program_id: str | None = None,
) -> dict[str, Any]:
    """Attested directory entry for a mouth — registry nerve of Mandate."""
    reg_id = f"reg_{uuid4().hex[:12]}"
    state = (funeral_state or "live").strip().lower()
    return {
        "spec": "gate-mouth-registry-v1",
        "invention": "Mouth Registry",
        "pillar": "mouth_registry",
        "verdict": "REGISTERED",
        "registry_id": reg_id,
        "mouth_id": mouth_id or reg_id,
        "semver": semver or "gate-mouth-v1",
        "meta_license_id": meta_license_id,
        "funeral_state": state,
        "program_id": program_id,
        "attested_at": _now_iso(),
        "stranger_auditable": True,
        "detail": "Mouth registered under Mandate — stranger-auditable directory.",
        "rule": "Every production mouth earns a registry row. Ghost/unregistered mouths are antimay-adjacent.",
    }


PILLARS = (
    ("meta_sheath_license", "Meta-Sheath License", "gate-meta-sheath-license-v1"),
    ("restraint_clearing", "Restraint Clearing", "gate-restraint-clearing-v1"),
    ("principal_continuity", "Principal Continuity", "gate-principal-continuity-v1"),
    ("mouth_registry", "Mouth Registry", "gate-mouth-registry-v1"),
)


def evaluate(name: str, **kwargs: Any) -> dict[str, Any]:
    n = (name or "").strip().lower().replace("-", "_")
    table = {
        "meta_sheath_license": meta_sheath_license_evaluate,
        "meta_sheath": meta_sheath_license_evaluate,
        "restraint_clearing": restraint_clearing_evaluate,
        "principal_continuity": principal_continuity_evaluate,
        "mouth_registry": lambda **k: mouth_registry_stamp(**k),
    }
    fn = table.get(n)
    if not fn:
        return {"error": "unknown_pillar", "known": [p[0] for p in PILLARS]}
    return fn(**kwargs)


def attach(plan: dict, *, public_url: str = "") -> dict:
    base = (public_url or "").rstrip("/")
    layer: dict[str, Any] = {
        "spec": SPEC_PACK,
        "invention": INVENTION,
        "layer": LAYER,
        "family": FAMILY,
        "pillars": {},
        "stack_doc": "gate/NISABA_STACK.md",
    }

    if plan.get("would_mint_mouth") or plan.get("meta_license_check"):
        layer["pillars"]["meta_sheath_license"] = meta_sheath_license_evaluate(
            issuer_id=plan.get("meta_issuer_id"),
            licensee_id=plan.get("meta_licensee_id"),
            license_live=plan.get("meta_license_live"),
            expired=plan.get("meta_license_expired"),
            revoked=plan.get("meta_license_revoked"),
            coordinator_attested=plan.get("meta_coordinator_attested"),
            would_mint_mouth=plan.get("would_mint_mouth", True),
        )

    ru = plan.get("restraint_unit") if isinstance(plan.get("restraint_unit"), dict) else {}
    if plan.get("settle_restraint") or plan.get("clear_rho"):
        layer["pillars"]["restraint_clearing"] = restraint_clearing_evaluate(
            rho_mass=plan.get("rho_mass") or ru.get("rho_mass") or ru.get("rho_mass_total"),
            window_id=plan.get("may_window_id") or plan.get("clearing_window_id"),
            desk_id=plan.get("desk_id"),
            counterparty_desk=plan.get("counterparty_desk"),
            settle=True,
        )

    if (
        plan.get("principal_dead")
        or plan.get("may_handoff")
        or plan.get("substrate_swap")
        or plan.get("continuity_check")
    ):
        layer["pillars"]["principal_continuity"] = principal_continuity_evaluate(
            handoff=plan.get("may_handoff") or plan.get("handoff"),
            stranger_attested=plan.get("stranger_attested"),
            principal_dead=plan.get("principal_dead"),
            substrate_swap=plan.get("substrate_swap"),
            may_hooks_live=plan.get("may_hooks_live"),
            from_principal=plan.get("from_principal"),
            to_principal=plan.get("to_principal"),
        )

    # Always stamp registry nerve when event/mouth present
    if plan.get("event_id") or plan.get("register_mouth") or plan.get("mouth_id"):
        layer["pillars"]["mouth_registry"] = mouth_registry_stamp(
            mouth_id=plan.get("mouth_id"),
            semver=(plan.get("throat") or {}).get("spec")
            if isinstance(plan.get("throat"), dict)
            else plan.get("mouth_semver"),
            meta_license_id=plan.get("meta_license_id"),
            funeral_state=plan.get("funeral_state"),
            program_id=plan.get("program_id"),
        )

    blockers = []
    for key, inv in layer["pillars"].items():
        if inv.get("may_proceed") is False and inv.get("verdict") not in (
            "LICENSE_IDLE",
            "CLEARING_IDLE",
            "CONTINUITY_IDLE",
            "MAY_BURIED",
        ):
            blockers.append(key)
    layer["blockers"] = blockers
    layer["pillar_count"] = len(PILLARS)
    layer["active_count"] = len(layer["pillars"])
    if base:
        layer["well_known"] = f"{base}/.well-known/mandate-layer.json"
        layer["stack"] = f"{base}/.well-known/nisaba-stack.json"
    plan["mandate_layer"] = layer

    for key in blockers:
        if plan.get("allow_bind") or plan.get("acted") or plan.get("would_mint_mouth"):
            plan["allow_bind"] = False
            if "bind_allowed" in plan:
                plan["bind_allowed"] = False
            plan["halt"] = True
            if not plan.get("decision") or plan.get("decision") in ("ALLOW", "LIVE"):
                plan["decision"] = "HALT"
            plan["reason"] = plan.get("reason") or f"mandate_layer:{key}"
            break
    return plan


def stack_manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": "nisaba-stack-v1",
        "doc": "gate/NISABA_STACK.md",
        "one_liner": "L0 can · L1 sight · L2 Gate may · L3 Mandate — stack the floor above the mouth ahead of time.",
        "layers": {
            "L0_can": {"ours": False, "verb": "act/carry/hit"},
            "L1_sight": {"ours": False, "verb": "see/fuse/suggest"},
            "L2_may": {"ours": True, "product": "Gate", "verb": "clear/sheath/prove"},
            "L3_mandate": {
                "ours": True,
                "product": "Mandate Layer",
                "verb": "mint mouths / clear ρ / hold principals",
                "well_known": f"{base}/.well-known/mandate-layer.json",
            },
        },
        "posture": POSTURE,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC_PACK,
        "invention": INVENTION,
        "layer": LAYER,
        "family": FAMILY,
        "one_liner": "L3 Mandate — meta-sheath license, restraint clearing, principal continuity, mouth registry.",
        "pillars": [
            {
                "slug": slug,
                "invention": title,
                "spec": spec,
                "well_known": f"{base}/.well-known/{slug.replace('_', '-')}.json",
            }
            for slug, title, spec in PILLARS
        ],
        "demo": f"POST {base}/demo/pas/mandate-layer",
        "well_known": f"{base}/.well-known/mandate-layer.json",
        "stack": f"{base}/.well-known/nisaba-stack.json",
        "doc": "gate/NISABA_STACK.md",
        "ahead_of_time": True,
        "posture": POSTURE,
    }
