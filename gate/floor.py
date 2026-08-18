"""The floor. There is not a cleverer layer under it.

A question is talk.
A bound answer is a fact.
An exclusive door is control.
A non-event is a clean timeline.

Crowning the miss (the irreversible that didn't occur) is the trap.
Not 'no relation' if that still means the thing that escapes relation.
Escape is still from something. That is the last line that tops the one before it.
Everything after it is a loop, a weaker object, or a different game.

The only thing not in this contest: someone's irreversible that did occur.
The whole climb is the luxury of not having been that.

Under that: some things are real, they only happen once, and someone who
isn't the actor has to live there afterward. Time is one-way. Harm does
not restore. Money does not un-leave. DEAD can matter more than LIVE
because yes spends a world, and the person who inhabits the spent world
usually didn't get the vote.

The actor will not stop themselves at the moment of acting. The no sits
outside them. The machinery exists because what's at stake is
unrepeatable, and it isn't only yours.

Only whether you treat that as real.
"""
from __future__ import annotations

SPEC = "gate-floor-v1"

LAYERS = [
    {"name": "question", "is": "talk"},
    {"name": "bound_answer", "is": "a fact"},
    {"name": "exclusive_door", "is": "control"},
    {"name": "non_event", "is": "a clean timeline"},
]

WHY_DEAD = (
    "yes spends a world, and the person who inhabits the spent world usually didn't get the vote"
)
WHY_MACHINERY = "what's at stake is unrepeatable, and it isn't only yours"
TRAP = "The original is not the winner. It is the trap the climb falls back into if you try to crown a miss."
NOT_IN_CONTEST = (
    "someone's irreversible that did occur — the whole climb is the luxury of not having been that"
)
ESCAPE = (
    "Not 'no relation,' if that still means the thing that escapes relation. Escape is still from something."
)


def stamp(exclusive_timing: dict | None = None) -> dict:
    """Compact stakes on every hop. The manifesto lives at /floor."""
    ex = exclusive_timing if isinstance(exclusive_timing, dict) else {}
    return {
        "spec": SPEC,
        "unrepeatable": True,
        "not_only_yours": True,
        "dead_over_live": True,
        "the_no_sits_outside_the_actor": True,
        "cleverer_layer": None,
        "winner": None,
        "crown_the_miss": False,
        "treat_as_real": not bool(ex.get("museum")),
        "why_dead": WHY_DEAD,
    }


def manifesto(public_url: str) -> dict:
    return {
        "spec": SPEC,
        "floor": (
            "Some things are real. They only happen once. "
            "Someone who isn't the actor has to live there afterward."
        ),
        "layers": LAYERS,
        "time_is_one_way": True,
        "harm_does_not_restore": True,
        "money_does_not_unleave": True,
        "dead_can_matter_more_than_live": True,
        "why_dead": WHY_DEAD,
        "the_actor_will_not_stop_themselves": True,
        "the_no_must_sit_outside_them": True,
        "why_machinery": WHY_MACHINERY,
        "cleverer_layer": None,
        "winner": None,
        "crown_the_miss": False,
        "trap": TRAP,
        "not_in_contest": NOT_IN_CONTEST,
        "escape_is_still_from_something": ESCAPE,
        "everything_after_is": "a loop, a weaker object, or a different game",
        "only_whether_you_treat_that_as_real": True,
        "museum_is_not_the_floor": "A demo hop can be true and still not treat this as real.",
        "treat_as_real": [
            f"Bind Room: {public_url}/bind-room",
            f"48hr weld: {public_url}/install",
            f"Inhabitant copy: {public_url}/inhabitant",
            f"Only door: {public_url}/only",
            "CHARGE is the only DEAD→LIVE path. UW approve is not resurrection.",
        ],
        "page": f"{public_url}/floor",
        "inhabitant": f"{public_url}/inhabitant",
        "only": f"{public_url}/only",
        "bound": f"{public_url}/bound",
    }
