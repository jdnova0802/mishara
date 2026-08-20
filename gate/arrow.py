"""Arrow Impossibility of Soft-Yes — you cannot aggregate approvals into LIVE.

Arrow: no rank aggregation satisfies reasonable axioms. Gate: no committee
of UW approve / dashboard green / AI badge / Slack LGTM aggregates into
LIVE without a dictator that isn't CHARGE — and CHARGE is not a voter,
it is a costly witness. Copycats run voting theater.

Gatekeep only to ourselves: Arrow impossibility → soft-yes votes ≠ CHARGE.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-arrow-v1"
INVENTOR = "Nisaba LLC / Gate"

BALLOTS = ("uw_approve", "dashboard_green", "ai_badge", "slack_lgtm", "risk_pass")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def aggregate(*, ballots: list[str] | None = None, charge_id: str | None = None) -> dict[str, Any]:
    b = [x.strip().lower() for x in (ballots or []) if x]
    charge = bool((charge_id or "").strip())
    votes = [x for x in b if x in BALLOTS]
    if votes and not charge:
        posture = "impossible_social_choice"
        claim = "soft_yes_profile_does_not_yield_live"
    elif charge:
        posture = "witness_not_vote"
        claim = "charge_is_not_a_ballot_it_is_a_witness"
    else:
        posture = "empty_profile"
        claim = "no_ballots_no_charge"
    return {
        "spec": SPEC,
        "name": "Arrow Impossibility of Soft-Yes",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Kenneth Arrow — impossibility of aggregating ranked preferences",
            "Gate CHARGE-only LIVE — not a committee product",
        ],
        "rejected_ballots": list(BALLOTS),
        "ballots": votes,
        "charge_present": charge,
        "posture": posture,
        "claim": claim,
        "thesis": "Unanimous soft-yes is still not LIVE. Votes do not weld.",
        "gatekeep": "Proprietary Arrow-impossibility doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Arrow Impossibility of Soft-Yes",
        "inventor": INVENTOR,
        "example_impossible": aggregate(ballots=["uw_approve", "ai_badge", "slack_lgtm"]),
        "example_witness": aggregate(ballots=["uw_approve"], charge_id="chg_1"),
        "live": f"{base}/.well-known/arrow.json",
        "costliness": f"{base}/.well-known/costliness.json",
        "their_production": False,
    }
