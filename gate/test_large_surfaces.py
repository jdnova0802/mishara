"""Items 28–36 — map, board, sports feed, exposure, packet, twin, skin, companion, dating."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-large-surfaces.db")
os.environ["GATE_TRUST_SKINS_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-trust-skins.json")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import large_surfaces as ls  # noqa: E402


class MapAndBoardTests(unittest.TestCase):
    def test_unlocated_block_is_counted_not_invented(self):
        payload = ls.restraint_map(
            [{"id": "e1", "decision": "BLOCK", "hop": {}, "created_at": "2026-11-10"}]
        )
        self.assertEqual(payload["points"], [])
        self.assertEqual(payload["unlocated"], 1)

    def test_colorado_block_pins(self):
        payload = ls.restraint_map(
            [{"id": "e2", "decision": "BLOCK", "hop": {"state": "CO"}, "created_at": "2026-11-10"}]
        )
        self.assertEqual(len(payload["points"]), 1)
        self.assertEqual(payload["points"][0]["code"], "CO")
        self.assertTrue(payload["points"][0]["located"])

    def test_leaderboard_is_counts_not_cdpi(self):
        board = ls.leaderboard(
            [
                {"fuse_id": "fuse_a", "decision": "BLOCK", "id": "1"},
                {"fuse_id": "fuse_a", "decision": "ALLOW", "id": "2"},
            ]
        )
        self.assertEqual(board["methodology"], "event_counts_not_cdpi_v1")
        self.assertEqual(board["agents"][0]["block"], 1)
        self.assertEqual(board["agents"][0]["allow"], 1)

    def test_sports_feed_empty_is_honest(self):
        feed = ls.sports_feed([{"id": "e", "decision": "BLOCK", "hop": {"line": "GL"}}])
        self.assertEqual(feed["events"], [])
        self.assertTrue(feed["empty_is_honest"])

    def test_sports_feed_hits_kalshi(self):
        feed = ls.sports_feed(
            [{"id": "e", "decision": "BLOCK", "hop": {"venue": "kalshi"}, "fuse_id": "fuse_x"}]
        )
        self.assertEqual(len(feed["events"]), 1)

    def test_exposure_is_arithmetic(self):
        out = ls.exposure(notional=50000, unauthorized_per_year=12, loss_fraction=1)
        self.assertEqual(out["dollars"], 600000)
        self.assertTrue(out["not_a_quote"])

    def test_twin_does_not_claim_recorded(self):
        out = ls.twin({"premium": 62400, "authority_limit": 50000, "hop": {"verdict": True, "state": "LIVE"}})
        self.assertTrue(out["dry_run"])
        self.assertFalse(out["recorded"])
        self.assertFalse(out["their_production"])
        self.assertEqual(out["plan"]["result"], "BLOCK")

    def test_dating_does_not_claim_a_model(self):
        miss = ls.dating_status(None)
        self.assertFalse(miss["catfish_model"])
        self.assertFalse(miss["receipt_present"])
        hit = ls.dating_status({"id": "e", "decision": "BLOCK", "receipt_hash": "aa"})
        self.assertTrue(hit["receipt_present"])
        self.assertFalse(hit["catfish_model"])

    def test_companion_is_not_emergency(self):
        miss = ls.companion_status(None)
        self.assertFalse(miss["emergency"])
        self.assertFalse(miss["ok"])


class FlaskSurfaceTests(unittest.TestCase):
    def setUp(self):
        self.client = app_mod.app.test_client()

    def test_pages_200(self):
        for path in ("/map", "/board", "/sports", "/exposure", "/sandbox", "/companion", "/dating"):
            r = self.client.get(path)
            self.assertEqual(r.status_code, 200, path)

    def test_twin_api(self):
        r = self.client.post(
            "/v1/sandbox/twin",
            json={"premium": 10, "authority_limit": 100, "hop": {"verdict": True, "state": "LIVE"}},
        )
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertTrue(body["dry_run"])
        self.assertEqual(body["plan"]["result"], "ALLOW")

    def test_skin_dev_save_and_404(self):
        missing = self.client.get("/trust/skin/nope")
        self.assertEqual(missing.status_code, 404)
        created = self.client.post(
            "/v1/trust-skins",
            json={"slug": "acme", "name": "Acme MGA", "tagline": "Path only"},
        )
        self.assertEqual(created.status_code, 201)
        page = self.client.get("/trust/skin/acme")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"No second company", page.data)
        self.assertIn(b"DNS: not_edited", page.data)

    def test_companion_and_dating_api_missing(self):
        c = self.client.get("/v1/companion?event_id=nope")
        self.assertFalse(c.get_json()["ok"])
        d = self.client.get("/v1/dating?event_id=nope")
        self.assertFalse(d.get_json()["catfish_model"])


if __name__ == "__main__":
    unittest.main()
