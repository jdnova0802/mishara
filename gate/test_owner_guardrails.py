"""Owner guardrails well-known route."""
from __future__ import annotations

import unittest

import app as gate_app


class OwnerGuardrailsTests(unittest.TestCase):
    def setUp(self):
        gate_app.app.config["TESTING"] = True
        self.client = gate_app.app.test_client()

    def test_owner_guardrails_manifest(self):
        r = self.client.get("/.well-known/owner-guardrails.json")
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(body["spec"], "gate-owner-guardrails-v1")
        self.assertEqual(body["operator"], "Nisaba LLC")
        self.assertEqual(body["distribution_policy"]["buckets"]["owner_distribution"], 0.30)
        self.assertTrue(body["pilot_guardrails"]["no_personal_guarantee"])
        self.assertIn("No IP assignment", body["pilot_guardrails"]["ip_non_assign_one_liner"])

    def test_licensing_pack_links_guardrails_docs(self):
        r = self.client.get("/.well-known/licensing-pack.json")
        self.assertEqual(r.status_code, 200)
        docs = {d["id"]: d["path"] for d in r.get_json()["documents"]}
        self.assertIn("distribution_policy", docs)
        self.assertIn("pilot_contract_stub", docs)


if __name__ == "__main__":
    unittest.main()
