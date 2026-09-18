"""Signed-line witness — written line vs signed line; in-authority at the second.

The share can mutate after the act (signing down).
Authority is measured at the bind second, not an MGA allowlist.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

SPEC = "gate-signed-line-v1"
INVARIANT = (
    "Written line is not the signed line. "
    "In-authority is at the second the pen lands."
)
MUTATIONS = (
    "SAME",
    "DOWN",
    "UP",
    "DIFF",
    "UNSIGNED",
    "UNWRITTEN",
    "ABSENT",
)
AUTHORITY = ("IN", "OUT", "UNKNOWN")


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _present(raw: Any) -> bool:
    if raw is None:
        return False
    if isinstance(raw, str):
        return bool(raw.strip())
    if isinstance(raw, dict):
        return any(v is not None and v != "" for v in raw.values())
    if isinstance(raw, (list, tuple)):
        return len(raw) > 0
    return True


def line_hash(raw: Any) -> str:
    if not _present(raw):
        body = {"spec": SPEC, "line": None}
    elif isinstance(raw, (dict, list)):
        body = {"spec": SPEC, "line": raw}
    else:
        body = {"spec": SPEC, "line": str(raw).strip()}
    return hashlib.sha256(_canonical_json(body).encode("utf-8")).hexdigest()


def _share_number(raw: Any) -> float | None:
    if isinstance(raw, dict):
        for key in ("share", "percent", "signed_share", "line_share", "premium", "limit"):
            if key in raw and raw[key] is not None:
                try:
                    return float(raw[key])
                except (TypeError, ValueError):
                    return None
        return None
    if raw is None or raw == "":
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def _mutation(written: Any, signed: Any) -> str:
    w_on = _present(written)
    s_on = _present(signed)
    if not w_on and not s_on:
        return "ABSENT"
    if w_on and not s_on:
        return "UNSIGNED"
    if s_on and not w_on:
        return "UNWRITTEN"
    if line_hash(written) == line_hash(signed):
        return "SAME"
    w_n = _share_number(written)
    s_n = _share_number(signed)
    if w_n is not None and s_n is not None:
        if s_n < w_n:
            return "DOWN"
        if s_n > w_n:
            return "UP"
    return "DIFF"


def _parse_iso(raw: Any) -> datetime | None:
    s = str(raw or "").strip()
    if not s:
        return None
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _iso_z(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _authority_at(
    authority: dict | None,
) -> tuple[str, str | None, bool, str | None, str | None]:
    """Return (IN|OUT|UNKNOWN, at_iso, gap, gap_reason, valid_until)."""
    auth = authority if isinstance(authority, dict) else {}
    at_raw = auth.get("at") or auth.get("bind_at") or auth.get("signed_at")
    at_dt = _parse_iso(at_raw)
    at_iso = _iso_z(at_dt)

    start = _parse_iso(auth.get("window_start") or auth.get("effective"))
    end = _parse_iso(auth.get("window_end") or auth.get("expires") or auth.get("valid_until"))
    inside = auth.get("inside")
    if inside is None:
        inside = auth.get("in_authority")
    if inside is None and "ultra_vires" in auth:
        inside = not bool(auth.get("ultra_vires"))

    if inside is True:
        iaa = "IN"
    elif inside is False:
        iaa = "OUT"
    else:
        iaa = "UNKNOWN"

    clock = at_dt or datetime.now(timezone.utc)
    if start and clock < start:
        iaa = "OUT"
    if end and clock > end:
        iaa = "OUT"

    valid_until = _iso_z(end)
    if iaa == "OUT":
        return iaa, at_iso, False, None, valid_until
    if iaa == "IN":
        return iaa, at_iso, False, None, valid_until
    return "UNKNOWN", at_iso, True, "missing_authority", valid_until


def witness(
    *,
    written: Any = None,
    signed: Any = None,
    authority: dict | None = None,
) -> dict[str, Any]:
    """Measure written vs signed; whether power held at the pen second."""
    mut = _mutation(written, signed)
    iaa, at_iso, gap, gap_reason, valid_until = _authority_at(authority)
    if mut == "UNWRITTEN":
        gap = True
        gap_reason = "unwritten"
    halt = iaa == "OUT"
    return {
        "spec": SPEC,
        "written_hash": line_hash(written),
        "signed_hash": line_hash(signed),
        "mutation": mut,
        "in_authority": iaa,
        "authority_at": at_iso,
        "valid_until": valid_until,
        "gap": gap,
        "gap_reason": gap_reason,
        "halt": halt,
        "invariant": INVARIANT,
        "not": (
            "MGA line/state allowlist, PPL placing, Bind Room, "
            "or a pre-bind subjectivity tracker."
        ),
    }


def from_body(body: dict | None, context: dict | None = None) -> dict[str, Any]:
    b = body if isinstance(body, dict) else {}
    ctx = context if isinstance(context, dict) else {}
    args = b.get("args") if isinstance(b.get("args"), dict) else {}
    cand = b.get("candidate") if isinstance(b.get("candidate"), dict) else {}
    cand_args = cand.get("args") if isinstance(cand.get("args"), dict) else {}
    written = (
        b.get("written_line")
        or ctx.get("written_line")
        or args.get("written_line")
        or cand.get("written_line")
        or cand_args.get("written_line")
    )
    signed = (
        b.get("signed_line")
        or ctx.get("signed_line")
        or args.get("signed_line")
        or cand.get("signed_line")
        or cand_args.get("signed_line")
    )
    authority = (
        b.get("authority")
        or ctx.get("authority")
        or b.get("in_authority")
        or ctx.get("in_authority")
    )
    if not isinstance(authority, dict):
        authority = {}
    return witness(written=written, signed=signed, authority=authority)
