"""Item 121 — Verra bind step-up, after 3DS2 frictionless vs challenge.

High-confidence exact-match binds may clear frictionlessly. Weak or
classifier-only matches always challenge. No ACS, no desk-invented risk score.
Liability recorded is which flow ran, not a card-network legal opinion.
"""
from __future__ import annotations

from typing import Any

try:
    from gate import harm_tiers as harm_tiers_mod
except ImportError:
    import harm_tiers as harm_tiers_mod

SPEC = "gate-verra-step-up-v1"
FRICTIONLESS = "FRICTIONLESS"
CHALLENGE = "CHALLENGE"
NONE = "NONE"
STRENGTHS = ("HIGH", "WEAK", "UNSET")

NUMERIC_REFUSED = (
    "acs_score",
    "risk_score",
    "threshold",
    "device_reputation",
    "account_age",
    "confidence",
)


def _strength(raw: Any) -> str | None:
    if raw is None or raw is False or raw == "":
        return "UNSET"
    if isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        return None
    text = str(raw).strip().upper().replace("-", "_")
    aliases = {"HIGH_CONFIDENCE": "HIGH", "LOW": "WEAK", "LOW_CONFIDENCE": "WEAK"}
    mapped = aliases.get(text, text)
    return mapped if mapped in STRENGTHS else None


def evaluate(
    *,
    tier: str | None = None,
    match_hash: str | None = None,
    match_strength: Any = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body = extra if isinstance(extra, dict) else {}
    hits = [k for k in NUMERIC_REFUSED if body.get(k) not in (None, "", False)]
    if hits:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "acs_score_refused",
            "refused": hits,
            "acs": False,
            "legal_advice": False,
            "plain": "No ACS risk number. Strength is HIGH, WEAK, or UNSET — not a 3DS2 score.",
        }

    strength = _strength(match_strength if match_strength is not None else body.get("match_strength"))
    if strength is None:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "strength_not_numeric",
            "acs": False,
            "legal_advice": False,
            "plain": "Match strength is an enum, not a float.",
        }

    tier_rec = harm_tiers_mod.classify(tier=tier or body.get("tier"), match_hash=match_hash or body.get("match_hash"))
    named = tier_rec.get("tier")
    if not named:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "tier_required",
            "flow": None,
            "acs": False,
            "legal_advice": False,
            "plain": "Step-up needs a 120 tier. Uniform strictness is refused.",
        }

    if named == harm_tiers_mod.PROVENANCE:
        return {
            "spec": SPEC,
            "ok": True,
            "tier": named,
            "match_strength": strength,
            "flow": NONE,
            "frictionless": False,
            "challenged": False,
            "liability_shift": False,
            "liability_follows_flow": True,
            "acs": False,
            "legal_advice": False,
            "harm_tier": tier_rec,
            "plain": "Provenance is orthogonal. It is not a bind match and does not frictionless-clear.",
        }

    classifier = named == harm_tiers_mod.CLASSIFIER
    hashed = bool((match_hash or body.get("match_hash") or "").strip())
    high = strength == "HIGH" and named == harm_tiers_mod.EXACT_MATCH and hashed and not classifier
    flow = FRICTIONLESS if high else CHALLENGE
    return {
        "spec": SPEC,
        "ok": True,
        "tier": named,
        "match_strength": strength,
        "flow": flow,
        "frictionless": flow == FRICTIONLESS,
        "challenged": flow == CHALLENGE,
        "liability_shift": flow == CHALLENGE,
        "liability_follows_flow": True,
        "acs": False,
        "legal_advice": False,
        "harm_tier": tier_rec,
        "plain": (
            "High-confidence exact-match cleared frictionlessly. Liability follows this flow, not a network opinion."
            if flow == FRICTIONLESS
            else "Weak or classifier match stepped up to a challenge. Not uniform strictness. Not an ACS score."
        ),
    }
