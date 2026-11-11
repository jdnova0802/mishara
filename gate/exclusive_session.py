"""R1 — exclusive-door session transcript.

One object: passed 161 challenge + covering 163 bond + policy transcript
+ absence proof + current signing fingerprint. Any rail fail → abort.
write_executed is always false here. Gate still does not do the write.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any

try:
    from gate import absence as absence_mod
except ImportError:
    import absence as absence_mod

try:
    from gate import exposure_bond as exposure_bond_mod
except ImportError:
    import exposure_bond as exposure_bond_mod

try:
    from gate import key_transparency as key_transparency_mod
except ImportError:
    import key_transparency as key_transparency_mod

try:
    from gate import live_channel as live_channel_mod
except ImportError:
    import live_channel as live_channel_mod

try:
    from gate import policy_transcript as policy_transcript_mod
except ImportError:
    import policy_transcript as policy_transcript_mod

SPEC = "gate-exclusive-session-v1"


def _iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def open_session(
    rows: list[dict[str, Any]],
    *,
    fuse_id: str,
    job_id: str,
    challenge_id: str,
    bond_id: str,
    amount: str,
    public_inputs: dict[str, Any] | None,
    t0: str,
    t1: str,
    media_evidence_claimed: Any = False,
) -> dict[str, Any]:
    rails: dict[str, Any] = {}
    abort: str | None = None

    store = live_channel_mod._load()
    ch = next((c for c in store["challenges"] if c.get("challenge_id") == (challenge_id or "").strip()), None)
    if not ch or not ch.get("response_verified"):
        rails["challenge"] = {"ok": False, "error": "passed_challenge_required"}
        abort = "challenge"
    else:
        rails["challenge"] = {"ok": True, "challenge_id": ch["challenge_id"], "method": ch.get("out_of_band_method")}

    if media_evidence_claimed in (True, 1, "1", "true", "yes"):
        rails["media"] = {"ok": False, "error": "media_is_not_evidence"}
        abort = abort or "media"
    else:
        rails["media"] = {"ok": True, "call_status": "untrusted_by_doctrine"}

    cover = exposure_bond_mod.covers(bond_id=bond_id or "", value_at_risk=amount)
    rails["bond"] = cover
    if not cover.get("covers"):
        abort = abort or "bond"

    policy = policy_transcript_mod.evaluate(public_inputs=public_inputs or {})
    rails["policy"] = {
        "ok": True,
        "verdict": policy["verdict"],
        "policy_hash": policy["policy_hash"],
        "transcript_sha256": policy["transcript_sha256"],
        "zk_circuit": False,
    }
    if policy["verdict"] == "BLOCK":
        abort = abort or "policy"

    absn = absence_mod.prove(rows, fuse_id=fuse_id, job_id=job_id, t0=t0, t1=t1)
    rails["absence"] = absn
    if not absn.get("absent"):
        abort = abort or "absence"

    eq = key_transparency_mod.equivocation()
    cur = key_transparency_mod.current()
    rails["keydir"] = {
        "ok": not eq.get("equivocation"),
        "equivocation": eq.get("equivocation"),
        "current": cur,
        "hsm": False,
    }
    if eq.get("equivocation"):
        abort = abort or "keydir"

    body = {
        "fuse_id": (fuse_id or "").strip(),
        "job_id": (job_id or "").strip(),
        "rails": {k: (v.get("ok") if isinstance(v, dict) else None) for k, v in rails.items()},
        "policy_hash": policy.get("policy_hash"),
        "absence_sha256": absn.get("statement_sha256"),
        "fingerprint": (cur or {}).get("fingerprint"),
        "abort": abort,
    }
    digest = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    rec = {
        "spec": SPEC,
        "ok": abort is None,
        "session_id": "xs_" + uuid.uuid4().hex[:12],
        "fuse_id": body["fuse_id"],
        "job_id": body["job_id"],
        "abort": abort,
        "rails": rails,
        "write_executed": False,
        "clearance_only": True,
        "session_sha256": digest,
        "opened_at": _iso(),
        "plain": (
            "Every rail cleared. This is still not the irreversible write."
            if abort is None
            else f"Aborted on {abort}. No ALLOW leaf should follow without breaking absence."
        ),
    }
    return rec
