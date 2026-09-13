"""Hustle doors — Refusal + diligence discovery under commerce SSOT."""
from __future__ import annotations

import unittest

try:
    from gate import commerce as commerce_mod
    from gate.app import app
except ImportError:
    import commerce as commerce_mod  # type: ignore
    from app import app  # type: ignore


class HustleDoorTests(unittest.TestCase):
    def setUp(self):
        self.c = app.test_client()

    def test_ssot_prices(self):
        self.assertEqual(commerce_mod.price_label("diligence_deposit"), "$2,500")
        self.assertEqual(commerce_mod.price_label("refusal"), "$7,500")
        self.assertEqual(commerce_mod.price_cents("refusal"), 750000)
        sprints = commerce_mod.erra_sprints()["sprints"]
        self.assertGreaterEqual(len(sprints), 5)
        labels = {s["price_label"] for s in sprints}
        self.assertIn("$4,500", labels)
        self.assertIn("$9,500", labels)

    def test_refusal_is_public_and_institutional(self):
        r = self.c.get("/refusal")
        self.assertEqual(r.status_code, 200)
        html = r.get_data(as_text=True)
        self.assertIn("$7,500", html)
        self.assertNotIn("noindex", html.lower())
        self.assertNotIn("DTCC", html)
        self.assertNotIn("SWIFT", html)
        self.assertNotIn("illegitimate", html.lower())
        robots = self.c.get("/robots.txt").get_data(as_text=True)
        self.assertNotIn("Disallow: /refusal", robots)

    def test_diligence_and_hustle_board_discovery(self):
        self.assertEqual(self.c.get("/diligence").status_code, 200)
        board = self.c.get("/outbound/HUSTLE_BOARD.md")
        self.assertEqual(board.status_code, 200)
        body = board.get_data(as_text=True)
        self.assertIn("Bind Room", body)
        self.assertIn("Refusal", body)
        self.assertIn("Erra", body)
        self.assertIn("$1,750", body)
        self.assertIn("$2,500", body)
        self.assertIn("$7,500", body)
        self.assertNotIn("{bind_room}", body)
        self.assertNotIn("{refusal}", body)

        sm = self.c.get("/sitemap.xml").get_data(as_text=True)
        for path in ("/diligence", "/refusal", "/outbound/HUSTLE_BOARD.md"):
            self.assertIn(path, sm)

        llms = self.c.get("/llms.txt").get_data(as_text=True)
        self.assertIn("/refusal", llms)
        self.assertIn("/diligence", llms)
        self.assertIn("HUSTLE_BOARD.md", llms)
        self.assertIn("velaru.xyz/erra", llms)

        commerce = self.c.get("/.well-known/commerce.json").get_json()
        ids = [row["id"] for row in commerce["ladder"]]
        self.assertIn("refusal", ids)
        self.assertIn("diligence_deposit", ids)
        self.assertIn("erra_sprints", commerce)
        self.assertIn("refusal", commerce.get("links") or {})

    def test_start_lists_hustle_doors(self):
        html = self.c.get("/start").get_data(as_text=True)
        self.assertIn("/refusal", html)
        self.assertIn("/diligence", html)
        self.assertIn("HUSTLE_BOARD.md", html)
        self.assertIn("velaru.xyz/erra", html)


if __name__ == "__main__":
    unittest.main()
