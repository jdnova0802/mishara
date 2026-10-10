"""Gate Mine OS — catalog retained as a kill record.

Liquidation / funding / cross-venue searcher paths are KILLED. Same blade as
Keepers: zero-sum trading income vs fail-closed verification. See
gate/outbound/PASTE_KILL_MINE_OS.md. clear_gate refuses any KILLED mine.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-mine-os-v1"

# Searcher / trading mines are a kill record, not a roadmap.
MINES = (
    {
        "id": "liquidation",
        "name": "DeFi liquidation bonus",
        "status": "KILLED",
        "kill_reason": "keepers_blade",
        "payer": "protocol",
        "shape": "Flash-loan seize undercollateralized debt; keep bonus.",
        "cite": "Profits real (~$207M class; ~87% top-5). Gate seat is not. Same kill as Keepers.",
        "capital": "Near-zero with flash loans; edge is indexer + route + builder bid",
        "gate_role": "DO NOT OPERATE",
        "fed_scale": "killed_for_gate",
    },
    {
        "id": "funding",
        "name": "Perp funding cash-and-carry",
        "status": "KILLED",
        "kill_reason": "trading_desk_not_verification",
        "payer": "market",
        "shape": "Long spot + short perp when funding > threshold; collect every 8h.",
        "cite": "Real elsewhere. Not a Gate mouth.",
        "capital": "Working capital is the ASIC ($10k+ practical floor)",
        "gate_role": "DO NOT OPERATE",
        "fed_scale": "killed_for_gate",
    },
    {
        "id": "cross_venue_arb",
        "name": "Cross-venue / listing arb",
        "status": "KILLED",
        "kill_reason": "trading_desk_not_verification",
        "payer": "market_spread",
        "shape": "CEX↔DEX / cross-chain inventory when spread > fee drag.",
        "cite": "Speed race vs searchers. Not a Gate mouth.",
        "capital": "$10–50k inventory + colo for competitive tier",
        "gate_role": "DO NOT OPERATE",
        "fed_scale": "killed_for_gate",
    },
    {
        "id": "commerce_spread",
        "name": "Agent commerce spread mine",
        "status": "NOT_THIS_KILL",
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
        "status": "NOT_THIS_KILL",
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
            "KILL: liquidation, funding, and cross-venue searcher paths are dead "
            "for Gate — same blade as Keepers. Profits elsewhere do not open a seat. "
            "clear_gate refuses any mine whose status is KILLED."
        ),
        "killed": ["liquidation", "funding", "cross_venue_arb"],
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
    if str(mine.get("status") or "").startswith("KILLED"):
        return {
            "spec": SPEC,
            "mine": mine,
            "decision": "NO_GO",
            "halt": True,
            "reason": "mine_killed",
            "signals": [mine.get("kill_reason") or "keepers_blade"],
            "note": "Same kill as Keepers. Gate does not operate this desk.",
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
            "counterparty": "0x00000000000000000000000000000000000000f1",
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
