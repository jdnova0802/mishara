"""STIT hop particles — nested agency is unsat; NON-ACT names the settler.

Independent agents cannot see-to-it that another sees-to-it.
When the otherwise is collapsed, liability does not vanish: it reverts
to whoever locked the histories.
"""
from __future__ import annotations

from typing import Any

SPEC_NESTED = "gate-nested-stit-v1"
SPEC_SETTLER = "gate-settler-v1"
INVARIANT_NESTED = (
    "Independent agents cannot nested-STIT. "
    "i sees-to-it that j sees-to-it that A is unsatisfiable."
)
INVARIANT_SETTLER = (
    "NON-ACT does not erase the bag. The settler is who collapsed the otherwise."
)


def _id(raw: Any) -> str:
    return str(raw or "").strip()


def nested_stit(
    *,
    actor: str | None,
    principal: str | None,
    claims_nested: bool = False,
) -> dict[str, Any]:
    """Principal cannot wear the agent's seeing-to-it as their own act."""
    a = _id(actor)
    p = _id(principal)
    distinct = bool(a and p and a != p)
    # Nested STIT is unsat whenever two different agents are on the hop.
    unsat = distinct
    claimed = bool(claims_nested) or distinct
    return {
        "spec": SPEC_NESTED,
        "delegated": False,
        "nested_possible": not unsat,
        "misfire": unsat and claimed,
        "actor": a or None,
        "principal": p or None,
        "invariant": INVARIANT_NESTED,
        "not": "A mandate, wrap SDK, or 'we delegated to the agent' board slide.",
    }


def settler(
    *,
    agency: str,
    open_count: int,
    policy: dict | None,
    context: dict | None,
    body: dict | None,
) -> dict[str, Any] | None:
    """Who locked the histories. Only named when agency is NON-ACT."""
    if agency != "NON-ACT":
        return None
    ctx = context if isinstance(context, dict) else {}
    pol = policy if isinstance(policy, dict) else {}
    b = body if isinstance(body, dict) else {}
    named = _id(
        ctx.get("settler_id")
        or b.get("settler_id")
        or pol.get("settler_id")
        or ctx.get("charge_id")
    )
    if named:
        kind = "named"
        settler_id = named
    elif int(open_count or 0) == 1:
        kind = "allowlist"
        allowed = pol.get("allowed_actions") or pol.get("actions") or []
        settler_id = "policy:allowlist:" + ",".join(
            str(x).strip() for x in allowed if str(x).strip()
        ) or "policy:allowlist"
    elif int(open_count or 0) == 0:
        kind = "policy"
        settler_id = "policy:no_open_write"
    else:
        kind = "unknown"
        settler_id = "unknown"
    return {
        "spec": SPEC_SETTLER,
        "kind": kind,
        "settler_id": settler_id,
        "open_count": int(open_count or 0),
        "invariant": INVARIANT_SETTLER,
    }
