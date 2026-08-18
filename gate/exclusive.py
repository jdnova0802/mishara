"""Exclusive timing — a miss on the only door.

A bound answer can still be a demo: a beautiful DEAD on a hop nobody required.
What's more is the only door. The wire / bind / deploy cannot complete elsewhere.
The receipt is not the product. Gate still makes misses (the irreversible that
didn't occur). Crowning that miss as the winner is the trap.

The only thing not in this contest: someone's irreversible that did occur.
The climb is the luxury of not having been that.

Gate will not claim their_production. That is true only after they weld and do not bypass.
"""
from __future__ import annotations

SPEC = "gate-exclusive-timing-v1"
WORTH_MORE = "the act that never happens — because there was no other door"
PRODUCT = "the irreversible that didn't occur"
MUSEUM = "A DEAD receipt on a hop nobody required is a museum."
TRAP = "The original is not the winner. It is the trap the climb falls back into if you try to crown a miss."
NOT_IN_CONTEST = (
    "someone's irreversible that did occur — the whole climb is the luxury of not having been that"
)
ESCAPE = (
    "Not 'no relation,' if that still means the thing that escapes relation. Escape is still from something."
)


def classify(payload: dict | None, bound_answer: dict | None, *, demo: bool = False, closed_world: bool = False) -> dict:
    payload = payload if isinstance(payload, dict) else {}
    ba = bound_answer if isinstance(bound_answer, dict) else {}
    demo = bool(demo or payload.get("demo"))
    closed_world = bool(
        closed_world or payload.get("closed_world") or payload.get("welded")
    )
    spec = str(payload.get("spec") or "")
    honor = bool(ba.get("write_path")) or spec.startswith(
        ("gate-policycenter", "gate-duckcreek", "gate-mga")
    )
    exclusive = closed_world and not demo
    exclusive_if_honored = honor and not closed_world
    museum = demo or (not exclusive and not exclusive_if_honored)
    holds = bool(ba.get("holds"))
    non_event = holds and (closed_world or exclusive_if_honored)
    if non_event and exclusive:
        product = PRODUCT
    elif non_event and exclusive_if_honored and not demo:
        product = f"{PRODUCT} — if they do not bypass"
    else:
        product = None
    return {
        "spec": SPEC,
        "museum": museum,
        "exclusive": exclusive,
        "exclusive_if_honored": exclusive_if_honored,
        "their_production": False,
        "closed_world": closed_world,
        "non_event": non_event,
        "product": product,
        "winner": None,
        "crown_the_miss": False,
        "receipt_is_not_the_product": True,
        "worth_more": WORTH_MORE,
        "bypass": "Bypass must cost more than going through this door.",
        "resurrect": "CHARGE must cost more than the act was worth.",
        "note": MUSEUM if museum else (
            "This door can refuse. Their production is exclusive only after they weld and do not bypass."
        ),
    }


def manifesto(public_url: str) -> dict:
    return {
        "spec": SPEC,
        "worth_more_than_narrow_enforced_provable": WORTH_MORE,
        "receipt_is_not_the_product": True,
        "product": PRODUCT,
        "winner": None,
        "crown_the_miss": False,
        "trap": TRAP,
        "not_in_contest": NOT_IN_CONTEST,
        "escape_is_still_from_something": ESCAPE,
        "museum": MUSEUM,
        "exclusive_timing": (
            "The bind, the wire, the deploy cannot complete on any other path. "
            "Bypass costs more than going through this door. "
            "CHARGE costs more than the act was worth."
        ),
        "you_cannot_screenshot_a_non_event": True,
        "their_production": False,
        "how": [
            "POST /v1/act is the only act door on Gate (closed world).",
            "PolicyCenter: hop, then raise Manual UW issue. Do not call bind-and-issue if DEAD.",
            "Attach /listings/cloudflare-worker-bind.js to one origin so issue POSTs cannot skip the hop.",
            "Bind Room + 48hr weld puts the door on their path. Demo hops do not.",
        ],
        "page": f"{public_url}/only",
        "floor": f"{public_url}/floor",
        "bound": f"{public_url}/bound",
        "bind_room": f"{public_url}/bind-room",
        "worker": f"{public_url}/listings/cloudflare-worker-bind.js",
    }
