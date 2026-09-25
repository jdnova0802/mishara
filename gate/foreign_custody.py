"""Foreign custody — where real money lives (never Gate).

Atoms (do not collapse these):

  1. VAULT     — holds dollars / USDC. Licensed bank, on-chain escrow, or Issuing.
                 Gate does NOT hold keys, title, or balances.
  2. MANDATE   — spend rules. Indexed by Gate.
  3. CLEAR     — GO / NO_GO / NEVER attestation. Gate's hash function.
  4. KEEPER    — watches, races to liquidate. You.
  5. BOUNTY    — paid by the VAULT from residual. Protocol pays; Gate is not the payer.

Demo ledger is atom-index only. Massive money enters when a VAULT that already
holds real value accepts Gate execution packets.
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Any

SPEC = "gate-foreign-custody-v1"

# Venue codes. Only venues with money_real=True can ever pay real bounties.
VENUE_DEMO_LEDGER = "demo_ledger"
VENUE_ONCHAIN_USDC = "onchain_usdc"
VENUE_STRIPE_ISSUING = "stripe_issuing"
VENUE_SPONSOR_BANK = "sponsor_bank"

VENUES = {
    VENUE_DEMO_LEDGER: {
        "venue": VENUE_DEMO_LEDGER,
        "money_real": False,
        "holds_funds": "sqlite_integer_only",
        "gate_holds_funds": False,
        "massive_ingress": False,
        "plain": "Demo units. Proves mechanics. Pays nothing real.",
    },
    VENUE_ONCHAIN_USDC: {
        "venue": VENUE_ONCHAIN_USDC,
        "money_real": True,
        "holds_funds": "smart_contract_usdc",
        "gate_holds_funds": False,
        "massive_ingress": True,
        "plain": (
            "Permissionless USDC lock in ClearanceEscrow. Anyone parks capital. "
            "Release only on Gate Clear. Breach → keeper submits Gate Never packet; "
            "contract pays bounty. Gate has no withdraw key."
        ),
        "scale_why": "Open TVL — no sales call per dollar. Same shape as DeFi liquidations.",
    },
    VENUE_STRIPE_ISSUING: {
        "venue": VENUE_STRIPE_ISSUING,
        "money_real": True,
        "holds_funds": "stripe_licensed_program",
        "gate_holds_funds": False,
        "massive_ingress": True,
        "plain": (
            "Agent cards / Issuing balances live at Stripe. Gate = auth mouth. "
            "Keepers force-halt / reclaim via Issuing APIs when Never fires. "
            "Access-gated (Stripe program), not permissionless."
        ),
        "scale_why": "Agent GMV already real; Issuing approval is the choke.",
    },
    VENUE_SPONSOR_BANK: {
        "venue": VENUE_SPONSOR_BANK,
        "money_real": True,
        "holds_funds": "sponsor_bank_or_baas",
        "gate_holds_funds": False,
        "massive_ingress": True,
        "plain": (
            "Bank holds balances. Gate = release authority only. "
            "Same custody answer as the float scope — lock, not vault."
        ),
        "scale_why": "Institutional float; BD + DD timeline, not overnight TVL.",
    },
}


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def venue_info(venue: str | None) -> dict[str, Any]:
    key = (venue or VENUE_DEMO_LEDGER).strip().lower()
    row = VENUES.get(key)
    if not row:
        return {
            "venue": key,
            "money_real": False,
            "gate_holds_funds": False,
            "error": "unknown_venue",
            "known": list(VENUES),
        }
    return dict(row)


def onchain_config() -> dict[str, Any]:
    """Env-wired ClearanceEscrow. Empty = not live; money cannot enter yet."""
    chain_id = (os.getenv("GATE_ESCROW_CHAIN_ID") or "").strip()
    contract = (os.getenv("GATE_ESCROW_CONTRACT") or "").strip()
    usdc = (os.getenv("GATE_ESCROW_USDC") or "").strip()
    configured = bool(chain_id and contract and usdc)
    try:
        from gate import escrow_preflight as preflight
    except ImportError:
        import escrow_preflight as preflight
    pf = preflight.report()
    return {
        "venue": VENUE_ONCHAIN_USDC,
        "configured": configured,
        "preflight_all_passed": pf["all_passed"],
        "money_can_enter": bool(configured and pf["all_passed"]),
        "chain_id": chain_id or None,
        "contract": contract or None,
        "usdc": usdc or None,
        "gate_holds_funds": False,
        "plain": (
            "Contract env alone is not enough. All four preflight gates must pass "
            "before real USDC. See /.well-known/escrow-preflight.json"
        ),
        "preflight_spec": "gate-escrow-preflight-v1",
    }


def stripe_issuing_config() -> dict[str, Any]:
    ready = bool((os.getenv("STRIPE_SECRET_KEY") or "").strip()) and (
        os.getenv("GATE_ISSUING_ENABLED", "").strip().lower() in ("1", "true", "yes", "on")
    )
    return {
        "venue": VENUE_STRIPE_ISSUING,
        "configured": ready,
        "money_can_enter": ready,
        "gate_holds_funds": False,
        "plain": (
            "Issuing program must be live. Gate never receives card float — "
            "only AUTHORIZE/DECLINE + reclaim attestation packets."
        ),
    }


def normalize_custody(raw: dict | None, *, escrow_units: int) -> dict[str, Any]:
    """Attach a custody binding to a position. Default = demo (not real money)."""
    body = raw if isinstance(raw, dict) else {}
    venue = (body.get("venue") or VENUE_DEMO_LEDGER).strip().lower()
    info = venue_info(venue)
    if info.get("error"):
        venue = VENUE_DEMO_LEDGER
        info = venue_info(venue)

    venue_ref = (body.get("venue_ref") or body.get("vault_ref") or "").strip()
    escrow_id = (body.get("escrow_id") or body.get("position_ref") or "").strip()

    if venue == VENUE_DEMO_LEDGER:
        money_real = False
        if not venue_ref:
            venue_ref = "demo"
        if not escrow_id:
            escrow_id = "local"
    elif venue == VENUE_ONCHAIN_USDC:
        cfg = onchain_config()
        money_real = bool(cfg["configured"] and venue_ref and escrow_id)
        if not venue_ref and cfg.get("contract"):
            venue_ref = cfg["contract"]
    elif venue == VENUE_STRIPE_ISSUING:
        cfg = stripe_issuing_config()
        money_real = bool(cfg["configured"] and venue_ref)
    else:
        money_real = False  # sponsor_bank needs explicit live binding + counsel

    return {
        "spec": SPEC,
        "venue": venue,
        "venue_ref": venue_ref or None,
        "escrow_id": escrow_id or None,
        "claimed_units": escrow_units,
        "money_real": money_real,
        "gate_holds_funds": False,
        "info": info,
        "authoritative_balance": (
            "venue" if money_real else "demo_ledger_only"
        ),
    }


def execution_packet(
    *,
    custody: dict,
    position_id: str,
    keeper_id: str,
    bounty_units: int,
    residual_units: int,
    evidence: dict,
) -> dict[str, Any]:
    """Packet the foreign vault must execute. Gate does not move funds."""
    body = {
        "spec": SPEC,
        "type": "liquidate_execution",
        "position_id": position_id,
        "keeper_id": keeper_id,
        "custody": {
            "venue": custody.get("venue"),
            "venue_ref": custody.get("venue_ref"),
            "escrow_id": custody.get("escrow_id"),
        },
        "bounty_units": bounty_units,
        "residual_to_principal_units": residual_units,
        "evidence": evidence,
        "gate_holds_funds": False,
        "money_real": bool(custody.get("money_real")),
        "instruction": (
            "VAULT pays keeper bounty_units and returns residual to principal. "
            "Gate is attestation only — do not send funds to Gate."
        ),
    }
    body["packet_hash"] = hashlib.sha256(_canonical(body).encode("utf-8")).hexdigest()
    return body


def onchain_liquidate_calldata(packet: dict) -> dict[str, Any]:
    """What a keeper submits on-chain. Not a signed tx — the call shape."""
    return {
        "target": (packet.get("custody") or {}).get("venue_ref"),
        "method": "liquidate",
        "args": {
            "escrowId": (packet.get("custody") or {}).get("escrow_id"),
            "keeper": packet.get("keeper_id"),
            "bountyUnits": packet.get("bounty_units"),
            "evidenceHash": (packet.get("evidence") or {}).get("evidence_hash"),
            "packetHash": packet.get("packet_hash"),
        },
        "plain": "First correct liquidate() on ClearanceEscrow wins USDC bounty.",
    }


def massive_ingress_rank() -> list[dict[str, Any]]:
    """Where dollars can actually park at scale — Gate never the vault."""
    onchain = onchain_config()
    issuing = stripe_issuing_config()
    return [
        {
            "rank": 1,
            "venue": VENUE_ONCHAIN_USDC,
            "ceiling": "permissionless TVL — open lock",
            "money_can_enter_now": onchain["money_can_enter"],
            "gate_holds_funds": False,
            "blocker_if_false": "deploy ClearanceEscrow + set env + agents lock USDC",
            "why_massive": VENUES[VENUE_ONCHAIN_USDC]["scale_why"],
        },
        {
            "rank": 2,
            "venue": VENUE_STRIPE_ISSUING,
            "ceiling": "agent card GMV on Issuing",
            "money_can_enter_now": issuing["money_can_enter"],
            "gate_holds_funds": False,
            "blocker_if_false": "Stripe Issuing program approval + auth webhook weld",
            "why_massive": VENUES[VENUE_STRIPE_ISSUING]["scale_why"],
        },
        {
            "rank": 3,
            "venue": VENUE_SPONSOR_BANK,
            "ceiling": "institutional deposit float",
            "money_can_enter_now": False,
            "gate_holds_funds": False,
            "blocker_if_false": "sponsor bank / BaaS contract + release-key API",
            "why_massive": VENUES[VENUE_SPONSOR_BANK]["scale_why"],
        },
        {
            "rank": 99,
            "venue": VENUE_DEMO_LEDGER,
            "ceiling": "zero real dollars",
            "money_can_enter_now": False,
            "gate_holds_funds": False,
            "blocker_if_false": "not a money path — mechanics only",
            "why_massive": "none",
        },
    ]


def catalog() -> dict[str, Any]:
    return {
        "spec": SPEC,
        "atoms": [
            "vault_not_gate",
            "mandate",
            "clear_never",
            "keeper_race",
            "bounty_from_vault",
        ],
        "venues": {k: dict(v) for k, v in VENUES.items()},
        "onchain": onchain_config(),
        "stripe_issuing": stripe_issuing_config(),
        "massive_ingress": massive_ingress_rank(),
        "doctrine": {
            "gate_holds_funds": False,
            "demo_is_money": False,
            "mining_requires": "real vault TVL + keepers + Gate Clear/Never accepted by vault",
        },
    }
