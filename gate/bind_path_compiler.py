"""Bind Path Compiler — actionable procedure graph, not thumbs up/down.

Invention (Action OS foothill): when the mouth is not OPEN, Gate returns the
remaining lawful steps, next actions, and repair packet — fail-closed still,
but the desk knows what to do next.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

try:
    from gate import throat as throat_mod
    from gate import desk_quorum_fob as quorum_mod
    from gate import charge_bride as charge_mod
    from gate import ghost_bind as ghost_mod
except ImportError:
    import throat as throat_mod
    import desk_quorum_fob as quorum_mod
    import charge_bride as charge_mod
    import ghost_bind as ghost_mod

SPEC = "gate-bind-path-compiler-v1"
INVENTION = "Bind Path Compiler"
FAMILY = "applicable_now"

STATE_READY = "READY"
STATE_BLOCKED = "BLOCKED"
STATE_CHOKE = "CHOKE"
STATE_CLOSED = "CLOSED"
STATE_HOLD = "HOLD"


def _base(public_url: str) -> str:
    return (public_url or "").rstrip("/")


def _step(
    *,
    step_id: str,
    label: str,
    status: str,
    detail: str,
    remaining: int | None = None,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "id": step_id,
        "label": label,
        "status": status,
        "detail": detail,
    }
    if remaining is not None:
        out["remaining"] = remaining
    return out


def _action(
    *,
    op: str,
    method: str,
    url: str,
    detail: str,
    body_hint: dict | None = None,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "op": op,
        "method": method,
        "url": url,
        "detail": detail,
    }
    if body_hint:
        out["body_hint"] = body_hint
    return out


def compile_plan(*, plan: dict, public_url: str = "", job_id: str | None = None) -> dict[str, Any]:
    """Compile remaining bind procedure from a finalized or demo plan."""
    base = _base(public_url)
    jid = (job_id or plan.get("job_id") or "").strip() or None
    throat = plan.get("throat") if isinstance(plan.get("throat"), dict) else {}
    quorum = plan.get("desk_quorum_fob") if isinstance(plan.get("desk_quorum_fob"), dict) else {}
    charge = plan.get("charge_bride") if isinstance(plan.get("charge_bride"), dict) else {}
    ghost = plan.get("ghost_bind") if isinstance(plan.get("ghost_bind"), dict) else {}
    license_fuse = plan.get("license_fuse") if isinstance(plan.get("license_fuse"), dict) else {}
    epoch = plan.get("epoch") if isinstance(plan.get("epoch"), dict) else {}
    passport = plan.get("agent_passport_weld") if isinstance(plan.get("agent_passport_weld"), dict) else {}
    twin = plan.get("twin_diode") if isinstance(plan.get("twin_diode"), dict) else {}
    panic = plan.get("panic_latch") if isinstance(plan.get("panic_latch"), dict) else {}
    watchman = plan.get("watchman_fuse") if isinstance(plan.get("watchman_fuse"), dict) else {}
    mercy = plan.get("pardon_sunset") if isinstance(plan.get("pardon_sunset"), dict) else {}
    indulgence = plan.get("indulgence_trap") if isinstance(plan.get("indulgence_trap"), dict) else {}
    mass_tag = plan.get("mass_tag") if isinstance(plan.get("mass_tag"), dict) else {}
    restraint = plan.get("restraint_invoice") if isinstance(plan.get("restraint_invoice"), dict) else {}

    allow = bool(plan.get("allow_bind") or plan.get("bind_allowed"))
    throat_state = throat.get("state") or ""
    reason = (plan.get("reason") or "").strip() or None
    steps: list[dict[str, Any]] = []
    next_actions: list[dict[str, Any]] = []
    blockers: list[str] = []
    repair: list[dict[str, Any]] = []
    do_not: list[str] = []

    # --- procedure steps (always present for sacred/heavy desks) ---
    mass_class = mass_tag.get("tag") or mass_tag.get("mass_class")
    quorum_required = quorum.get("verdict") != quorum_mod.VERDICT_NOT_REQUIRED
    if quorum_required:
        need = int(quorum.get("required_n") or 0)
        got = int(quorum.get("got_n") or 0)
        q_status = "done" if quorum.get("verdict") == quorum_mod.VERDICT_OK else "pending"
        steps.append(
            _step(
                step_id="desk_quorum",
                label="Desk quorum",
                status=q_status,
                detail=quorum.get("detail") or "Collect N-of-M UW approvals for high-mass bind.",
                remaining=max(0, need - got) if q_status == "pending" else 0,
            )
        )
        if q_status == "pending":
            blockers.append("desk_quorum_short")
            next_actions.append(
                _action(
                    op="collect_quorum",
                    method="POST",
                    url=f"{base}/demo/pas/desk-quorum-fob",
                    detail="Add UW approvals / fob tokens until quorum satisfied.",
                    body_hint={
                        "mass_class": mass_class,
                        "uw_approvals": need,
                        "charge_present": bool(quorum.get("charge_required")),
                        "job_id": jid,
                    },
                )
            )

    charge_needed = bool(quorum.get("charge_required")) or bool(epoch.get("locked"))
    charge_ok = bool(plan.get("charge_id") or plan.get("charge_present") or charge.get("charge_present"))
    if charge_needed or epoch.get("locked"):
        c_status = "done" if charge_ok and not epoch.get("locked") else "pending"
        steps.append(
            _step(
                step_id="charge_resurrect",
                label="CHARGE resurrection",
                status=c_status,
                detail=(
                    "Epoch locked or sacred mass — CHARGE-only re-open."
                    if epoch.get("locked") or charge_needed
                    else "CHARGE path available if fuse DEAD."
                ),
                remaining=0 if c_status == "done" else 1,
            )
        )
        if c_status == "pending":
            blockers.append("charge_required")
            next_actions.append(
                _action(
                    op="issue_charge",
                    method="POST",
                    url=f"{base}/v1/charge",
                    detail="CHARGE webhook / operator door — UW approve alone does not resurrect.",
                    body_hint={"job_id": jid, "fuse_id": plan.get("fuse_id")},
                )
            )
            do_not.append("treat_uw_approve_as_charge")

    hop_ok = bool(plan.get("verify_url") or (plan.get("hop_tattoo") or {}).get("verify_url"))
    steps.append(
        _step(
            step_id="pre_bind_hop",
            label="Pre-bind hop + verify",
            status="done" if hop_ok else "pending",
            detail="Stranger verify_url burned into hop before PAS write.",
            remaining=0 if hop_ok else 1,
        )
    )
    if not hop_ok:
        blockers.append("missing_verify_url")
        next_actions.append(
            _action(
                op="re_hop",
                method="POST",
                url=f"{base}/v1/pas/policycenter/pre-bind",
                detail="Re-run pre-bind hop; tattoo verify_url on job.",
                body_hint={"job_id": jid},
            )
        )

    # --- blockers from inventions ---
    if license_fuse.get("fused") and not license_fuse.get("ok"):
        blockers.append("license_fuse_dead")
        repair.append({"op": "renew_license", "detail": license_fuse.get("reason") or "license_not_live"})

    if throat_state == throat_mod.CHOKE:
        blockers.append("throat_choke")
        choke_reasons = throat.get("reasons") or []
        for r in choke_reasons:
            repair.append({"op": "resolve_throat", "reason": r})
        if "timeout_is_halt_not_live" in choke_reasons:
            do_not.append("treat_timeout_as_live")
            repair.append({"op": "re_hop", "detail": "Timeout is HALT — re-hop; never soft-allow."})
        if "soft_pas_without_mouth" in choke_reasons:
            repair.append({"op": "enable_mouth", "detail": "Install pre-bind hop — soft PAS without mouth is CHOKE."})

    if charge.get("verdict") == charge_mod.VERDICT_FORGED:
        blockers.append("forged_resurrection")
        do_not.extend(["boss_said_yes_without_quorum", "chat_yes_as_charge", "uw_approve_without_charge"])

    if ghost.get("verdict") in ("HAUNTED", "HAUNTED_CRITICAL"):
        blockers.append("ghost_bind")
        repair.append({"op": "ghost_bind_drill", "url": f"{base}/demo/pas/ghost-bind/drills"})

    if passport.get("verdict") in ("CHOKE", "FORGED", "EXPIRED"):
        blockers.append("agent_passport")
        next_actions.append(
            _action(
                op="mint_passport",
                method="POST",
                url=f"{base}/demo/pas/agent-passport-weld/mint",
                detail="Agent principal needs scoped passport weld before bind.",
                body_hint={"job_id": jid},
            )
        )

    if twin.get("verdict") == "BLOCK":
        blockers.append("twin_diode")
        repair.append({"op": "seal_twin", "detail": "Simulation twin cannot write reality — break seal with forge may."})

    if panic.get("verdict") in ("DENY", "ESCALATE"):
        blockers.append("panic_latch")
        repair.append({"op": "declare_incident", "detail": "Panic latch engaged — escalate before sacred commit."})

    if watchman.get("verdict") in ("DERELICT", "COWARD_CHOKE"):
        blockers.append("watchman_derelict")
        repair.append({"op": "duty_ping", "detail": "Duty SLA silence — watchman DERELICT; coward CHOKE."})

    if indulgence.get("verdict") == "TRIPPED":
        blockers.append("indulgence_trap")
        do_not.append("paid_or_relationship_mercy")

    if mercy.get("verdict") in ("FORGED_MERCY", "MERCY_EXPIRED"):
        blockers.append("mercy_invalid")
        repair.append({"op": "re_mercy", "detail": "Mercy must be scarred, co-signed, sunsetting."})

    cool_off_ends = plan.get("cool_off_ends_at")
    hold_active = False
    if cool_off_ends:
        try:
            end = datetime.fromisoformat(str(cool_off_ends).replace("Z", "+00:00"))
            if end.tzinfo is None:
                end = end.replace(tzinfo=timezone.utc)
            hold_active = datetime.now(timezone.utc) < end.astimezone(timezone.utc)
        except ValueError:
            hold_active = False
    if hold_active:
        blockers.append("cool_off_hold")
        steps.append(
            _step(
                step_id="cool_off",
                label="Cool-off hold",
                status="pending",
                detail=f"Sacred/heavy mass cooling until {cool_off_ends}.",
                remaining=1,
            )
        )

    # --- aggregate state ---
    if throat_state == throat_mod.OPEN and allow and not blockers:
        path_state = STATE_READY
        may_proceed = True
        summary = "Procedure complete — mouth OPEN under coordinator policy."
    elif throat_state == throat_mod.CLOSED and not allow:
        path_state = STATE_CLOSED
        may_proceed = False
        summary = "DENY proved — bind must not proceed; stranger can verify halt."
    elif hold_active:
        path_state = STATE_HOLD
        may_proceed = False
        summary = "HOLD — cool-off active; LIVE not yet eligible."
    elif throat_state == throat_mod.CHOKE or "throat_choke" in blockers:
        path_state = STATE_CHOKE
        may_proceed = False
        summary = "CHOKE — ambiguity cannot soft-allow; repair packet attached."
    else:
        path_state = STATE_BLOCKED
        may_proceed = False
        summary = "Blocked — remaining procedure steps before LIVE is eligible."

    pending_steps = [s for s in steps if s.get("status") == "pending"]
    restraint_eligible = bool(restraint.get("billable")) or (
        not allow and plan.get("decision") in ("HALT", "BLOCK") and plan.get("acted") is not True
    )

    if path_state in (STATE_CHOKE, STATE_BLOCKED, STATE_HOLD) and not repair:
        repair.append({"op": "review_blockers", "blockers": blockers, "reason": reason})

    if restraint_eligible:
        next_actions.append(
            _action(
                op="draft_restraint_invoice",
                method="GET",
                url=f"{base}/demo/pas/restraint-invoice",
                detail="Counterfactual SKU — prove what did not bind.",
                body_hint={"job_id": jid, "decision": plan.get("decision")},
            )
        )

    if blockers and path_state != STATE_READY:
        next_actions.append(
            _action(
                op="witness_verify",
                method="GET",
                url=plan.get("verify_url") or f"{base}/verify",
                detail="Stranger verification — share with examiner without IT ticket.",
            )
        )

    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "path_state": path_state,
        "may_proceed": may_proceed,
        "summary": summary,
        "job_id": jid,
        "throat_state": throat_state or None,
        "blockers": blockers,
        "reason": reason,
        "steps": steps,
        "pending_step_count": len(pending_steps),
        "next_actions": next_actions,
        "repair_packet": {
            "choke_reason": reason or (blockers[0] if blockers else None),
            "repair": repair,
            "do_not": do_not,
            "restraint_invoice_eligible": restraint_eligible,
        },
        "escalate_if_stuck_after": plan.get("escalate_after") or "4h",
        "rule": "Fail-closed still — procedure tells the desk what to do; it never soft-allows.",
        "pairs_with": "Throat · Desk Quorum Fob · Charge Bride · Restraint Invoice · Action OS",
    }


def attach(plan: dict, *, public_url: str = "", job_id: str | None = None) -> dict:
    plan["bind_path_compiler"] = compile_plan(
        plan=plan,
        public_url=public_url,
        job_id=job_id or plan.get("job_id"),
    )
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = _base(public_url)
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Actionable procedure graph — remaining steps + repair packet, not thumbs up/down.",
        "demo": f"POST {base}/demo/pas/bind-path-compiler",
        "well_known": f"{base}/.well-known/bind-path-compiler.json",
        "bind_room": f"{base}/bind-room",
        "manufactures": [
            "procedure_graph",
            "repair_packet",
            "next_action_urls",
            "restraint_path",
        ],
        "north_star": "gate/NORTH_STAR.md#inventions-forge-catalog",
        "posture": "Under coordinators. Action OS foothill — compile may, do not cosplay traffic lights.",
    }
