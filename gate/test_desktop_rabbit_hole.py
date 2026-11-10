"""Deepest desktop rabbit-hole lineup — structure + SSOT lock."""
from __future__ import annotations

import json
import os
import re
import unittest
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(HERE, "desktop_rabbit_hole.json")
HTML_PATH = os.path.join(HERE, "desktop_rabbit_hole.html")
MD_PATH = os.path.join(HERE, "DESKTOP_RABBIT_HOLE_DEEPEST.md")
ORDERS_PATH = os.path.join(HERE, "DESKTOP_ORDERS_RABBIT_HOLE_DEEPEST_2026-09-18.md")


class DesktopRabbitHoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(JSON_PATH, encoding="utf-8") as f:
            cls.data = json.load(f)
        with open(HTML_PATH, encoding="utf-8") as f:
            cls.html = f.read()
        with open(MD_PATH, encoding="utf-8") as f:
            cls.md = f.read()
        with open(ORDERS_PATH, encoding="utf-8") as f:
            cls.orders = f.read()

    def test_four_windows_eight_tabs(self):
        windows = self.data["windows"]
        self.assertEqual([w["id"] for w in windows], ["K", "P", "M", "A"])
        for w in windows:
            self.assertEqual(len(w["tabs"]), 8, w["id"])
            self.assertTrue(w["name"] and w["job"])

    def test_core_ids_and_https(self):
        ids = []
        urls = []
        for w in self.data["windows"]:
            for t in w["tabs"]:
                ids.append(t["id"])
                urls.append(t["url"])
                self.assertTrue(t["id"].startswith(w["id"]))
                self.assertGreater(len(t["first_move"]), 20, t["id"])
                self.assertGreater(len(t["useful"]), 20, t["id"])
                parsed = urlparse(t["url"])
                self.assertEqual(parsed.scheme, "https", t["url"])
                self.assertTrue(parsed.netloc)
        self.assertEqual(len(ids), 32)
        self.assertEqual(len(set(ids)), 32)
        self.assertEqual(len(set(urls)), 32)

    def test_html_embeds_matching_json(self):
        m = re.search(
            r'<script id="lineup" type="application/json">\s*(.+?)\s*</script>',
            self.html,
            re.S,
        )
        self.assertIsNotNone(m)
        embedded = json.loads(m.group(1))
        self.assertEqual(embedded, self.data)
        self.assertIn("noindex", self.html)
        self.assertNotIn("PLACEHOLDER", self.html)

    def test_html_and_orders_list_every_core_url(self):
        for w in self.data["windows"]:
            for t in w["tabs"]:
                self.assertIn(t["url"], self.html, t["id"])
                self.assertIn(t["url"], self.orders, t["id"])
                self.assertIn(t["url"], self.md, t["id"])

    def test_choreography_and_crosswalks(self):
        self.assertGreaterEqual(len(self.data["choreography"]), 5)
        self.assertGreaterEqual(len(self.data["crosswalks"]), 3)
        self.assertIn("Aggregators", self.data["law"])
        self.assertIn("eCFR", self.md)
        self.assertIn("nLab", self.md)
        self.assertIn("Bitsavers", self.md)

    def test_not_a_public_gate_plate(self):
        self.assertNotIn("url_for(", self.html)
        self.assertIn("not wired to `/`", self.md)


if __name__ == "__main__":
    unittest.main()
