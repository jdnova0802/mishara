"""Bind-event settlement clock. Run from gate/: python3 test_clock.py"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import unittest
from datetime import datetime, timedelta, timezone

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

    def test_window_is_bind_settlement_not_issuing_sla(self):
        self.assertEqual(clock.BIND_SETTLEMENT_WINDOW_MINUTES, 60)
        self.assertEqual(clock.WINDOW_MINUTES, 60)
        minted = clock.normalize(
            None,
            started_at="2026-10-22T12:00:00+00:00",
            decision="HOLD",
            acted=False,
        )
        self.assertEqual(minted["window_minutes"], 60)
        started = datetime(2026, 10, 22, 12, tzinfo=timezone.utc)
        due = datetime.fromisoformat(minted["due_at"])
        self.assertEqual(due - started, timedelta(minutes=60))
        issuing = pathlib.Path(__file__).with_name("issuing_mouth.py").read_text(encoding="utf-8")
        self.assertNotIn("import clock", issuing)
        self.assertNotIn("from clock", issuing)
        self.assertNotIn("BIND_SETTLEMENT_WINDOW_MINUTES", issuing)

    def test_production_attach_ignores_hop_due_at(self):
        hop = clock.attach(
            {
                "clock": {
                    "started_at": "2020-01-01T00:00:00+00:00",
                    "due_at": "2020-01-01T01:00:00+00:00",
                    "disposition": "open",
                }
            },
            started_at="2026-10-22T12:00:00+00:00",
            decision="HOLD",
            acted=False,
            inject=False,
        )
        self.assertEqual(hop["clock"]["started_at"], "2026-10-22T12:00:00+00:00")
        self.assertEqual(hop["clock"]["due_at"], "2026-10-22T13:00:00+00:00")
        self.assertEqual(hop["clock"]["disposition"], "open")
        self.assertIsNone(clock.word(hop["clock"], now=datetime(2026, 10, 22, 12, 30, tzinfo=timezone.utc)))
        self.assertEqual(
            clock.word(hop["clock"], now=datetime(2026, 10, 22, 13, 1, tzinfo=timezone.utc)),
            "LATE",
        )

    def test_denied_hop_cannot_inject_open_on_production(self):
        hop = clock.attach(
            {
                "clock": {
                    "disposition": "open",
                    "due_at": "2020-01-01T01:00:00+00:00",
                }
            },
            started_at="2026-10-22T12:00:00+00:00",
            decision="HALT",
            acted=False,
            inject=False,
        )
        self.assertEqual(hop["clock"]["disposition"], "denied")
        self.assertEqual(hop["clock"]["reason_code"], "HALT")
        self.assertIsNone(clock.word(hop["clock"], now=datetime(2026, 10, 23, tzinfo=timezone.utc)))


if __name__ == "__main__":
    unittest.main()
