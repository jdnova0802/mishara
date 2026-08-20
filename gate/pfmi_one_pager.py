"""PFMI one-pager — where Gate sits vs finality I/II/III."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-pfmi-one-pager-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "PFMI placement",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "one_sentence": (
            "We do not replace your net. We clear the irreversible instruction before it "
            "becomes your exception queue."
        ),
        "sequence": [
            {
                "step": 1,
                "who": "Intermediary / operator",
                "event": "Irreversible instruction formed (bind-only, payout, withdraw)",
                "gate": "Pre-net clearance · SSI-preauth equivalent at hop",
            },
            {
                "step": 2,
                "who": "Gate mouth",
                "event": "Instruction finality at hop — PERMIT/DENY + receipt",
                "gate": "Fail-closed HALT/BLOCK with stranger verify",
            },
            {
                "step": 3,
                "who": "Clearing member",
                "event": "Gross admitted to settlement window",
                "gate": "Pre-net filter — exceptions never enter CNS",
            },
            {
                "step": 4,
                "who": "FMI apex (DTCC peers)",
                "event": "Netting · CNS · finality III",
                "gate": "Reference PFMI manifests only — net unchanged",
            },
        ],
        "pfmi_mapping": {
            "P12_dvp": f"{base}/.well-known/dvp-mouth.json",
            "P17_operational_risk": f"{base}/.well-known/fmi-p17.json",
            "finality_I": "Possibility — instruction can still HALT at hop",
            "finality_II": "Instruction finality — receipt welded at hop",
            "finality_III": "Settlement finality — your CSD/CCP (unchanged)",
        },
        "not": ["CCP replacement", "ALERT clone", "blockchain settlement cosplay"],
        "distribution": f"{base}/.well-known/distribution.json",
        "settlement": f"{base}/.well-known/settlement.json",
    }
