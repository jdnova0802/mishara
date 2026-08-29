"""Owner guardrails well-known route."""
from __future__ import annotations

import unittest

import app as gate_app


class OwnerGuardrailsTests(unittest.TestCase):
    def setUp(self):
        gate_app.app.config["TESTING"] = True
        self.client = gate_app.app.test_client()

    def test_personal_wire_calculator_presets(self):
        r = self.client.get("/.well-known/personal-wire-calculator.json")
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(body["spec"], "gate-personal-wire-calculator-v1")
        presets = {p["label"]: p for p in body["example_presets"]}
        ten_m = presets["ten_m_company"]["personal_pretax"]["total_annual_usd"]
        self.assertGreater(ten_m, 2_000_000)

    def test_personal_wire_demo_post(self):
        r = self.client.post(
            "/demo/pas/personal-wire-calculator",
            json={
                "company_gross_annual_usd": 2_000_000,
                "opex_annual_usd": 400_000,
                "salary_annual_usd": 100_000,
                "reserve_funded": True,
            },
        )
        self.assertEqual(r.status_code, 200)
        wire = r.get_json()["personal_pretax"]
        self.assertAlmostEqual(wire["owner_distribution_annual_usd"], 450_000, delta=1)
        self.assertAlmostEqual(wire["total_annual_usd"], 550_000, delta=1)

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
        self.assertIn("entity_map", docs)
        self.assertIn("personal_liquidity_stub", docs)
        self.assertIn("pilot_contract_stub", docs)

    def test_owner_guardrails_entity_and_liquidity_docs(self):
        r = self.client.get("/.well-known/owner-guardrails.json")
        body = r.get_json()
        docs = body["documents"]
        self.assertEqual(docs["entity_map"], "gate/ENTITY_MAP.md")
        self.assertEqual(docs["personal_liquidity_stub"], "gate/PERSONAL_LIQUIDITY_STUB.md")
        self.assertIn("entity_map_holdco_opco_personal_layers", body["ownership_checklist_summary"])

    def test_wire_calculator_recurring_nine_figure_context(self):
        r = self.client.get("/.well-known/personal-wire-calculator.json")
        ctx = r.get_json()["income_context"]
        self.assertIn("hundred_m_plus_recurring_takehome_structured_global", ctx)


if __name__ == "__main__":
    unittest.main()
