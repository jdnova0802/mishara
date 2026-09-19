"""Oracle Compiler v0 — claim/source → oracle class (Nisaba / Gate artifact).

NOT a sister company. Companion to Finality Compiler.
Oracle = anything that imports an outside claim so an irreversible write can fire.

Surfaces:
  GET  /.well-known/oracle-compiler.json
  POST /demo/oracle/classify
  POST /v1/oracle/classify
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-oracle-compiler-v0"
FIRM = "Nisaba LLC"
CARD = (
    "On-card Gate artifact. Upstream of Finality Compiler + Prefinality. "
    "Does not rename the firm. No bounty gym. No sister brand."
)

CLASSES = (
    "LIVE_HARD",  # fresh, bound, stranger-checkable enough to gate leave
    "LIVE_SOFT",  # usable but return/manipulation/soft window remains
    "STALE",  # value present; age exceeds heartbeat / policy
    "UNSIGNED",  # claim exists without attributable attestation
    "MANIPULABLE_LOCAL",  # local market / single-writer / spot path
    "FAIL_OPEN",  # missing/timeout treated as allow — critical mouth
    "UNKNOWN",
)

LEAVE_HINT = {
    "LIVE_HARD": "Claim may gate leave only if Clear also binds policy+intent at T.",
    "LIVE_SOFT": "Soft claim — require stronger Clear or deny high-stakes leave.",
    "STALE": "Fail closed. Presence of a value is not authority at T.",
    "UNSIGNED": "Fail closed. No attributable attestation → no may.",
    "MANIPULABLE_LOCAL": "Fail closed for leave. Local spot is not stranger-hard truth.",
    "FAIL_OPEN": "Critical mouth: timeout/missing claim must not authorize write.",
    "UNKNOWN": "Fail closed. No may → no leave.",
}

# (claim_type, source_normalized) → class
TAXONOMY: dict[tuple[str, str], str] = {
    # Price / DeFi-shaped (commercial map only — not bounty gym)
    ("price", "push_feed_fresh"): "LIVE_SOFT",
    ("price", "push_feed_stale"): "STALE",
    ("price", "spot_amm"): "MANIPULABLE_LOCAL",
    ("price", "twap_long"): "LIVE_SOFT",
    ("price", "missing"): "FAIL_OPEN",
    # Event / webhook oracles (software money)
    ("event", "webhook_unsigned"): "UNSIGNED",
    ("event", "webhook_signed"): "LIVE_SOFT",
    ("event", "provider_poll_reconciled"): "LIVE_HARD",
    ("event", "timeout_allow"): "FAIL_OPEN",
    ("event", "payment_succeeded"): "LIVE_SOFT",
    ("event", "payout_paid"): "LIVE_SOFT",
    # Identity
    ("identity", "kyc_decision"): "LIVE_SOFT",
    ("identity", "kyc_unsigned"): "UNSIGNED",
    ("identity", "stale_approval"): "STALE",
    # Availability
    ("availability", "sequencer_up"): "LIVE_SOFT",
    ("availability", "sequencer_down"): "STALE",
    ("availability", "unchecked"): "FAIL_OPEN",
    # Bridge / message
    ("message", "light_client"): "LIVE_HARD",
    ("message", "trusted_relay"): "LIVE_SOFT",
    ("message", "unsigned_relay"): "UNSIGNED",
    # Human / bind
    ("human", "officer_signed"): "LIVE_HARD",
    ("human", "checkbox"): "UNSIGNED",
    # Enterprise agent tool gates
    ("agent_tool", "human_approval_required"): "LIVE_HARD",
    ("agent_tool", "external_allow"): "LIVE_SOFT",
    ("agent_tool", "timeout_default_allow"): "FAIL_OPEN",
    ("agent_tool", "prompt_only"): "UNSIGNED",
    # Inference-as-oracle
    ("inference", "model_output"): "UNSIGNED",
    ("inference", "grounded_deterministic"): "LIVE_SOFT",
    ("inference", "ungrounded"): "MANIPULABLE_LOCAL",
}


def _norm(s: Any) -> str:
    return str(s or "").strip().lower().replace(" ", "_").replace("-", "_")


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "firm": FIRM,
        "name": "Oracle Compiler",
        "version": "0",
        "card": CARD,
        "job": (
            "Classify a claim_type+source into an oracle class so external "
            "claims are not mistaken for Clear/may on irreversible writes."
        ),
        "classes": list(CLASSES),
        "leave_hint": LEAVE_HINT,
        "taxonomy_rows": len(TAXONOMY),
        "pairs_with": ["gate-finality-compiler-v0", "gate-prefinality-v1"],
        "inventions_adjacent": [
            "clear_at_t_bind",
            "webhook_as_oracle_pack",
            "identity_oracle_mouth",
            "fail_closed_oracle_death",
            "inference_as_oracle_gate",
        ],
        "urls": {
            "well_known": f"{base}/.well-known/oracle-compiler.json",
            "demo_classify": f"{base}/demo/oracle/classify",
            "classify": f"{base}/v1/oracle/classify",
            "finality_compiler": f"{base}/.well-known/finality-compiler.json",
            "diligence": f"{base}/diligence",
        },
        "not": [
            "Not a sister company",
            "Not a pentest / bounty gym",
            "Not price manipulation tooling",
            "Not legal advice",
        ],
    }


def classify(
    *,
    claim_type: str | None = None,
    source: str | None = None,
    age_seconds: float | None = None,
    heartbeat_seconds: float | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    ct = _norm(claim_type) or "event"
    src = _norm(source)

    oracle_class = TAXONOMY.get((ct, src), "UNKNOWN")
    if oracle_class == "UNKNOWN" and src:
        for key in (ct, "event"):
            hit = TAXONOMY.get((key, src))
            if hit:
                oracle_class = hit
                ct = key
                break

    # Age override: if heartbeat known and age exceeds it → STALE
    if (
        age_seconds is not None
        and heartbeat_seconds is not None
        and heartbeat_seconds > 0
        and age_seconds > heartbeat_seconds
        and oracle_class in ("LIVE_HARD", "LIVE_SOFT", "UNKNOWN")
    ):
        oracle_class = "STALE"

    return {
        "spec": SPEC,
        "firm": FIRM,
        "input": {
            "claim_type": ct,
            "source": src or None,
            "age_seconds": age_seconds,
            "heartbeat_seconds": heartbeat_seconds,
            "notes": notes,
        },
        "oracle_class": oracle_class,
        "leave_hint": LEAVE_HINT.get(oracle_class, LEAVE_HINT["UNKNOWN"]),
        "may_ok_for_leave": oracle_class == "LIVE_HARD",
        "fail_closed_required": oracle_class
        in ("STALE", "UNSIGNED", "MANIPULABLE_LOCAL", "FAIL_OPEN", "UNKNOWN"),
        "card_note": "Artifact for H1 maps + Prefinality. Not a new firm.",
    }


def taxonomy_table() -> list[dict[str, str]]:
    rows = []
    for (claim_type, source), cls in sorted(TAXONOMY.items()):
        rows.append(
            {
                "claim_type": claim_type,
                "source": source,
                "oracle_class": cls,
                "leave_hint": LEAVE_HINT[cls],
            }
        )
    return rows
