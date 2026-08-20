"""Controls mapping — PFMI / NAIC / EU Art 12 → receipt fields."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-controls-map-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Controls mapping",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "disclaimer": "Mapping for evaluation — not certification or legal advice.",
        "frameworks": {
            "pfmi": {
                "P12_dvp": {
                    "requirement": "Settlement legs linked or abort",
                    "gate_artifact": "dvp-mouth.json + PERMIT/DENY at hop",
                    "receipt_fields": ["decision", "acted", "instruction_finality"],
                },
                "P17_operational_risk": {
                    "requirement": "Operational risk evidence at decision time",
                    "gate_artifact": "fmi-p17.json receipt attachment",
                    "receipt_fields": ["fmi_p17", "verify_url", "created_at"],
                },
            },
            "naic_ai_evaluation": {
                "decision_point_receipt": {
                    "requirement": "Proof at moment of agent/bind action",
                    "gate_artifact": "counterfactual-spend.json + bind-check",
                    "receipt_fields": ["counterfactual_spend", "verify_url", "event_id"],
                },
                "officer_pack": f"{base}/bind-room/officer-pack.json",
            },
            "eu_ai_act_art12": {
                "logging": {
                    "requirement": "Automatic logging of model/agent decisions",
                    "gate_artifact": "receipt/{{event_id}}.json + evidence-head",
                    "receipt_fields": ["decision", "receipt_hash", "verify_url"],
                },
            },
        },
        "comparison": {
            "agent_observability": "Gate is pre-commit mouth — not post-hoc traces",
            "pas_workflow": "Gate is PERMIT/DENY before bind-only — not UW workflow",
            "ccp": "Gate filters gross before net — does not replace finality III",
        },
        "proof_suite": f"{base}/.well-known/proof-suite.json",
    }
