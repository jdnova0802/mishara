"""Unforgeable Costliness of CHARGE — Szabo × Gate resurrection.

Szabo: value that is hard to spoof because creating it was costly.
Gate: DEAD→LIVE is CHARGE-only. The costliness must be unforgeable —
admin approve, UW soft-yes, and dashboard toggles are forgeable 'resurrection'.

This invention publishes the costliness ladder: which transitions are
cheap-to-fake vs unforgeably costly, and stamps CHARGE / weld as the
costly commitments that may change regime.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-costliness-v1"
INVENTOR = "Nisaba LLC / Gate"

# Economic floor language already in exclusive/floor: CHARGE must cost more than the act.
COSTLY_TRANSITIONS = (
    {
        "id": "charge_resurrection",
        "act": "DEAD|UNSIGNED → LIVE via CHARGE webhook / charge_id",
        "costliness": "unforgeable",
        "why": (
            "Requires named charge_id spanning old and new regimes. "
            "UW approve without CHARGE does not resurrect — forgeable soft-yes rejected."
        ),
        "forgeable_substitutes_rejected": [
            "UW approve",
            "admin toggle",
            "dashboard LIVE flip",
            "re-run hop with same ticket",
        ],
    },
    {
        "id": "operator_weld",
        "act": "Operator weld checkout — production mouth goes LIVE",
        "costliness": "unforgeable",
        "why": "Idempotent paid weld; human commits before production door opens.",
        "forgeable_substitutes_rejected": [
            "demo fuse",
            "their_production:false theater",
            "unsigned license parent",
        ],
    },
    {
        "id": "epoch_regime_change",
        "act": "Prior HALT/BLOCK → ALLOW on same job_id",
        "costliness": "unforgeable",
        "why": "Epoch lock requires charge_id. Monotonic accountability.",
        "forgeable_substitutes_rejected": [
            "reinterpret prior halt",
            "delete evidence",
            "new hop without charge_id",
        ],
    },
)

CHEAP_FORGEABLE = (
    "risk score green",
    "policy PDF",
    "trust-me email",
    "museum DEAD receipt on an optional hop",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def assay(
    *,
    transition: str | None = None,
    charge_id: str | None = None,
    weld_completed: bool | None = None,
    prior_halt: bool | None = None,
) -> dict[str, Any]:
    """Assay whether a claimed regime change has unforgeable costliness."""
    t = (transition or "").strip().lower()
    cid = (charge_id or "").strip() or None

    if t in ("charge", "charge_resurrection", "resurrection"):
        ok = bool(cid)
        matched = COSTLY_TRANSITIONS[0]
        verdict = "costly_and_witnessed" if ok else "forgeable_or_missing_witness"
    elif t in ("weld", "operator_weld"):
        ok = bool(weld_completed)
        matched = COSTLY_TRANSITIONS[1]
        verdict = "costly_and_witnessed" if ok else "forgeable_or_missing_witness"
    elif t in ("epoch", "epoch_regime_change"):
        ok = bool(cid) and bool(prior_halt)
        matched = COSTLY_TRANSITIONS[2]
        verdict = "costly_and_witnessed" if ok else "forgeable_or_missing_witness"
    else:
        matched = None
        ok = False
        verdict = "unknown_transition"

    return {
        "spec": SPEC,
        "name": "Unforgeable Costliness Assay",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "transition": t or None,
        "matched": matched,
        "charge_id_present": bool(cid),
        "verdict": verdict,
        "passes": ok,
        "rule": "CHARGE / weld / epoch change must cost more than the irreversible act was worth.",
        "their_production": False,
    }


def ladder() -> dict[str, Any]:
    return {
        "spec": SPEC,
        "name": "Unforgeable Costliness of CHARGE",
        "inventor": INVENTOR,
        "lineage": [
            "Nick Szabo — unforgeable costliness; bit gold",
            "Gate exclusive timing — resurrect must cost more than the act was worth",
            "Gate epoch — charge_id is the sole admissible regime witness",
        ],
        "costly_transitions": list(COSTLY_TRANSITIONS),
        "cheap_forgeable_rejected": list(CHEAP_FORGEABLE),
        "thesis": (
            "Permission resurrection without unforgeable cost is counterfeit. "
            "Gate only accepts costly witnesses: CHARGE, weld, epoch charge_id."
        ),
        "gatekeep": "Proprietary costliness ladder for irreversible-permission regimes. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    body = ladder()
    body["live"] = f"{base}/.well-known/costliness.json"
    body["example_assay"] = assay(transition="charge", charge_id="chg_example")
    body["license_fuse"] = f"{base}/.well-known/license-fuse.json"
    body["operator"] = f"{base}/.well-known/operator.json"
    return body
