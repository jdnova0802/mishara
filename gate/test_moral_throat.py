"""Tests for Moral Throat foothills: Pardon Sunset, Watchman Fuse, Indulgence Trap."""
from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

try:
    from gate import pardon_sunset as pardon_mod
    from gate import watchman_fuse as watch_mod
    from gate import indulgence_trap as trap_mod
except ImportError:
    import pardon_sunset as pardon_mod
    import watchman_fuse as watch_mod
    import indulgence_trap as trap_mod


class PardonSunsetTests(unittest.TestCase):
    def test_forged_self_mercy(self):
        r = pardon_mod.evaluate(
            against_score=True,
            grantor_id="u1",
            subject_id="u1",
            cosigner_id="u2",
            ttl_seconds=3600,
            scar=True,
        )
        self.assertEqual(r["verdict"], pardon_mod.VERDICT_FORGED)
        self.assertIn(pardon_mod.REASON_SELF_MERCY, r["reasons"])

    def test_forged_no_cosign(self):
        r = pardon_mod.evaluate(against_score=True, grantor_id="a", subject_id="b", ttl_seconds=60, scar=True)
        self.assertEqual(r["verdict"], pardon_mod.VERDICT_FORGED)

    def test_mercy_ok(self):
        r = pardon_mod.evaluate(
            against_score=True,
            grantor_id="uw1",
            subject_id="job1",
            cosigner_id="uw2",
            ttl_seconds=600,
            scar=True,
        )
        self.assertEqual(r["verdict"], pardon_mod.VERDICT_MERCY)
        self.assertTrue(r["may_proceed"])

    def test_expired(self):
        now = datetime.now(timezone.utc)
        r = pardon_mod.evaluate(
            against_score=True,
            grantor_id="uw1",
            subject_id="job1",
            cosigner_id="uw2",
            sunset_at=(now - timedelta(seconds=5)).isoformat(),
            now=now.isoformat(),
            scar=True,
        )
        self.assertEqual(r["verdict"], pardon_mod.VERDICT_EXPIRED)

    def test_paid_forged(self):
        r = pardon_mod.evaluate(
            against_score=True,
            grantor_id="a",
            subject_id="b",
            cosigner_id="c",
            ttl_seconds=60,
            scar=True,
            paid=True,
        )
        self.assertEqual(r["verdict"], pardon_mod.VERDICT_FORGED)


class WatchmanFuseTests(unittest.TestCase):
    def test_not_duty(self):
        r = watch_mod.evaluate(duty_class=False)
        self.assertEqual(r["verdict"], watch_mod.VERDICT_NOT_DUTY)

    def test_derelict(self):
        now = datetime.now(timezone.utc)
        r = watch_mod.evaluate(
            duty_class=True,
            duty_sla_seconds=60,
            armed_at=(now - timedelta(seconds=120)).isoformat(),
            now=now.isoformat(),
        )
        self.assertEqual(r["verdict"], watch_mod.VERDICT_DERELICT)

    def test_pulse_ok(self):
        now = datetime.now(timezone.utc)
        r = watch_mod.evaluate(
            duty_class=True,
            duty_sla_seconds=300,
            last_pulse_at=(now - timedelta(seconds=10)).isoformat(),
            now=now.isoformat(),
        )
        self.assertEqual(r["verdict"], watch_mod.VERDICT_PULSE_OK)

    def test_coward_choke(self):
        r = watch_mod.evaluate(duty_class=True, clear_required=True, choked=True, acted=False)
        self.assertEqual(r["verdict"], watch_mod.VERDICT_COWARD_CHOKE)


class IndulgenceTrapTests(unittest.TestCase):
    def test_paid_trips(self):
        r = trap_mod.evaluate(mercy_attempt=True, paid=True)
        self.assertTrue(r["tripped"])
        self.assertEqual(r["verdict"], trap_mod.VERDICT_TRIPPED)

    def test_clean(self):
        r = trap_mod.evaluate(mercy_attempt=True, scar=True, has_sunset=True)
        self.assertFalse(r["tripped"])

    def test_drills(self):
        report = trap_mod.drills()
        self.assertTrue(report["all_ok"], report["drills"])

    def test_attach_halts(self):
        plan = {"mercy": True, "paid_mercy": True, "allow_bind": True}
        trap_mod.attach(plan)
        self.assertFalse(plan["allow_bind"])
        self.assertTrue(plan["indulgence_trap"]["tripped"])


if __name__ == "__main__":
    unittest.main()
