"""Items 91–94 — per-vertical V1 (irreversibility threshold) from real inputs.

V1 is the named instant an act becomes irrevocable. Distance is 1 far from that
instant and 0 once it is crossed. Derived fields (over-limit, over-cap, reserve
shortfall) are computed, never copied from a static lookup table.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

SPEC = "gate-v1-computation-v1"
FINALITY_SPEC = "gate-finality-event-v1"
UNDO_SPEC = "gate-v1-undo-v1"

DEFAULT_TTL_SECONDS = 300.0


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _now()).astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _num(value: Any) -> float | None:
    if value is None or value is False:
        return None
    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _clamp(value: float) -> float:
    if value < 0:
        return 0.0
    if value > 1:
        return 1.0
    return float(value)


def _ttl_distance(inp: dict[str, Any]) -> tuple[float, bool]:
    ttl = _num(inp.get("ttl_seconds")) or DEFAULT_TTL_SECONDS
    if ttl <= 0:
        ttl = DEFAULT_TTL_SECONDS
    remaining = _num(inp.get("remaining_seconds"))
    bound = bool(
        inp.get("bound")
        or inp.get("bind_committed")
        or inp.get("write_executed")
        or str(inp.get("phase") or "").upper() == "SPENT"
    )
    if remaining is None:
        remaining = 0.0 if bound else ttl
    crossed = bound or remaining <= 0
    if crossed:
        return 0.0, True
    return _clamp(remaining / ttl), False


def _snapshot(
    *,
    vertical: str,
    finality_event: str,
    derived: dict[str, Any],
    distance: float,
    crossed: bool,
    lookup_table: bool = False,
) -> dict[str, Any]:
    return {
        "spec": SPEC,
        "vertical": vertical,
        "finality_event": finality_event,
        "finality": {
            "spec": FINALITY_SPEC,
            "event": finality_event,
            "crossed": crossed,
        },
        "derived": derived,
        "v1_distance": distance,
        "crossed": crossed,
        "undo_open": not crossed,
        "lookup_table": lookup_table,
        "plain": (
            f"{'V1 crossed' if crossed else 'Pre-V1 window open'} — {finality_event}."
        ),
    }


def insurance(inp: dict[str, Any]) -> dict[str, Any]:
    premium = _num(inp.get("premium_usd") if inp.get("premium_usd") is not None else inp.get("premium"))
    limit = _num(
        inp.get("delegation_limit_usd")
        if inp.get("delegation_limit_usd") is not None
        else inp.get("authority_limit")
    )
    over = None if premium is None or limit is None else premium - limit
    distance, crossed = _ttl_distance(inp)
    return _snapshot(
        vertical="insurance",
        finality_event="pas_bind_commit",
        derived={
            "premium_usd": premium,
            "delegation_limit_usd": limit,
            "over_limit_usd": over,
        },
        distance=distance,
        crossed=crossed,
    )


def network(inp: dict[str, Any]) -> dict[str, Any]:
    nodes = _num(inp.get("nodes_in_cascade"))
    cap = _num(inp.get("fleet_cap"))
    over = None if nodes is None or cap is None else nodes - cap
    distance, crossed = _ttl_distance(inp)
    return _snapshot(
        vertical="network",
        finality_event="fleet_deploy_commit",
        derived={
            "nodes_in_cascade": nodes,
            "fleet_cap": cap,
            "over_cap": over,
        },
        distance=distance,
        crossed=crossed,
    )


def climate(inp: dict[str, Any]) -> dict[str, Any]:
    floor = _num(inp.get("reserve_floor_mw"))
    projected = _num(inp.get("projected_mw"))
    shortfall = None if floor is None or projected is None else floor - projected
    distance, crossed = _ttl_distance(inp)
    return _snapshot(
        vertical="climate",
        finality_event="grid_commit",
        derived={
            "reserve_floor_mw": floor,
            "projected_mw": projected,
            "reserve_shortfall_mw": shortfall,
        },
        distance=distance,
        crossed=crossed,
    )


def payments(inp: dict[str, Any]) -> dict[str, Any]:
    amount = _num(inp.get("amount"))
    distance, crossed = _ttl_distance(inp)
    return _snapshot(
        vertical="payments",
        finality_event="irrevocable_credit_push",
        derived={"amount": amount, "rail": inp.get("rail")},
        distance=distance,
        crossed=crossed,
    )


def hiring(inp: dict[str, Any]) -> dict[str, Any]:
    sent = bool(inp.get("adverse_action_sent") or inp.get("bound"))
    distance, crossed = (0.0, True) if sent else _ttl_distance(inp)
    return _snapshot(
        vertical="hiring",
        finality_event="adverse_action_notice_sent",
        derived={"adverse_action_sent": sent},
        distance=distance,
        crossed=crossed,
    )


def forensic(inp: dict[str, Any]) -> dict[str, Any]:
    entered = bool(inp.get("testimony_entered") or inp.get("bound"))
    distance, crossed = (0.0, True) if entered else _ttl_distance(inp)
    return _snapshot(
        vertical="forensic",
        finality_event="testimony_entered",
        derived={"testimony_entered": entered},
        distance=distance,
        crossed=crossed,
    )


def actuarial(inp: dict[str, Any]) -> dict[str, Any]:
    return _snapshot(
        vertical="actuarial",
        finality_event="treaty_bind_commit",
        derived={"treaty": inp.get("treaty")},
        distance=_ttl_distance(inp)[0],
        crossed=_ttl_distance(inp)[1],
    )


def mortgage(inp: dict[str, Any]) -> dict[str, Any]:
    return _snapshot(
        vertical="mortgage",
        finality_event="closing_wire",
        derived={"loan_id": inp.get("loan_id")},
        distance=_ttl_distance(inp)[0],
        crossed=_ttl_distance(inp)[1],
    )


def defense(inp: dict[str, Any]) -> dict[str, Any]:
    return _snapshot(
        vertical="defense",
        finality_event="order_release",
        derived={"order_id": inp.get("order_id")},
        distance=_ttl_distance(inp)[0],
        crossed=_ttl_distance(inp)[1],
    )


def creator(inp: dict[str, Any]) -> dict[str, Any]:
    return _snapshot(
        vertical="creator",
        finality_event="publish_commit",
        derived={"asset_id": inp.get("asset_id")},
        distance=_ttl_distance(inp)[0],
        crossed=_ttl_distance(inp)[1],
    )


def public(inp: dict[str, Any]) -> dict[str, Any]:
    return _snapshot(
        vertical="public",
        finality_event="benefit_write",
        derived={"benefit_id": inp.get("benefit_id")},
        distance=_ttl_distance(inp)[0],
        crossed=_ttl_distance(inp)[1],
    )


def biology(inp: dict[str, Any]) -> dict[str, Any]:
    return _snapshot(
        vertical="biology",
        finality_event="clinical_act",
        derived={"protocol_id": inp.get("protocol_id"), "model_digest": inp.get("model_digest")},
        distance=_ttl_distance(inp)[0],
        crossed=_ttl_distance(inp)[1],
    )


def animal_welfare(inp: dict[str, Any]) -> dict[str, Any]:
    return _snapshot(
        vertical="animal_welfare",
        finality_event="animal_procedure",
        derived={
            "protocol_id": inp.get("protocol_id"),
            "inspection": inp.get("inspection"),
        },
        distance=_ttl_distance(inp)[0],
        crossed=_ttl_distance(inp)[1],
    )


def institutional(inp: dict[str, Any]) -> dict[str, Any]:
    have = _num(inp.get("keys_present")) or 0.0
    need = _num(inp.get("quorum_required")) or 2.0
    crossed_keys = have >= need and bool(inp.get("bound"))
    distance, crossed_ttl = _ttl_distance(inp)
    crossed = crossed_keys or crossed_ttl
    return _snapshot(
        vertical="institutional",
        finality_event="board_instrument_executed",
        derived={"keys_present": have, "quorum_required": need},
        distance=0.0 if crossed else distance,
        crossed=crossed,
    )


def epistemics(inp: dict[str, Any]) -> dict[str, Any]:
    return _snapshot(
        vertical="epistemics",
        finality_event="filing_commit",
        derived={"assumptions_required": bool(inp.get("assumptions_required", True))},
        distance=_ttl_distance(inp)[0],
        crossed=_ttl_distance(inp)[1],
    )


FORMULAS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "insurance": insurance,
    "network": network,
    "climate": climate,
    "payments": payments,
    "hiring": hiring,
    "forensic": forensic,
    "actuarial": actuarial,
    "mortgage": mortgage,
    "defense": defense,
    "creator": creator,
    "biology": biology,
    "animal_welfare": animal_welfare,
    "institutional": institutional,
    "public": public,
    "epistemics": epistemics,
}

ALIASES = {
    "fleet": "network",
    "grid": "climate",
    "reinsurance": "actuarial",
    "clinical": "biology",
    "animal": "animal_welfare",
    "animal-welfare": "animal_welfare",
    "iacuc": "animal_welfare",
    "awa": "animal_welfare",
    "olaw": "animal_welfare",
    "board": "institutional",
    "counsel": "epistemics",
    "court": "forensic",
    "x402": "payments",
    "rtp": "payments",
    "oct": "payments",
    "issuing": "payments",
}


def _undo_path() -> Path:
    return Path(os.getenv("GATE_V1_UNDO_PATH") or Path(__file__).resolve().parent / "data" / "v1_undos.json")


def compute(vertical: str | None, inputs: dict[str, Any] | None) -> dict[str, Any]:
    """Replace the static table: formula from the inputs this vertical actually has."""
    key = ALIASES.get((vertical or "").strip().lower(), (vertical or "").strip().lower())
    inp = dict(inputs or {})
    fn = FORMULAS.get(key)
    if fn is None:
        distance, crossed = _ttl_distance(inp)
        return _snapshot(
            vertical=key or "unlabeled",
            finality_event="unnamed_irreversible_write",
            derived={},
            distance=distance,
            crossed=crossed,
        )
    return fn(inp)


def inputs_from_row(row: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    hop = row.get("hop") if isinstance(row.get("hop"), dict) else {}
    vertical = str(
        hop.get("vertical") or hop.get("domain") or hop.get("line") or hop.get("rail") or ""
    ).lower()
    inp = dict(hop)
    inp["phase"] = row.get("phase") or hop.get("phase")
    if hop.get("bound") is not None:
        inp["bound"] = hop.get("bound")
    elif hop.get("bind_committed") is not None:
        inp["bound"] = hop.get("bind_committed")
    elif hop.get("write_executed"):
        inp["bound"] = True
    return vertical, inp


def for_receipt(row: dict[str, Any]) -> dict[str, Any]:
    vertical, inp = inputs_from_row(row)
    snap = compute(vertical, inp)
    return {
        "spec": FINALITY_SPEC,
        "finality_event": snap["finality_event"],
        "v1_distance": snap["v1_distance"],
        "crossed": snap["crossed"],
        "undo_open": snap["undo_open"],
        "derived": snap["derived"],
        "vertical": snap["vertical"],
        "in_signed_canonical": False,
        "plain": snap["plain"],
    }


def load_undos() -> list[dict[str, Any]]:
    path = _undo_path()
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return list(data.get("rows") or []) if isinstance(data, dict) else []


def _save_undos(rows: list[dict[str, Any]]) -> None:
    path = _undo_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"spec": UNDO_SPEC, "rows": rows[-200:]}, indent=2), encoding="utf-8")


def undo(event_id: str, snap: dict[str, Any]) -> dict[str, Any]:
    """Item 93 — real UNDO only while the pre-V1 window is open."""
    event_id = (event_id or "").strip()
    if not event_id:
        return {"ok": False, "error": "event_id_required", "spec": UNDO_SPEC}
    if snap.get("crossed") or not snap.get("undo_open"):
        return {
            "ok": False,
            "error": "v1_crossed",
            "spec": UNDO_SPEC,
            "finality_event": snap.get("finality_event"),
            "plain": "UNDO is removed the instant V1 is crossed.",
        }
    rows = load_undos()
    rec = {
        "event_id": event_id,
        "vertical": snap.get("vertical"),
        "finality_event": snap.get("finality_event"),
        "undone": True,
        "at": _iso(),
    }
    rows.append(rec)
    _save_undos(rows)
    return {"ok": True, "spec": UNDO_SPEC, **rec, "undo_open": True}


def undone(event_id: str) -> bool:
    event_id = (event_id or "").strip()
    return any(r.get("event_id") == event_id and r.get("undone") for r in load_undos())


def gauge(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Item 94 — decisions approaching V1, not only after-the-fact status."""
    approaching = []
    crossed = []
    for row in rows:
        snap = for_receipt(row)
        item = {
            "id": row.get("id"),
            "decision": row.get("decision"),
            "vertical": snap["vertical"],
            "finality_event": snap["finality_event"],
            "v1_distance": snap["v1_distance"],
            "crossed": snap["crossed"],
            "undo_open": snap["undo_open"] and not undone(str(row.get("id") or "")),
            "undone": undone(str(row.get("id") or "")),
        }
        if snap["crossed"]:
            crossed.append(item)
        else:
            approaching.append(item)
    approaching.sort(key=lambda x: x["v1_distance"])
    return {
        "spec": SPEC,
        "plain": "V1-distance is remaining room before the named irreversible instant. 0 is crossed.",
        "approaching": approaching[:50],
        "crossed": crossed[:50],
        "lookup_table": False,
    }
