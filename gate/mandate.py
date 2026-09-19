"""Mandate — living authority that must reconstruct at consequence time.

S-tier above Right-to-Act:
  Right-to-Act asks: may this act EXIST?
  Mandate asks: whose living authority still reconstructs NOW?
  Mortality asks: is this authority still allowed to become real?

Invariant: Prior approval is not current authority.
A(t) = F(state_now). If reconstruct fails → HALT (never guess).
Death certificates make every sink burn path non-completable for a lineage.

Root mandates bind a human principal digest. Children may only attenuate
(narrow). Revocation cascades. Mortality is stranger-verifiable and stronger
than revoke: dead lineages cannot issue, attenuate, reconstruct, or burn.
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
DEATH_SPEC = "gate-mortality-v1"
RECONSTRUCT_OUTCOMES = ("ADMIT", "DENY", "HALT")

_lock = threading.Lock()
_mandates: dict[str, dict[str, Any]] = {}
_revoked: set[str] = set()
_deaths: dict[str, dict[str, Any]] = {}  # death_id -> certificate
_dead_mandates: dict[str, str] = {}  # mandate_id -> death_id
_dead_roots: dict[str, str] = {}  # human_root_digest -> death_id
_dead_agents: dict[str, str] = {}  # agent_id -> death_id
_death_epoch = 0


def _reset_for_tests() -> None:
    """Clear in-memory mandate/mortality state (unit tests only)."""
    global _death_epoch
    with _lock:
        _mandates.clear()
        _revoked.clear()
        _deaths.clear()
        _dead_mandates.clear()
        _dead_roots.clear()
        _dead_agents.clear()
        _death_epoch = 0


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
            if cur in _revoked or cur in _dead_mandates:
                return True
            seen.add(cur)
            row = _mandates.get(cur)
            if not row:
                return True
            cur = row.get("parent_id")
        return False


def _death_hit_for_row(row: dict) -> dict | None:
    """Return death certificate if this mandate/root/agent is dead."""
    mid = str(row.get("mandate_id") or "")
    root = str(row.get("human_root_digest") or "")
    agent = str(row.get("agent_id") or "")
    principal = str(row.get("human_principal_id") or "")
    death_id = None
    if mid and mid in _dead_mandates:
        death_id = _dead_mandates[mid]
    elif root and root in _dead_roots:
        death_id = _dead_roots[root]
    elif principal and f"principal:{principal}" in _dead_roots:
        death_id = _dead_roots[f"principal:{principal}"]
    elif agent and agent in _dead_agents:
        death_id = _dead_agents[agent]
    if not death_id:
        # Walk parents for mandate death.
        cur = mid
        seen: set[str] = set()
        while cur and cur not in seen:
            if cur in _dead_mandates:
                death_id = _dead_mandates[cur]
                break
            seen.add(cur)
            parent = _mandates.get(cur)
            if not parent:
                break
            cur = parent.get("parent_id")
    if not death_id:
        return None
    cert = _deaths.get(death_id)
    return dict(cert) if cert else None


def _collect_descendants(root_id: str) -> list[str]:
    out: list[str] = []
    stack = [root_id]
    seen: set[str] = set()
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        out.append(cur)
        for child_id, row in list(_mandates.items()):
            if row.get("parent_id") == cur:
                stack.append(child_id)
    return out


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

    principal = human_principal_id.strip()
    with _lock:
        if root in _dead_roots or f"principal:{principal}" in _dead_roots:
            return {
                "ok": False,
                "reason": "dead_human_root",
                "mandate": None,
                "invariant": "Death ends the right to become real — cannot issue.",
            }
        if agent in _dead_agents:
            return {
                "ok": False,
                "reason": "dead_agent",
                "mandate": None,
                "invariant": "Death ends the right to become real — cannot issue.",
            }

    now = time.time()
    ttl = max(60, min(int(ttl_seconds), 30 * 86400))
    mid = f"man_{uuid.uuid4().hex}"
    body = {
        "spec": SPEC,
        "mandate_id": mid,
        "parent_id": None,
        "depth": 0,
        "human_principal_id": principal,
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
        death_cert = _death_hit_for_row(parent) if parent else None
    if not parent:
        return {"ok": False, "reason": "unknown_parent", "mandate": None}
    if death_cert:
        return {
            "ok": False,
            "reason": "parent_dead",
            "mandate": None,
            "death_id": death_cert.get("death_id"),
            "invariant": "Death ends the right to become real — cannot attenuate.",
        }
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


def die(
    *,
    mandate_id: str | None = None,
    human_principal_id: str | None = None,
    human_root_digest: str | None = None,
    agent_id: str | None = None,
    reason: str = "mortality",
    public_url: str = "",
) -> dict:
    """Issue a Death Certificate. Ends the right to become real.

    Kill switches ask a process to stop.
    Mortality makes every sink burn path non-completable for the lineage.
    """
    global _death_epoch
    mid = (mandate_id or "").strip() or None
    principal = (human_principal_id or "").strip() or None
    root = (human_root_digest or "").strip() or None
    agent = (agent_id or "").strip() or None

    if not any([mid, principal, root, agent]):
        return {
            "ok": False,
            "reason": "subject_required",
            "death_certificate": None,
            "invariant": "Death needs a subject: mandate, human root, or agent.",
        }

    with _lock:
        subjects: list[str] = []
        killed: list[str] = []

        if mid:
            if mid not in _mandates and mid not in _dead_mandates:
                return {
                    "ok": False,
                    "reason": "unknown_mandate",
                    "death_certificate": None,
                }
            subjects = _collect_descendants(mid) if mid in _mandates else [mid]
        elif root or principal:
            if principal and not root:
                # Kill all mandates under this principal id (exact match).
                subjects = [
                    k
                    for k, row in _mandates.items()
                    if row.get("human_principal_id") == principal
                ]
                if not subjects and not root:
                    # Still issue a principal-scoped death even with zero live mandates.
                    pass
            if root:
                subjects = list(
                    {
                        *subjects,
                        *[
                            k
                            for k, row in _mandates.items()
                            if row.get("human_root_digest") == root
                        ],
                    }
                )
        elif agent:
            subjects = [k for k, row in _mandates.items() if row.get("agent_id") == agent]

        for sid in subjects:
            _revoked.add(sid)
            killed.append(sid)

        _death_epoch += 1
        death_id = f"death_{uuid.uuid4().hex}"
        now = time.time()

        # Resolve root/agent labels from first subject when possible.
        sample = _mandates.get(subjects[0]) if subjects else None
        cert_body = {
            "spec": DEATH_SPEC,
            "death_id": death_id,
            "epoch": _death_epoch,
            "reason": reason or "mortality",
            "died_at": _iso(now),
            "died_at_unix": int(now),
            "subject": {
                "mandate_id": mid,
                "human_principal_id": principal
                or (sample or {}).get("human_principal_id"),
                "human_root_digest": root
                or (sample or {}).get("human_root_digest"),
                "agent_id": agent or (sample or {}).get("agent_id"),
            },
            "cascade_killed": sorted(set(killed)),
            "kid": key_id(),
            "invariant": "Death ends the right to become real — burns must fail.",
        }
        sig = _sign_body(cert_body)
        if signing_required() and not sig:
            return {"ok": False, "reason": "unsigned_halt", "death_certificate": None}
        cert_body["signature"] = sig

        _deaths[death_id] = dict(cert_body)
        for sid in killed:
            _dead_mandates[sid] = death_id
        # Scope death markers to the *subject of die*, not incidental labels on a mandate.
        # mandate-only death → tree via _dead_mandates; root/agent/principal death → lineage.
        if root:
            _dead_roots[root] = death_id
        if agent:
            _dead_agents[agent] = death_id
        if principal:
            _dead_roots[f"principal:{principal}"] = death_id
            # Also mark concrete root digests currently under this principal.
            for row in _mandates.values():
                if row.get("human_principal_id") == principal and row.get("human_root_digest"):
                    _dead_roots[str(row["human_root_digest"])] = death_id

    base = (public_url or "").rstrip("/")
    # Index into Finder — death becomes searchable consequence.
    try:
        from gate import finder as finder_mod
    except ImportError:
        try:
            import finder as finder_mod
        except ImportError:
            finder_mod = None
    if finder_mod is not None:
        try:
            finder_mod.record_death(cert_body)
        except Exception:
            pass

    return {
        "ok": True,
        "reason": None,
        "death_certificate": cert_body,
        "verify_url": f"{base}/v1/mandate/death/verify" if base else None,
        "well_known": f"{base}/.well-known/deaths/{death_id}.json" if base else None,
        "cascade_killed": cert_body["cascade_killed"],
        "invariant": "Kill switches stop processes. Death certificates void authority.",
    }


def get_death(death_id: str) -> dict | None:
    with _lock:
        row = _deaths.get(death_id)
        return dict(row) if row else None


def verify_death(certificate: dict | str | None = None, *, death_id: str | None = None) -> dict:
    """Stranger-verify a death certificate. valid | invalid | unknown."""
    cert = None
    if isinstance(certificate, dict):
        cert = dict(certificate)
        death_id = str(cert.get("death_id") or death_id or "")
    elif death_id:
        cert = get_death(death_id)

    if not cert:
        return {
            "spec": DEATH_SPEC,
            "valid": False,
            "reason": "unknown_death",
            "death_id": death_id,
        }

    if not _verify_sig(cert, cert.get("signature")):
        return {
            "spec": DEATH_SPEC,
            "valid": False,
            "reason": "bad_signature",
            "death_id": cert.get("death_id"),
        }

    # Presence in clearinghouse is current-world truth for this node.
    stored = get_death(str(cert.get("death_id") or ""))
    if not stored:
        return {
            "spec": DEATH_SPEC,
            "valid": False,
            "reason": "not_in_clearinghouse",
            "death_id": cert.get("death_id"),
            "note": "Signature may verify, but this node has no mortality record.",
        }

    return {
        "spec": DEATH_SPEC,
        "valid": True,
        "reason": None,
        "death_id": cert.get("death_id"),
        "epoch": cert.get("epoch"),
        "cascade_killed": cert.get("cascade_killed") or [],
        "subject": cert.get("subject"),
        "died_at": cert.get("died_at"),
        "invariant": "Death is stranger-verifiable current-state truth.",
    }


def is_dead(
    *,
    mandate_id: str | None = None,
    human_root_digest: str | None = None,
    agent_id: str | None = None,
) -> dict:
    """Quick mortality check for sinks."""
    with _lock:
        death_id = None
        if mandate_id and mandate_id in _dead_mandates:
            death_id = _dead_mandates[mandate_id]
        elif mandate_id:
            cur = mandate_id
            seen: set[str] = set()
            while cur and cur not in seen:
                if cur in _dead_mandates:
                    death_id = _dead_mandates[cur]
                    break
                seen.add(cur)
                parent = _mandates.get(cur)
                if not parent:
                    break
                # root/agent death also counts
                root = parent.get("human_root_digest")
                agent = parent.get("agent_id")
                if root and root in _dead_roots:
                    death_id = _dead_roots[root]
                    break
                if agent and agent in _dead_agents:
                    death_id = _dead_agents[agent]
                    break
                cur = parent.get("parent_id")
        if not death_id and human_root_digest and human_root_digest in _dead_roots:
            death_id = _dead_roots[human_root_digest]
        if not death_id and agent_id and agent_id in _dead_agents:
            death_id = _dead_agents[agent_id]
        cert = dict(_deaths[death_id]) if death_id and death_id in _deaths else None
    return {
        "dead": bool(cert),
        "death_id": death_id,
        "death_certificate": cert,
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

    # Mortality clears first — dead authority cannot admit.
    with _lock:
        death_cert = _death_hit_for_row(row)
    if death_cert:
        return {
            "outcome": "DENY",
            "reason": "dead",
            "admitted": False,
            "mandate_id": mid,
            "human_root_digest": row.get("human_root_digest"),
            "death_id": death_cert.get("death_id"),
            "death_certificate": death_cert,
            "invariant": "Death ends the right to become real — burns must fail.",
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


def export_deaths(*, since_epoch: int = 0, since_unix: int = 0) -> dict:
    """Federation export — peer nodes pull stranger-verifiable death certificates."""
    with _lock:
        rows = []
        for cert in _deaths.values():
            if int(cert.get("epoch") or 0) < int(since_epoch or 0):
                continue
            if int(cert.get("died_at_unix") or 0) < int(since_unix or 0):
                continue
            rows.append(dict(cert))
        epoch = _death_epoch
    rows.sort(key=lambda c: (int(c.get("epoch") or 0), int(c.get("died_at_unix") or 0)))
    return {
        "spec": DEATH_SPEC,
        "federation": "gate-mortality-fed-v1",
        "epoch": epoch,
        "count": len(rows),
        "deaths": rows,
        "invariant": "Death clears across nodes — authority voided everywhere it is known.",
    }


def ingest_death(
    certificate: dict | None = None,
    *,
    peer: str | None = None,
    public_url: str = "",
) -> dict:
    """Federation ingest — accept a verified foreign death into this clearinghouse.

    Does not re-sign. Stores the peer certificate after local signature verify,
    then applies the same lineage voiding as a local die for known subjects.
    """
    global _death_epoch
    cert = dict(certificate) if isinstance(certificate, dict) else None
    if not cert:
        return {"ok": False, "reason": "certificate_required", "death_certificate": None}

    death_id = str(cert.get("death_id") or "").strip()
    if not death_id:
        return {"ok": False, "reason": "death_id_required", "death_certificate": None}

    if not _verify_sig(cert, cert.get("signature")):
        return {"ok": False, "reason": "bad_signature", "death_certificate": None}

    with _lock:
        if death_id in _deaths:
            return {
                "ok": True,
                "reason": "already_known",
                "death_certificate": dict(_deaths[death_id]),
                "peer": peer,
            }

        subj = cert.get("subject") if isinstance(cert.get("subject"), dict) else {}
        mid = (subj.get("mandate_id") or "").strip() or None
        principal = (subj.get("human_principal_id") or "").strip() or None
        root = (subj.get("human_root_digest") or "").strip() or None
        agent = (subj.get("agent_id") or "").strip() or None

        subjects: list[str] = []
        if mid and mid in _mandates:
            subjects = _collect_descendants(mid)
        elif root or principal:
            if principal:
                subjects.extend(
                    k
                    for k, row in _mandates.items()
                    if row.get("human_principal_id") == principal
                )
            if root:
                subjects.extend(
                    k
                    for k, row in _mandates.items()
                    if row.get("human_root_digest") == root
                )
            subjects = list(dict.fromkeys(subjects))
        elif agent:
            subjects = [k for k, row in _mandates.items() if row.get("agent_id") == agent]

        killed: list[str] = []
        for sid in subjects:
            _revoked.add(sid)
            killed.append(sid)

        stored = dict(cert)
        stored["federated_from"] = (peer or "").strip() or None
        stored["ingested_at"] = _iso()
        # Merge cascade with local kills for this node's view.
        prior = list(stored.get("cascade_killed") or [])
        stored["cascade_killed"] = sorted(set(prior) | set(killed))

        _deaths[death_id] = stored
        for sid in stored["cascade_killed"]:
            _dead_mandates[sid] = death_id
        if root:
            _dead_roots[root] = death_id
        if agent:
            _dead_agents[agent] = death_id
        if principal:
            _dead_roots[f"principal:{principal}"] = death_id
            for row in _mandates.values():
                if row.get("human_principal_id") == principal and row.get("human_root_digest"):
                    _dead_roots[str(row["human_root_digest"])] = death_id

        try:
            _death_epoch = max(int(_death_epoch), int(cert.get("epoch") or 0))
        except (TypeError, ValueError):
            pass

    # Index into Finder (the Google that never happened).
    try:
        from gate import finder as finder_mod
    except ImportError:
        try:
            import finder as finder_mod
        except ImportError:
            finder_mod = None
    if finder_mod is not None:
        finder_mod.record_death(stored)

    base = (public_url or "").rstrip("/")
    return {
        "ok": True,
        "reason": None,
        "death_certificate": stored,
        "peer": peer,
        "well_known": f"{base}/.well-known/deaths/{death_id}.json" if base else None,
        "invariant": "Federated death is local non-completability.",
    }


def manifest(public_url: str) -> dict:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "death_spec": DEATH_SPEC,
        "name": "Gate Mandate + Mortality Clearinghouse",
        "description": (
            "Living authority for agents. Human-rooted, attenuable-only, cascade-revocable. "
            "Must reconstruct at consequence time (A(t)=F(state_now)). "
            "Death certificates make burn paths non-completable for a lineage. "
            "HALT when authority cannot be determined — never guess."
        ),
        "invariant": "Prior approval is not current authority. Death ends the right to become real.",
        "outcomes": list(RECONSTRUCT_OUTCOMES),
        "issue": f"{base}/v1/mandate/issue",
        "attenuate": f"{base}/v1/mandate/attenuate",
        "revoke": f"{base}/v1/mandate/revoke",
        "die": f"{base}/v1/mandate/die",
        "reconstruct": f"{base}/v1/mandate/reconstruct",
        "death_verify": f"{base}/v1/mandate/death/verify",
        "death_export": f"{base}/v1/mandate/deaths/export",
        "death_ingest": f"{base}/v1/mandate/deaths/ingest",
        "death_well_known": f"{base}/.well-known/deaths/{{death_id}}.json",
        "jwks": f"{base}/.well-known/mandate-jwks.json",
        "related": {
            "right_to_act": f"{base}/.well-known/right-to-act.json",
            "finder": f"{base}/.well-known/finder.json",
            "note": (
                "Mandate = WHO still authorizes; Mortality = authority is dead; "
                "Right-to-Act = whether the act may EXIST; "
                "Finder = the Google that never happened."
            ),
        },
    }
