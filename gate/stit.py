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


def _self_named(named: str) -> bool:
    n = named.strip().lower()
    if n in {"unknown", "nobody", "policy", "allowlist", "gap", "the policy"}:
        return True
    return n.startswith("policy:") or n.startswith("allowlist:")


def nested_stit(
    *,
    actor: str | None,
    principal: str | None,
    claims_nested: bool = False,
    principals: list | None = None,
) -> dict[str, Any]:
    """Principal cannot wear the agent's seeing-to-it as their own act.

    Org charts are not two-deep. Any second distinct mouth on the hop is unsat.
    """
    a = _id(actor)
    p = _id(principal)
    extra = [_id(x) for x in (principals or []) if _id(x)]
    mouths = [x for x in [a, p, *extra] if x]
    distinct = len(set(mouths)) > 1
    unsat = distinct
    claimed = bool(claims_nested) or distinct
    return {
        "spec": SPEC_NESTED,
        "delegated": False,
        "nested_possible": not unsat,
        "misfire": unsat and claimed,
        "actor": a or None,
        "principal": p or None,
        "principals": extra or None,
        "depth": len(set(mouths)),
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
        or pol.get("owner_id")
        or pol.get("authored_by")
    )
    if named and _self_named(named):
        kind = "spoof"
        settler_id = named
        owned = False
        gap = True
        gap_reason = "self_named"
    elif named:
        kind = "named"
        settler_id = named
        owned = True
        gap = False
        gap_reason = None
    elif int(open_count or 0) == 1:
        kind = "allowlist"
        allowed = pol.get("allowed_actions") or pol.get("actions") or []
        settler_id = "policy:allowlist:" + ",".join(
            str(x).strip() for x in allowed if str(x).strip()
        ) or "policy:allowlist"
        owned = False
        gap = True
        gap_reason = "unowned_policy"
    elif int(open_count or 0) == 0:
        kind = "policy"
        settler_id = "policy:no_open_write"
        owned = False
        gap = True
        gap_reason = "unowned_policy"
    else:
        kind = "unknown"
        settler_id = "unknown"
        owned = False
        gap = True
        gap_reason = "nobody"
    return {
        "spec": SPEC_SETTLER,
        "kind": kind,
        "settler_id": settler_id,
        "owned": owned,
        "gap": gap,
        "gap_reason": gap_reason,
        "open_count": int(open_count or 0),
        "invariant": INVARIANT_SETTLER,
        "not": "A vendor default, inherited allowlist, or 'the policy' as a person.",
    }
