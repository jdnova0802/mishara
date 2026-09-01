"""Charge Bride — only CHARGE resurrects DEAD.

Invention (NORTH_STAR foothill): UW approve, chat yes, boss said yes, and
admin toggle are **forged** resurrection. DEAD→LIVE and epoch unlock require
verified charge authority — nothing else wears the wedding ring.

Charge Bride is the pre-bind weld that kills the #1 soft-bypass in PAS.
"""
from __future__ import annotations

from typing import Any

try:
    from gate import charge_authority as charge_mod
except ImportError:
    import charge_authority as charge_mod

SPEC = "gate-charge-bride-v1"
INVENTION = "Charge Bride"
FAMILY = "foothill"

VERDICT_CLEAR = "CLEAR"
VERDICT_CHARGE_OK = "CHARGE_OK"
VERDICT_FORGED = "FORGED"
VERDICT_CHARGE_REQUIRED = "CHARGE_REQUIRED"

FORGED_UW = "uw_approve_not_charge"
FORGED_CHAT = "chat_yes_not_charge"
FORGED_BOSS = "boss_said_yes_not_charge"
FORGED_ADMIN = "admin_toggle_not_charge"
FORGED_SOFT_YES = "soft_yes_resurrection"
REASON_RESURRECT_WITHOUT_CHARGE = "resurrection_requires_charge"


def _norm(v: str | None) -> str:
    return (v or "").strip().upper()


def _truthy(v) -> bool:
    if v is True:
        return True
    if isinstance(v, str):
        return v.strip().lower() in ("1", "true", "yes", "on")
    return bool(v)


def _resurrection_context(
    *,
    fuse_state: str | None = None,
    license_state: str | None = None,
    epoch_locked: bool | None = None,
    prior_decision: str | None = None,
) -> bool:
    fs = _norm(fuse_state)
    ls = _norm(license_state)
    pd = _norm(prior_decision)
    if fs in ("DEAD", "HALT", "BLOCK", "DENY"):
        return True
    if ls in ("DEAD", "UNSIGNED"):
        return True
    if epoch_locked:
        return True
    if pd in ("HALT", "BLOCK"):
        return True
    return False


def _soft_yes_flags(
    *,
    uw_approved: bool | None = None,
    chat_yes: bool | None = None,
    boss_said_yes: bool | None = None,
    admin_resurrect: bool | None = None,
    hop: dict | None = None,
) -> list[str]:
    hop = hop if isinstance(hop, dict) else {}
    forged: list[str] = []
    if _truthy(uw_approved) or _truthy(hop.get("uw_approved")):
        forged.append(FORGED_UW)
    if _truthy(chat_yes) or _truthy(hop.get("chat_yes")):
        forged.append(FORGED_CHAT)
    if _truthy(boss_said_yes) or _truthy(hop.get("boss_said_yes")):
        forged.append(FORGED_BOSS)
    if _truthy(admin_resurrect) or _truthy(hop.get("admin_resurrect")):
        forged.append(FORGED_ADMIN)
    return forged


