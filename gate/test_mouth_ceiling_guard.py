"""Mouth Ceiling guard tests."""
from __future__ import annotations

import unittest

import app as gate_app


class MouthCeilingGuardTests(unittest.TestCase):
    def setUp(self):
        gate_app.app.config["TESTING"] = True
        self.client = gate_app.app.test_client()

    def test_mouth_ceiling_guard_passes_frozen_inventory(self):
        try:
            from gate.mouth_ceiling_guard import mouth_ceiling_check
        except ImportError:
            from mouth_ceiling_guard import mouth_ceiling_check

        result = mouth_ceiling_check()
        self.assertTrue(result["ok"], result.get("message"))
        self.assertNotEqual(result["code"], "mouth_ceiling_new_l2_modules")

    def test_ops_guards_includes_mouth_ceiling(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        guards = r.get_json().get("guards") or {}
        self.assertIn("mouth_ceiling", guards)

    def test_licensing_pack_gate1_docs(self):
        r = self.client.get("/.well-known/licensing-pack.json")
        docs = {d["id"]: d["path"] for d in r.get_json()["documents"]}
        self.assertEqual(docs["licensed_field_value"], "gate/LICENSED_FIELD_VALUE.md")
        self.assertEqual(docs["patent_counsel_brief"], "gate/PATENT_COUNSEL_BRIEF.md")
        self.assertEqual(docs["wealth_apparatus_freeze"], "gate/WEALTH_APPARATUS_FREEZE.md")

    def test_nisaba_wyoming_in_term_sheet(self):
        from pathlib import Path

        text = Path(__file__).resolve().parent / "PATENT_LICENSE_TERM_SHEET.md"
        body = text.read_text(encoding="utf-8")
        self.assertIn("Wyoming", body)
        self.assertNotIn("Delaware", body)

    def test_patent_counsel_brief_narrow_scope(self):
        from pathlib import Path

        brief = (Path(__file__).resolve().parent / "PATENT_COUNSEL_BRIEF.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("epoch lock", brief.lower())
        self.assertIn("single-use", brief.lower())
        self.assertIn("Do NOT send counsel", brief)
        self.assertIn("micro-entity", brief.lower())
        self.assertIn("flat-fee", brief.lower())
        self.assertIn("IBCT", brief)
        self.assertIn("macaroon", brief.lower())


if __name__ == "__main__":
    unittest.main()
