"""Skip remaining protocol. Run from gate/: python3 test_skip_remaining.py"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-skip.db")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import skip_remaining as skip  # noqa: E402
import app as gate_app  # noqa: E402


class CaspPhysics(unittest.TestCase):
    def test_winner_only_is_zero(self):
        seq = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
        out = skip.casp_score(sequence=seq, placed_id="c", skip_ids=[])
        self.assertEqual(out["score"], 0.0)
        self.assertEqual(out["reason"], "winner_only")
        self.assertFalse(out["pass"])

    def test_complete_skips_pass(self):
        seq = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
        out = skip.casp_score(sequence=seq, placed_id="c", skip_ids=["a", "b"])
        self.assertEqual(out["score"], 1.0)
        self.assertTrue(out["pass"])

    def test_in_sequence_head_passes_without_skips(self):
        seq = [{"id": "a"}, {"id": "b"}]
        out = skip.casp_score(sequence=seq, placed_id="a", skip_ids=[])
        self.assertTrue(out["pass"])
        self.assertEqual(out["reason"], "in_sequence_head")


class LiveMint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            os.remove(os.environ["GATE_DB_PATH"])
        except OSError:
            pass
        gate_app.db.init_db()
        cls.client = gate_app.app.test_client()

    def test_spec_is_public(self):
        r = self.client.get("/.well-known/skip-remaining.json")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data["spec"], "gate-skip-remaining-v1")
        self.assertFalse(data["their_production"])
        self.assertIn("skip", data["types"])

    def test_organ_fixture_mints_corpses(self):
        r = self.client.post("/demo/skip/mint", json={"fixture": "organ"})
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertTrue(body["ok"])
        self.assertEqual(body["casp"]["score"], 1.0)
        self.assertEqual(len(body["skips"]), 4)
        eid = body["id"]
        v = self.client.get(f"/.well-known/skip/{eid}.json")
        self.assertEqual(v.status_code, 200)
        self.assertEqual(v.get_json()["edition_hash"], body["edition_hash"])
        page = self.client.get("/skip")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"jumped", page.data)

    def test_silent_policycenter_fails_casp(self):
        r = self.client.post("/demo/skip/mint", json={"fixture": "policycenter", "mint_skips": False})
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(body["casp"]["reason"], "winner_only")
        self.assertEqual(body["casp"]["score"], 0.0)

    def test_casp_endpoint_scores_incomplete(self):
        r = self.client.post(
            "/v1/skip/casp",
            json={
                "sequence": [{"id": "a"}, {"id": "b"}, {"id": "c"}],
                "placed_id": "c",
                "skip_ids": ["a"],
            },
        )
        self.assertEqual(r.status_code, 200)
        casp = r.get_json()["casp"]
        self.assertEqual(casp["reason"], "incomplete_skips")
        self.assertFalse(casp["pass"])
        self.assertEqual(casp["score"], 0.5)

    def test_listings_dates_skip(self):
        r = self.client.get("/.well-known/listings.json")
        data = r.get_json()
        self.assertIn("skip_remaining", data)
        self.assertIn("oos-conflicts/resolve", data["skip_remaining"]["married_write"])

    def test_silent_oos_resolve_halts(self):
        r = self.client.post("/demo/skip/dated-write", json={"fixture": "oos"})
        self.assertEqual(r.status_code, 403)
        body = r.get_json()
        self.assertTrue(body["halt"])
        self.assertFalse(body["allow"])
        self.assertEqual(body["casp"]["reason"], "winner_only")
        self.assertFalse(body["their_production"])
        self.assertIn("oos-conflicts/resolve", body["spend_write"]["path"])

    def test_oos_resolve_with_skips_allows(self):
        r = self.client.post("/demo/skip/dated-write", json={"fixture": "oos-mint"})
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertTrue(body["allow"])
        self.assertEqual(body["casp"]["score"], 1.0)
        self.assertTrue(body["verify_url"])
        eid = body["skip"]["id"]
        v = self.client.get(f"/.well-known/skip/{eid}.json")
        self.assertEqual(v.status_code, 200)
        self.assertEqual(len(v.get_json()["skips"]), 1)

    def test_preempt_silent_halts_and_mint_allows(self):
        silent = self.client.post("/demo/skip/dated-write", json={"fixture": "preempt"})
        self.assertEqual(silent.status_code, 403)
        minted = self.client.post("/demo/skip/dated-write", json={"fixture": "preempt-mint"})
        self.assertEqual(minted.status_code, 200)
        self.assertTrue(minted.get_json()["allow"])

    def test_bind_only_is_not_this_scanner(self):
        r = self.client.post("/demo/skip/dated-write", json={"fixture": "bind-only"})
        self.assertEqual(r.status_code, 403)
        self.assertEqual(r.get_json()["reason"], "skip_write_not_in_protocol")

    def test_skip_worker_is_listed(self):
        w = self.client.get("/listings/cloudflare-worker-skip.js")
        self.assertEqual(w.status_code, 200)
        self.assertIn(b"oos-conflicts/resolve", w.data)
        self.assertIn(b"/v1/skip/dated-write", w.data)
        spec = self.client.get("/.well-known/skip-remaining.json").get_json()
        self.assertIn("oos-conflicts/resolve", spec["married_write"]["path"])
        self.assertIn("cloudflare-worker-skip.js", spec["implementor"])

    def test_edition_page_and_robots(self):
        minted = self.client.post("/demo/skip/mint", json={"fixture": "organ"}).get_json()
        page = self.client.get(f"/skip/{minted['id']}")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"noindex", page.data)
        robots = self.client.get("/robots.txt").get_data(as_text=True)
        self.assertIn("Disallow: /skip", robots)


if __name__ == "__main__":
    unittest.main()
