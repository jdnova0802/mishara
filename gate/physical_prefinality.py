"""Physical Prefinality — park before actuators; society acts after bodies.

Bridgewater's Greg Jensen compared this moment to February 2020 before COVID:
harm arrives before institutions move.

Nisaba's answer is not a whitepaper. It is a fail-closed lane for absolute
physical sinks:

  REVERSIBLE   → proceed under ordinary Right-to-Act
  CONSEQUENTIAL → HOLD / reconstruct, then ask once
  ABSOLUTE PHYSICAL → PARK until living human root + mandate + subject clear

Invariant: Computation may propose motion. Prefinality decides whether atoms move.
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
    from gate import sinks as sinks_mod
except ImportError:
    import sinks as sinks_mod

try:
    from gate import receipt as receipt_mod
except ImportError:
    import receipt as receipt_mod

try:
    from gate import continuity as continuity_mod
except ImportError:
    import continuity as continuity_mod

try:
    from gate import mandate as mandate_mod
except ImportError:
    import mandate as mandate_mod

try:
    from gate import subject as subject_mod
except ImportError:
    import subject as subject_mod

SPEC = "gate-physical-prefinality-v1"
OUTCOMES = ("CLEARED", "PARKED", "REFUSED", "DEAD")

_lock = threading.Lock()
_parks: dict[str, dict[str, Any]] = {}


def _iso(ts: float | None = None) -> str:
    dt = datetime.fromtimestamp(ts or time.time(), tz=timezone.utc)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _reset_for_tests() -> None:
    with _lock:
        _parks.clear()


def _sign(digest_hex: str) -> str | None:
    try:
        return receipt_mod.sign_receipt_hash(digest_hex)
    except Exception:
        return None


def is_absolute_physical(sink_id: str) -> dict:
    row = sinks_mod.require_for_act(sink_id)
    absolute = bool(
        row.get("known")
        and row.get("class") == "physical"
        and row.get("irreversibility") == "absolute"
    )
    return {
        "absolute_physical": absolute,
        "sink": row,
        "lane": "IRREVERSIBLE" if absolute else "OTHER",
    }


def evaluate(
    body: dict | None = None,
    *,
    public_url: str = "",
) -> dict:
    """Prefinality check for physical world-writes.

    PARKED means: do not actuate. Institutions move after harm; this parks before.
    """
    body = body if isinstance(body, dict) else {}
    action = str(body.get("action") or "").strip()
    sink = str(body.get("sink") or body.get("sink_id") or "").strip()
    actor = str(body.get("actor") or body.get("agent_id") or "").strip()
    human_principal_id = str(
        body.get("human_principal_id") or body.get("principal_id") or ""
    ).strip()
    human_root_digest = str(body.get("human_root_digest") or "").strip() or None
    mandate_id = body.get("mandate_id")
    subject_id = str(
        body.get("subject_id")
        or body.get("subject_principal_id")
        or body.get("at_risk_subject_id")
        or ""
    ).strip()
    clearance_id = str(body.get("subject_clearance_id") or body.get("clearance_id") or "").strip() or None

    now = time.time()
    park_id = f"park_{uuid.uuid4().hex}"
    gates: list[dict[str, Any]] = []

    lane = is_absolute_physical(sink)
    gates.append({"gate": "physical_lane", "result": lane})
    if not sink:
        return _out(
            "PARKED",
            park_id=park_id,
            reason="sink_required",
            gates=gates,
            action=action,
            sink=sink,
            actor=actor,
            public_url=public_url,
            now=now,
        )
    if not lane["absolute_physical"]:
        return {
            "spec": SPEC,
            "ok": True,
            "outcome": "CLEARED",
            "reason": "not_absolute_physical",
            "park_id": None,
            "gates": gates,
            "lane": "OTHER",
            "action": action,
            "sink": sink,
            "actor": actor or None,
            "note": "Non-absolute sinks use ordinary Admittance / Right-to-Act.",
            "invariant": "Physical Prefinality only seizes absolute physical lanes.",
        }

    # Absolute physical: living human root required
    if not human_principal_id and not human_root_digest:
        return _park(
            park_id=park_id,
            reason="human_root_required",
            gates=gates,
            action=action,
            sink=sink,
            actor=actor,
            public_url=public_url,
            now=now,
            detail="Absolute physical writes need a living human root — not an orphan agent.",
        )

    if human_principal_id:
        cont = continuity_mod.is_non_authorizing(human_principal_id)
        gates.append({"gate": "continuity", "result": cont})
        if cont.get("non_authorizing"):
            return _out(
                "DEAD",
                park_id=park_id,
                reason="human_root_non_authorizing",
                gates=gates,
                action=action,
                sink=sink,
                actor=actor,
                public_url=public_url,
                now=now,
            )

    dead = mandate_mod.is_dead(
        mandate_id=str(mandate_id) if mandate_id else None,
        human_root_digest=human_root_digest,
        agent_id=actor or None,
    )
    gates.append({"gate": "mortality", "result": {"dead": dead.get("dead"), "death_id": dead.get("death_id")}})
    if dead.get("dead"):
        return _out(
            "DEAD",
            park_id=park_id,
            reason="lineage_dead",
            gates=gates,
            action=action,
            sink=sink,
            actor=actor,
            death_certificate=dead.get("death_certificate"),
            public_url=public_url,
            now=now,
        )

    if not mandate_id:
        return _park(
            park_id=park_id,
            reason="mandate_required",
            gates=gates,
            action=action,
            sink=sink,
            actor=actor,
            public_url=public_url,
            now=now,
            detail="Absolute physical effectuation requires a living mandate at burn time.",
        )

    # Subject at risk near actuators — fail closed without clearance
    if not subject_id:
        return _park(
            park_id=park_id,
            reason="at_risk_subject_required",
            gates=gates,
            action=action,
            sink=sink,
            actor=actor,
            public_url=public_url,
            now=now,
            detail="Name who/what may be harmed. Absolute physical has a subject.",
        )

    sub = subject_mod.require_for_admit(
        subject_id=subject_id,
        action=action or "device.actuate",
        sink=sink,
        actor=actor,
        clearance_id=clearance_id,
        subject_refuse=bool(body.get("subject_refuse")),
        public_url=public_url,
        consume=False,
    )
    gates.append({"gate": "subject", "result": sub})
    if not sub.get("ok"):
        outcome = "REFUSED" if sub.get("reason") == "subject_refused" else "PARKED"
        return _out(
            outcome,
            park_id=park_id,
            reason=str(sub.get("reason") or "subject_blocked"),
            gates=gates,
            action=action,
            sink=sink,
            actor=actor,
            subject=sub,
            public_url=public_url,
            now=now,
        )

    # Reconstruct mandate live
    try:
        amount = body.get("amount")
        amount_f = float(amount) if amount is not None else None
    except (TypeError, ValueError):
        amount_f = None
    reconstruction = mandate_mod.reconstruct(
        mandate_id=str(mandate_id),
        action=action or "device.actuate",
        sink=sink,
        amount=amount_f,
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
    if reconstruction.get("outcome") == "HALT":
        return _park(
            park_id=park_id,
            reason="reconstruct_halt",
            gates=gates,
            action=action,
            sink=sink,
            actor=actor,
            reconstruction=reconstruction,
            public_url=public_url,
            now=now,
        )
    if reconstruction.get("outcome") != "ADMIT" and not reconstruction.get("admitted"):
        reason = str(reconstruction.get("reason") or "denied")
        if reason == "dead":
            return _out(
                "DEAD",
                park_id=park_id,
                reason="reconstruct_dead",
                gates=gates,
                action=action,
                sink=sink,
                actor=actor,
                reconstruction=reconstruction,
                public_url=public_url,
                now=now,
            )
        return _park(
            park_id=park_id,
            reason=f"reconstruct_{reason}",
            gates=gates,
            action=action,
            sink=sink,
            actor=actor,
            reconstruction=reconstruction,
            public_url=public_url,
            now=now,
        )

    return {
        "spec": SPEC,
        "ok": True,
        "outcome": "CLEARED",
        "reason": None,
        "park_id": None,
        "gates": gates,
        "lane": "IRREVERSIBLE",
        "action": action,
        "sink": sink,
        "actor": actor or None,
        "subject_id": subject_id,
        "mandate_id": str(mandate_id),
        "reconstruction": reconstruction,
        "subject": sub,
        "invariant": (
            "Absolute physical cleared only under living human root, "
            "live mandate, and subject clearance. Otherwise: PARK."
        ),
        "feb2020": (
            "Institutions moved after bodies. Prefinality parks before actuators."
        ),
    }


def get_park(park_id: str) -> dict | None:
    with _lock:
        row = _parks.get(park_id)
        return dict(row) if row else None


def list_parks(limit: int = 50) -> list[dict]:
    with _lock:
        rows = sorted(
            _parks.values(),
            key=lambda r: int(r.get("parked_at_unix") or 0),
            reverse=True,
        )
    return [dict(r) for r in rows[: max(1, min(int(limit), 200))]]


def _park(**kwargs: Any) -> dict:
    return _out("PARKED", **kwargs)


def _out(
    outcome: str,
    *,
    park_id: str,
    reason: str,
    gates: list,
    action: str,
    sink: str,
    actor: str,
    public_url: str,
    now: float,
    detail: str | None = None,
    **extra: Any,
) -> dict:
    base = (public_url or "").rstrip("/")
    body = {
        "spec": SPEC,
        "kind": "park" if outcome == "PARKED" else outcome.lower(),
        "park_id": park_id,
        "outcome": outcome,
        "reason": reason,
        "detail": detail,
        "action": action or None,
        "sink": sink or None,
        "actor": actor or None,
        "parked_at": _iso(now),
        "parked_at_unix": int(now),
        "feb2020": (
            "Warning class: harm can arrive before society acts. "
            "This ticket parks absolute physical effectuation until living authority clears."
        ),
        "invariant": "Atoms do not move on a PARKED ticket.",
    }
    digest = hashlib.sha256(_canonical(body).encode()).hexdigest()
    body["park_digest"] = digest
    sig = _sign(digest)
    if receipt_mod.signing_required() and not sig and outcome == "PARKED":
        # Still return park decision; mark unsigned.
        body["signature"] = None
        body["unsigned"] = True
    else:
        body["signature"] = sig

    if outcome == "PARKED":
        with _lock:
            _parks[park_id] = dict(body)

    out = {
        "spec": SPEC,
        "ok": outcome == "CLEARED",
        "outcome": outcome,
        "reason": reason,
        "detail": detail,
        "park_id": park_id if outcome == "PARKED" else None,
        "park": body if outcome == "PARKED" else None,
        "gates": gates,
        "lane": "IRREVERSIBLE",
        "action": action or None,
        "sink": sink or None,
        "actor": actor or None,
        "park_url": f"{base}/v1/physical/park/{park_id}" if base and outcome == "PARKED" else None,
        "well_known_park": (
            f"{base}/.well-known/physical-parks/{park_id}.json"
            if base and outcome == "PARKED"
            else None
        ),
        "feb2020": body["feb2020"],
        "invariant": (
            "Society acts after harm. Physical Prefinality parks before actuators."
        ),
    }
    out.update(extra)
    return out


def manifest(public_url: str) -> dict:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Nisaba Physical Prefinality",
        "tagline": "Park before actuators. Society acts after bodies.",
        "description": (
            "Fail-closed lane for absolute physical sinks — robots, vehicles, "
            "grid switches, industrial controls, medical actuators. "
            "Maps the irreversible lane: without living human root + mandate + "
            "subject clearance, effectuation stays PARKED."
        ),
        "why_now": (
            "Capital allocators are already warning that AI may cause bodily harm "
            "before institutions catch up — a February 2020 rhyme. "
            "Prefinality is the protocol hedge: park kinetic writes until authority reconstructs."
        ),
        "outcomes": list(OUTCOMES),
        "lanes": {
            "REVERSIBLE": "Ordinary Right-to-Act",
            "CONSEQUENTIAL": "HOLD / reconstruct, then human once",
            "IRREVERSIBLE_PHYSICAL": "PARK until root + mandate + subject clear",
        },
        "evaluate": f"{base}/v1/physical/evaluate",
        "demo": f"{base}/demo/physical/evaluate",
        "park": f"{base}/v1/physical/park/{{park_id}}",
        "page": f"{base}/physical",
        "well_known": f"{base}/.well-known/physical-prefinality.json",
        "related": {
            "admittance": f"{base}/.well-known/admittance.json",
            "sinks": f"{base}/.well-known/sinks.json",
            "subject": f"{base}/.well-known/subject.json",
            "mandate": f"{base}/.well-known/mandate.json",
            "note": (
                "Admittance disposes world-writes. Physical Prefinality seizes "
                "the absolute physical lane before atoms move."
            ),
        },
        "operator": "Nisaba LLC",
        "invariant": "Computation proposes motion. Prefinality decides whether atoms move.",
    }
