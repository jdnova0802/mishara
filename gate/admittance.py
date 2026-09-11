"""Admittance — three civilizations compressed into one verb.

Civilization I   — Actor authority (Right-to-Act + live mandate reconstruct)
Civilization II  — Subject + sink (typed irreversibility, target refusal, mutual)
Civilization III — Lineage + fact (continuity, mortality, inheritance, world-fact)

Industry is rediscovering shards:
  ocaps attenuation, IETF execution-finality drafts, action-authorization
  boundaries, A-corp liability wrappers. None ship the full stack as one noun.

ADMIT is that noun.

  Reality does not change because something computed.
  Reality changes when a delta is ADMITTED.

Outcomes: ADMITTED | REFUSED | HALTED | DEAD

Invariant: Computation proposes. Admittance disposes. Absence is evidence.
"""
from __future__ import annotations

import hashlib
import json
import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Any

try:
    from gate import continuity as continuity_mod
except ImportError:
    import continuity as continuity_mod

try:
    from gate import mandate as mandate_mod
except ImportError:
    import mandate as mandate_mod

try:
    from gate import right_to_act as rta_mod
except ImportError:
    import right_to_act as rta_mod

try:
    from gate import sinks as sinks_mod
except ImportError:
    import sinks as sinks_mod

try:
    from gate import subject as subject_mod
except ImportError:
    import subject as subject_mod

SPEC = "gate-admittance-v1"
OUTCOMES = ("ADMITTED", "REFUSED", "HALTED", "DEAD")

_lock = threading.Lock()
_facts: dict[str, dict[str, Any]] = {}
_epoch = 0


def _iso(ts: float | None = None) -> str:
    dt = datetime.fromtimestamp(ts or time.time(), tz=timezone.utc)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _reset_for_tests() -> None:
    global _epoch
    with _lock:
        _facts.clear()
        _epoch = 0


def _finder_refusal(**kwargs: Any) -> None:
    try:
        from gate import finder as finder_mod
    except ImportError:
        try:
            import finder as finder_mod
        except ImportError:
            return
    try:
        finder_mod.record_refusal(**kwargs)
    except Exception:
        return


def _finder_death(cert: dict | None) -> None:
    if not isinstance(cert, dict):
        return
    try:
        from gate import finder as finder_mod
    except ImportError:
        try:
            import finder as finder_mod
        except ImportError:
            return
    try:
        finder_mod.record_death(cert)
    except Exception:
        return


def _finder_fact(fact: dict) -> None:
    try:
        from gate import finder as finder_mod
    except ImportError:
        try:
            import finder as finder_mod
        except ImportError:
            return
    try:
        doc = {
            "spec": getattr(finder_mod, "SPEC", SPEC),
            "kind": "mandate",
            "id": f"fact:{fact.get('fact_id')}",
            "fact_id": fact.get("fact_id"),
            "title": fact.get("title") or f"FACT · {fact.get('action')}",
            "summary": fact.get("summary")
            or "World-write admitted under living authority.",
            "action": fact.get("action"),
            "sink": fact.get("sink"),
            "actor": fact.get("actor"),
            "indexed_at": _iso(),
            "indexed_at_unix": int(time.time()),
            "_haystack": " ".join(
                [
                    "fact admitted worldwrite admittance",
                    str(fact.get("fact_id") or ""),
                    str(fact.get("action") or ""),
                    str(fact.get("sink") or ""),
                    str(fact.get("actor") or ""),
                    str(fact.get("human_principal_id") or ""),
                    str(fact.get("lineage_id") or ""),
                ]
            ).lower(),
            "invariant": "Admitted facts are searchable consequence, not logs.",
        }
        finder_mod._index_doc(doc)
    except Exception:
        return


