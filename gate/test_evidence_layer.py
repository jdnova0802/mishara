"""Evidence-layer reference page — map, not a SKU."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(
    tempfile.gettempdir(), "gate-test-evidence-layer.db"
)

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import evidence_layer as el  # noqa: E402


class EvidenceLayerPageTests(unittest.TestCase):
    def setUp(self):
        self.client = app_mod.app.test_client()

    def test_page_is_a_reference_map(self):
        r = self.client.get("/evidence-layer")
        self.assertEqual(r.status_code, 200)
        body = r.get_data(as_text=True)
        self.assertIn("who", body.lower())
        self.assertIn("how it paid", body.lower())
        self.assertIn("what happened", body)
        self.assertIn('id="lane-identity"', body)
        self.assertIn('id="lane-payment"', body)
        self.assertIn('id="lane-evidence"', body)
        for name in (
            "WIMSE",
            "OAuth CIMD",
            "DAWN",
            "draft-klrc-aiagent-auth",
            "ACP",
            "UCP",
            "AP2",
            "x402",
            "MPP",
            "TAP",
            "Mastercard Agent Pay",
            "Hive Transparency Log",
            "draft-hood-agtp-log",
            "Agent Record",
            "Gate",
        ):
            self.assertIn(name, body)
        self.assertIn("shipping", body)
        self.assertIn("draft", body)
        self.assertIn("proposed", body)
        self.assertIn("atxp.ai/blog/agent-payment-protocols-compared", body)
        self.assertIn("agenticcommerceprotocol.info/radar", body)
        self.assertIn("kya.fi/standards-tracker", body)
        self.assertIn("not production-hardened", body)
        self.assertIn("production-shippable at Gate", body)
        self.assertNotIn("btn-primary", body)
        self.assertNotRegex(body, r"(?i)payto")
        self.assertNotRegex(body, r"(?i)\$99")
        self.assertNotIn("/billing/checkout", body)
        self.assertNotIn("/operator/checkout", body)
        self.assertIn("<svg", body)
        self.assertIn("index,follow", body)

    def test_json_and_index_hooks(self):
        j = self.client.get("/.well-known/evidence-layer.json")
        self.assertEqual(j.status_code, 200)
        data = j.get_json()
        self.assertEqual(data["spec"], el.SPEC)
        self.assertTrue(data["not_a_sku"])
        self.assertFalse(data["production_hardened"])
        ids = [ln["id"] for ln in data["lanes"]]
        self.assertEqual(ids, ["identity", "payment", "evidence"])
        self.assertTrue(data["lanes"][2]["entries"][-1]["self"])
        sm = self.client.get("/sitemap.xml").get_data(as_text=True)
        self.assertIn("/evidence-layer", sm)
        llms = self.client.get("/llms.txt").get_data(as_text=True)
        self.assertIn("/evidence-layer", llms)
        gate = self.client.get("/.well-known/gate.json").get_json()
        self.assertTrue(gate["evidence_layer"].endswith("/evidence-layer"))


if __name__ == "__main__":
    unittest.main()
