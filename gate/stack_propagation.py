"""Stack Propagation — doctrine at apex, obligation at base, economics in the register.

How Gate distributes without SaaS seats: PFMI-aligned manifests at tier 0
for reference; settlement members mutualize at tier 1; intermediaries weld
and propagate at tier 2; operators pay bps on cleared at tier 3. Matches
the register genesis — management + flow — not cliche channel partner MDF.

Not a slide with arrows. The propagation model the stack actually uses.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-stack-propagation-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def propagate(*, tier: int | None = None, welded: bool | None = None) -> dict[str, Any]:
    t = int(tier) if tier is not None else -1
    w = bool(welded)
    if t == 0:
        posture = "reference_only"
        claim = "cite_manifests_do_not_buy_seats"
    elif t == 1:
        posture = "mutualize"
        claim = "settlement_member_waterfall_skin"
    elif t == 2:
        posture = "propagate_requirement"
        claim = "intermediary_welds_and_passes_down"
    elif t == 3 and w:
        posture = "register_bps"
        claim = "operator_pays_on_cleared_flow"
    elif t == 3:
        posture = "unwelded_demo"
        claim = "doctrine_without_obligation"
    else:
        posture = "unknown_tier"
        claim = "see_distribution_stack"
    return {
        "spec": SPEC,
        "name": "Stack Propagation",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "tier": t if t >= 0 else None,
        "welded": w,
        "posture": posture,
        "claim": claim,
        "thesis": "Distribution matches the register tiers. Apex cites. Base pays bps.",
        "gatekeep": "Proprietary stack propagation. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Stack Propagation",
        "inventor": INVENTOR,
        "example_apex": propagate(tier=0),
        "example_operator": propagate(tier=3, welded=True),
        "live": f"{base}/.well-known/stack-propagation.json",
        "distribution": f"{base}/.well-known/distribution.json",
        "their_production": False,
    }