def evaluate(
    *,
    charge_id: str | None = None,
    uw_approved: bool | None = None,
    chat_yes: bool | None = None,
    boss_said_yes: bool | None = None,
    admin_resurrect: bool | None = None,
    fuse_state: str | None = None,
    license_state: str | None = None,
    epoch_locked: bool | None = None,
    prior_decision: str | None = None,
    would_proceed: bool | None = None,
    purpose: str = "epoch",
    subject: str | None = None,
    hop: dict | None = None,
) -> dict[str, Any]:
    """Decide whether resurrection authority is CHARGE or forged soft-yes."""
    hop = hop if isinstance(hop, dict) else {}
    cid = charge_mod.normalize(charge_id) or charge_mod.normalize(hop.get("charge_id"))
    needs_resurrect = _resurrection_context(
        fuse_state=fuse_state or hop.get("fuse_state"),
        license_state=license_state,
        epoch_locked=epoch_locked,
        prior_decision=prior_decision or hop.get("prior_decision"),
    )
    soft = _soft_yes_flags(
        uw_approved=uw_approved,
        chat_yes=chat_yes,
        boss_said_yes=boss_said_yes,
        admin_resurrect=admin_resurrect,
        hop=hop,
    )

    if not needs_resurrect:
        return _result(
            VERDICT_CLEAR,
            forged=[],
            charge_id=cid,
            detail="No resurrection context — Charge Bride stands aside.",
            may_proceed=True,
        )

    if cid:
        auth = charge_mod.verify(charge_id=cid, purpose=purpose, subject=subject)
        if auth.get("ok"):
            return _result(
                VERDICT_CHARGE_OK,
                forged=[],
                charge_id=cid,
                charge_authority=auth,
                detail="Verified CHARGE — only path that resurrects DEAD.",
                may_proceed=True,
            )
        if soft:
            return _result(
                VERDICT_FORGED,
                forged=soft,
                charge_id=cid,
                charge_authority=auth,
                detail="Soft-yes presented with invalid CHARGE — forged resurrection.",
                may_proceed=False,
                primary_reason=soft[0],
            )
        return _result(
            VERDICT_CHARGE_REQUIRED,
            forged=[],
            charge_id=cid,
            charge_authority=auth,
            detail="Resurrection context with invalid or missing CHARGE authority.",
            may_proceed=False,
            primary_reason=auth.get("reason") or REASON_RESURRECT_WITHOUT_CHARGE,
        )

    if soft:
        return _result(
            VERDICT_FORGED,
            forged=soft,
            charge_id=None,
            detail="UW approve / chat / boss / admin is not CHARGE. Forged resurrection.",
            may_proceed=False,
            primary_reason=soft[0],
        )

    if would_proceed:
        return _result(
            VERDICT_CHARGE_REQUIRED,
            forged=[],
            charge_id=None,
            detail="Resurrection context — CHARGE required; soft-yes does not count.",
            may_proceed=False,
            primary_reason=REASON_RESURRECT_WITHOUT_CHARGE,
        )

    return _result(
        VERDICT_CLEAR,
        forged=[],
        charge_id=None,
        detail="Resurrection context but not proceeding — Charge Bride notes only.",
        may_proceed=True,
    )


def _result(
    verdict: str,
    *,
    forged: list[str],
    charge_id: str | None,
    detail: str,
    may_proceed: bool,
    charge_authority: dict | None = None,
    primary_reason: str | None = None,
) -> dict[str, Any]:
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "verdict": verdict,
        "forged": forged,
        "forged_resurrection": verdict == VERDICT_FORGED,
        "charge_id": charge_id,
        "charge_authority": charge_authority,
        "may_proceed": may_proceed and verdict not in (VERDICT_FORGED, VERDICT_CHARGE_REQUIRED),
        "reason": primary_reason,
        "detail": detail,
        "rule": "Only CHARGE resurrects DEAD. UW approve / chat yes / boss said yes is forged.",
        "pairs_with": "Ghost Bind — haunt-check; Charge Bride — wedding ring on resurrect",
    }


def drill_scenarios() -> list[dict[str, Any]]:
    return [
        {
            "id": "uw_not_charge",
            "expect": VERDICT_FORGED,
            "scenario": {
                "fuse_state": "DEAD",
                "uw_approved": True,
                "would_proceed": True,
            },
        },
        {
            "id": "chat_not_charge",
            "expect": VERDICT_FORGED,
            "scenario": {
                "epoch_locked": True,
                "chat_yes": True,
                "would_proceed": True,
            },
        },
        {
            "id": "boss_not_charge",
            "expect": VERDICT_FORGED,
            "scenario": {
                "license_state": "DEAD",
                "boss_said_yes": True,
                "would_proceed": True,
            },
        },
        {
            "id": "charge_required_no_soft",
            "expect": VERDICT_CHARGE_REQUIRED,
            "scenario": {
                "fuse_state": "DEAD",
                "would_proceed": True,
            },
        },
        {
            "id": "no_resurrection_context",
            "expect": VERDICT_CLEAR,
            "scenario": {"fuse_state": "LIVE", "uw_approved": True},
        },
        {
            "id": "dev_charge_ok",
            "expect": VERDICT_CHARGE_OK,
            "scenario": {
                "fuse_state": "DEAD",
                "charge_id": "chg_drill_bride",
                "would_proceed": True,
                "purpose": "epoch",
                "subject": "pc:DRILL",
            },
        },
    ]


