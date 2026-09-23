"""Human-facing clearance labels over rail truth + deny registry.

Apple-simple words. Same atoms underneath.
"""

from __future__ import annotations

from typing import Any

try:
    from gate import rail_truth as rail_truth_mod
except ImportError:
    import rail_truth as rail_truth_mod

try:
    from gate import deny_registry as deny_mod
except ImportError:
    import deny_registry as deny_mod

SPEC = "gate-clear-v1"

# Map agent_safe_default → one consumable word for states / civilians.
STATUS_MAP = {
    "treat_as_reversible_until_return_window_closed": {
        "word": "REVERSIBLE",
        "plain": "Can often still be pulled back for a while.",
    },
    "treat_as_hard_to_unwind_after_accept": {
        "word": "HARD TO UNWIND",
        "plain": "Once accepted, getting it back is the exception.",
    },
    "treat_as_final_after_accept": {
        "word": "FINAL",
        "plain": "Treat as done after the bank accepts it.",
    },
    "treat_as_reversible_via_chargeback_until_window_closed": {
        "word": "REVERSIBLE",
        "plain": "Disputes can unwind it until the window closes.",
    },
    "treat_as_ledger_final_after_N_confirmations_issuer_risk_remains": {
        "word": "LEDGER FINAL",
        "plain": "On-chain it’s done; the issuer can still intervene.",
    },
    "resolve_underlying_rail_then_apply_that_finality": {
        "word": "DEPENDS",
        "plain": "Follow whatever rail actually settles underneath.",
    },
}

LOSS_MAP = {
    "originator_heavy": "Usually the side that sent it.",
    "payer_instruction_heavy": "Usually whoever approved the instruction.",
    "reason_code_split": "Splits by dispute reason — merchant or issuer.",
    "signer_heavy": "Usually whoever held the key / signed.",
    "inherits_underlying": "Same as the rail underneath.",
}


def clear_rail(rail: str) -> dict[str, Any] | None:
    row = rail_truth_mod.lookup(rail)
    if not row:
        return None
    fin = row["finality"]
    loss = row["loss"]
    status = STATUS_MAP.get(
        fin.get("agent_safe_default") or "",
        {"word": "UNKNOWN", "plain": "No simple label for this rail yet."},
    )
    return {
        "spec": SPEC,
        "rail": row["rail"],
        "name": fin.get("name") or row["rail"],
        "word": status["word"],
        "plain": status["plain"],
        "who_eats_loss": LOSS_MAP.get(
            loss.get("machine_label") or "",
            loss.get("rail_default_eater") or "See rail rules.",
        ),
        "settle_speed": fin.get("typical_settle"),
        "their_production": False,
        "atoms": {
            "finality": f"/v1/rail-truth/{row['rail']}/finality",
            "loss": f"/v1/rail-truth/{row['rail']}/loss",
        },
    }


def clear_deny(payout_hash: str) -> dict[str, Any]:
    hit = deny_mod.lookup(payout_hash)
    denied = bool(hit.get("denied"))
    return {
        "spec": SPEC,
        "payout_hash": hit.get("payout_hash"),
        "word": "DENIED" if denied else "NOT DENIED",
        "plain": (
            "A deny is on record for this payout fingerprint."
            if denied
            else "No deny on record for this fingerprint."
        ),
        "count": hit.get("count") or 0,
        "their_production": False,
    }


def rails_for_ui() -> list[dict[str, str]]:
    out = []
    for key in rail_truth_mod.list_rails()["rails"]:
        c = clear_rail(key)
        if c:
            out.append({"id": key, "name": c["name"], "word": c["word"]})
    return out


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Clear",
        "promise": "One word. Will this settle — and can it come back?",
        "page": f"{base}/clear",
        "api": f"{base}/v1/clear",
        "rails": [r["id"] for r in rails_for_ui()],
        "their_production": False,
    }
