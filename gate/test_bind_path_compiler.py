"""Tests for Bind Path Compiler — actionable procedure, not binary gate."""
from __future__ import annotations

import unittest

try:
    from gate import bind_path_compiler as bpc_mod
    from gate import throat as throat_mod
    from gate import desk_quorum_fob as quorum_mod
except ImportError:
    import bind_path_compiler as bpc_mod
    import throat as throat_mod
    import desk_quorum_fob as quorum_mod


class BindPathCompilerTests(unittest.TestCase):
    def test_ready_when_open_and_allowed(self):
        plan = {
            "allow_bind": True,
            "verify_url": "https://gate.example/verify?r=1",
            "throat": {"state": throat_mod.OPEN},
            "desk_quorum_fob": {"verdict": quorum_mod.VERDICT_NOT_REQUIRED, "may_proceed": True},
            "mass_tag": {"tag": "light"},
        }
        r = bpc_mod.compile_plan(plan=plan, public_url="https://gate.example")
        self.assertEqual(r["path_state"], bpc_mod.STATE_READY)
        self.assertTrue(r["may_proceed"])
        self.assertEqual(r["pending_step_count"], 0)

    def test_blocked_quorum_short(self):
        plan = {
            "allow_bind": True,
            "job_id": "pc:JOB1",
            "throat": {"state": throat_mod.OPEN},
            "desk_quorum_fob": {
                "verdict": quorum_mod.VERDICT_SHORT,
                "required_n": 2,
                "got_n": 1,
                "charge_required": True,
                "charge_present": False,
                "may_proceed": False,
                "detail": "Quorum short",
            },
            "mass_tag": {"tag": "sacred"},
        }
        r = bpc_mod.compile_plan(plan=plan, public_url="https://gate.example")
        self.assertEqual(r["path_state"], bpc_mod.STATE_BLOCKED)
        self.assertFalse(r["may_proceed"])
        self.assertIn("desk_quorum_short", r["blockers"])
        ops = [a["op"] for a in r["next_actions"]]
        self.assertIn("collect_quorum", ops)
        self.assertIn("issue_charge", ops)

    def test_choke_repair_packet(self):
        plan = {
            "allow_bind": False,
            "decision": "HALT",
            "acted": False,
            "reason": "timeout_is_halt_not_live",
            "throat": {
                "state": throat_mod.CHOKE,
                "reasons": ["timeout_is_halt_not_live"],
            },
        }
        r = bpc_mod.compile_plan(plan=plan, public_url="https://gate.example")
        self.assertEqual(r["path_state"], bpc_mod.STATE_CHOKE)
        self.assertIn("treat_timeout_as_live", r["repair_packet"]["do_not"])
        self.assertTrue(r["repair_packet"]["restraint_invoice_eligible"])

    def test_attach_on_plan(self):
        plan = {"throat": {"state": throat_mod.CHOKE, "reasons": ["ambiguous_without_receipt"]}}
        bpc_mod.attach(plan, public_url="https://gate.example", job_id="pc:X")
        self.assertIn("bind_path_compiler", plan)
        self.assertEqual(plan["bind_path_compiler"]["path_state"], bpc_mod.STATE_CHOKE)

    def test_manifest(self):
        m = bpc_mod.manifest("https://gate.example")
        self.assertEqual(m["spec"], bpc_mod.SPEC)
        self.assertIn("procedure_graph", m["manufactures"])


if __name__ == "__main__":
    unittest.main()
