"""Tests for Promo Clock — stale marketing dates fail closed."""
from __future__ import annotations

import unittest

try:
    from gate import promo_clock as pc
except ImportError:
    import promo_clock as pc


class PromoClockTests(unittest.TestCase):
    def test_upcoming(self):
        r = pc.evaluate(
            next_at="2026-09-01T17:00:00-07:00",
            last_proved_at="2026-08-24T06:31:00Z",
            now="2026-08-26T12:00:00Z",
            label="AWS Loft SF",
        )
        self.assertEqual(r["mode"], "upcoming")
        self.assertTrue(r["render"])
        self.assertEqual(r["headline"], "Next drill")
        self.assertFalse(r["stale"])

    def test_stale_next_flips_to_last_proved(self):
        r = pc.evaluate(
            next_at="2026-08-18T17:00:00-07:00",
            last_proved_at="2026-08-24T06:31:00Z",
            now="2026-08-26T12:00:00Z",
            label="AWS Loft SF",
        )
        self.assertEqual(r["mode"], "proved")
        self.assertTrue(r["render"])
        self.assertEqual(r["headline"], "Last proved")
        self.assertTrue(r["stale"])

    def test_stale_without_proved_hides(self):
        r = pc.evaluate(
            next_at="2026-08-18T17:00:00-07:00",
            now="2026-08-26T12:00:00Z",
        )
        self.assertEqual(r["mode"], "hidden")
        self.assertFalse(r["render"])
        self.assertTrue(r["stale"])

    def test_invalid_next_hides(self):
        r = pc.evaluate(next_at="not-a-date", now="2026-08-26T12:00:00Z")
        self.assertEqual(r["mode"], "invalid")
        self.assertFalse(r["render"])

    def test_manifest(self):
        m = pc.manifest("https://gate.example", next_at="2026-08-18T17:00:00Z", now="2026-08-26T12:00:00Z")
        self.assertEqual(m["spec"], "gate-promo-clock-v1")
        self.assertIn("promo-clock.js", m["script"])
        self.assertEqual(m["state"]["mode"], "hidden")


if __name__ == "__main__":
    unittest.main()
