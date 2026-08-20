"""Register calculator — mouths × cleared volume × bps."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-register-calculator-v1"
INVENTOR = "Nisaba LLC / Gate"

WELD_CENTS = 2_500_000
MGMT_MONTH_CENTS = 500_000
BPS = 10


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def compute(
    *,
    mouths: int = 1,
    cleared_usd: float = 10_000_000.0,
    months: int = 12,
) -> dict[str, Any]:
    m = max(1, int(mouths))
    cleared = max(0.0, float(cleared_usd))
    mo = max(1, int(months))
    weld = m * WELD_CENTS
    mgmt = m * MGMT_MONTH_CENTS * mo
    flow = int(round(cleared * BPS / 10_000))
    total = weld + mgmt + flow
    return {
        "mouths": m,
        "cleared_usd": cleared,
        "months": mo,
        "weld_usd": weld / 100,
        "management_usd": mgmt / 100,
        "flow_bps_usd": flow / 100,
        "total_usd": total / 100,
        "bps": BPS,
        "not_charged": ["FMI apex reference tier", "per-seat dashboard", "SaaS tiers"],
    }


def examples() -> list[dict[str, Any]]:
    return [
        {"label": "One MGA · $10M cleared/yr", **compute(mouths=1, cleared_usd=10_000_000, months=12)},
        {"label": "Ten mouths · $100M cleared/yr", **compute(mouths=10, cleared_usd=100_000_000, months=12)},
        {
            "label": "Civilization scale · $1T cleared/yr (1 mouth)",
            **compute(mouths=1, cleared_usd=1_000_000_000_000, months=12),
        },
    ]


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Register calculator",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "formula": "total = mouths×weld + mouths×mgmt×months + cleared×bps/10000",
        "defaults": compute(),
        "examples": examples(),
        "api": f"{base}/.well-known/register-calculator.json?mouths=1&cleared_usd=10000000&months=12",
        "page": f"{base}/calculator",
    }
