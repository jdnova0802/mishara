"""Sink Registry — irreversible effect classes as public nouns.

The boom typed transport (TCP) and documents (HTTP). It never typed
consequence. Every POST looked the same. This registry is the missing
noun layer: money ≠ filing ≠ physical ≠ reputational ≠ destroy.
"""
from __future__ import annotations

import threading
from typing import Any

SPEC = "gate-sink-registry-v1"

IRREVERSIBILITY = (
    "reversible",
    "soft",          # undo costly but possible
    "hard",          # practically irreversible
    "absolute",      # physically / legally final
)

CLASSES = (
    "monetary",
    "legal",
    "physical",
    "reputational",
    "data_destroy",
    "identity",
    "compute",
    "message",
)

_lock = threading.Lock()
_sinks: dict[str, dict[str, Any]] = {}


def _seed() -> None:
    """Canonical boom-gap sinks — the types nobody named in '95."""
    defaults = [
        {
            "sink_id": "bank.rtp",
            "class": "monetary",
            "irreversibility": "hard",
            "burn_required": True,
            "mandate_required": True,
            "description": "Real-time payment rail — funds leave and rarely return.",
        },
        {
            "sink_id": "bank.ach",
            "class": "monetary",
            "irreversibility": "soft",
            "burn_required": True,
            "mandate_required": True,
            "description": "ACH credit — reversible window exists, then hardens.",
        },
        {
            "sink_id": "bank.wire",
            "class": "monetary",
            "irreversibility": "hard",
            "burn_required": True,
            "mandate_required": True,
            "description": "Domestic/international wire — finality is the product.",
        },
        {
            "sink_id": "court.filing",
            "class": "legal",
            "irreversibility": "hard",
            "burn_required": True,
            "mandate_required": True,
            "description": "Court or registry filing — creates lasting legal fact.",
        },
        {
            "sink_id": "contract.execute",
            "class": "legal",
            "irreversibility": "hard",
            "burn_required": True,
            "mandate_required": True,
            "description": "Execute a binding instrument.",
        },
        {
            "sink_id": "device.actuate",
            "class": "physical",
            "irreversibility": "absolute",
            "burn_required": True,
            "mandate_required": True,
            "description": "Physical actuator / robot / industrial control.",
        },
        {
            "sink_id": "vehicle.control",
            "class": "physical",
            "irreversibility": "absolute",
            "burn_required": True,
            "mandate_required": True,
            "description": "Vehicle motion / braking / steering — kinetic harm lane.",
        },
        {
            "sink_id": "drone.actuate",
            "class": "physical",
            "irreversibility": "absolute",
            "burn_required": True,
            "mandate_required": True,
            "description": "UAV / drone flight or payload actuation.",
        },
        {
            "sink_id": "grid.switch",
            "class": "physical",
            "irreversibility": "absolute",
            "burn_required": True,
            "mandate_required": True,
            "description": "Grid / power switch that can darken or energize physical plant.",
        },
        {
            "sink_id": "industrial.plc",
            "class": "physical",
            "irreversibility": "absolute",
            "burn_required": True,
            "mandate_required": True,
            "description": "Industrial PLC / SCADA write — plant motion or process change.",
        },
        {
            "sink_id": "medical.actuate",
            "class": "physical",
            "irreversibility": "absolute",
            "burn_required": True,
            "mandate_required": True,
            "description": "Medical device actuation with bodily consequence.",
        },
        {
            "sink_id": "publish.public",
            "class": "reputational",
            "irreversibility": "soft",
            "burn_required": True,
            "mandate_required": False,
            "description": "Public broadcast — copies outrun deletion.",
        },
        {
            "sink_id": "data.destroy",
            "class": "data_destroy",
            "irreversibility": "absolute",
            "burn_required": True,
            "mandate_required": True,
            "description": "Irreversible delete / crypto-shred.",
        },
        {
            "sink_id": "identity.attest",
            "class": "identity",
            "irreversibility": "hard",
            "burn_required": True,
            "mandate_required": True,
            "description": "Issue or bind durable identity claims.",
        },
        {
            "sink_id": "email.send",
            "class": "message",
            "irreversibility": "soft",
            "burn_required": False,
            "mandate_required": False,
            "description": "Outbound message — soft irrevocability via copies.",
        },
        {
            "sink_id": "compute.run",
            "class": "compute",
            "irreversibility": "reversible",
            "burn_required": False,
            "mandate_required": False,
            "description": "Pure computation — not consequence unless it opens a sink.",
        },
    ]
    for row in defaults:
        _sinks[row["sink_id"]] = {
            "spec": SPEC,
            **row,
            "seeded": True,
        }


