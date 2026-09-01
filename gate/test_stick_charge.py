"""Tests for Stick Meter + Charge Bride foothill inventions."""
from __future__ import annotations

import os
import unittest

try:
    from gate import stick_meter as stick_mod
    from gate import charge_bride as bride_mod
except ImportError:
    import stick_meter as stick_mod
    import charge_bride as bride_mod


class StickMeterTests(unittest.TestCase):
    def test_light_bind(self):
        r = stick_mod.score(write_kind="bind")
        self.assertEqual(r["mass_class"], stick_mod.CLASS_LIGHT)
        self.assertLess(r["score"], 40)

    def test_heavy_premium_over_limit(self):
        r = stick_mod.score(
            write_kind="bind",
            premium=60000,
            authority_limit=50000,
            would_bind=True,
        )
        self.assertGreaterEqual(r["score"], 40)
        self.assertEqual(r["mass_class"], stick_mod.CLASS_HEAVY)

    def test_sacred_dead_fuse(self):
        r = stick_mod.score(
            write_kind="payout",
            premium=90000,
            authority_limit=50000,
            fuse_state="DEAD",
            epoch_locked=True,
            sanction_flag=True,
            would_bind=True,
        )
        self.assertGreaterEqual(r["score"], 75)
        self.assertEqual(r["mass_class"], stick_mod.CLASS_SACRED)

    def test_attach_stamps_plan(self):
        plan = {"allow_bind": True, "premium": 70000, "authority_limit": 50000}
        stick_mod.attach(plan)
        self.assertIn("stick_meter", plan)
        self.assertIn(plan["mass_class"], (stick_mod.CLASS_HEAVY, stick_mod.CLASS_SACRED))

    def test_manifest(self):
        m = stick_mod.manifest("https://gate.example")
        self.assertEqual(m["spec"], stick_mod.SPEC)
        self.assertIn("demo", m)


class ChargeBrideTests(unittest.TestCase):
    def test_uw_forged(self):
        r = bride_mod.evaluate(
            fuse_state="DEAD",
            uw_approved=True,
            would_proceed=True,
        )
        self.assertEqual(r["verdict"], bride_mod.VERDICT_FORGED)
        self.assertIn(bride_mod.FORGED_UW, r["forged"])
        self.assertFalse(r["may_proceed"])

    def test_chat_forged(self):
        r = bride_mod.evaluate(
            epoch_locked=True,
            chat_yes=True,
            would_proceed=True,
        )
        self.assertEqual(r["verdict"], bride_mod.VERDICT_FORGED)
        self.assertIn(bride_mod.FORGED_CHAT, r["forged"])

    def test_clear_no_resurrection(self):
        r = bride_mod.evaluate(fuse_state="LIVE", uw_approved=True)
        self.assertEqual(r["verdict"], bride_mod.VERDICT_CLEAR)

    def test_charge_required(self):
        r = bride_mod.evaluate(fuse_state="DEAD", would_proceed=True)
        self.assertEqual(r["verdict"], bride_mod.VERDICT_CHARGE_REQUIRED)

    def test_dev_charge_ok(self):
        prev = os.environ.get("GATE_DEV_MODE")
        os.environ["GATE_DEV_MODE"] = "1"
        try:
            r = bride_mod.evaluate(
                fuse_state="DEAD",
                charge_id="chg_test_bride",
                would_proceed=True,
                purpose="epoch",
                subject="pc:TEST",
            )
            self.assertEqual(r["verdict"], bride_mod.VERDICT_CHARGE_OK)
            self.assertTrue(r["may_proceed"])
        finally:
            if prev is None:
                os.environ.pop("GATE_DEV_MODE", None)
            else:
                os.environ["GATE_DEV_MODE"] = prev

    def test_attach_halts_forged(self):
        plan = {"allow_bind": True, "uw_approved": True, "fuse_state": "DEAD"}
        bride_mod.attach(plan, epoch_meta={"locked": False})
        self.assertEqual(plan["charge_bride"]["verdict"], bride_mod.VERDICT_FORGED)
        self.assertFalse(plan["allow_bind"])
        self.assertEqual(plan["decision"], "HALT")

    def test_drills_all_ok(self):
        report = bride_mod.run_drills()
        self.assertTrue(report["all_ok"], report["drills"])

    def test_manifest(self):
        m = bride_mod.manifest("https://gate.example")
        self.assertEqual(m["spec"], bride_mod.SPEC)
        self.assertIn("drills", m)


class InventionQuadTests(unittest.TestCase):
    def test_stick_before_throat_on_heavy(self):
        plan = {
            "decision": "ALLOW",
            "allow_bind": True,
            "premium": 80000,
            "authority_limit": 50000,
            "fuse_state": "DEAD",
            "uw_approved": True,
        }
        bride_mod.attach(plan, epoch_meta={"locked": False})
        self.assertFalse(plan["allow_bind"])
        stick_mod.attach(plan)
        self.assertEqual(plan["stick_meter"]["mass_class"], stick_mod.CLASS_SACRED)


if __name__ == "__main__":
    unittest.main()
