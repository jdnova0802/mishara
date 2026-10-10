"""Agent commerce / API spread mine — machines pay USDC; you keep the margin.

Pattern proven by stableenrich.dev (~$940/mo pure resale) and Bitrefill (~$592k
tracked on x402 commerce). Wholesale cost → x402 retail. You + product.
"""
from __future__ import annotations

from typing import Any

try:
    from gate.mine import clear_gate
except ImportError:
    from mine import clear_gate  # type: ignore

SPEC = "gate-mine-spread-v1"

# Empty / high-WTP niches from CDP Bazaar analysis (Jul 2026) + live earners
SKUS = (
    {
        "id": "people_enrich",
        "wholesale_usd": 0.12,
        "retail_usd": 0.28,
        "note": "Highest WTP in Bazaar API segment — people enrichment",
    },
    {
        "id": "web_scrape_managed",
        "wholesale_usd": 0.004,
        "retail_usd": 0.02,
        "note": "Eyes-on-internet is ~half of paid calls; mid-price almost empty",
    },
    {
        "id": "hf_risk_passport",
        "wholesale_usd": 0.0,
        "retail_usd": 0.05,
        "note": "DeFi HF/liquidation passport — catalog nearly empty; Gate-native",
    },
    {
        "id": "gift_card_face_100",
        "wholesale_usd": 92.0,
        "retail_usd": 100.0,
        "note": "Bitrefill-class commerce: wholesale under parity → agent retail",
    },
)


def margin(sku: dict) -> dict[str, Any]:
    w = float(sku["wholesale_usd"])
    r = float(sku["retail_usd"])
    m = r - w
    pct = (m / r * 100.0) if r else 0.0
    return {
        "sku_id": sku["id"],
        "wholesale_usd": w,
        "retail_usd": r,
        "margin_usd": round(m, 6),
        "margin_pct": round(pct, 2),
        "note": sku.get("note"),
    }


def plan(
    *,
    sku_id: str,
    monthly_calls: int,
    public_url: str = "https://gate.local",
) -> dict[str, Any]:
    sku = next((s for s in SKUS if s["id"] == sku_id), None)
    if not sku:
        return {"spec": SPEC, "ok": False, "error": "unknown_sku", "sku_id": sku_id}

    m = margin(sku)
    calls = max(0, int(monthly_calls))
    gross = m["margin_usd"] * calls
    # Clear the wholesale float commitment for one month of buys
    wholesale_float = float(sku["wholesale_usd"]) * calls
    edge_bps = (m["margin_usd"] / float(sku["retail_usd"]) * 10_000) if sku["retail_usd"] else 0.0

    gate = clear_gate(
        mine_id="commerce_spread",
        notional_usd=max(wholesale_float, 1.0),
        expected_edge_bps=float(edge_bps),
        max_loss_usd=max(wholesale_float * 0.05, 1.0),
        public_url=public_url,
    )

    return {
        "spec": SPEC,
        "ok": True,
        "margin": m,
        "monthly_calls": calls,
        "projected_gross_margin_usd": round(gross, 2),
        "wholesale_float_usd": round(wholesale_float, 2),
        "gate": gate,
        "print_shape": (
            "Agents settle USDC to your payTo. You buy wholesale. Margin = block reward. "
            "No outreach — discovery + 402. Scale = call volume × margin."
        ),
        "skus": [margin(s) for s in SKUS],
    }
