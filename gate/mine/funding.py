"""Funding cash-and-carry scanner — market pays you every 8h.

No human customer. You + capital + Gate Clear. Funding rate IS the block reward.
"""
from __future__ import annotations

import json
from typing import Any
from urllib.request import Request, urlopen

try:
    from gate.mine import clear_gate
except ImportError:
    from mine import clear_gate  # type: ignore

SPEC = "gate-mine-funding-v1"
# Enter when 8h rate ≥ this (0.025% = 25 bps per 8h ≈ ~27% APR floor after fees)
DEFAULT_ENTER_BPS_8H = 25.0
DEFAULT_EXIT_BPS_8H = 5.0


def _fetch_binance_premium(symbol: str = "BTCUSDT") -> dict[str, Any] | None:
    url = f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol}"
    try:
        req = Request(url, headers={"User-Agent": "gate-mine/1.0"})
        with urlopen(req, timeout=8) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        return {"error": str(exc)[:200]}


def scan(
    *,
    symbol: str = "BTCUSDT",
    notional_usd: float = 10_000.0,
    max_loss_usd: float = 200.0,
    enter_bps_8h: float = DEFAULT_ENTER_BPS_8H,
    public_url: str = "https://gate.local",
) -> dict[str, Any]:
    """Pull live funding; Clear-gate whether to open cash-and-carry."""
    raw = _fetch_binance_premium(symbol)
    if not raw or raw.get("error"):
        return {
            "spec": SPEC,
            "ok": False,
            "symbol": symbol,
            "error": (raw or {}).get("error") or "premium_fetch_failed",
        }

    # lastFundingRate is decimal per 8h (e.g. 0.0001 = 1 bps)
    try:
        rate = float(raw.get("lastFundingRate") or 0.0)
    except (TypeError, ValueError):
        rate = 0.0
    rate_bps_8h = rate * 10_000.0
    # Annualize roughly: 3 settlements/day × 365
    apr_pct = rate_bps_8h * 3 * 365 / 100.0

    edge_bps = rate_bps_8h  # collect positive funding as short-perp
    action = "open_short_perp_long_spot" if rate_bps_8h >= enter_bps_8h else "stand_down"
    if rate_bps_8h <= -enter_bps_8h:
        action = "open_long_perp_short_spot"
        edge_bps = abs(rate_bps_8h)

    gate = clear_gate(
        mine_id="funding",
        notional_usd=float(notional_usd),
        expected_edge_bps=float(edge_bps) if action != "stand_down" else 0.0,
        max_loss_usd=float(max_loss_usd),
        public_url=public_url,
    )

    return {
        "spec": SPEC,
        "ok": True,
        "symbol": symbol,
        "mark_price": raw.get("markPrice"),
        "last_funding_rate": rate,
        "rate_bps_8h": round(rate_bps_8h, 4),
        "apr_pct_approx": round(apr_pct, 2),
        "enter_threshold_bps_8h": enter_bps_8h,
        "proposed_action": action,
        "gate": gate,
        "print_shape": (
            "Market pays funding to the side you hold. Gate Clear is the mining OS — "
            "size only on GO. Scale = capital × rate × uptime."
        ),
    }
