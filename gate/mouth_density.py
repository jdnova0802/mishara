"""Mouth Density Pack — maximize mouth thesis as demoable foothill seeds.

Eight mountain→foothill inventions that thicken the mouth without new media:

  1. Stale LIVE Rejector   — old clearance is forged
  2. Cool-Off Shim         — sacred/heavy mass must HOLD(τ) before LIVE eligible
  3. Silence Gate          — loss of contact ⇒ DENY (anti-Perimeter, software)
  4. Algedonic Relay       — local hold timeout ⇒ signed escalate packet
  5. May Budget            — N sacred LIVEs per window; exhaust ⇒ DENY
  6. Funeral Bit           — decommission may-hooks; prove mouth dead
  7. Bind Genealogy        — serial lineage of which throat shipped on which job
  8. Cold Weld             — genesis receipt before first production irreversible

Same physics: may · sheath · prove. Under coordinators. Never sovereign.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

SPEC_PACK = "gate-mouth-density-v1"
FAMILY = "applicable_now"
POSTURE = "Under coordinators. Mouth densifiers — fail-closed, stranger-provable."

# --- shared ---

def _now(ts: str | None = None) -> datetime:
    if ts:
        t = ts.strip().replace("Z", "+00:00")
        dt = datetime.fromisoformat(t)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


# =============================================================================
# 1. Stale LIVE Rejector
# =============================================================================

STALE_SPEC = "gate-stale-live-v1"
STALE_INVENTION = "Stale LIVE Rejector"


def stale_live_evaluate(
    *,
    live_issued_at: str | None = None,
    stale_after_seconds: int = 300,
    now: str | None = None,
    decision: str | None = None,
    would_act: bool | None = None,
) -> dict[str, Any]:
    """Reject LIVE that aged past τ — stale clearance is forged."""
    d = (decision or "").strip().upper()
    issued = None
    age = None
    stale = False
    if live_issued_at:
        try:
            issued_dt = _now(live_issued_at)
            now_dt = _now(now)
            age = max(0, int((now_dt - issued_dt).total_seconds()))
            stale = age > max(1, int(stale_after_seconds))
        except ValueError:
            stale = True
            age = None
    # Only bite when someone treats a LIVE as still good
    attempting_live = d in ("ALLOW", "LIVE", "GO") or would_act is True
    forged = bool(stale and attempting_live and live_issued_at)
    return {
        "spec": STALE_SPEC,
        "invention": STALE_INVENTION,
        "family": FAMILY,
        "verdict": "STALE_FORGED" if forged else ("STALE" if stale else "FRESH"),
        "forged": forged,
        "stale": stale,
        "age_seconds": age,
        "stale_after_seconds": int(stale_after_seconds),
        "live_issued_at": live_issued_at,
        "may_proceed": not forged,
        "detail": (
            "Stale LIVE worn as fresh — forged. Re-clear."
            if forged
            else ("Clearance aged out — re-LIVE required before act." if stale else "Clearance within freshness window.")
        ),
        "rule": "LIVE has half-life. Age > τ ⇒ forged if used.",
    }


# =============================================================================
# 2. Cool-Off Shim
# =============================================================================

COOL_SPEC = "gate-cool-off-v1"
COOL_INVENTION = "Cool-Off Shim"


def cool_off_evaluate(
    *,
    mass_class: str | None = None,
    cool_off_seconds: int | None = None,
    cool_started_at: str | None = None,
    now: str | None = None,
    skip_attempt: bool | None = None,
) -> dict[str, Any]:
    """Sacred/heavy mass must HOLD(τ) before LIVE is eligible."""
    mc = (mass_class or "light").strip().lower()
    if cool_off_seconds is None:
        cool_off_seconds = {"sacred": 3600, "heavy": 900, "light": 0}.get(mc, 0)
    tau = max(0, int(cool_off_seconds))
    if tau <= 0 or mc == "light":
        return {
            "spec": COOL_SPEC,
            "invention": COOL_INVENTION,
            "family": FAMILY,
            "verdict": "COOL_NOT_REQUIRED",
            "hold_active": False,
            "may_proceed": True,
            "remaining_seconds": 0,
            "mass_class": mc,
            "detail": "Light mass — cool-off not required.",
            "rule": "Heavy/sacred mass earns HOLD(τ) before LIVE eligible. Speed aristocracy is forged.",
        }
    if skip_attempt:
        return {
            "spec": COOL_SPEC,
            "invention": COOL_INVENTION,
            "family": FAMILY,
            "verdict": "COOL_SKIP_FORGED",
            "hold_active": True,
            "may_proceed": False,
            "remaining_seconds": tau,
            "mass_class": mc,
            "detail": "Cool-off skip attempt — forged speed aristocracy.",
            "rule": "Heavy/sacred mass earns HOLD(τ) before LIVE eligible. Speed aristocracy is forged.",
        }
    if not cool_started_at:
        return {
            "spec": COOL_SPEC,
            "invention": COOL_INVENTION,
            "family": FAMILY,
            "verdict": "COOL_HOLD",
            "hold_active": True,
            "may_proceed": False,
            "remaining_seconds": tau,
            "cool_ends_at": _iso(_now() + timedelta(seconds=tau)),
            "mass_class": mc,
            "detail": f"Cool-off HOLD({tau}s) — LIVE not yet eligible.",
            "rule": "Heavy/sacred mass earns HOLD(τ) before LIVE eligible. Speed aristocracy is forged.",
        }
    try:
        start = _now(cool_started_at)
        now_dt = _now(now)
        elapsed = max(0, int((now_dt - start).total_seconds()))
        remaining = max(0, tau - elapsed)
        active = remaining > 0
    except ValueError:
        active, remaining = True, tau
    return {
        "spec": COOL_SPEC,
        "invention": COOL_INVENTION,
        "family": FAMILY,
        "verdict": "COOL_HOLD" if active else "COOL_CLEAR",
        "hold_active": active,
        "may_proceed": not active,
        "remaining_seconds": remaining,
        "cool_off_seconds": tau,
        "mass_class": mc,
        "detail": (
            f"Cool-off active — {remaining}s remaining."
            if active
            else "Cool-off elapsed — LIVE eligible under other mouths."
        ),
        "rule": "Heavy/sacred mass earns HOLD(τ) before LIVE eligible. Speed aristocracy is forged.",
    }


# =============================================================================
# 3. Silence Gate (software)
# =============================================================================

SILENCE_SPEC = "gate-silence-gate-v1"
SILENCE_INVENTION = "Silence Gate"


def silence_gate_evaluate(
    *,
    link_ok: bool | None = None,
    heartbeat_age_seconds: int | None = None,
    heartbeat_max_seconds: int = 60,
    loss_of_contact: bool | None = None,
    would_auto_live: bool | None = None,
) -> dict[str, Any]:
    """Loss of contact ⇒ DENY — never auto-LIVE (Perimeter inverted)."""
    lost = bool(loss_of_contact) or link_ok is False
    if heartbeat_age_seconds is not None and heartbeat_age_seconds > heartbeat_max_seconds:
        lost = True
    auto = bool(would_auto_live)
    verdict = "SILENCE_DENY"
    if not lost:
        verdict = "LINK_OK"
    elif auto:
        verdict = "SILENCE_ANTI_PERIMETER"  # would have auto-LIVE — blocked
    return {
        "spec": SILENCE_SPEC,
        "invention": SILENCE_INVENTION,
        "family": FAMILY,
        "verdict": verdict,
        "link_lost": lost,
        "may_proceed": not lost,
        "anti_perimeter": True,
        "blocked_auto_live": lost and auto,
        "detail": (
            "Link lost — DENY. Anti-Perimeter: silence never mints LIVE."
            if lost
            else "Link healthy — Silence Gate idle."
        ),
        "rule": "Loss of contact ⇒ DENY. Dead Hand inverted. Software foothill; hardware Senate later.",
    }


# =============================================================================
# 4. Algedonic Relay
# =============================================================================

ALGEDONIC_SPEC = "gate-algedonic-relay-v1"
ALGEDONIC_INVENTION = "Algedonic Relay"


def algedonic_evaluate(
    *,
    local_hold_seconds: int | None = None,
    escalate_after_seconds: int = 14400,
    unresolved: bool | None = None,
    local_state: str | None = None,
    job_id: str | None = None,
) -> dict[str, Any]:
    """Local mouth holds; past τ unresolved ⇒ signed pain escalate upward."""
    held = int(local_hold_seconds or 0)
    need = max(60, int(escalate_after_seconds))
    stuck = bool(unresolved) or (local_state or "").upper() in ("HOLD", "CHOKE", "BLOCKED", "HALT")
    fire = stuck and held >= need
    packet = None
    if fire:
        packet = {
            "type": "ALGEDONIC_ESCALATE",
            "job_id": job_id,
            "local_state": local_state,
            "held_seconds": held,
            "escalate_after_seconds": need,
            "claim": "local_mouth_unresolved_past_tau",
            "next": "higher_recursion_with_signed_receipt",
        }
    return {
        "spec": ALGEDONIC_SPEC,
        "invention": ALGEDONIC_INVENTION,
        "family": FAMILY,
        "verdict": "ESCALATE" if fire else ("HOLDING" if stuck else "IDLE"),
        "escalate": fire,
        "held_seconds": held,
        "escalate_after_seconds": need,
        "packet": packet,
        "detail": (
            "Algedonic fire — local autonomy failed past timeout; escalate with receipt."
            if fire
            else ("Local mouth still holding within τ." if stuck else "No unresolved local hold.")
        ),
        "rule": "Pain rises only when local mouth fails past τ — Cybersyn-class, bind-desk scale.",
    }


# =============================================================================
# 5. May Budget
# =============================================================================

BUDGET_SPEC = "gate-may-budget-v1"
BUDGET_INVENTION = "May Budget"


def may_budget_evaluate(
    *,
    window_id: str | None = None,
    sacred_live_limit: int = 3,
    sacred_lives_used: int = 0,
    requesting_sacred_live: bool | None = None,
    mass_class: str | None = None,
) -> dict[str, Any]:
    """N sacred LIVEs per window — exhaust ⇒ DENY until window rolls."""
    limit = max(0, int(sacred_live_limit))
    used = max(0, int(sacred_lives_used))
    remaining = max(0, limit - used)
    want = bool(requesting_sacred_live) or (mass_class or "").lower() == "sacred"
    broke = want and remaining <= 0
    return {
        "spec": BUDGET_SPEC,
        "invention": BUDGET_INVENTION,
        "family": FAMILY,
        "verdict": "BUDGET_EXHAUSTED" if broke else ("BUDGET_OK" if not want or remaining > 0 else "BUDGET_OK"),
        "window_id": window_id or "default",
        "sacred_live_limit": limit,
        "sacred_lives_used": used,
        "remaining": remaining,
        "may_proceed": not broke,
        "would_debit": want and not broke,
        "detail": (
            "May budget exhausted — no sacred LIVE left this window."
            if broke
            else f"May budget {remaining}/{limit} sacred LIVEs remaining."
        ),
        "rule": "Sacred LIVE is scarce runtime spend — not unlimited clearance. Debit on OPEN.",
    }


# =============================================================================
# 6. Funeral Bit
# =============================================================================

FUNERAL_SPEC = "gate-funeral-bit-v1"
FUNERAL_INVENTION = "Funeral Bit"


def funeral_bit_evaluate(
    *,
    decommission: bool | None = None,
    principal_dead: bool | None = None,
    scrap: bool | None = None,
    may_hooks_remain: bool | None = None,
    fuse_id: str | None = None,
) -> dict[str, Any]:
    """Kill may-hooks at scrap/death — prove the mouth is dead."""
    rite = bool(decommission or principal_dead or scrap)
    ghost = bool(may_hooks_remain) and rite
    if not rite:
        return {
            "spec": FUNERAL_SPEC,
            "invention": FUNERAL_INVENTION,
            "family": FAMILY,
            "verdict": "FUNERAL_IDLE",
            "may_dead": False,
            "ghost_authority": False,
            "detail": "No decommission rite requested.",
            "rule": "Death/scrap of principal or unit ⇒ may dies. Ghost authority is Filter mode.",
        }
    funeral_id = f"fun_{uuid4().hex[:12]}"
    return {
        "spec": FUNERAL_SPEC,
        "invention": FUNERAL_INVENTION,
        "family": FAMILY,
        "verdict": "GHOST_AUTHORITY" if ghost else "MAY_DEAD",
        "may_dead": not ghost,
        "ghost_authority": ghost,
        "funeral_id": funeral_id,
        "fuse_id": fuse_id,
        "may_proceed": False,  # funeral never clears a bind
        "detail": (
            "Funeral incomplete — may-hooks still live (ghost authority)."
            if ghost
            else "Funeral complete — may-hooks killed; mouth proved dead."
        ),
        "rule": "Death/scrap of principal or unit ⇒ may dies. Ghost authority is Filter mode.",
        "prove": "Stranger can verify funeral_id — may must not resurrect without CHARGE+new commission.",
    }


# =============================================================================
# 7. Bind Genealogy
# =============================================================================

GENEALOGY_SPEC = "gate-bind-genealogy-v1"
GENEALOGY_INVENTION = "Bind Genealogy"


def bind_genealogy_stamp(
    *,
    job_id: str | None = None,
    throat_semver: str | None = None,
    oath_preset: str | None = None,
    skin: str | None = None,
    parent_event_id: str | None = None,
    event_id: str | None = None,
    program_id: str | None = None,
) -> dict[str, Any]:
    """Serial lineage: which mouth grammar shipped on which job."""
    stamp_id = f"gen_{uuid4().hex[:12]}"
    return {
        "spec": GENEALOGY_SPEC,
        "invention": GENEALOGY_INVENTION,
        "family": FAMILY,
        "stamp_id": stamp_id,
        "job_id": job_id,
        "event_id": event_id,
        "program_id": program_id,
        "throat_semver": throat_semver or "throat-v1",
        "oath_preset": oath_preset,
        "skin": skin or "gate_c",
        "parent_event_id": parent_event_id,
        "lineage": {
            "parent": parent_event_id,
            "self": event_id or stamp_id,
            "grammar": ["may", "sheath", "prove"],
        },
        "detail": "Genealogy stamp — may-line for this hop.",
        "rule": "Every production mouth act earns a serial lineage stamp. Orphan LIVE is forged.",
    }


# =============================================================================
# 8. Cold Weld (software genesis)
# =============================================================================

COLD_SPEC = "gate-cold-weld-v1"
COLD_INVENTION = "Cold Weld"


def cold_weld_evaluate(
    *,
    first_production: bool | None = None,
    genesis_done: bool | None = None,
    throat_pinned: bool | None = None,
    ghost_drill_passed: bool | None = None,
    witness_present: bool | None = None,
    program_id: str | None = None,
) -> dict[str, Any]:
    """Genesis ritual before first irreversible production bind."""
    if not first_production:
        return {
            "spec": COLD_SPEC,
            "invention": COLD_INVENTION,
            "family": FAMILY,
            "verdict": "COLD_WELD_NOT_REQUIRED",
            "may_proceed": True,
            "detail": "Not first production bind — Cold Weld idle.",
            "rule": "First production irreversible requires genesis receipt before LIVE.",
        }
    steps = {
        "genesis_receipt": bool(genesis_done),
        "throat_pinned": bool(throat_pinned),
        "ghost_drill_passed": bool(ghost_drill_passed),
        "witness_present": bool(witness_present),
    }
    missing = [k for k, ok in steps.items() if not ok]
    ready = not missing
    weld_id = f"cold_{uuid4().hex[:12]}" if ready else None
    return {
        "spec": COLD_SPEC,
        "invention": COLD_INVENTION,
        "family": FAMILY,
        "verdict": "COLD_WELD_READY" if ready else "COLD_WELD_INCOMPLETE",
        "may_proceed": ready,
        "steps": steps,
        "missing": missing,
        "weld_id": weld_id,
        "program_id": program_id,
        "detail": (
            "Cold Weld complete — genesis receipt minted; first LIVE eligible under other mouths."
            if ready
            else f"Cold Weld incomplete — missing: {', '.join(missing)}"
        ),
        "rule": "First production irreversible requires genesis receipt before LIVE.",
    }


# =============================================================================
# Pack attach + manifests
# =============================================================================

INVENTIONS = (
    ("stale_live", STALE_INVENTION, STALE_SPEC),
    ("cool_off", COOL_INVENTION, COOL_SPEC),
    ("silence_gate", SILENCE_INVENTION, SILENCE_SPEC),
    ("algedonic_relay", ALGEDONIC_INVENTION, ALGEDONIC_SPEC),
    ("may_budget", BUDGET_INVENTION, BUDGET_SPEC),
    ("funeral_bit", FUNERAL_INVENTION, FUNERAL_SPEC),
    ("bind_genealogy", GENEALOGY_INVENTION, GENEALOGY_SPEC),
    ("cold_weld", COLD_INVENTION, COLD_SPEC),
)


def attach(plan: dict, *, public_url: str = "") -> dict:
    """Run all densifiers that have signals on the plan; always stamp genealogy."""
    base = (public_url or "").rstrip("/")
    sm = plan.get("stick_meter") if isinstance(plan.get("stick_meter"), dict) else {}
    mt = plan.get("mass_tag") if isinstance(plan.get("mass_tag"), dict) else {}
    od = plan.get("gate_od_skins") if isinstance(plan.get("gate_od_skins"), dict) else {}
    mass = mt.get("mass_class") or mt.get("tag") or sm.get("mass_class") or od.get("mass_class")

    pack: dict[str, Any] = {"spec": SPEC_PACK, "family": FAMILY, "inventions": {}}

    pack["inventions"]["stale_live"] = stale_live_evaluate(
        live_issued_at=plan.get("live_issued_at"),
        stale_after_seconds=int(plan.get("stale_after_seconds") or 300),
        decision=plan.get("decision"),
        would_act=plan.get("acted") or plan.get("allow_bind"),
    )
    pack["inventions"]["cool_off"] = cool_off_evaluate(
        mass_class=mass,
        cool_off_seconds=plan.get("cool_off_seconds"),
        cool_started_at=plan.get("cool_started_at"),
        skip_attempt=plan.get("cool_skip"),
    )
    pack["inventions"]["silence_gate"] = silence_gate_evaluate(
        link_ok=plan.get("link_ok"),
        heartbeat_age_seconds=plan.get("heartbeat_age_seconds"),
        loss_of_contact=plan.get("loss_of_link") or plan.get("loss_of_contact"),
        would_auto_live=plan.get("would_auto_live"),
    )
    bpc = plan.get("bind_path_compiler") if isinstance(plan.get("bind_path_compiler"), dict) else {}
    pack["inventions"]["algedonic_relay"] = algedonic_evaluate(
        local_hold_seconds=plan.get("local_hold_seconds"),
        escalate_after_seconds=int(plan.get("escalate_after_seconds") or 14400),
        unresolved=bpc.get("path_state") in ("BLOCKED", "CHOKE", "HOLD") or plan.get("halt"),
        local_state=bpc.get("path_state") or plan.get("decision"),
        job_id=plan.get("job_id"),
    )
    pack["inventions"]["may_budget"] = may_budget_evaluate(
        window_id=plan.get("may_window_id"),
        sacred_live_limit=int(plan.get("sacred_live_limit") or 3),
        sacred_lives_used=int(plan.get("sacred_lives_used") or 0),
        requesting_sacred_live=plan.get("requesting_sacred_live"),
        mass_class=mass,
    )
    if plan.get("decommission") or plan.get("funeral") or plan.get("scrap"):
        pack["inventions"]["funeral_bit"] = funeral_bit_evaluate(
            decommission=plan.get("decommission") or plan.get("funeral"),
            principal_dead=plan.get("principal_dead"),
            scrap=plan.get("scrap"),
            may_hooks_remain=plan.get("may_hooks_remain"),
            fuse_id=plan.get("fuse_id"),
        )
    oath = plan.get("oath_compiler") if isinstance(plan.get("oath_compiler"), dict) else {}
    pack["inventions"]["bind_genealogy"] = bind_genealogy_stamp(
        job_id=plan.get("job_id"),
        throat_semver=(plan.get("throat") or {}).get("spec") if isinstance(plan.get("throat"), dict) else None,
        oath_preset=oath.get("preset"),
        skin=od.get("skin") or plan.get("gate_skin"),
        parent_event_id=plan.get("parent_event_id"),
        event_id=plan.get("event_id"),
        program_id=plan.get("program_id"),
    )
    if plan.get("first_production"):
        pack["inventions"]["cold_weld"] = cold_weld_evaluate(
            first_production=True,
            genesis_done=plan.get("genesis_done"),
            throat_pinned=plan.get("throat_pinned"),
            ghost_drill_passed=plan.get("ghost_drill_passed"),
            witness_present=plan.get("witness_present"),
            program_id=plan.get("program_id"),
        )

    # Aggregate blockers from densifiers
    blockers = []
    for key, inv in pack["inventions"].items():
        if inv.get("may_proceed") is False and inv.get("verdict") not in (
            "FUNERAL_IDLE",
            "COOL_NOT_REQUIRED",
            "COLD_WELD_NOT_REQUIRED",
            "LINK_OK",
            "IDLE",
            "HOLDING",
            "BUDGET_OK",
            "FRESH",
            "STALE",
        ):
            blockers.append(key)
        if inv.get("forged") or inv.get("ghost_authority"):
            blockers.append(key)
    pack["blockers"] = sorted(set(blockers))
    pack["mouth_density_score"] = len(INVENTIONS)
    pack["active_count"] = len(pack["inventions"])
    if base:
        pack["well_known"] = f"{base}/.well-known/mouth-density.json"
    plan["mouth_density"] = pack

    # Fail-closed hooks: forged stale / silence / cool skip / budget / cold incomplete / ghost
    for key in ("stale_live", "silence_gate", "cool_off", "may_budget", "cold_weld", "funeral_bit"):
        inv = pack["inventions"].get(key) or {}
        if inv.get("may_proceed") is False and key in pack["blockers"]:
            if plan.get("allow_bind") or plan.get("acted"):
                plan["allow_bind"] = False
                if "bind_allowed" in plan:
                    plan["bind_allowed"] = False
                plan["halt"] = True
                if not plan.get("decision") or plan.get("decision") == "ALLOW":
                    plan["decision"] = "HALT"
                plan["reason"] = plan.get("reason") or f"mouth_density:{key}"
    return plan


def evaluate(name: str, **kwargs: Any) -> dict[str, Any]:
    n = (name or "").strip().lower().replace("-", "_")
    table = {
        "stale_live": stale_live_evaluate,
        "cool_off": cool_off_evaluate,
        "silence_gate": silence_gate_evaluate,
        "algedonic_relay": algedonic_evaluate,
        "may_budget": may_budget_evaluate,
        "funeral_bit": funeral_bit_evaluate,
        "bind_genealogy": lambda **k: bind_genealogy_stamp(**k),
        "cold_weld": cold_weld_evaluate,
    }
    fn = table.get(n)
    if not fn:
        return {"error": "unknown_invention", "known": list(table)}
    return fn(**kwargs)


def manifest(public_url: str, name: str | None = None) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    catalog = []
    for slug, title, spec in INVENTIONS:
        catalog.append(
            {
                "slug": slug,
                "invention": title,
                "spec": spec,
                "well_known": f"{base}/.well-known/{slug.replace('_', '-')}.json",
                "demo": f"POST {base}/demo/pas/mouth-density",
            }
        )
    if name:
        slug = name.strip().lower().replace("-", "_")
        for c in catalog:
            if c["slug"] == slug:
                return {
                    **c,
                    "family": FAMILY,
                    "pack": SPEC_PACK,
                    "posture": POSTURE,
                    "mouth_thesis": "may · sheath · prove — densified before/during/after/life",
                }
    return {
        "spec": SPEC_PACK,
        "invention": "Mouth Density Pack",
        "family": FAMILY,
        "one_liner": "Eight foothill densifiers — stale LIVE, cool-off, silence, algedonic, may budget, funeral, genealogy, cold weld.",
        "count": len(INVENTIONS),
        "inventions": catalog,
        "demo": f"POST {base}/demo/pas/mouth-density",
        "well_known": f"{base}/.well-known/mouth-density.json",
        "mouth_thesis": "Maximize mouth: freshness · time · link · escalate · scarcity · death · lineage · genesis",
        "posture": POSTURE,
    }


def manifest_one(public_url: str, slug: str) -> dict[str, Any]:
    return manifest(public_url, name=slug)
