"""Pre-finality clearance — GO/NO-GO before irreversible commit (x402, RTP).

Rail-agnostic evaluate contract:
  POST body → decision + signed JWT receipt bound to transfer fingerprint.

Fail-closed: missing fields, policy breach, fuse DEAD/unverified, unsigned
receipt, storage errors, or any exception → NO_GO.

GO receipts are single-use: jti is consumed on first successful commit-path
verification (consume=True). Legitimate retries after redemption must
re-evaluate for a new jti — replay of the same JWT is rejected.
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

try:
    from gate import receipt as receipt_mod
except ImportError:
    import receipt as receipt_mod

SPEC = "gate-prefinality-v1"
RAILS = ("x402", "rtp")
DECISIONS = ("GO", "NO_GO", "HOLD")
DEFAULT_TTL_SECONDS = 300

_EVM_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")
_ROUTING_RE = re.compile(r"^\d{9}$")
_ACCOUNT_RE = re.compile(r"^\d{4,17}$")


def _db_mod():
    try:
        from gate import db as db_mod
    except ImportError:
        import db as db_mod
    return db_mod


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _utc_now()).replace(microsecond=0).isoformat()


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def signing_required() -> bool:
    return receipt_mod.signing_required()


def _signing_key():
    return receipt_mod._ed25519_signing_key()


def _public_key_bytes() -> bytes | None:
    return receipt_mod._ed25519_public_key_bytes()


def key_id() -> str | None:
    fp = receipt_mod.receipt_public_key_fingerprint()
    return f"gate-prefinality-{fp}" if fp else None


def transfer_fingerprint(*, rail: str, transfer: dict) -> str:
    body = {"spec": SPEC, "rail": rail, "transfer": _normalize_transfer(rail, transfer)}
    return hashlib.sha256(_canonical_json(body).encode("utf-8")).hexdigest()


def _normalize_transfer(rail: str, transfer: dict | None) -> dict:
    t = transfer if isinstance(transfer, dict) else {}
    out: dict[str, Any] = {}
    amount = t.get("amount")
    if amount is not None:
        out["amount"] = str(amount).strip()
    currency = (t.get("currency") or "").strip().upper()
    if currency:
        out["currency"] = currency
    cp = (
        t.get("counterparty")
        or t.get("payto")
        or t.get("payTo")
        or ""
    ).strip()
    if cp:
        out["counterparty"] = cp
    if rail == "rtp":
        routing = (t.get("routing_number") or "").strip()
        account = (t.get("account_number") or "").strip()
        if routing:
            out["routing_number"] = routing
        if account:
            out["account_number"] = _mask_account(account)
        ext = (t.get("external_account_id") or "").strip()
        if ext:
            out["external_account_id"] = ext
    resource = (t.get("resource_url") or "").strip()
    if resource:
        out["resource_url"] = resource[:512]
    return out


def _mask_account(account: str) -> str:
    digits = re.sub(r"\D", "", account)
    if len(digits) <= 4:
        return "****"
    return f"****{digits[-4:]}"


def _parse_amount(raw) -> float | None:
    if raw is None:
        return None
    try:
        return float(str(raw).strip())
    except (TypeError, ValueError):
        return None


def _validate_transfer(rail: str, transfer: dict) -> list[str]:
    errors: list[str] = []
    t_raw = transfer if isinstance(transfer, dict) else {}
    t = _normalize_transfer(rail, t_raw)
    amount = _parse_amount(t.get("amount"))
    if amount is None or amount <= 0:
        errors.append("invalid_amount")
    currency = (t.get("currency") or "").upper()
    cp = t.get("counterparty") or ""
    if rail == "x402":
        if currency not in ("", "USDC", "USD"):
            errors.append("unsupported_currency")
        if not _EVM_RE.match(cp):
            errors.append("invalid_counterparty")
    elif rail == "rtp":
        if currency not in ("", "USD"):
            errors.append("unsupported_currency")
        has_ext = bool(t.get("external_account_id"))
        has_bank = bool(t_raw.get("routing_number") and t_raw.get("account_number"))
        if not has_ext and not has_bank:
            errors.append("rtp_counterparty_required")
        if t_raw.get("routing_number") and not _ROUTING_RE.match(str(t_raw["routing_number"]).strip()):
            errors.append("invalid_routing_number")
        acct = t_raw.get("account_number")
        if acct and not _ACCOUNT_RE.match(re.sub(r"\D", "", str(acct))):
            errors.append("invalid_account_number")
    else:
        errors.append("unsupported_rail")
    return errors


def _policy_signals(
    *,
    rail: str,
    transfer: dict,
    mandate: dict | None,
    context: dict | None,
) -> tuple[str, list[str]]:
    signals: list[str] = []
    mandate = mandate if isinstance(mandate, dict) else {}
    context = context if isinstance(context, dict) else {}
    t = transfer if isinstance(transfer, dict) else {}

    errors = _validate_transfer(rail, t)
    if errors:
        return "NO_GO", errors

    amount = _parse_amount(t.get("amount"))
    max_amount = _parse_amount(
        mandate.get("max_amount") or mandate.get("max_payment") or mandate.get("amount_cap")
    )
    if max_amount is not None and amount is not None and amount > max_amount:
        signals.append("amount_exceeds_cap")
        return "NO_GO", signals

    expected = (
        mandate.get("expected_payto")
        or mandate.get("expected_counterparty")
        or mandate.get("expected_payTo")
        or ""
    ).strip()
    actual = (t.get("counterparty") or t.get("payto") or t.get("payTo") or "").strip()
    if expected and actual and expected.lower() != actual.lower():
        signals.append("routing_anomaly")
        return "NO_GO", signals

    untrusted = (context.get("untrusted_text") or context.get("untrusted") or "").strip()
    if untrusted and actual and actual.lower() in untrusted.lower():
        signals.append("injection_destination")
        return "NO_GO", signals

    intent = (mandate.get("intent") or context.get("intended") or "").strip()
    if intent and untrusted and intent.lower() not in untrusted.lower() and actual:
        if untrusted.lower() in actual.lower():
            signals.append("intent_mismatch")
            return "NO_GO", signals

    review_ceiling = _parse_amount(mandate.get("review_ceiling") or mandate.get("hold_above"))
    if review_ceiling is not None and amount is not None and amount > review_ceiling:
        signals.append("review_threshold")
        return "HOLD", signals

    daily_cap = _parse_amount(mandate.get("daily_cap"))
    if daily_cap is not None and amount is not None and amount > daily_cap:
        signals.append("daily_cap_exceeded")
        return "NO_GO", signals

    return "GO", signals


def _ensure_redemption_table(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS prefinality_receipt_redemptions (
            jti TEXT PRIMARY KEY,
            fingerprint TEXT NOT NULL,
            rail TEXT,
            redeemed_at TEXT NOT NULL,
            evaluation_id TEXT
        )
        """
    )


