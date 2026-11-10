"""Items 123–124 — custody link-graph view over ingredient chaining."""
from __future__ import annotations

from typing import Any

try:
    from gate import standing as standing_mod
except ImportError:
    import standing as standing_mod

SPEC = "gate-custody-graph-v1"
ROLES = ("erra", "gate", "verra", "mishara")
ROLE_Y = {"erra": 56, "gate": 140, "verra": 224, "mishara": 308}
ROLE_LABEL = {
    "erra": "Erra signal",
    "gate": "Gate decision",
    "verra": "Verra bind",
    "mishara": "Mishara outcome",
}


def _roles(row: dict[str, Any]) -> list[str]:
    hop = row.get("hop") if isinstance(row.get("hop"), dict) else {}
    roles = ["gate"]
    if hop.get("erra") or hop.get("pattern_grade") is not None or hop.get("reason"):
        roles.insert(0, "erra")
    if hop.get("state") is not None or hop.get("verdict") is not None or hop.get("velaru"):
        roles.append("verra")
    if hop.get("mishara") or hop.get("outcome") or hop.get("harm"):
        roles.append("mishara")
    # Unique, keep order
    out = []
    for r in roles:
        if r not in out:
            out.append(r)
    return out


def view(rows: list[dict[str, Any]], *, event_id: str | None = None) -> dict[str, Any]:
    by_id = {str(r.get("id")): r for r in rows}
    start = by_id.get(str(event_id)) if event_id else (rows[-1] if rows else None)
    if not start:
        return {
            "spec": SPEC,
            "nodes": [],
            "edges": [],
            "plain": "No specimen on this mouth. Empty graph, not a hidden Palantir.",
            "width": 800,
            "height": 360,
        }
    ings = standing_mod.ingredients(start, rows)
    chain_rows = []
    for item in reversed(ings.get("ingredients") or []):
        rid = item.get("ingredient_receipt_id")
        if rid and rid in by_id:
            chain_rows.append(by_id[rid])
    chain_rows.append(start)

    nodes = []
    edges = []
    col_w = 160
    x0 = 70
    prev_gate = None
    for i, row in enumerate(chain_rows):
        x = x0 + i * col_w
        present = _roles(row)
        last = None
        for role in present:
            nid = f"{role}:{row.get('id')}"
            nodes.append(
                {
                    "id": nid,
                    "role": role,
                    "label": ROLE_LABEL[role],
                    "event_id": row.get("id"),
                    "decision": row.get("decision"),
                    "created_at": row.get("created_at"),
                    "receipt_hash": row.get("receipt_hash"),
                    "x": x,
                    "y": ROLE_Y[role],
                }
            )
            if last:
                edges.append(
                    {
                        "from": last,
                        "to": nid,
                        "kind": "role",
                        "x1": x,
                        "y1": ROLE_Y[last.split(":")[0]],
                        "x2": x,
                        "y2": ROLE_Y[role],
                    }
                )
            last = nid
            if role == "gate":
                if prev_gate:
                    edges.append(
                        {
                            "from": prev_gate,
                            "to": nid,
                            "kind": "ingredient",
                            "x1": x - col_w,
                            "y1": ROLE_Y["gate"],
                            "x2": x,
                            "y2": ROLE_Y["gate"],
                        }
                    )
                prev_gate = nid
    return {
        "spec": SPEC,
        "plain": (
            "Erra → Gate → Verra → Mishara as nodes. Horizontal edges are item 114 "
            "ingredient links. Near-black plate, one accent, machine-truth on IDs."
        ),
        "nodes": nodes,
        "edges": edges,
        "width": max(800, x0 + len(chain_rows) * col_w),
        "height": 360,
        "start": start.get("id"),
        "length": len(chain_rows),
    }