def _finish(
    outcome: str,
    *,
    admit_id: str,
    reason: str,
    gates: list,
    action: str,
    sink: str,
    actor: str,
    public_url: str,
    now: float,
    **extra: Any,
) -> dict:
    base = (public_url or "").rstrip("/")
    out: dict[str, Any] = {
        "spec": SPEC,
        "ok": False,
        "outcome": outcome,
        "admit_id": admit_id,
        "reason": reason,
        "gates": gates,
        "action": action,
        "sink": sink,
        "actor": actor or None,
        "decided_at": _iso(now),
        "manifest": f"{base}/.well-known/admittance.json" if base else None,
        "civilizations_compressed": [
            "I:actor_authority",
            "II:subject_and_sink",
            "III:lineage_and_fact",
        ],
        "invariant": (
            "Computation proposes. Admittance disposes. "
            "Three civilizations. One verb: ADMIT."
        ),
    }
    out.update(extra)
    if outcome == "REFUSED":
        digest = extra.get("refusal_digest") or (extra.get("right_to_act") or {}).get(
            "refusal_digest"
        )
        if digest:
            out["refusal_digest"] = digest
            _finder_refusal(
                refusal_digest=str(digest),
                action=action,
                sink=sink,
                actor=actor,
                signals=[reason],
                evaluation_id=(extra.get("right_to_act") or {}).get("evaluation_id"),
                fingerprint=(extra.get("right_to_act") or {}).get("fingerprint"),
            )
    if outcome == "DEAD":
        _finder_death(extra.get("death_certificate"))
    return out


