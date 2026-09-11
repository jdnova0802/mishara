"""Mandate — living authority that must reconstruct at consequence time.

S-tier above Right-to-Act:
  Right-to-Act asks: may this act EXIST?
  Mandate asks: whose living authority still reconstructs NOW?

Invariant: Prior approval is not current authority.
A(t) = F(state_now). If reconstruct fails → HALT (never guess).

Root mandates bind a human principal digest. Children may only attenuate
(narrow). Revocation cascades. Burn-time re-prove is mandatory when a
mandate is attached to an EXIST ticket.
"""
from __future__ import annotations

import base64
import hashlib
import json
import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Any

try:
    from gate import receipt as receipt_mod
except ImportError:
    import receipt as receipt_mod

SPEC = "gate-mandate-v1"
RECONSTRUCT_OUTCOMES = ("ADMIT", "DENY", "HALT")

_lock = threading.Lock()
_mandates: dict[str, dict[str, Any]] = {}
_revoked: set[str] = set()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(ts: float | None = None) -> str:
    if ts is None:
        dt = _utc_now()
    else:
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _signing_key():
    return receipt_mod._ed25519_signing_key()


def _public_key_bytes() -> bytes | None:
    return receipt_mod._ed25519_public_key_bytes()


def signing_required() -> bool:
    return receipt_mod.signing_required()


def key_id() -> str | None:
    fp = receipt_mod.receipt_public_key_fingerprint()
    return f"gate-mandate-{fp}" if fp else None


def human_root_digest(*, principal_id: str, approval_bytes: str | bytes | None = None) -> str:
    pid = (principal_id or "").strip()
    if not pid:
        raise ValueError("human_principal_id_required")
    material = approval_bytes if approval_bytes is not None else pid
    if isinstance(material, str):
        material = material.encode("utf-8")
    body = b"gate-human-root-v1|" + pid.encode("utf-8") + b"|" + material
    return hashlib.sha256(body).hexdigest()


def _sign_body(body: dict) -> str | None:
    key = _signing_key()
    if not key:
        return None
    return _b64url(key.sign(_canonical_json(body).encode("utf-8")))


def _verify_sig(body: dict, signature: str | None) -> bool:
    if not signature:
        return not signing_required()
    pub = _public_key_bytes()
    if not pub:
        return False
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        unsigned = {k: v for k, v in body.items() if k != "signature"}
        pad = "=" * (-len(signature) % 4)
        Ed25519PublicKey.from_public_bytes(pub).verify(
            base64.urlsafe_b64decode(signature + pad),
            _canonical_json(unsigned).encode("utf-8"),
        )
        return True
    except Exception:
        return False


def _normalize_scope(scope: dict | None) -> dict:
    s = scope if isinstance(scope, dict) else {}
    actions = s.get("actions") or s.get("allowed_actions") or []
    sinks = s.get("sinks") or s.get("allowed_sinks") or []
    out: dict[str, Any] = {
        "actions": sorted({str(a).strip() for a in actions if str(a).strip()}),
        "sinks": sorted({str(x).strip() for x in sinks if str(x).strip()}),
    }
    if s.get("max_amount") is not None:
        out["max_amount"] = float(s["max_amount"])
    if s.get("resource_prefix"):
        out["resource_prefix"] = str(s["resource_prefix"]).strip()
    return out


def _scope_allows(
    scope: dict,
    *,
    action: str,
    sink: str,
    amount: float | None,
    resource: str,
) -> tuple[bool, str | None]:
    actions = scope.get("actions") or []
    sinks = scope.get("sinks") or []
    if actions and action not in actions:
        return False, "action_outside_mandate"
    if sinks and sink not in sinks:
        return False, "sink_outside_mandate"
    if scope.get("max_amount") is not None and amount is not None:
        if amount > float(scope["max_amount"]):
            return False, "amount_outside_mandate"
    prefix = scope.get("resource_prefix")
    if prefix and resource and not str(resource).startswith(prefix):
        return False, "resource_outside_mandate"
    return True, None


def _is_narrower(child: dict, parent: dict) -> bool:
    p_actions = set(parent.get("actions") or [])
    c_actions = set(child.get("actions") or [])
    if p_actions and not c_actions.issubset(p_actions):
        return False

    p_sinks = set(parent.get("sinks") or [])
    c_sinks = set(child.get("sinks") or [])
    if p_sinks and not c_sinks.issubset(p_sinks):
        return False

    if parent.get("max_amount") is not None and child.get("max_amount") is not None:
        if float(child["max_amount"]) > float(parent["max_amount"]):
            return False
    if parent.get("max_amount") is not None and child.get("max_amount") is None:
        return False

    p_prefix = parent.get("resource_prefix") or ""
    c_prefix = child.get("resource_prefix") or ""
    if p_prefix and c_prefix and not c_prefix.startswith(p_prefix):
        return False
    if p_prefix and not c_prefix:
        return False
    return True


