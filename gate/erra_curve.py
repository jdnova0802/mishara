"""Item 118 — Erra precision/recall curve per vertical.

Grounded in Wikipedia ORES: publish a table, let policy pick the operating
point. This checkout has no live labels, so the table is empty and the
operating point is null. Item 138: exact cutoffs are not published.
"""
from __future__ import annotations

from typing import Any

try:
    from gate import v1 as v1_mod
except ImportError:
    import v1 as v1_mod

SPEC = "gate-erra-threshold-curve-v1"

# Named bands only. No precision/recall numbers until live labels exist.
BANDS = (
    {
        "id": "auto_act",
        "use": "Automatic action, once a live operating point is picked.",
        "precision_band": None,
        "recall_band": None,
    },
    {
        "id": "human_review",
        "use": "Human-review queue, once a live operating point is picked.",
        "precision_band": None,
        "recall_band": None,
    },
)

ORES_NOTE = (
    "Wikipedia ORES publishes precision/recall per operating point and lets "
    "each consumer pick the point. Erra will too. The cells here are empty "
    "until live labels exist. These are not ORES's numbers."
)

OPSEC_NOTE = (
    "Item 138: prefer banded ranges over exact cutoffs. Exact precision/recall "
    "is not accepted on this mouth. ZK consistency proofs are item 51, unbuilt."
)


def verticals() -> list[str]:
    names = set(v1_mod.FORMULAS) | set(v1_mod.ALIASES)
    return sorted(names)


def _normalize(vertical: str | None) -> str | None:
    raw = (vertical or "").strip().lower()
    if not raw:
        return None
    if raw in v1_mod.FORMULAS:
        return raw
    if raw in v1_mod.ALIASES:
        return v1_mod.ALIASES[raw]
    return raw


def curve(vertical: str | None = None) -> dict[str, Any]:
    canon = _normalize(vertical)
    return {
        "spec": SPEC,
        "vertical": canon,
        "operating_point": None,
        "operating_point_source": "unset — policy has not picked a live point",
        "points": [],
        "bands": [dict(b) for b in BANDS],
        "live_labels": False,
        "disclosure": "banded",
        "ores_note": ORES_NOTE,
        "opsec_note": OPSEC_NOTE,
        "plain": (
            "No live precision/recall for this vertical. "
            "The buyer-facing answer is an empty curve, not a hardcoded cutoff."
        ),
    }


def catalog() -> dict[str, Any]:
    verts = verticals()
    return {
        "spec": SPEC,
        "verticals": verts,
        "curves": [curve(v) for v in sorted(v1_mod.FORMULAS)],
        "live_labels": False,
        "disclosure": "banded",
        "ores_note": ORES_NOTE,
        "opsec_note": OPSEC_NOTE,
        "plain": "Per-vertical curves exist as empty tables. Operating points are null.",
    }


def reject_numeric_cutoff(body: dict[str, Any] | None) -> dict[str, Any] | None:
    """Refuse a desk-invented precision/recall or threshold. Live labels only."""
    body = body if isinstance(body, dict) else {}
    forbidden = (
        "precision",
        "recall",
        "threshold",
        "operating_point",
        "cutoff",
        "f1",
    )
    hits = []
    for key in forbidden:
        val = body.get(key)
        if val is None or val is False or val == "":
            continue
        hits.append(key)
    points = body.get("points")
    if isinstance(points, list) and points:
        hits.append("points")
    if not hits:
        return None
    return {
        "ok": False,
        "error": "live_labels_required",
        "refused": hits,
        "plain": (
            "Precision, recall, and operating points are not accepted without live labels. "
            "Do not paste ORES's table in as Erra's."
        ),
    }
