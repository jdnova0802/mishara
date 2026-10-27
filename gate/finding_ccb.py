"""Dated public finding: CCB New York left the QUSFI list.

Strangers recompute the hash. The signature is over that hash. No login.
Their production stays false. This is not a fraud finding and not a bank score.
"""
from __future__ import annotations

import hashlib
from typing import Any

try:
    from gate import qusfi
    from gate import receipt as receipt_mod
except ImportError:
    import qusfi
    import receipt as receipt_mod

SPEC = "gate-finding-ccb-svo-v1"
DATED = "2026-10-27"
_SIG_FIELDS = ("canonical_sha256", "signature", "signed_over", "public_key_fingerprint", "verify")


def _core() -> dict[str, Any]:
    looked = qusfi.lookup(qusfi.CCB_NY_ABA)
    current = looked.get("current") or {}
    prior = looked.get("prior") or {}
    return {
        "spec": SPEC,
        "dated": DATED,
        "subject": "China Construction Bank Corporation, New York Branch, ABA 26014685",
        "finding": (
            "On the NAIC SVO List of Qualified U.S. Financial Institutions dated "
            "2025-12-31, ABA 26014685 (China Construction Bank Corporation, New York) "
            "appears. On the list dated 2026-09-30, it does not. The next evergreen, "
            "renewal, extension, modification, or amendment cannot treat that issuer "
            "as qualified for surplus credit. A letter issued while the issuer was "
            "on the list is not automatically dead."
        ),
        "aba": qusfi.CCB_NY_ABA,
        "prior_on_list": bool(prior.get("on_list")),
        "current_on_list": bool(current.get("on_list")),
        "prior": {
            "as_of": (prior.get("as_of")),
            "pdf_sha256": prior.get("pdf_sha256"),
            "source_url": prior.get("source_url"),
        },
        "current": {
            "as_of": current.get("as_of"),
            "pdf_sha256": current.get("pdf_sha256"),
            "source_url": current.get("source_url"),
        },
        "grandfather": qusfi.GRANDFATHER,
        "claim_when_off_current_list": qusfi.CLAIM_OFF_LIST,
        "not_a_claim": qusfi.NOT_A_CLAIM,
        "clocks": qusfi.clocks(),
        "confirmation": {
            "phone_or_email_on_instrument": "HALT",
            "advised_mt760_via_own_bank": "required_channel_for_any_clear",
        },
        "not": [
            "Not a fraud finding. The list footnote also removes institutions that did not pay the annual fee.",
            "Not a bank credit score.",
            "Not a statement that every CCB letter in force is already disallowed.",
            "Lloyd's Y5410 six-month confirm is Funds at Lloyd's. It is not Model 785 surplus credit.",
        ],
        "scope": qusfi.SCOPE,
    }


def _unsigned(document: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in document.items() if key not in _SIG_FIELDS}


def publish() -> dict[str, Any]:
    core = _core()
    canonical = receipt_mod.canonical_dumps(core)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    signature = receipt_mod.sign_receipt_hash(digest)
    core["canonical_sha256"] = digest
    core["signature"] = signature
    core["public_key_fingerprint"] = receipt_mod.receipt_public_key_fingerprint()
    core["signed_over"] = "sha256(canonical JSON of this object excluding signature fields)"
    core["verify"] = (
        "Drop canonical_sha256, signature, signed_over, public_key_fingerprint, and verify. "
        "Canonical JSON, SHA-256 hex, Ed25519 over that hex string with the receipt public key. "
        "No login."
    )
    return core


def verifies(document: dict[str, Any] | None) -> bool:
    if not isinstance(document, dict):
        return False
    digest = document.get("canonical_sha256")
    signature = document.get("signature")
    if not isinstance(digest, str) or not signature:
        return False
    recomputed = hashlib.sha256(
        receipt_mod.canonical_dumps(_unsigned(document)).encode("utf-8")
    ).hexdigest()
    if recomputed != digest:
        return False
    return receipt_mod.verify_receipt_signature(receipt_hash=digest, signature_b64=signature)
