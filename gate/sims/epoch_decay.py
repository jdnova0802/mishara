"""S16 Epoch/Decay — LIVE grant ≠ fresh policy epoch at actus time.

Lab only. their_production always False.
CommitGuard pattern: re-check freshness at action time.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from gate.sims.lab_invariant import stamp_lab_flag


SPEC = "nisaba-epoch-decay-lab-v1"
THEIR_PRODUCTION = False


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass
class PolicyEpoch:
    epoch_id: str
    policy_digest: str
    live: bool


@dataclass
class BoundGrant:
    grant_id: str
    epoch_id: str
    policy_digest: str
    action_digest: str


@dataclass
class Store:
    epochs: dict[str, PolicyEpoch] = field(default_factory=dict)
    current_epoch_id: str | None = None
    grants: dict[str, BoundGrant] = field(default_factory=dict)
    receipts: dict[str, dict[str, Any]] = field(default_factory=dict)


STORE = Store()


def reset() -> None:
    STORE.epochs.clear()
    STORE.current_epoch_id = None
    STORE.grants.clear()
    STORE.receipts.clear()


def _receipt(
    decision: str,
    reason_code: str,
    *,
    epoch_id: str | None = None,
    policy_digest: str | None = None,
    grant_id: str | None = None,
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rid = str(uuid.uuid4())
    payload = {
        "spec": SPEC,
        "receipt_id": rid,
        "receipt_class": "epoch",
        "decision": decision,
        "reason_code": reason_code,
        "epoch_id": epoch_id,
        "policy_digest": policy_digest,
        "grant_id": grant_id,
        "result": result,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="epoch_decay"),
        "ts": time.time(),
    }
    payload["receipt_hash"] = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
    STORE.receipts[rid] = payload
    return {**payload, "receipt_url": f"/v1/epoch/receipts/{rid}"}


def rotate_epoch(policy_body: dict[str, Any]) -> dict[str, Any]:
    for e in STORE.epochs.values():
        e.live = False
    eid = str(uuid.uuid4())
    digest = hashlib.sha256(_canonical(policy_body).encode("utf-8")).hexdigest()
    STORE.epochs[eid] = PolicyEpoch(epoch_id=eid, policy_digest=digest, live=True)
    STORE.current_epoch_id = eid
    return {
        "epoch_id": eid,
        "policy_digest": digest,
        "live": True,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="epoch_decay"),
    }


def bind_grant(action_digest: str) -> dict[str, Any]:
    eid = STORE.current_epoch_id
    if eid is None:
        return _receipt("DENY", "no_live_epoch", result={"action_digest": action_digest})
    e = STORE.epochs[eid]
    if not e.live:
        return _receipt("DENY", "epoch_not_live", epoch_id=eid, policy_digest=e.policy_digest)
    gid = str(uuid.uuid4())
    STORE.grants[gid] = BoundGrant(
        grant_id=gid,
        epoch_id=eid,
        policy_digest=e.policy_digest,
        action_digest=action_digest,
    )
    return {
        "grant_id": gid,
        "epoch_id": eid,
        "policy_digest": e.policy_digest,
        "action_digest": action_digest,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="epoch_decay"),
    }


def check_grant(grant_id: str, action_digest: str) -> dict[str, Any]:
    g = STORE.grants.get(grant_id)
    if g is None:
        return _receipt("DENY", "no_grant", grant_id=grant_id)

    if g.action_digest != action_digest:
        return _receipt(
            "DENY",
            "grant_digest_mismatch",
            grant_id=grant_id,
            epoch_id=g.epoch_id,
            policy_digest=g.policy_digest,
        )

    e = STORE.epochs.get(g.epoch_id)
    if e is None or not e.live:
        return _receipt(
            "DENY",
            "epoch_decayed",
            grant_id=grant_id,
            epoch_id=g.epoch_id,
            policy_digest=g.policy_digest,
        )

    if STORE.current_epoch_id != g.epoch_id:
        return _receipt(
            "DENY",
            "epoch_rotated",
            grant_id=grant_id,
            epoch_id=g.epoch_id,
            policy_digest=g.policy_digest,
            result={"current_epoch_id": STORE.current_epoch_id},
        )

    if e.policy_digest != g.policy_digest:
        return _receipt(
            "DENY",
            "policy_digest_mismatch",
            grant_id=grant_id,
            epoch_id=g.epoch_id,
            policy_digest=g.policy_digest,
        )

    return _receipt(
        "ALLOW",
        "epoch_fresh",
        grant_id=grant_id,
        epoch_id=g.epoch_id,
        policy_digest=g.policy_digest,
        result={"action_digest": action_digest},
    )


def get_receipt(receipt_id: str) -> dict[str, Any] | None:
    r = STORE.receipts.get(receipt_id)
    if r is None:
        return None
    return {**r, "receipt_url": f"/v1/epoch/receipts/{receipt_id}"}
