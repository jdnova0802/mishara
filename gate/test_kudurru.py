"""Items 129 / 129b / 131 — Kudurru card hash, unset streak policy, spoiler-safe glyph."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-kudurru.db")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import kudurru  # noqa: E402


IDS = ["rec_a", "rec_b", "rec_c"]


class KudurruLogicTests(unittest.TestCase):
    def test_hash_is_order_sensitive(self):
        a = kudurru.root_hash(IDS)
        b = kudurru.root_hash(list(reversed(IDS)))
        self.assertNotEqual(a, b)
        card = kudurru.card(
            operator_id="op1",
            org_id="org1",
            cohort_vertical="insurance",
            period_start="2026-01-01",
            period_end="2026-01-10",
            underlying_receipt_ids=IDS,
        )
        self.assertTrue(card["ok"])
        self.assertEqual(card["receipt_root_hash"], a)
        self.assertEqual(card["cohort_vertical"], "Insurance")
        self.assertIsNone(card["streak_policy"])

    def test_calendar_gap_does_not_pick_a_skip_policy(self):
        days = [
            {"date": "2026-01-01", "mark": "CLEAN"},
            {"date": "2026-01-04", "mark": "CLEAN"},
        ]
        card = kudurru.card(
            operator_id="op1",
            org_id="org1",
            cohort_vertical="Fleet",
            period_start="2026-01-01",
            period_end="2026-01-04",
            underlying_receipt_ids=IDS,
            days=days,
        )
        self.assertEqual(card["streak_days"], 2)
        self.assertIsNone(card["streak_broken_at"])
        self.assertIsNone(card["streak_policy"])
        self.assertTrue(card["gap_unscored"])
        refused = kudurru.card(
            operator_id="op1",
            org_id="org1",
            cohort_vertical="Fleet",
            period_start="2026-01-01",
            period_end="2026-01-04",
            underlying_receipt_ids=IDS,
            extra={"streak_policy": "chess_2day_grace"},
        )
        self.assertEqual(refused["error"], "streak_policy_open")

    def test_glyph_omits_operator_and_cause(self):
        g = kudurru.glyph(
            card_id="kud_x",
            days=[
                {"mark": "CLEAN", "cause_receipt_id": "secret"},
                {"mark": "WATCH"},
                {"mark": "BREAK", "cause_receipt_id": "secret2"},
            ],
        )
        self.assertEqual(g["glyph_string"], "🟩🟨🟥")
        blob = str(g)
        self.assertNotIn("secret", blob)
        self.assertNotIn("operator_id", blob)

    def test_watch_refuses_stakes(self):
        bad = kudurru.watch(card_id="kud_x", extra={"stake": 5})
        self.assertEqual(bad["error"], "stakes_refused")
        good = kudurru.watch(card_id="kud_x", status="NEGATIVE_WATCH", follower_count=3)
        self.assertTrue(good["ok"])
        self.assertFalse(good["stakes"])
        self.assertEqual(good["follower_count"], 3)


class KudurruFlaskTests(unittest.TestCase):
    def setUp(self):
        self.client = app_mod.app.test_client()

    def test_page_and_apis(self):
        self.assertEqual(self.client.get("/kudurru").status_code, 200)
        posted = self.client.post(
            "/v1/kudurru",
            json={
                "operator_id": "op",
                "org_id": "org",
                "cohort_vertical": "Grid",
                "period_start": "2026-01-01",
                "period_end": "2026-01-02",
                "underlying_receipt_ids": ["a", "b"],
            },
        )
        self.assertEqual(posted.status_code, 201)
        body = posted.get_json()
        self.assertTrue(body["receipt_root_hash"])
        self.assertIsNone(body["streak_policy"])
        glyph = self.client.post(
            "/v1/kudurru/glyph",
            json={"card_id": body["card_id"], "days": [{"mark": "CLEAN"}, {"mark": "CLEAN"}]},
        )
        self.assertEqual(glyph.get_json()["glyph_string"], "🟩🟩")
        watch = self.client.post("/v1/kudurru/watch", json={"card_id": body["card_id"], "wager": 1})
        self.assertEqual(watch.status_code, 409)


if __name__ == "__main__":
    unittest.main()
