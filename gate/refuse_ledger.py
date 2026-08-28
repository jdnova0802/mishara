"""Refuse Ledger — ρ bind line items for sticks that did not happen.

PCAA names non_execution_proof. Nobody sells refusal as carrier accounting.
Every HALT/BLOCK is a line item with restraint mass — not a log tail.
"""
from __future__ import annotations

from typing import Any

try:
    from gate import db
except ImportError:
    import db

try:
    from gate import stick_meter as stick_meter_mod
except ImportError:
    import stick_meter as stick_meter_mod

SPEC = "gate-refuse-ledger-v1"
INVENTION = "Refuse Ledger"
FAMILY = "competitive-response"
RHO_UNIT = "restraint_mass_bind"


def line_from_event(row: dict | None, *, premium: float | None = None) -> dict[str, Any] | None:
    if not isinstance(row, dict):
        return None
    dec = (row.get("decision") or "").upper()
    if dec not in ("HALT", "BLOCK") or row.get("acted"):
        return None
    jid = (row.get("job_id") or "").strip()
    score = stick_meter_mod.score(
        write_kind="bind",
        premium=premium,
        fuse_state="HALT" if dec == "HALT" else "DEAD",
        epoch_locked=dec == "HALT",
        would_bind=False,
        acted=False,
    )
    mu = score.get("score") or score.get("mass") or 0
    return {
        "spec": SPEC,
        "line_id": f"refuse:{row.get('id')}",
        "job_id": jid,
        "event_id": row.get("id"),
        "decision": dec,
        "premium_unbound": premium,
        "restraint_mass": mu,
        "rho_unit": RHO_UNIT,
        "verify_url": row.get("verify_url"),
        "receipt_hash": row.get("receipt_hash"),
        "created_at": row.get("created_at"),
        "accounting_class": "bind_refused_not_ghost",
        "rule": "Refusal is a first-class line item — ρ on premium that never stuck.",
    }


def attach(plan: dict, *, row: dict | None = None, premium: float | None = None) -> dict:
    if not plan.get("halt") and (plan.get("decision") or "").upper() not in ("HALT", "BLOCK"):
        return plan
    if plan.get("acted"):
        return plan
    line = line_from_event(
        row
        or {
            "id": plan.get("event_id"),
            "job_id": plan.get("job_id"),
            "decision": plan.get("decision"),
            "acted": plan.get("acted"),
            "verify_url": plan.get("verify_url"),
            "receipt_hash": plan.get("receipt_hash"),
            "created_at": plan.get("created_at"),
        },
        premium=premium,
    )
    if line:
        plan["refuse_ledger"] = line
    return plan


def ledger(*, limit: int = 50) -> dict[str, Any]:
    lim = max(1, min(int(limit or 50), 500))
    rows = db.list_bind_events(None, limit=lim * 4)
    lines: list[dict] = []
    total_mass = 0.0
    for row in rows:
        line = line_from_event(row)
        if line:
            lines.append(line)
            total_mass += float(line.get("restraint_mass") or 0)
        if len(lines) >= lim:
            break
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "line_count": len(lines),
        "total_restraint_mass": round(total_mass, 3),
        "rho_unit": RHO_UNIT,
        "lines": lines,
        "vs_survey": "PCAA names non_execution_proof; this is the carrier ledger SKU.",
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Binds that didn't happen as accounting — ρ on refused premium.",
        "demo": f"GET {base}/demo/pas/refuse-ledger",
        "well_known": f"{base}/.well-known/refuse-ledger.json",
        "pairs_with": "Counterfactual Spend · HALT Cemetery · Stick Meter",
        "posture": "Sell refusal — not pre-execution proof cosplay.",
    }
