"""Tests for OCT / Fast Funds sink mouth."""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_ALLOW_LOCAL", "1")

from gate import sink_mouth as mouth  # noqa: E402
from gate import prefinality as pf  # noqa: E402
from gate.app import app  # noqa: E402


class SinkMouthTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_oct_is_prefinality_rail(self):
        self.assertIn("oct", pf.RAILS)
        ids = [r["id"] for r in pf.manifest("https://example.test")["rails"]]
        self.assertIn("oct", ids)

    def test_push_maps_to_evaluate(self):
        push = mouth.dogfood_push()
        body = mouth.push_to_evaluate_body(push)
        self.assertEqual(body["rail"], "oct")
        self.assertEqual(body["transfer"]["counterparty"], "ADP Wisely Now")
        self.assertEqual(body["transfer"]["receive_fee_usd"], 0.60)

    def test_visa_fees_match_primary(self):
        self.assertEqual(mouth.RECEIVE_FEES_USD["original_credit"], 0.29)
        self.assertEqual(mouth.RECEIVE_FEES_USD["fast_funds"], 0.60)
        self.assertIn("visa.com", mouth.VISA_PRIMARY)

    def test_dogfood_go(self):
        r = self.client.post(
            "/demo/sink/mouth",
            json={"force_breach": False, "agent_id": "t1", "max_amount": "500.00"},
        )
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(body["spec"], "gate-sink-mouth-v1")
        self.assertTrue(body["accepted"])
        self.assertEqual(body["receive"]["receive_fee_usd"], 0.60)

    def test_dogfood_never(self):
        r = self.client.post("/demo/sink/mouth", json={"force_breach": True})
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertFalse(body["accepted"])
        self.assertEqual(body["decision"], "NO_GO")

    def test_well_known_and_page(self):
        m = self.client.get("/.well-known/sink-mouth.json")
        self.assertEqual(m.status_code, 200)
        self.assertEqual(m.get_json()["spec"], "gate-sink-mouth-v1")
        page = self.client.get("/sink-mouth")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"Fast Funds", page.data)

    def test_aft_illustration(self):
        r = self.client.post("/demo/sink/aft", json={"load_amount": 100})
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertAlmostEqual(body["issuer_interchange_usd"], 1.95, places=2)

    def test_health_lists_sink(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertIn("sink_mouth", body)
        self.assertIn("dogfood", body["sink_mouth"])

    def test_webhook_accepts_go(self):
        push = mouth.dogfood_push()
        r = self.client.post("/v1/sink/oct", json=push)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.get_json()["accepted"])

    def test_webhook_rejects_breach(self):
        push = mouth.dogfood_push(force_breach=True)
        r = self.client.post("/v1/sink/oct", json=push)
        self.assertEqual(r.status_code, 403)
        self.assertFalse(r.get_json()["accepted"])


if __name__ == "__main__":
    unittest.main()
