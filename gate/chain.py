"""Chain witness — a hop inherits the weakest claim it stood on.

One airtight receipt that is silent about a rotten upstream is not honest.
"""
from __future__ import annotations

from typing import Any, Callable

SPEC = "gate-chain-v1"
INVARIANT = "A clean hop on a rotten upstream is still rotten."
MAX_UPSTREAM = 16
GRADES = ("CLEAN", "STAINED", "ROTTEN")

_STAIN_MUT = frozenset({"DOWN", "UP", "DIFF", "UNWRITTEN"})
_ROTTEN_DEC = frozenset({"NONEXIST", "HOLD"})


def _s(raw: Any) -> str:
    return str(raw or "").strip()


def claim_from_payload(payload: dict | None) -> dict[str, Any]:
    p = payload if isinstance(payload, dict) else {}
    decision = _s(p.get("dec") or p.get("decision")).upper() or "EXIST"
    iaa = _s(p.get("iaa") or p.get("in_authority")).upper() or "UNKNOWN"
    agency = _s(p.get("agc") or p.get("agency")).upper() or "NON-ACT"
    mut = _s(p.get("mut") or p.get("mutation")).upper() or "ABSENT"
    stl = _s(p.get("stl") or p.get("settler_id"))
    gap = bool(p.get("gap")) or stl.upper() == "GAP"
    halt = bool(p.get("halt")) or decision in _ROTTEN_DEC or iaa == "OUT"
    unverified = bool(p.get("unverified"))
    if unverified:
        halt = True
    return {
        "agency": agency if agency in ("ACT", "NON-ACT") else "NON-ACT",
        "gap": gap,
        "mutation": mut if mut else "ABSENT",
        "in_authority": iaa if iaa in ("IN", "OUT", "UNKNOWN") else "UNKNOWN",
        "decision": decision if decision in ("EXIST", "NONEXIST", "HOLD") else "NONEXIST",
        "halt": halt,
        "unverified": unverified,
    }


def claim_from_result(out: dict | None) -> dict[str, Any]:
    o = out if isinstance(out, dict) else {}
    sl = o.get("signed_line") if isinstance(o.get("signed_line"), dict) else {}
    settler = o.get("settler") if isinstance(o.get("settler"), dict) else {}
    payload = {
        "dec": o.get("decision"),
        "agc": o.get("agency"),
        "mut": sl.get("mutation"),
        "iaa": sl.get("in_authority"),
        "stl": "GAP" if settler.get("gap") else settler.get("settler_id"),
        "gap": bool(settler.get("gap") or sl.get("gap")),
        "halt": bool(o.get("halt") or sl.get("halt")),
    }
    if o.get("chain") and isinstance(o["chain"], dict) and o["chain"].get("halt"):
        payload["halt"] = True
    return claim_from_payload(payload)


def collect(raw: Any, *, decode: Callable[[str], dict] | None = None) -> list[dict[str, Any]]:
    if raw is None:
        return []
    if isinstance(raw, dict):
        raw = raw.get("upstream") or raw.get("chain") or raw.get("hops") or []
    if not isinstance(raw, list):
        raw = [raw]
    out: list[dict[str, Any]] = []
    for item in raw[:MAX_UPSTREAM]:
        if isinstance(item, str) and item.count(".") == 2 and decode is not None:
            verified = decode(item)
            if not verified.get("valid"):
                out.append(
                    claim_from_payload(
                        {"dec": "NONEXIST", "unverified": True, "halt": True, "gap": True}
                    )
                )
                continue
            out.append(claim_from_payload(verified.get("payload") or {}))
        elif isinstance(item, dict) and (
            "decision" in item or "agency" in item or "signed_line" in item or "otherwise" in item
        ):
            out.append(claim_from_result(item))
        elif isinstance(item, dict):
            out.append(claim_from_payload(item))
        else:
            out.append(
                claim_from_payload(
                    {"dec": "NONEXIST", "unverified": True, "halt": True, "gap": True}
                )
            )
    return out


def _rotten(c: dict) -> bool:
    return bool(
        c.get("halt")
        or c.get("unverified")
        or c.get("decision") in _ROTTEN_DEC
        or c.get("in_authority") == "OUT"
    )


def _stained(c: dict) -> bool:
    if _rotten(c):
        return True
    return bool(
        c.get("agency") == "NON-ACT"
        or c.get("gap")
        or c.get("mutation") in _STAIN_MUT
        or c.get("in_authority") == "UNKNOWN"
    )


def _min_agency(claims: list[dict]) -> str:
    if any(c.get("agency") != "ACT" for c in claims):
        return "NON-ACT"
    return "ACT" if claims else "NON-ACT"


def _min_iaa(claims: list[dict]) -> str:
    ranks = {"OUT": 0, "UNKNOWN": 1, "IN": 2}
    if not claims:
        return "UNKNOWN"
    return min((c.get("in_authority") or "UNKNOWN" for c in claims), key=lambda x: ranks.get(x, 1))


def _worst_mut(claims: list[dict]) -> str:
    rank = {
        "ABSENT": 0,
        "SAME": 1,
        "UNSIGNED": 2,
        "DIFF": 3,
        "UP": 4,
        "DOWN": 5,
        "UNWRITTEN": 6,
    }
    worst = "ABSENT"
    best = -1
    for c in claims:
        m = c.get("mutation") or "ABSENT"
        r = rank.get(m, 3)
        if r > best:
            best = r
            worst = m
    return worst


def floor(upstream: list[dict[str, Any]] | None) -> dict[str, Any]:
    """Halt before minting if any causal parent is dead."""
    ups = [claim_from_payload(c) for c in (upstream or []) if isinstance(c, dict)]
    halt = any(_rotten(c) for c in ups)
    return {
        "spec": SPEC,
        "halt": halt,
        "upstream_count": len(ups),
        "reason": "chain_rotten" if halt else None,
    }


def witness(
    *,
    current: dict[str, Any] | None,
    upstream: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    cur = claim_from_payload(current) if current else claim_from_payload({})
    ups = [claim_from_payload(c) for c in (upstream or []) if isinstance(c, dict)]
    chain = [cur] + ups
    min_agency = _min_agency(chain)
    upstream_gap = any(bool(c.get("gap") or c.get("unverified")) for c in ups)
    halt = any(_rotten(c) for c in ups)
    if not ups:
        grade = "CLEAN"
    elif halt:
        grade = "ROTTEN"
    elif any(_stained(c) for c in ups):
        grade = "STAINED"
    else:
        grade = "CLEAN"
    return {
        "spec": SPEC,
        "grade": grade,
        "min_agency": min_agency,
        "upstream_gap": upstream_gap,
        "upstream_count": len(ups),
        "mutation": _worst_mut(chain),
        "in_authority": _min_iaa(chain),
        "halt": halt,
        "invariant": INVARIANT,
        "not": "A single-hop receipt, a wrap SDK, or 'the agent called another agent'.",
    }
