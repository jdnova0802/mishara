"""CHARGE authority — DEAD→LIVE / epoch unlock is not a free-form string.

Accepted authorities (first match wins):
1. Dev drill: GATE_DEV_MODE and charge_id matching chg_* (tests + lab only)
2. HMAC: charge_id = "sig:{nonce}:{hex_mac}"
   mac = HMAC_SHA256(GATE_CHARGE_SECRET|GATE_SECRET_KEY, "{purpose}|{subject}|{nonce}")
3. Paid Stripe/dev checkout session id already marked paid on an install_order
4. Stripe PaymentIntent id (pi_*) retrieved and status=succeeded (when Stripe configured)

Replay: each accepted charge_id may be consumed at most once.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import re
import secrets

try:
    from gate import db
except ImportError:
    import db

SPEC = "gate-charge-authority-v1"
REASON_REQUIRED = "charge_id_required"
REASON_INVALID = "charge_authority_invalid"
REASON_REPLAY = "charge_authority_replay"
REASON_UNCONFIGURED = "charge_authority_unconfigured"

_DEV_RE = re.compile(r"^chg_[A-Za-z0-9._:-]{1,120}$")
_SIG_RE = re.compile(r"^sig:([A-Za-z0-9._-]{8,64}):([A-Fa-f0-9]{64})$")
_PI_RE = re.compile(r"^pi_[A-Za-z0-9]+$")


def _dev_mode() -> bool:
    return os.getenv("GATE_DEV_MODE", "").strip().lower() in ("1", "true", "yes", "on")


def _secret() -> str:
    return (os.getenv("GATE_CHARGE_SECRET") or os.getenv("GATE_SECRET_KEY") or "").strip()


def normalize(raw) -> str | None:
    if raw is None:
        return None
    s = str(raw).strip()[:200]
    return s or None


def mint_hmac(*, purpose: str, subject: str, nonce: str | None = None) -> str | None:
    """Ops helper: mint a one-time charge token bound to purpose+subject."""
    secret = _secret()
    if not secret:
        return None
    n = (nonce or secrets.token_hex(8)).strip()[:64]
    body = f"{purpose}|{subject}|{n}".encode("utf-8")
    dig = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sig:{n}:{dig}"


def _verify_hmac(cid: str, *, purpose: str, subject: str | None) -> bool:
    m = _SIG_RE.match(cid)
    if not m:
        return False
    secret = _secret()
    if not secret:
        return False
    nonce, got = m.group(1), m.group(2)
    body = f"{purpose}|{(subject or '').strip()}|{nonce}".encode("utf-8")
    expect = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expect, got.lower())


def _stripe_pi_succeeded(charge_id: str) -> bool:
    key = (os.getenv("STRIPE_SECRET_KEY") or "").strip()
    if not key or not _PI_RE.match(charge_id):
        return False
    try:
        import stripe

        stripe.api_key = key
        pi = stripe.PaymentIntent.retrieve(charge_id)
        return getattr(pi, "status", None) == "succeeded"
    except Exception:
        return False


def verify(*, charge_id: str | None, purpose: str, subject: str | None = None) -> dict:
    """Verify charge_id is real authority for purpose (license|epoch)."""
    cid = normalize(charge_id)
    meta = {
        "spec": SPEC,
        "ok": False,
        "halt": True,
        "purpose": purpose,
        "subject": subject,
        "charge_id": cid,
        "authority": None,
    }
    if not cid:
        meta["reason"] = REASON_REQUIRED
        return meta

    if db.charge_authority_consumed(cid):
        meta["reason"] = REASON_REPLAY
        return meta

    if _dev_mode() and _DEV_RE.match(cid):
        meta.update({"ok": True, "halt": False, "authority": "dev_drill"})
        return meta

    if cid.startswith("sig:"):
        if not _secret():
            meta["reason"] = REASON_UNCONFIGURED
            return meta
        if _verify_hmac(cid, purpose=purpose, subject=subject):
            meta.update({"ok": True, "halt": False, "authority": "hmac_sig"})
            return meta
        meta["reason"] = REASON_INVALID
        return meta

    order = db.get_install_order_by_session(cid)
    if order and (order.get("status") or "") == "paid":
        meta.update({"ok": True, "halt": False, "authority": "paid_checkout"})
        return meta

    if _stripe_pi_succeeded(cid):
        meta.update({"ok": True, "halt": False, "authority": "stripe_pi"})
        return meta

    if not _dev_mode() and _DEV_RE.match(cid):
        meta["reason"] = REASON_INVALID
        meta["hint"] = "chg_* drill tokens only work in GATE_DEV_MODE"
        return meta

    meta["reason"] = REASON_INVALID
    return meta


def consume(*, charge_id: str, purpose: str, subject: str | None = None) -> None:
    cid = normalize(charge_id)
    if not cid:
        return
    db.consume_charge_authority(charge_id=cid, purpose=purpose, subject=subject or "")