def admit(
    body: dict | None = None,
    *,
    public_url: str = "",
    account_id: str | None = None,
) -> dict:
    """Single clearance for irreversible becoming."""
    global _epoch
    body = body if isinstance(body, dict) else {}
    candidate = body.get("candidate") if isinstance(body.get("candidate"), dict) else {}
    if not candidate:
        candidate = {
            "action": body.get("action"),
            "sink": body.get("sink"),
            "actor": body.get("actor") or body.get("agent_id"),
            "args": body.get("args") if isinstance(body.get("args"), dict) else {},
            "resource": body.get("resource") or body.get("target"),
        }

    action = str(candidate.get("action") or body.get("action") or "").strip()
    sink = str(candidate.get("sink") or body.get("sink") or "").strip()
    actor = str(
        candidate.get("actor") or body.get("actor") or body.get("agent_id") or ""
    ).strip()
    subject_id = str(
        body.get("subject_id")
        or body.get("subject_principal_id")
        or body.get("target_principal_id")
        or ""
    ).strip()
    human_principal_id = str(
        body.get("human_principal_id") or body.get("principal_id") or ""
    ).strip()
    human_root_digest = str(body.get("human_root_digest") or "").strip() or None
    mandate_obj = body.get("mandate") if isinstance(body.get("mandate"), dict) else None
    mandate_id = body.get("mandate_id") or (mandate_obj or {}).get("mandate_id")
    counterpart_mandate_id = str(body.get("counterpart_mandate_id") or "").strip() or None
    lineage_id = str(body.get("lineage_id") or "").strip() or None
    args = candidate.get("args") if isinstance(candidate.get("args"), dict) else {}
    amount = args.get("amount", body.get("amount"))
    try:
        amount_f = float(amount) if amount is not None else None
    except (TypeError, ValueError):
        amount_f = None

    admit_id = f"adm_{uuid.uuid4().hex}"
    now = time.time()
    gates: list[dict[str, Any]] = []

    # Civ II — typed sink (unknown → fail closed)
    sink_req = sinks_mod.require_for_act(sink or "unknown")
    gates.append({"gate": "sink", "result": sink_req})
    if not sink:
        return _finish(
            "REFUSED",
            admit_id=admit_id,
            reason="sink_required",
            gates=gates,
            action=action,
            sink=sink,
            actor=actor,
            public_url=public_url,
            now=now,
        )

    # Civ III — continuity of human root
    if human_principal_id:
        cont = continuity_mod.is_non_authorizing(human_principal_id)
        gates.append({"gate": "continuity", "result": cont})
        if cont.get("non_authorizing"):
            return _finish(
                "DEAD",
                admit_id=admit_id,
                reason="continuity_non_authorizing",
                gates=gates,
                action=action,
                sink=sink,
                actor=actor,
                human_principal_id=human_principal_id,
                public_url=public_url,
                now=now,
            )

    # Civ III — mortality
    dead = mandate_mod.is_dead(
        mandate_id=str(mandate_id) if mandate_id else None,
        human_root_digest=human_root_digest,
        agent_id=actor or None,
    )
    gates.append(
        {
            "gate": "mortality",
            "result": {"dead": dead.get("dead"), "death_id": dead.get("death_id")},
        }
    )
    if dead.get("dead"):
        return _finish(
            "DEAD",
            admit_id=admit_id,
            reason="lineage_dead",
            gates=gates,
            action=action,
            sink=sink,
            actor=actor,
            death_certificate=dead.get("death_certificate"),
            public_url=public_url,
            now=now,
        )

    # Civ II — subject sovereignty (first-class, meterable)
    subject_gate = None
    if subject_id:
        subject_gate = subject_mod.require_for_admit(
            subject_id=subject_id,
            action=action,
            sink=sink,
            actor=actor,
            clearance_id=str(body.get("subject_clearance_id") or body.get("clearance_id") or "")
            or None,
            subject_refuse=bool(body.get("subject_refuse") or body.get("subject_denies")),
            public_url=public_url,
        )
        gates.append({"gate": "subject", "result": subject_gate})
        if not subject_gate.get("ok"):
            return _finish(
                "REFUSED",
                admit_id=admit_id,
                reason=str(subject_gate.get("reason") or "subject_refused"),
                gates=gates,
                action=action,
                sink=sink,
                actor=actor,
                subject_id=subject_id,
                subject=subject_gate,
                refusal_digest=(subject_gate.get("refusal") or {}).get("refusal_digest"),
                public_url=public_url,
                now=now,
            )

    # Civ I — Right-to-Act
    require_mandate = body.get("require_mandate")
    if require_mandate is None:
        require_mandate = bool(mandate_id) or bool(sink_req.get("mandate_required"))
    rta_body = {
        "action": action,
        "sink": sink,
        "actor": actor,
        "args": args,
        "resource": candidate.get("resource") or body.get("resource") or "",
        "mandate_id": mandate_id,
        "mandate": mandate_obj,
        "policy": {
            "require_mandate": bool(require_mandate),
            **(body.get("policy") if isinstance(body.get("policy"), dict) else {}),
        },
    }
    rta = rta_mod.evaluate(rta_body, account_id=account_id, public_url=public_url)
    gates.append(
        {
            "gate": "right_to_act",
            "result": {
                "decision": rta.get("decision"),
                "refusal_digest": rta.get("refusal_digest"),
                "ticket_id": rta.get("ticket_id"),
                "evaluation_id": rta.get("evaluation_id"),
            },
        }
    )
    if rta.get("decision") == "HOLD":
        return _finish(
            "HALTED",
            admit_id=admit_id,
            reason="right_to_act_hold",
            gates=gates,
            action=action,
            sink=sink,
            actor=actor,
            right_to_act=rta,
            public_url=public_url,
            now=now,
        )
    if rta.get("decision") != "EXIST":
        return _finish(
            "REFUSED",
            admit_id=admit_id,
            reason="right_to_act_nonexist",
            gates=gates,
            action=action,
            sink=sink,
            actor=actor,
            right_to_act=rta,
            refusal_digest=rta.get("refusal_digest"),
            public_url=public_url,
            now=now,
        )

    # Civ I+III — live reconstruct
    reconstruction = None
    if mandate_id or mandate_obj:
        reconstruction = mandate_mod.reconstruct(
            mandate_id=str(mandate_id) if mandate_id else None,
            mandate=mandate_obj,
            action=action,
            sink=sink,
            amount=amount_f,
            resource=str(candidate.get("resource") or body.get("resource") or ""),
            agent_id=actor or None,
        )
        gates.append(
            {
                "gate": "reconstruct",
                "result": {
                    "outcome": reconstruction.get("outcome"),
                    "reason": reconstruction.get("reason"),
                    "admitted": reconstruction.get("admitted"),
                },
            }
        )
        outcome = reconstruction.get("outcome")
        if outcome == "HALT":
            return _finish(
                "HALTED",
                admit_id=admit_id,
                reason=f"reconstruct_{reconstruction.get('reason') or 'halt'}",
                gates=gates,
                action=action,
                sink=sink,
                actor=actor,
                right_to_act=rta,
                reconstruction=reconstruction,
                public_url=public_url,
                now=now,
            )
        if outcome == "DENY" or not reconstruction.get("admitted"):
            reason = str(reconstruction.get("reason") or "denied")
            if reason == "dead":
                return _finish(
                    "DEAD",
                    admit_id=admit_id,
                    reason="reconstruct_dead",
                    gates=gates,
                    action=action,
                    sink=sink,
                    actor=actor,
                    right_to_act=rta,
                    reconstruction=reconstruction,
                    death_certificate=reconstruction.get("death_certificate"),
                    public_url=public_url,
                    now=now,
                )
            return _finish(
                "REFUSED",
                admit_id=admit_id,
                reason=f"reconstruct_{reason}",
                gates=gates,
                action=action,
                sink=sink,
                actor=actor,
                right_to_act=rta,
                reconstruction=reconstruction,
                public_url=public_url,
                now=now,
            )

    # Civ II — mutual clearance
    counterpart = None
    if counterpart_mandate_id:
        counterpart = mandate_mod.reconstruct(
            mandate_id=counterpart_mandate_id,
            action=action,
            sink=sink,
            amount=amount_f,
            resource=str(candidate.get("resource") or ""),
            agent_id=str(body.get("counterpart_agent_id") or "").strip() or None,
        )
        gates.append(
            {
                "gate": "mutual",
                "result": {
                    "counterpart_mandate_id": counterpart_mandate_id,
                    "outcome": counterpart.get("outcome"),
                    "reason": counterpart.get("reason"),
                },
            }
        )
        if counterpart.get("outcome") == "HALT":
            return _finish(
                "HALTED",
                admit_id=admit_id,
                reason="counterpart_halt",
                gates=gates,
                action=action,
                sink=sink,
                actor=actor,
                right_to_act=rta,
                reconstruction=reconstruction,
                counterpart=counterpart,
                public_url=public_url,
                now=now,
            )
        if counterpart.get("outcome") != "ADMIT" and not counterpart.get("admitted"):
            return _finish(
                "REFUSED",
                admit_id=admit_id,
                reason=f"counterpart_{counterpart.get('reason') or 'denied'}",
                gates=gates,
                action=action,
                sink=sink,
                actor=actor,
                right_to_act=rta,
                reconstruction=reconstruction,
                counterpart=counterpart,
                public_url=public_url,
                now=now,
            )

    # Civ III — mint world-fact
    with _lock:
        _epoch += 1
        epoch = _epoch
        fact_id = f"fact_{uuid.uuid4().hex}"
        fact_body = {
            "spec": SPEC,
            "fact_id": fact_id,
            "admit_id": admit_id,
            "epoch": epoch,
            "outcome": "ADMITTED",
            "action": action,
            "sink": sink,
            "sink_class": sink_req.get("class"),
            "irreversibility": sink_req.get("irreversibility"),
            "actor": actor or None,
            "subject_id": subject_id or None,
            "human_principal_id": human_principal_id or None,
            "human_root_digest": human_root_digest,
            "mandate_id": str(mandate_id) if mandate_id else None,
            "counterpart_mandate_id": counterpart_mandate_id,
            "lineage_id": lineage_id,
            "ticket_id": rta.get("ticket_id"),
            "evaluation_id": rta.get("evaluation_id"),
            "fingerprint": rta.get("fingerprint"),
            "amount": amount_f,
            "admitted_at": _iso(now),
            "admitted_at_unix": int(now),
            "account_id": account_id,
            "title": f"FACT · {action} → {sink}",
            "summary": (
                f"World-write admitted: {actor or 'actor'} / {action} at {sink} "
                f"under living authority (epoch {epoch})."
            ),
            "invariant": (
                "Admittance is the only path from computation to shared reality. "
                "This fact is stranger-searchable finality — not a log line."
            ),
        }
        fact_body["fact_digest"] = hashlib.sha256(
            _canonical({k: v for k, v in fact_body.items() if k != "fact_digest"}).encode()
        ).hexdigest()
        _facts[fact_id] = dict(fact_body)

    _finder_fact(fact_body)
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "ok": True,
        "outcome": "ADMITTED",
        "admit_id": admit_id,
        "reason": None,
        "gates": gates,
        "fact": fact_body,
        "right_to_act": rta,
        "reconstruction": reconstruction,
        "counterpart": counterpart,
        "sink": sink_req,
        "subject": subject_gate,
        "meter": (subject_gate or {}).get("meter"),
        "ticket_id": rta.get("ticket_id"),
        "burn_url": f"{base}/v1/right-to-act/burn" if base else None,
        "fact_url": f"{base}/v1/admittance/fact/{fact_id}" if base else None,
        "well_known_fact": f"{base}/.well-known/facts/{fact_id}.json" if base else None,
        "civilizations_compressed": [
            "I:actor_authority",
            "II:subject_and_sink",
            "III:lineage_and_fact",
        ],
        "invariant": (
            "Computation proposes. Admittance disposes. "
            "Three civilizations. One verb: ADMIT."
        ),
    }


