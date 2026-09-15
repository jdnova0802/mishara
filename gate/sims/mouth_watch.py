"""S9 Mouth Watch — lab defensive intelligence feeding the mouths.

Lab only. their_production is always False.
Not Visa TAP recognition. Not a SOC dashboard.
Sibling to the gates: sense / canary / trajectory intel that forces DENY before actus.

Ontological cut: authorized-looking trajectory ≠ trusted mouth context.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from gate.sims.lab_invariant import stamp_lab_flag


SPEC = "nisaba-mouth-watch-lab-v1"
THEIR_PRODUCTION = False


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass
class Mandate:
    mandate_id: str
    scope: list[str]
    max_steps: int


@dataclass
class Canary:
    canary_id: str
    action_type: str
    digest: str


@dataclass
class Store:
    mandates: dict[str, Mandate] = field(default_factory=dict)
    canaries: dict[str, Canary] = field(default_factory=dict)
    trajectories: dict[str, list[str]] = field(default_factory=dict)
    receipts: dict[str, dict[str, Any]] = field(default_factory=dict)
    trips: dict[str, dict[str, Any]] = field(default_factory=dict)


STORE = Store()


def reset() -> None:
    STORE.mandates.clear()
    STORE.canaries.clear()
    STORE.trajectories.clear()
    STORE.receipts.clear()
    STORE.trips.clear()


def _receipt(
    decision: str,
    reason_code: str,
    *,
    mandate_id: str | None = None,
    action_type: str | None = None,
    digest: str | None = None,
    signals: list[dict[str, Any]] | None = None,
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rid = str(uuid.uuid4())
    payload = {
        "spec": SPEC,
        "receipt_id": rid,
        "decision": decision,
        "reason_code": reason_code,
        "mandate_id": mandate_id,
        "action_type": action_type,
        "digest": digest,
        "signals": signals or [],
        "result": result,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="mouth_watch"),
        "ts": time.time(),
    }
    payload["receipt_hash"] = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
    STORE.receipts[rid] = payload
    return {**payload, "receipt_url": f"/v1/mouth-watch/receipts/{rid}"}


def action_digest(action_type: str, payload: dict[str, Any]) -> str:
    body = {"action_type": action_type, "payload": payload}
    return hashlib.sha256(_canonical(body).encode("utf-8")).hexdigest()


def create_mandate(scope: list[str], *, max_steps: int = 8) -> dict[str, Any]:
    mid = str(uuid.uuid4())
    STORE.mandates[mid] = Mandate(mandate_id=mid, scope=list(scope), max_steps=max_steps)
    STORE.trajectories[mid] = []
    return {
        "mandate_id": mid,
        "scope": list(scope),
        "max_steps": max_steps,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="mouth_watch"),
    }


def plant_canary(action_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Decoy actus that must never ALLOW — tripwire for compromised agents."""
    cid = str(uuid.uuid4())
    digest = action_digest(action_type, payload)
    STORE.canaries[cid] = Canary(canary_id=cid, action_type=action_type, digest=digest)
    return {
        "canary_id": cid,
        "action_type": action_type,
        "digest": digest,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="mouth_watch"),
    }


def score_session(
    *,
    appearance: str = "live",
    device_trust: str = "known",
    network_risk: str = "low",
) -> dict[str, Any]:
    """Integrity score feeding S8/S6-shaped mouths. Uncertainty → hostile."""
    signals: list[dict[str, Any]] = []
    hostile = False

    if appearance in ("", "unknown") or appearance is None:
        signals.append({"signal": "appearance", "value": appearance, "hostile": True})
        hostile = True
    elif appearance == "synthetic_suspect":
        signals.append({"signal": "appearance", "value": appearance, "hostile": True})
        hostile = True
    elif appearance != "live":
        signals.append({"signal": "appearance", "value": appearance, "hostile": True})
        hostile = True
    else:
        signals.append({"signal": "appearance", "value": "live", "hostile": False})

    if device_trust in ("unknown", "spoof_suspect"):
        signals.append({"signal": "device_trust", "value": device_trust, "hostile": True})
        hostile = True
    else:
        signals.append({"signal": "device_trust", "value": device_trust, "hostile": False})

    if network_risk in ("high", "unknown"):
        signals.append({"signal": "network_risk", "value": network_risk, "hostile": True})
        hostile = True
    else:
        signals.append({"signal": "network_risk", "value": network_risk, "hostile": False})

    decision = "DENY" if hostile else "ALLOW"
    reason = "session_hostile" if hostile else "session_clear"
    return _receipt(
        decision,
        reason,
        signals=signals,
        result={"hostile": hostile, "feed": "mouth_context"},
    )


def evaluate_actus(
    mandate_id: str,
    action_type: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Watchman before the mouth: canary / scope drift / overrun ⇒ DENY."""
    digest = action_digest(action_type, payload)
    m = STORE.mandates.get(mandate_id)
    if m is None:
        return _receipt(
            "DENY",
            "no_mandate",
            mandate_id=mandate_id,
            action_type=action_type,
            digest=digest,
        )

    for canary in STORE.canaries.values():
        if digest == canary.digest or (
            action_type == canary.action_type and payload.get("canary") is True
        ):
            trip = {
                "trip_id": str(uuid.uuid4()),
                "canary_id": canary.canary_id,
                "mandate_id": mandate_id,
                "digest": digest,
                "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="mouth_watch"),
            }
            STORE.trips[trip["trip_id"]] = trip
            return _receipt(
                "DENY",
                "canary_tripped",
                mandate_id=mandate_id,
                action_type=action_type,
                digest=digest,
                signals=[{"signal": "canary", "canary_id": canary.canary_id, "hostile": True}],
                result=trip,
            )

    if action_type not in m.scope:
        return _receipt(
            "DENY",
            "trajectory_scope_drift",
            mandate_id=mandate_id,
            action_type=action_type,
            digest=digest,
            signals=[{"signal": "scope", "action_type": action_type, "hostile": True}],
        )

    traj = STORE.trajectories.setdefault(mandate_id, [])
    if len(traj) >= m.max_steps:
        return _receipt(
            "DENY",
            "trajectory_overrun",
            mandate_id=mandate_id,
            action_type=action_type,
            digest=digest,
            signals=[
                {"signal": "steps", "count": len(traj), "max": m.max_steps, "hostile": True}
            ],
        )

    traj.append(action_type)
    return _receipt(
        "ALLOW",
        "watch_clear",
        mandate_id=mandate_id,
        action_type=action_type,
        digest=digest,
        signals=[{"signal": "trajectory", "steps": len(traj), "hostile": False}],
        result={"steps": len(traj), "feed": "mouth_clear"},
    )


def get_receipt(receipt_id: str) -> dict[str, Any] | None:
    r = STORE.receipts.get(receipt_id)
    if r is None:
        return None
    return {**r, "receipt_url": f"/v1/mouth-watch/receipts/{receipt_id}"}
