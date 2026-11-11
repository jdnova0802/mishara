"""Item 161 — live-channel identity challenge binding.

Gates the instruction, not the later receipt. Out-of-band nonce,
never a biometric liveness test. claimed_identity_ref points at a
pre-registered callback contact. No exceptions column on the gate.
"""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

try:
    from gate import sanitize as sanitize_mod
except ImportError:
    import sanitize as sanitize_mod

SPEC = "gate-live-channel-v1"
CHANNELS = ("voice_call", "video_call")
OOB = ("callback_on_file", "federation_lookup", "law_firm_main_line")
INSTRUCTIONS = ("wire_transfer", "credential_disclosure", "contract_execution")
CHALLENGE_TTL_S = 300


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _now()).astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _path() -> Path:
    return Path(os.getenv("GATE_LIVE_CHANNEL_PATH") or Path(__file__).resolve().parent / "data" / "live_channel.json")


def _load() -> dict[str, Any]:
    path = _path()
    if not path.exists():
        return {"spec": SPEC, "contacts": [], "challenges": [], "instructions": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"spec": SPEC, "contacts": [], "challenges": [], "instructions": []}
    if not isinstance(data, dict):
        return {"spec": SPEC, "contacts": [], "challenges": [], "instructions": []}
    for key in ("contacts", "challenges", "instructions"):
        data.setdefault(key, [])
    return data


def _save(store: dict[str, Any]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")


def catalog() -> dict[str, Any]:
    store = _load()
    return {
        "spec": SPEC,
        "iso_30107_cited": False,
        "exceptions_column": False,
        "contacts": store["contacts"],
        "challenges": store["challenges"],
        "instructions": store["instructions"],
        "plain": "Callback must already be on file. A name spoken on the call is not an identity.",
    }


def register_contact(
    *,
    claimed_identity_ref: str,
    callback: str,
    legal_person: str,
) -> dict[str, Any]:
    ident = sanitize_mod.strip_agent(claimed_identity_ref, limit=200)
    cb = sanitize_mod.strip_agent(callback, limit=200)
    who = sanitize_mod.strip_agent(legal_person, limit=200)
    if not ident or not cb or not who:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "contact_required",
            "plain": "Pre-register a callback the attacker does not control. Never a spoken name.",
        }
    rec = {
        "spec": SPEC,
        "ok": True,
        "claimed_identity_ref": ident,
        "callback": cb,
        "legal_person": who,
        "agent_signatory": False,
        "registered_at": _iso(),
    }
    store = _load()
    store["contacts"] = [c for c in store["contacts"] if c.get("claimed_identity_ref") != ident]
    store["contacts"].append(rec)
    _save(store)
    return rec


def issue_challenge(
    *,
    claimed_identity_ref: str,
    channel: str,
    out_of_band_method: str = "callback_on_file",
) -> dict[str, Any]:
    ident = sanitize_mod.strip_agent(claimed_identity_ref, limit=200)
    ch = (channel or "").strip()
    method = (out_of_band_method or "").strip()
    if ch not in CHANNELS:
        return {"spec": SPEC, "ok": False, "error": "channel_unknown", "plain": "voice_call or video_call."}
    if method not in OOB:
        return {"spec": SPEC, "ok": False, "error": "oob_unknown"}
    store = _load()
    contact = next((c for c in store["contacts"] if c.get("claimed_identity_ref") == ident), None)
    if contact is None:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "identity_not_on_file",
            "plain": "No pre-registered callback. This would not have stopped an in-band impersonation.",
        }
    if method == "federation_lookup":
        return {
            "spec": SPEC,
            "ok": False,
            "error": "federation_not_built",
            "plain": "Item 160 is not a peer instance. Use callback_on_file.",
        }
    nonce = secrets.token_hex(16)
    now = _now()
    rec = {
        "spec": SPEC,
        "ok": True,
        "challenge_id": "lc_" + uuid.uuid4().hex[:12],
        "claimed_identity_ref": ident,
        "channel": ch,
        "challenge_nonce": nonce,
        "nonce_sha256": hashlib.sha256(nonce.encode()).hexdigest(),
        "issued_at": _iso(now),
        "expires_at": _iso(now + timedelta(seconds=CHALLENGE_TTL_S)),
        "response_verified": False,
        "out_of_band_method": method,
        "callback_used": contact["callback"],
        "verified_at": None,
        "plain": "Nonce issued on the registered callback path, not inside the call.",
    }
    store["challenges"].append(rec)
    _save(store)
    return rec


def respond(*, challenge_id: str, nonce: str) -> dict[str, Any]:
    store = _load()
    row = next((c for c in store["challenges"] if c.get("challenge_id") == (challenge_id or "").strip()), None)
    if not row:
        return {"spec": SPEC, "ok": False, "error": "challenge_not_found"}
    exp = datetime.fromisoformat(str(row["expires_at"]).replace("Z", "+00:00"))
    if _now() > exp:
        return {"spec": SPEC, "ok": False, "error": "challenge_expired", "plain": "Time-bound. Re-issue on the callback path."}
    if not secrets.compare_digest(str(row.get("challenge_nonce") or ""), nonce or ""):
        return {"spec": SPEC, "ok": False, "error": "nonce_mismatch", "plain": "In-band guess failed. Gate stays closed."}
    row["response_verified"] = True
    row["verified_at"] = _iso()
    row["plain"] = "Out-of-band response matched. Instruction gate may now bind to this challenge."
    _save(store)
    return {**row, "ok": True}


def gate_instruction(
    *,
    challenge_id: str,
    instruction_type: str,
    amount: str | None = None,
) -> dict[str, Any]:
    kind = (instruction_type or "").strip()
    if kind not in INSTRUCTIONS:
        return {"spec": SPEC, "ok": False, "error": "instruction_unknown"}
    store = _load()
    ch = next((c for c in store["challenges"] if c.get("challenge_id") == (challenge_id or "").strip()), None)
    if not ch or not ch.get("response_verified"):
        return {
            "spec": SPEC,
            "ok": False,
            "error": "passed_challenge_required",
            "plain": "No exceptions column. The high-value instruction does not run.",
        }
    rec = {
        "spec": SPEC,
        "ok": True,
        "instruction_id": "ins_" + uuid.uuid4().hex[:12],
        "challenge_id": ch["challenge_id"],
        "instruction_type": kind,
        "amount": sanitize_mod.strip_agent(amount, limit=40) or None,
        "created_at": _iso(),
        "plain": "Instruction bound to a passed out-of-band challenge.",
    }
    store["instructions"].append(rec)
    _save(store)
    return rec


def failure_events() -> list[dict[str, Any]]:
    return [c for c in _load()["challenges"] if not c.get("response_verified")]
