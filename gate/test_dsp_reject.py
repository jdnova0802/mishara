"""DOJ DSP § 202.1104 reject-report mouth."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-dsp-reject.db")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import mouths  # noqa: E402
import app as gate_app  # noqa: E402


class DspRejectMouthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = gate_app.app.test_client()

    def test_manifest_and_page(self):
        wk = self.client.get("/.well-known/dsp-reject.json")
        self.assertEqual(wk.status_code, 200)
        self.assertEqual(wk.get_json()["spec"], "gate-dsp-reject-v1")
        page = self.client.get("/dsp-reject")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"DSP Reject", page.data)
        gate = self.client.get("/.well-known/gate.json").get_json()
        self.assertIn("dsp_reject", gate)

    def test_report_due_packs_clock_and_mailto(self):
        rejected = "2026-09-20T12:00:00+00:00"
        out = mouths.evaluate(
            "dsp-reject",
            {
                "data_brokerage_offer": "yes",
                "bulk_sensitive_or_gov_data": "yes",
                "counterparty_covered_or_coc": "yes",
                "affirmatively_rejected": "yes",
                "rejected_on_or_after_2025_10_06": "yes",
                "reject_date": rejected,
            },
        )
        self.assertEqual(out["word"], "REPORT DUE")
        pack = out["report_pack"]
        self.assertEqual(pack["submit_to"], "NSD.FIRS.datasecurity@usdoj.gov")
        self.assertFalse(pack["gate_files_for_you"])
        self.assertIn("mailto:NSD.FIRS.datasecurity@usdoj.gov", pack["mailto"])
        due = datetime.fromisoformat(pack["due_at"])
        start = datetime.fromisoformat(rejected)
        self.assertEqual(due - start, timedelta(days=14))
        self.assertEqual(out["write_state"]["phase"], "IN_FLIGHT")
        self.assertFalse(out["write_state"]["cancellable"])
        self.assertIn("claim_scope", out)
        self.assertTrue(out["signed_claim"]["claim_hash"])
        self.assertFalse(out["covered_persons_list_exhaustive"])

    def test_not_this_when_not_brokerage(self):
        out = mouths.evaluate(
            "dsp-reject",
            {
                "data_brokerage_offer": "no",
                "bulk_sensitive_or_gov_data": "yes",
                "counterparty_covered_or_coc": "yes",
                "affirmatively_rejected": "yes",
                "rejected_on_or_after_2025_10_06": "yes",
            },
        )
        self.assertEqual(out["word"], "NOT THIS")

    def test_hold_unknown_covered_person(self):
        out = mouths.evaluate(
            "dsp-reject",
            {
                "data_brokerage_offer": "yes",
                "bulk_sensitive_or_gov_data": "yes",
                "counterparty_covered_or_coc": "unknown",
                "affirmatively_rejected": "yes",
                "rejected_on_or_after_2025_10_06": "yes",
            },
        )
        self.assertEqual(out["word"], "HOLD")

    def test_hold_before_reject(self):
        out = mouths.evaluate(
            "dsp-reject",
            {
                "data_brokerage_offer": "yes",
                "bulk_sensitive_or_gov_data": "yes",
                "counterparty_covered_or_coc": "yes",
                "affirmatively_rejected": "no",
                "rejected_on_or_after_2025_10_06": "yes",
            },
        )
        self.assertEqual(out["word"], "HOLD")

    def test_api_post(self):
        r = self.client.post(
            "/v1/dsp-reject",
            json={
                "data_brokerage_offer": "yes",
                "bulk_sensitive_or_gov_data": "yes",
                "counterparty_covered_or_coc": "yes",
                "affirmatively_rejected": "yes",
                "rejected_on_or_after_2025_10_06": "yes",
            },
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["word"], "REPORT DUE")


if __name__ == "__main__":
    unittest.main()
