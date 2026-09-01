"""Mass Tag — labels a write with commit-mass class before the mouth.

Invention (NORTH_STAR foothill): makes Stick Meter actionable in UW UI.
Light / heavy / sacred tag travels with the hop so the desk knows quorum rules.
"""
from __future__ import annotations

from typing import Any

try:
    from gate import stick_meter as stick_mod
except ImportError:
    import stick_meter as stick_mod

SPEC = "gate-mass-tag-v1"
INVENTION = "Mass Tag"
FAMILY = "foothill"


def tag(*, plan: dict | None = None, stick_meter: dict | None = None) -> dict[str, Any]:
    sm = stick_meter if isinstance(stick_meter, dict) else {}
    if not sm and isinstance(plan, dict):
        sm = plan.get("stick_meter") if isinstance(plan.get("stick_meter"), dict) else {}
    mass_class = sm.get("mass_class") or stick_mod.CLASS_LIGHT
    score = sm.get("score", 0)
    quorum_hint = {
        stick_mod.CLASS_LIGHT: "standard mouth",
        stick_mod.CLASS_HEAVY: "desk escalation recommended",
        stick_mod.CLASS_SACRED: "quorum + CHARGE expected",
    }.get(mass_class, "standard mouth")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "tag": mass_class,
        "mass_class": mass_class,
        "score": score,
        "write_kind": sm.get("write_kind"),
        "quorum_hint": quorum_hint,
        "actionable": mass_class != stick_mod.CLASS_LIGHT,
        "pairs_with": "Stick Meter — score becomes UW-visible tag",
        "rule": "Tag travels with the hop. Sacred mass expects extra mouth.",
    }


def attach(plan: dict) -> dict:
    plan["mass_tag"] = tag(plan=plan)
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Light / heavy / sacred tag from Stick Meter — actionable in UW UI.",
        "classes": {
            stick_mod.CLASS_LIGHT: "routine — standard mouth",
            stick_mod.CLASS_HEAVY: "escalate — desk feels the weight",
            stick_mod.CLASS_SACRED: "quorum + CHARGE — sacred mass",
        },
        "stick_meter": f"{base}/.well-known/stick-meter.json",
        "well_known": f"{base}/.well-known/mass-tag.json",
        "bind_room": f"{base}/bind-room",
        "north_star": "gate/NORTH_STAR.md#inventions-forge-catalog",
        "posture": "Under coordinators. UW UI tag — does not mint LIVE.",
    }
