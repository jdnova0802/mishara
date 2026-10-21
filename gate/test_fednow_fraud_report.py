"""FedNow OC-8 Appendix C fraud-report pack mouth."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-fednow-fraud.db")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import mouths  # noqa: E402
import app as gate_app  # noqa: E402


class FedNowFraudReportMouthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = gate_app.app.test_client()

    def test_manifest_and_page(self):
        wk = self.client.get("/.well-known/fednow-fraud-report.json")
        self.assertEqual(wk.status_code, 200)
        self.assertEqual(wk.get_json()["spec"], "gate-fednow-fraud-report-v1")
        page = self.client.get("/fednow-fraud-report")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"FedNow", page.data)
        gate = self.client.get("/.well-known/gate.json").get_json()
        self.assertIn("fednow_fraud_report", gate)

    def test_reportable_packs_no_transmit(self):
        out = mouths.evaluate(
            "fednow-fraud-report",
            {
                "caller_is_fednow_participant": "yes",
                "report_role": "sender",
                "investigated_unusual_payment_order": "yes",
                "good_faith_fraud_reportable": "yes",
                "has_underlying_facts": "yes",
            },
        )
        self.assertEqual(out["word"], "REPORTABLE")
        pack = out["report_pack"]
        self.assertFalse(pack["gate_transmits_to_fednow"])
        self.assertIn("FRAD", pack["suggested_iso_path"])
        self.assertIn("deny_registry.payout_hash", " ".join(pack["suggested_payload_fields"]))
        self.assertTrue(out["signed_claim"]["claim_hash"])
        self.assertTrue(out["not_a_bounty"])
        self.assertTrue(out["gate_is_not_fedline_endpoint"])

    def test_not_this_when_not_participant(self):
        out = mouths.evaluate(
            "fednow-fraud-report",
            {
                "caller_is_fednow_participant": "no",
                "report_role": "sender",
                "investigated_unusual_payment_order": "yes",
                "good_faith_fraud_reportable": "yes",
                "has_underlying_facts": "yes",
            },
        )
        self.assertEqual(out["word"], "NOT THIS")

    def test_hold_when_not_investigated(self):
        out = mouths.evaluate(
            "fednow-fraud-report",
            {
                "caller_is_fednow_participant": "yes",
                "report_role": "receiver",
                "investigated_unusual_payment_order": "no",
                "good_faith_fraud_reportable": "yes",
                "has_underlying_facts": "yes",
            },
        )
        self.assertEqual(out["word"], "HOLD")
        self.assertIn("investigate", out["report_pack"]["checklist"][1].lower())


if __name__ == "__main__":
    unittest.main()
