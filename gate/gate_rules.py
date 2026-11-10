"""Item 23 — no-code gate rules. JSON only. No deploy per rule."""
from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Any

SPEC = "gate-rules-v1"
OPS = ("eq", "neq", "gt", "lt", "gte", "lte", "contains")
ACTIONS = ("BLOCK", "HOLD", "ALLOW")


def _path() -> Path:
    return Path(os.getenv("GATE_RULES_PATH") or Path(__file__).resolve().parent / "data" / "gate_rules.json")


def load_rules() -> list[dict[str, Any]]:
    p = _path()
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return list(data.get("rules") or []) if isinstance(data, dict) else []


def save_rules(rules: list[dict[str, Any]]) -> None:
    p = _path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"spec": SPEC, "rules": rules}, indent=2), encoding="utf-8")


def add_rule(*, name: str, field: str, op: str, value: Any, action: str = "BLOCK") -> dict[str, Any]:
    op = (op or "").strip().lower()
    action = (action or "BLOCK").strip().upper()
    if op not in OPS:
        raise ValueError("unknown_op")
    if action not in ACTIONS:
        raise ValueError("unknown_action")
    field = (field or "").strip()
    if not field or not name.strip():
        raise ValueError("name_and_field_required")
    rule = {
        "id": "rul_" + uuid.uuid4().hex[:10],
        "name": name.strip(),
        "field": field,
        "op": op,
        "value": value,
        "action": action,
    }
    rules = load_rules()
    rules.append(rule)
    save_rules(rules)
    return rule


def _get(body: dict, field: str) -> Any:
    cur: Any = body
    for part in field.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def _cmp(left: Any, op: str, right: Any) -> bool:
    if op == "eq":
        return left == right
    if op == "neq":
        return left != right
    if op == "contains":
        return str(right) in str(left or "")
    try:
        lv, rv = float(left), float(right)
    except (TypeError, ValueError):
        return False
    if op == "gt":
        return lv > rv
    if op == "lt":
        return lv < rv
    if op == "gte":
        return lv >= rv
    if op == "lte":
        return lv <= rv
    return False


def preview(body: dict[str, Any], rules: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    hits = []
    for rule in rules if rules is not None else load_rules():
        if _cmp(_get(body, rule["field"]), rule["op"], rule["value"]):
            hits.append(rule)
    action = "ALLOW"
    for h in hits:
        if h["action"] == "BLOCK":
            action = "BLOCK"
            break
        if h["action"] == "HOLD":
            action = "HOLD"
    return {
        "spec": SPEC,
        "action": action,
        "hits": hits,
        "rule_count": len(rules if rules is not None else load_rules()),
    }
