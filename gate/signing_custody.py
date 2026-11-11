"""Item 142 status — single-admin online key, named honestly.

A ceremony record can be filed. It cannot flip hsm or quorum to true
from this process. Those are ops facts, not JSON.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from gate import receipt as receipt_mod
except ImportError:
    import receipt as receipt_mod

try:
    from gate import sanitize as sanitize_mod
except ImportError:
    import sanitize as sanitize_mod

SPEC = "gate-signing-custody-v1"


def _iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _path() -> Path:
    return Path(os.getenv("GATE_CUSTODY_PATH") or Path(__file__).resolve().parent / "data" / "signing_custody.json")


def status() -> dict[str, Any]:
    fp = receipt_mod.receipt_public_key_fingerprint()
    return {
        "spec": SPEC,
        "single_admin": True,
        "online": True,
        "hsm": False,
        "quorum_m": None,
        "quorum_n": None,
        "fingerprint": fp,
        "configured": bool(fp),
        "env": "GATE_RECEIPT_PRIVATE_KEY",
        "plain": "One online Ed25519. DigiNotar-shaped until a ceremony happens outside this repo.",
    }


def record_ceremony(*, custodians: list[str], m: int, n: int, note: str) -> dict[str, Any]:
    names = [sanitize_mod.strip_agent(x, limit=80) for x in (custodians or []) if str(x).strip()]
    try:
        mm, nn = int(m), int(n)
    except (TypeError, ValueError):
        return {"spec": SPEC, "ok": False, "error": "m_of_n_numeric"}
    if not names or mm < 1 or nn < mm:
        return {"spec": SPEC, "ok": False, "error": "ceremony_incomplete"}
    rec = {
        "spec": SPEC,
        "ok": True,
        "custodians": names,
        "m": mm,
        "n": nn,
        "note": sanitize_mod.strip_agent(note, limit=400),
        "hsm": False,
        "quorum_active": False,
        "recorded_at": _iso(),
        "plain": "Intent recorded. Keys on Render did not move. Do not treat this row as an HSM.",
    }
    path = _path()
    store = {"spec": SPEC, "ceremonies": []}
    if path.exists():
        try:
            store = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            store = {"spec": SPEC, "ceremonies": []}
    store.setdefault("ceremonies", []).append(rec)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")
    return rec
