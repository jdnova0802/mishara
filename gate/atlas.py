"""Item 136 — MITRE ATLAS technique refs as a *soft* field.

Not written into the signed receipt. Fuzzy/rule classification is not
tamper-evident proof (item 116). A stranger can still hash-verify the
receipt; this layer is 'how we labeled it against a public taxonomy.'
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
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

CLASSIFIERS = ("rule", "llm", "human_analyst")


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _path() -> Path:
    return Path(os.getenv("GATE_ATLAS_PATH") or Path(__file__).resolve().parent / "data" / "atlas.json")


def _load() -> dict[str, Any]:
    path = _path()
    if not path.exists():
        return {"spec": SPEC, "refs": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"spec": SPEC, "refs": []}
    if not isinstance(data, dict):
        return {"spec": SPEC, "refs": []}
    data.setdefault("refs", [])
    return data


def _save(store: dict[str, Any]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")


def list_refs() -> list[dict[str, Any]]:
    return list(_load().get("refs") or [])


def record(
    *,
    receipt_id: str,
    atlas_technique_id: str,
    classified_by: str,
    classification_confidence: Any,
    event_id: str | None = None,
) -> dict[str, Any]:
    tech_id = (atlas_technique_id or "").strip().upper()
    catalog = TECHNIQUES.get(tech_id)
    if catalog is None:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "unknown_technique",
            "allowed": sorted(TECHNIQUES),
            "plain": "Only named ATLAS ids. This mouth does not invent a TTP.",
        }
    who = (classified_by or "").strip().lower()
    if who not in CLASSIFIERS:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "classified_by_unknown",
            "allowed": list(CLASSIFIERS),
            "plain": "classified_by is rule, llm, or human_analyst — shown, not hidden.",
        }
    try:
        conf = float(classification_confidence)
    except (TypeError, ValueError):
        return {"spec": SPEC, "ok": False, "error": "confidence_required", "plain": "classification_confidence is 0.0–1.0."}
    if conf < 0 or conf > 1:
        return {"spec": SPEC, "ok": False, "error": "confidence_range", "plain": "classification_confidence is 0.0–1.0."}
    rid = (receipt_id or "").strip()
    if not rid:
        return {"spec": SPEC, "ok": False, "error": "receipt_required", "plain": "Tag a real receipt_id."}
    rec = {
        "spec": SPEC,
        "ok": True,
        "ref_id": "atlas_" + uuid.uuid4().hex[:12],
        "receipt_id": rid,
        "event_id": (event_id or "").strip() or None,
        "atlas_tactic_id": catalog["atlas_tactic_id"],
        "atlas_technique_id": catalog["atlas_technique_id"],
        "name": catalog["name"],
        "classification_confidence": conf,
        "classified_by": who,
        "classified_at": _now_iso(),
        "evidentiary_weight": EVIDENTIARY_WEIGHT,
        "hard_binding": False,
        "plain": "Soft ATLAS label. Hash-verify the receipt separately.",
    }
    store = _load()
    store["refs"].append(rec)
    _save(store)
    return rec


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
    rid = event.get("receipt_hash") or event.get("id")
    stored = [r for r in list_refs() if r.get("receipt_id") == rid or r.get("event_id") == event.get("id")]
    body["human_refs"] = stored
    return 200, body
