"""Items 69–74 — taxonomy, handlers, public hash re-derive."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-dfir-verify.db")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import dfir  # noqa: E402
import receipt  # noqa: E402


class DfirVerifyTests(unittest.TestCase):
    def test_taxonomy_maps_premium_over_limit(self):
        out = dfir.classify_reason("premium_exceeds_authority")
        self.assertEqual(out["reason_code"], "LIMIT")
        self.assertIn("delegated", out["reason_text"])

    def test_handlers_do_not_invent_erra_signatures(self):
        handlers = dfir.chain_of_handlers({"receipt_public_key_fingerprint": "fp", "receipt_signature": "s", "hop": {}})
        roles = {h["role"]: h for h in handlers}
        self.assertTrue(roles["gate"]["present"])
        self.assertFalse(roles["erra"]["present"])
        self.assertIsNone(roles["erra"]["signature"])
        self.assertTrue(roles["velaru"]["present"] is False or roles["velaru"]["signature"] is None)

    def test_envelope_uses_taxonomy_and_anchor(self):
        env = receipt.dfir_envelope(
            {
                "id": "evt",
                "receipt_hash": "abc",
                "prev_receipt_hash": "prev",
                "receipt_public_key_fingerprint": "fp",
                "receipt_signature": "sig",
                "hop": {"reason": "premium_exceeds_authority"},
            },
            {"public_url": "https://gate.example"},
        )
        self.assertEqual(env["reason_code"], "LIMIT")
        self.assertEqual(env["ledger_position"]["prev_receipt_hash"], "prev")
        self.assertIn("evidence-head.json", env["durable_anchor"]["merkle_head"])
        self.assertIsNone(env["durable_anchor"]["scitt"])
        self.assertFalse(env["in_signed_canonical"])

    def test_public_verify_recomputes_hash(self):
        issued = receipt.issue_receipt(
            event_id="evt-verify",
            fuse_id="fuse_x",
            job_id=None,
            decision="BLOCK",
            acted=False,
            verify_url="https://example/verify",
            created_at="2026-11-10T16:00:00+00:00",
            hop={"verdict": False, "state": "DEAD"},
            prev_receipt_hash=None,
        )
        row = {
            "id": "evt-verify",
            "fuse_id": "fuse_x",
            "job_id": None,
            "decision": "BLOCK",
            "acted": False,
            "verify_url": "https://example/verify",
            "created_at": "2026-11-10T16:00:00+00:00",
            "hop": {"verdict": False, "state": "DEAD"},
            "prev_receipt_hash": None,
            "receipt_hash": issued["receipt_hash"],
            "receipt_signature": issued["receipt_signature"],
            "receipt_public_key_fingerprint": issued["receipt_public_key_fingerprint"],
        }
        out = dfir.public_verify(row, public_url="https://example")
        self.assertTrue(out["hash_matches"])
        self.assertTrue(out["receipt_does_not_name_the_key"])
        self.assertEqual(out["key_source"], "gate_published_env")


class DfirVerifyFlaskTests(unittest.TestCase):
    def setUp(self):
        self.client = app_mod.app.test_client()

    def test_verify_requires_id(self):
        self.assertEqual(self.client.get("/v1/verify").status_code, 400)
        self.assertEqual(self.client.get("/v1/verify?event_id=missing").status_code, 404)


if __name__ == "__main__":
    unittest.main()
