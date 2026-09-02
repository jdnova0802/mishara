"""Harden pass: real-route health probes + chain continuity audit."""
from __future__ import annotations

import os
import tempfile
import unittest
from unittest import mock

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_PUBLIC_URL", "http://localhost:5001")

try:
    from gate import app as gate_app
    from gate import chain_continuity as cc
    from gate import db
    from gate import health_probes
except ImportError:
    import app as gate_app
    import chain_continuity as cc
    import db
    import health_probes


class HealthProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_health_includes_probes(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIn("probes", data)
        self.assertIn("probes_ok", data)
        self.assertTrue(data["probes_ok"])
        self.assertIn("sentry_configured", data)
        routes = data["probes"]["routes"]
        self.assertTrue(routes["bind_room"]["ok"])
        self.assertTrue(routes["officer_pack"]["ok"])
        self.assertTrue(routes["evidence_head"]["ok"])
        self.assertTrue(routes["prefinality_jwks"]["ok"])

    def test_probe_local_routes_helper(self):
        probes = health_probes.probe_local_routes(self.client)
        summary = health_probes.summarize(probes)
        self.assertTrue(summary["ok"])


class ChainContinuityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp.name, "gate.db")
        self.env = mock.patch.dict(
            os.environ,
            {"GATE_DB_PATH": self.db_path, "GATE_DEV_MODE": "1"},
            clear=False,
        )
        self.env.start()
        db.init_db()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_empty_chain_ok(self):
        audit = cc.audit_link_integrity([])
        self.assertTrue(audit["ok"])
        self.assertEqual(audit["broken_link_count"], 0)

    def test_broken_link_detected(self):
        rows = [
            {
                "id": "a",
                "created_at": "2026-08-01T00:00:00+00:00",
                "receipt_hash": "aa" * 32,
                "prev_receipt_hash": None,
            },
            {
                "id": "b",
                "created_at": "2026-09-01T12:00:00+00:00",
                "receipt_hash": "bb" * 32,
                "prev_receipt_hash": "cc" * 32,  # wrong
            },
        ]
        audit = cc.audit_sep1_window(rows)
        self.assertEqual(audit["result"], "broken_links")
        self.assertEqual(audit["severity"], "material")
        self.assertEqual(audit["events_in_window"], 1)

    def test_sep1_clear_writes_ledger(self):
        result = cc.record_sep1_audit([], force=True)
        self.assertTrue(result["wrote"])
        self.assertEqual(result["audit"]["result"], "no_broken_links")
        doc = cc.load_corrections()
        self.assertEqual(len(doc["entries"]), 1)
        self.assertEqual(doc["entries"][0]["kind"], "sep1_2026_continuity")
        self.assertIsNone(doc["entries"][0]["correction"])

    def test_ops_and_well_known(self):
        client = gate_app.app.test_client()
        r = client.get("/.well-known/chain-corrections.json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["spec"], "gate-chain-corrections-v1")
        # Dev mode: ops authorized without token when GATE_DEV_MODE.
        with mock.patch.object(gate_app, "GATE_DEV_MODE", True):
            r2 = client.get("/ops/chain-continuity")
        self.assertEqual(r2.status_code, 200)
        body = r2.get_json()
        self.assertIn("audit", body)


if __name__ == "__main__":
    unittest.main()
