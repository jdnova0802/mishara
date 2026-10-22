"""Settlement-window clock. Run from gate/: python3 test_clock.py"""
from __future__ import annotations

import json
import os
import sys
import unittest
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import clock  # noqa: E402


class ClockTests(unittest.TestCase):
    def test_open_past_due_is_late(self):
        minted = clock.normalize(
            {
                "started_at": "2020-01-01T00:00:00+00:00",
                "due_at": "2020-01-01T01:00:00+00:00",
                "disposition": "open",
                "documents": "must not survive",
            },
            started_at="2026-01-01T00:00:00+00:00",
            decision="HOLD",
            acted=False,
        )
        self.assertNotIn("documents", minted)
        self.assertEqual(
            clock.word(minted, now=datetime(2020, 1, 1, 2, tzinfo=timezone.utc)),
            "LATE",
        )
        self.assertIsNone(
            clock.word(minted, now=datetime(2020, 1, 1, 0, 30, tzinfo=timezone.utc))
        )

    def test_denied_names_a_reason_and_is_not_late(self):
        minted = clock.normalize(
            None,
            started_at="2020-01-01T00:00:00+00:00",
            decision="HALT",
            acted=False,
        )
        self.assertEqual(minted["disposition"], "denied")
        self.assertEqual(minted["reason_code"], "HALT")
        self.assertIsNone(
            clock.word(minted, now=datetime(2021, 1, 1, tzinfo=timezone.utc))
        )

    def test_held_is_not_late(self):
        minted = clock.normalize(
            None,
            started_at="2020-01-01T00:00:00+00:00",
            decision="GO",
            acted=True,
        )
        self.assertEqual(minted["disposition"], "held")
        self.assertNotIn("reason_code", minted)
        self.assertIsNone(
            clock.word(minted, now=datetime(2021, 1, 1, tzinfo=timezone.utc))
        )

    def test_attach_round_trip_is_signed_shape(self):
        hop = clock.attach(
            {"state": "halt", "documents": {"body": "no"}},
            started_at="2026-10-22T12:00:00+00:00",
            decision="HALT",
            acted=False,
        )
        self.assertEqual(hop["state"], "halt")
        self.assertNotIn("documents", hop["clock"])
        json.dumps(hop["clock"], sort_keys=True)


if __name__ == "__main__":
    unittest.main()
