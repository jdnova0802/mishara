"""Capability Conversion — Sen-shaped freedom to spend (or be restrained).

Capability approach: resources convert to functionings via conversion factors.
Having a ticket (resource) is not the same as the real freedom to bind.

Gate conversion factors: fuse LIVE, license parent LIVE, epoch unlocked,
exclusion ok, exclusive door. Mouth evaluates whether resources convert
into the functioning 'permitted irreversible spend' — or into 'restraint'.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-capability-v1"
INVENTOR = "Nisaba LLC / Gate"

CONVERSION_FACTORS = (
    "fuse_live",
    "license_parent_live",
    "epoch_unlocked",
    "exclusion_ok",
    "ticket_live",
    "exclusive_door_honored",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def convert(
    *,
    has_ticket: bool | None = None,
    fuse_live: bool | None = None,
    license_parent_live: bool | None = None,
    license_fused: bool | None = None,
    epoch_locked: bool | None = None,
    exclusion_ok: bool | None = None,
    exclusive_door: bool | None = None,
) -> dict[str, Any]:
    factors = {
        "fuse_live": fuse_live,
        "license_parent_live": (
            True
            if license_fused is False
            else license_parent_live
        ),
        "epoch_unlocked": (False if epoch_locked else (True if epoch_locked is False else None)),
        "exclusion_ok": exclusion_ok,
        "ticket_live": has_ticket,
        "exclusive_door_honored": exclusive_door,
    }
    # Fail-closed: any known False blocks conversion to permitted spend
    blockers = [k for k, v in factors.items() if v is False]
    # license fused + parent not live
    if license_fused and license_parent_live is False:
        if "license_parent_live" not in blockers:
            blockers.append("license_parent_live")

    resource = {"ticket": bool(has_ticket)}
    if blockers:
        functioning = "restraint"
        capability = "no_real_freedom_to_spend"
        converted = False
    elif has_ticket and fuse_live is True and not blockers:
        # still need no unknowns that are critical — treat unknown exclusion as not converting
        if exclusion_ok is False or has_ticket is not True:
            functioning = "restraint"
            capability = "conversion_incomplete"
            converted = False
        elif all(factors[k] is not False for k in ("fuse_live", "ticket_live")):
            if epoch_locked:
                functioning = "restraint"
                capability = "epoch_blocks_conversion"
                converted = False
            else:
                functioning = "permitted_irreversible_spend"
                capability = "real_freedom_to_spend_on_this_hop"
                converted = True
        else:
            functioning = "unevaluated"
            capability = "insufficient_conversion_facts"
            converted = False
    else:
        functioning = "restraint_or_unevaluated"
        capability = "resources_without_conversion"
        converted = False

    return {
        "spec": SPEC,
        "name": "Capability Conversion",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Amartya Sen — capability approach; resources → functionings via conversion factors",
            "Gate commit-auth — ticket is resource; mouth evaluates conversion",
        ],
        "resource": resource,
        "conversion_factors": factors,
        "blockers": blockers,
        "functioning": functioning,
        "capability": capability,
        "converted_to_permitted_spend": converted,
        "thesis": (
            "A live ticket is not freedom to spend. Conversion factors — fuse, parent, "
            "epoch, exclusion, door — decide the real capability."
        ),
        "gatekeep": "Proprietary capability-conversion framing for mouth hops. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Capability Conversion",
        "inventor": INVENTOR,
        "conversion_factor_names": list(CONVERSION_FACTORS),
        "example_converted": convert(
            has_ticket=True,
            fuse_live=True,
            license_fused=False,
            epoch_locked=False,
            exclusion_ok=True,
            exclusive_door=True,
        ),
        "example_blocked": convert(
            has_ticket=True,
            fuse_live=True,
            license_fused=True,
            license_parent_live=False,
            epoch_locked=False,
        ),
        "live": f"{base}/.well-known/capability.json",
        "commit_auth": f"{base}/.well-known/commit-auth.json",
        "their_production": False,
    }
