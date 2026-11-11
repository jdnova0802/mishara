"""Item 163 — exposure-capped permission, not EigenLayer slash-after.

The whitepaper gap is post-hoc: an act runs, then slashable stake can be
smaller than attacker profit. This module never lets the write through
when posted < value_at_risk for *this* attestation. Forfeit cannot exceed
what was posted and never claims it equals profit recovered.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

try:
    from gate import sanitize as sanitize_mod
except ImportError:
    import sanitize as sanitize_mod

SPEC = "gate-exposure-bond-v1"


def _iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _path() -> Path:
    return Path(os.getenv("GATE_EXPOSURE_BOND_PATH") or Path(__file__).resolve().parent / "data" / "exposure_bond.json")


def _load() -> dict[str, Any]:
    path = _path()
    if not path.exists():
        return {"spec": SPEC, "bonds": [], "forfeits": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"spec": SPEC, "bonds": [], "forfeits": []}
    if not isinstance(data, dict):
        return {"spec": SPEC, "bonds": [], "forfeits": []}
    data.setdefault("bonds", [])
    data.setdefault("forfeits", [])
    return data


def _save(store: dict[str, Any]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")


def parse_amount(raw: Any) -> Decimal | None:
    s = str(raw or "").replace(",", "").replace("$", "").strip()
    if not s:
        return None
    try:
        n = Decimal(s)
    except (InvalidOperation, ValueError):
        return None
    if n < 0:
        return None
    return n


def catalog() -> dict[str, Any]:
    store = _load()
    return {
        "spec": SPEC,
        "eigenlayer_slash_after": False,
        "profit_equals_slash": False,
        "bonds": store["bonds"],
        "forfeits": store["forfeits"],
        "plain": "Permission dies if posted < this attestation's value_at_risk. Slash-after is not this module.",
    }


def post(
    *,
    legal_person: str,
    posted: Any,
    covers_ref: str,
) -> dict[str, Any]:
    who = sanitize_mod.strip_agent(legal_person, limit=200)
    ref = (covers_ref or "").strip()
    amt = parse_amount(posted)
    if not who or not ref or amt is None:
        return {"spec": SPEC, "ok": False, "error": "bond_fields_required", "plain": "Need a legal person, a posted amount, and the attestation this covers."}
    rec = {
        "spec": SPEC,
        "ok": True,
        "bond_id": "bnd_" + uuid.uuid4().hex[:12],
        "legal_person": who,
        "posted": str(amt),
        "covers_ref": ref,
        "spent": False,
        "posted_at": _iso(),
        "plain": "Posted. Coverage is checked per instruction, not as a standing umbrella.",
    }
    store = _load()
    store["bonds"].append(rec)
    _save(store)
    return rec


def covers(*, bond_id: str, value_at_risk: Any) -> dict[str, Any]:
    var = parse_amount(value_at_risk)
    if var is None:
        return {"spec": SPEC, "ok": False, "error": "value_at_risk_required"}
    store = _load()
    row = next((b for b in store["bonds"] if b.get("bond_id") == (bond_id or "").strip()), None)
    if not row or row.get("spent"):
        return {
            "spec": SPEC,
            "ok": False,
            "covers": False,
            "error": "underbonded",
            "plain": "No live bond covering this exposure. The instruction does not run.",
        }
    posted = Decimal(str(row["posted"]))
    ok = posted >= var
    return {
        "spec": SPEC,
        "ok": ok,
        "covers": ok,
        "bond_id": row["bond_id"],
        "posted": str(posted),
        "value_at_risk": str(var),
        "shortfall": str(var - posted) if not ok else "0",
        "error": None if ok else "underbonded",
        "plain": (
            "Posted covers this exposure. Write may proceed on other gates."
            if ok
            else "Underbonded. Fail closed. This is not a slash of $20M with $8M posted."
        ),
    }


def forfeit(*, bond_id: str, reason: str) -> dict[str, Any]:
    why = sanitize_mod.strip_agent(reason, limit=400)
    if not why:
        return {"spec": SPEC, "ok": False, "error": "reason_required"}
    store = _load()
    row = next((b for b in store["bonds"] if b.get("bond_id") == (bond_id or "").strip()), None)
    if not row:
        return {"spec": SPEC, "ok": False, "error": "bond_not_found"}
    posted = str(row["posted"])
    row["spent"] = True
    rec = {
        "spec": SPEC,
        "ok": True,
        "forfeit_id": "for_" + uuid.uuid4().hex[:12],
        "bond_id": row["bond_id"],
        "forfeited": posted,
        "profit_recovered": False,
        "reason": why,
        "at": _iso(),
        "plain": "Forfeit equals posted, never attacker profit. EigenLayer's gap is not closed by this number.",
    }
    store["forfeits"].append(rec)
    _save(store)
    return rec
