"""Offline receipt check — valid or invalid with the server absent."""
from __future__ import annotations

import base64
import json
import os
import socket
import sys
import tempfile
import unittest
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import offline_verify  # noqa: E402
import receipt  # noqa: E402


def _key_material():
    priv = Ed25519PrivateKey.generate()
    priv_b = priv.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    pub_b = priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    return (
        base64.b64encode(priv_b).decode("utf-8"),
        base64.b64encode(pub_b).decode("utf-8"),
        pub_b,
    )


def _issue(priv_b64: str, pub_b64: str) -> dict:
    os.environ["GATE_RECEIPT_PRIVATE_KEY"] = priv_b64
    os.environ["GATE_RECEIPT_PUBLIC_KEY"] = pub_b64
    issued = receipt.issue_receipt(
        event_id="evt-offline-1",
        fuse_id="fuse_velaru_drill",
        job_id="pc:DEMO",
        decision="BLOCK",
        acted=False,
        verify_url="https://gate.velaru.xyz/verify/evt-offline-1",
        created_at="2026-10-21T14:00:00+00:00",
        hop={"state": "halt", "halt": True, "verdict": "BLOCK"},
        prev_receipt_hash=None,
    )
    os.environ.pop("GATE_RECEIPT_PRIVATE_KEY", None)
    os.environ.pop("GATE_RECEIPT_PUBLIC_KEY", None)
    canonical = json.loads(issued["canonical_receipt_json"])
    return {
        "spec": "gate-receipt-payload-v1",
        "canonical_receipt": canonical,
        "canonical_receipt_json": issued["canonical_receipt_json"],
        "receipt_hash": issued["receipt_hash"],
        "receipt_signature": issued["receipt_signature"],
        "receipt_public_key_fingerprint": issued["receipt_public_key_fingerprint"],
        "verify_url": "https://gate.velaru.xyz/verify/evt-offline-1",
    }


class OfflineVerifyTests(unittest.TestCase):
    def setUp(self):
        self.priv_b64, self.pub_b64, self.pub_b = _key_material()
        self.payload = _issue(self.priv_b64, self.pub_b64)
        self.dir = tempfile.mkdtemp()
        self.receipt_path = os.path.join(self.dir, "receipt.json")
        self.key_path = os.path.join(self.dir, "public.key")
        with open(self.receipt_path, "w", encoding="utf-8") as f:
            json.dump(self.payload, f)
        with open(self.key_path, "w", encoding="utf-8") as f:
            f.write(self.pub_b64 + "\n")

    def test_valid_with_env_keys_absent(self):
        self.assertNotIn("GATE_RECEIPT_PRIVATE_KEY", os.environ)
        result = offline_verify.verify_files(self.receipt_path, self.key_path)
        self.assertEqual(result["verdict"], "valid")
        self.assertEqual(result["reasons"], [])
        self.assertEqual(result["spec"], "gate-receipt-v1")
        self.assertEqual(result["receipt_hash"], self.payload["receipt_hash"])

    def test_stdout_is_the_word(self):
        from io import StringIO

        buf = StringIO()
        with patch("sys.stdout", buf):
            code = offline_verify.main([self.receipt_path, "--public-key", self.pub_b64])
        self.assertEqual(code, 0)
        self.assertEqual(buf.getvalue().strip(), "valid")

    def test_tampered_decision_is_invalid(self):
        doc = json.loads(json.dumps(self.payload))
        doc["canonical_receipt"]["decision"] = "ALLOW"
        doc["canonical_receipt_json"] = receipt.canonical_dumps(doc["canonical_receipt"])
        result = offline_verify.verify_document(doc, self.pub_b)
        self.assertEqual(result["verdict"], "invalid")
        self.assertIn("signature_invalid", result["reasons"])

    def test_wrong_key_is_invalid(self):
        _, other_b64, _ = _key_material()
        result = offline_verify.verify_files(self.receipt_path, other_b64)
        self.assertEqual(result["verdict"], "invalid")
        self.assertIn("fingerprint_mismatch", result["reasons"])
        self.assertIn("signature_invalid", result["reasons"])

    def test_spec_mismatch_is_invalid(self):
        doc = json.loads(json.dumps(self.payload))
        canonical = doc["canonical_receipt"]
        canonical["spec"] = "gate-receipt-v2"
        doc["canonical_receipt_json"] = receipt.canonical_dumps(canonical)
        doc["receipt_hash"] = receipt.compute_receipt_hash(doc["canonical_receipt_json"])
        result = offline_verify.verify_document(doc, self.pub_b)
        self.assertEqual(result["verdict"], "invalid")
        self.assertIn("spec_mismatch", result["reasons"])

    def test_missing_signature_is_invalid(self):
        doc = json.loads(json.dumps(self.payload))
        doc["receipt_signature"] = None
        result = offline_verify.verify_document(doc, self.pub_b)
        self.assertEqual(result["verdict"], "invalid")
        self.assertIn("missing_signature", result["reasons"])

    def test_does_not_open_a_socket(self):
        def boom(*_a, **_k):
            raise AssertionError("network")

        with patch.object(socket, "socket", boom), patch.object(socket, "create_connection", boom):
            result = offline_verify.verify_files(self.receipt_path, self.key_path)
        self.assertEqual(result["verdict"], "valid")

    def test_disagreeing_canonical_copies_are_invalid(self):
        doc = json.loads(json.dumps(self.payload))
        doc["canonical_receipt"]["decision"] = "ALLOW"
        result = offline_verify.verify_document(doc, self.pub_b)
        self.assertEqual(result["verdict"], "invalid")
        self.assertEqual(result["reasons"], ["canonical_mismatch"])

    def test_embedded_key_is_ignored(self):
        doc = json.loads(json.dumps(self.payload))
        _, other_b64, _ = _key_material()
        doc["public_key_b64"] = other_b64
        result = offline_verify.verify_document(doc, self.pub_b)
        self.assertEqual(result["verdict"], "valid")


if __name__ == "__main__":
    unittest.main()
