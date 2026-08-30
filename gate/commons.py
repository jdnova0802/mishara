"""Incident Remaining Commons — Ostrom pool. You operate. You do not found.

July's unpaid object: incident-data pooling for the agent-insurance stack.
Cold-start public good. No single carrier funds the pool alone. Once it
exists, every member pays annually forever — not one deployer's renewal.

Honest locks (do not violate):
- Consortiums are convened by standing (trade body, regulator, large carrier).
  The vendor is appointed technical operator. Do not sell "join my consortium."
- No data, no convening. Pilots produce seed. Bind / Finished / Standing
  fund the concentration problem. The commons is the exit from one bad
  renewal, not a skip around Gate 1.
- Do not become the carrier. Do not become AIUC. Do not sell may.
- Closed Claims / UL origin: conveners with skin, a lab/secretariat that
  holds the books. Nisaba is the lab, not the chair.

Not a sixth sibling. Not a /for/ plate. Not Being-as-SKU.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

try:
    from gate import inventor as inventor_mod
except ImportError:
    import inventor as inventor_mod

try:
    from gate import remaining as remaining_mod
except ImportError:
    import remaining as remaining_mod

try:
    from gate import restraint as restraint_mod
except ImportError:
    import restraint as restraint_mod

SPEC = "gate-incident-remaining-commons-v1"
FAMILY_SIBLINGS_REMAIN = 5
L2_MODULE = False
CLEVERER_LAYER = None
PAYEE = "Nisaba LLC"
NO_SPLIT = True

OPERATOR_LABEL = "$150,000/yr"
OPERATOR_CENTS = 15_000_000
OPERATOR_SKU = "operator_of_record"
ASSESSMENT_LABEL = "$50,000/yr"
ASSESSMENT_CENTS = 5_000_000

IDENTITY = "incident remaining is a commons — we operate, we do not convene"

INVENTION = (
    "Pooled incident remaining: given / spent one-wayness / HALT-or-silence "
    "after an agent write, stripped of PII, stranger-openable. Not claims PDFs. "
    "Not a system badge. An Ostrom commons of the world after incidents. "
    "Nisaba is the technical operator when a convener with standing appoints. "
    "Members who do not contribute do not query."
)

EMAIL_LINE = (
    "Don't buy a consortium from a vendor. Appoint Nisaba as technical operator "
    "of the incident-remaining pool — $150,000/yr. Closed Claims shape: once "
    "it exists, members pay annually forever. Seed comes from pilots, not a pitch."
)

OSTROM: dict[str, str] = {
    "boundaries": "Members who contribute incident remaining. Non-members do not query.",
    "congruence": "Agent E&O / CG 40 47 remaining — not medical closed-claims cosplay.",
    "collective_choice": "Convener chairs the levy. Operator does not vote its own rent.",
    "monitoring": "Stranger-openable remaining. Fake seed fails identity_holds.",
    "sanctions": "No contribute → no query. Graduated: warn, suspend, expel.",
    "conflict": "Recused mouth. CHARGE-outside. Actor cannot self-wipe an incident.",
    "recognition": "Trade body / regulator / large carrier convenes. Vendor does not.",
    "nested": "Nisaba operates under the convener. Never the chair. Never the carrier.",
}

HONEST: dict[str, str] = {
    "not_the_founder": (
        "Consortiums are almost never founded by the vendor. "
        "Get named operator of one somebody else is forming."
    ),
    "no_skip": (
        "You cannot convene without data. Pilots produce it. "
        "This does not skip one-deployer concentration — it is what concentration funds."
    ),
    "exit_not_onramp": (
        "The commons is the exit from being one bad renewal away from zero. "
        "It is not a way around Gate 1."
    ),
}

PRINT = {
    "first_dollar": {
        "engine": "named technical operator",
        "unit": OPERATOR_LABEL,
        "who": "Convener with standing (carrier, trade body, regulator-adjacent)",
        "this_month": False,
        "until_gate1_usd": 0,
    },
    "forever_levy": {
        "engine": "member assessment — Closed Claims shape",
        "unit": ASSESSMENT_LABEL,
        "n_for_10m": 200,
        "why_forever": "Payments are not tied to one platform's renewal. Leave the pool, lose the book.",
    },
    "nine_figure": {
        "engine": "no pool query, no bind — commons as forced input to insurability",
        "attach": "S4 insurability gate × pool as the loss table underwriters cite",
        "shape": "5–15% evidence rent on agent E&O premium once the pool is the default table",
        "honest": "Needs a convener + seed + Schelling. Not a September wire.",
    },
    "seed": {
        "from": ("bind_room", "finished_remaining", "standing_remaining", "restraint_halt"),
        "what": "Stripped remaining + HALT class. No PII. No job_id outbound.",
    },
}


def ostrom() -> dict[str, str]:
    return dict(OSTROM)


def stripe_line_item() -> dict[str, Any]:
    return {
        "price_data": {
            "currency": "usd",
            "unit_amount": OPERATOR_CENTS,
            "recurring": {"interval": "year"},
            "product_data": {
                "name": "Incident Remaining Commons — technical operator of record",
                "description": (
                    "Appointed operator of a convener-chaired incident-remaining pool. "
                    "Not a consortium for sale. Not the carrier."
                ),
            },
        },
        "quantity": 1,
    }


def seed(job_id: str, public_url: str = "") -> dict[str, Any]:
    """What a pilot puts in the pool. Stripped. Not a claim file."""
    folio = remaining_mod.folio((job_id or "").strip())
    remaining = folio.get("remaining") or {}
    given = folio.get("given") or {}
    act = folio.get("act") or {}
    return {
        "spec": SPEC,
        "kind": "incident_remaining_seed",
        "inventor": inventor_mod.stamp(),
        "pii": False,
        "job_id": None,
        "identity": remaining_mod.IDENTITY,
        "one_way_class": remaining.get("one_way_class"),
        "identity_holds": folio.get("identity_holds"),
        "given_absent": given.get("absent"),
        "act_occurred": act.get("occurred"),
        "one_way_spent": remaining.get("one_way_spent"),
        "for": remaining.get("for"),
        "not_for": remaining.get("not_for"),
        "restraint": {
            "what": restraint_mod.inventory(public_url or "https://example.invalid", limit=1).get("what"),
            "pii": False,
        },
        "not": [
            "a claims PDF",
            "PII",
            "a job_id",
            "an AIUC system badge",
            "a consortium you founded",
        ],
        "ostrom_monitoring": True,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }


def seed_near_miss(job_id: str, public_url: str = "") -> dict[str, Any]:
    """The only layer anyone will contribute: nobody is suing yet. ASRS shape."""
    row = seed(job_id, public_url)
    row["kind"] = "near_miss_remaining_seed"
    row["incident"] = False
    row["near_miss"] = True
    row["not_a_claim"] = True
    row["not_discoverable_as_incident"] = True
    row["why_contributable"] = "nobody is suing yet — aviation ASRS shape"
    row["not"] = list(row.get("not") or []) + ["an incident file", "a lawsuit exhibit"]
    return row


def can_query(*, contributed: bool) -> dict[str, Any]:
    """Free-rider exclusion. The padlock of the commons."""
    return {
        "spec": SPEC,
        "kind": "commons_query_gate",
        "contributed": bool(contributed),
        "may_query": bool(contributed),
        "sanction": None if contributed else "no_contribute_no_query",
        "operator_does_not_waive": True,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Incident Remaining Commons",
        "inventor": inventor_mod.stamp(),
        "identity": IDENTITY,
        "thesis": INVENTION,
        "email_line": EMAIL_LINE,
        "ostrom": ostrom(),
        "honest": dict(HONEST),
        "print": dict(PRINT),
        "payee": PAYEE,
        "no_split": NO_SPLIT,
        "connect": False,
        "we_do_not_convene": True,
        "we_do_not_carry_risk": True,
        "not_aiuc": True,
        "sku": {
            "id": OPERATOR_SKU,
            "name": "Technical operator of record",
            "label": OPERATOR_LABEL,
            "cents": OPERATOR_CENTS,
            "interval": "year",
            "who": "Convener with standing appointing an operator — not a deployer renewing a pack",
            "deliverable": (
                "Operator-of-record for the incident-remaining pool: seed ingest, "
                "identity_holds monitoring, free-rider exclusion, stranger-openable "
                "query for members. Convener chairs. Nisaba does not vote the levy."
            ),
        },
        "assessment_after_convening": {
            "label": ASSESSMENT_LABEL,
            "cents": ASSESSMENT_CENTS,
            "checkout": False,
            "why_not_yet": "No levy without a named convener and a live pool. Do not fake members.",
        },
        "family_siblings_remain": FAMILY_SIBLINGS_REMAIN,
        "l2_module": L2_MODULE,
        "cleverer_layer": CLEVERER_LAYER,
        "not_museum": True,
        "civilizational": True,
        "prints_when": "a convener appoints — then members pay forever",
        "cash_door": f"{base}/commons",
        "checkout": f"{base}/commons/checkout",
        "links": {
            "page": f"{base}/commons",
            "restraint": f"{base}/.well-known/restraint.json",
            "remaining": f"{base}/remaining",
            "finished": f"{base}/finished",
            "standing": f"{base}/standing",
            "general": f"{base}/general",
            "bind_room": f"{base}/bind-room",
        },
        "page": f"{base}/commons",
        "gatekeep": (
            "Commons operator door. Not a consortium for sale. "
            "Not a /for/ plate. Not a sixth sibling. Not the carrier."
        ),
    }
