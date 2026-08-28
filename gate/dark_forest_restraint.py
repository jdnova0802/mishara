"""Dark Forest Restraint — chain-of-suspicion formalism for bind broadcast.

Fiction: Liu Cixin *The Dark Forest* — civilizations stay silent because any
broadcast reveals position and invites annihilation; chain of suspicion is optimal.

Twist: Publishing bind intent (LIVE hop, ticket hash, premium) without server redeem
proof is a dark-forest broadcast — CHOKE before stick; restraint is the equilibrium.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-dark-forest-restraint-v1"
INVENTION = "Dark Forest Restraint"
TIER = "S"
FAMILY = "s-tier"

REAL = {
    "institution": "Formal game-theoretic derivations of Dark Forest (Liu Cixin 2008)",
    "concept": "Chain of suspicion — any observable signal invites preemption",
    "formal": "Broadcast without mutual verification = dominated strategy",
    "url": "https://en.wikipedia.org/wiki/The_Dark_Forest",
}


def evaluate(
    *,
    broadcast_bind_intent: bool | None = None,
    server_redeem_proved: bool | None = None,
    stranger_verify_url: str | None = None,
    premium_leaked: bool | None = None,
) -> dict[str, Any]:
    broadcast = bool(broadcast_bind_intent or premium_leaked)
    proved = bool(server_redeem_proved and stranger_verify_url)
    if broadcast and not proved:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "tier": TIER,
            "real_institution": REAL,
            "verdict": "DARK_FOREST_BROADCAST",
            "may_stick": False,
            "chain_of_suspicion": True,
            "reason": "bind_intent_observable_without_redeem_proof",
            "equilibrium": "restraint — do not stick until stranger can verify redeem",
        }
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "tier": TIER,
        "real_institution": REAL,
        "verdict": "FOREST_SILENT",
        "may_stick": True,
        "chain_of_suspicion": False,
        "rule": "No broadcast without proof — the forest stays dark until redeem lands.",
    }


def attach(plan: dict) -> dict:
    ghost = (plan.get("ghost_bind") or {}).get("haunted")
    ev = evaluate(
        broadcast_bind_intent=bool(plan.get("verdict") == "LIVE" or plan.get("state") == "LIVE"),
        server_redeem_proved=bool((plan.get("bind_ticket") or {}).get("consumed")),
        stranger_verify_url=plan.get("verify_url"),
        premium_leaked=bool(plan.get("premium") and ghost),
    )
    plan["dark_forest"] = ev
    if ev.get("verdict") == "DARK_FOREST_BROADCAST":
        plan["dark_forest_choke"] = True
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "tier": TIER,
        "one_liner": "Dark Forest chain-of-suspicion — no bind broadcast without redeem proof.",
        "real_institution": REAL,
        "demo": f"POST {base}/demo/pas/dark-forest-restraint",
        "well_known": f"{base}/.well-known/dark-forest-restraint.json",
    }
