"""Tests for ops guards — foothill only."""
from __future__ import annotations

import os
import unittest
from datetime import datetime, timezone
from unittest import mock

try:
    from gate import ops_guards as og
except ImportError:
    import ops_guards as og


class OpsGuardsTests(unittest.TestCase):
    def test_patent_ok_far_out(self):
        r = og.patent_alarm(now=datetime(2026, 8, 26, tzinfo=timezone.utc))
        self.assertIn(r["level"], ("ok", "warn"))
        self.assertEqual(r["patent"], "64/124,027")

    def test_patent_urgent(self):
        with mock.patch.dict(os.environ, {"GATE_PATENT_DEADLINE_AT": "2026-09-01"}, clear=False):
            r = og.patent_alarm(now=datetime(2026, 8, 26, tzinfo=timezone.utc))
        self.assertEqual(r["level"], "fail")
        self.assertLessEqual(r["days_remaining"], 60)

    def test_stripe_missing_bind_room(self):
        env = {k: v for k, v in os.environ.items() if not k.startswith("STRIPE_")}
        env["STRIPE_SECRET_KEY"] = "sk_test"
        env["GATE_DEV_MODE"] = "1"
        with mock.patch.dict(os.environ, env, clear=True):
            r = og.stripe_sku_health()
        self.assertIn("bind_room", r.get("missing", []))

    def test_buyer_lint_runs(self):
        r = og.buyer_surface_lint()
        self.assertEqual(r["code"], "buyer_surface_lint")
        self.assertIn(r["level"], ("ok", "warn", "fail"))

    def test_snapshot_shape(self):
        snap = og.snapshot(include_live=False)
        self.assertEqual(snap["spec"], "gate-ops-guards-v1")
        self.assertIn("patent", snap["guards"])
        self.assertIn("stripe", snap["guards"])
        self.assertIn("gate1", snap["guards"])
        self.assertNotIn("live_smoke", snap["guards"])

    def test_live_smoke_flags_stale(self):
        bodies = {
            "https://gate.velaru.xyz/": (200, "Weld a path · $25k"),
            "https://gate.velaru.xyz/bind-room": (200, "Two artifacts. Book Bind Room."),
            "https://velaru.xyz/check": (200, "Next drill · Tue Aug 18 2026"),
        }

        def fake_fetch(url, timeout=12.0):
            return bodies[url]

        with mock.patch.object(og, "_fetch", side_effect=fake_fetch):
            r = og.live_smoke()
        self.assertEqual(r["level"], "fail")
        self.assertEqual(len(r["checks"]), 3)
        self.assertTrue(all(not c["ok"] for c in r["checks"]))


if __name__ == "__main__":
    unittest.main()
