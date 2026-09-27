"""Gate Mine OS — fail-closed brain of a self-operating money machine.

Philosophical remix: Gate is no longer "sell Clear to strangers."
Gate is the ASIC controller. Markets / protocols / agent rails pay the block
reward. Clear refuses suicide commits. You + product. No forms. No sales.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-mine-os-v1"

# Mines ranked by how close they are to early Bitcoin mining:
# protocol/market pays YOU for work. No human customer.
MINES = (
    {
        "id": "liquidation",
        "name": "DeFi liquidation bonus",
        "payer": "protocol",
        "shape": "Flash-loan seize undercollateralized debt; keep bonus.",
        "cite": "Top liquidator ~$26M net / 14mo across Aave/Morpho/Spark; top-20 take ~89%",
        "capital": "Near-zero with flash loans; edge is indexer + route + builder bid",
        "gate_role": "Clear before seize — refuse unprofitable / HF-edge suicides",
        "fed_scale": "yes_if_top_cohort",
    },
    {
        "id": "funding",
        "name": "Perp funding cash-and-carry",
        "payer": "market",
        "shape": "Long spot + short perp when funding > threshold; collect every 8h.",
        "cite": "Worked examples ~3–7%/mo on ~$50k; crash-day rates spike harder",
        "capital": "Working capital is the ASIC ($10k+ practical floor)",
        "gate_role": "Clear before size / flip — refuse rate-inversion traps",
        "fed_scale": "scales_with_capital",
    },
    {
        "id": "cross_venue_arb",
        "name": "Cross-venue / listing arb",
        "payer": "market_spread",
        "shape": "CEX↔DEX / cross-chain inventory when spread > fee drag.",
        "cite": "Solana listing spikes: hundreds per event with inventory; pure atomic DEX arb saturated",
        "capital": "$10–50k inventory + colo for competitive tier",
        "gate_role": "Clear before bridge/withdraw — refuse incomplete legs",
        "fed_scale": "yes_with_inventory_and_speed",
    },
    {
        "id": "commerce_spread",
        "name": "Agent commerce spread mine",
        "payer": "agent_wallets",
        "shape": "Buy wholesale (gift cards / premium APIs) → sell via x402 retail.",
        "cite": "Bitrefill x402 ~$592k tracked; stableenrich.dev ~$940/mo pure API resale pattern",
        "capital": "Wholesale float + API keys",
        "gate_role": "Issuing/x402 Clear on YOUR buy side; meter on sell side",
        "fed_scale": "yes_at_commerce_volume",
    },
    {
        "id": "action_execution",
        "name": "Paid agent actions (swap/hire/rent)",
        "payer": "agent_wallets",
        "shape": "Agents pay for doing the thing — swap execute, browser rent, hire.",
        "cite": "hibra swap execute organic payers; Browserbase return×50; molty hire tips",
        "capital": "Execution float + infra",
        "gate_role": "Clear before irreversible on-chain act you execute for them",
        "fed_scale": "rising",
    },
)


def catalog() -> dict[str, Any]:
    return {
        "spec": SPEC,
        "doctrine": (
            "Markets and protocols are the Fed. Gate Clear is the mining OS — "
            "fail-closed before irreversible size. You operate the farm. "
            "No forms. No sales. No waiting on humans."
        ),
        "mines": list(MINES),
        "empty_niches_agents_pay": [
            "DeFi health-factor / liquidation-candidate passports (catalog almost empty)",
            "Compliance AML/sanctions screen before agent spend",
            "Agent commerce beyond gift cards (tickets, domains, hosting)",
            "DeFi operation execution (swaps/limits/bridges) — one notable player",
        ],
    }


def clear_gate(
    *,
    mine_id: str,
    notional_usd: float,
    expected_edge_bps: float,
    max_loss_usd: float,
    public_url: str = "https://gate.local",
) -> dict[str, Any]:
    """Fail-closed sizing gate before a mine action commits capital."""
    try:
        from gate import prefinality as prefinality_mod
    except ImportError:
        import prefinality as prefinality_mod

    mine = next((m for m in MINES if m["id"] == mine_id), None)
    if not mine:
        return {
            "spec": SPEC,
            "decision": "NO_GO",
            "halt": True,
            "reason": "unknown_mine",
            "mine_id": mine_id,
        }

    # Refuse negative / zero edge and uncapped loss
    signals: list[str] = []
    decision = "GO"
    if expected_edge_bps <= 0:
        decision = "NO_GO"
        signals.append("nonpositive_edge")
    if max_loss_usd <= 0 or max_loss_usd > notional_usd:
        decision = "NO_GO"
        signals.append("loss_cap_invalid")
    if notional_usd <= 0:
        decision = "NO_GO"
        signals.append("zero_notional")

    # Soft hold if edge thin vs fee drag (~8 bps round-trip typical)
    if decision == "GO" and expected_edge_bps < 10:
        decision = "HOLD"
        signals.append("edge_below_fee_drag")

    body = {
        "rail": "x402",
        "transfer": {
            "amount": f"{notional_usd:.2f}",
            "currency": "USDC",
            "counterparty": "0x00000000000000000000000000000000000000m1",
        },
        "mandate": {
            "agent_id": f"mine-{mine_id}",
            "max_amount": f"{notional_usd:.2f}",
            "max_loss_usd": f"{max_loss_usd:.2f}",
            "expected_edge_bps": expected_edge_bps,
        },
        "context": {"mine_id": mine_id, "signals": signals},
    }
    pf = prefinality_mod.evaluate(body, public_url=public_url)
    # Prefer mine signals over soft prefinality when we already NO_GO
    if decision == "NO_GO":
        return {
            "spec": SPEC,
            "mine": mine,
            "decision": "NO_GO",
            "halt": True,
            "signals": signals,
            "prefinality": {
                "decision": pf.get("decision"),
                "evaluation_id": pf.get("evaluation_id"),
            },
            "note": "Mine OS refused — would not commit capital.",
        }

    out_decision = pf.get("decision") or decision
    if decision == "HOLD" and out_decision == "GO":
        out_decision = "HOLD"

    return {
        "spec": SPEC,
        "mine": mine,
        "decision": out_decision,
        "halt": out_decision != "GO",
        "signals": signals,
        "notional_usd": notional_usd,
        "expected_edge_bps": expected_edge_bps,
        "max_loss_usd": max_loss_usd,
        "receipt": pf.get("receipt"),
        "evaluation_id": pf.get("evaluation_id"),
        "transfer_fingerprint": pf.get("transfer_fingerprint") or pf.get("fingerprint"),
        "note": (
            "GO = mine may size. HOLD = edge too thin. NO_GO = refuse. "
            "Block reward comes from the market/protocol — not from a buyer email."
        ),
    }
