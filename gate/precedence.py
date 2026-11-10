"""Item 56 — ordered regulatory precedence. First matching higher-rank rule wins."""
from __future__ import annotations

from typing import Any

SPEC = "gate-precedence-v1"

# Lower rank number = higher precedence. House policy is last on purpose.
RULES: list[dict[str, Any]] = [
    {
        "rank": 10,
        "id": "iec_61511",
        "when": {"field": "vertical", "op": "eq", "value": "ot"},
        "governs": "IEC 61511 — sensor / logic solver / final element",
        "citation": "https://webstore.iec.ch/publication/5527",
    },
    {
        "rank": 20,
        "id": "naic_model_225",
        "when": {"field": "mga_contract_terminated", "op": "eq", "value": "yes"},
        "governs": "NAIC Model 225 §5E — 30-day commissioner notice",
        "citation": "https://content.naic.org/sites/default/files/model-law-225.pdf",
    },
    {
        "rank": 30,
        "id": "ks_40_2133",
        "when": {"field": "state", "op": "eq", "value": "KS"},
        "governs": "K.S.A. 40-2,133(f) — same 30-day clock",
        "citation": "https://www.insurance.kansas.gov/",
    },
    {
        "rank": 40,
        "id": "eu_ai_act_annex_iii",
        "when": {"field": "annex_iii", "op": "eq", "value": True},
        "governs": "EU AI Act Art. 12 logging for high-risk systems",
        "citation": "https://artificialintelligenceact.eu/",
    },
    {
        "rank": 90,
        "id": "house_policy",
        "when": {"field": "*", "op": "always", "value": True},
        "governs": "Operator house policy — lowest. Does not preempt statute.",
        "citation": None,
    },
]


def _get(body: dict[str, Any], field: str) -> Any:
    if field == "*":
        return True
    cur: Any = body
    for part in field.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def _match(left: Any, op: str, right: Any) -> bool:
    if op == "always":
        return True
    if op == "eq":
        if isinstance(right, str) and left is not None:
            return str(left).lower() == right.lower() if not isinstance(right, bool) else left == right
        return left == right
    return False


def resolve(body: dict[str, Any]) -> dict[str, Any]:
    considered = []
    winner = None
    for rule in sorted(RULES, key=lambda r: r["rank"]):
        hit = _match(_get(body, rule["when"]["field"]), rule["when"]["op"], rule["when"]["value"])
        considered.append({"id": rule["id"], "rank": rule["rank"], "hit": hit})
        if hit and winner is None:
            winner = rule
    return {
        "spec": SPEC,
        "winner": {
            "id": winner["id"],
            "rank": winner["rank"],
            "governs": winner["governs"],
            "citation": winner["citation"],
        }
        if winner
        else None,
        "considered": considered,
        "plain": "First matching rule wins. Lower rank number preempts house policy.",
    }