def _redeem_jti(*, jti: str, fingerprint: str, rail: str | None = None) -> dict:
    """Atomically consume a GO jti. First success wins; reuse → receipt_replay."""
    jti = (jti or "").strip()
    fingerprint = (fingerprint or "").strip()
    if not jti or not fingerprint:
        return {"ok": False, "reason": "redeem_missing_jti_or_fingerprint"}
    db_mod = _db_mod()
    now = _iso()
    try:
        with db_mod.db() as conn:
            _ensure_redemption_table(conn)
            existing = conn.execute(
                "SELECT jti, redeemed_at FROM prefinality_receipt_redemptions WHERE jti = ?",
                (jti,),
            ).fetchone()
            if existing:
                redeemed_at = existing["redeemed_at"] if not isinstance(existing, tuple) else existing[1]
                return {"ok": False, "reason": "receipt_replay", "redeemed_at": redeemed_at}
            conn.execute(
                """INSERT INTO prefinality_receipt_redemptions
                   (jti, fingerprint, rail, redeemed_at, evaluation_id)
                   VALUES (?, ?, ?, ?, ?)""",
                (jti, fingerprint, rail, now, jti),
            )
        return {"ok": True, "reason": None, "redeemed_at": now}
    except Exception as exc:  # noqa: BLE001 — fail closed
        msg = str(exc).lower()
        if "unique" in msg or "constraint" in msg:
            return {"ok": False, "reason": "receipt_replay"}
        return {"ok": False, "reason": "redeem_store_error"}


