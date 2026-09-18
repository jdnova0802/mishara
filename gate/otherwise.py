"""Branch witness — the otherwise at the hop.

An effect that could not have been otherwise is not an act.
Live alternatives must be executable writes of the same kind, not token samples.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

SPEC = "gate-otherwise-v1"
MAX_LIVE = 16
INVARIANT = "EXIST with no live other write is not an act."


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _open_hash(fingerprints: list[str]) -> str:
    body = {"spec": SPEC, "open": sorted(fingerprints)}
    return hashlib.sha256(_canonical_json(body).encode("utf-8")).hexdigest()


def witness(*, live: list[dict[str, Any]]) -> dict[str, Any]:
    """Collapse a consideration set to agency.

    `live` items: action, sink, fingerprint, exists (bool — policy/mouth EXIST).
    Dedupes by fingerprint. Caps the published list.
    """
    by_fp: dict[str, dict[str, Any]] = {}
    for raw in live:
        if not isinstance(raw, dict):
            continue
        fp = str(raw.get("fingerprint") or "").strip()
        if not fp:
            continue
        exists = bool(raw.get("exists"))
        prev = by_fp.get(fp)
        if prev is None or (exists and not prev.get("exists")):
            by_fp[fp] = {
                "action": str(raw.get("action") or "").strip(),
                "sink": str(raw.get("sink") or "").strip(),
                "fingerprint": fp,
                "exists": exists,
            }

    open_rows = [row for row in by_fp.values() if row["exists"]]
    open_rows.sort(key=lambda r: r["fingerprint"])
    fps = [r["fingerprint"] for r in open_rows]
    open_count = len(fps)
    settled = open_count < 2
    return {
        "spec": SPEC,
        "open_count": open_count,
        "open_hash": _open_hash(fps),
        "settled": settled,
        "agency": "NON-ACT" if settled else "ACT",
        "live": open_rows[:MAX_LIVE],
        "invariant": INVARIANT,
        "not": "Model n-best, HITL diary, or a path that could not execute.",
    }


def normalize_open_writes(raw: Any) -> list[dict]:
    if isinstance(raw, dict):
        raw = raw.get("open_writes") or raw.get("siblings") or []
    if not isinstance(raw, list):
        return []
    out: list[dict] = []
    for item in raw[:MAX_LIVE]:
        if isinstance(item, dict):
            out.append(item)
    return out
