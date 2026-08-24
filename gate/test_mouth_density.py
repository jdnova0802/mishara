"""Tests for Mouth Density Pack — eight foothill densifiers."""
from __future__ import annotations

import unittest

try:
    from gate import mouth_density as md
except ImportError:
    import mouth_density as md


class MouthDensityTests(unittest.TestCase):
    def test_stale_live_forged(self):
        r = md.stale_live_evaluate(
            live_issued_at="2020-01-01T00:00:00Z",
            decision="LIVE",
            would_act=True,
        )
        self.assertEqual(r["verdict"], "STALE_FORGED")
        self.assertTrue(r["forged"])
        self.assertFalse(r["may_proceed"])

    def test_cool_off_sacred(self):
        r = md.cool_off_evaluate(mass_class="sacred")
        self.assertEqual(r["verdict"], "COOL_HOLD")
        self.assertFalse(r["may_proceed"])

    def test_cool_skip_forged(self):
        r = md.cool_off_evaluate(mass_class="heavy", skip_attempt=True)
        self.assertEqual(r["verdict"], "COOL_SKIP_FORGED")

    def test_silence_anti_perimeter(self):
        r = md.silence_gate_evaluate(loss_of_contact=True, would_auto_live=True)
        self.assertEqual(r["verdict"], "SILENCE_ANTI_PERIMETER")
        self.assertFalse(r["may_proceed"])

    def test_algedonic_escalate(self):
        r = md.algedonic_evaluate(
            local_hold_seconds=20000,
            escalate_after_seconds=14400,
            unresolved=True,
            job_id="pc:1",
        )
        self.assertEqual(r["verdict"], "ESCALATE")
        self.assertTrue(r["escalate"])
        self.assertIsNotNone(r["packet"])

    def test_may_budget_exhausted(self):
        r = md.may_budget_evaluate(
            sacred_live_limit=2,
            sacred_lives_used=2,
            requesting_sacred_live=True,
        )
        self.assertEqual(r["verdict"], "BUDGET_EXHAUSTED")
        self.assertFalse(r["may_proceed"])

    def test_funeral_kills_may(self):
        r = md.funeral_bit_evaluate(decommission=True, may_hooks_remain=False)
        self.assertEqual(r["verdict"], "MAY_DEAD")
        self.assertTrue(r["may_dead"])

    def test_genealogy_stamp(self):
        r = md.bind_genealogy_stamp(job_id="pc:9", skin="gate_c")
        self.assertTrue(r["stamp_id"].startswith("gen_"))

    def test_cold_weld_incomplete(self):
        r = md.cold_weld_evaluate(first_production=True)
        self.assertEqual(r["verdict"], "COLD_WELD_INCOMPLETE")
        self.assertIn("genesis_receipt", r["missing"])

    def test_cold_weld_ready(self):
        r = md.cold_weld_evaluate(
            first_production=True,
            genesis_done=True,
            throat_pinned=True,
            ghost_drill_passed=True,
            witness_present=True,
        )
        self.assertEqual(r["verdict"], "COLD_WELD_READY")
        self.assertTrue(r["may_proceed"])

    def test_attach_blocks_silence(self):
        plan = {
            "decision": "ALLOW",
            "allow_bind": True,
            "loss_of_link": True,
            "would_auto_live": True,
            "mass_tag": {"mass_class": "light"},
        }
        md.attach(plan, public_url="https://gate.example")
        self.assertIn("silence_gate", plan["mouth_density"]["blockers"])
        self.assertFalse(plan.get("allow_bind"))
        self.assertEqual(plan.get("decision"), "HALT")

    def test_manifest_count(self):
        m = md.manifest("https://gate.example")
        self.assertEqual(m["count"], 8)
        self.assertEqual(len(md.INVENTIONS), 8)


if __name__ == "__main__":
    unittest.main()
