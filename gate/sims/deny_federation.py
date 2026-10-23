"""S13 Deny Federation STUB — local mouth consults foreign DENY for same digest.

Lab only. their_production is always False.
IN-PROCESS ONLY — no network, no HTTP, no sockets, no ledger product.

ForeignDenyStore is a dict in this process. Do not grow into a shared ledger.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from gate.sims.lab_invariant import stamp_lab_flag

# Hard rule: this module must never open a network path.
_FORBIDDEN_IMPORT_NAMES = frozenset(
    {
        "urllib",
        "urllib.request",
        "urllib3",
        "requests",
        "httpx",
        "aiohttp",
        "socket",
        "http.client",
        "http.server",
    }
)

SPEC = "nisaba-deny-federation-stub-lab-v1"
THEIR_PRODUCTION = False


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass
class ForeignDeny:
    digest: str
    source_mouth: str
    foreign_receipt_id: str
    receipt_class: str
    ts: float


@dataclass
class Store:
    foreign: dict[str, ForeignDeny] = field(default_factory=dict)  # digest -> deny
    receipts: dict[str, dict[str, Any]] = field(default_factory=dict)


STORE = Store()


def reset() -> None:
    STORE.foreign.clear()
    STORE.receipts.clear()


def assert_in_process_only() -> None:
    """Prove-time guard: this module must not import network clients."""
    import pathlib

    forbidden = ("urllib", "requests", "httpx", "aiohttp", "socket", "http.client")
    for line in pathlib.Path(__file__).read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith(("import ", "from ")):
            continue
        low = stripped.lower()
        for bad in forbidden:
            if bad in low:
                raise AssertionError(
                    f"deny_federation stub must stay in-process; found import line: {stripped!r}"
                )


def _receipt(
    decision: str,
    reason_code: str,
    *,
    digest: str | None = None,
    foreign_receipt_id: str | None = None,
    source_mouth: str | None = None,
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rid = str(uuid.uuid4())
    payload = {
        "spec": SPEC,
        "receipt_id": rid,
        "receipt_class": "clearance",  # local mouth decision
        "decision": decision,
        "reason_code": reason_code,
        "digest": digest,
        "foreign_block": foreign_receipt_id is not None and decision == "DENY",
        "foreign_receipt_id": foreign_receipt_id,
        "source_mouth": source_mouth,
        "result": result,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="deny_federation"),
        "ts": time.time(),
    }
    payload["receipt_hash"] = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
    STORE.receipts[rid] = payload
    return {**payload, "receipt_url": f"/v1/deny-fed/receipts/{rid}"}


def plant_foreign_deny(
    digest: str,
    *,
    source_mouth: str,
    foreign_receipt_id: str | None = None,
    receipt_class: str = "threat",
) -> dict[str, Any]:
    """In-process fixture only — simulates a stranger mouth's prior DENY."""
    assert_in_process_only()
    fid = foreign_receipt_id or str(uuid.uuid4())
    STORE.foreign[digest] = ForeignDeny(
        digest=digest,
        source_mouth=source_mouth,
        foreign_receipt_id=fid,
        receipt_class=receipt_class,
        ts=time.time(),
    )
    return {
        "digest": digest,
        "source_mouth": source_mouth,
        "foreign_receipt_id": fid,
        "receipt_class": receipt_class,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="deny_federation"),
    }


def check_digest(digest: str) -> dict[str, Any]:
    """Local mouth consult: foreign DENY for digest → local clearance DENY with link."""
    assert_in_process_only()
    hit = STORE.foreign.get(digest)
    if hit is None:
        return _receipt(
            "ALLOW",
            "no_foreign_deny",
            digest=digest,
            result={"foreign_hit": False},
        )
    return _receipt(
        "DENY",
        "foreign_deny",
        digest=digest,
        foreign_receipt_id=hit.foreign_receipt_id,
        source_mouth=hit.source_mouth,
        result={
            "foreign_hit": True,
            "foreign_receipt_class": hit.receipt_class,
            "foreign_receipt_id": hit.foreign_receipt_id,
        },
    )


def get_receipt(receipt_id: str) -> dict[str, Any] | None:
    r = STORE.receipts.get(receipt_id)
    if r is None:
        return None
    return {**r, "receipt_url": f"/v1/deny-fed/receipts/{receipt_id}"}
