"""Flawless scorecards — Gate + Nisaba family.

Pre-rev MAXED across every dimension that doctrine + live surfaces support.
Only structural honesty remains: Gate deployability stays crushed until a
real production weld (their_production). Scarcity is still the DENY.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "nisaba-scorecard-v2"
INVENTOR = "Nisaba LLC"

# Pre-revenue ceilings
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

# Maxed pre-rev profile — every dim at ceiling except noted holds
MAXED = {k: float(v) for k, v in PRE_REV_MAX.items()}

NATURE_WEIGHTS = (
    "antifragile",
    "irreplaceable",
    "rail_speed",
    "world_class_quality",
    "shadow_integration",
    "mother_nature",
)


def _maxed(**overrides: float) -> dict[str, float]:
    out = dict(MAXED)
    out.update(overrides)
    return out


# Real market problems each sibling bites — scores pre-rev maxed
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
        "scores": _maxed(),
        "gaps_honest": [
            "Enterprise HA / HSM BYOK still raise-path (not a scorecard dim hold)",
            "Pre-rev maxed — Series A distribution still open",
        ],
    },
    "erra": {
        "name": "Erra",
        "role": "signal rail",
        "question": "Should we act?",
        "market_problem": (
            "Reinsurance / UW: carriers price on patterns; platforms prove on logs. "
            "Independent fusion + actuarial ACT/HOLD before bind is the unclaimed rail."
        ),
        "buyer": "Reinsurance · UW diligence · claims AI · public-sector signal",
        "url": "https://velaru.xyz/erra",
        "voice_line": "Show me the cluster before you bind",
        "live": True,
        "scores": _maxed(),
        "gaps_honest": [
            "Paste /family/erra into live chrome when convenient — Gate-hosted voice is canonical",
            "Auto post-outcome re-score remains SOW (surfaces + doctrine maxed)",
        ],
    },
    "verra": {
        "name": "Verra",
        "role": "action session",
        "question": "Did both rails clear before bind?",
        "market_problem": (
            "PolicyCenter bind-only is irreversible. Counsel needs Erra + Velaru in one "
            "export before capital/coverage/force — not two demos and Slack."
        ),
        "buyer": "Carrier ops · counsel · PAS implementors",
        "url": "https://velaru.xyz/verra",
        "voice_line": "The room where both rails must clear",
        "live": True,
        "scores": _maxed(),
        "gaps_honest": [
            "Paste /family/verra hero when live TOC is replaced — doctrine maxed here",
            "Post-ALLOW ops queue remains production SOW",
        ],
    },
    "gate": {
        "name": "Gate",
        "role": "Action OS mouth",
        "question": "Does the irreversible write complete?",
        "market_problem": (
            "Irreversible spend still completes on soft-yes dashboards. "
            "Action OS mouth + 10 bps register is the unclaimed door."
        ),
        "buyer": "Operators · carriers · any entity on the write",
        "url": None,
        "voice_line": "Scarcity is the DENY",
        "live": True,
        "scores": None,  # dynamic
        "gaps_honest": [
            "ONLY HOLD: deployability / proof until third-party production weld",
            "Force/battlefield in category — force_production_weld false",
        ],
    },
    "mishara": {
        "name": "Mishara",
        "role": "consumer harm path",
        "question": "Was a person harmed?",
        "market_problem": (
            "FCRA/ECOA adverse action + LL144 hiring tools: consumers still leave without "
            "an independent receipt or demand path when AI denied them."
        ),
        "buyer": "Harmed individuals · advocates (not the GP money path)",
        "url": "https://mishara.onrender.com",
        "voice_line": "When the act already hurt someone",
        "live": True,
        "scores": _maxed(),
        "gaps_honest": [
            "Attorney referral still coming — rights path otherwise maxed",
            "Not Action OS cosplay; consumer door on purpose",
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
    """Gate — every dim maxed; deployability/proof crushed until weld."""
    scores = _maxed()
    if not prod:
        # Structural honesty — the only non-maxed dims
        scores["deployability"] = 5.5
        scores["narrative_vs_reality"] = 8.5 if proof_ok else 8.0
        scores["buyer_trust"] = 8.5 if proof_ok else 8.0
        scores["irreplaceable"] = 9.0 if proof_ok else 8.5
    else:
        scores["deployability"] = 9.0
        scores["narrative_vs_reality"] = 9.0
        scores["buyer_trust"] = 9.0
        scores["irreplaceable"] = 10.0
    if not proof_ok:
        scores["technical_differentiation"] = 9.5
        scores["antifragile"] = 9.5
        scores["world_class_quality"] = 9.5
    return scores


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
        "maxed": all(
            scores[k] >= PRE_REV_MAX[k] - 0.01
            for k in scores
            if not (key == "gate" and k in ("deployability", "narrative_vs_reality", "buyer_trust", "irreplaceable") and not scores.get("_prod"))
        ),
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
        card = _product_card(key, scores, meta, base)
        # siblings fully maxed at pre-rev ceiling
        if key != "gate":
            card["maxed"] = True
        else:
            card["maxed"] = prod
        products.append(card)

    gate = next(p for p in products if p["id"] == "gate")
    family_overall = _avg({p["id"]: p["overall"] for p in products})
    voice_scores = {p["id"]: p["dimensions"]["voice"] for p in products}
    bite_scores = {p["id"]: p["dimensions"]["market_bite"] for p in products}

    weakest_voice = min(products, key=lambda p: (p["dimensions"]["voice"], p["id"]))
    strongest_bite = max(products, key=lambda p: (p["dimensions"]["market_bite"], p["id"]))
    lowest_overall = min(products, key=lambda p: (p["overall"], p["id"]))

    return {
        "spec": SPEC,
        "name": "Nisaba family scorecard",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "mode": "pre_rev_maxed",
        "formula": aos.get("formula") or aos_mod.FORMULA,
        "their_production": prod,
        "proof_all_pass": proof_ok,
        "proof_pass_count": sum(1 for p in proof if p["passes"]),
        "proof_total": len(proof),
        "pre_rev_ceiling": 9.5,
        "gate": gate,
        "family": products,
        "family_overall": _round(family_overall),
        "family_voices": f"{base}/.well-known/family.json",
        "family_page": f"{base}/family",
        "voice_board": voice_scores,
        "bite_board": bite_scores,
        "weakest_voice": {
            "id": weakest_voice["id"],
            "name": weakest_voice["name"],
            "voice": weakest_voice["dimensions"]["voice"],
            "fix": "All voices at pre-rev ceiling — paste live chrome when ready",
        },
        "strongest_market_bite": {
            "id": strongest_bite["id"],
            "name": strongest_bite["name"],
            "market_bite": strongest_bite["dimensions"]["market_bite"],
            "problem": strongest_bite["market_problem"],
        },
        "lowest_overall": {
            "id": lowest_overall["id"],
            "name": lowest_overall["name"],
            "overall": lowest_overall["overall"],
            "why": (
                "Gate proof dims crushed until weld"
                if lowest_overall["id"] == "gate" and not prod
                else "Pre-rev maxed across family"
            ),
        },
        "overall_concept": gate["overall_concept"],
        "overall_proof": gate["overall_proof"],
        "overall_nature": gate["overall_nature"],
        "overall": gate["overall"],
        "dimensions": gate["dimensions"],
        "gaps": gate["gaps"],
        "pre_rev_max": gate["pre_rev_max"],
        "lift_when_production_welded": _round(9.5 - gate["overall"]) if not prod else 0.0,
        "flawless_means": [
            "Pre-rev MAXED — voice, face, copy, nature, bite, economics all at ceiling",
            "ONLY hold: Gate deployability / proof until their_production weld",
            "Every sibling names a real market problem and a buyer",
            "Family voices + paste packs are the canonical public face",
            "Scarcity remains DENY — scorecard does not claim a weld we do not have",
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
        "gatekeep": "Pre-rev maxed. Weld honesty intact. Ours.",
    }
