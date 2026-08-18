"""A bound answer — more valuable than a question.

Cheap: "Is this agent safe?" → score, dashboard, PDF.
Bound: yes or no, on the write path, a stranger can open the receipt.

The stack already on Gate: question → four states → hop that fails closed → verify.
The prize is a no that holds.
"""
from __future__ import annotations

try:
    from gate import exclusive as exclusive_mod
except ImportError:
    import exclusive as exclusive_mod

try:
    from gate import floor as floor_mod
except ImportError:
    import floor as floor_mod

QUESTION = "Can this agent still act right now?"
SPEC = "gate-bound-answer-v1"
STACK = "question → four states → hop that fails closed → verify"
CHEAP = ["safety score", "dashboard warning", "trust-me PDF", "museum label"]


def _hop_of(payload: dict | None) -> dict:
    if not isinstance(payload, dict):
        return {}
    inner = payload.get("hop")
    if isinstance(inner, dict):
        return inner
    return payload


def _verify(hop: dict) -> str | None:
    url = hop.get("verify_url") or hop.get("restraint_permalink")
    return url if isinstance(url, str) and url else None


def from_payload(payload: dict | None, status: int, *, write_path: str | None = None) -> dict:
    """Narrow + enforced + provable. holds = the no sat on the hop or write."""
    payload = payload if isinstance(payload, dict) else {}
    hop = _hop_of(payload)
    unreachable = (
        status >= 500
        or hop.get("fail_closed") is True
        or hop.get("state") == "UNREACHABLE"
        or payload.get("fail_closed") is True
    )
    deadish = (
        unreachable
        or hop.get("halt") is True
        or payload.get("halt") is True
        or hop.get("verdict") is False
        or payload.get("allow_bind") is False
        or payload.get("bind_allowed") is False
    )

    if "allow_bind" in payload:
        answer = bool(payload.get("allow_bind"))
        acted = answer
    elif "bind_allowed" in payload:
        answer = bool(payload.get("bind_allowed"))
        acted = answer
    elif "acted" in payload and payload.get("acted") is not None:
        acted = bool(payload.get("acted"))
        answer = acted and not deadish
    else:
        answer = hop.get("verdict") is True and not deadish
        acted = False

    if payload.get("acted") is True and deadish:
        answer = False
        acted = True
    elif deadish and payload.get("acted") is not True:
        answer = False
        acted = False

    enforced = not (acted and not answer)
    holds = (not answer) and (not acted) and enforced
    verify = _verify(hop) or _verify(payload)
    nxt = payload.get("next") if isinstance(payload.get("next"), dict) else None
    refuse = payload.get("do_not_call") if isinstance(payload.get("do_not_call"), dict) else None
    path = write_path or (nxt or {}).get("path") or (refuse or {}).get("path")
    yes_bound = bool(answer) and (bool(verify) or bool(path))
    state = hop.get("state") or payload.get("state") or ("UNREACHABLE" if unreachable else None)

    return {
        "spec": SPEC,
        "question": QUESTION,
        "answer": bool(answer),
        "no": not bool(answer),
        "holds": bool(holds),
        "bound": bool(holds or yes_bound),
        "state": state,
        "acted": bool(acted),
        "verify_url": verify,
        "write_path": path,
        "tests": {
            "narrow": True,
            "enforced": bool(enforced),
            "provable": bool(verify) or unreachable,
        },
        "stack": STACK,
        "prize": "a no that holds" if holds else ("a bound yes" if yes_bound else None),
        "not": list(CHEAP),
    }


def attach(
    payload,
    status: int,
    *,
    write_path: str | None = None,
    demo: bool = False,
    closed_world: bool = False,
):
    if isinstance(payload, dict) and (
        payload.get("halt") is not None
        or payload.get("verdict") is not None
        or payload.get("allow_bind") is not None
        or payload.get("bind_allowed") is not None
        or payload.get("acted") is not None
        or payload.get("state")
        or isinstance(payload.get("hop"), dict)
    ):
        payload["bound_answer"] = from_payload(payload, status, write_path=write_path)
        payload["exclusive_timing"] = exclusive_mod.classify(
            payload, payload["bound_answer"], demo=demo, closed_world=closed_world
        )
        payload["stakes"] = floor_mod.stamp(payload["exclusive_timing"])
    return payload


def manifesto(public_url: str) -> dict:
    return {
        "spec": SPEC,
        "more_valuable_than_a_question": "a no that holds",
        "question": QUESTION,
        "cheap": "A question that cannot stop a write is a museum label.",
        "tests": {
            "narrow": "Yes or no. Not a score.",
            "enforced": "DEAD cannot act. Dashboard warning is not a no.",
            "provable": "A stranger opens the receipt. No login.",
        },
        "stack": STACK,
        "states": ["LIVE", "ARMED", "DEAD", "UNSIGNED"],
        "on_the_write_path": (
            "A DEAD hop that still lets bind-and-issue fire is a no that does not hold. "
            "Raise the Manual UW issue. Do not call bind-and-issue. CHARGE is the only resurrect."
        ),
        "demo": {
            "hop": f"POST {public_url}/demo/hop",
            "act": f"POST {public_url}/demo/act",
            "pre_bind": f"POST {public_url}/demo/pas/policycenter/pre-bind",
        },
        "page": f"{public_url}/bound",
        "deeper": f"{public_url}/only",
        "floor": f"{public_url}/floor",
        "bind_room": f"{public_url}/bind-room",
        "verify": "https://velaru.xyz/verify",
        "worth_more": "A bound answer can still be a museum. Exclusive timing is the only door.",
    }
