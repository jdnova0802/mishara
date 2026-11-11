"""Item 156 — declarative property-derived link types.

Coded resolvers (ingredient, co_signer, shared_cohort, shared_counterparty)
stay as built. property_match is for field-equality edges that should not
need a deploy.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from gate import link_graph as lg
except ImportError:
    import link_graph as lg

try:
    from gate import sanitize as sanitize_mod
except ImportError:
    import sanitize as sanitize_mod

SPEC = "gate-ontology-links-v1"
OBJECT_TYPES = ("receipt", "operator", "org", "campaign_cluster")
RESOLUTIONS = ("property_match", "coded_resolver")
CODED = ("ingredient", "co_signer", "shared_cohort", "shared_counterparty")


def _iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _path() -> Path:
    return Path(os.getenv("GATE_ONTOLOGY_PATH") or Path(__file__).resolve().parent / "data" / "ontology_links.json")


def _load() -> dict[str, Any]:
    path = _path()
    if not path.exists():
        return {
            "spec": SPEC,
            "object_types": [
                {"object_type_id": "receipt", "properties": ["device_fingerprint", "payment_processor_id", "cohort_vertical"]},
                {"object_type_id": "operator", "properties": ["operator_id", "org_id"]},
                {"object_type_id": "org", "properties": ["org_id"]},
                {"object_type_id": "campaign_cluster", "properties": ["campaign_cluster_id"]},
            ],
            "link_types": [
                {"link_type_id": "coded_ingredient", "name": "ingredient", "resolution": "coded_resolver", "coded_resolver_ref": "ingredient"},
                {"link_type_id": "coded_co_signer", "name": "co_signer", "resolution": "coded_resolver", "coded_resolver_ref": "co_signer"},
                {"link_type_id": "coded_shared_cohort", "name": "shared_cohort", "resolution": "coded_resolver", "coded_resolver_ref": "shared_cohort"},
                {"link_type_id": "coded_shared_counterparty", "name": "shared_counterparty", "resolution": "coded_resolver", "coded_resolver_ref": "shared_counterparty"},
            ],
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"spec": SPEC, "object_types": [], "link_types": []}
    if not isinstance(data, dict):
        return {"spec": SPEC, "object_types": [], "link_types": []}
    data.setdefault("object_types", [])
    data.setdefault("link_types", [])
    return data


def _save(store: dict[str, Any]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")


def catalog() -> dict[str, Any]:
    store = _load()
    return {
        "spec": SPEC,
        "object_types": store["object_types"],
        "link_types": store["link_types"],
        "plain": "property_match is field equality. Computation still needs an engineer.",
    }


def register_link_type(
    *,
    name: str,
    from_object_type_id: str,
    to_object_type_id: str,
    resolution: str,
    registered_by: str,
    match_property: str | None = None,
    coded_resolver_ref: str | None = None,
) -> dict[str, Any]:
    res = (resolution or "").strip()
    frm = (from_object_type_id or "").strip()
    to = (to_object_type_id or "").strip()
    who = sanitize_mod.strip_agent(registered_by, limit=200)
    label = sanitize_mod.strip_agent(name, limit=200)
    if res not in RESOLUTIONS:
        return {"spec": SPEC, "ok": False, "error": "resolution_unknown", "plain": "property_match or coded_resolver."}
    if frm not in OBJECT_TYPES or to not in OBJECT_TYPES:
        return {"spec": SPEC, "ok": False, "error": "object_type_unknown", "plain": "receipt, operator, org, or campaign_cluster."}
    if not label or not who:
        return {"spec": SPEC, "ok": False, "error": "fields_required"}
    match = (match_property or "").strip() or None
    coded = (coded_resolver_ref or "").strip() or None
    if res == "property_match" and not match:
        return {"spec": SPEC, "ok": False, "error": "match_property_required", "plain": "property_match needs the field name."}
    if res == "coded_resolver":
        if coded not in CODED:
            return {"spec": SPEC, "ok": False, "error": "coded_resolver_unknown", "plain": "Point at an existing 132 resolver."}
    rec = {
        "spec": SPEC,
        "ok": True,
        "link_type_id": "lt_" + uuid.uuid4().hex[:12],
        "name": label,
        "from_object_type_id": frm,
        "to_object_type_id": to,
        "resolution": res,
        "match_property": match,
        "coded_resolver_ref": coded,
        "registered_by": who,
        "registered_at": _iso(),
        "plain": "Registered. Does not replace ingredient or co-signer logic.",
    }
    store = _load()
    store["link_types"].append(rec)
    _save(store)
    return rec


def _node_id(object_type: str, rec: lg.ReceiptRecord) -> str | None:
    if object_type == "receipt":
        return f"receipt_id:{rec.receipt_id}"
    if object_type == "operator":
        return f"actor:{rec.operator_id}"
    if object_type == "org":
        return f"org:{rec.org_id}"
    return None


def property_value(rec: lg.ReceiptRecord, prop: str) -> str:
    if prop == "device_fingerprint":
        return str(rec.properties.get("device_fingerprint") or "")
    if prop == "payment_processor_id":
        return str(rec.properties.get("payment_processor_id") or "")
    if prop == "cohort_vertical":
        return rec.cohort_vertical
    if prop == "operator_id":
        return rec.operator_id
    if prop == "org_id":
        return rec.org_id
    return str(rec.properties.get(prop) or "")


def match_edges(records: list[lg.ReceiptRecord], link_type: dict[str, Any]) -> list[dict[str, str]]:
    if link_type.get("resolution") != "property_match":
        return []
    prop = str(link_type.get("match_property") or "")
    buckets: dict[str, list[lg.ReceiptRecord]] = {}
    for rec in records:
        val = property_value(rec, prop)
        if not val:
            continue
        buckets.setdefault(val, []).append(rec)
    edges: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    frm = str(link_type.get("from_object_type_id") or "receipt")
    to = str(link_type.get("to_object_type_id") or "receipt")
    name = str(link_type.get("name") or prop)
    for val, members in buckets.items():
        if len(members) < 2:
            continue
        for i, a in enumerate(members):
            na = _node_id(frm, a)
            if not na:
                continue
            for b in members[i + 1 :]:
                nb = _node_id(to, b)
                if not nb or na == nb:
                    continue
                key = tuple(sorted((na, nb)))
                if key in seen:
                    continue
                seen.add(key)
                edges.append(
                    {
                        "edge_id": f"property_match:{name}:{na}->{nb}",
                        "from_node_id": na,
                        "to_node_id": nb,
                        "edge_type": name,
                        "source_receipt_id": a.receipt_id,
                        "match_value_present": "true",
                    }
                )
    return edges


def expand_with_declared(
    rows: list[dict[str, Any]],
    *,
    root_type: str,
    root_id: str,
    max_hops: int = 3,
    edge_types: list[str] | None = None,
) -> dict[str, Any]:
    records = lg.records_from_bind_events(rows)
    graph = lg.LinkGraphBuilder(records).expand(
        root_type=root_type,
        root_id=root_id,
        max_hops=max_hops,
        edge_types=edge_types,
    )
    declared = [lt for lt in _load()["link_types"] if lt.get("resolution") == "property_match"]
    extra = []
    wanted = set(edge_types or [])
    for lt in declared:
        if wanted and lt.get("name") not in wanted and "property_match" not in wanted:
            continue
        extra.extend(match_edges(records, lt))
    if extra:
        graph["edges"] = list(graph.get("edges") or []) + extra
        graph["declared_link_types"] = [lt.get("name") for lt in declared]
    graph["ontology_spec"] = SPEC
    return graph
