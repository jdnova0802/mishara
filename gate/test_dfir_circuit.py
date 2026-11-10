"""Items 18, 19, 20, 69–73."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-dfir-circuit.db")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import circuit_breaker  # noqa: E402
import receipt  # noqa: E402
import safe_mode  # noqa: E402
import weld  # noqa: E402


class DistanceTests(unittest.TestCase):
    def test_premium_over_limit_is_named_in_dollars(self):
        plan = weld.mga_authority(
            {"verdict": True, "state": "LIVE"},
            200,
            premium=62400,
            authority_limit=50000,
            line="GL",
            state="CO",
            allowed_lines=None,
            allowed_states=None,
        )
        self.assertEqual(plan["result"], "BLOCK")
        self.assertEqual(plan["distance_to_compliance"]["delta"], 12400)
        self.assertIn("12,400 over the $50,000 limit", plan["distance_to_compliance"]["plain"])


class CircuitTests(unittest.TestCase):
    def test_spike_opens_breaker(self):
        now = datetime(2026, 11, 10, 16, 0, tzinfo=timezone.utc)
        rows = [
            {
                "fuse_id": "fuse_x",
                "decision": "BLOCK",
                "created_at": "2026-11-10T15:50:00+00:00",
            }
            for _ in range(5)
        ]
        out = circuit_breaker.evaluate(rows, "fuse_x", now=now)
        self.assertTrue(out["open"])
        self.assertEqual(out["action"], "HALT_AGENT")

    def test_quiet_fuse_stays_closed(self):
        now = datetime(2026, 11, 10, 16, 0, tzinfo=timezone.utc)
        rows = [{"fuse_id": "fuse_x", "decision": "ALLOW", "created_at": "2026-11-10T15:50:00+00:00"}]
        out = circuit_breaker.evaluate(rows, "fuse_x", now=now)
        self.assertFalse(out["open"])


class SafeModeTests(unittest.TestCase):
    def test_hold_names_forbidden_writes(self):
        snap = safe_mode.snapshot(reason="HOLD")
        self.assertEqual(snap["state"], "SAFE_MODE")
        self.assertIn("bind", snap["forbidden"])
        self.assertIn("read", snap["allowed"])


class DfirTests(unittest.TestCase):
    def test_envelope_labels_hash_and_does_not_claim_canonical(self):
        env = receipt.dfir_envelope(
            {
                "id": "evt",
                "receipt_hash": "abc",
                "prev_receipt_hash": "prev",
                "receipt_public_key_fingerprint": "fp",
                "receipt_signature": "sig",
                "hop": {"reason": "premium_exceeds_authority"},
            },
            {},
        )
        self.assertEqual(env["event_id"], "evt")
        self.assertEqual(env["payload_hash_sha256"], "abc")
        self.assertEqual(env["agent_key_id"], "fp")
        self.assertFalse(env["in_signed_canonical"])
        self.assertEqual(env["ledger_position"]["prev_receipt_hash"], "prev")


if __name__ == "__main__":
    unittest.main()
