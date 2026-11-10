"""Item 119 — IEC 61511 interlock mapping and BLOCK proof-test."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-interlock.db")
os.environ["GATE_PROOF_TEST_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-proof-tests.json")
os.environ.pop("GATE_PROOF_TEST_INTERVAL_HOURS", None)

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import interlock  # noqa: E402
import triple_vote  # noqa: E402


class InterlockLogicTests(unittest.TestCase):
    def setUp(self):
        path = os.environ["GATE_PROOF_TEST_PATH"]
        if os.path.exists(path):
            os.remove(path)
        os.environ.pop("GATE_PROOF_TEST_INTERVAL_HOURS", None)

    def test_sil_unset_and_roles_named(self):
        arch = interlock.architecture()
        self.assertIsNone(arch["sil"])
        self.assertFalse(arch["sil_named"])
        self.assertFalse(arch["hazard_analysis"])
        self.assertEqual(arch["sensor"]["name"], "Erra")
        self.assertEqual(arch["logic_solver"]["name"], "Gate")
        self.assertEqual(arch["final_element"]["name"], "write-block")
        self.assertEqual(arch["sensor"]["vote_spec"], triple_vote.SPEC)
        self.assertIsNone(arch["proof_test_interval_hours"])
        self.assertFalse(arch["unanimous_block_possible"])

    def test_untested_is_assumed_failed(self):
        st = interlock.status()
        self.assertTrue(st["untested"])
        self.assertTrue(st["assumed_failed"])
        self.assertTrue(st["overdue"])

    def test_proof_test_trips_write_block_via_triple_vote(self):
        rec = interlock.run_proof_test()
        self.assertTrue(rec["tripped"])
        self.assertTrue(rec["write_blocked"])
        self.assertFalse(rec["acted"])
        self.assertFalse(rec["hard_trip"])
        self.assertEqual(rec["vote"]["result"], "HOLD")
        self.assertFalse(rec["vote"]["agreed"])
        self.assertEqual(rec["vote"]["votes"]["hop"], "BLOCK")
        self.assertEqual(rec["vote"]["votes"]["constraints"], "BLOCK")
        self.assertEqual(rec["vote"]["votes"]["circuit"], "ALLOW")
        self.assertIsNone(rec["sil"])
        self.assertTrue(rec["receipt_hash"])
        st = interlock.status()
        self.assertFalse(st["untested"])
        self.assertFalse(st["assumed_failed"])
        self.assertFalse(st["overdue"])

    def test_interval_overdue_without_inventing_sil_hours(self):
        rec = interlock.run_proof_test()
        rec["tested_at"] = (datetime.now(timezone.utc) - timedelta(hours=10)).replace(microsecond=0).isoformat()
        store = {"spec": interlock.PROOF_SPEC, "drills": [rec]}
        interlock._save(store)
        os.environ["GATE_PROOF_TEST_INTERVAL_HOURS"] = "1"
        self.assertEqual(interlock.interval_hours(), 1.0)
        self.assertTrue(interlock.overdue())
        self.assertTrue(interlock.status()["assumed_failed"])


class InterlockFlaskTests(unittest.TestCase):
    def setUp(self):
        path = os.environ["GATE_PROOF_TEST_PATH"]
        if os.path.exists(path):
            os.remove(path)
        self.client = app_mod.app.test_client()

    def test_page_and_drill_api(self):
        page = self.client.get("/interlock")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"write-block", page.data)
        self.assertIn(b"SIL", page.data)
        empty = self.client.get("/v1/interlock")
        body = empty.get_json()
        self.assertTrue(body["assumed_failed"])
        self.assertIsNone(body["architecture"]["sil"])
        posted = self.client.post("/v1/interlock/proof-test")
        self.assertEqual(posted.status_code, 201)
        rec = posted.get_json()
        self.assertTrue(rec["tripped"])
        after = self.client.get("/v1/interlock")
        self.assertFalse(after.get_json()["assumed_failed"])


if __name__ == "__main__":
    unittest.main()