_seed()


def _reset_for_tests() -> None:
    with _lock:
        _sinks.clear()
        _seed()


def register(
    *,
    sink_id: str,
    sink_class: str,
    irreversibility: str = "hard",
    burn_required: bool = True,
    mandate_required: bool = True,
    description: str = "",
) -> dict:
    sid = (sink_id or "").strip()
    cls = (sink_class or "").strip()
    irr = (irreversibility or "hard").strip()
    if not sid:
        return {"ok": False, "reason": "sink_id_required", "sink": None}
    if cls not in CLASSES:
        return {"ok": False, "reason": "unknown_class", "sink": None, "classes": list(CLASSES)}
    if irr not in IRREVERSIBILITY:
        return {
            "ok": False,
            "reason": "unknown_irreversibility",
            "sink": None,
            "irreversibility": list(IRREVERSIBILITY),
        }
    row = {
        "spec": SPEC,
        "sink_id": sid,
        "class": cls,
        "irreversibility": irr,
        "burn_required": bool(burn_required),
        "mandate_required": bool(mandate_required),
        "description": (description or "").strip(),
        "seeded": False,
    }
    with _lock:
        _sinks[sid] = row
    return {"ok": True, "reason": None, "sink": dict(row)}


def get(sink_id: str) -> dict | None:
    with _lock:
        row = _sinks.get((sink_id or "").strip())
        return dict(row) if row else None


def list_sinks(
    *,
    sink_class: str | None = None,
    irreversibility: str | None = None,
    burn_required: bool | None = None,
) -> list[dict]:
    with _lock:
        rows = [dict(v) for v in _sinks.values()]
    if sink_class:
        rows = [r for r in rows if r.get("class") == sink_class]
    if irreversibility:
        rows = [r for r in rows if r.get("irreversibility") == irreversibility]
    if burn_required is not None:
        rows = [r for r in rows if bool(r.get("burn_required")) is burn_required]
    rows.sort(key=lambda r: (r.get("class") or "", r.get("sink_id") or ""))
    return rows


def require_for_act(sink_id: str) -> dict:
    """Policy hint for Right-to-Act / burn paths."""
    row = get(sink_id)
    if not row:
        return {
            "known": False,
            "sink_id": sink_id,
            "burn_required": True,
            "mandate_required": True,
            "irreversibility": "hard",
            "note": "Unknown sink → fail closed: treat as hard irreversible.",
        }
    return {
        "known": True,
        "sink_id": row["sink_id"],
        "class": row["class"],
        "irreversibility": row["irreversibility"],
        "burn_required": row["burn_required"],
        "mandate_required": row["mandate_required"],
        "description": row.get("description"),
    }


def manifest(public_url: str) -> dict:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Gate Sink Registry",
        "description": (
            "Typed irreversible effect classes. The boom never named consequence; "
            "this does. money ≠ legal ≠ physical ≠ reputational ≠ destroy."
        ),
        "invariant": "Unknown sink → fail closed as hard irreversible.",
        "classes": list(CLASSES),
        "irreversibility": list(IRREVERSIBILITY),
        "list": f"{base}/v1/sinks",
        "get": f"{base}/v1/sinks/{{sink_id}}",
        "register": f"{base}/v1/sinks/register",
        "well_known": f"{base}/.well-known/sinks.json",
        "related": {
            "finder": f"{base}/.well-known/finder.json",
            "right_to_act": f"{base}/.well-known/right-to-act.json",
        },
    }
