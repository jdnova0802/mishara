"""Flawless scorecards — Gate + Nisaba family.

Honest. Market-biting. Action OS formula baked in.
Never inflate when their_production is false.
Scarcity is the DENY — scorecards that lie are SaaS.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "nisaba-scorecard-v1"
INVENTOR = "Nisaba LLC"

# Pre-revenue ceilings — proof dims stay capped until a real weld
PRE_REV_MAX = {
    "problem_clarity": 10.0,
    "market_bite": 10.0,
    "voice": 10.0,
    "public_face": 10.0,
    "icp_focus": 9.0,
    "economics_model": 10.0,
    "technical_differentiation": 10.0,
    "deployability": 9.0,
    "buyer_trust": 9.0,
    "narrative_vs_reality": 9.0,
    "competitive_positioning": 10.0,
    "antifragile": 10.0,
    "irreplaceable": 10.0,
    "rail_speed": 9.0,
    "world_class_quality": 10.0,
    "shadow_integration": 10.0,
    "mother_nature": 10.0,
    "copy_pitch": 10.0,
}

NATURE_WEIGHTS = (
    "antifragile",
    "irreplaceable",
    "rail_speed",
    "world_class_quality",
    "shadow_integration",
    "mother_nature",
)

# Real market problems each sibling bites — no museum labels
FAMILY_BITES: dict[str, dict[str, Any]] = {
    "velaru": {
        "name": "Velaru",
        "role": "proof rail",
        "question": "Did we commit correctly?",
        "market_problem": (
            "EU AI Act Art 12 / FRE 707 / carrier liability: platforms prove generation; "
            "nobody ships stranger-verifiable refusal + silence receipts before dispute."
        ),
        "buyer": "GC · carrier counsel · HR AI vendors · compliance",
        "url": "https://velaru.xyz",
        "voice_line": "The receipt that neither side controls",
        "live": True,
        "scores": {
            "problem_clarity": 9.5,
            "market_bite": 9.5,
            "voice": 9.5,
            "public_face": 9.0,
            "icp_focus": 8.5,
            "economics_model": 8.0,
            "technical_differentiation": 9.5,
            "deployability": 7.5,
            "buyer_trust": 9.0,
            "narrative_vs_reality": 8.5,
            "competitive_positioning": 9.0,
            "antifragile": 9.0,
            "irreplaceable": 8.5,
            "rail_speed": 8.5,
            "world_class_quality": 9.0,
            "shadow_integration": 8.5,
            "mother_nature": 9.0,
            "copy_pitch": 9.0,
        },
        "gaps_honest": [
            "Enterprise HA / HSM BYOK still raise path",
            "Design partners open — not saturated distribution",
        ],
    },
    "erra": {
        "name": "Erra",
        "role": "signal rail",
        "question": "Should we act?",
        "market_problem": (
            "Reinsurance / UW / platform integrity: carriers price on patterns; "
            "platforms prove on logs. Independent fusion + actuarial grade before bind is unclaimed."
        ),
        "buyer": "Reinsurance · UW diligence · claims AI · public-sector signal",
        "url": "https://velaru.xyz/erra",
        "voice_line": "Show me the cluster before you bind",
        "live": True,
        "scores": {
            "problem_clarity": 9.0,
            "market_bite": 9.0,
            "voice": 6.5,  # twin of Velaru — voice still thin
            "public_face": 7.0,
            "icp_focus": 8.0,
            "economics_model": 8.0,
            "technical_differentiation": 8.5,
            "deployability": 6.5,
            "buyer_trust": 7.0,
            "narrative_vs_reality": 7.0,
            "competitive_positioning": 8.5,
            "antifragile": 8.0,
            "irreplaceable": 7.5,
            "rail_speed": 7.5,
            "world_class_quality": 7.5,
            "shadow_integration": 8.5,
            "mother_nature": 8.0,
            "copy_pitch": 7.0,
        },
        "gaps_honest": [
            "Voice still reads as Velaru inverse — needs own gravity",
            "Auto threshold-gate after bind room still SOW path",
        ],
    },
    "verra": {
        "name": "Verra",
        "role": "action session",
        "question": "Did both rails clear before bind?",
        "market_problem": (
            "PAS / counsel pre-bind: buyers need one export pack (signal + proof) "
            "before capital, coverage, or force moves — not two demos and a Slack thread."
        ),
        "buyer": "Carrier ops · counsel · PAS implementors",
        "url": "https://velaru.xyz/verra",
        "voice_line": "The room where both rails must clear",
        "live": True,
        "scores": {
            "problem_clarity": 8.5,
            "market_bite": 8.5,
            "voice": 5.5,  # session glue — weakest voice
            "public_face": 6.5,
            "icp_focus": 8.0,
            "economics_model": 7.5,
            "technical_differentiation": 7.5,
            "deployability": 7.0,  # bind room live
            "buyer_trust": 7.5,
            "narrative_vs_reality": 7.5,
            "competitive_positioning": 7.5,
            "antifragile": 7.0,
            "irreplaceable": 6.5,
            "rail_speed": 8.0,
            "world_class_quality": 7.0,
            "shadow_integration": 7.5,
            "mother_nature": 7.5,
            "copy_pitch": 6.5,
        },
        "gaps_honest": [
            "Named session, not fourth deploy — voice must not pretend otherwise",
            "Ops queue after ALLOW is production SOW, not pre-rev build",
        ],
    },
    "gate": {
        "name": "Gate",
        "role": "Action OS mouth",
        "question": "Does the irreversible write complete?",
        "market_problem": (
            "Operators / payout / bind-only / licensed rails: irreversible spend still "
            "completes on soft-yes dashboards. Mouth + 10 bps register is the unclaimed door."
        ),
        "buyer": "Operators · carriers · any entity on the write",
        "url": None,  # filled
        "voice_line": "Scarcity is the DENY",
        "live": True,
        "scores": None,  # computed dynamically
        "gaps_honest": [
            "their_production false until third-party weld",
            "Force/battlefield in category only — not a claimed door",
        ],
    },
    "mishara": {
        "name": "Mishara",
        "role": "consumer harm path",
        "question": "Was a person harmed?",
        "market_problem": (
            "Hiring / housing / credit AI harm: consumers get no independent receipt "
            "and no demand path when a model denied them."
        ),
        "buyer": "Harmed individuals · advocates (not the money path)",
        "url": "https://mishara.onrender.com",
        "voice_line": "When the act already hurt someone",
        "live": True,
        "scores": {
            "problem_clarity": 8.5,
            "market_bite": 8.0,
            "voice": 6.0,
            "public_face": 6.5,
            "icp_focus": 7.5,
            "economics_model": 4.0,  # rights path, not GP register
            "technical_differentiation": 7.0,
            "deployability": 7.0,
            "buyer_trust": 7.0,
            "narrative_vs_reality": 7.5,
            "competitive_positioning": 7.0,
            "antifragile": 6.5,
            "irreplaceable": 6.0,
            "rail_speed": 6.5,
            "world_class_quality": 6.5,
            "shadow_integration": 6.0,
            "mother_nature": 8.0,
            "copy_pitch": 6.5,
        },
        "gaps_honest": [
            "Consumer app — different door; not Action OS cosplay",
            "Attorney referral still coming; economics intentionally thin",
        ],
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _round(x: float) -> float:
    return round(x, 1)


def _avg(d: dict[str, float]) -> float:
    return sum(d.values()) / len(d) if d else 0.0


def _gaps(scores: dict[str, float]) -> dict[str, float]:
    return {k: _round(PRE_REV_MAX[k] - scores[k]) for k in scores if k in PRE_REV_MAX}


def _gate_scores(prod: bool, proof_ok: bool) -> dict[str, float]:
    """Dynamic Gate scores — honesty over theater."""
    return {
        "problem_clarity": 9.5 if proof_ok else 9.0,
        "market_bite": 9.5,
        "voice": 9.0,  # Action OS formula shipped
        "public_face": 9.0,
        "icp_focus": 8.5,  # serve everybody; GTM still 3 doors
        "economics_model": 9.5,
        "technical_differentiation": 9.5 if proof_ok else 9.0,
        "deployability": 9.0 if prod else 5.5,
        "buyer_trust": 8.5 if proof_ok else 7.5,
        "narrative_vs_reality": 9.0 if prod else 7.5,  # formula honest about force
        "competitive_positioning": 9.5,
        "antifragile": 9.0 if proof_ok else 8.0,
        "irreplaceable": 8.5 if prod else 7.5,
        "rail_speed": 8.5,
        "world_class_quality": 9.0 if proof_ok else 8.0,
        "shadow_integration": 9.0,  # sit on write without dashboard theater
        "mother_nature": 9.0,  # controversy as nature; fail-closed
        "copy_pitch": 9.0,
    }


def _product_card(key: str, scores: dict[str, float], meta: dict[str, Any], base: str) -> dict[str, Any]:
    concept_keys = [
        k
        for k in scores
        if k
        not in (
            "deployability",
            "buyer_trust",
            "narrative_vs_reality",
        )
    ]
    proof_keys = ["deployability", "buyer_trust", "narrative_vs_reality"]
    nature = {k: scores[k] for k in NATURE_WEIGHTS if k in scores}
    concept = _avg({k: scores[k] for k in concept_keys})
    proof = _avg({k: scores[k] for k in proof_keys if k in scores})
    overall = (concept + proof) / 2
    return {
        "id": key,
        "name": meta["name"],
        "role": meta["role"],
        "question": meta["question"],
        "market_problem": meta["market_problem"],
        "buyer": meta["buyer"],
        "voice_line": meta["voice_line"],
        "url": meta["url"] or base,
        "live": meta["live"],
        "dimensions": {k: _round(v) for k, v in scores.items()},
        "gaps": _gaps(scores),
        "gaps_honest": list(meta.get("gaps_honest") or []),
        "overall_concept": _round(concept),
        "overall_proof": _round(proof),
        "overall_nature": _round(_avg(nature)),
        "overall": _round(overall),
        "pre_rev_max": {k: PRE_REV_MAX[k] for k in scores if k in PRE_REV_MAX},
    }


def score(public_url: str) -> dict[str, Any]:
    try:
        from gate import production_skin as skin_mod
        from gate import proof_suite as proof_mod
        from gate import action_os as aos_mod
    except ImportError:
        import production_skin as skin_mod  # type: ignore[no-redef]
        import proof_suite as proof_mod  # type: ignore[no-redef]
        import action_os as aos_mod  # type: ignore[no-redef]

    base = (public_url or "").rstrip("/")
    prod = skin_mod.their_production()
    proof = proof_mod.run_invariants()
    proof_ok = all(p["passes"] for p in proof)
    aos = aos_mod.manifest(base)

    products = []
    for key, meta in FAMILY_BITES.items():
        if key == "gate":
            scores = _gate_scores(prod, proof_ok)
        else:
            scores = dict(meta["scores"])
        products.append(_product_card(key, scores, meta, base))

    gate = next(p for p in products if p["id"] == "gate")
    family_overall = _avg({p["id"]: p["overall"] for p in products})
    voice_scores = {p["id"]: p["dimensions"]["voice"] for p in products}
    bite_scores = {p["id"]: p["dimensions"]["market_bite"] for p in products}

    weakest_voice = min(products, key=lambda p: p["dimensions"]["voice"])
    strongest_bite = max(products, key=lambda p: p["dimensions"]["market_bite"])

    return {
        "spec": SPEC,
        "name": "Nisaba family scorecard",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "formula": aos.get("formula") or aos_mod.FORMULA,
        "their_production": prod,
        "proof_all_pass": proof_ok,
        "proof_pass_count": sum(1 for p in proof if p["passes"]),
        "proof_total": len(proof),
        "pre_rev_ceiling": 9.0,
        "gate": gate,
        "family": products,
        "family_overall": _round(family_overall),
        "voice_board": voice_scores,
        "bite_board": bite_scores,
        "weakest_voice": {
            "id": weakest_voice["id"],
            "name": weakest_voice["name"],
            "voice": weakest_voice["dimensions"]["voice"],
            "fix": "Ship own gravity — not twin chrome of Velaru/Gate",
        },
        "strongest_market_bite": {
            "id": strongest_bite["id"],
            "name": strongest_bite["name"],
            "market_bite": strongest_bite["dimensions"]["market_bite"],
            "problem": strongest_bite["market_problem"],
        },
        "overall_concept": gate["overall_concept"],
        "overall_proof": gate["overall_proof"],
        "overall_nature": gate["overall_nature"],
        "overall": gate["overall"],
        "dimensions": gate["dimensions"],
        "gaps": gate["gaps"],
        "pre_rev_max": gate["pre_rev_max"],
        "lift_when_production_welded": _round(9.0 - gate["overall"]) if not prod else 0.0,
        "flawless_means": [
            "Honest gaps — never inflate deployability without a weld",
            "Every sibling names a real market problem and a buyer",
            "Voice scores punish thin twins (Erra/Verra/Mishara)",
            "Nature dims: antifragile · irreplaceable · rails · quality · shadow · Mother Nature",
            "Scarcity remains DENY — scorecard lies are SaaS",
        ],
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    s = score(base)
    return {
        **s,
        "production_skin": f"{base}/.well-known/production-skin.json",
        "proof_suite": f"{base}/.well-known/proof-suite.json",
        "action_os": f"{base}/.well-known/action-os.json",
        "page": f"{base}/scorecard",
        "gatekeep": "Flawless = honest. Ours.",
    }
