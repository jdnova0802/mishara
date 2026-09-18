"""Signed-line witness — written vs signed; in-authority at the second."""
from __future__ import annotations

import unittest

from gate import signed_line as sl


class SignedLineWitnessTests(unittest.TestCase):
    def test_absent_is_gap_not_halt(self):
        out = sl.witness()
        self.assertEqual(out["mutation"], "ABSENT")
        self.assertEqual(out["in_authority"], "UNKNOWN")
        self.assertTrue(out["gap"])
        self.assertFalse(out["halt"])
        self.assertEqual(out["gap_reason"], "missing_authority")

    def test_same_line_hashes_match(self):
        line = {"share": 25, "class": "cargo"}
        out = sl.witness(written=line, signed=line, authority={"inside": True})
        self.assertEqual(out["mutation"], "SAME")
        self.assertEqual(out["written_hash"], out["signed_hash"])
        self.assertEqual(out["in_authority"], "IN")
        self.assertFalse(out["halt"])
        self.assertFalse(out["gap"])

    def test_signing_down_is_down_not_halt(self):
        out = sl.witness(
            written={"share": 40, "slip": "A"},
            signed={"share": 10, "slip": "A"},
            authority={"inside": True, "at": "2026-09-18T12:00:00Z"},
        )
        self.assertEqual(out["mutation"], "DOWN")
        self.assertNotEqual(out["written_hash"], out["signed_hash"])
        self.assertFalse(out["halt"])
        self.assertEqual(out["in_authority"], "IN")

    def test_signed_grew_is_up(self):
        out = sl.witness(
            written={"share": 10},
            signed={"share": 40},
            authority={"inside": True},
        )
        self.assertEqual(out["mutation"], "UP")

    def test_unwritten_pen_is_gap(self):
        out = sl.witness(signed={"share": 10}, authority={"inside": True})
        self.assertEqual(out["mutation"], "UNWRITTEN")
        self.assertTrue(out["gap"])
        self.assertEqual(out["gap_reason"], "unwritten")
        self.assertFalse(out["halt"])

    def test_unsigned_written_only(self):
        out = sl.witness(written={"share": 10}, authority={"inside": True})
        self.assertEqual(out["mutation"], "UNSIGNED")
        self.assertFalse(out["halt"])

    def test_out_of_authority_halts(self):
        out = sl.witness(
            written={"share": 25},
            signed={"share": 25},
            authority={"inside": False, "at": "2026-09-18T12:00:00Z"},
        )
        self.assertEqual(out["in_authority"], "OUT")
        self.assertTrue(out["halt"])

    def test_window_miss_is_out(self):
        out = sl.witness(
            written="cargo 25",
            signed="cargo 25",
            authority={
                "window_start": "2026-01-01T00:00:00Z",
                "window_end": "2026-06-01T00:00:00Z",
                "at": "2026-09-18T12:00:00Z",
            },
        )
        self.assertEqual(out["in_authority"], "OUT")
        self.assertTrue(out["halt"])

    def test_ultra_vires_flag(self):
        out = sl.witness(
            written={"share": 5},
            signed={"share": 5},
            authority={"ultra_vires": True},
        )
        self.assertEqual(out["in_authority"], "OUT")
        self.assertTrue(out["halt"])

    def test_from_body_reads_flat_fields(self):
        out = sl.from_body(
            {
                "written_line": {"share": 30},
                "signed_line": {"share": 12},
                "authority": {"inside": True},
            }
        )
        self.assertEqual(out["mutation"], "DOWN")
        self.assertEqual(out["in_authority"], "IN")


if __name__ == "__main__":
    unittest.main()
