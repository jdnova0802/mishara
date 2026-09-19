"""S10 Preflight Diff — lab intelligence: proposed actus ≠ simulated world-delta.

Lab only. their_production is always False.

NOT S9 Mouth Watch:
  S9  = is this session trustworthy?     → receipt_class threat | watch_clear
  S10 = does actus match simulated delta? → receipt_class preflight

Critical prove: S9 clear + S10 DENY on delta mismatch alone (no shared logic).
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from gate.sims.lab_invariant import stamp_lab_flag


SPEC = "nisaba-preflight-diff-lab-v1"
THEIR_PRODUCTION = False


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass
class Preflight:
    preflight_id: str
    digest: str
    projected_delta: dict[str, Any]
    invariants_ok: bool | None
    hostile: bool
    expires_at: float


@dataclass
class Store:
    preflights: dict[str, Preflight] = field(default_factory=dict)
    receipts: dict[str, dict[str, Any]] = field(default_factory=dict)


STORE = Store()


def reset() -> None:
    STORE.preflights.clear()
    STORE.receipts.clear()


def action_digest(action_type: str, payload: dict[str, Any]) -> str:
    body = {"action_type": action_type, "payload": payload}
    return hashlib.sha256(_canonical(body).encode("utf-8")).hexdigest()


def _receipt(
    decision: str,
    reason_code: str,
    *,
    preflight_id: str | None = None,
    digest: str | None = None,
    action_type: str | None = None,
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rid = str(uuid.uuid4())
    payload = {
        "spec": SPEC,
        "receipt_id": rid,
        "receipt_class": "preflight",
        "threat_class": None,
        "decision": decision,
        "reason_code": reason_code,
        "preflight_id": preflight_id,
        "digest": digest,
        "action_type": action_type,
        "result": result,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="preflight_diff"),
        "ts": time.time(),
    }
    payload["receipt_hash"] = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
    STORE.receipts[rid] = payload
    return {**payload, "receipt_url": f"/v1/preflight/receipts/{rid}"}


def record_preflight(
    action_type: str,
    payload: dict[str, Any],
    *,
    projected_delta: dict[str, Any],
    invariants_ok: bool | None,
    hostile: bool = False,
    ttl_sec: float = 300,
) -> dict[str, Any]:
    digest = action_digest(action_type, payload)
    pid = str(uuid.uuid4())
    STORE.preflights[pid] = Preflight(
        preflight_id=pid,
        digest=digest,
        projected_delta=dict(projected_delta),
        invariants_ok=invariants_ok,
        hostile=hostile,
        expires_at=time.time() + ttl_sec,
    )
    return {
        "preflight_id": pid,
        "digest": digest,
        "expires_at": STORE.preflights[pid].expires_at,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="preflight_diff"),
    }


def check_preflight(
    action_type: str,
    payload: dict[str, Any],
    *,
    preflight_id: str | None = None,
    actual_delta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    digest = action_digest(action_type, payload)

    if not preflight_id:
        return _receipt("DENY", "preflight_missing", digest=digest, action_type=action_type)

    pf = STORE.preflights.get(preflight_id)
    if pf is None:
        return _receipt(
            "DENY",
            "preflight_missing",
            preflight_id=preflight_id,
            digest=digest,
            action_type=action_type,
        )

    if pf.expires_at < time.time():
        return _receipt(
            "DENY",
            "preflight_stale",
            preflight_id=preflight_id,
            digest=digest,
            action_type=action_type,
        )

    if pf.digest != digest:
        return _receipt(
            "DENY",
            "preflight_digest_mismatch",
            preflight_id=preflight_id,
            digest=digest,
            action_type=action_type,
        )

    if pf.hostile:
        return _receipt(
            "DENY",
            "preflight_hostile_delta",
            preflight_id=preflight_id,
            digest=digest,
            action_type=action_type,
            result={"projected_delta": pf.projected_delta},
        )

    if pf.invariants_ok is None:
        return _receipt(
            "DENY",
            "preflight_uncertain",
            preflight_id=preflight_id,
            digest=digest,
            action_type=action_type,
        )

    if pf.invariants_ok is False:
        return _receipt(
            "DENY",
            "preflight_invariants_failed",
            preflight_id=preflight_id,
            digest=digest,
            action_type=action_type,
            result={"projected_delta": pf.projected_delta},
        )

    if actual_delta is not None and actual_delta != pf.projected_delta:
        return _receipt(
            "DENY",
            "preflight_delta_mismatch",
            preflight_id=preflight_id,
            digest=digest,
            action_type=action_type,
            result={
                "projected_delta": pf.projected_delta,
                "actual_delta": actual_delta,
            },
        )

    return _receipt(
        "ALLOW",
        "preflight_clear",
        preflight_id=preflight_id,
        digest=digest,
        action_type=action_type,
        result={"projected_delta": pf.projected_delta, "invariants_ok": True},
    )


def get_receipt(receipt_id: str) -> dict[str, Any] | None:
    r = STORE.receipts.get(receipt_id)
    if r is None:
        return None
    return {**r, "receipt_url": f"/v1/preflight/receipts/{receipt_id}"}
