"""Right-to-Act — does this candidate get to EXIST as an executable event?

Above coding: computation is not permission.
Rail-agnostic CandidateAct → EXIST | NONEXIST | HOLD, with signed receipts
for BOTH outcomes (NO_GO digests are first-class product, not log noise).

Optional single-use ticket: EXIST mints a burnable handle the sink must consume
before effectuation (atomic admit path against TOCTOU).
"""
from __future__ import annotations

import base64
import hashlib
import json
import secrets
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

try:
    from gate import receipt as receipt_mod
except ImportError:
    import receipt as receipt_mod

try:
    from gate import mandate as mandate_mod
except ImportError:
    import mandate as mandate_mod

SPEC = "gate-right-to-act-v1"
DECISIONS = ("EXIST", "NONEXIST", "HOLD")
DECISION_ALIASES = {
    "GO": "EXIST",
    "NO_GO": "NONEXIST",
    "NOGO": "NONEXIST",
    "DENY": "NONEXIST",
    "ALLOW": "EXIST",
    "HOLD": "HOLD",
    "EXIST": "EXIST",
    "NONEXIST": "NONEXIST",
}
DEFAULT_TTL_SECONDS = 300

_ticket_lock = threading.Lock()
_tickets: dict[str, dict[str, Any]] = {}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


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
    return f"gate-rta-{fp}" if fp else None


def normalize_decision(raw: str | None) -> str:
    s = (raw or "").strip().upper().replace("-", "_")
    return DECISION_ALIASES.get(s, s if s in DECISIONS else "NONEXIST")


def _args_hash(candidate: dict) -> str:
    if candidate.get("args_hash"):
        return str(candidate["args_hash"]).strip().lower()
    args = candidate.get("args")
    if args is None:
        return hashlib.sha256(b"").hexdigest()
    return hashlib.sha256(_canonical_json(args).encode("utf-8")).hexdigest()


def candidate_fingerprint(candidate: dict) -> str:
    c = candidate if isinstance(candidate, dict) else {}
    body = {
        "spec": SPEC,
        "action": str(c.get("action") or "").strip(),
        "sink": str(c.get("sink") or "").strip(),
        "actor": str(c.get("actor") or "").strip(),
        "args_hash": _args_hash(c),
        "resource": str(c.get("resource") or c.get("target") or "").strip(),
    }
    return hashlib.sha256(_canonical_json(body).encode("utf-8")).hexdigest()


def _policy_decide(candidate: dict, policy: dict | None, context: dict | None) -> tuple[str, list[str]]:
    """Non-compensatory Right-to-Act: any failed required constraint → NONEXIST."""
    signals: list[str] = []
    policy = policy if isinstance(policy, dict) else {}
    context = context if isinstance(context, dict) else {}
    c = candidate if isinstance(candidate, dict) else {}

    action = str(c.get("action") or "").strip()
    sink = str(c.get("sink") or "").strip()
    if not action:
        return "NONEXIST", ["missing_action"]
    if not sink:
        return "NONEXIST", ["missing_sink"]

    allowed_actions = policy.get("allowed_actions") or policy.get("actions")
    if isinstance(allowed_actions, list) and allowed_actions:
        if action not in {str(a).strip() for a in allowed_actions}:
            return "NONEXIST", ["action_not_allowed"]

    denied_actions = policy.get("denied_actions") or policy.get("deny")
    if isinstance(denied_actions, list) and action in {str(a).strip() for a in denied_actions}:
        return "NONEXIST", ["action_denied"]

    allowed_sinks = policy.get("allowed_sinks") or policy.get("sinks")
    if isinstance(allowed_sinks, list) and allowed_sinks:
        if sink not in {str(s).strip() for s in allowed_sinks}:
            return "NONEXIST", ["sink_not_allowed"]

    if policy.get("require_args_hash") and not (c.get("args_hash") or c.get("args") is not None):
        return "NONEXIST", ["args_uncommitted"]

    args = c.get("args") if isinstance(c.get("args"), dict) else {}
    amount = None
    if "amount" in args:
        try:
            amount = float(args["amount"])
        except (TypeError, ValueError):
            return "NONEXIST", ["invalid_amount"]

    max_amount = policy.get("max_amount")
    if max_amount is not None and amount is not None:
        try:
            if amount > float(max_amount):
                return "NONEXIST", ["amount_exceeds_cap"]
        except (TypeError, ValueError):
            return "NONEXIST", ["invalid_max_amount"]

    if policy.get("require_actor") and not str(c.get("actor") or "").strip():
        return "NONEXIST", ["missing_actor"]

    hold_actions = policy.get("hold_actions") or []
    if isinstance(hold_actions, list) and action in {str(a).strip() for a in hold_actions}:
        return "HOLD", ["human_review"]

    if context.get("force_nonexist"):
        return "NONEXIST", ["forced_nonexist"]

    return "EXIST", signals


