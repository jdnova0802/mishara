"""Item 136 — MITRE ATLAS technique refs as a *soft* field.

Not written into the signed receipt. Fuzzy/rule classification is not
tamper-evident proof (item 116). A stranger can still hash-verify the
receipt; this layer is 'how we labeled it against a public taxonomy.'
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-atlas-ref-v1"
EVIDENTIARY_WEIGHT = "CORROBORATING_ONLY"

# Documented ATLAS ids (ATT&CK-style). Rule matches only; classified_by=rule.
TECHNIQUES = {
    "AML.T0043": {
        "atlas_tactic_id": "AML.TA0001",
        "atlas_technique_id": "AML.T0043",
        "name": "Craft Adversarial Data",
        "tokens": ("adversarial", "jailbreak", "prompt injection", "crafted input"),
    },
    "AML.T0015": {
        "atlas_tactic_id": "AML.TA0003",
        "atlas_technique_id": "AML.T0015",
        "name": "Evade ML Model",
        "tokens": ("evade", "bypass", "threshold", "near-threshold", "sub-threshold"),
    },
    "AML.T0040": {
        "atlas_tactic_id": "AML.TA0002",
        "atlas_technique_id": "AML.T0040",
        "name": "ML Supply Chain Compromise",
        "tokens": ("supply chain", "weights", "checkpoint", "model lineage"),
    },
    "AML.T0048": {
        "atlas_tactic_id": "AML.TA0002",
        "atlas_technique_id": "AML.T0048",
        "name": "Backdoor ML Model",
        "tokens": ("backdoor", "poison", "data poisoning"),
    },
}


def _blob(event: dict[str, Any]) -> str:
    hop = event.get("hop") if isinstance(event.get("hop"), dict) else {}
    parts = [
        str(event.get("decision") or ""),
        str(event.get("fuse_id") or ""),
        str(hop.get("reason") or hop.get("epoch_reason") or ""),
        str(hop.get("state") or ""),
    ]
    return " ".join(parts).lower()


def classify_event(event: dict[str, Any]) -> dict[str, Any]:
    blob = _blob(event)
    hits = []
    for tech in TECHNIQUES.values():
        matched = [t for t in tech["tokens"] if t in blob]
        if not matched:
            continue
        hits.append(
            {
                "atlas_tactic_id": tech["atlas_tactic_id"],
                "atlas_technique_id": tech["atlas_technique_id"],
                "name": tech["name"],
                "matched_tokens": matched,
                "classification_confidence": min(0.45 + 0.15 * len(matched), 0.9),
            }
        )
    hits.sort(key=lambda h: h["classification_confidence"], reverse=True)
    chosen = hits[0] if hits else None
    return {
        "spec": SPEC,
        "ref_id": f"atlas:{(event.get('receipt_hash') or event.get('id') or 'unknown')}",
        "receipt_id": event.get("receipt_hash") or event.get("id"),
        "event_id": event.get("id"),
        "classified_by": "rule",
        "classified_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "evidentiary_weight": EVIDENTIARY_WEIGHT,
        "hard_binding": False,
        "atlas": chosen,
        "candidates": hits,
        "note": "Soft label. Hash-verify the receipt separately. Unknown BLOCK is unlabeled, not 'suspicious pattern.'",
    }


def classify_or_404(event: dict[str, Any] | None) -> tuple[int, dict[str, Any]]:
    if not event:
        return 404, {"ok": False, "error": "event_not_found"}
    body = classify_event(event)
    body["ok"] = True
    return 200, body
