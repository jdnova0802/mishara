"""Item 120 — Mishara three-tier harm split, after Thorn.

exact-match hash may auto-act. Predictive classifier is human-only.
Provenance/watermark is orthogonal: is this generated, not is this abusive.
No hash DB and no classifier ship in this checkout.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-harm-tiers-v1"

EXACT_MATCH = "exact_match"
CLASSIFIER = "classifier"
PROVENANCE = "provenance"
TIERS = (EXACT_MATCH, CLASSIFIER, PROVENANCE)

AUTO = "AUTO"
HUMAN = "HUMAN"
ORTHOGONAL = "ORTHOGONAL"


def normalize(tier: str | None) -> str | None:
    raw = (tier or "").strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "hash": EXACT_MATCH,
        "exact": EXACT_MATCH,
        "exact_match_hash": EXACT_MATCH,
        "predictive": CLASSIFIER,
        "model": CLASSIFIER,
        "watermark": PROVENANCE,
        "c2pa": PROVENANCE,
        "ai_generated": PROVENANCE,
    }
    mapped = aliases.get(raw, raw)
    return mapped if mapped in TIERS else None


def classify(
    *,
    tier: str | None,
    auto_act: bool = False,
    match_hash: str | None = None,
) -> dict[str, Any]:
    named = normalize(tier)
    if named is None:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "tier_required",
            "tier": None,
            "disposition": None,
            "auto_act": False,
            "plain": "Name exact_match, classifier, or provenance. One flat 'harm detected' is refused.",
        }

    requested = bool(auto_act)
    if named == EXACT_MATCH:
        hashed = bool((match_hash or "").strip())
        if requested and not hashed:
            return {
                "spec": SPEC,
                "ok": False,
                "error": "exact_match_hash_required",
                "tier": named,
                "disposition": HUMAN,
                "auto_act": False,
                "never_auto_act_on_classifier_only": True,
                "plain": "Exact-match auto-act needs a hash. There is no hash DB on this mouth yet.",
            }
        disposition = AUTO if requested and hashed else HUMAN
        return {
            "spec": SPEC,
            "ok": True,
            "tier": named,
            "disposition": disposition,
            "auto_act": disposition == AUTO,
            "never_auto_act_on_classifier_only": True,
            "match_hash_present": hashed,
            "plain": (
                "Exact-match hash may auto-act."
                if disposition == AUTO
                else "Exact-match tier, no auto-act on this row."
            ),
        }

    if named == CLASSIFIER:
        if requested:
            return {
                "spec": SPEC,
                "ok": False,
                "error": "classifier_never_auto_act",
                "tier": named,
                "disposition": HUMAN,
                "auto_act": False,
                "never_auto_act_on_classifier_only": True,
                "plain": "Classifier-only never auto-acts. Human review only.",
            }
        return {
            "spec": SPEC,
            "ok": True,
            "tier": named,
            "disposition": HUMAN,
            "auto_act": False,
            "never_auto_act_on_classifier_only": True,
            "plain": "Predictive classifier: flagged for a human. Not auto-acted.",
        }

    return {
        "spec": SPEC,
        "ok": True,
        "tier": named,
        "disposition": ORTHOGONAL,
        "auto_act": False,
        "never_auto_act_on_classifier_only": True,
        "plain": "Provenance/watermark answers 'generated?', not 'abusive?'. Orthogonal to harm auto-act.",
    }


def schema() -> dict[str, Any]:
    return {
        "spec": SPEC,
        "tiers": list(TIERS),
        "dispositions": [AUTO, HUMAN, ORTHOGONAL],
        "never_auto_act_on_classifier_only": True,
        "hash_db": False,
        "classifier": False,
        "grounding": "Thorn: exact-match hash (auto) vs predictive classifier (human only) vs provenance (orthogonal).",
        "plain": "Three-tier split. Never auto-act on classifier-only. No detector ships here.",
    }
