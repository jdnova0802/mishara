"""Nisaba Action OS — company nature, not homepage theater.

Palantir integrates data so institutions can know faster.
Nisaba sits on irreversible action: should this act run?

We serve everybody — economies, politicians, companies, any entity
whose write moves capital, coverage, or force. Controversy is nature
when DENY/DEAD is a real event. Integrity is CHARGE-only, stranger
verify, one door, fail-closed — not buyer purity theater.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "nisaba-action-os-v1"
INVENTOR = "Nisaba LLC"

THESIS = (
    "We serve everybody. Economies, politicians, companies — any entity "
    "that moves irreversible authority. Controversial or not: that is nature "
    "when you sit on the act. Palantir made knowing cheaper. Nisaba is the "
    "Action OS — governable irreversible action."
)

EQUIVALENT = {
    "palantir": {
        "job": "data integration",
        "bite": "fuse silos so power can see and act faster",
        "controversy": "willing to be the tool inside hard institutional loops",
    },
    "nisaba": {
        "job": "Action OS",
        "bite": "fail-closed mouth before wire, bind, payout, force",
        "controversy": "DENY/DEAD is a political–economic event for whoever we serve",
    },
}

SERVE = (
    {
        "id": "economies",
        "who": "Economies · treasuries · payment and settlement rails",
        "act": "Clear or halt irreversible money movement before the write completes",
    },
    {
        "id": "politicians",
        "who": "Politicians · states · public institutions",
        "act": "Permission mortality on authority that spends, binds, or forces",
    },
    {
        "id": "companies",
        "who": "Companies · carriers · platforms · operators",
        "act": "One welded door on licensed payout or bind-only — register on cleared flow",
    },
    {
        "id": "any_entity",
        "who": "Any entity whose write is irreversible",
        "act": "Same mouth. Same CHARGE. Same stranger verify. No soft-yes for nice buyers only",
    },
)

FAMILY = (
    {
        "name": "Erra",
        "question": "Should we act?",
        "rail": "signal · ACT / HOLD",
        "url": "https://velaru.xyz/erra",
    },
    {
        "name": "Velaru",
        "question": "Did we commit correctly?",
        "rail": "proof · ALLOW / BLOCK",
        "url": "https://velaru.xyz",
    },
    {
        "name": "Gate",
        "question": "Does the irreversible write complete?",
        "rail": "mouth · /v1/act · CHARGE · weld",
        "url": None,  # filled with public_url
    },
    {
        "name": "Verra",
        "question": "Did both rails clear before bind?",
        "rail": "action session",
        "url": "https://velaru.xyz/verra",
    },
    {
        "name": "Mishara",
        "question": "Was a person harmed?",
        "rail": "consumer harm path",
        "url": "https://mishara.onrender.com",
    },
)

NATURE = (
    "Sitting on the write means serving entities that conflict. Neutrality is fake.",
    "Controversy is structural — not dark copy, not founder cosplay.",
    "Hands dirty = welded on their irreversible path. Hands clean = CHARGE-only LIVE.",
    "We do not refuse the category. We refuse soft-yes resurrection and forged LIVE.",
)

INTEGRITY = (
    "CHARGE is the only DEAD→LIVE path — payer cannot buy a dashboard flip",
    "Stranger verify without login — exterior audit of the mouth",
    "One exclusive door per weld — no bypass UI / renewal / second write",
    "Fail closed on DEAD / timeout / 5xx — never treat UNREACHABLE as LIVE",
    "their_production stays false until a real production weld exists",
)

NOT = (
    "Palantir logo cosplay or claimed contracts we do not have",
    "Edge homepage as the product",
    "AI governance inventory that never sits on the write",
    "Serving only 'ethical' buyers while soft-yesing the rest",
    "Action OS marketing with no ACT/HOLD · ALLOW/BLOCK · /v1/act behavior",
)

OPERATIONAL = (
    {"surface": "POST /v1/act", "why": "Welded closed-world act — hop first, DEAD never acts"},
    {"surface": "POST /demo/hop", "why": "Public drill — proof without API key theater"},
    {"surface": "CHARGE webhook", "why": "Only regime change from DEAD→LIVE"},
    {"surface": "/.well-known/*.json", "why": "Machine-readable mouth — ops room without wallpaper"},
    {"surface": "/register", "why": "10 bps + management — infrastructure fees, not SaaS seats"},
    {"surface": "/operator", "why": "Weld checkout — human commits before production mouth"},
    {"surface": "https://velaru.xyz/verify", "why": "Stranger proof — neither party forges alone"},
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    family = []
    for f in FAMILY:
        row = dict(f)
        if row["name"] == "Gate":
            row["url"] = base or None
        family.append(row)
    return {
        "spec": SPEC,
        "name": "Nisaba Action OS",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "thesis": THESIS,
        "equivalent": EQUIVALENT,
        "serve": list(SERVE),
        "family": family,
        "nature": list(NATURE),
        "integrity": list(INTEGRITY),
        "not": list(NOT),
        "operational": [
            {
                **op,
                "href": (
                    f"{base}{op['surface']}"
                    if op["surface"].startswith("/")
                    else op["surface"]
                ),
            }
            for op in OPERATIONAL
        ],
        "one_liner": (
            "Palantir integrates data. Nisaba is the Action OS. "
            "We serve everybody — controversy is nature on the irreversible act."
        ),
        "ads": (
            "We serve economies, politicians, companies — any entity on the write. "
            "Fail closed. CHARGE only. Stranger verify."
        ),
        "links": {
            "register": f"{base}/register",
            "operator": f"{base}/operator",
            "act": f"{base}/v1/act",
            "gate": f"{base}/.well-known/gate.json",
            "positioning": f"{base}/.well-known/positioning.json",
            "erra": "https://velaru.xyz/erra",
            "verra": "https://velaru.xyz/verra",
            "velaru": "https://velaru.xyz",
            "verify": "https://velaru.xyz/verify",
        },
        "page": f"{base}/action-os",
        "their_production": False,
        "gatekeep": "Proprietary Nisaba Action OS doctrine. Ours.",
    }


def page_blocks() -> list[dict[str, Any]]:
    """HTML blocks — who we serve."""
    return [
        {
            "tag": "Serve",
            "title": s["who"],
            "body": s["act"],
            "id": s["id"],
        }
        for s in SERVE
    ]
