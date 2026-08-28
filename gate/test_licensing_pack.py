"""Formal licensing pack well-known routes."""
from __future__ import annotations

import unittest

import app as gate_app

try:
    from gate import licensing_pack as lp
except ImportError:
    import licensing_pack as lp


class LicensingPackTests(unittest.TestCase):
    def setUp(self):
        gate_app.app.config["TESTING"] = True
        self.client = gate_app.app.test_client()

    def test_pack_manifest(self):
        r = self.client.get("/.well-known/licensing-pack.json")
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(body["spec"], "gate-licensing-pack-v1")
        self.assertEqual(body["patent"], "64/124,027")
        self.assertIn("I", body["exhibits"])
        self.assertIn("premium_bps_meter", body["formal_modules"])

    def test_premium_bps_schedule_exhibit_i(self):
        r = self.client.get("/.well-known/premium-bps-schedule.json")
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(body["spec"], "gate-premium-bps-schedule-v1")
        self.assertEqual(body["exhibit"], "I")
        self.assertIn("formula", body)

    def test_gate_conformant_mark_spec_exhibit_j(self):
        r = self.client.get("/.well-known/gate-conformant-mark-spec.json")
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(body["spec"], "gate-conformant-mark-spec-v1")
        self.assertEqual(body["exhibit"], "J")
        self.assertIn("requirements", body)

    def test_qic_meter_exhibit_k(self):
        r = self.client.get("/.well-known/qic-meter.json")
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(body["spec"], "gate-qic-meter-v1")
        self.assertEqual(body["billable_formula"], "max(MAR, LAQ × per_QIC_rate)")

    def test_commit_auth_points_at_pack(self):
        r = self.client.get("/.well-known/commit-auth.json")
        self.assertEqual(r.status_code, 200)
        pl = r.get_json()["patent_licensing"]
        self.assertEqual(pl["status"], "formal_draft_counsel_review")
        self.assertIn("licensing-pack.json", pl["well_known_pack"])


if __name__ == "__main__":
    unittest.main()
