"""The inhabitant's copy — they did not have to ask.

Every other Gate artifact is for the actor's institution: carrier, UW,
auditor, congregation. The floor said the machinery exists because it
isn't only yours. Particular said: hand it to the someone who has to
live there. The worker promised verify_url so the inhabitant gets a
receipt without asking.

This is that copy. No name. No PII. No vote. Same event.

Two letters, neither crowned:
- spared: this bind did not happen
- spent: this one happened; we do not interpret it

Demo hops still mint a copy, marked museum. Lying to the inhabitant
would be the worse object.
"""
from __future__ import annotations

SPEC = "gate-inhabitant-v1"
AUDIENCE = "the someone who has to live there"
LETTER_SPARED = (
    "This bind did not happen. You did not get a vote. You did not need one. "
    "The no sat outside the actor."
)
LETTER_SPENT = (
    "This one happened. We do not interpret it. It is dated. A stranger can open it. "
    "You are the someone who has to live there."
)
LETTER_RECORDED = "This hop was recorded. A stranger can open it."
DRILL_FUSE = "fuse_velaru_drill"


def is_spared(row: dict | None) -> bool:
    row = row if isinstance(row, dict) else {}
    if row.get("acted") is True:
        return False
    return (row.get("decision") or "").upper() in ("HALT", "BLOCK")


def is_spent(row: dict | None) -> bool:
    row = row if isinstance(row, dict) else {}
    if row.get("acted") is True:
        return True
    return (row.get("decision") or "").upper() == "ALLOW"


def is_museum(row: dict | None) -> bool:
    row = row if isinstance(row, dict) else {}
    hop = row.get("hop") if isinstance(row.get("hop"), dict) else {}
    fuse = (row.get("fuse_id") or hop.get("fuse_id") or "").strip()
    return fuse == DRILL_FUSE or bool(hop.get("demo") or row.get("demo"))


def for_event(row: dict | None, public_url: str) -> dict:
    row = row if isinstance(row, dict) else {}
    event_id = row.get("id")
    spared = is_spared(row)
    spent = is_spent(row)
    if spared:
        letter = LETTER_SPARED
    elif spent:
        letter = LETTER_SPENT
    else:
        letter = LETTER_RECORDED
    page = f"{public_url}/inhabitant/{event_id}" if event_id else f"{public_url}/inhabitant"
    receipt = (
        f"{public_url}/.well-known/receipt/{event_id}.json" if event_id else None
    )
    return {
        "spec": SPEC,
        "audience": AUDIENCE,
        "they_did_not_have_to_ask": True,
        "name": None,
        "pii": False,
        "vote": False,
        "needed_a_vote": False,
        "spared": spared,
        "spent": spent,
        "letter": letter,
        "event_id": event_id,
        "created_at": row.get("created_at"),
        "verify_url": row.get("verify_url"),
        "receipt": receipt,
        "page": page,
        "museum": is_museum(row),
        "winner": None,
        "crown_the_miss": False,
        "not_only_yours": True,
        "their_production": False,
        "not_in_contest": "someone's irreversible that did occur",
    }


def attach_to_receipt_payload(payload: dict, row: dict, public_url: str) -> dict:
    payload["inhabitant"] = for_event(row, public_url)
    return payload


def urls(public_url: str, event_id: str | None = None) -> dict:
    page = f"{public_url}/inhabitant/{event_id}" if event_id else f"{public_url}/inhabitant"
    return {
        "page": page,
        "manifest": f"{public_url}/.well-known/inhabitant.json",
        "letter": (
            f"{public_url}/.well-known/inhabitant/{event_id}.json" if event_id else None
        ),
    }


def manifest(public_url: str) -> dict:
    return {
        "spec": SPEC,
        "name": "Inhabitant copy",
        "audience": AUDIENCE,
        "they_did_not_have_to_ask": True,
        "why": (
            "Yes spends a world. The person who inhabits the spent world usually "
            "didn't get the vote. This copy is for them. They do not have to ask."
        ),
        "no_name": True,
        "no_pii": True,
        "letters": {
            "spared": LETTER_SPARED,
            "spent": LETTER_SPENT,
        },
        "page": f"{public_url}/inhabitant",
        "letter": f"{public_url}/inhabitant/{{event_id}}",
        "json": f"{public_url}/.well-known/inhabitant/{{event_id}}.json",
        "winner": None,
        "crown_the_miss": False,
        "their_production": False,
    }
