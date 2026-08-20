"""Production skin — what ships vs what is moat. Central their_production gate."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

SPEC = "gate-production-skin-v1"
INVENTOR = "Nisaba LLC / Gate"

CANONICAL_SENTENCE = (
    "We do not replace your net. We clear the irreversible instruction before it "
    "becomes your exception queue."
)

CANONICAL_SENTENCE_DOOR = (
    "Irreversible spend does not complete unless this layer says yes — one welded door, "
    "fail closed on DEAD."
)

CANONICAL_SENTENCE_CHARGE = (
    "DEAD→LIVE only via unforgeable CHARGE — UW approve without CHARGE does not resurrect."
)

# Runtime beyond well-known JSON
SHIPPED_RUNTIME = frozenset(
    {
        "mouth_constitution",
        "costliness",
        "fulfillment",
        "variety",
        "closure",
        "temporal_weld",
        "nonrepudiation",
        "regime_function",
        "custody",
        "possibility_finality",
        "counterfactual",
        "post_trade_distribution",
        "instruction_finality",
        "pre_net_clearance",
        "dvp_mouth",
        "ssi_preauth",
        "stack_propagation",
        "settlement",
        "restraint",
        "license_fuse",
        "spend_protocol",
        "commit_auth",
        "monolith",
        "moat",
    }
)

RECEIPT_ATTACHED = frozenset(
    {
        "mouth_constitution",
        "bayesian_binding",
        "temporal_weld",
        "fulfillment",
        "nonrepudiation",
        "option_halt",
        "performative",
        "custody",
        "hyperobject",
        "complementarity",
        "irreversibility_horizon",
        "semiotics",
        "antifragile_halt",
        "agential_cut",
        "prehension",
        "mouth_isa",
        "event_horizon",
        "stranger_antenna",
        "nmi_halt",
        "landauer",
        "holographic",
        "curry_howard",
        "superselection",
        "unlanguage",
        "instruction_finality",
        "fmi_p17",
        "possibility_finality",
    }
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def their_production() -> bool:
    """True when Gate has a real production weld (env or recorded dogfood)."""
    flag = os.getenv("GATE_PRODUCTION_WELDED", "").strip().lower()
    if flag in ("1", "true", "yes", "on"):
        return True
    try:
        from gate import db as gate_db
    except ImportError:
        import db as gate_db  # type: ignore[no-redef]
    return gate_db.has_gate_production_weld()


def classify_spec(spec_id: str) -> str:
    if spec_id in RECEIPT_ATTACHED and spec_id in SHIPPED_RUNTIME:
        return "shipped+receipt"
    if spec_id in RECEIPT_ATTACHED:
        return "receipt-attached"
    if spec_id in SHIPPED_RUNTIME:
        return "shipped"
    return "doctrine-only"


def spec_classification(public_url: str) -> dict[str, Any]:
    try:
        from gate import inventions as inventions_mod
    except ImportError:
        import inventions as inventions_mod  # type: ignore[no-redef]

    base = (public_url or "").rstrip("/")
    entries = []
    counts = {"shipped": 0, "shipped+receipt": 0, "receipt-attached": 0, "doctrine-only": 0}
    for inv_id, name, spec, one_liner, filename in inventions_mod.CATALOG:
        tier = classify_spec(inv_id)
        counts[tier] = counts.get(tier, 0) + 1
        entries.append(
            {
                "id": inv_id,
                "name": name,
                "spec": spec,
                "tier": tier,
                "href": f"{base}/.well-known/{filename}" if base else None,
                "one_liner": one_liner,
            }
        )
    return {
        "spec": "gate-spec-classification-v1",
        "evaluated_at": _now(),
        "counts": counts,
        "total": len(entries),
        "public_face_only": ["door", "charge", "distribution"],
        "entries": entries,
    }


def pillar_map(public_url: str) -> list[dict[str, Any]]:
    base = (public_url or "").rstrip("/")
    return [
        {
            "pillar": "door",
            "name": "Exclusive door",
            "canonical": CANONICAL_SENTENCE_DOOR,
            "routes": {
                "html": [f"{base}/operator", f"{base}/register", f"{base}/only"],
                "api": [f"{base}/v1/pas/bind-check", f"{base}/v1/pas/policycenter/pre-bind"],
                "manifest": f"{base}/.well-known/monolith.json",
            },
            "modules": ["weld.py", "fields.py", "license_fuse.py", "operator_invoice.py"],
            "receipt_fields": [
                "decision",
                "acted",
                "verify_url",
                "counterfactual_spend",
                "intervention",
                "counts_as",
            ],
            "proof": f"POST {base}/demo/pas/bind-check → verify_url in response",
        },
        {
            "pillar": "charge",
            "name": "CHARGE port",
            "canonical": CANONICAL_SENTENCE_CHARGE,
            "routes": {
                "html": [f"{base}/for/charge"],
                "api": [f"{base}/v1/fuse/lookup"],
                "manifest": f"{base}/.well-known/costliness.json",
            },
            "modules": ["costliness.py", "license_fuse.py", "closure.py", "epoch.py"],
            "receipt_fields": ["charge_id", "complementarity", "landauer", "agential_cut"],
            "proof": "closure.classify_operation('uw_approve_without_charge') → not in network",
        },
        {
            "pillar": "distribution",
            "name": "Distribution stack",
            "canonical": CANONICAL_SENTENCE,
            "routes": {
                "html": [f"{base}/for/post-trade"],
                "api": [],
                "manifest": f"{base}/.well-known/distribution.json",
            },
            "modules": [
                "distribution.py",
                "settlement.py",
                "instruction_finality.py",
                "pre_net.py",
                "fmi_p17.py",
            ],
            "receipt_fields": ["instruction_finality", "fmi_p17", "policy_depth"],
            "proof": f"{base}/.well-known/settlement.json finality hash",
        },
    ]


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    prod = their_production()
    classification = spec_classification(base)
    return {
        "spec": SPEC,
        "name": "Production skin",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "their_production": prod,
        "canonical_sentences": {
            "distribution": CANONICAL_SENTENCE,
            "door": CANONICAL_SENTENCE_DOOR,
            "charge": CANONICAL_SENTENCE_CHARGE,
        },
        "pillars": pillar_map(base),
        "classification_summary": classification["counts"],
        "classification": f"{base}/.well-known/spec-classification.json" if base else None,
        "proof_suite": f"{base}/.well-known/proof-suite.json" if base else None,
        "runbook": f"{base}/.well-known/runbook.json" if base else None,
        "scorecard": f"{base}/.well-known/scorecard.json" if base else None,
        "page": f"{base}/production-skin" if base else None,
        "flip_production": (
            "Set GATE_PRODUCTION_WELDED=1 after real weld, or POST /ops/dogfood-weld with GATE_OPS_TOKEN."
        ),
    }
