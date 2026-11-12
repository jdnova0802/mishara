"""Z3 IANA Root Zone Change Mouth — lab mouth: intent ≠ root-zone write.

Lab only. their_production is always False.
Not a DNS product. Not DNSSEC monitoring SaaS.
Gates DS/NS root-zone changes behind PTI-shaped tech checks.
"""

from __future__ import annotations

import hashlib
import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from gate.sims.lab_invariant import stamp_lab_flag
from gate.sims.logos import canonical


SPEC = "nisaba-iana-root-change-lab-v1"
THEIR_PRODUCTION = False

_TLD = re.compile(r"^[a-z0-9-]{2,63}$")
_KEYTAG = re.compile(r"^\d{1,5}$")


@dataclass
class ChangeRequest:
    change_id: str
    tld: str
    change_type: str  # ns | ds
    payload: dict[str, Any]
    tech_ok: bool
    applied: bool = False


@dataclass
class Store:
    tlds: dict[str, dict[str, Any]] = field(default_factory=dict)
    changes: dict[str, ChangeRequest] = field(default_factory=dict)
    receipts: dict[str, dict[str, Any]] = field(default_factory=dict)


STORE = Store()


def reset() -> None:
    STORE.tlds.clear()
    STORE.changes.clear()
    STORE.receipts.clear()


def _receipt(
    decision: str,
    reason_code: str,
    *,
    change_id: str | None = None,
    tld: str | None = None,
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rid = str(uuid.uuid4())
    payload = {
        "spec": SPEC,
        "receipt_id": rid,
        "receipt_class": "clearance",
        "decision": decision,
        "reason_code": reason_code,
        "change_id": change_id,
        "tld": tld,
        "result": result,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="iana_root_change"),
        "ts": time.time(),
    }
    payload["receipt_hash"] = hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()
    STORE.receipts[rid] = payload
    return {**payload, "receipt_url": f"/v1/iana-root/receipts/{rid}"}


def register_tld(tld: str, *, ns: list[str] | None = None, ds: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    tld = tld.lower().lstrip(".")
    if not _TLD.match(tld):
        return {
            "ok": False,
            "reason_code": "malformed_tld",
            "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="iana_root_change"),
        }
    STORE.tlds[tld] = {"ns": list(ns or ["a.nic.example", "b.nic.example"]), "ds": list(ds or [])}
    return {
        "tld": tld,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="iana_root_change"),
    }


def _tech_check_ds(ds: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    keytag = str(ds.get("keytag") or "")
    if not _KEYTAG.match(keytag) or not (0 <= int(keytag) <= 65535):
        failures.append("bad_keytag")
    alg = ds.get("algorithm")
    if alg not in (8, 13, 15, 16):  # common DNSSEC algs fixture
        failures.append("bad_algorithm")
    digest_type = ds.get("digest_type")
    if digest_type not in (2, 4):
        failures.append("bad_digest_type")
    digest = str(ds.get("digest") or "")
    if len(digest) < 32 or not re.fullmatch(r"[0-9a-fA-F]+", digest):
        failures.append("bad_digest")
    if ds.get("matches_child_dnskey") is False:
        failures.append("ds_dnskey_mismatch")
    if ds.get("matches_child_dnskey") is None:
        failures.append("ds_dnskey_unverified")
    return failures


def _tech_check_ns(ns_list: list[str]) -> list[str]:
    failures: list[str] = []
    if not ns_list or len(ns_list) < 2:
        failures.append("insufficient_ns")
    for ns in ns_list:
        if not ns or "." not in ns:
            failures.append("malformed_ns")
            break
    return failures


def submit_change(
    *,
    tld: str,
    change_type: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    tld = tld.lower().lstrip(".")
    if tld not in STORE.tlds:
        return _receipt("DENY", "unknown_tld", tld=tld)
    if change_type not in ("ns", "ds"):
        return _receipt("DENY", "unsupported_change_type", tld=tld)

    failures: list[str] = []
    if change_type == "ds":
        failures = _tech_check_ds(payload)
    else:
        failures = _tech_check_ns(list(payload.get("ns") or []))

    cid = str(uuid.uuid4())
    tech_ok = len(failures) == 0
    STORE.changes[cid] = ChangeRequest(
        change_id=cid,
        tld=tld,
        change_type=change_type,
        payload=dict(payload),
        tech_ok=tech_ok,
    )
    if not tech_ok:
        return _receipt(
            "DENY",
            "tech_check_failed",
            change_id=cid,
            tld=tld,
            result={"failures": failures, "pti_shaped": True},
        )
    return {
        "change_id": cid,
        "tld": tld,
        "change_type": change_type,
        "tech_ok": True,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="iana_root_change"),
    }


def apply_root_change(change_id: str, *, maintainer_ack: bool = True) -> dict[str, Any]:
    """Mouth: apply only after tech OK + maintainer (Verisign-shaped) ack. Lab fixture."""
    ch = STORE.changes.get(change_id)
    if ch is None:
        return _receipt("DENY", "no_change_request", change_id=change_id)

    if not ch.tech_ok:
        return _receipt(
            "DENY",
            "tech_check_failed",
            change_id=change_id,
            tld=ch.tld,
            result={"cannot_apply_failed_tech": True},
        )

    if not maintainer_ack:
        return _receipt(
            "DENY",
            "maintainer_nack",
            change_id=change_id,
            tld=ch.tld,
            result={"verisign_shaped": True},
        )

    if ch.applied:
        return _receipt(
            "ALLOW",
            "already_applied",
            change_id=change_id,
            tld=ch.tld,
        )

    zone = STORE.tlds[ch.tld]
    if ch.change_type == "ds":
        zone["ds"] = [dict(ch.payload)]
    else:
        zone["ns"] = list(ch.payload.get("ns") or [])

    ch.applied = True
    return _receipt(
        "ALLOW",
        "root_zone_updated",
        change_id=change_id,
        tld=ch.tld,
        result={
            "change_type": ch.change_type,
            "zone_snapshot": {"ns": list(zone["ns"]), "ds": list(zone["ds"])},
            "real_root": False,
            "fixture": True,
            "pti_verisign_shaped": True,
        },
    )


def get_receipt(receipt_id: str) -> dict[str, Any] | None:
    r = STORE.receipts.get(receipt_id)
    if r is None:
        return None
    return {**r, "receipt_url": f"/v1/iana-root/receipts/{receipt_id}"}
