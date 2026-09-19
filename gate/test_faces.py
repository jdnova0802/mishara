"""Chewable faces — SSOT-backed display doors on existing SKUs."""
from __future__ import annotations

import unittest

try:
    from gate import commerce as commerce_mod
    from gate import faces as faces_mod
    from gate.app import app
except ImportError:
    import commerce as commerce_mod  # type: ignore
    import faces as faces_mod  # type: ignore
    from app import app  # type: ignore


class FaceSurfaceTests(unittest.TestCase):
    def setUp(self):
        self.c = app.test_client()

    def test_faces_ssot_resolves_ladder_prices(self):
        boss = faces_mod.face_by_id("boss_receipt", public_url="https://gate.test")
        self.assertEqual(boss["price_label"], commerce_mod.price_label("bind_room"))
        self.assertEqual(boss["price_label"], "$1,750")
        renewal = faces_mod.face_by_id("renewal_packet", public_url="https://gate.test")
        self.assertEqual(renewal["price_label"], "$1,750")
        find = faces_mod.face_by_id("find_my_agents", public_url="https://gate.test")
        self.assertIn("Free", find["price_label"])
        denial = faces_mod.face_by_id("denial_receipt", mishara_url="https://mishara.test")
        self.assertEqual(denial["price_label"], "Free")
        self.assertEqual(denial["host"], "mishara")

    def test_gate_face_pages_200_and_institutional(self):
        for path in ("/faces", "/boss-receipt", "/find-my-agents", "/renewal-packet"):
            r = self.c.get(path)
            self.assertEqual(r.status_code, 200, path)
            html = r.get_data(as_text=True)
            self.assertIn("og:title", html, path)
            self.assertNotIn("DTCC", html, path)
            self.assertNotIn("SWIFT", html, path)
            self.assertNotIn("CHOKE", html, path)
            self.assertNotIn("HAUNTED", html, path)
            self.assertNotIn("Google that never", html, path)

    def test_boss_and_renewal_cite_bind_room_price(self):
        for path in ("/boss-receipt", "/renewal-packet"):
            html = self.c.get(path).get_data(as_text=True)
            self.assertIn("$1,750", html, path)
            self.assertIn("/bind-room", html, path)

    def test_faces_manifest_and_discovery(self):
        r = self.c.get("/.well-known/faces.json")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        ids = [f["id"] for f in data["faces"]]
        self.assertEqual(
            ids,
            ["boss_receipt", "find_my_agents", "renewal_packet", "denial_receipt"],
        )
        commerce = self.c.get("/.well-known/commerce.json").get_json()
        self.assertIn("faces", commerce.get("links") or {})
        sm = self.c.get("/sitemap.xml").get_data(as_text=True)
        for path in ("/faces", "/boss-receipt", "/find-my-agents", "/renewal-packet"):
            self.assertIn(path, sm)
        llms = self.c.get("/llms.txt").get_data(as_text=True)
        self.assertIn("Boss Receipt", llms)
        self.assertIn("Find My Agents", llms)
        self.assertIn("Renewal Packet", llms)
        # ladder line must come from SSOT, not a retired number
        self.assertIn(commerce_mod.price_label("bind_room"), llms)

    def test_nav_footer_link_faces(self):
        home = self.c.get("/").get_data(as_text=True)
        self.assertIn("/faces", home)
        self.assertIn("Faces", home)


if __name__ == "__main__":
    unittest.main()
