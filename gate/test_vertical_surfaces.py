"""Items 37–49 — ticker, legit, worker, radar, shadow, research stubs, parametric."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-vertical-surfaces.db")
os.environ["GATE_TICKER_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-ticker.json")
os.environ["GATE_LEGIT_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-legit.json")
os.environ["GATE_SHADOW_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-shadow.json")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import vertical_surfaces as vs  # noqa: E402


class VerticalLogicTests(unittest.TestCase):
    def test_ticker_is_not_a_detector(self):
        vs.record_tick(kind="dating", event_id="abc12345xxxx", present=False)
        payload = vs.ticker([])
        self.assertFalse(payload["catfish_model"])
        self.assertTrue(payload["ticks"])

    def test_legit_unsigned_is_shame_not_cv(self):
        out = vs.legit_check(listing_id="sku-1", row=None)
        self.assertFalse(out["cv_model"])
        self.assertFalse(out["receipt_present"])
        board = vs.legit_board()
        self.assertTrue(any(r["listing_id"] == "sku-1" for r in board["shame"]))

    def test_worker_score_is_not_fcra(self):
        score = vs.worker_score(
            [{"fuse_id": "fuse_w", "decision": "BLOCK"}, {"fuse_id": "fuse_w", "decision": "ALLOW"}],
            "fuse_w",
        )
        self.assertFalse(score["fcra_score"])
        self.assertEqual(score["counts"]["BLOCK"], 1)

    def test_wati_uses_named_employer(self):
        board = vs.wati([{"decision": "BLOCK", "hop": {"company": "Acme Gig"}}])
        self.assertEqual(board["companies"][0]["company"], "Acme Gig")
        self.assertEqual(board["companies"][0]["block"], 1)

    def test_radar_is_not_a_scrape(self):
        radar = vs.radar([])
        self.assertFalse(radar["scraped"])

    def test_shift_needs_twenty(self):
        short = vs.shift_anomaly([8] * 10)
        self.assertEqual(short["reason"], "no_samples")
        self.assertTrue(short["never_auto_acted"])
        series = [8.0] * 19 + [80.0]
        long = vs.shift_anomaly(series)
        self.assertTrue(long["flags"])
        self.assertTrue(long["never_auto_acted"])

    def test_shadow_rejects_pii_and_reconstructs(self):
        with self.assertRaises(ValueError):
            vs.add_shadow(employer_hash="not-hex", feature="nights", outcome="BLOCK")
        h = "a" * 16
        vs.add_shadow(employer_hash=h, feature="nights", outcome="BLOCK")
        vs.add_shadow(employer_hash=h, feature="nights", outcome="ALLOW")
        out = vs.reconstruct(h)
        self.assertEqual(out["n"], 2)
        self.assertAlmostEqual(out["reconstructed"][0]["block_rate"], 0.5)

    def test_research_and_parametric_are_stubs(self):
        stub = vs.research_stub(45, "liveness")
        self.assertFalse(stub["built"])
        para = vs.parametric_stub()
        self.assertFalse(para["product"])
        self.assertFalse(para["munich_re"])
        self.assertFalse(para["endorsement"])

    def test_listing_anomaly_not_cv(self):
        out = vs.listing_price_anomaly([10] * 19 + [400])
        self.assertFalse(out["cv_model"])
        self.assertTrue(out["never_auto_acted"])
        self.assertTrue(out["flags"])


class VerticalFlaskTests(unittest.TestCase):
    def setUp(self):
        self.client = app_mod.app.test_client()

    def test_pages_200(self):
        for path in (
            "/ticker",
            "/legit",
            "/worker",
            "/wati",
            "/radar",
            "/shifts",
            "/shadow",
            "/research/liveness",
            "/research/reverse-image",
            "/research/cv-auth",
            "/listing-anomaly",
            "/parametric",
        ):
            r = self.client.get(path)
            self.assertEqual(r.status_code, 200, path)

    def test_parametric_json(self):
        r = self.client.get("/.well-known/parametric.json")
        self.assertFalse(r.get_json()["product"])

    def test_research_json(self):
        body = self.client.get("/.well-known/research.json").get_json()
        self.assertFalse(body["45"]["built"])

    def test_shadow_api(self):
        bad = self.client.post("/v1/shadow", json={"employer_hash": "x", "feature": "nights", "outcome": "BLOCK"})
        self.assertEqual(bad.status_code, 400)
        ok = self.client.post(
            "/v1/shadow",
            json={"employer_hash": "ab" * 8, "feature": "weekend", "outcome": "HOLD"},
        )
        self.assertEqual(ok.status_code, 201)


if __name__ == "__main__":
    unittest.main()
