"""Oath Compiler — ROE / policy text → executable inhibit graph.

Civilizational question: what compiles ROE into inhibit?
Answer (foothill): structured oath clauses → graph nodes the mouth can enforce
(CHOKE / HOLD / DENY / quorum / CHARGE / cool-off / witness).

Not a full treaty AI. A compiler for named clause kinds desks already use.
Ethics that execute — under coordinators.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-oath-compiler-v1"
INVENTION = "Oath Compiler"
FAMILY = "applicable_now"

# Clause kinds → inhibit ops
CLAUSE_DENY_ALWAYS = "deny_always"
CLAUSE_REQUIRE_QUORUM = "require_quorum"
CLAUSE_REQUIRE_CHARGE = "require_charge"
CLAUSE_COOL_OFF = "cool_off"
CLAUSE_WITNESS = "require_witness"
CLAUSE_LOSS_OF_LINK_DENY = "loss_of_link_deny"
CLAUSE_NO_CHARISMA = "no_charisma_live"
CLAUSE_NO_PANIC = "no_panic_live"
CLAUSE_MASS_FLOOR = "mass_floor"
CLAUSE_SUNSET = "sunset_live"
CLAUSE_WINDOW = "live_window_only"
CLAUSE_MERCY_SCAR = "mercy_requires_scar"

OP_DENY = "DENY"
OP_CHOKE = "CHOKE"
OP_HOLD = "HOLD"
OP_REQUIRE = "REQUIRE"
OP_ATTACH = "ATTACH_INVENTION"


def _node(
    *,
    node_id: str,
    op: str,
    detail: str,
    invention: str | None = None,
    params: dict | None = None,
    source_clause: str | None = None,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "id": node_id,
        "op": op,
        "detail": detail,
    }
    if invention:
        out["invention"] = invention
    if params:
        out["params"] = params
    if source_clause:
        out["source_clause"] = source_clause
    return out


def compile_clauses(clauses: list[dict] | None = None) -> dict[str, Any]:
    """Compile a list of oath clauses into an inhibit graph."""
    nodes: list[dict[str, Any]] = []
    errors: list[str] = []
    edges: list[dict[str, str]] = []
    prev = None

    for i, raw in enumerate(clauses or []):
        if not isinstance(raw, dict):
            errors.append(f"clause_{i}_not_object")
            continue
        kind = (raw.get("kind") or raw.get("type") or "").strip().lower()
        label = (raw.get("label") or raw.get("text") or kind or f"clause_{i}").strip()
        nid = (raw.get("id") or f"c{i}_{kind or 'x'}").strip()
        node = None

        if kind in (CLAUSE_DENY_ALWAYS, "taboo", "absolute_deny"):
            node = _node(
                node_id=nid,
                op=OP_DENY,
                detail=label or "Named taboo — absolute DENY",
                source_clause=kind,
            )
        elif kind in (CLAUSE_REQUIRE_QUORUM, "quorum", "n_of_m"):
            n = int(raw.get("n") or raw.get("required_n") or 2)
            node = _node(
                node_id=nid,
                op=OP_REQUIRE,
                detail=label or f"Require {n}-of-M desk quorum",
                invention="desk_quorum_fob",
                params={"required_n": n},
                source_clause=kind,
            )
        elif kind in (CLAUSE_REQUIRE_CHARGE, "charge", "charge_only"):
            node = _node(
                node_id=nid,
                op=OP_REQUIRE,
                detail=label or "CHARGE-only resurrection / sacred clear",
                invention="charge_bride",
                params={"charge_required": True},
                source_clause=kind,
            )
        elif kind in (CLAUSE_COOL_OFF, "cool", "cool_off"):
            tau = int(raw.get("seconds") or raw.get("tau") or 3600)
            node = _node(
                node_id=nid,
                op=OP_HOLD,
                detail=label or f"Cool-off HOLD({tau}s) before LIVE eligible",
                invention="temporal_sheath",
                params={"cool_off_seconds": tau},
                source_clause=kind,
            )
        elif kind in (CLAUSE_WITNESS, "witness", "stranger_verify"):
            node = _node(
                node_id=nid,
                op=OP_REQUIRE,
                detail=label or "Stranger witness seat before LIVE",
                invention="witness_seat",
                params={"witness_required": True},
                source_clause=kind,
            )
        elif kind in (CLAUSE_LOSS_OF_LINK_DENY, "anti_perimeter", "deadman"):
            node = _node(
                node_id=nid,
                op=OP_DENY,
                detail=label or "Loss of contact ⇒ DENY (anti-Perimeter)",
                invention="deadman_echo",
                params={"loss_of_link": "DENY"},
                source_clause=kind,
            )
        elif kind in (CLAUSE_NO_CHARISMA, "anti_charisma", "no_boss_yes"):
            node = _node(
                node_id=nid,
                op=OP_CHOKE,
                detail=label or "Boss/chat yes without quorum = forged CHOKE",
                invention="soft_yes_snare",
                params={"boss_said_yes": "CHOKE"},
                source_clause=kind,
            )
        elif kind in (CLAUSE_NO_PANIC, "anti_panic"):
            node = _node(
                node_id=nid,
                op=OP_CHOKE,
                detail=label or "Panic soft-yes without incident path = CHOKE",
                invention="panic_latch",
                params={"panic_soft_yes": "CHOKE"},
                source_clause=kind,
            )
        elif kind in (CLAUSE_MASS_FLOOR, "mass_floor"):
            floor = (raw.get("floor") or raw.get("mass_class") or "heavy").strip().lower()
            node = _node(
                node_id=nid,
                op=OP_ATTACH,
                detail=label or f"Mass floor {floor}",
                invention="mass_tag",
                params={"mass_floor": floor},
                source_clause=kind,
            )
        elif kind in (CLAUSE_SUNSET, "sunset"):
            ttl = int(raw.get("ttl_seconds") or raw.get("seconds") or 86400)
            node = _node(
                node_id=nid,
                op=OP_HOLD,
                detail=label or f"LIVE/mercy sunsets after {ttl}s",
                invention="pardon_sunset",
                params={"ttl_seconds": ttl},
                source_clause=kind,
            )
        elif kind in (CLAUSE_WINDOW, "window"):
            node = _node(
                node_id=nid,
                op=OP_HOLD,
                detail=label or "LIVE only inside declared window",
                invention="temporal_sheath",
                params={
                    "window_start": raw.get("start"),
                    "window_end": raw.get("end"),
                },
                source_clause=kind,
            )
        elif kind in (CLAUSE_MERCY_SCAR, "mercy"):
            node = _node(
                node_id=nid,
                op=OP_REQUIRE,
                detail=label or "Mercy only scarred + co-signed + sunsetting",
                invention="pardon_sunset",
                params={"scar": True, "cosign": True, "sunset": True},
                source_clause=kind,
            )
        else:
            errors.append(f"unknown_clause_kind:{kind or 'missing'}")
            node = _node(
                node_id=nid,
                op=OP_CHOKE,
                detail=f"Uncompilable clause — CHOKE until kind known ({label})",
                source_clause=kind or "unknown",
            )

        nodes.append(node)
        if prev is not None:
            edges.append({"from": prev, "to": nid, "rel": "then"})
        prev = nid

    # Always terminate with throat + path compiler lean
    tail_id = "mouth_tail"
    nodes.append(
        _node(
            node_id=tail_id,
            op=OP_ATTACH,
            detail="Evaluate Throat; compile remaining path if not OPEN",
            invention="throat+bind_path_compiler",
        )
    )
    if prev is not None:
        edges.append({"from": prev, "to": tail_id, "rel": "then"})

    executable = len(errors) == 0 and any(
        n.get("op") in (OP_DENY, OP_REQUIRE, OP_HOLD, OP_CHOKE) for n in nodes[:-1]
    ) if nodes else False

    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "compiled": True,
        "executable": executable and not errors,
        "clause_count": len(clauses or []),
        "node_count": len(nodes),
        "nodes": nodes,
        "edges": edges,
        "errors": errors,
        "inventions_referenced": sorted(
            {n["invention"] for n in nodes if n.get("invention")}
        ),
        "rule": (
            "Unknown clause kinds CHOKE — ethics that cannot compile must not soft-allow. "
            "Compiled graph attaches inventions; Throat still owns OPEN/CLOSED/CHOKE."
        ),
        "civilizational_question": "What compiles ROE into inhibit?",
        "posture": "Under coordinators. Oath → graph; never private Omega.",
    }


def pas_bind_oath() -> list[dict]:
    """Seed oath for PAS bind desk — compiles to Gate foothill stack."""
    return [
        {"id": "no_soft", "kind": CLAUSE_NO_CHARISMA, "label": "No boss/chat LIVE without quorum"},
        {"id": "timeout", "kind": CLAUSE_LOSS_OF_LINK_DENY, "label": "Timeout / link loss ⇒ DENY"},
        {"id": "mass", "kind": CLAUSE_MASS_FLOOR, "floor": "heavy", "label": "Bind mass floor heavy"},
        {"id": "quorum", "kind": CLAUSE_REQUIRE_QUORUM, "n": 2, "label": "Heavy/sacred needs desk quorum"},
        {"id": "charge", "kind": CLAUSE_REQUIRE_CHARGE, "label": "Sacred / dead fuse needs CHARGE"},
        {"id": "witness", "kind": CLAUSE_WITNESS, "label": "Stranger verify on every hop"},
    ]


def force_roe_oath_seed() -> list[dict]:
    """Seed ROE-shaped oath for Gate-D/O demos — not a real ROE."""
    return [
        {"id": "taboo", "kind": CLAUSE_DENY_ALWAYS, "label": "Named taboo acts — absolute DENY"},
        {"id": "anti_perim", "kind": CLAUSE_LOSS_OF_LINK_DENY, "label": "Loss of contact ⇒ DENY"},
        {"id": "no_panic", "kind": CLAUSE_NO_PANIC, "label": "Panic soft-yes forged"},
        {"id": "no_charisma", "kind": CLAUSE_NO_CHARISMA, "label": "Commander vibe ≠ LIVE"},
        {"id": "quorum", "kind": CLAUSE_REQUIRE_QUORUM, "n": 2, "label": "Release needs quorum"},
        {"id": "cool", "kind": CLAUSE_COOL_OFF, "seconds": 300, "label": "Cool-off before sacred release"},
        {"id": "mercy", "kind": CLAUSE_MERCY_SCAR, "label": "Exception only scarred+cosigned+sunset"},
        {"id": "witness", "kind": CLAUSE_WITNESS, "label": "Stranger prove after"},
    ]


def compile_preset(name: str | None = None) -> dict[str, Any]:
    n = (name or "pas_bind").strip().lower()
    if n in ("force", "roe", "gate_d", "gate_o", "force_roe"):
        clauses = force_roe_oath_seed()
        preset = "force_roe_seed"
    else:
        clauses = pas_bind_oath()
        preset = "pas_bind"
    out = compile_clauses(clauses)
    out["preset"] = preset
    out["clauses_in"] = clauses
    return out


def evaluate_against_plan(graph: dict, plan: dict) -> dict[str, Any]:
    """Lightweight check: which REQUIRE/DENY nodes are already satisfied on plan."""
    nodes = graph.get("nodes") if isinstance(graph, dict) else []
    satisfied = []
    violated = []
    pending = []
    for n in nodes or []:
        if not isinstance(n, dict):
            continue
        op = n.get("op")
        inv = n.get("invention") or ""
        nid = n.get("id")
        if op == OP_DENY and plan.get("loss_of_link"):
            violated.append(nid)
        elif op == OP_REQUIRE and "quorum" in inv:
            q = plan.get("desk_quorum_fob") if isinstance(plan.get("desk_quorum_fob"), dict) else {}
            if q.get("may_proceed") or q.get("verdict") in ("QUORUM_OK", "QUORUM_NOT_REQUIRED"):
                satisfied.append(nid)
            else:
                pending.append(nid)
        elif op == OP_REQUIRE and "charge" in inv:
            if plan.get("charge_id") or plan.get("charge_present"):
                satisfied.append(nid)
            else:
                pending.append(nid)
        elif op == OP_CHOKE and plan.get("boss_said_yes") and not plan.get("charge_id"):
            violated.append(nid)
        elif op in (OP_ATTACH, OP_HOLD):
            pending.append(nid)
        else:
            pending.append(nid)
    return {
        "satisfied": satisfied,
        "pending": pending,
        "violated": violated,
        "may_proceed_hint": not violated and not pending,
    }


def attach(plan: dict, *, public_url: str = "", clauses: list | None = None) -> dict:
    if clauses:
        graph = compile_clauses(clauses)
    elif plan.get("oath_preset"):
        graph = compile_preset(str(plan.get("oath_preset")))
    elif isinstance(plan.get("oath_clauses"), list):
        graph = compile_clauses(plan.get("oath_clauses"))
    else:
        graph = compile_preset("pas_bind")
    check = evaluate_against_plan(graph, plan)
    plan["oath_compiler"] = {
        **graph,
        "evaluation": check,
    }
    if public_url:
        base = public_url.rstrip("/")
        plan["oath_compiler"]["well_known"] = f"{base}/.well-known/oath-compiler.json"
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "ROE / oath clauses → inhibit graph the mouth can enforce — ethics that execute.",
        "clause_kinds": [
            CLAUSE_DENY_ALWAYS,
            CLAUSE_REQUIRE_QUORUM,
            CLAUSE_REQUIRE_CHARGE,
            CLAUSE_COOL_OFF,
            CLAUSE_WITNESS,
            CLAUSE_LOSS_OF_LINK_DENY,
            CLAUSE_NO_CHARISMA,
            CLAUSE_NO_PANIC,
            CLAUSE_MASS_FLOOR,
            CLAUSE_SUNSET,
            CLAUSE_WINDOW,
            CLAUSE_MERCY_SCAR,
        ],
        "presets": {
            "pas_bind": f"POST {base}/demo/pas/oath-compiler  {{\"preset\":\"pas_bind\"}}",
            "force_roe_seed": f"POST {base}/demo/pas/oath-compiler  {{\"preset\":\"force_roe\"}}",
        },
        "demo": f"POST {base}/demo/pas/oath-compiler",
        "well_known": f"{base}/.well-known/oath-compiler.json",
        "pairs_with": "Throat · Bind Path Compiler · Desk Quorum · Charge Bride · Temporal Sheath",
        "civilizational_question": "What compiles ROE into inhibit?",
        "posture": "Under coordinators. Unknown clauses CHOKE. Never private Omega.",
    }
