"""Diplomatics v0 — issuer-incomplete stranger verification (Nisaba / Gate invent).

Civilizational gap: most "verify" portals are finished by the operator.
Digital diplomatics: stranger completes authentication the issuer cannot forge alone.

Rooted in diplomatics (genesis · form · transmission) — already gestured at /verify.
This invent makes issuer-incompleteness a hard law-object.

NOT a sister company.
Surfaces:
  GET /.well-known/diplomatics.json
  POST /demo/diplomatics/challenge
"""
from __future__ import annotations

import hashlib
import secrets
from typing import Any

SPEC = "gate-diplomatics-v0"
FIRM = "Nisaba LLC"
CARD = (
    "On-card invent. Stranger finishes verify; issuer cannot complete it alone. "
    "Does not rename the firm. Extends velaru.xyz/verify doctrine."
)

CHECKS = (
    "GENESIS",  # origin / key / epoch binding
    "FORM",  # required fields / canonical shape
    "TRANSMISSION",  # hash chain / signature path
    "PARTIAL_STRANGER",  # check only stranger can finish (issuer-incomplete)
)


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "firm": FIRM,
        "name": "Issuer-Incomplete Diplomatics",
        "version": "0",
        "card": CARD,
        "job": (
            "Make verification structurally incomplete for the issuer. "
            "Stranger witness authenticates genesis, form, and transmission in their own environment."
        ),
        "thesis": (
            "Screenshot is cheap talk. Green in the stranger's browser is felicity. "
            "If the operator can finish every check alone, it is not diplomatics — it is marketing."
        ),
        "laws": [
            "Issuer never receives stranger private material required to finish PARTIAL_STRANGER",
            "Crypto runs in stranger browser / local verifier when possible",
            "Fail closed if PARTIAL_STRANGER cannot complete",
            "Receipt remains useful without login to Nisaba/Velaru",
        ],
        "checks": list(CHECKS),
        "pairs_with": [
            "gate-deny-meter-v0",
            "gate-documentary-protest-v0",
            "velaru.verify",
        ],
        "urls": {
            "well_known": f"{base}/.well-known/diplomatics.json",
            "demo_challenge": f"{base}/demo/diplomatics/challenge",
            "verify": "https://velaru.xyz/verify",
        },
        "civilizational": True,
        "novelty_honest": (
            "Notaries and diplomatics are old. Issuer-incomplete machine verify as "
            "mandatory law before irreversible leave — underbuilt in software money / agents."
        ),
        "not": [
            "Trust-me dashboard verify",
            "Operator-only green check",
            "Sister company",
        ],
    }


def challenge(*, receipt_hint: str | None = None) -> dict[str, Any]:
    """Issue a challenge the issuer cannot complete without stranger-side recomputation."""
    nonce = secrets.token_hex(16)
    hint = (receipt_hint or "").strip()[:256]
    # Issuer publishes commitment; stranger must recompute local material
    commitment = hashlib.sha256(f"{SPEC}|{nonce}|{hint}".encode()).hexdigest()
    return {
        "spec": SPEC,
        "firm": FIRM,
        "challenge_id": nonce,
        "issuer_commitment": commitment,
        "issuer_incomplete": True,
        "stranger_must": [
            "Load receipt bytes in local environment",
            "Recompute hash / signature checks (GENESIS·FORM·TRANSMISSION)",
            "Bind local entropy or browser-side verify so issuer cannot forge completion",
            "Produce stranger_attestation = H(commitment || local_verify_transcript)",
        ],
        "accepts_only": "stranger_attestation that issuer cannot derive without local transcript",
        "verify_url": "https://velaru.xyz/verify",
        "card_note": "Diplomatics law-object. Not a sister co.",
    }
