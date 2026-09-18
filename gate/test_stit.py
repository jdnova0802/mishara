"""Nested STIT is unsat; NON-ACT names the settler."""
from __future__ import annotations

import unittest

from gate import stit as stit_mod


class NestedStitTests(unittest.TestCase):
    def test_two_agents_cannot_nested_stit(self):
        out = stit_mod.nested_stit(
            actor="agent-1", principal="human:uw", claims_nested=True
        )
        self.assertFalse(out["delegated"])
        self.assertFalse(out["nested_possible"])
        self.assertTrue(out["misfire"])

    def test_same_agent_is_not_nested(self):
        out = stit_mod.nested_stit(
            actor="human:uw", principal="human:uw", claims_nested=True
        )
        self.assertTrue(out["nested_possible"])
        self.assertFalse(out["misfire"])

    def test_actor_only_is_not_nested(self):
        out = stit_mod.nested_stit(actor="agent-1", principal=None)
        self.assertTrue(out["nested_possible"])
        self.assertFalse(out["misfire"])


class SettlerTests(unittest.TestCase):
    def test_act_has_no_settler(self):
        self.assertIsNone(
            stit_mod.settler(
                agency="ACT",
                open_count=2,
                policy={},
                context={},
                body={},
            )
        )

    def test_named_settler_wins(self):
        out = stit_mod.settler(
            agency="NON-ACT",
            open_count=1,
            policy={"allowed_actions": ["wire.send"]},
            context={"settler_id": "charge:abc"},
            body={},
        )
        self.assertEqual(out["kind"], "named")
        self.assertEqual(out["settler_id"], "charge:abc")
        self.assertTrue(out["owned"])
        self.assertFalse(out["gap"])

    def test_allowlist_settler(self):
        out = stit_mod.settler(
            agency="NON-ACT",
            open_count=1,
            policy={"allowed_actions": ["wire.send"]},
            context={},
            body={},
        )
        self.assertEqual(out["kind"], "allowlist")
        self.assertIn("wire.send", out["settler_id"])
        self.assertFalse(out["owned"])
        self.assertTrue(out["gap"])
        self.assertEqual(out["gap_reason"], "unowned_policy")


if __name__ == "__main__":
    unittest.main()