def get_fact(fact_id: str) -> dict | None:
    with _lock:
        row = _facts.get(fact_id)
        return dict(row) if row else None


def list_facts(limit: int = 50) -> list[dict]:
    with _lock:
        rows = sorted(
            _facts.values(),
            key=lambda r: int(r.get("admitted_at_unix") or 0),
            reverse=True,
        )
    return [dict(r) for r in rows[: max(1, min(int(limit), 200))]]


def manifest(public_url: str) -> dict:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Gate Admittance",
        "tagline": "Three civilizations. One verb: ADMIT.",
        "description": (
            "Reality-write clearance. Compresses actor authority, subject/sink law, "
            "and lineage/fact finality into one fail-closed decision. "
            "Industry drafts name shards of this; Admittance is the full stack."
        ),
        "outcomes": list(OUTCOMES),
        "invariant": "Computation proposes. Admittance disposes. Absence is evidence.",
        "civilizations": {
            "I": "Actor authority — Right-to-Act + live mandate reconstruct",
            "II": "Subject + sink — typed irreversibility + target refusal + mutual clearance",
            "III": "Lineage + fact — continuity, mortality, inheritance handle, world-fact receipt",
        },
        "admit": f"{base}/v1/admittance/admit",
        "demo": f"{base}/demo/admittance/admit",
        "fact": f"{base}/v1/admittance/fact/{{fact_id}}",
        "facts_well_known": f"{base}/.well-known/facts/{{fact_id}}.json",
        "page": f"{base}/admittance",
        "well_known": f"{base}/.well-known/admittance.json",
        "related": {
            "finder": f"{base}/.well-known/finder.json",
            "right_to_act": f"{base}/.well-known/right-to-act.json",
            "mandate": f"{base}/.well-known/mandate.json",
            "sinks": f"{base}/.well-known/sinks.json",
            "continuity": f"{base}/.well-known/continuity.json",
            "note": (
                "Finder indexes consequence. Admittance decides consequence. "
                "TCP/IP of irreversible becoming."
            ),
        },
        "rabbit_holes": [
            "object capabilities / attenuation (Miller) — authority narrows, never widens",
            "IETF execution-finality drafts — fail-closed before effectuation",
            "action authorization boundaries — mediate proposals before side effects",
            "law rejects AI personhood — human root must remain reconstructable",
            "A-corp proposals — still identity wrappers; not world-write admittance",
        ],
    }
