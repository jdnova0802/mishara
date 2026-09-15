"""S1 Actus Fence — lab mouth: logos-before-actus for agent tools/pay.

Lab only. their_production is always False.
Not Fidacy/Visa — those exist. This proves digest-bound DENY + stranger receipt.
"""

from __future__ import annotations

import hashlib
import json
import secrets
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from gate.sims.lab_invariant import stamp_lab_flag


SPEC = "nisaba-actus-fence-lab-v1"
THEIR_PRODUCTION = False


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def action_digest(action_type: str, payload: dict[str, Any]) -> str:
    body = {"action_type": action_type, "payload": payload}
    return hashlib.sha256(_canonical(body).encode("utf-8")).hexdigest()


@dataclass
class Mandate:
    mandate_id: str
    scope: list[str]
    max_amount_cents: int | None
    payee_allowlist: list[str]
    expires_at: float
    revoked: bool = False


@dataclass
class Grant:
    grant_id: str
    mandate_id: str
    digest: str
    expires_at: float


@dataclass
class Store:
    mandates: dict[str, Mandate] = field(default_factory=dict)
    grants: dict[str, Grant] = field(default_factory=dict)
    receipts: dict[str, dict[str, Any]] = field(default_factory=dict)


STORE = Store()


def reset() -> None:
    STORE.mandates.clear()
    STORE.grants.clear()
    STORE.receipts.clear()


def _receipt(
    decision: str,
    reason_code: str,
    *,
    mandate_id: str | None = None,
    grant_id: str | None = None,
    digest: str | None = None,
    action_type: str | None = None,
    result: dict[str, Any] | None = None,
    watch_block: bool = False,
    threat_receipt_id: str | None = None,
    threat_class: str | None = None,
) -> dict[str, Any]:
    rid = str(uuid.uuid4())
    payload = {
        "spec": SPEC,
        "receipt_id": rid,
        # Clearance object — never "threat". Banks branch on receipt_class.
        "receipt_class": "clearance",
        "decision": decision,
        "reason_code": reason_code,
        "mandate_id": mandate_id,
        "grant_id": grant_id,
        "digest": digest,
        "action_type": action_type,
        "result": result,
        "watch_block": watch_block,
        "threat_receipt_id": threat_receipt_id,
        "threat_class": threat_class,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="actus_fence"),
        "ts": time.time(),
    }
    payload["receipt_hash"] = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
    STORE.receipts[rid] = payload
    return {
        **payload,
        "receipt_url": f"/v1/actus/receipts/{rid}",
    }


def create_mandate(
    scope: list[str],
    *,
    max_amount_cents: int | None = None,
    payee_allowlist: list[str] | None = None,
    ttl_sec: float = 3600,
) -> dict[str, Any]:
    mid = str(uuid.uuid4())
    m = Mandate(
        mandate_id=mid,
        scope=list(scope),
        max_amount_cents=max_amount_cents,
        payee_allowlist=list(payee_allowlist or []),
        expires_at=time.time() + ttl_sec,
    )
    STORE.mandates[mid] = m
    return {
        "mandate_id": mid,
        "scope": m.scope,
        "max_amount_cents": m.max_amount_cents,
        "payee_allowlist": m.payee_allowlist,
        "expires_at": m.expires_at,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="actus_fence"),
    }


def create_grant(mandate_id: str, digest: str, *, ttl_sec: float = 300) -> dict[str, Any]:
    m = STORE.mandates.get(mandate_id)
    if m is None:
        return _receipt("DENY", "no_mandate", mandate_id=mandate_id, digest=digest)
    if m.revoked or m.expires_at < time.time():
        return _receipt("DENY", "mandate_not_live", mandate_id=mandate_id, digest=digest)
    if not digest or len(digest) != 64:
        return _receipt("DENY", "malformed_digest", mandate_id=mandate_id, digest=digest)
    gid = secrets.token_urlsafe(16)
    g = Grant(
        grant_id=gid,
        mandate_id=mandate_id,
        digest=digest,
        expires_at=time.time() + ttl_sec,
    )
    STORE.grants[gid] = g
    return {
        "grant_id": gid,
        "mandate_id": mandate_id,
        "digest": digest,
        "expires_at": g.expires_at,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="actus_fence"),
    }


def revoke_mandate(mandate_id: str) -> dict[str, Any]:
    m = STORE.mandates.get(mandate_id)
    if m is None:
        return {
            "ok": False,
            "reason_code": "no_mandate",
            "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="actus_fence"),
        }
    m.revoked = True
    return {
        "ok": True,
        "mandate_id": mandate_id,
        "revoked": True,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="actus_fence"),
    }