def _lineage_revoked(mandate_id: str) -> bool:
    with _lock:
        cur = mandate_id
        seen: set[str] = set()
        while cur and cur not in seen:
            if cur in _revoked:
                return True
            seen.add(cur)
            row = _mandates.get(cur)
            if not row:
                return True
            cur = row.get("parent_id")
        return False


def issue_root(
    *,
    human_principal_id: str,
    agent_id: str,
    scope: dict | None = None,
    ttl_seconds: int = 86400,
    approval_bytes: str | bytes | None = None,
    public_url: str = "",
) -> dict:
    try:
        root = human_root_digest(
            principal_id=human_principal_id, approval_bytes=approval_bytes
        )
    except ValueError as exc:
        return {"ok": False, "reason": str(exc), "mandate": None}

    agent = (agent_id or "").strip()
    if not agent:
        return {"ok": False, "reason": "agent_id_required", "mandate": None}

    now = time.time()
    ttl = max(60, min(int(ttl_seconds), 30 * 86400))
    mid = f"man_{uuid.uuid4().hex}"
    body = {
        "spec": SPEC,
        "mandate_id": mid,
        "parent_id": None,
        "depth": 0,
        "human_principal_id": human_principal_id.strip(),
        "human_root_digest": root,
        "agent_id": agent,
        "scope": _normalize_scope(scope),
        "status": "active",
        "issued_at": _iso(),
        "expires_at": _iso(now + ttl),
        "expires_at_unix": int(now + ttl),
        "kid": key_id(),
    }
    sig = _sign_body(body)
    if signing_required() and not sig:
        return {"ok": False, "reason": "unsigned_halt", "mandate": None}
    body["signature"] = sig

    with _lock:
        _mandates[mid] = dict(body)

    base = (public_url or "").rstrip("/")
    return {
        "ok": True,
        "reason": None,
        "mandate": body,
        "reconstruct_url": f"{base}/v1/mandate/reconstruct" if base else None,
        "invariant": "Prior approval is not current authority.",
    }


def attenuate(
    *,
    parent_id: str,
    agent_id: str | None = None,
    scope: dict | None = None,
    ttl_seconds: int | None = None,
    public_url: str = "",
) -> dict:
    with _lock:
        parent = dict(_mandates[parent_id]) if parent_id in _mandates else None
    if not parent:
        return {"ok": False, "reason": "unknown_parent", "mandate": None}
    if parent.get("status") != "active" or parent_id in _revoked or _lineage_revoked(parent_id):
        return {"ok": False, "reason": "parent_not_active", "mandate": None}
    if time.time() > float(parent.get("expires_at_unix") or 0):
        return {"ok": False, "reason": "parent_expired", "mandate": None}
    if not _verify_sig(parent, parent.get("signature")):
        return {"ok": False, "reason": "parent_bad_signature", "mandate": None}

    child_scope = _normalize_scope(scope if scope is not None else parent.get("scope"))
    if not _is_narrower(child_scope, parent.get("scope") or {}):
        return {"ok": False, "reason": "widening_forbidden", "mandate": None}

    now = time.time()
    parent_exp = float(parent.get("expires_at_unix") or now)
    exp = parent_exp if ttl_seconds is None else min(parent_exp, now + max(60, int(ttl_seconds)))

    mid = f"man_{uuid.uuid4().hex}"
    body = {
        "spec": SPEC,
        "mandate_id": mid,
        "parent_id": parent_id,
        "depth": int(parent.get("depth") or 0) + 1,
        "human_principal_id": parent.get("human_principal_id"),
        "human_root_digest": parent.get("human_root_digest"),
        "agent_id": (agent_id or parent.get("agent_id") or "").strip(),
        "scope": child_scope,
        "status": "active",
        "issued_at": _iso(),
        "expires_at": _iso(exp),
        "expires_at_unix": int(exp),
        "kid": key_id(),
    }
    if not body["agent_id"]:
        return {"ok": False, "reason": "agent_id_required", "mandate": None}

    sig = _sign_body(body)
    if signing_required() and not sig:
        return {"ok": False, "reason": "unsigned_halt", "mandate": None}
    body["signature"] = sig

    with _lock:
        _mandates[mid] = dict(body)

    base = (public_url or "").rstrip("/")
    return {
        "ok": True,
        "reason": None,
        "mandate": body,
        "reconstruct_url": f"{base}/v1/mandate/reconstruct" if base else None,
        "invariant": "Authority may only attenuate — never widen.",
    }


def revoke(mandate_id: str, *, reason: str | None = None) -> dict:
    mid = (mandate_id or "").strip()
    if not mid:
        return {"ok": False, "reason": "mandate_id_required", "revoked": []}

    revoked_ids: list[str] = []
    with _lock:
        if mid not in _mandates and mid not in _revoked:
            return {"ok": False, "reason": "unknown_mandate", "revoked": []}
        stack = [mid]
        while stack:
            cur = stack.pop()
            if cur in _revoked:
                continue
            _revoked.add(cur)
            # Do NOT mutate signed mandate bytes — revocation is out-of-band state.
            revoked_ids.append(cur)
            for child_id, row in list(_mandates.items()):
                if row.get("parent_id") == cur and child_id not in _revoked:
                    stack.append(child_id)

    return {
        "ok": True,
        "reason": reason or None,
        "revoked": revoked_ids,
        "cascade": True,
        "invariant": "Revocation is current-state truth — reconstruct must see it.",
    }


