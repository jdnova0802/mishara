"""T+0 Honesty — atomic rails and multilateral nets are both real.

We do not replace CNS. Pre-net mouth on netted flow; atomic honesty on
irrevocable instant rails. Lying about either loses the peer.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-t0-honesty-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def mode(
    *,
    settlement_mode: str | None = None,
    claims_replace_net: bool | None = None,
) -> dict[str, Any]:
    m = (settlement_mode or "netted").strip().lower()
    replace = bool(claims_replace_net)
    if replace:
        posture = "dishonest_replace"
        claim = "reject_ccp_cosplay"
        ok = False
    elif m in ("atomic", "t0", "instant"):
        posture = "atomic_rail_honest"
        claim = "mouth_before_instant_finality"
        ok = True
    elif m in ("netted", "cns", "t1"):
        posture = "netted_rail_honest"
        claim = "pre_net_filter_before_cns"
        ok = True
    else:
        posture = "unknown_mode"
        claim = "declare_atomic_or_netted"
        ok = False
    return {
        "spec": SPEC,
        "name": "T+0 Honesty",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "GreySpark / industry T+0 vs netting tension",
            "DTCC CNS — multilateral net unchanged",
            "Gate distribution — do not replace your net",
        ],
        "settlement_mode": m,
        "claims_replace_net": replace,
        "posture": posture,
        "claim": claim,
        "passes": ok,
        "thesis": "Two modes. One alphabet. Never pretend to be the CCP.",
        "gatekeep": "Proprietary T+0 honesty. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "T+0 Honesty",
        "inventor": INVENTOR,
        "example_reject": mode(claims_replace_net=True),
        "example_netted": mode(settlement_mode="netted"),
        "example_atomic": mode(settlement_mode="atomic"),
        "live": f"{base}/.well-known/t0-honesty.json",
        "hardest": f"{base}/.well-known/hardest.json",
        "their_production": False,
    }
