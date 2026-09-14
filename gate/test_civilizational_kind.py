"""Civilizational kind yellow paper. Run from gate/: python3 test_civilizational_kind.py"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-kind.db")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as gate_app  # noqa: E402


class KindPaper(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            os.remove(os.environ["GATE_DB_PATH"])
        except OSError:
            pass
        gate_app.db.init_db()
        cls.client = gate_app.app.test_client()

    def test_spec_does_not_overwrite_thesis(self):
        r = self.client.get("/.well-known/civilizational-kind.json")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data["spec"], "nisaba-civilizational-kind-v1")
        self.assertFalse(data["their_production"])
        self.assertTrue(data["action_os_still_seated"])
        self.assertTrue(data["not_outbound"])
        self.assertTrue(data["skip_remaining_does_not_change_thesis"])
        self.assertTrue(data["srt_seed_does_not_change_thesis"])
        self.assertEqual(data["srt"]["shipped"], "seed")
        self.assertFalse(data["srt"]["civilization_default"])
        self.assertIn("K1", data["kinds"])
        self.assertIn("office", data["kinds"]["K2"]["name"].lower())

    def test_page_is_buried(self):
        page = self.client.get("/kind")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"noindex", page.data)
        self.assertIn(b"major technology company", page.data)
        self.assertIn(b"Action OS is still the seated thesis", page.data)
        robots = self.client.get("/robots.txt").get_data(as_text=True)
        self.assertIn("Disallow: /kind", robots)

    def test_listings_dates_kind(self):
        data = self.client.get("/.well-known/listings.json").get_json()
        self.assertIn("civilizational_kind", data)
        self.assertTrue(data["civilizational_kind"]["action_os_still_seated"])


if __name__ == "__main__":
    unittest.main()