def mint_receipt_jwt(
    *,
    evaluation_id: str,
    decision: str,
    fingerprint: str,
    signals: list[str],
    actor: str | None,
    action: str,
    sink: str,
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
    issuer: str | None = None,
    ticket_id: str | None = None,
) -> str | None:
    key = _signing_key()
    if not key:
        return None
    now = _utc_now()
    exp = now + timedelta(seconds=max(30, min(int(ttl_seconds or DEFAULT_TTL_SECONDS), 3600)))
    payload = {
        "spec": SPEC,
        "jti": evaluation_id,
        "iss": issuer or "gate.velaru.xyz",
        "sub": actor or "anonymous",
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "dec": decision,
        "fp": fingerprint,
        "sig": signals,
        "act": action,
        "sink": sink,
        "exists": decision == "EXIST",
        "refusal": decision == "NONEXIST",
    }
    if ticket_id:
        payload["tid"] = ticket_id
    header = {"alg": "EdDSA", "typ": "JWT", "kid": key_id()}
    header_b64 = _b64url(_canonical_json(header).encode("utf-8"))
    payload_b64 = _b64url(_canonical_json(payload).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    sig = key.sign(signing_input)
    return f"{header_b64}.{payload_b64}.{_b64url(sig)}"


def refusal_digest_from_payload(payload: dict) -> str:
    body = {
        "spec": SPEC,
        "kind": "no_go",
        "jti": payload.get("jti"),
        "fp": payload.get("fp"),
        "act": payload.get("act"),
        "sink": payload.get("sink"),
        "sig": payload.get("sig") or [],
        "iat": payload.get("iat"),
    }
    return hashlib.sha256(_canonical_json(body).encode("utf-8")).hexdigest()


def verify_receipt_jwt(token: str, *, expected_fingerprint: str | None = None) -> dict:
    meta: dict[str, Any] = {
        "spec": SPEC,
        "valid": False,
        "decision": None,
        "reason": None,
        "payload": None,
        "refusal_digest": None,
    }
    if not token or not isinstance(token, str):
        meta["reason"] = "missing_token"
        return meta
    parts = token.split(".")
    if len(parts) != 3:
        meta["reason"] = "malformed_jwt"
        return meta
    try:
        header = json.loads(_b64url_decode(parts[0]))
        payload = json.loads(_b64url_decode(parts[1]))
        sig = _b64url_decode(parts[2])
    except Exception:
        meta["reason"] = "decode_error"
        return meta

    pub = _public_key_bytes()
    if not pub:
        meta["reason"] = "verify_unconfigured"
        return meta
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        Ed25519PublicKey.from_public_bytes(pub).verify(
            sig, f"{parts[0]}.{parts[1]}".encode("utf-8")
        )
    except Exception:
        meta["reason"] = "bad_signature"
        return meta

    if header.get("alg") != "EdDSA":
        meta["reason"] = "unsupported_alg"
        return meta

    exp = payload.get("exp")
    if exp is not None and int(exp) < int(_utc_now().timestamp()):
        meta["reason"] = "expired"
        meta["payload"] = payload
        return meta

    if expected_fingerprint and payload.get("fp") != expected_fingerprint:
        meta["reason"] = "fingerprint_mismatch"
        meta["payload"] = payload
        return meta

    decision = normalize_decision(payload.get("dec"))
    if decision not in DECISIONS:
        meta["reason"] = "invalid_decision"
        meta["payload"] = payload
        return meta

    meta.update(
        {
            "valid": True,
            "decision": decision,
            "payload": payload,
            "reason": None,
            "refusal_digest": (
                refusal_digest_from_payload(payload) if decision == "NONEXIST" else None
            ),
        }
    )
    return meta


def _mint_ticket(
    *,
    evaluation_id: str,
    fingerprint: str,
    sink: str,
    ttl_seconds: int,
    mandate_id: str | None = None,
    action: str | None = None,
    agent_id: str | None = None,
    amount: float | None = None,
    resource: str | None = None,
) -> str:
    tid = f"rta_{secrets.token_hex(16)}"
    with _ticket_lock:
        _tickets[tid] = {
            "evaluation_id": evaluation_id,
            "fingerprint": fingerprint,
            "sink": sink,
            "expires_at": time.time() + max(30, min(int(ttl_seconds), 3600)),
            "burned": False,
            "mandate_id": mandate_id,
            "action": action,
            "agent_id": agent_id,
            "amount": amount,
            "resource": resource or "",
        }
    return tid


def burn_ticket(ticket_id: str, *, fingerprint: str, sink: str) -> dict:
    """Consume EXIST ticket. If mandate-bound, reconstruct living authority NOW."""
    now = time.time()
    with _ticket_lock:
        row = _tickets.get(ticket_id)
        if not row:
            return {"ok": False, "reason": "unknown_ticket", "burned": False}
        if row["burned"]:
            return {"ok": False, "reason": "already_burned", "burned": True}
        if now > float(row["expires_at"]):
            return {"ok": False, "reason": "expired", "burned": False}
        if row["fingerprint"] != fingerprint:
            return {"ok": False, "reason": "fingerprint_mismatch", "burned": False}
        if row["sink"] != sink:
            return {"ok": False, "reason": "sink_mismatch", "burned": False}
        snap = dict(row)

    # Reconstructive authority at consequence time (S-tier).
    mandate_id = snap.get("mandate_id")
    reconstruction = None
    if mandate_id:
        reconstruction = mandate_mod.reconstruct(
            mandate_id=mandate_id,
            action=str(snap.get("action") or ""),
            sink=sink,
            amount=snap.get("amount"),
            resource=str(snap.get("resource") or ""),
            agent_id=snap.get("agent_id"),
        )
        if reconstruction.get("outcome") == "HALT":
            return {
                "ok": False,
                "reason": "mandate_halt",
                "burned": False,
                "reconstruction": reconstruction,
                "invariant": "Cannot determine living authority → HALT, never burn.",
            }
        if not reconstruction.get("admitted"):
            return {
                "ok": False,
                "reason": f"mandate_{reconstruction.get('reason') or 'denied'}",
                "burned": False,
                "reconstruction": reconstruction,
                "invariant": "Prior EXIST is not current authority.",
            }

    with _ticket_lock:
        row = _tickets.get(ticket_id)
        if not row or row["burned"]:
            return {"ok": False, "reason": "already_burned", "burned": True}
        row["burned"] = True
        row["burned_at"] = now
        evaluation_id = row["evaluation_id"]

    out = {
        "ok": True,
        "reason": None,
        "burned": True,
        "evaluation_id": evaluation_id,
        "ticket_id": ticket_id,
    }
    if reconstruction:
        out["reconstruction"] = reconstruction
    return out


def evaluate(body: dict, *, account_id: str | None = None, public_url: str) -> dict:
    _ = account_id
    candidate = body.get("candidate") if isinstance(body.get("candidate"), dict) else {}
    if not candidate:
        candidate = {
            "action": body.get("action"),
            "sink": body.get("sink"),
            "actor": body.get("actor") or body.get("agent_id"),
            "args": body.get("args"),
            "args_hash": body.get("args_hash"),
            "resource": body.get("resource") or body.get("target"),
        }
    policy = body.get("policy") if isinstance(body.get("policy"), dict) else {}
    context = body.get("context") if isinstance(body.get("context"), dict) else {}
    ttl = int(body.get("ttl_seconds") or policy.get("ttl_seconds") or DEFAULT_TTL_SECONDS)
    mint_ticket = bool(body.get("mint_ticket", True))

    evaluation_id = f"rta_{uuid.uuid4().hex}"
    created_at = _iso(_utc_now())
    fingerprint = candidate_fingerprint(candidate)
    decision, signals = _policy_decide(candidate, policy, context)

    # Mandate gate: living authority must reconstruct before EXIST.
    mandate_obj = body.get("mandate") if isinstance(body.get("mandate"), dict) else None
    mandate_id = body.get("mandate_id") or (mandate_obj or {}).get("mandate_id")
    require_mandate = bool(policy.get("require_mandate") or context.get("require_mandate"))
    reconstruction = None
    amount = None
    args = candidate.get("args") if isinstance(candidate.get("args"), dict) else {}
    if "amount" in args:
        try:
            amount = float(args["amount"])
        except (TypeError, ValueError):
            amount = None

    if require_mandate and not (mandate_id or mandate_obj):
        decision = "NONEXIST"
        signals = list(signals) + ["mandate_required"]
    elif mandate_id or mandate_obj:
        reconstruction = mandate_mod.reconstruct(
            mandate_id=str(mandate_id) if mandate_id else None,
            mandate=mandate_obj,
            action=str(candidate.get("action") or "").strip(),
            sink=str(candidate.get("sink") or "").strip(),
            amount=amount,
            resource=str(candidate.get("resource") or candidate.get("target") or ""),
            agent_id=str(candidate.get("actor") or "").strip() or None,
        )
        if reconstruction.get("outcome") == "HALT":
            decision = "HOLD"
            signals = list(signals) + ["mandate_halt", reconstruction.get("reason") or "halt"]
        elif not reconstruction.get("admitted"):
            decision = "NONEXIST"
            signals = list(signals) + [
                "mandate_denied",
                reconstruction.get("reason") or "denied",
            ]
        else:
            mandate_id = reconstruction.get("mandate_id") or mandate_id

    if signing_required() and not _signing_key():
        decision = "NONEXIST"
        if "unsigned_halt" not in signals:
            signals.append("unsigned_halt")

    ticket_id = None
    if decision == "EXIST" and mint_ticket:
        ticket_id = _mint_ticket(
            evaluation_id=evaluation_id,
            fingerprint=fingerprint,
            sink=str(candidate.get("sink") or "").strip(),
            ttl_seconds=ttl,
            mandate_id=str(mandate_id) if mandate_id else None,
            action=str(candidate.get("action") or "").strip() or None,
            agent_id=str(candidate.get("actor") or "").strip() or None,
            amount=amount,
            resource=str(candidate.get("resource") or candidate.get("target") or ""),
        )

    issuer = (
        (public_url or "").replace("https://", "").replace("http://", "").split("/")[0]
        or "gate.velaru.xyz"
    )
    receipt = mint_receipt_jwt(
        evaluation_id=evaluation_id,
        decision=decision,
        fingerprint=fingerprint,
        signals=signals,
        actor=str(candidate.get("actor") or "").strip() or None,
        action=str(candidate.get("action") or "").strip(),
        sink=str(candidate.get("sink") or "").strip(),
        ttl_seconds=ttl,
        issuer=issuer,
        ticket_id=ticket_id,
    )

    if signing_required() and not receipt:
        decision = "NONEXIST"
        signals = list(signals) + ["unsigned_halt"]
        ticket_id = None

    refusal = None
    if decision == "NONEXIST":
        if receipt:
            verified = verify_receipt_jwt(receipt)
            refusal = verified.get("refusal_digest")
        if not refusal:
            refusal = refusal_digest_from_payload(
                {
                    "jti": evaluation_id,
                    "fp": fingerprint,
                    "act": candidate.get("action"),
                    "sink": candidate.get("sink"),
                    "sig": signals,
                    "iat": int(_utc_now().timestamp()),
                }
            )

    base = (public_url or "").rstrip("/")
    out = {
        "spec": SPEC,
        "evaluation_id": evaluation_id,
        "decision": decision,
        "go": decision == "EXIST",
        "alias": {"GO": "EXIST", "NO_GO": "NONEXIST", "HOLD": "HOLD"},
        "halt": decision != "EXIST",
        "exists": decision == "EXIST",
        "signals": signals,
        "fingerprint": fingerprint,
        "args_hash": _args_hash(candidate),
        "receipt": receipt,
        "ticket_id": ticket_id,
        "mandate_id": mandate_id,
        "reconstruction": reconstruction,
        "refusal_digest": refusal,
        "expires_in": ttl,
        "created_at": created_at,
        "verify_url": f"{base}/v1/right-to-act/verify",
        "burn_url": f"{base}/v1/right-to-act/burn",
        "manifest": f"{base}/.well-known/right-to-act.json",
        "clearance_only": True,
        "write_executed": False,
        "invariant": "Computation does not confer authority for consequence.",
    }
    if decision == "EXIST":
        out["message"] = (
            "Right-to-Act EXIST — sink may effectuate only after ticket burn "
            "+ live mandate reconstruct + receipt verify."
        )
    elif decision == "HOLD":
        out["message"] = (
            "Right-to-Act HOLD — living authority could not be determined (HALT). "
            "Act remains non-effective."
        )
    else:
        out["message"] = (
            "Right-to-Act NONEXIST — act has no right to become real. Refusal is the product."
        )
    return out


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
        "name": "Gate Right-to-Act",
        "description": (
            "Does this CandidateAct get to EXIST as an executable event? "
            "Non-compensatory GO/NO_GO with signed receipts for both outcomes. "
            "NO_GO digests are first-class. EXIST mints a single-use sink ticket."
        ),
        "invariant": "Computation does not confer authority for consequence.",
        "decisions": list(DECISIONS),
        "evaluate": f"{base}/v1/right-to-act/evaluate",
        "demo_evaluate": f"{base}/demo/right-to-act/evaluate",
        "verify": f"{base}/v1/right-to-act/verify",
        "burn": f"{base}/v1/right-to-act/burn",
        "jwks": f"{base}/.well-known/right-to-act-jwks.json",
        "sdk": f"{base}/sdk/right-to-act/wrap.mjs",
        "fail_closed": True,
        "receipt_ttl_seconds_default": DEFAULT_TTL_SECONDS,
        "related": {
            "prefinality": f"{base}/.well-known/prefinality.json",
            "mandate": f"{base}/.well-known/mandate.json",
            "note": (
                "Mandate = living who; Right-to-Act = may this act EXIST; "
                "Prefinality = payment-rail specialization."
            ),
        },
    }