def execute(
    action_type: str,
    payload: dict[str, Any],
    *,
    mandate_id: str | None = None,
    grant_id: str | None = None,
    watch_session: dict[str, str] | None = None,
    watch_mandate_id: str | None = None,
) -> dict[str, Any]:
    """Execute actus behind optional S9 Mouth Watch.

    watch_session: appearance/device_trust/network_risk for score_session
    watch_mandate_id: S9 mandate used for canary/trajectory evaluate_actus

    On watch DENY: emits clearance DENY (receipt_class=clearance) that *links*
    to a separate threat receipt (receipt_class=threat). No session lockout.
    """
    from gate.sims import mouth_watch as mw

    if not action_type or not isinstance(payload, dict):
        return _receipt("DENY", "malformed", action_type=action_type)

    digest = action_digest(action_type, payload)

    # --- S9 watchman (before clearance checks) ---
    if watch_session is not None:
        scored = mw.score_session(
            appearance=watch_session.get("appearance", "live"),
            device_trust=watch_session.get("device_trust", "known"),
            network_risk=watch_session.get("network_risk", "low"),
        )
        if scored["decision"] == "DENY":
            return _receipt(
                "DENY",
                "watch_blocked",
                mandate_id=mandate_id,
                digest=digest,
                action_type=action_type,
                watch_block=True,
                threat_receipt_id=scored["receipt_id"],
                threat_class=scored.get("threat_class"),
                result={
                    "watch_block": True,
                    "threat_receipt_id": scored["receipt_id"],
                    "threat_receipt_url": scored.get("receipt_url"),
                    "threat_class": scored.get("threat_class"),
                    "effect": scored.get("effect"),
                },
            )

    if watch_mandate_id is not None:
        watched = mw.evaluate_actus(watch_mandate_id, action_type, payload)
        if watched["decision"] == "DENY":
            return _receipt(
                "DENY",
                "watch_blocked",
                mandate_id=mandate_id,
                digest=digest,
                action_type=action_type,
                watch_block=True,
                threat_receipt_id=watched["receipt_id"],
                threat_class=watched.get("threat_class"),
                result={
                    "watch_block": True,
                    "threat_receipt_id": watched["receipt_id"],
                    "threat_receipt_url": watched.get("receipt_url"),
                    "threat_class": watched.get("threat_class"),
                    "effect": watched.get("effect"),
                },
            )

    if not mandate_id:
        return _receipt("DENY", "no_mandate", digest=digest, action_type=action_type)

    m = STORE.mandates.get(mandate_id)
    if m is None:
        return _receipt("DENY", "no_mandate", mandate_id=mandate_id, digest=digest, action_type=action_type)
    if m.revoked or m.expires_at < time.time():
        return _receipt(
            "DENY",
            "mandate_not_live",
            mandate_id=mandate_id,
            digest=digest,
            action_type=action_type,
        )
    if action_type not in m.scope:
        return _receipt(
            "DENY",
            "scope_mismatch",
            mandate_id=mandate_id,
            digest=digest,
            action_type=action_type,
        )

    if action_type == "pay":
        payee = str(payload.get("payee") or "")
        amount = payload.get("amount_cents")
        if m.payee_allowlist and payee not in m.payee_allowlist:
            return _receipt(
                "DENY",
                "payee_not_allowlisted",
                mandate_id=mandate_id,
                digest=digest,
                action_type=action_type,
            )
        if m.max_amount_cents is not None:
            try:
                cents = int(amount)
            except (TypeError, ValueError):
                return _receipt(
                    "DENY",
                    "malformed_amount",
                    mandate_id=mandate_id,
                    digest=digest,
                    action_type=action_type,
                )
            if cents > m.max_amount_cents:
                return _receipt(
                    "DENY",
                    "over_cap",
                    mandate_id=mandate_id,
                    digest=digest,
                    action_type=action_type,
                )

    if not grant_id:
        return _receipt(
            "DENY",
            "no_grant",
            mandate_id=mandate_id,
            digest=digest,
            action_type=action_type,
        )

    g = STORE.grants.get(grant_id)
    if g is None:
        return _receipt(
            "DENY",
            "no_grant",
            mandate_id=mandate_id,
            grant_id=grant_id,
            digest=digest,
            action_type=action_type,
        )
    if g.mandate_id != mandate_id:
        return _receipt(
            "DENY",
            "grant_mandate_mismatch",
            mandate_id=mandate_id,
            grant_id=grant_id,
            digest=digest,
            action_type=action_type,
        )
    if g.expires_at < time.time():
        return _receipt(
            "DENY",
            "grant_expired",
            mandate_id=mandate_id,
            grant_id=grant_id,
            digest=digest,
            action_type=action_type,
        )
    if g.digest != digest:
        return _receipt(
            "DENY",
            "digest_mismatch",
            mandate_id=mandate_id,
            grant_id=grant_id,
            digest=digest,
            action_type=action_type,
        )

    result = {
        "executed": True,
        "action_type": action_type,
        "digest": digest,
        "sim_result_id": str(uuid.uuid4()),
    }
    return _receipt(
        "ALLOW",
        "ok",
        mandate_id=mandate_id,
        grant_id=grant_id,
        digest=digest,
        action_type=action_type,
        result=result,
    )


def get_receipt(receipt_id: str) -> dict[str, Any] | None:
    r = STORE.receipts.get(receipt_id)
    if r is None:
        return None
    return {**r, "receipt_url": f"/v1/actus/receipts/{receipt_id}"}
