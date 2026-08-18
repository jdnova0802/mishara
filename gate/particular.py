"""A particular — not a deeper idea. An event.

Philosophy names the floor and Tuesday does not move. What's more is one dated
instance: this path, this moment, this someone, this no that sat.

You do not ask the particular. You put it on a path where yes would spend
someone else's world, and yes is not allowed without live permission.

Name one. Remove the other doors. Let it try to spend. The check is an act.
If it's already spent: don't interpret. Date it, sign it, let a stranger
open it, hand it to the someone who has to live there.

Ask nothing of the actor. Make the particular answer by trying.
Gate will not claim that their Tuesday moved.
"""
from __future__ import annotations

SPEC = "gate-particular-v1"
NOT_AI = "Not 'AI'. This fuse. This job. This bind."
WORK = "the gate firing for this one, before the spend, with no bypass"


def _hop(payload: dict) -> dict:
    inner = payload.get("hop")
    return inner if isinstance(inner, dict) else payload


def name_one(payload: dict | None) -> dict:
    payload = payload if isinstance(payload, dict) else {}
    hop = _hop(payload)
    fuse_id = str(payload.get("fuse_id") or hop.get("fuse_id") or "").strip()
    if fuse_id.lower() in {"ai", "an ai", "the ai", "agent"}:
        fuse_id = ""
    job_id = payload.get("job_id")
    if job_id is not None:
        job_id = str(job_id).strip() or None
    action = payload.get("action")
    if action is not None:
        action = str(action).strip()[:128] or None
    return {
        "fuse_id": fuse_id or None,
        "job_id": job_id,
        "action": action,
        "not": "AI",
    }


def classify(
    payload: dict | None,
    bound_answer: dict | None,
    exclusive_timing: dict | None,
    *,
    demo: bool = False,
) -> dict:
    payload = payload if isinstance(payload, dict) else {}
    ba = bound_answer if isinstance(bound_answer, dict) else {}
    ex = exclusive_timing if isinstance(exclusive_timing, dict) else {}
    named = name_one(payload)
    spend_path = ba.get("write_path") or named.get("action")
    on_door = bool(
        ex.get("closed_world") or ex.get("exclusive_if_honored") or ba.get("write_path")
    )
    has_name = bool(named.get("fuse_id")) and bool(named.get("job_id") or named.get("action"))
    particular = has_name and on_door
    philosophizing = not particular
    drill = bool(demo or ex.get("museum"))
    tried = particular
    return {
        "spec": SPEC,
        "name_one": named,
        "particular": particular,
        "philosophizing": philosophizing,
        "drill": drill,
        "spend_path": spend_path,
        "this_one_tried": tried,
        "tuesday_moved": False,
        "check_is_an_act": True,
        "ask_nothing_of_the_actor": True,
        "work": WORK if particular else "still a label until this one tries to spend",
        "event": (
            "this one tried to spend. the gate fired."
            if tried
            else None
        ),
        "already_spent": (
            "don't interpret. date, sign, stranger-verify, hand to the someone who has to live there."
        ),
        "not": NOT_AI,
    }


def from_event(row: dict) -> dict:
    """Appendix item: a dated instance, not a prompt."""
    return {
        "spec": SPEC,
        "id": row.get("id"),
        "created_at": row.get("created_at"),
        "name_one": {
            "fuse_id": row.get("fuse_id"),
            "job_id": row.get("job_id"),
            "not": "AI",
        },
        "decision": row.get("decision"),
        "acted": row.get("acted"),
        "verify_url": row.get("verify_url"),
        "tuesday_moved": False,
        "undeniable": bool(row.get("verify_url") or row.get("created_at")),
    }


def manifesto(public_url: str) -> dict:
    return {
        "spec": SPEC,
        "worth_more_than_philosophy": "a particular that already spent the world — or was stopped before it did",
        "not_a_deeper_idea": True,
        "an_event": True,
        "do_not_ask_the_particular": True,
        "put_it_on_a_path": (
            "Yes would spend someone else's world. Yes is not allowed without live permission."
        ),
        "that_looks_like": [
            "Name one. This agent. This bind. This job. Not 'AI'.",
            "Remove the other doors. If they can skip you, you are still philosophizing.",
            "Let the particular try to spend. Hop, bind, send, deploy. The check is an act, not a prompt.",
            "If it's already spent: don't interpret. Dated, signed, stranger-verifiable. Hand it to the someone who has to live there.",
        ],
        "label": "Can this agent still act right now? That's a label on a gate.",
        "work": WORK,
        "ask_nothing_of_the_actor": True,
        "make_the_particular_answer_by_trying": True,
        "tuesday_moved": False,
        "try": f"POST {public_url}/demo/pas/policycenter/pre-bind",
        "appendix": f"GET {public_url}/v1/pas/bind-appendix",
        "page": f"{public_url}/this",
        "floor": f"{public_url}/floor",
        "bind_room": f"{public_url}/bind-room",
    }
