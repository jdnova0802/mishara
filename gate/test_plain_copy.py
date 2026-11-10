"""Copy/jargon pass — items 12–17."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-plain-copy.db")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402


class PlainCopyTests(unittest.TestCase):
    def setUp(self):
        self.client = app_mod.app.test_client()

    def test_doors_is_plain(self):
        res = self.client.get("/doors")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"How you call the stop", res.data)
        self.assertIn(b"There is no chatbot", res.data)

    def test_claims_two_person_and_not_black_box(self):
        res = self.client.get("/trust/claims")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Two-person rule", res.data)
        self.assertIn(b"Not a black box", res.data)

    def test_bind_room_two_person(self):
        res = self.client.get("/bind-room")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Two-person rule", res.data)

    def test_carrier_demo_is_not_zero_percent_compliant(self):
        res = self.client.get("/for/carriers")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"not a score that the carrier is 0% compliant", res.data)

    def test_ticker_says_signed_checks(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"signed checks", res.data)
        self.assertIn(b"not a stock ticker", res.data)


if __name__ == "__main__":
    unittest.main()