def mint_receipt_jwt(
    *,
    evaluation_id: str,
    rail: str,
    decision: str,
    fingerprint: str,
    signals: list[str],
    agent_id: str | None,
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
    issuer: str | None = None,
) -> str | None:
    key = _signing_key()
    if not key:
        return None
    now = _utc_now()
    exp = now + timedelta(seconds=max(30, min(int(ttl_seconds or DEFAULT_TTL_SECONDS), 3600)))
    kid = key_id()
    payload = {
        "spec": SPEC,
        "jti": evaluation_id,
        "iss": issuer or "gate.velaru.xyz",
        "sub": agent_id or "anonymous",
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "rail": rail,
        "dec": decision,
        "fp": fingerprint,
        "sig": list(signals or []),
        "one_shot": True,
    }
    header = {"alg": "EdDSA", "typ": "JWT", "kid": kid}
    header_b64 = _b64url(_canonical_json(header).encode("utf-8"))
    payload_b64 = _b64url(_canonical_json(payload).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    sig = key.sign(signing_input)
    return f"{header_b64}.{payload_b64}.{_b64url(sig)}"


def verify_receipt_jwt(
    token: str,
    *,
    expected_fingerprint: str | None = None,
    consume: bool = True,
) -> dict:
    """Verify receipt JWT.

    consume=True (default): GO jti is single-use — first successful verify
    redeems it; reuse returns valid=False reason=receipt_replay.
    Pass consume=False for signature-only audit inspection (does not authorize commit).
    """
    meta: dict[str, Any] = {
        "spec": SPEC,
        "valid": False,
        "decision": None,
        "reason": None,
        "payload": None,
        "redeemed": False,
        "consume": bool(consume),
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

        pk = Ed25519PublicKey.from_public_bytes(pub)
        signing_input = f"{parts[0]}.{parts[1]}".encode("utf-8")
        pk.verify(sig, signing_input)
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

    fp = payload.get("fp")
    if expected_fingerprint and fp != expected_fingerprint:
        meta["reason"] = "fingerprint_mismatch"
        meta["payload"] = payload
        return meta

    decision = (payload.get("dec") or "").upper()
    if decision not in DECISIONS:
        meta["reason"] = "invalid_decision"
        meta["payload"] = payload
        return meta

    if consume and decision == "GO":
        jti = str(payload.get("jti") or "").strip()
        red = _redeem_jti(jti=jti, fingerprint=str(fp or ""), rail=payload.get("rail"))
        if not red.get("ok"):
            meta["reason"] = red.get("reason") or "receipt_replay"
            meta["payload"] = payload
            meta["decision"] = decision
            return meta
        meta["redeemed"] = True
        meta["redeemed_at"] = red.get("redeemed_at")

    meta.update({"valid": True, "decision": decision, "payload": payload, "reason": None})
    return meta


def redeem_receipt_jwt(
    token: str,
    *,
    expected_fingerprint: str | None = None,
) -> dict:
    """Commit-path helper: verify + consume GO jti (one-shot)."""
    return verify_receipt_jwt(token, expected_fingerprint=expected_fingerprint, consume=True)


def evaluate(
    body: dict,
    *,
    account_id: str | None = None,
    public_url: str,
    fuse_hop: Callable[[str], dict | None] | None = None,
) -> dict:
    """Core evaluate — returns API response dict. Fail closed to NO_GO."""
    try:
        return _evaluate_inner(
            body if isinstance(body, dict) else {},
            account_id=account_id,
            public_url=public_url,
            fuse_hop=fuse_hop,
        )
    except Exception as exc:  # noqa: BLE001 — never GO on internal error
        eid = f"pf_{uuid.uuid4().hex}"
        return _response(
            evaluation_id=eid,
            rail="unknown",
            decision="NO_GO",
            fingerprint="",
            signals=["evaluate_error"],
            receipt=None,
            created_at=_iso(),
            public_url=public_url or "",
            halt=True,
            reason=f"evaluate_error:{type(exc).__name__}",
        )


def _evaluate_inner(
    body: dict,
    *,
    account_id: str | None,
    public_url: str,
    fuse_hop: Callable[[str], dict | None] | None,
) -> dict:
    rail = (body.get("rail") or "").strip().lower()
    transfer = body.get("transfer") if isinstance(body.get("transfer"), dict) else {}
    mandate = body.get("mandate") if isinstance(body.get("mandate"), dict) else {}
    context = body.get("context") if isinstance(body.get("context"), dict) else {}
    ttl = int(body.get("ttl_seconds") or mandate.get("ttl_seconds") or DEFAULT_TTL_SECONDS)
    agent_id = (
        mandate.get("agent_id") or body.get("agent_id") or context.get("agent_id") or ""
    ).strip() or None
    fuse_id = (mandate.get("fuse_id") or body.get("fuse_id") or "").strip() or None

    evaluation_id = f"pf_{uuid.uuid4().hex}"
    created_at = _iso()

    if rail not in RAILS:
        return _response(
            evaluation_id=evaluation_id,
            rail=rail or "unknown",
            decision="NO_GO",
            fingerprint="",
            signals=["unsupported_rail"],
            receipt=None,
            created_at=created_at,
            public_url=public_url,
            halt=True,
            reason="unsupported_rail",
        )

    fingerprint = transfer_fingerprint(rail=rail, transfer=transfer)
    decision, signals = _policy_signals(
        rail=rail, transfer=transfer, mandate=mandate, context=context
    )

    hop_meta = None
    if fuse_id:
        # fuse_id present ⇒ must prove LIVE. Missing hop, unreachable, or
        # ambiguous state/verdict is NO_GO — never GO by omission.
        if not fuse_hop:
            decision = "NO_GO"
            if "fuse_unverified" not in signals:
                signals.append("fuse_unverified")
        else:
            hop_meta = fuse_hop(fuse_id)
            if not isinstance(hop_meta, dict):
                decision = "NO_GO"
                if "fuse_unverified" not in signals:
                    signals.append("fuse_unverified")
            elif (
                hop_meta.get("halt")
                or hop_meta.get("verdict") is False
                or hop_meta.get("state") == "DEAD"
            ):
                decision = "NO_GO"
                if "fuse_dead" not in signals:
                    signals.append("fuse_dead")
            elif hop_meta.get("state") != "LIVE" or hop_meta.get("verdict") is not True:
                decision = "NO_GO"
                if "fuse_unverified" not in signals:
                    signals.append("fuse_unverified")

    # GO always requires a signed receipt — missing keys => NO_GO (incl. DEV_MODE).
    if not _signing_key():
        if decision == "GO":
            decision = "NO_GO"
        if "unsigned_halt" not in signals:
            signals.append("unsigned_halt")

    issuer = (
        (public_url or "").replace("https://", "").replace("http://", "").split("/")[0]
        or "gate.velaru.xyz"
    )
    receipt = mint_receipt_jwt(
        evaluation_id=evaluation_id,
        rail=rail,
        decision=decision,
        fingerprint=fingerprint,
        signals=signals,
        agent_id=agent_id,
        ttl_seconds=ttl,
        issuer=issuer,
    )

    if decision == "GO" and not receipt:
        decision = "NO_GO"
        if "unsigned_halt" not in signals:
            signals.append("unsigned_halt")

    if decision != "GO" and receipt and _signing_key():
        receipt = mint_receipt_jwt(
            evaluation_id=evaluation_id,
            rail=rail,
            decision=decision,
            fingerprint=fingerprint,
            signals=signals,
            agent_id=agent_id,
            ttl_seconds=ttl,
            issuer=issuer,
        )
    if decision == "NO_GO" and not _signing_key():
        receipt = None

    halt = decision != "GO"
    db = _db_mod()
    db.record_prefinality_evaluation(
        evaluation_id=evaluation_id,
        account_id=account_id,
        rail=rail,
        decision=decision,
        fingerprint=fingerprint,
        agent_id=agent_id,
        signals=signals,
        receipt_jwt=receipt,
        created_at=created_at,
    )

    return _response(
        evaluation_id=evaluation_id,
        rail=rail,
        decision=decision,
        fingerprint=fingerprint,
        signals=signals,
        receipt=receipt,
        created_at=created_at,
        public_url=public_url,
        halt=halt,
        hop=hop_meta,
        agent_id=agent_id,
        ttl_seconds=ttl,
    )


def _response(
    *,
    evaluation_id: str,
    rail: str,
    decision: str,
    fingerprint: str,
    signals: list[str],
    receipt: str | None,
    created_at: str,
    public_url: str,
    halt: bool,
    reason: str | None = None,
    hop: dict | None = None,
    agent_id: str | None = None,
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
) -> dict:
    base = (public_url or "").rstrip("/")
    out: dict[str, Any] = {
        "spec": SPEC,
        "evaluation_id": evaluation_id,
        "restraint_id": evaluation_id,
        "rail": rail,
        "decision": decision,
        "halt": halt,
        "signals": signals,
        "fingerprint": fingerprint,
        "receipt": receipt,
        "expires_in": ttl_seconds,
        "created_at": created_at,
        "verify_url": f"{base}/v1/prefinality/verify",
        "manifest": f"{base}/.well-known/prefinality.json",
        "clearance_only": True,
        "write_executed": False,
        "their_production": False,
        "receipt_one_shot": True,
    }
    if agent_id:
        out["agent_id"] = agent_id
    if reason:
        out["reason"] = reason
    if hop and isinstance(hop, dict):
        out["fuse_hop"] = {
            "state": hop.get("state"),
            "verdict": hop.get("verdict"),
            "halt": hop.get("halt"),
        }
    if decision == "GO":
        out["message"] = (
            "Pre-finality GO — rail may commit only if receipt verifies, "
            "is unexpired, and jti has not been redeemed."
        )
    elif decision == "HOLD":
        out["message"] = "Pre-finality HOLD — human review required before commit."
    else:
        out["message"] = "Pre-finality NO_GO — do not sign or send. Fail closed."
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
        "name": "Gate pre-finality clearance",
        "description": (
            "Rail-agnostic GO/NO-GO before irreversible commit. "
            "x402 (agent wallet sign) and RTP/FedNow (instant fiat credit) adapters share one receipt. "
            "GO receipts are single-use (jti consumed on commit-path verify)."
        ),
        "rails": [
            {
                "id": "x402",
                "status": "live",
                "hook": "before_wallet_sign",
                "currencies": ["USDC"],
                "evaluate": f"{base}/v1/prefinality/evaluate",
                "demo_evaluate": f"{base}/demo/prefinality/evaluate",
                "sdk": f"{base}/sdk/prefinality/wrap.mjs",
            },
            {
                "id": "rtp",
                "status": "adapter",
                "hook": "before_payment_order",
                "note": "FedNow and RTP abstract to payment_type=rtp on PSP APIs (e.g. Modern Treasury).",
                "currencies": ["USD"],
                "evaluate": f"{base}/v1/prefinality/evaluate",
                "verify": f"{base}/v1/prefinality/verify",
            },
        ],
        "evaluate": f"{base}/v1/prefinality/evaluate",
        "verify": f"{base}/v1/prefinality/verify",
        "jwks": f"{base}/.well-known/prefinality-jwks.json",
        "fail_closed": True,
        "receipt_one_shot": True,
        "receipt_ttl_seconds_default": DEFAULT_TTL_SECONDS,
        "decisions": list(DECISIONS),
        "their_production": False,
    }
