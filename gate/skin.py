"""Skin in the Weld — Taleb symmetry on irreversible permission.

Taleb: who gets the upside must share the downside. Asymmetry is the bug.

Gate: operator weld price, Gate capital in the default waterfall, mutualized
member fund — skin that faces loss when the mouth or settlement fails.
Demo without weld = no skin. their_production:false until costly commit.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-skin-v1"
INVENTOR = "Nisaba LLC / Gate"

SKIN_LAYERS = (
    {
        "id": "operator_weld",
        "who": "licensed operator",
        "downside": "paid weld + management; reputation on LIVE mouth",
        "upside_without_skin_rejected": "demo theater as production",
    },
    {
        "id": "gate_capital",
        "who": "Nisaba / Gate",
        "downside": "skin-in-the-game capital in settlement default waterfall",
        "upside_without_skin_rejected": "fee-only rail with zero loss absorption",
    },
    {
        "id": "mutualized_fund",
        "who": "settlement members",
        "downside": "mutualized default fund contribution",
        "upside_without_skin_rejected": "members who only take netting benefit",
    },
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def symmetry(
    *,
    weld_paid: bool | None = None,
    their_production: bool | None = None,
    gate_capital_posted: bool | None = True,
) -> dict[str, Any]:
    weld = bool(weld_paid)
    prod = bool(their_production) if their_production is not None else weld
    capital = True if gate_capital_posted is None else bool(gate_capital_posted)

    asymmetric = prod and not weld
    return {
        "spec": SPEC,
        "name": "Skin in the Weld",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Nassim Taleb — Skin in the Game; symmetry of upside and downside",
            "Gate operator weld — costly commit before production mouth",
            "Gate settlement waterfall — Gate capital + mutualized fund",
        ],
        "layers": list(SKIN_LAYERS),
        "assay": {
            "weld_paid": weld,
            "their_production": prod,
            "gate_capital_posted": capital,
            "asymmetric": asymmetric,
            "claim": (
                "production_claimed_without_weld_skin"
                if asymmetric
                else "symmetry_or_honest_non_production"
            ),
        },
        "rule": "Never trust a production mouth with no skin in the weld.",
        "thesis": "Clear-before-wire needs someone who loses when the no fails.",
        "gatekeep": "Proprietary skin-symmetry doctrine for Gate production. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Skin in the Weld",
        "inventor": INVENTOR,
        "example_ok": symmetry(weld_paid=True, their_production=True),
        "example_asymmetric": symmetry(weld_paid=False, their_production=True),
        "live": f"{base}/.well-known/skin.json",
        "operator": f"{base}/.well-known/operator.json",
        "settlement": f"{base}/.well-known/settlement.json",
        "their_production": False,
    }
