"""Stick Meter — scores mass of a commercial write before the mouth.

Invention (NORTH_STAR foothill): CUOs already feel "this one's heavy" — give
them a number. Scores bind, payout, sanction-flag, and agent/PLC writes on
0–100 and labels commit-mass class (light / heavy / sacred) before Throat.

Stick Meter does not clear or deny. It measures gravity so the desk knows
what kind of mouth they're standing in front of.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-stick-meter-v1"
INVENTION = "Stick Meter"
FAMILY = "foothill"

CLASS_LIGHT = "light"
CLASS_HEAVY = "heavy"
CLASS_SACRED = "sacred"

WRITE_BIND = "bind"
WRITE_PAYOUT = "payout"
WRITE_SANCTION = "sanction_flag"
WRITE_AGENT = "agent_tool"
WRITE_PLC = "plc_write"

_BASE = {
    WRITE_BIND: 35,
    WRITE_PAYOUT: 45,
    WRITE_SANCTION: 55,
    WRITE_AGENT: 40,
    WRITE_PLC: 50,
}


def _norm(v: str | None) -> str:
    return (v or "").strip().lower()


def _write_kind(*, write_kind: str | None = None, spend_write: dict | None = None) -> str:
    wk = _norm(write_kind)
    if wk in _BASE:
        return wk
    if isinstance(spend_write, dict):
        sk = _norm(spend_write.get("spend_kind"))
        if sk in ("bind", "payout", "sanction", "sanction_flag"):
            return WRITE_SANCTION if sk.startswith("sanction") else sk
        path = (spend_write.get("path") or "").lower()
        if "payout" in path or "withdraw" in path:
            return WRITE_PAYOUT
        if "bind" in path:
            return WRITE_BIND
    return WRITE_BIND


def score(
    *,
    write_kind: str | None = None,
    spend_write: dict | None = None,
    premium: float | None = None,
    authority_limit: float | None = None,
    sanction_flag: bool | None = None,
    fuse_state: str | None = None,
    license_state: str | None = None,
    epoch_locked: bool | None = None,
    would_bind: bool | None = None,
    acted: bool | None = None,
) -> dict[str, Any]:
    """Score commit-mass 0–100 and assign light / heavy / sacred class."""
    kind = _write_kind(write_kind=write_kind, spend_write=spend_write)
    total = _BASE.get(kind, 35)
    factors: list[dict[str, Any]] = [
        {"factor": "write_kind", "kind": kind, "points": _BASE.get(kind, 35)},
    ]

    prem = float(premium) if premium is not None else None
    limit = float(authority_limit) if authority_limit is not None else None
    if prem is not None and limit is not None and limit > 0:
        ratio = prem / limit
        if ratio > 1.0:
            pts = 25
            factors.append({"factor": "premium_over_authority", "ratio": round(ratio, 4), "points": pts})
            total += pts
        elif ratio >= 0.8:
            pts = 12
            factors.append({"factor": "premium_near_ceiling", "ratio": round(ratio, 4), "points": pts})
            total += pts

    fs = _norm(fuse_state).upper()
    if fs in ("DEAD", "HALT", "BLOCK", "DENY"):
        pts = 20
        factors.append({"factor": "fuse_not_live", "state": fs, "points": pts})
        total += pts

    ls = _norm(license_state).upper()
    if ls and ls not in ("", "LIVE", "ARMED"):
        pts = 15
        factors.append({"factor": "license_parent_not_live", "state": ls, "points": pts})
        total += pts

    if epoch_locked:
        pts = 15
        factors.append({"factor": "epoch_locked", "points": pts})
        total += pts

    if sanction_flag:
        pts = 15
        factors.append({"factor": "sanction_flag", "points": pts})
        total += pts

    if would_bind or acted:
        pts = 8
        factors.append({"factor": "irreversible_edge", "points": pts})
        total += pts

    total = min(100, max(0, total))
    if total >= 75:
        mass_class = CLASS_SACRED
    elif total >= 40:
        mass_class = CLASS_HEAVY
    else:
        mass_class = CLASS_LIGHT

    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "score": total,
        "mass_class": mass_class,
        "write_kind": kind,
        "factors": factors,
        "interpretation": {
            CLASS_LIGHT: "Routine commercial write — standard mouth",
            CLASS_HEAVY: "High commit-mass — desk should feel the weight",
            CLASS_SACRED: "Sacred mass — quorum / CHARGE / extra mouth expected",
        }[mass_class],
        "rule": "Measure gravity before the mouth. Stick Meter does not clear or deny.",
        "pairs_with": "Throat — mouth; Stick Meter — how heavy the stick would be",
    }


def attach(plan: dict, *, spend_write: dict | None = None) -> dict:
    """Stamp Stick Meter onto a pre-bind / bind-check plan."""
    lf = plan.get("license_fuse") if isinstance(plan.get("license_fuse"), dict) else {}
    epoch = plan.get("epoch") if isinstance(plan.get("epoch"), dict) else {}
    hop = plan.get("hop") if isinstance(plan.get("hop"), dict) else {}
    sw = spend_write if isinstance(spend_write, dict) else plan.get("spend_protocol", {}).get("write")
    meter = score(
        write_kind=plan.get("write_kind"),
        spend_write=sw if isinstance(sw, dict) else None,
        premium=plan.get("premium"),
        authority_limit=plan.get("authority_limit"),
        sanction_flag=plan.get("sanction_flag") or hop.get("sanction_flag"),
        fuse_state=plan.get("fuse_state") or hop.get("fuse_state") or hop.get("decision"),
        license_state=lf.get("stored") or lf.get("state"),
        epoch_locked=bool(epoch.get("locked")) if epoch else bool(plan.get("epoch_locked")),
        would_bind=bool(plan.get("allow_bind") or plan.get("bind_allowed")),
        acted=bool(plan.get("acted")),
    )
    plan["stick_meter"] = meter
    plan["mass_class"] = meter["mass_class"]
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Scores commit-mass of bind/payout/sanction writes before the mouth.",
        "classes": {
            CLASS_LIGHT: "score < 40 — routine write",
            CLASS_HEAVY: "40 ≤ score < 75 — desk should feel the weight",
            CLASS_SACRED: "score ≥ 75 — sacred mass; extra mouth / quorum expected",
        },
        "write_kinds": list(_BASE.keys()),
        "pairs_with": "Throat + Charge Bride — measure before mouth; Bride blocks forged resurrect",
        "demo": f"POST {base}/demo/pas/stick-meter",
        "well_known": f"{base}/.well-known/stick-meter.json",
        "bind_room": f"{base}/bind-room",
        "north_star": "gate/NORTH_STAR.md#inventions-forge-catalog",
        "posture": "Under coordinators. Scoreboard invention — does not mint LIVE.",
    }
