"""Item 166 — one-breath graph for a stranger, not an analyst.

Analyst overlays (confidence, path tracing, drill-down) stay on /graph.
This surface refuses hops > 1, refuses to color by sigma, and speaks one
sentence a person can check in ten seconds. The sentence hashes with the
receipt ids — Kudurru law: flex object is the proof object.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

try:
    from gate import kudurru as kudurru_mod
except ImportError:
    import kudurru as kudurru_mod

try:
    from gate import sanitize as sanitize_mod
except ImportError:
    import sanitize as sanitize_mod

SPEC = "gate-stranger-graph-v1"
MAX_HOPS = 1


def _short(node_id: str) -> str:
    raw = (node_id or "").strip()
    _, _, ref = raw.partition(":")
    text = ref or raw
    if len(text) > 18:
        return text[:8] + "…" + text[-6:]
    return text


def breath(
    graph: dict[str, Any] | None,
    *,
    flags: list[dict[str, Any]] | None = None,
    verify_path: str = "/verify",
) -> dict[str, Any]:
    g = graph if isinstance(graph, dict) else {}
    hops = int((g.get("query") or {}).get("max_hops") or 0)
    if hops > MAX_HOPS:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "too_much_graph",
            "plain": "A stranger gets one hop. Multi-hop is an analyst surface.",
        }
    edges = list(g.get("edges") or [])
    nodes = {n.get("node_id"): n for n in (g.get("nodes") or []) if isinstance(n, dict)}
    undisposed = [f for f in (flags or []) if not f.get("disposition")]
    if not edges:
        sentence = "No shared edge on this mouth. Empty is empty, not a hidden network."
        kind = "empty"
        ids: list[str] = []
    else:
        e = edges[0]
        a = _short(str(e.get("from_node_id") or ""))
        b = _short(str(e.get("to_node_id") or ""))
        kind_edge = sanitize_mod.strip_agent(e.get("edge_type"), limit=80) or "a field"
        sentence = f"{a} and {b} share {kind_edge}. That is a match, not a finding of coordination."
        kind = "match"
        ids = [str(e.get("from_node_id") or ""), str(e.get("to_node_id") or "")]
        if e.get("source_receipt_id"):
            ids.append(str(e["source_receipt_id"]))
    flag_line = ""
    if undisposed:
        flag_line = "A 133 flag exists and has not been disposed. A flag is not a verdict."
    check = f"Check {verify_path}. You do not log in."
    lines = [sentence]
    if flag_line:
        lines.append(flag_line)
    lines.append(check)
    card = " ".join(lines)
    root = kudurru_mod.root_hash(ids or ["empty-stranger-graph"])
    digest = hashlib.sha256(card.encode()).hexdigest()
    return {
        "spec": SPEC,
        "ok": True,
        "kind": kind,
        "hops": hops,
        "edge_count_shown": 0 if kind == "empty" else 1,
        "extra_edges_hidden": max(0, len(edges) - 1),
        "sigma_colored": False,
        "sentence": sentence,
        "flag_line": flag_line or None,
        "check_line": check,
        "card": card,
        "card_sha256": digest,
        "receipt_root_hash": root,
        "verify_path": verify_path,
        "ten_second": True,
        "plain": card,
    }


def from_bind_rows(
    rows: list[dict[str, Any]],
    *,
    root_type: str,
    root_id: str,
    flags: list[dict[str, Any]] | None = None,
    verify_path: str = "/verify",
) -> dict[str, Any]:
    try:
        from gate import link_graph as lg
    except ImportError:
        import link_graph as lg

    graph = lg.graph_from_bind_events(
        rows,
        root_type=root_type,
        root_id=root_id,
        max_hops=MAX_HOPS,
        edge_types=["ingredient", "co_signer", "shared_counterparty"],
    )
    return breath(graph, flags=flags, verify_path=verify_path)
