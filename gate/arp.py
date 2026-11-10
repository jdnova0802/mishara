"""Item 25 — dated Agent Receipt Protocol v0.1."""
from __future__ import annotations

from pathlib import Path
from typing import Any

SPEC = "agent-receipt-protocol-v0.1"
DATED = "2026-11-10"
MARKDOWN = Path(__file__).resolve().parent.parent / "docs" / "spec" / "agent-receipt-protocol-v0.1.md"


def manifest(public_url: str) -> dict[str, Any]:
    base = public_url.rstrip("/")
    return {
        "spec": SPEC,
        "dated": DATED,
        "status": "draft",
        "publisher": "Nisaba LLC",
        "markdown": f"{base}/spec/agent-receipt-protocol/v0.1.md",
        "json": f"{base}/.well-known/agent-receipt-protocol.json",
        "verify_template": f"{base}/.well-known/receipt/{{event_id}}.json",
        "badge_template": f"{base}/badge/verify.svg?event_id={{event_id}}",
        "cli": "python3 gate/offline_verify.py <receipt.json>",
        "mcp_tool": "verify_receipt",
        "hash_algorithm": "SHA-256",
        "signature": "Ed25519",
        "envelope_outside_hash": [
            "receipt_hash",
            "receipt_signature",
            "receipt_public_key_fingerprint",
            "dfir",
        ],
        "not_in_v0_1": [
            "parametric_insurance_triggers",
            "zero_knowledge_linkage",
            "computer_vision_authenticity",
        ],
    }


def markdown() -> str:
    if MARKDOWN.exists():
        return MARKDOWN.read_text(encoding="utf-8")
    return f"# {SPEC}\nDated {DATED}. Draft.\n"
