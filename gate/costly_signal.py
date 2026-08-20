"""Costly Signal Weld — Veblen / CST without luxury cosplay.

Costly signaling: only those who can bear the cost send a reliable signal.
Veblen conspicuous consumption is the wrong costume — Gate's signal is
operational: paid weld + their_production flip. Cheap demos cannot forge
the production signal.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-costly-signal-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def signal(
    *,
    weld_paid: bool | None = None,
    their_production: bool | None = None,
    weld_price_label: str | None = "$25k weld",
) -> dict[str, Any]:
    paid = bool(weld_paid)
    prod = bool(their_production) if their_production is not None else False
    if paid and prod:
        grade = "reliable_production_signal"
    elif paid and not prod:
        grade = "costly_commit_pending_production_flag"
    elif not paid and prod:
        grade = "forged_signal_asymmetric"
    else:
        grade = "no_production_claim_honest_demo"
    return {
        "spec": SPEC,
        "name": "Costly Signal Weld",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Costly signaling theory — differential marginal cost keeps signals honest",
            "Veblen — conspicuous cost (inverted: Gate costs must be operational, not ornamental)",
            "Gate operator weld — unforgeable production signal",
        ],
        "signal_cost": weld_price_label,
        "weld_paid": paid,
        "their_production": prod,
        "grade": grade,
        "not_luxury_branding": True,
        "thesis": "Production is a costly signal. Demo without weld is cheap talk.",
        "gatekeep": "Proprietary costly-signal doctrine for weld/production. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Costly Signal Weld",
        "inventor": INVENTOR,
        "example_reliable": signal(weld_paid=True, their_production=True),
        "example_forged": signal(weld_paid=False, their_production=True),
        "live": f"{base}/.well-known/costly-signal.json",
        "operator": f"{base}/.well-known/operator.json",
        "skin": f"{base}/.well-known/skin.json",
        "their_production": False,
    }
