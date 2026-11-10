"""Item 104 — Trust & Safety vertical for AI-generated abuse.

Uses the 120 three-tier split and 122 named assumptions. Provenance
answers 'generated?'. Abuse is a separate question. No CV model.
"""
from __future__ import annotations

from typing import Any

try:
    from gate import harm_tiers as harm_tiers_mod
except ImportError:
    import harm_tiers as harm_tiers_mod

try:
    from gate import assumptions as assumptions_mod
except ImportError:
    import assumptions as assumptions_mod

SPEC = "gate-tns-vertical-v1"
VERTICAL = "trust_safety"


def evaluate(
    *,
    abuse_tier: str | None = None,
    match_hash: str | None = None,
    auto_act: bool = False,
    generated_tier: str | None = None,
    verified: bool = False,
    under_assumptions: Any = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body = extra if isinstance(extra, dict) else {}
    if body.get("harm_detected") not in (None, "", False) and not (abuse_tier or body.get("abuse_tier")):
        return {
            "spec": SPEC,
            "ok": False,
            "error": "flat_harm_refused",
            "vertical": VERTICAL,
            "cv_model": False,
            "hash_db": False,
            "plain": "One flat 'harm detected' is refused. Name an abuse tier and keep provenance orthogonal.",
        }

    abuse = harm_tiers_mod.classify(
        tier=abuse_tier or body.get("abuse_tier") or body.get("tier"),
        auto_act=bool(auto_act or body.get("auto_act")),
        match_hash=match_hash or body.get("match_hash"),
    )
    if not abuse.get("ok"):
        return {
            "spec": SPEC,
            "ok": False,
            "error": abuse.get("error"),
            "vertical": VERTICAL,
            "abuse": abuse,
            "cv_model": False,
            "hash_db": False,
            "plain": abuse.get("plain"),
        }

    gen_tier = generated_tier or body.get("generated_tier") or body.get("provenance_tier")
    if gen_tier:
        generated = harm_tiers_mod.classify(tier=gen_tier, auto_act=False)
    elif body.get("generated") not in (None, "", False):
        generated = harm_tiers_mod.classify(tier=harm_tiers_mod.PROVENANCE, auto_act=False)
    else:
        generated = {
            "spec": harm_tiers_mod.SPEC,
            "ok": True,
            "tier": None,
            "disposition": None,
            "plain": "Generated? was not asked. That is not an abuse verdict.",
        }

    if generated.get("tier") == harm_tiers_mod.PROVENANCE and generated.get("auto_act"):
        return {
            "spec": SPEC,
            "ok": False,
            "error": "provenance_not_abuse",
            "vertical": VERTICAL,
            "plain": "Provenance is orthogonal to abuse. It cannot auto-act as harm.",
        }

    claim = None
    if verified or body.get("verified"):
        claim = assumptions_mod.claim(
            verified=True,
            under_assumptions=under_assumptions if under_assumptions is not None else body.get("under_assumptions"),
            kind=body.get("kind") or "test",
        )
        if not claim.get("ok"):
            return {
                "spec": SPEC,
                "ok": False,
                "error": claim.get("error"),
                "vertical": VERTICAL,
                "assumption_claim": claim,
                "cv_model": False,
                "plain": claim.get("plain"),
            }

    return {
        "spec": SPEC,
        "ok": True,
        "vertical": VERTICAL,
        "cv_model": False,
        "hash_db": False,
        "classifier": False,
        "abuse": abuse,
        "generated": generated,
        "auto_act": bool(abuse.get("auto_act")),
        "assumption_claim": claim,
        "plain": (
            "Abuse and generated stay two questions. "
            + str(abuse.get("plain"))
            + " "
            + str(generated.get("plain"))
        ),
    }
