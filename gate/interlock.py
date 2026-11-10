"""Item 119 — IEC 61511 interlock: sensor → logic solver → final element.

Borrowed from 61511: a scheduled, logged proof-test that BLOCK still trips.
SIL is unset — there is no HAZOP/LOPA on file. Voting is item 21 (triple vote),
not a 2-of-2 sensor pair we do not run.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from gate import receipt as receipt_mod
except ImportError:
    import receipt as receipt_mod

try:
    from gate import triple_vote as triple_vote_mod
except ImportError:
    import triple_vote as triple_vote_mod

SPEC = "gate-iec-61511-interlock-v1"
PROOF_SPEC = "gate-block-proof-test-v1"
FUSE = "gate-interlock"

# IEC 61511 names. These are role labels, not a claimed SIL rating.
SENSOR = "Erra"
LOGIC_SOLVER = "Gate"
FINAL_ELEMENT = "write-block"

KNOWN_TRIP_HOP = {
    "halt": True,
    "state": "DEAD",
    "verdict": False,
    "reason": "proof_test_trip",
    "kind": "block_proof_test",
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _now()).astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _path() -> Path:
    return Path(os.getenv("GATE_PROOF_TEST_PATH") or Path(__file__).resolve().parent / "data" / "proof_tests.json")


def _load() -> dict[str, Any]:
    path = _path()
    if not path.exists():
        return {"spec": PROOF_SPEC, "drills": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"spec": PROOF_SPEC, "drills": []}
    if not isinstance(data, dict):
        return {"spec": PROOF_SPEC, "drills": []}
    data.setdefault("drills", [])
    return data


def _save(store: dict[str, Any]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")


def interval_hours() -> float | None:
    """Operator-set interval. Unset is honest — not a SIL-derived demo number."""
    raw = (os.getenv("GATE_PROOF_TEST_INTERVAL_HOURS") or "").strip()
    if not raw:
        return None
    try:
        value = float(raw)
    except ValueError:
        return None
    if value <= 0:
        return None
    return value


def architecture() -> dict[str, Any]:
    return {
        "spec": SPEC,
        "grounding": "IEC 61511 — sensor → logic solver → final element; voting; SIL; proof-test interval.",
        "citation": "https://webstore.iec.ch/publication/5527",
        "sensor": {
            "name": SENSOR,
            "role": "sensor",
            "voting": "item 21 triple_vote (three independent graders must agree)",
            "vote_spec": triple_vote_mod.SPEC,
            "not": "2-of-2 physical sensors. We do not run that pair.",
        },
        "logic_solver": {"name": LOGIC_SOLVER, "role": "logic_solver"},
        "final_element": {
            "name": FINAL_ELEMENT,
            "role": "final_element",
            "meaning": "BLOCK sets acted=false. No spend write.",
        },
        "sil": None,
        "sil_named": False,
        "hazard_analysis": False,
        "proof_test_interval_hours": interval_hours(),
        "unanimous_block_possible": False,
        "unanimous_block_note": (
            "Item 21's circuit grader votes HOLD when open and ALLOW when closed. "
            "It has no BLOCK ballot, so 3-of-3 BLOCK cannot fire on a healthy circuit. "
            "The final-element trip is write-block: result is not ALLOW."
        ),
        "plain": (
            "Erra senses, Gate solves, write-block is the final element. "
            "SIL is unset until a hazard analysis exists. "
            "An untested trip is assumed failed."
        ),
    }


def list_drills() -> list[dict[str, Any]]:
    return list(_load().get("drills") or [])


def last_drill() -> dict[str, Any] | None:
    drills = list_drills()
    return drills[-1] if drills else None


def overdue(*, now: datetime | None = None) -> bool:
    last = last_drill()
    if last is None or not (last.get("write_blocked") or last.get("tripped")):
        return True
    hours = interval_hours()
    if hours is None:
        return False
    ran = str(last.get("tested_at") or "")
    try:
        tested = datetime.fromisoformat(ran.replace("Z", "+00:00"))
    except ValueError:
        return True
    age_h = ((_now() if now is None else now) - tested.astimezone(timezone.utc)).total_seconds() / 3600.0
    return age_h > hours


def status() -> dict[str, Any]:
    last = last_drill()
    untested = last is None
    late = overdue()
    tripped = bool((last or {}).get("write_blocked") or (last or {}).get("tripped"))
    assumed_failed = untested or late or not tripped
    return {
        "spec": PROOF_SPEC,
        "architecture": architecture(),
        "last_drill": last,
        "untested": untested,
        "overdue": late,
        "assumed_failed": assumed_failed,
        "plain": (
            "No logged BLOCK drill — trip assumed failed."
            if untested
            else (
                "Last BLOCK drill is overdue — trip assumed failed."
                if late
                else (
                    "Last drill did not trip — trip assumed failed."
                    if assumed_failed
                    else "Last logged drill tripped BLOCK. Write did not go through."
                )
            )
        ),
    }


def _trip_vote() -> dict[str, Any]:
    return triple_vote_mod.grade(
        hop=KNOWN_TRIP_HOP,
        plan={"reasons": ["proof_test_trip"], "result": "BLOCK", "halt": True},
        breaker={"open": False},
    )


def run_proof_test(*, verify_url: str = "", persist: bool = True) -> dict[str, Any]:
    """Exercise the real vote path with a known-BLOCK hop. Record whether write blocked."""
    vote = _trip_vote()
    result = str(vote.get("result") or "")
    hard_trip = bool(vote.get("agreed") and result == "BLOCK")
    write_blocked = result in ("BLOCK", "HOLD") and result != "ALLOW"
    tripped = write_blocked
    tested_at = _iso()
    event_id = "proof-test:" + uuid.uuid4().hex[:12]
    issued = receipt_mod.issue_receipt(
        event_id=event_id,
        fuse_id=FUSE,
        job_id=None,
        decision=result or "HOLD",
        acted=False,
        verify_url=verify_url or None,
        created_at=tested_at,
        hop={
            **KNOWN_TRIP_HOP,
            "tripped": tripped,
            "write_blocked": write_blocked,
            "hard_trip": hard_trip,
        },
        prev_receipt_hash=(last_drill() or {}).get("receipt_hash"),
    )
    rec = {
        "spec": PROOF_SPEC,
        "drill_id": event_id,
        "tested_at": tested_at,
        "tripped": tripped,
        "hard_trip": hard_trip,
        "write_blocked": write_blocked,
        "acted": False,
        "vote": vote,
        "receipt_hash": issued.get("receipt_hash"),
        "receipt_signature": issued.get("receipt_signature"),
        "receipt_public_key_fingerprint": issued.get("receipt_public_key_fingerprint"),
        "sil": None,
        "ok": write_blocked,
        "plain": (
            "Write-block tripped (vote "
            + result
            + "). Unanimous BLOCK is not available while the circuit grader has no BLOCK ballot."
            if write_blocked
            else "Proof-test failed: known-BLOCK hop yielded ALLOW. Assumed failed."
        ),
    }
    if persist:
        store = _load()
        store["drills"].append(rec)
        _save(store)
    return rec
