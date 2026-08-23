"""Tests for applicable-now Bind Room inventions (batch 2)."""
from __future__ import annotations

import unittest

try:
    from gate import hop_tattoo as tattoo_mod
    from gate import soft_yes_snare as snare_mod
    from gate import mass_tag as tag_mod
    from gate import issue_bind_splitter as splitter_mod
    from gate import ticket_fuse_pack as fuse_pack_mod
    from gate import throat as throat_mod
except ImportError:
    import hop_tattoo as tattoo_mod
    import soft_yes_snare as snare_mod
    import mass_tag as tag_mod
    import issue_bind_splitter as splitter_mod
    import ticket_fuse_pack as fuse_pack_mod
    import throat as throat_mod


class HopTattooTests(unittest.TestCase):
    def test_burn_hash(self):
        r = tattoo_mod.burn(
            job_id="pc:DEMO",
            verify_url="https://velaru.xyz/verify?r=1",
            event_id="evt_1",
            fuse_id="fuse_velaru_drill",
        )
        self.assertTrue(r["burned"])
        self.assertEqual(len(r["tattoo_hash"]), 64)

    def test_attach_ensures_verify_url(self):
        plan = {"decision": "HALT", "halt": True}
        tattoo_mod.attach(plan, job_id="pc:X", verify_url="https://v/1", event_id="e1", fuse_id="f1")
        self.assertEqual(plan["verify_url"], "https://v/1")
        self.assertIn("hop_tattoo", plan)

    def test_manifest(self):
        m = tattoo_mod.manifest("https://gate.example")
        self.assertEqual(m["spec"], tattoo_mod.SPEC)


class SoftYesSnareTests(unittest.TestCase):
    def test_timeout_snared(self):
        r = snare_mod.evaluate_scenario({"timeout": True, "decision": "ALLOW", "allow_bind": True})
        self.assertTrue(r["snared"])
        self.assertEqual(r["throat_state"], throat_mod.CHOKE)

    def test_boss_snared(self):
        r = snare_mod.evaluate_scenario({"boss_said_yes": True, "decision": "ALLOW", "allow_bind": True})
        self.assertTrue(r["snared"])

    def test_clean_halt_not_snared(self):
        r = snare_mod.evaluate_scenario(
            {"decision": "HALT", "halt": True, "would_bind": False, "verify_url": "https://x/v"}
        )
        self.assertFalse(r["snared"])

    def test_drills_all_ok(self):
        report = snare_mod.run_drills()
        self.assertTrue(report["all_ok"], report["drills"])


class MassTagTests(unittest.TestCase):
    def test_tag_from_stick_meter(self):
        plan = {"stick_meter": {"mass_class": "heavy", "score": 55, "write_kind": "bind"}}
        tag_mod.attach(plan)
        self.assertEqual(plan["mass_tag"]["tag"], "heavy")
        self.assertTrue(plan["mass_tag"]["actionable"])


class IssueBindSplitterTests(unittest.TestCase):
    def test_quote_release_leak(self):
        r = splitter_mod.evaluate(issue_type="UWManagerReviewBlocksQuoteRelease")
        self.assertEqual(r["verdict"], "LEAK")
        self.assertTrue(r["leak"])

    def test_blocks_bind_ok(self):
        r = splitter_mod.evaluate(blocking_point="Binding")
        self.assertEqual(r["verdict"], "SPLIT_OK")


class TicketFusePackTests(unittest.TestCase):
    def test_pack_manifest(self):
        m = fuse_pack_mod.manifest("https://gate.example")
        self.assertEqual(m["spec"], fuse_pack_mod.SPEC)

    def test_pack_story(self):
        p = fuse_pack_mod.pack(public_url="https://gate.example")
        self.assertIn("children", p["story"])


if __name__ == "__main__":
    unittest.main()
