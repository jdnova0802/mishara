"""Incommensurable Alphabet — ALLOW/HALT/BLOCK does not translate into KPI English.

Alien languages leave remainder under translation. Gate's mouth alphabet
is incommensurable with 'risk score', 'confidence', and 'approve rate'.
Forcing a translation is how Goodhart starts. Copycats localize the mouth
into BI. Gate keeps remainder.

Gatekeep only to ourselves: incommensurability / xenolinguistics → refuse KPI gloss.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-incommensurable-v1"
INVENTOR = "Nisaba LLC / Gate"

FORBIDDEN_GLOSSES = (
    "risk_score",
    "confidence_percent",
    "approve_rate",
    "halt_kpi",
    "safety_grade",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def translate(*, gloss: str | None = None, keep_remainder: bool | None = None) -> dict[str, Any]:
    g = (gloss or "").strip().lower()
    keep = True if keep_remainder is None else bool(keep_remainder)
    if g in FORBIDDEN_GLOSSES or g.endswith("_kpi"):
        posture = "false_translation"
        claim = "kpi_english_erases_the_alphabet"
    elif keep and not g:
        posture = "remainder_held"
        claim = "mouth_stays_allow_halt_block"
    else:
        posture = "unevaluated"
        claim = "no_gloss_assay"
    return {
        "spec": SPEC,
        "name": "Incommensurable Alphabet",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Incommensurability (Kuhn/Feyerabend) — remainder under translation",
            "Xenolinguistics — alien lexemes that do not map to earthly KPIs",
            "Gate Goodhart mouth — never gloss HALT as a target",
        ],
        "forbidden_glosses": list(FORBIDDEN_GLOSSES),
        "gloss": g or None,
        "keep_remainder": keep,
        "posture": posture,
        "claim": claim,
        "thesis": "HALT is not a percent. Translation without remainder is a hack.",
        "gatekeep": "Proprietary incommensurable-alphabet doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Incommensurable Alphabet",
        "inventor": INVENTOR,
        "example_held": translate(keep_remainder=True),
        "example_false": translate(gloss="risk_score"),
        "live": f"{base}/.well-known/incommensurable.json",
        "goodhart": f"{base}/.well-known/goodhart.json",
        "their_production": False,
    }
