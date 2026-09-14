"""Finality Compiler v0 — status/rail → finality class (Nisaba / Gate artifact).

NOT a sister company. Same mouth as diligence + Prefinality.
Maps software money "success" strings to rail finality so H1 finds
and Clear decisions do not confuse webhook receipts with leave finality.

Surfaces:
  GET  /.well-known/finality-compiler.json
  POST /demo/finality/classify
  POST /v1/finality/classify
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-finality-compiler-v0"
FIRM = "Nisaba LLC"
CARD = (
    "On-card Gate artifact. Funds H1 mouth maps; sharpens Prefinality. "
    "Does not rename the firm. No bounty gym. No sister brand."
)

# Atomic finality classes — ordered soft → hard
CLASSES = (
    "SOFTWARE_RECEIPT",  # webhook/API object said something; rail may not have left
    "AUTHORIZED_HOLD",  # auth/hold; not capture; not settlement
    "CAPTURED_OR_POSTED",  # merchant/processor posted; still soft-final on many rails
    "NETWORK_SETTLED_SOFT",  # settled-ish but return/chargeback window open (ACH/card)
    "RAIL_FINAL_HARD",  # accept/settlement irrevocable on rail (e.g. RTP credit push)
    "UNKNOWN",  # cannot classify — fail closed for may decisions
)

REVERSIBILITY = {
    "SOFTWARE_RECEIPT": "high",
    "AUTHORIZED_HOLD": "high",
    "CAPTURED_OR_POSTED": "medium",
    "NETWORK_SETTLED_SOFT": "medium_low",
    "RAIL_FINAL_HARD": "near_zero",
    "UNKNOWN": "unknown",
}

# Seed taxonomy: (rail, status_normalized) → class
# Extend in diligence deliveries; this is the inventable spine.
TAXONOMY: dict[tuple[str, str], str] = {
    # Generic / processor object language
    ("processor", "created"): "SOFTWARE_RECEIPT",
    ("processor", "pending"): "SOFTWARE_RECEIPT",
    ("processor", "processing"): "SOFTWARE_RECEIPT",
    ("processor", "requires_action"): "SOFTWARE_RECEIPT",
    ("processor", "requires_capture"): "AUTHORIZED_HOLD",
    ("processor", "requires_confirmation"): "SOFTWARE_RECEIPT",
    ("processor", "succeeded"): "CAPTURED_OR_POSTED",
    ("processor", "paid"): "CAPTURED_OR_POSTED",
    ("processor", "in_transit"): "CAPTURED_OR_POSTED",
    ("processor", "canceled"): "SOFTWARE_RECEIPT",
    ("processor", "failed"): "SOFTWARE_RECEIPT",
    # Card
    ("card", "authorized"): "AUTHORIZED_HOLD",
    ("card", "auth"): "AUTHORIZED_HOLD",
    ("card", "captured"): "CAPTURED_OR_POSTED",
    ("card", "settled"): "NETWORK_SETTLED_SOFT",
    ("card", "chargeback_open"): "NETWORK_SETTLED_SOFT",
    # ACH
    ("ach", "initiated"): "SOFTWARE_RECEIPT",
    ("ach", "pending"): "SOFTWARE_RECEIPT",
    ("ach", "processed"): "CAPTURED_OR_POSTED",
    ("ach", "settled"): "NETWORK_SETTLED_SOFT",
    ("ach", "returned"): "SOFTWARE_RECEIPT",
    # RTP / hard credit push
    ("rtp", "accepted"): "RAIL_FINAL_HARD",
    ("rtp", "accept"): "RAIL_FINAL_HARD",
    ("rtp", "accept_without_posting"): "RAIL_FINAL_HARD",
    ("rtp", "rejected"): "SOFTWARE_RECEIPT",
    # Payout / leave
    ("payout", "pending"): "SOFTWARE_RECEIPT",
    ("payout", "in_transit"): "CAPTURED_OR_POSTED",
    ("payout", "paid"): "NETWORK_SETTLED_SOFT",
    ("payout", "failed"): "SOFTWARE_RECEIPT",
    ("payout", "canceled"): "SOFTWARE_RECEIPT",
    # Crypto withdraw / peg-out (treat broadcast≠final unless confirmed)
    ("withdraw", "requested"): "SOFTWARE_RECEIPT",
    ("withdraw", "broadcast"): "CAPTURED_OR_POSTED",
    ("withdraw", "confirmed"): "RAIL_FINAL_HARD",
    ("withdraw", "finalized"): "RAIL_FINAL_HARD",
    ("pegout", "requested"): "SOFTWARE_RECEIPT",
    ("pegout", "minted_burned"): "CAPTURED_OR_POSTED",
    ("pegout", "released"): "RAIL_FINAL_HARD",
    # BaaS / ledger (Synapse-class caution)
    ("baas_ledger", "available"): "SOFTWARE_RECEIPT",
    ("baas_ledger", "posted"): "SOFTWARE_RECEIPT",
    ("baas_ledger", "bank_reconciled"): "NETWORK_SETTLED_SOFT",
}


def _norm(s: Any) -> str:
    return str(s or "").strip().lower().replace(" ", "_").replace("-", "_")


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "firm": FIRM,
        "name": "Finality Compiler",
        "version": "0",
        "card": CARD,
        "job": (
            "Classify a rail+status into a finality class so software receipts "
            "are not mistaken for irreversible leave."
        ),
        "classes": list(CLASSES),
        "reversibility": REVERSIBILITY,
        "taxonomy_rows": len(TAXONOMY),
        "inventions_adjacent": [
            "dual_ledger_clear",
            "stage_bound_may",
            "command_intent_lock",
            "omnibus_exit_prove",
            "platform_key_mouth_map",
        ],
        "urls": {
            "well_known": f"{base}/.well-known/finality-compiler.json",
            "demo_classify": f"{base}/demo/finality/classify",
            "classify": f"{base}/v1/finality/classify",
            "diligence": f"{base}/diligence",
            "prefinality": f"{base}/.well-known/prefinality.json",
        },
        "not": [
            "Not a sister company",
            "Not a pentest gym",
            "Not settlement execution",
            "Not legal advice",
        ],
    }


def classify(
    *,
    rail: str | None = None,
    status: str | None = None,
    raw_event: str | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    """Fail soft to UNKNOWN — Prefinality should treat UNKNOWN as no-may."""
    r = _norm(rail) or "processor"
    s = _norm(status)
    if not s and raw_event:
        s = _norm(raw_event)

    finality_class = TAXONOMY.get((r, s), "UNKNOWN")
    if finality_class == "UNKNOWN" and s:
        # soft fallback: common verbs across rails
        for rail_key in (r, "processor"):
            hit = TAXONOMY.get((rail_key, s))
            if hit:
                finality_class = hit
                r = rail_key
                break

    may_before_leave = finality_class in (
        "SOFTWARE_RECEIPT",
        "AUTHORIZED_HOLD",
        "CAPTURED_OR_POSTED",
        "NETWORK_SETTLED_SOFT",
        "UNKNOWN",
    )
    # HARD final still wants may *before* the accept — after accept, may is too late
    stranger_halt_relevant = finality_class != "RAIL_FINAL_HARD"

    return {
        "spec": SPEC,
        "firm": FIRM,
        "input": {
            "rail": r,
            "status": s or None,
            "raw_event": raw_event,
            "notes": notes,
        },
        "finality_class": finality_class,
        "reversibility": REVERSIBILITY.get(finality_class, "unknown"),
        "may_still_meaningful": may_before_leave or finality_class == "RAIL_FINAL_HARD",
        "stranger_halt_after_this_status": stranger_halt_relevant,
        "leave_risk": {
            "SOFTWARE_RECEIPT": "Treat as non-final. Do not unlock downstream irreversible leave.",
            "AUTHORIZED_HOLD": "Hold only. Capture/payout needs separate Clear.",
            "CAPTURED_OR_POSTED": "Posted in software — confirm rail class before treating as left.",
            "NETWORK_SETTLED_SOFT": "Settled with return/chargeback path — soft finality.",
            "RAIL_FINAL_HARD": "Rail-final. May must precede accept; after is recovery not halt.",
            "UNKNOWN": "Fail closed. No may → no leave.",
        }.get(finality_class, "Fail closed."),
        "card_note": "Artifact for H1 maps + Prefinality. Not a new firm.",
    }


def taxonomy_table() -> list[dict[str, str]]:
    rows = []
    for (rail, status), cls in sorted(TAXONOMY.items()):
        rows.append(
            {
                "rail": rail,
                "status": status,
                "finality_class": cls,
                "reversibility": REVERSIBILITY[cls],
            }
        )
    return rows
