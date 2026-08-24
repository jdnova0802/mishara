"""Tests for Invisible Staple Scale."""
from __future__ import annotations

import unittest

try:
    from gate import invisible_scale as inv
except ImportError:
    import invisible_scale as inv


class InvisibleScaleTests(unittest.TestCase):
    def test_manifest_full_diet(self):
        m = inv.manifest("https://gate.example")
        self.assertEqual(len(m["staples"]), 44)
        self.assertEqual(m["counts"]["cbr"], 8)
        self.assertEqual(m["counts"]["hate"], 15)
        self.assertEqual(m["counts"]["bedrock"], 9)
        self.assertTrue(m["not_outbound"])

    def test_bedrock_unit(self):
        u = next(s for s in inv.STAPLES if s["slug"] == "may_unit_of_account")
        self.assertEqual(u["score"], -10)
        self.assertEqual(u["zone"], "bedrock")

    def test_hate_unpaid(self):
        r = inv.evaluate_hate(
            would_irreversible_write=True,
            desk_rent_current=False,
        )
        self.assertEqual(r["verdict"], "HATE_UNPAID")
        self.assertIn("desk_rent", r["blockers"])

    def test_staple_with_hate(self):
        r = inv.evaluate_staple(
            would_irreversible_write=True,
            act_serial="act_1",
            who_field="desk-a",
            when_stamp="2026-08-24T00:00:00Z",
            mass_number=3,
            verify_stub="https://v/1",
            hate_check=True,
            desk_rent_current=False,
        )
        self.assertEqual(r["verdict"], "HATE_UNPAID")

    def test_staple_starved(self):
        r = inv.evaluate_staple(would_irreversible_write=True)
        self.assertEqual(r["verdict"], "STAPLE_STARVED")
        self.assertIn("act_serial", r["missing"])

    def test_staple_fed(self):
        r = inv.evaluate_staple(
            would_irreversible_write=True,
            act_serial="act_1",
            who_field="desk-a",
            when_stamp="2026-08-24T00:00:00Z",
            mass_number=3,
            verify_stub="https://v/1",
        )
        self.assertEqual(r["verdict"], "STAPLE_FED")

    def test_attach_halts_starved(self):
        plan = {
            "cbr_check": True,
            "decision": "ALLOW",
            "allow_bind": True,
            "would_bind": True,
        }
        inv.attach(plan, public_url="https://gate.example")
        self.assertEqual(plan["invisible_scale"]["verdict"], "STAPLE_STARVED")
        self.assertEqual(plan.get("decision"), "HALT")

    def test_bone_law_is_ten(self):
        bone = next(s for s in inv.STAPLES if s["slug"] == "bone_law")
        self.assertEqual(bone["score"], 10)
        serial = next(s for s in inv.STAPLES if s["slug"] == "act_serial")
        self.assertEqual(serial["score"], 0)


if __name__ == "__main__":
    unittest.main()
