"""Pre-finality clearance — GO/NO-GO before irreversible commit (x402, RTP).

Rail-agnostic evaluate contract:
  POST body → decision + signed JWT receipt bound to transfer fingerprint.

Fail-closed: missing fields, policy breach, fuse DEAD, or unsigned receipt in prod → NO_GO.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

try:
    from gate import receipt as receipt_mod
except ImportError:
    import receipt as receipt_mod

try:
    from gate import claim_scope as claim_scope_mod
except ImportError:
    import claim_scope as claim_scope_mod

try:
    from gate import write_state as write_state_mod
except ImportError:
    import write_state as write_state_mod

SPEC = "gate-prefinality-v1"
RAILS = ("x402", "rtp", "issuing", "oct")
DECISIONS = ("GO", "NO_GO", "HOLD")
DEFAULT_TTL_SECONDS = 300

_EVM_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")
_ROUTING_RE = re.compile(r"^\d{9}$")
_ACCOUNT_RE = re.compile(r"^\d{4,17}$")


def _dev_mode() -> bool:
    return os.getenv("GATE_DEV_MODE", "").strip().lower() in ("1", "true", "yes", "on")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat()


def recorded_at_z(value: Any) -> str | None:
    """UTC stamp as `...Z` so a stranger does not have to parse +00:00."""
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        dt = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(int(value), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    s = str(value).strip()
    if s.endswith("+00:00"):
        return s[:-6] + "Z"
    return s or None


def expired_receipt_copy(*, decision: str | None, recorded_at: str | None) -> str:
    """TTL expiry is not a decline. Keep the stored/signed decision on the copy."""
    dec = (decision or "").strip().upper() or "UNKNOWN"
    stamp = recorded_at_z(recorded_at)
    if stamp:
        return f"expired (decision was {dec}, recorded {stamp})"
    return f"expired (decision was {dec})"


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def signing_required() -> bool:
    return receipt_mod.signing_required()


def _signing_key(demo: bool = False):
    """Prod key by default. Demo receipts use the separate demo key when provisioned,
    else fall back to the prod key (still marked via the demo=true payload flag)."""
    if demo:
        demo_key = receipt_mod._ed25519_demo_signing_key()
        if demo_key is not None:
            return demo_key
    return receipt_mod._ed25519_signing_key()


def _public_key_bytes() -> bytes | None:
    return receipt_mod._ed25519_public_key_bytes()


def _demo_public_key_bytes() -> bytes | None:
    return receipt_mod._ed25519_demo_public_key_bytes()


def key_id(demo: bool = False) -> str | None:
    fp = (
        receipt_mod.demo_public_key_fingerprint()
        if demo and receipt_mod.demo_signing_configured()
        else receipt_mod.receipt_public_key_fingerprint()
    )
    return f"gate-prefinality-{fp}" if fp else None


def upstream_id(transfer: dict | None) -> str:
    """Bank or processor id for this write. Aliases stay one field in the fingerprint."""
    t = transfer if isinstance(transfer, dict) else {}
    for key in ("upstream_id", "payment_id", "instruction_id", "authorization_id"):
        raw = t.get(key)
        if raw is None:
            continue
        text = str(raw).strip()
        if text:
            return text[:128]
    return ""


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
    cp = (t.get("counterparty") or t.get("payto") or t.get("payTo") or "").strip()
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
    uid = upstream_id(t)
    if uid:
        out["upstream_id"] = uid
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
    t = _normalize_transfer(rail, transfer if isinstance(transfer, dict) else {})
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
        has_bank = bool(transfer.get("routing_number") and transfer.get("account_number"))
        if not has_ext and not has_bank:
            errors.append("rtp_counterparty_required")
        if transfer.get("routing_number") and not _ROUTING_RE.match(str(transfer["routing_number"]).strip()):
            errors.append("invalid_routing_number")
        if transfer.get("account_number") and not _ACCOUNT_RE.match(re.sub(r"\D", "", str(transfer["account_number"]))):
            errors.append("invalid_account_number")
    elif rail == "issuing":
        if currency not in ("", "USD", "USDC"):
            errors.append("unsupported_currency")
        if not cp:
            errors.append("invalid_counterparty")
    elif rail == "oct":
        if currency not in ("", "USD", "USDC"):
            errors.append("unsupported_currency")
        if not cp:
            errors.append("invalid_counterparty")
    return errors


def _policy_signals(
    *,
    rail: str,
    transfer: dict,
    mandate: dict | None,
    context: dict | None,
) -> tuple[str, list[str]]:
    """Return decision + signal codes."""
    signals: list[str] = []
    mandate = mandate if isinstance(mandate, dict) else {}
    context = context if isinstance(context, dict) else {}
    t = transfer if isinstance(transfer, dict) else {}

    errors = _validate_transfer(rail, t)
    if errors:
        return "NO_GO", errors

    amount = _parse_amount(t.get("amount"))
    max_amount = _parse_amount(mandate.get("max_amount") or mandate.get("max_payment"))

    # Card/push rails must carry a spend bound. A card with no Gate mandate
    # (no per-auth cap and no daily cap) fails closed — never a blanket approve.
    if rail in ("issuing", "oct"):
        daily_cap_present = _parse_amount(mandate.get("daily_cap")) is not None
        if max_amount is None and not daily_cap_present:
            signals.append("mandate_required")
            return "NO_GO", signals

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
        # Soft signal only when intent is declared but doesn't match untrusted source.
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

    if not upstream_id(t):
        signals.append("upstream_id_required")
        return "NO_GO", signals

    return "GO", signals


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
    claim_scope: dict | None = None,
    demo: bool = False,
) -> str | None:
    key = _signing_key(demo=demo)
    if not key:
        return None
    now = _utc_now()
    exp = now + timedelta(seconds=max(30, min(int(ttl_seconds or DEFAULT_TTL_SECONDS), 3600)))
    kid = key_id(demo=demo)
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
        "sig": signals,
    }
    # Demo/dogfood receipts are signed (stranger-verifiable) but must never action a
    # live rail. Live gates (e.g. RTP) refuse any receipt carrying demo=true.
    if demo:
        payload["demo"] = True
    # Scope of the negative/clearance claim — inside the signed JWT, not implied by endpoint.
    if claim_scope:
        payload["scope"] = claim_scope
    header = {"alg": "EdDSA", "typ": "JWT", "kid": kid}
    header_b64 = _b64url(_canonical_json(header).encode("utf-8"))
    payload_b64 = _b64url(_canonical_json(payload).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    sig = key.sign(signing_input)
    return f"{header_b64}.{payload_b64}.{_b64url(sig)}"


def verify_receipt_jwt(token: str, *, expected_fingerprint: str | None = None) -> dict:
    meta = {
        "spec": SPEC,
        "valid": False,
        "decision": None,
        "reason": None,
        "payload": None,
        "demo": False,
        "jti": None,
        "key_class": None,
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

    prod_pub = _public_key_bytes()
    demo_pub = _demo_public_key_bytes()
    if not prod_pub and not demo_pub:
        meta["reason"] = "verify_unconfigured"
        return meta
    # Try the production key first, then the demo key. key_class records which signed
    # it so live rails can refuse demo-key receipts regardless of the demo payload flag.
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    signing_input = f"{parts[0]}.{parts[1]}".encode("utf-8")
    key_class = None
    for candidate, klass in ((prod_pub, "prod"), (demo_pub, "demo")):
        if not candidate:
            continue
        try:
            Ed25519PublicKey.from_public_bytes(candidate).verify(sig, signing_input)
            key_class = klass
            break
        except Exception:
            continue
    if key_class is None:
        meta["reason"] = "bad_signature"
        return meta
    meta["key_class"] = key_class

    if header.get("alg") != "EdDSA":
        meta["reason"] = "unsupported_alg"
        return meta

    exp = payload.get("exp")
    if exp is not None and int(exp) < int(_utc_now().timestamp()):
        meta["reason"] = "expired"
        meta["payload"] = payload
        decision = (payload.get("dec") or "").upper()
        if decision in DECISIONS:
            meta["decision"] = decision
        scope = payload.get("scope") if isinstance(payload.get("scope"), dict) else {}
        recorded = recorded_at_z(scope.get("as_of")) if scope else None
        if not recorded and payload.get("iat") is not None:
            recorded = recorded_at_z(payload.get("iat"))
        meta["message"] = expired_receipt_copy(decision=decision or None, recorded_at=recorded)
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

    meta.update(
        {
            "valid": True,
            "decision": decision,
            "payload": payload,
            "reason": None,
            # Demo if the payload says so OR it was signed by the demo key. Either
            # one is enough for a live rail to refuse it.
            "demo": bool(payload.get("demo")) or meta.get("key_class") == "demo",
            "jti": payload.get("jti"),
        }
    )
    return meta


def evaluate(
    body: dict,
    *,
    account_id: str | None = None,
    public_url: str,
    fuse_hop: Callable[[str], dict | None] | None = None,
    demo: bool = False,
) -> dict:
    """Core evaluate — returns API response dict."""
    rail = (body.get("rail") or "").strip().lower()
    transfer = body.get("transfer") if isinstance(body.get("transfer"), dict) else {}
    mandate = body.get("mandate") if isinstance(body.get("mandate"), dict) else {}
    context = body.get("context") if isinstance(body.get("context"), dict) else {}
    ttl = int(body.get("ttl_seconds") or mandate.get("ttl_seconds") or DEFAULT_TTL_SECONDS)
    agent_id = (mandate.get("agent_id") or body.get("agent_id") or context.get("agent_id") or "").strip() or None
    fuse_id = (mandate.get("fuse_id") or body.get("fuse_id") or "").strip() or None

    evaluation_id = f"pf_{uuid.uuid4().hex}"
    created_at = _iso(_utc_now())

    if rail not in RAILS:
        scope = claim_scope_mod.for_go(
            rail=rail or "unknown",
            decision="NO_GO",
            signals=["unsupported_rail"],
            fingerprint="",
            as_of=created_at,
        )
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
            claim_scope=scope,
        )

    fingerprint = transfer_fingerprint(rail=rail, transfer=transfer)
    decision, signals = _policy_signals(rail=rail, transfer=transfer, mandate=mandate, context=context)

    hop_meta = None
    if fuse_id and fuse_hop:
        hop_meta = fuse_hop(fuse_id)
        if isinstance(hop_meta, dict):
            if hop_meta.get("halt") or hop_meta.get("verdict") is False or hop_meta.get("state") == "DEAD":
                decision = "NO_GO"
                if "fuse_dead" not in signals:
                    signals.append("fuse_dead")

    authorization_id = (
        (transfer.get("authorization_id") or context.get("stripe_authorization_id") or "").strip()
        or None
    )
    amount_val = _parse_amount(transfer.get("amount"))
    # Rolling spend window for card/push rails — the daily_cap is a true 24h sum,
    # not a per-transaction limit (a card could otherwise approve the cap repeatedly).
    if rail in ("issuing", "oct") and decision == "GO" and not demo:
        daily_cap = _parse_amount(mandate.get("daily_cap"))
        if daily_cap is not None and amount_val is not None and agent_id:
            try:
                from gate import db as _db
            except ImportError:
                import db as _db
            window_start = _iso(_utc_now() - timedelta(hours=24))
            prior = _db.approved_amount_in_window(
                agent_id=agent_id,
                rail=rail,
                since=window_start,
                exclude_authorization_id=authorization_id,
            )
            if prior + amount_val > daily_cap:
                decision = "NO_GO"
                if "daily_cap_exceeded" not in signals:
                    signals.append("daily_cap_exceeded")

    if signing_required() and not _signing_key():
        decision = "NO_GO"
        signals.append("unsigned_halt")

    scope = claim_scope_mod.for_go(
        rail=rail,
        decision=decision,
        signals=signals,
        fingerprint=fingerprint,
        as_of=created_at,
    )
    # Counterparty boundary when presented — part of signed scope.
    cp = (transfer.get("counterparty") or transfer.get("payto") or transfer.get("payTo") or "").strip()
    if cp:
        scope["counterparties"] = [cp]
        expected = (mandate.get("expected_counterparty") or "").strip()
        if expected:
            scope["keys_checked"]["expected_counterparty"] = expected

    receipt = mint_receipt_jwt(
        evaluation_id=evaluation_id,
        rail=rail,
        decision=decision,
        fingerprint=fingerprint,
        signals=signals,
        agent_id=agent_id,
        ttl_seconds=ttl,
        issuer=public_url.replace("https://", "").replace("http://", "").split("/")[0] or "gate.velaru.xyz",
        claim_scope=scope,
        demo=demo,
    )

    if signing_required() and not receipt:
        decision = "NO_GO"
        signals.append("unsigned_halt")

    halt = decision != "GO"
    try:
        from gate import db
    except ImportError:
        import db

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
        amount=amount_val,
        currency=(transfer.get("currency") or "").strip().upper() or None,
        counterparty=cp or None,
        authorization_id=authorization_id,
        card_id=(context.get("card_id") or "").strip() or None,
        merchant_category=(transfer.get("merchant_category") or "").strip() or None,
        event_id=(context.get("event_id") or "").strip() or None,
        mandate=mandate if isinstance(mandate, dict) else None,
        demo=demo,
    )

    log_stamp = None
    if receipt:
        try:
            from gate import seal_anchor as seal_anchor_mod
        except ImportError:
            import seal_anchor as seal_anchor_mod
        try:
            log_stamp = seal_anchor_mod.log_stamp(receipt)
        except Exception:
            log_stamp = None
        if log_stamp:
            try:
                db.record_clearance_stamp(
                    evaluation_id=evaluation_id,
                    receipt_hash=log_stamp["leaf_hash"],
                    upstream_id=upstream_id(transfer),
                    created_at=created_at,
                )
            except Exception:
                pass

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
        claim_scope=scope,
        log_stamp=log_stamp,
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
    claim_scope: dict | None = None,
    log_stamp: dict | None = None,
) -> dict:
    base = (public_url or "").rstrip("/")
    write_state = write_state_mod.for_clearance_mouth(decision=decision, rail=rail)
    out = {
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
        "write_state": write_state,
        "their_production": False,
    }
    if log_stamp:
        out["log_stamp"] = log_stamp
    if claim_scope:
        out["claim_scope"] = claim_scope
    if agent_id:
        out["agent_id"] = agent_id
    if reason:
        out["reason"] = reason
    if hop:
        out["fuse_hop"] = {
            "state": hop.get("state"),
            "verdict": hop.get("verdict"),
            "halt": hop.get("halt"),
        }
    if decision == "GO":
        out["message"] = "Pre-finality GO — rail may commit only if receipt verifies and is unexpired."
    elif decision == "HOLD":
        out["message"] = "Pre-finality HOLD — human review required before commit."
    else:
        out["message"] = "Pre-finality NO_GO — do not sign or send. Fail closed."
    # Sign negative clearance claims as a stranger-verifiable envelope (JWT already holds scope).
    if decision in ("NO_GO", "HOLD") and claim_scope:
        out = claim_scope_mod.attach(
            {**out, "word": decision},
            scope=claim_scope,
            force=True,
        )
    return out


def jwks() -> dict:
    keys = []
    prod_pub = _public_key_bytes()
    prod_kid = key_id()
    if prod_pub and prod_kid:
        keys.append(
            {
                "kty": "OKP",
                "crv": "Ed25519",
                "kid": prod_kid,
                "x": _b64url(prod_pub),
                "use": "sig",
                "alg": "EdDSA",
            }
        )
    # Publish the demo key too (when provisioned) so strangers can still verify demo
    # receipts — they are signed, just not trusted by live rails.
    if receipt_mod.demo_signing_configured():
        demo_pub = _demo_public_key_bytes()
        demo_kid = key_id(demo=True)
        if demo_pub and demo_kid:
            keys.append(
                {
                    "kty": "OKP",
                    "crv": "Ed25519",
                    "kid": demo_kid,
                    "x": _b64url(demo_pub),
                    "use": "sig",
                    "alg": "EdDSA",
                    "gate_key_class": "demo",
                }
            )
    return {"keys": keys}


def manifest(public_url: str) -> dict:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Gate pre-finality clearance",
        "description": (
            "Rail-agnostic GO/NO-GO before irreversible commit. "
            "x402 (agent wallet sign), RTP/FedNow (instant fiat credit), "
            "Stripe Issuing (agent card auth), and inbound OCT/Fast Funds "
            "sink clearance share one receipt."
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
            {
                "id": "issuing",
                "status": "live",
                "hook": "issuing_authorization.request",
                "note": "Stripe Issuing agent cards — Gate is AUTHORIZE/DECLINE mouth only.",
                "currencies": ["USD"],
                "evaluate": f"{base}/v1/prefinality/evaluate",
                "mouth": f"{base}/v1/issuing/authorization",
                "dogfood": f"{base}/demo/issuing/mouth",
                "verify": f"{base}/v1/prefinality/verify",
            },
            {
                "id": "oct",
                "status": "live",
                "hook": "before_accept_inbound_oct",
                "note": (
                    "Visa Original Credit / Fast Funds receive — Gate Clear before "
                    "the program treats an inbound push as intentional. Receive fees "
                    "are Visa IRF schedule ($0.29 / Fast Funds $0.60); Gate does not collect."
                ),
                "currencies": ["USD"],
                "evaluate": f"{base}/v1/prefinality/evaluate",
                "mouth": f"{base}/v1/sink/oct",
                "dogfood": f"{base}/demo/sink/mouth",
                "verify": f"{base}/v1/prefinality/verify",
            },
        ],
        "evaluate": f"{base}/v1/prefinality/evaluate",
        "verify": f"{base}/v1/prefinality/verify",
        "jwks": f"{base}/.well-known/prefinality-jwks.json",
        "upstream_id": {
            "required_for": "GO",
            "aliases": ["upstream_id", "payment_id", "instruction_id", "authorization_id"],
            "plain": "The bank or processor id for this write. It is inside the fingerprint.",
        },
        "log_stamp": {
            "spec": "gate-log-stamp-v1",
            "plain": "sha256 of the receipt JWT. tree_size and log_id fill when that leaf is in a published seal root.",
        },
        "fail_closed": True,
        "receipt_ttl_seconds_default": DEFAULT_TTL_SECONDS,
        "decisions": list(DECISIONS),
        "their_production": False,
    }
