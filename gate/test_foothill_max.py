"""Tests for Foothill Max Pack — remaining software mouth seeds."""
from __future__ import annotations

import unittest

try:
    from gate import foothill_max as fm
except ImportError:
    import foothill_max as fm


class FoothillMaxTests(unittest.TestCase):
    def test_tool_throat_choke(self):
        r = fm.tool_throat_evaluate(
            tool_name="bind_and_issue",
            irreversible=True,
            soft_prompt_yes=True,
        )
        self.assertEqual(r["verdict"], "TOOL_CHOKE")
        self.assertFalse(r["may_proceed"])

    def test_time_lock_sealed(self):
        r = fm.time_lock_evaluate(
            now="2026-01-01T00:00:00Z",
            unlock_at="2026-06-01T00:00:00Z",
        )
        self.assertEqual(r["verdict"], "TIME_LOCKED")
        self.assertFalse(r["may_proceed"])

    def test_charisma_forged(self):
        r = fm.charisma_nullifier_evaluate(boss_said_yes=True, synthetic_voice=True)
        self.assertEqual(r["verdict"], "CHARISMA_FORGED")
        self.assertTrue(r["forged"])

    def test_sabbath_deny(self):
        r = fm.sabbath_latch_evaluate(sabbath_active=True, would_commit=True)
        self.assertEqual(r["verdict"], "SABBATH_DENY")

    def test_quarantine(self):
        r = fm.may_quarantine_evaluate(
            quarantined=True, principal_id="p1", requesting_live=True
        )
        self.assertEqual(r["verdict"], "QUARANTINE_DENY")

    def test_tombstone(self):
        r = fm.branch_tombstone_evaluate(halted=True, acted=False, branch_id="b1")
        self.assertEqual(r["verdict"], "TOMBSTONE_MINTED")
        self.assertTrue(r["tombstone_id"].startswith("tomb_"))

    def test_secure_macro_deny(self):
        r = fm.secure_write_macro_evaluate(
            command_class="actuator_release",
            approved_classes=["status_read"],
            would_write=True,
        )
        self.assertEqual(r["verdict"], "MACRO_DENY")

    def test_dose_choke(self):
        r = fm.dose_throat_evaluate(dose_irreversible=True, panic_push=True)
        self.assertEqual(r["verdict"], "DOSE_CHOKE")

    def test_jubilee_due(self):
        r = fm.jubilee_clock_evaluate(
            now="2026-08-24T00:00:00Z",
            jubilee_at="2026-01-01T00:00:00Z",
            may_retired=False,
        )
        self.assertEqual(r["verdict"], "JUBILEE_DUE")

    def test_antimay(self):
        r = fm.antimay_evaluate(spoofed_live=True)
        self.assertEqual(r["verdict"], "ANTIMAY_TRIPPED")

    def test_senate_short(self):
        r = fm.senate_socket_soft_evaluate(
            mass_class="sacred", required_n=2, approvals=["a"]
        )
        self.assertEqual(r["verdict"], "SENATE_SHORT")

    def test_receipt_stone(self):
        r = fm.receipt_stone_stamp(event_id="e1", verify_url="https://v/1")
        self.assertTrue(r["stone_id"].startswith("stone_"))

    def test_attach_blocks_charisma(self):
        plan = {
            "decision": "ALLOW",
            "allow_bind": True,
            "boss_said_yes": True,
            "mass_tag": {"mass_class": "sacred"},
        }
        fm.attach(plan, public_url="https://gate.example")
        self.assertIn("charisma_nullifier", plan["foothill_max"]["blockers"])
        self.assertEqual(plan.get("decision"), "HALT")

    def test_manifest_count(self):
        m = fm.manifest("https://gate.example")
        self.assertEqual(m["count"], 12)
        self.assertEqual(len(fm.INVENTIONS), 12)


if __name__ == "__main__":
    unittest.main()
