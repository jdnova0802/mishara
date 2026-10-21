#!/usr/bin/env python3
"""Dead-hand receipt check. No server, no env key, no verify_url fetch.

A stranger passes a receipt file and a public key they already hold.
Stdout is `valid` or `invalid`. The receipt does not get to name the key.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys
from typing import Any

try:
    from gate import receipt as receipt_mod
except ImportError:
    import receipt as receipt_mod

SPEC = "gate-receipt-v1"

# Envelope fields a public payload may carry beside the signed object.
# They are never part of the hash.
_ENVELOPE_KEYS = frozenset(
    {
        "receipt_hash",
        "receipt_signature",
        "receipt_public_key_fingerprint",
        "canonical_receipt",
        "canonical_receipt_json",
        "event_id",
        "public_key",
        "public_key_b64",
    }
)


def _b64decode(s: str) -> bytes | None:
    t = s.strip().replace("-", "+").replace("_", "/")
    pad = "=" * (-len(t) % 4)
    try:
        return base64.b64decode(t + pad, validate=False)
    except Exception:
        return None


def _extract_canonical(doc: dict) -> tuple[str | None, dict | None, str | None]:
    raw = doc.get("canonical_receipt_json")
    nested = doc.get("canonical_receipt")
    parsed = None
    if isinstance(raw, str) and raw.strip():
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return None, None, "canonical_json_not_json"
        if not isinstance(parsed, dict):
            return None, None, "canonical_not_object"
        if isinstance(nested, dict) and receipt_mod.canonical_dumps(nested) != receipt_mod.canonical_dumps(parsed):
            return None, None, "canonical_mismatch"
        return raw, parsed, None

    if isinstance(nested, dict):
        return receipt_mod.canonical_dumps(nested), nested, None

    if doc.get("spec") == SPEC:
        canonical = {k: v for k, v in doc.items() if k not in _ENVELOPE_KEYS}
        return receipt_mod.canonical_dumps(canonical), canonical, None

    return None, None, "missing_canonical_receipt"


def _load_public_key(arg: str) -> bytes | None:
    text = arg
    try:
        with open(arg, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError:
        text = arg
    text = text.strip()
    if not text:
        return None
    if text.startswith("{"):
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return None
        if not isinstance(parsed, dict):
            return None
        text = str(parsed.get("public_key_b64") or parsed.get("public_key") or "").strip()
        if not text:
            return None
    pub = _b64decode(text)
    if not pub or len(pub) != 32:
        return None
    return pub


def _signature_ok(pub: bytes, signature_b64: str, receipt_hash: str) -> bool:
    sig = _b64decode(signature_b64)
    if not sig:
        return False
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        Ed25519PublicKey.from_public_bytes(pub).verify(sig, receipt_hash.encode("utf-8"))
        return True
    except Exception:
        return False


def verify_document(doc: dict, public_key: bytes) -> dict[str, Any]:
    """Return a verdict. Does not read GATE_RECEIPT_* and does not open a socket."""
    reasons: list[str] = []
    canonical_json, canonical, extract_err = _extract_canonical(doc)
    if extract_err or canonical_json is None or canonical is None:
        return {
            "verdict": "invalid",
            "spec": SPEC,
            "receipt_hash": None,
            "reasons": [extract_err or "missing_canonical_receipt"],
        }

    spec = canonical.get("spec")
    if spec != SPEC:
        reasons.append("spec_mismatch")

    receipt_hash = receipt_mod.compute_receipt_hash(canonical_json)
    claimed_hash = doc.get("receipt_hash")
    if isinstance(claimed_hash, str) and claimed_hash and claimed_hash != receipt_hash:
        reasons.append("hash_mismatch")

    claimed_fp = doc.get("receipt_public_key_fingerprint")
    fingerprint = hashlib.sha256(public_key).hexdigest()[:16]
    if isinstance(claimed_fp, str) and claimed_fp and claimed_fp != fingerprint:
        reasons.append("fingerprint_mismatch")

    signature = doc.get("receipt_signature")
    if not isinstance(signature, str) or not signature.strip():
        reasons.append("missing_signature")
    elif not _signature_ok(public_key, signature, receipt_hash):
        reasons.append("signature_invalid")

    return {
        "verdict": "valid" if not reasons else "invalid",
        "spec": SPEC,
        "receipt_hash": receipt_hash,
        "public_key_fingerprint": fingerprint,
        "reasons": reasons,
    }


def verify_files(receipt_path: str, public_key_arg: str) -> dict[str, Any]:
    try:
        with open(receipt_path, "r", encoding="utf-8") as f:
            doc = json.load(f)
    except OSError as e:
        return {"verdict": "invalid", "spec": SPEC, "receipt_hash": None, "reasons": [f"receipt_unreadable:{e.strerror or e}"]}
    except json.JSONDecodeError:
        return {"verdict": "invalid", "spec": SPEC, "receipt_hash": None, "reasons": ["receipt_not_json"]}
    if not isinstance(doc, dict):
        return {"verdict": "invalid", "spec": SPEC, "receipt_hash": None, "reasons": ["receipt_not_object"]}
    pub = _load_public_key(public_key_arg)
    if pub is None:
        return {"verdict": "invalid", "spec": SPEC, "receipt_hash": None, "reasons": ["bad_public_key"]}
    return verify_document(doc, pub)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check a Gate receipt with a public key you already hold. Does not contact the server."
    )
    parser.add_argument("receipt", help="Receipt JSON (public payload or canonical bundle)")
    parser.add_argument(
        "--public-key",
        required=True,
        help="Ed25519 public key: raw base64, a text file of that base64, or JSON with public_key_b64",
    )
    parser.add_argument("--json", action="store_true", help="Print the verdict object instead of valid/invalid")
    args = parser.parse_args(argv)
    result = verify_files(args.receipt, args.public_key)
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(result["verdict"])
        if result["reasons"]:
            print(",".join(result["reasons"]), file=sys.stderr)
    return 0 if result["verdict"] == "valid" else 1


if __name__ == "__main__":
    sys.exit(main())
