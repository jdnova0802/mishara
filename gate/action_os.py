"""Nisaba Action OS — company nature, not homepage theater.

Formula:
  Own permission on irreversible acts for any power that needs it —
  and make your scarcity the DENY, not the narrative.

Palantir integrates data so institutions can know faster.
Nisaba sits on irreversible action: should this act run?

We serve everybody — economies, politicians, companies, any entity
whose write moves capital, coverage, or force. Controversy is nature
when DENY/DEAD is a real event. Integrity is CHARGE-only, stranger
verify, one door, fail-closed — not buyer purity theater.

Force / battlefield authority is in the category. It is not a claimed
production weld until someone pays for that door.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "nisaba-action-os-v2"
INVENTOR = "Nisaba LLC"

FORMULA = (
    "Own permission on irreversible acts for any power that needs it — "
    "and make your scarcity the DENY, not the narrative."
)

THESIS = (
    "We serve everybody. Economies, politicians, companies — any entity "
    "that moves irreversible authority. Controversial or not: that is nature "
    "when you sit on the act. Palantir made knowing cheaper. Nisaba is the "
    "Action OS — governable irreversible action. Scarcity is the DENY."
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
        "scarcity": "the halt — not the story about the halt",
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
        "id": "force",
        "who": "Force · defense · public-safety irreversible release",
        "act": (
            "Same mouth class: does the irreversible release complete? "
            "In category under serve-everybody. Not a claimed production weld today."
        ),
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
    "Scarcity is DENY/DEAD that holds — narrative without a halt is SaaS.",
)

INTEGRITY = (
    "CHARGE is the only DEAD→LIVE path — payer cannot buy a dashboard flip",
    "Stranger verify without login — exterior audit of the mouth",
    "One exclusive door per weld — no bypass UI / renewal / second write",
    "Fail closed on DEAD / timeout / 5xx — never treat UNREACHABLE as LIVE",
    "their_production stays false until a real production weld exists",
    "Force/battlefield doors stay unclaimed until welded — category ≠ costume",
)

NOT = (
    "Palantir logo cosplay or claimed contracts we do not have",
    "Edge homepage as the product",
    "AI governance inventory that never sits on the write",
    "Serving only 'ethical' buyers while soft-yesing the rest",
    "Action OS marketing with no ACT/HOLD · ALLOW/BLOCK · /v1/act behavior",
    "Battlefield marketing without a force-path weld",
    "Scarcity as storytelling — DENY that does not hold",
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

PLAYBOOK = (
    "Sit on irreversible acts, not content or dashboards",
    "Serve any power that needs the door — without letting them forge LIVE",
    "Be Action OS (permission on the act), not data-integration cosplay",
    "One welded door beats a SKU buffet — expand mouths after the first cannot be bypassed",
    "Make absence audible — receipts for what did not happen, stranger verify, public nos",
    "Sell to owners of the write — operators, treasuries, carriers, states — not vibe buyers",
    "Let DENY do the talking — nature over narrative",
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
        "formula": FORMULA,
        "thesis": THESIS,
        "scarcity": "DENY/DEAD that holds — not the narrative about the product",
        "equivalent": EQUIVALENT,
        "serve": list(SERVE),
        "family": family,
        "nature": list(NATURE),
        "integrity": list(INTEGRITY),
        "not": list(NOT),
        "playbook": list(PLAYBOOK),
        "category_includes_force": True,
        "force_production_weld": False,
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
        "one_liner": FORMULA,
        "ads": (
            "Own the door on irreversible acts. Scarcity is the DENY. "
            "We serve everybody. Fail closed. CHARGE only. Stranger verify."
        ),
        "links": {
            "scorecard": f"{base}/scorecard",
            "register": f"{base}/register",
            "operator": f"{base}/operator",
            "science": f"{base}/science",
            "science_pri": f"{base}/.well-known/science-pri.json",
            "unison": f"{base}/.well-known/unison.json",
            "unison_page": f"{base}/unison",
            "act": f"{base}/v1/act",
            "demo_hop": f"{base}/demo/hop",
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