def get_mandate(mandate_id: str) -> dict | None:
    with _lock:
        row = _mandates.get(mandate_id)
        return dict(row) if row else None


def reconstruct(
    *,
    mandate_id: str | None = None,
    mandate: dict | None = None,
    action: str,
    sink: str,
    amount: float | None = None,
    resource: str = "",
    agent_id: str | None = None,
) -> dict:
    """Live authority reconstruction → ADMIT | DENY | HALT."""
    action = (action or "").strip()
    sink = (sink or "").strip()
    if not action or not sink:
        return {
            "outcome": "HALT",
            "reason": "action_and_sink_required",
            "admitted": False,
            "invariant": "A(t)=F(state_now) — incomplete act descriptor cannot admit.",
        }

    mid = (mandate_id or (mandate or {}).get("mandate_id") or "").strip()
    row = None
    if isinstance(mandate, dict) and mandate.get("mandate_id"):
        row = dict(mandate)
    elif mid:
        row = get_mandate(mid)

    if row is None:
        return {
            "outcome": "HALT",
            "reason": "mandate_unresolvable",
            "admitted": False,
            "invariant": "Missing mandate state → HALT, never guess.",
        }

    mid = str(row.get("mandate_id") or mid)
    if not _verify_sig(row, row.get("signature")):
        return {
            "outcome": "HALT",
            "reason": "signature_unverified",
            "admitted": False,
            "mandate_id": mid,
        }

    if mid in _revoked or _lineage_revoked(mid):
        return {
            "outcome": "DENY",
            "reason": "revoked",
            "admitted": False,
            "mandate_id": mid,
            "human_root_digest": row.get("human_root_digest"),
        }

    if time.time() > float(row.get("expires_at_unix") or 0):
        return {
            "outcome": "DENY",
            "reason": "expired",
            "admitted": False,
            "mandate_id": mid,
            "human_root_digest": row.get("human_root_digest"),
        }

    if not row.get("human_root_digest"):
        return {
            "outcome": "HALT",
            "reason": "human_root_missing",
            "admitted": False,
            "mandate_id": mid,
        }

    if agent_id and row.get("agent_id") and agent_id != row.get("agent_id"):
        return {
            "outcome": "DENY",
            "reason": "agent_mismatch",
            "admitted": False,
            "mandate_id": mid,
        }

    ok, why = _scope_allows(
        row.get("scope") or {},
        action=action,
        sink=sink,
        amount=amount,
        resource=resource or "",
    )
    if not ok:
        return {
            "outcome": "DENY",
            "reason": why,
            "admitted": False,
            "mandate_id": mid,
            "human_root_digest": row.get("human_root_digest"),
            "scope": row.get("scope"),
        }

    return {
        "outcome": "ADMIT",
        "reason": None,
        "admitted": True,
        "mandate_id": mid,
        "human_principal_id": row.get("human_principal_id"),
        "human_root_digest": row.get("human_root_digest"),
        "agent_id": row.get("agent_id"),
        "scope": row.get("scope"),
        "depth": row.get("depth"),
        "reconstructed_at": _iso(),
        "invariant": "Living authority reconstructed at consequence time.",
    }


def jwks() -> dict:
    pub = _public_key_bytes()
    kid = key_id()
    if not pub or not kid:
        return {"keys": []}
    return {
        "keys": [
            {
                "kty": "OKP",
                "crv": "Ed25519",
                "kid": kid,
                "x": _b64url(pub),
                "use": "sig",
                "alg": "EdDSA",
            }
        ]
    }


def manifest(public_url: str) -> dict:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Gate Mandate",
        "description": (
            "Living authority for agents. Human-rooted, attenuable-only, cascade-revocable. "
            "Must reconstruct at consequence time (A(t)=F(state_now)). "
            "HALT when authority cannot be determined — never guess."
        ),
        "invariant": "Prior approval is not current authority.",
        "outcomes": list(RECONSTRUCT_OUTCOMES),
        "issue": f"{base}/v1/mandate/issue",
        "attenuate": f"{base}/v1/mandate/attenuate",
        "revoke": f"{base}/v1/mandate/revoke",
        "reconstruct": f"{base}/v1/mandate/reconstruct",
        "jwks": f"{base}/.well-known/mandate-jwks.json",
        "related": {
            "right_to_act": f"{base}/.well-known/right-to-act.json",
            "note": "Mandate answers WHO still authorizes; Right-to-Act answers whether the act may EXIST.",
        },
    }
