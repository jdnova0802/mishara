"""Scenario 3 live gate — exclusive door before vendor bank-detail write.

FinCEN FIN-2016-A003 Scenario 3: criminal emails new account number → victim
updates vendor master → wire leaves. This module fail-closes that write unless:

  Clear: who may change this vendor + what fingerprints (old→new, hashed)
  Seal:  out-of-band callback confirmed + dual approve
  Go:    bind ticket for POST /v1/scenario-3/apply/{change_id}
  Never: missing callback / dual approve / same-fp / raw account numbers

No raw account or routing numbers — client sends SHA-256 fingerprints only.
"""
from __future__ import annotations

import re
from typing import Any

from spend_protocol import (
    VENDOR_BANK_KIND,
    fingerprint,
    intended_vendor_bank,
    vendor_bank_path,
)

SPEC = "gate-scenario-3-gate-v1"
FINCEN = "FIN-2016-A003"
SCENARIO = "Scenario 3 — Criminal Impersonates a Supplier"

REASON_CALLBACK = "callback_not_confirmed"
REASON_DUAL = "dual_approve_required"
REASON_SAME_FP = "new_account_fp_must_differ"
REASON_FP = "account_fp_required_sha256"
REASON_IDS = "vendor_id_and_change_id_required"
REASON_CHANNEL = "callback_channel_required"

_HEX64 = re.compile(r"^[a-f0-9]{64}$")

ALLOWED_KEYS = frozenset(
    {
        "fuse_id",
        "vendor_id",
        "change_id",
        "old_account_fp",
        "new_account_fp",
        "callback_confirmed",
        "dual_approve",
        "callback_channel",
        "approver_a",
        "approver_b",
        "charge_id",
        "license_id",
        "ticket_id",
        "token",
        "method",
        "path",
        "spend_fingerprint",
        "spend_kind",
        "now",
        "job_id",
    }
)


def allowlist(body: dict | None) -> dict:
    cleaned = {}
    for key, value in (body or {}).items():
        if key in ALLOWED_KEYS:
            cleaned[key] = value
    return cleaned


def _truthy(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return v != 0
    s = str(v or "").strip().lower()
    return s in {"1", "true", "yes", "y", "on"}


def _fp(v: Any) -> str:
    return str(v or "").strip().lower()


def evaluate_change(body: dict | None) -> dict:
    """Return plan: allow_bind + reason + spend_write. Fail closed."""
    src = body if isinstance(body, dict) else {}
    vendor_id = str(src.get("vendor_id") or "").strip()
    change_id = str(src.get("change_id") or "").strip()
    old_fp = _fp(src.get("old_account_fp"))
    new_fp = _fp(src.get("new_account_fp"))
    channel = str(src.get("callback_channel") or "").strip()
    callback_ok = _truthy(src.get("callback_confirmed"))
    dual_ok = _truthy(src.get("dual_approve"))

    spend = intended_vendor_bank(vendor_id=vendor_id, change_id=change_id)
    base = {
        "spec": SPEC,
        "primary": {"advisory": FINCEN, "scenario": SCENARIO},
        "vendor_id": vendor_id or None,
        "change_id": change_id or None,
        "old_account_fp": old_fp or None,
        "new_account_fp": new_fp or None,
        "callback_confirmed": callback_ok,
        "dual_approve": dual_ok,
        "callback_channel": channel or None,
        "allow_bind": False,
        "halt": True,
        "write_executed": False,
    }

    if spend is None:
        return {**base, "reason": REASON_IDS, "spend_write": None}

    if not _HEX64.match(old_fp) or not _HEX64.match(new_fp):
        return {**base, "reason": REASON_FP, "spend_write": spend}

    if old_fp == new_fp:
        return {**base, "reason": REASON_SAME_FP, "spend_write": spend}

    if not callback_ok:
        return {**base, "reason": REASON_CALLBACK, "spend_write": spend}

    if not channel:
        return {**base, "reason": REASON_CHANNEL, "spend_write": spend}

    if not dual_ok:
        return {**base, "reason": REASON_DUAL, "spend_write": spend}

    approver_a = str(src.get("approver_a") or "").strip()
    approver_b = str(src.get("approver_b") or "").strip()
    if approver_a and approver_b and approver_a.lower() == approver_b.lower():
        return {**base, "reason": REASON_DUAL, "spend_write": spend}

    return {
        **base,
        "allow_bind": True,
        "halt": False,
        "reason": None,
        "spend_write": spend,
        "spend_fingerprint": fingerprint(spend),
        "apply_path": vendor_bank_path(change_id),
        "spend_kind": VENDOR_BANK_KIND,
        "clear": {
            "vendor_id": vendor_id,
            "change_id": change_id,
            "old_account_fp": old_fp,
            "new_account_fp": new_fp,
        },
        "seal_inputs": {
            "callback_confirmed": True,
            "callback_channel": channel,
            "dual_approve": True,
            "approver_a": approver_a or None,
            "approver_b": approver_b or None,
        },
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Scenario 3 live gate",
        "primary": {"advisory": FINCEN, "scenario": SCENARIO},
        "mouth": (
            "May this vendor bank-detail write proceed — only after sealed "
            "out-of-band callback + dual approve bound to account fingerprints."
        ),
        "not": [
            "Not a Diligence memo page alone",
            "Not an account-validation reseller",
            "Does not accept raw account or routing numbers",
        ],
        "required_before_go": [
            "old_account_fp + new_account_fp (sha256 hex, must differ)",
            "callback_confirmed=true",
            "callback_channel (e.g. phone_on_file)",
            "dual_approve=true",
        ],
        "married_write": {
            "method": "POST",
            "path": "/v1/scenario-3/apply/{change_id}",
            "spend_kind": VENDOR_BANK_KIND,
        },
        "urls": {
            "page": f"{base}/scenario-3",
            "manifest": f"{base}/.well-known/scenario-3-gate.json",
            "pre_change": f"{base}/demo/scenario-3/pre-change",
            "pre_change_v1": f"{base}/v1/scenario-3/pre-change",
            "redeem": f"{base}/v1/pas/bind-ticket/redeem",
            "apply": f"{base}/demo/scenario-3/apply",
            "seal": f"{base}/v1/seal",
        },
        "their_production": False,
    }
