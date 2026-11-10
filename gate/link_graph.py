"""Item 132 — cross-receipt link graph over existing bind_events.

Edges are ingredient (prev_receipt_hash / hop.ingredients) and co_signer.
Node identity is interned as type:id. Receipt hashes contain underscores;
never parse identity by splitting that string.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

SPEC = "gate-link-graph-v1"
ENTITY_TYPES = ("actor", "org", "receipt_id")
EDGE_TYPES = ("ingredient", "co_signer", "shared_cohort", "shared_counterparty")
MAX_HOPS_CAP = 8


@dataclass
class ReceiptRecord:
    receipt_id: str
    operator_id: str
    org_id: str
    cohort_vertical: str
    ingredients: list[dict[str, str]]
    co_signers: list[str]
    metrics: dict[str, float]
    created_at: str
    event_id: str = ""
    counterparties: list[str] = field(default_factory=list)


@dataclass
class LinkGraphNode:
    node_id: str
    entity_type: str
    entity_ref: str


@dataclass
class LinkGraphEdge:
    edge_id: str
    from_node_id: str
    to_node_id: str
    edge_type: str
    source_receipt_id: str


class NodeRegistry:
    def __init__(self) -> None:
        self._by_id: dict[str, LinkGraphNode] = {}

    def intern(self, entity_type: str, entity_id: str) -> LinkGraphNode:
        node_id = f"{entity_type}:{entity_id}"
        existing = self._by_id.get(node_id)
        if existing:
            return existing
        node = LinkGraphNode(node_id=node_id, entity_type=entity_type, entity_ref=entity_id)
        self._by_id[node_id] = node
        return node

    def get(self, node_id: str) -> LinkGraphNode | None:
        return self._by_id.get(node_id)


def records_from_bind_events(rows: Iterable[dict[str, Any]]) -> list[ReceiptRecord]:
    out: list[ReceiptRecord] = []
    for row in rows:
        rid = (row.get("receipt_hash") or row.get("id") or "").strip()
        if not rid:
            continue
        hop = row.get("hop") if isinstance(row.get("hop"), dict) else {}
        ingredients: list[dict[str, str]] = []
        prev = (row.get("prev_receipt_hash") or "").strip()
        if prev:
            ingredients.append({"ingredient_receipt_id": prev, "ingredient_hash": prev})
        for ing in hop.get("ingredients") or []:
            if isinstance(ing, dict) and ing.get("ingredient_receipt_id"):
                ingredients.append(
                    {
                        "ingredient_receipt_id": str(ing["ingredient_receipt_id"]),
                        "ingredient_hash": str(ing.get("ingredient_hash") or ing["ingredient_receipt_id"]),
                    }
                )
        co_signers = [str(x) for x in (hop.get("co_signers") or []) if x]
        raw_cp = hop.get("counterparties")
        if isinstance(raw_cp, list):
            counterparties = [str(x).strip() for x in raw_cp if str(x).strip()]
        elif hop.get("counterparty"):
            counterparties = [str(hop.get("counterparty")).strip()]
        elif hop.get("counterparty_id"):
            counterparties = [str(hop.get("counterparty_id")).strip()]
        else:
            counterparties = []
        decision = (row.get("decision") or "").upper()
        block = 1.0 if decision in ("BLOCK", "HALT") else 0.0
        out.append(
            ReceiptRecord(
                receipt_id=rid,
                operator_id=str(row.get("account_id") or row.get("fuse_id") or "anonymous"),
                org_id=str(row.get("account_id") or "public"),
                cohort_vertical=str(hop.get("cohort_vertical") or hop.get("vertical") or "unspecified"),
                ingredients=ingredients,
                co_signers=co_signers,
                metrics={"block_rate": block},
                created_at=str(row.get("created_at") or ""),
                event_id=str(row.get("id") or ""),
                counterparties=counterparties,
            )
        )
    return out


class LinkGraphBuilder:
    def __init__(self, records: list[ReceiptRecord]) -> None:
        self._by_receipt = {r.receipt_id: r for r in records}

    def _edges(self, registry: NodeRegistry) -> list[LinkGraphEdge]:
        edges: list[LinkGraphEdge] = []
        for receipt in self._by_receipt.values():
            receipt_node = registry.intern("receipt_id", receipt.receipt_id)
            registry.intern("actor", receipt.operator_id)
            registry.intern("org", receipt.org_id)
            for ing in receipt.ingredients:
                other = registry.intern("receipt_id", ing["ingredient_receipt_id"])
                edges.append(
                    LinkGraphEdge(
                        edge_id=f"ingredient:{other.node_id}->{receipt_node.node_id}",
                        from_node_id=other.node_id,
                        to_node_id=receipt_node.node_id,
                        edge_type="ingredient",
                        source_receipt_id=receipt.receipt_id,
                    )
                )
            for signer in receipt.co_signers:
                actor = registry.intern("actor", signer)
                edges.append(
                    LinkGraphEdge(
                        edge_id=f"co_signer:{actor.node_id}->{receipt_node.node_id}",
                        from_node_id=actor.node_id,
                        to_node_id=receipt_node.node_id,
                        edge_type="co_signer",
                        source_receipt_id=receipt.receipt_id,
                    )
                )
            for cp in receipt.counterparties:
                other = registry.intern("org", cp)
                edges.append(
                    LinkGraphEdge(
                        edge_id=f"shared_counterparty:{receipt_node.node_id}->{other.node_id}",
                        from_node_id=receipt_node.node_id,
                        to_node_id=other.node_id,
                        edge_type="shared_counterparty",
                        source_receipt_id=receipt.receipt_id,
                    )
                )
        return edges

    def _cohort_edges(self, registry: NodeRegistry, cohort: str) -> list[LinkGraphEdge]:
        members = sorted(
            {r.operator_id for r in self._by_receipt.values() if r.cohort_vertical == cohort}
        )
        edges: list[LinkGraphEdge] = []
        for i, a_id in enumerate(members):
            for b_id in members[i + 1 :]:
                a = registry.intern("actor", a_id)
                b = registry.intern("actor", b_id)
                edges.append(
                    LinkGraphEdge(
                        edge_id=f"shared_cohort:{a.node_id}<->{b.node_id}",
                        from_node_id=a.node_id,
                        to_node_id=b.node_id,
                        edge_type="shared_cohort",
                        source_receipt_id="",
                    )
                )
        return edges

    def expand(
        self,
        *,
        root_type: str,
        root_id: str,
        max_hops: int = 3,
        edge_types: list[str] | None = None,
    ) -> dict[str, Any]:
        if root_type not in ENTITY_TYPES:
            raise ValueError("unknown_root_type")
        hops = max(0, min(int(max_hops), MAX_HOPS_CAP))
        wanted = set(edge_types or ["ingredient", "co_signer"])
        wanted &= set(EDGE_TYPES)
        registry = NodeRegistry()
        root = registry.intern(root_type, root_id)
        all_edges = self._edges(registry)
        if "shared_cohort" in wanted:
            rec = next((r for r in self._by_receipt.values() if r.operator_id == root_id), None)
            if rec:
                all_edges.extend(self._cohort_edges(registry, rec.cohort_vertical))
        relevant = [e for e in all_edges if e.edge_type in wanted]
        nodes = {root.node_id: root}
        edges: dict[str, LinkGraphEdge] = {}
        frontier = {root.node_id}
        visited = {root.node_id}
        for _ in range(hops):
            nxt: set[str] = set()
            for edge in relevant:
                if edge.from_node_id not in frontier and edge.to_node_id not in frontier:
                    continue
                edges[edge.edge_id] = edge
                for side in (edge.from_node_id, edge.to_node_id):
                    if side in visited:
                        continue
                    visited.add(side)
                    nxt.add(side)
                    node = registry.get(side)
                    if node is None:
                        raise RuntimeError("link graph node was never interned")
                    nodes[side] = node
            if not nxt:
                break
            frontier = nxt
        return {
            "spec": SPEC,
            "query": {
                "root_entity_type": root_type,
                "root_entity_id": root_id,
                "max_hops": hops,
                "edge_types": sorted(wanted),
            },
            "nodes": [n.__dict__ for n in nodes.values()],
            "edges": [e.__dict__ for e in edges.values()],
            "demo": False,
            "their_production": False,
        }


def graph_from_bind_events(
    rows: list[dict[str, Any]],
    *,
    root_type: str,
    root_id: str,
    max_hops: int = 3,
    edge_types: list[str] | None = None,
) -> dict[str, Any]:
    records = records_from_bind_events(rows)
    return LinkGraphBuilder(records).expand(
        root_type=root_type,
        root_id=root_id,
        max_hops=max_hops,
        edge_types=edge_types,
    )


def catalog_roots(rows: list[dict[str, Any]], *, limit: int = 40) -> dict[str, Any]:
    records = records_from_bind_events(rows)
    receipts: list[dict[str, str]] = []
    actors: list[str] = []
    orgs: list[str] = []
    seen_act: set[str] = set()
    seen_org: set[str] = set()
    for rec in reversed(records):
        if len(receipts) < limit:
            receipts.append(
                {
                    "receipt_id": rec.receipt_id,
                    "event_id": rec.event_id,
                    "operator_id": rec.operator_id,
                }
            )
        if rec.operator_id not in seen_act and len(actors) < limit:
            seen_act.add(rec.operator_id)
            actors.append(rec.operator_id)
        if rec.org_id not in seen_org and len(orgs) < limit:
            seen_org.add(rec.org_id)
            orgs.append(rec.org_id)
    return {
        "spec": SPEC,
        "edge_types": list(EDGE_TYPES),
        "entity_types": list(ENTITY_TYPES),
        "receipts": receipts,
        "actors": actors,
        "orgs": orgs,
        "empty": not records,
        "plain": (
            "No receipts on this mouth yet. Empty graph, not a hidden network."
            if not records
            else "Roots from live bind_events. Not mock data."
        ),
    }


def inspect_node(rows: list[dict[str, Any]], node_id: str) -> dict[str, Any]:
    nid = (node_id or "").strip()
    if ":" not in nid:
        return {"spec": SPEC, "ok": False, "error": "node_id_required", "plain": "node_id is type:id, never split on underscore."}
    entity_type, _, entity_ref = nid.partition(":")
    if entity_type not in ENTITY_TYPES:
        return {"spec": SPEC, "ok": False, "error": "unknown_root_type", "allowed": list(ENTITY_TYPES)}
    records = records_from_bind_events(rows)
    hits = []
    for rec in records:
        match = (
            (entity_type == "receipt_id" and rec.receipt_id == entity_ref)
            or (entity_type == "actor" and rec.operator_id == entity_ref)
            or (entity_type == "org" and rec.org_id == entity_ref)
        )
        if not match:
            continue
        hits.append(
            {
                "event_id": rec.event_id,
                "receipt_id": rec.receipt_id,
                "operator_id": rec.operator_id,
                "org_id": rec.org_id,
                "cohort_vertical": rec.cohort_vertical,
                "created_at": rec.created_at,
            }
        )
    return {
        "spec": SPEC,
        "ok": True,
        "node_id": nid,
        "entity_type": entity_type,
        "entity_ref": entity_ref,
        "rows": hits[:25],
        "plain": "Live bind_events pointed to by this node. Empty if the id is not on this mouth.",
    }
