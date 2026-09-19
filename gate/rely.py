"""Reliance gate — may the taxpayer still rely on this named cert.

Not a PFE determination. Not a credit-clean stamp.
The machine cannot wear the supplier mouth.
Public-info collisions arrive as rented inputs, not a people-map we grow.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

SPEC = "gate-rely-v1"
INVARIANT = (
    "Reliance is not a PFE determination. "
    "The machine cannot wear the supplier mouth."
)
DECISIONS = ("EXIST", "HOLD", "NONEXIST", "GAP")
RTK = ("CLEAN", "TRIP", "OPEN", "GAP")
MOUTH_KEYS = (
    "pfe_status",
    "credit_clean",
    "feoc_clean",
    "determination",
    "macr_pass",
    "eligible",
    "feoc_ok",
    "credit_ok",
)


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _present(raw: Any) -> bool:
    if raw is None:
        return False
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, str):
        return bool(raw.strip())
    if isinstance(raw, dict):
        return any(_present(v) for v in raw.values())
    if isinstance(raw, (list, tuple, set)):
        return any(_present(v) for v in raw)
    return True


def _as_dict(raw: Any) -> dict[str, Any]:
    return raw if isinstance(raw, dict) else {}


def _truthy(raw: Any) -> bool:
    if raw is True:
        return True
    if raw is False or raw is None:
        return False
    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        return raw != 0
    s = str(raw).strip().lower()
    return s in {"1", "true", "yes", "on", "trip", "hit", "stale"}


def _mouth_keys_in(obj: Any, found: set[str] | None = None) -> set[str]:
    acc = found if found is not None else set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            lk = str(k).strip().lower()
            if lk in MOUTH_KEYS:
                acc.add(lk)
            _mouth_keys_in(v, acc)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            _mouth_keys_in(item, acc)
    return acc


def cert_hash(cert: Any) -> str:
    c = _as_dict(cert)
    body = {
        "spec": SPEC,
        "cert_id": str(c.get("id") or c.get("cert_id") or "").strip() or None,
        "supplier_id": str(c.get("supplier_id") or c.get("supplier") or "").strip() or None,
        "ein": str(c.get("ein") or c.get("tin") or "").strip() or None,
        "text": c.get("text") or c.get("body") or c.get("hash") or None,
    }
    return hashlib.sha256(_canonical_json(body).encode("utf-8")).hexdigest()


def _tables_moved(rely: dict) -> bool:
    if _truthy(rely.get("tables_stale") or rely.get("tables_moved")):
        return True
    current = str(rely.get("tables_current") or rely.get("tables_live") or "").strip()
    used = str(rely.get("tables_id") or rely.get("tables_used") or "").strip()
    if current and used and current != used:
        return True
    return False


def witness(
    *,
    cert: Any = None,
    questionnaire: Any = None,
    sourcing_map: Any = None,
    public_collision: Any = None,
    known_inaccurate: Any = None,
    require: bool = False,
    tables_stale: bool = False,
    mouth_keys: set[str] | None = None,
) -> dict[str, Any]:
    """EXIST = may still rely. Never = this credit is clean."""
    c = _as_dict(cert)
    cert_on = _present(c)
    mouths = set(mouth_keys or ())
    ch = cert_hash(c) if cert_on else None

    if mouths:
        return {
            "spec": SPEC,
            "decision": "NONEXIST",
            "status": "NONEXIST",
            "halt": True,
            "gap": False,
            "gap_reason": None,
            "reason": "mouth_substitution",
            "rtk": "TRIP",
            "cert_hash": ch,
            "mouth_keys": sorted(mouths),
            "required": require,
            "invariant": INVARIANT,
            "not": (
                "PFE determination, credit-clean stamp, Kharon, Empact, Reunion, "
                "or the machine wearing the supplier mouth."
            ),
        }

    if not cert_on and not require:
        return {
            "spec": SPEC,
            "decision": "GAP",
            "status": "GAP",
            "halt": False,
            "gap": True,
            "gap_reason": "missing_cert",
            "reason": None,
            "rtk": "GAP",
            "cert_hash": None,
            "mouth_keys": [],
            "required": require,
            "invariant": INVARIANT,
            "not": (
                "PFE determination, credit-clean stamp, Kharon, Empact, Reunion, "
                "or the machine wearing the supplier mouth."
            ),
        }

    if not cert_on:
        decision, reason, rtk = "HOLD", "missing_cert", "OPEN"
    elif tables_stale:
        decision, reason, rtk = "HOLD", "tables_moved", "OPEN"
    elif not _truthy(c.get("signed_under_penalty") or c.get("penalty_of_perjury")):
        decision, reason, rtk = "HOLD", "incomplete_cert", "OPEN"
    elif not str(c.get("ein") or c.get("tin") or "").strip():
        decision, reason, rtk = "HOLD", "incomplete_cert", "OPEN"
    elif not _present(questionnaire):
        decision, reason, rtk = "HOLD", "missing_questionnaire", "OPEN"
    elif not _present(sourcing_map):
        decision, reason, rtk = "HOLD", "missing_map", "OPEN"
    elif _truthy(known_inaccurate) or _present(public_collision) or _truthy(public_collision):
        decision, reason, rtk = "NONEXIST", "reason_to_know", "TRIP"
    else:
        decision, reason, rtk = "EXIST", None, "CLEAN"

    halt = decision in {"HOLD", "NONEXIST"}
    return {
        "spec": SPEC,
        "decision": decision,
        "status": decision,
        "halt": halt,
        "gap": False,
        "gap_reason": None,
        "reason": reason,
        "rtk": rtk,
        "cert_hash": ch,
        "mouth_keys": [],
        "required": require,
        "invariant": INVARIANT,
        "not": (
            "PFE determination, credit-clean stamp, Kharon, Empact, Reunion, "
            "or the machine wearing the supplier mouth."
        ),
    }


def from_body(
    body: dict | None,
    context: dict | None = None,
    policy: dict | None = None,
) -> dict[str, Any]:
    b = body if isinstance(body, dict) else {}
    ctx = context if isinstance(context, dict) else {}
    pol = policy if isinstance(policy, dict) else {}
    args = b.get("args") if isinstance(b.get("args"), dict) else {}
    cand = b.get("candidate") if isinstance(b.get("candidate"), dict) else {}
    cand_args = cand.get("args") if isinstance(cand.get("args"), dict) else {}
    blob = (
        b.get("rely")
        or ctx.get("rely")
        or args.get("rely")
        or cand.get("rely")
        or cand_args.get("rely")
        or {}
    )
    if not isinstance(blob, dict):
        blob = {}
    cert = (
        blob.get("cert")
        or blob.get("supplier_cert")
        or b.get("supplier_cert")
        or b.get("cert")
        or ctx.get("supplier_cert")
        or ctx.get("cert")
    )
    questionnaire = (
        blob.get("questionnaire")
        or b.get("questionnaire")
        or ctx.get("questionnaire")
    )
    sourcing_map = (
        blob.get("sourcing_map")
        or blob.get("map")
        or b.get("sourcing_map")
        or ctx.get("sourcing_map")
    )
    public_collision = (
        blob.get("public_collision")
        or blob.get("collision")
        or b.get("public_collision")
        or ctx.get("public_collision")
    )
    known_inaccurate = blob.get("known_inaccurate") or b.get("known_inaccurate")
    require = bool(
        pol.get("require_rely")
        or blob.get("required")
        or b.get("require_rely")
        or ctx.get("require_rely")
    )
    tables_stale = _tables_moved(blob) or _tables_moved(b)
    mouths = _mouth_keys_in(blob) | _mouth_keys_in(cert)
    return witness(
        cert=cert,
        questionnaire=questionnaire,
        sourcing_map=sourcing_map,
        public_collision=public_collision,
        known_inaccurate=known_inaccurate,
        require=require,
        tables_stale=tables_stale,
        mouth_keys=mouths,
    )
