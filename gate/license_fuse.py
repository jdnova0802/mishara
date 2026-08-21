"""License Fuse — the parent. Children cannot outlive it.

lookup exists. This mouth does not look up a directory and fail open.
If a hop names license_id, the parent must be LIVE to print a ticket,
and still LIVE to redeem it. DEAD → LIVE is CHARGE only.

Omit license_id and the scanner behaves as it does today.
Never license_number (that key is PII).
"""
from __future__ import annotations

import re

try:
    from gate import db
except ImportError:
    import db

try:
    from gate import epoch as epoch_mod
except ImportError:
    import epoch as epoch_mod

SPEC = "gate-license-fuse-v1"
REASON_REQUIRED = "license_id_required"
REASON_INVALID = "license_id_invalid"
REASON_NOT_LIVE = "license_parent_not_live"
REASON_MISMATCH = "license_parent_mismatch"
REASON_CHARGE_REQUIRED = "charge_id_required"
STATES = ("UNSIGNED", "LIVE", "ARMED", "DEAD")
_ID_RE = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")


def normalize_id(raw) -> str | None:
    if raw is None:
        return None
    s = str(raw).strip()[:128]
    if not s or not _ID_RE.match(s):
        return None
    return s


def snapshot(license_id: str | None) -> dict:
    lid = normalize_id(license_id)
    meta = {
        "spec": SPEC,
        "fused": False,
        "license_id": lid,
        "state": None,
        "stored": None,
        "charge_id": None,
        "outstanding_tickets": 0,
        "children_cannot_outlive_parent": True,
        "resurrection": "CHARGE only",
        "not_admin_charge": True,
    }
    if not lid:
        return meta
    row = db.get_license_parent(lid)
    stored = (row or {}).get("state") or "UNSIGNED"
    outstanding = db.count_unconsumed_tickets_for_license(lid)
    public = "ARMED" if stored == "LIVE" and outstanding else stored
    meta.update(
        {
            "fused": True,
            "state": public,
            "stored": stored,
            "charge_id": (row or {}).get("charge_id"),
            "outstanding_tickets": outstanding,
        }
    )
    return meta


def presented(raw) -> dict:
    """Empty/omitted → not fused. Non-empty invalid id → fail closed. Else require LIVE."""
    if raw is None:
        return {"ok": True, "fused": False, "state": None, "license_id": None}
    s = str(raw).strip()
    if not s:
        return {"ok": True, "fused": False, "state": None, "license_id": None}
    lid = normalize_id(s)
    if not lid:
        return {"ok": False, "fused": True, "reason": REASON_INVALID, "license_id": None, "state": None}
    return require_live(lid)


def require_live(license_id: str | None) -> dict:
    """Omitted license_id is not fused. Present license_id must be stored LIVE."""
    lid = normalize_id(license_id)
    if not lid:
        return {"ok": True, "fused": False, "state": None, "license_id": None}
    snap = snapshot(lid)
    stored = snap.get("stored") or "UNSIGNED"
    if stored != "LIVE":
        return {
            "ok": False,
            "fused": True,
            "state": snap.get("state") or stored,
            "stored": stored,
            "license_id": lid,
            "reason": REASON_NOT_LIVE,
        }
    return {
        "ok": True,
        "fused": True,
        "state": snap.get("state") or "LIVE",
        "stored": "LIVE",
        "license_id": lid,
    }


def charge(*, license_id: str | None, charge_id: str | None) -> dict:
    """The only path UNSIGNED/DEAD → LIVE. Verified charge authority required."""
    try:
        from gate import charge_authority as charge_mod
    except ImportError:
        import charge_authority as charge_mod

    lid = normalize_id(license_id)
    cid = charge_mod.normalize(charge_id)
    if not lid:
        return {"ok": False, "halt": True, "reason": REASON_REQUIRED, "state": None}
    auth = charge_mod.verify(charge_id=cid, purpose="license", subject=lid)
    if not auth.get("ok"):
        return {
            "ok": False,
            "halt": True,
            "reason": auth.get("reason") or REASON_CHARGE_REQUIRED,
            "state": (snapshot(lid).get("stored") or "UNSIGNED"),
            "license_id": lid,
            "charge_authority": auth,
        }
    charge_mod.consume(charge_id=cid, purpose="license", subject=lid)
    db.upsert_license_parent(license_id=lid, state="LIVE", charge_id=cid)
    return {
        "ok": True,
        "halt": False,
        "license_id": lid,
        "state": "LIVE",
        "stored": "LIVE",
        "charge_id": cid,
        "charge_authority": auth.get("authority"),
        "spec": SPEC,
        "resurrection": "CHARGE only",
    }


def dead(*, license_id: str | None) -> dict:
    """Blow the parent. Outstanding tickets cannot redeem until CHARGE."""
    lid = normalize_id(license_id)
    if not lid:
        return {"ok": False, "halt": True, "reason": REASON_REQUIRED, "state": None}
    prior = db.get_license_parent(lid) or {}
    db.upsert_license_parent(
        license_id=lid,
        state="DEAD",
        charge_id=prior.get("charge_id"),
    )
    return {
        "ok": True,
        "halt": False,
        "license_id": lid,
        "state": "DEAD",
        "stored": "DEAD",
        "spec": SPEC,
        "children_cannot_outlive_parent": True,
        "outstanding_tickets": db.count_unconsumed_tickets_for_license(lid),
        "resurrection": "CHARGE only",
    }


def spec(public_url: str) -> dict:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "License Fuse",
        "what": "Parent permission. Children (tickets) cannot outlive it.",
        "not": [
            "iGregulator",
            "BMM BOAT",
            "a license directory that fails open",
            "OCSP in a browser",
            "license_number",
            "a second bind-only write",
        ],
        "pas_key": "license_id",
        "children_cannot_outlive_parent": True,
        "omit": "No license_id → current scanner behavior.",
        "states": list(STATES),
        "stored_states": ["UNSIGNED", "LIVE", "DEAD"],
        "armed": "LIVE parent with at least one unredeemed child ticket.",
        "issue": "license_id present → parent must be stored LIVE or the hop is HALT and no ticket prints.",
        "redeem": "Ticket remembers license_id. Parent must still be LIVE. Parent DEAD does not consume the ticket.",
        "charge": {
            "path": f"{base}/v1/pas/licenses/{{license_id}}/charge",
            "demo": f"{base}/demo/pas/licenses/{{license_id}}/charge",
            "required": ["charge_id"],
            "from": ["UNSIGNED", "DEAD"],
            "to": "LIVE",
            "not_admin_charge": True,
        },
        "dead": {
            "path": f"{base}/v1/pas/licenses/{{license_id}}/dead",
            "demo": f"{base}/demo/pas/licenses/{{license_id}}/dead",
            "to": "DEAD",
        },
        "married_write": "POST /job/v1/jobs/{job_id}/bind-only",
        "counterpart": f"{base}/.well-known/license-fuse.json#counterpart",
        "restraint": f"{base}/.well-known/restraint.json",
        "commit_auth": f"{base}/.well-known/commit-auth.json",
        "their_production": False,
    }
