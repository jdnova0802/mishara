"""Tests for Throat + Ghost Bind foothill inventions."""
from __future__ import annotations

import unittest

try:
    from gate import throat as throat_mod
    from gate import ghost_bind as ghost_bind_mod
except ImportError:
    import throat as throat_mod
    import ghost_bind as ghost_bind_mod


class ThroatTests(unittest.TestCase):
    def test_open_on_live(self):
        r = throat_mod.evaluate(decision="ALLOW", allow_bind=True)
        self.assertEqual(r["state"], throat_mod.OPEN)
        self.assertTrue(r["may_proceed"])

    def test_closed_on_halt(self):
        r = throat_mod.evaluate(decision="HALT", halt=True)
        self.assertEqual(r["state"], throat_mod.CLOSED)
        self.assertTrue(r["deny_proved"])
        self.assertFalse(r["may_proceed"])

    def test_choke_on_timeout(self):
        r = throat_mod.evaluate(timeout=True, decision="ALLOW")
        self.assertEqual(r["state"], throat_mod.CHOKE)
        self.assertTrue(r["fail_closed"])
        self.assertIn(throat_mod.REASON_TIMEOUT, r["reasons"])

    def test_choke_on_soft_pas(self):
        r = throat_mod.evaluate(soft_pas=True)
        self.assertEqual(r["state"], throat_mod.CHOKE)
        self.assertIn(throat_mod.REASON_SOFT_CONFIG, r["reasons"])

    def test_choke_on_sight_only(self):
        r = throat_mod.evaluate(sight_only=True, decision="ALLOW")
        self.assertEqual(r["state"], throat_mod.CHOKE)

    def test_choke_on_boss(self):
        r = throat_mod.evaluate(boss_said_yes=True, decision="ALLOW", allow_bind=True)
        self.assertEqual(r["state"], throat_mod.CHOKE)
        self.assertIn(throat_mod.REASON_CHARISMA, r["reasons"])

    def test_choke_missing_decision(self):
        r = throat_mod.evaluate()
        self.assertEqual(r["state"], throat_mod.CHOKE)

    def test_attach_chokes_plan(self):
        plan = {"timeout": True, "allow_bind": True, "decision": "ALLOW"}
        throat_mod.attach(plan)
        self.assertEqual(plan["throat"]["state"], throat_mod.CHOKE)
        self.assertFalse(plan["allow_bind"])
        self.assertEqual(plan["decision"], "HALT")

    def test_manifest(self):
        m = throat_mod.manifest("https://gate.example")
        self.assertEqual(m["spec"], throat_mod.SPEC)
        self.assertIn("demo", m)


class GhostBindTests(unittest.TestCase):
    def test_soft_pas_haunts(self):
        r = ghost_bind_mod.scan({"soft_pas": True, "would_bind": True})
        self.assertTrue(r["haunted"])
        self.assertTrue(r["critical"])
        self.assertEqual(r["verdict"], "HAUNTED_CRITICAL")

    def test_timeout_as_live(self):
        r = ghost_bind_mod.scan({"timeout": True, "decision": "ALLOW"})
        self.assertTrue(r["haunted"])
        ghosts = {g["ghost"] for g in r["ghosts"]}
        self.assertIn(ghost_bind_mod.GHOST_TIMEOUT_AS_LIVE, ghosts)

    def test_clean_clear(self):
        r = ghost_bind_mod.scan(
            {
                "throat_present": True,
                "hop_required": True,
                "decision": "HALT",
                "would_bind": False,
                "verify_url": "https://x/v",
            }
        )
        self.assertFalse(r["haunted"])
        self.assertEqual(r["verdict"], "CLEAR")

    def test_drills_all_ok(self):
        report = ghost_bind_mod.run_drills()
        self.assertTrue(report["all_ok"], report["drills"])

    def test_attach_haunt(self):
        plan = {"decision": "ALLOW", "allow_bind": True, "soft_pas": True}
        ghost_bind_mod.attach_haunt(plan)
        self.assertTrue(plan["ghost_bind"]["haunted"])

    def test_manifest(self):
        m = ghost_bind_mod.manifest("https://gate.example")
        self.assertEqual(m["spec"], ghost_bind_mod.SPEC)
        self.assertIn("ghost_classes", m)


class InventionPairTests(unittest.TestCase):
    def test_both_on_soft_would_bind(self):
        plan = {
            "decision": "ALLOW",
            "allow_bind": True,
            "soft_pas": True,
            "acted": False,
        }
        throat_mod.attach(plan)
        ghost_bind_mod.attach_haunt(plan)
        self.assertEqual(plan["throat"]["state"], throat_mod.CHOKE)
        self.assertTrue(plan["ghost_bind"]["haunted"])
        self.assertFalse(plan["allow_bind"])


if __name__ == "__main__":
    unittest.main()