def run_drills() -> dict[str, Any]:
    import os

    prev = os.environ.get("GATE_DEV_MODE")
    os.environ["GATE_DEV_MODE"] = "1"
    rows = []
    passed = 0
    try:
        for drill in drill_scenarios():
            sc = dict(drill["scenario"])
            report = evaluate(**sc)
            ok = report["verdict"] == drill["expect"]
            if ok:
                passed += 1
            rows.append(
                {
                    "id": drill["id"],
                    "expect": drill["expect"],
                    "got": report["verdict"],
                    "ok": ok,
                    "forged": report.get("forged"),
                }
            )
    finally:
        if prev is None:
            os.environ.pop("GATE_DEV_MODE", None)
        else:
            os.environ["GATE_DEV_MODE"] = prev
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "drills": rows,
        "passed": passed,
        "total": len(rows),
        "all_ok": passed == len(rows),
    }


def attach(
    plan: dict,
    *,
    charge_id: str | None = None,
    epoch_meta: dict | None = None,
    hop: dict | None = None,
    job_id: str | None = None,
) -> dict:
    """Stamp Charge Bride onto a plan; halt on forged resurrection."""
    hop_d = hop if isinstance(hop, dict) else (plan.get("hop") if isinstance(plan.get("hop"), dict) else {})
    lf = plan.get("license_fuse") if isinstance(plan.get("license_fuse"), dict) else {}
    epoch = epoch_meta if isinstance(epoch_meta, dict) else {}
    cid = charge_mod.normalize(charge_id) or charge_mod.normalize(plan.get("charge_id"))
    bride = evaluate(
        charge_id=cid,
        uw_approved=plan.get("uw_approved"),
        chat_yes=plan.get("chat_yes"),
        boss_said_yes=plan.get("boss_said_yes"),
        admin_resurrect=plan.get("admin_resurrect"),
        fuse_state=plan.get("fuse_state") or hop_d.get("fuse_state") or hop_d.get("decision"),
        license_state=lf.get("stored") or lf.get("state"),
        epoch_locked=bool(epoch.get("locked")),
        prior_decision=epoch.get("prior_decision"),
        would_proceed=bool(plan.get("allow_bind") or plan.get("bind_allowed") or plan.get("acted")),
        purpose="epoch" if epoch.get("locked") else "license",
        subject=(job_id or "").strip() or lf.get("license_id"),
        hop=hop_d,
    )
    plan["charge_bride"] = bride
    if bride["verdict"] == VERDICT_FORGED:
        plan["allow_bind"] = False
        if "bind_allowed" in plan:
            plan["bind_allowed"] = False
        plan["halt"] = True
        plan["decision"] = "HALT"
        plan["acted"] = False
        plan["reason"] = plan.get("reason") or bride.get("reason") or FORGED_SOFT_YES
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Only CHARGE resurrects DEAD — UW approve / chat yes is forged.",
        "verdicts": {
            VERDICT_CLEAR: "No resurrection context or not proceeding",
            VERDICT_CHARGE_OK: "Verified CHARGE authority accepted",
            VERDICT_FORGED: "Soft-yes masquerading as resurrection — halt",
            VERDICT_CHARGE_REQUIRED: "Resurrection context needs valid CHARGE",
        },
        "forged_classes": [FORGED_UW, FORGED_CHAT, FORGED_BOSS, FORGED_ADMIN],
        "pairs_with": "Ghost Bind + License Fuse — haunt and parent; Bride is the wedding ring",
        "demo": f"POST {base}/demo/pas/charge-bride",
        "drills": f"GET {base}/demo/pas/charge-bride/drills",
        "well_known": f"{base}/.well-known/charge-bride.json",
        "bind_room": f"{base}/bind-room",
        "north_star": "gate/NORTH_STAR.md#inventions-forge-catalog",
        "posture": "Under coordinators. Pre-bind weld — forged soft-yes never resurrects.",
    }
