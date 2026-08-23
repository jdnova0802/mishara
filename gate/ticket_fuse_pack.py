"""Ticket Fuse pack — productize license parent story for Bind Room / MGA pen.

Invention (NORTH_STAR foothill): bind ticket dies with parent license;
children cannot outlive the mouth. License fuse already ships in code —
this pack is the examiner-facing story and demo surface.
"""
from __future__ import annotations

from typing import Any

try:
    from gate import license_fuse as fuse_mod
except ImportError:
    import license_fuse as fuse_mod

SPEC = "gate-ticket-fuse-pack-v1"
INVENTION = "Ticket Fuse"
FAMILY = "foothill"


def pack(*, license_id: str | None = None, public_url: str = "") -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    lid = fuse_mod.normalize_id(license_id)
    snap = fuse_mod.snapshot(lid) if lid else fuse_mod.snapshot(None)
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "license_fuse": snap,
        "story": {
            "parent": "license_id is the parent permission mouth",
            "children": "bind tickets are children — cannot outlive parent",
            "dead": "parent DEAD → tickets cannot redeem until CHARGE",
            "armed": "LIVE parent with unredeemed child tickets → ARMED public state",
            "not": ["second bind-only write", "UW approve resurrection", "license_number PII key"],
        },
        "demo": {
            "charge": f"POST {base}/demo/pas/licenses/{{license_id}}/charge" if base else None,
            "dead": f"POST {base}/demo/pas/licenses/{{license_id}}/dead" if base else None,
            "pre_bind": f"POST {base}/demo/pas/policycenter/pre-bind" if base else None,
        },
        "spec_url": f"{base}/.well-known/license-fuse.json" if base else None,
        "pairs_with": "Charge Bride — only CHARGE resurrects DEAD parent",
        "rule": "Children cannot outlive the parent. Ticket fuse is the MGA pen story.",
    }


def attach(plan: dict, *, public_url: str = "") -> dict:
    lf = plan.get("license_fuse") if isinstance(plan.get("license_fuse"), dict) else {}
    plan["ticket_fuse"] = pack(license_id=lf.get("license_id"), public_url=public_url)
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Bind ticket dies with parent license — children cannot outlive the mouth.",
        "license_fuse": f"{base}/.well-known/license-fuse.json",
        "demo_pack": f"GET {base}/demo/pas/ticket-fuse-pack",
        "well_known": f"{base}/.well-known/ticket-fuse-pack.json",
        "bind_room": f"{base}/bind-room",
        "north_star": "gate/NORTH_STAR.md#inventions-forge-catalog",
        "posture": "Under coordinators. MGA pen productization — fuse already in code.",
    }
