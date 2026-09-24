"""Fail-closed tests for the Colorado 6-1-1703 packet clerk."""
from __future__ import annotations

import os
import unittest

from packet import build_packet, packet_markdown

BASE = {
    "deployer_name": "Front Range Credit Union",
    "third_party_name": "Nisaba LLC",
    "system_name": "LoanDesk Ranker",
    "kind": "initial",
    "assessment_date": "2026-06-15",
    "consequential_decision": "lending",
    "purpose": "Rank unsecured consumer applications for underwriter review.",
    "intended_uses": "Colorado-resident unsecured personal loans under $25,000.",
    "deployment_context": "Used inside the credit union; underwriter must accept or override.",
    "benefits": "Faster queue; same credit-policy grid as the 2024 manual.",
    "discrimination_risks": "Zip and proxy features can tilt denial rates by race and national origin.",
    "discrimination_mitigations": "Zip dropped; annual disparate-impact table by race/ethnicity/sex; human override logged.",
    "inputs": "Application fields, bureau score, internal deposit history. No facial data.",
    "outputs": "Rank 1–99 plus a reason code for the underwriter.",
    "metrics_limitations": "KS test on score by protected class quarterly; known limit: thin-file applicants.",
    "transparency": "Adverse-action notice names the system and offers a contact.",
    "monitoring_safeguards": "Weekly override review; model freeze if DI ratio < 0.8 until counsel signs.",
    "discrimination_review": "2026-06-01 review found no unresolved algorithmic discrimination on the 2025 book.",
}


class PacketTest(unittest.TestCase):
    def test_emits_statutory_cites(self):
        packet, errors = build_packet(BASE)
        self.assertEqual(errors, [])
        self.assertIsNotNone(packet)
        cites = [s["cite"] for s in packet["sections"]]
        self.assertIn("6-1-1703(3)(b)(I)", cites)
        self.assertIn("6-1-1703(3)(b)(VII)", cites)
        self.assertIn("6-1-1703(3)(g)", cites)
        self.assertNotIn("6-1-1703(3)(c)", cites)
        self.assertTrue(packet["not_legal_advice"])
        self.assertTrue(packet["not_remaining"])
        self.assertEqual(packet["effective_date"], "2026-06-30")
        self.assertEqual(len(packet["packet_sha256"]), 64)
        md = packet_markdown(packet)
        self.assertIn("6-1-1703(3)(b)(II)", md)
        self.assertIn("three years", md)

    def test_blank_fails_closed(self):
        src = dict(BASE)
        src["purpose"] = "  "
        packet, errors = build_packet(src)
        self.assertIsNone(packet)
        self.assertTrue(any("purpose" in e for e in errors))

    def test_modification_requires_variance_statement(self):
        src = dict(BASE)
        src["kind"] = "modification"
        packet, errors = build_packet(src)
        self.assertIsNone(packet)
        self.assertTrue(any("6-1-1703(3)(c)" in e for e in errors))
        src["use_vs_developer_intent"] = "Used only for the intended unsecured book; no auto-decision."
        packet, errors = build_packet(src)
        self.assertEqual(errors, [])
        self.assertEqual(packet["sections"][-1]["cite"], "6-1-1703(3)(c)")

    def test_customization_requires_categories(self):
        src = dict(BASE)
        src["used_customization_data"] = "yes"
        packet, errors = build_packet(src)
        self.assertIsNone(packet)
        src["customization_data"] = "Internal 2024–2025 originations, no vendor scores."
        packet, errors = build_packet(src)
        self.assertEqual(errors, [])
        self.assertTrue(packet["sections"][3]["used"])

    def test_bad_decision_rejected(self):
        src = dict(BASE)
        src["consequential_decision"] = "marketing"
        packet, errors = build_packet(src)
        self.assertIsNone(packet)


class AppTest(unittest.TestCase):
    def setUp(self):
        os.environ.setdefault("ASSESSMENT_CONTACT_EMAIL", "hello@velaru.xyz")
        import app as assessment_app

        self.c = assessment_app.app.test_client()

    def test_health_and_home(self):
        h = self.c.get("/health")
        self.assertEqual(h.status_code, 200)
        self.assertEqual(h.get_json()["service"], "colorado-assessment")
        self.assertEqual(self.c.get("/").status_code, 200)

    def test_packet_route_fail_closed(self):
        r = self.c.post("/packet", json={"deployer_name": "x"})
        self.assertEqual(r.status_code, 400)
        self.assertFalse(r.get_json()["ok"])

    def test_packet_route_ok(self):
        r = self.c.post("/packet", json=BASE)
        self.assertEqual(r.status_code, 200, r.get_data(as_text=True))
        body = r.get_json()
        self.assertTrue(body["ok"])
        self.assertIn("markdown", body)
        self.assertEqual(body["packet"]["deployer_name"], BASE["deployer_name"])


if __name__ == "__main__":
    unittest.main()
