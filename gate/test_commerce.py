"""Commerce SSOT + institutional surface checks."""
from __future__ import annotations

import unittest

try:
    from gate import commerce as commerce_mod
    from gate.app import app
except ImportError:
    import commerce as commerce_mod  # type: ignore
    from app import app  # type: ignore


class CommerceSSOTTests(unittest.TestCase):
    def setUp(self):
        self.c = app.test_client()

    def test_ladder_bind_room_matches_env_default(self):
        self.assertEqual(commerce_mod.price_label("bind_room"), "$1,750")
        self.assertEqual(commerce_mod.price_cents("bind_room"), 175000)
        self.assertEqual(commerce_mod.price_label("operator_weld"), "$25,000")
        self.assertEqual(commerce_mod.bps("operator_flow_bps"), 10)

    def test_entity_patent_and_support(self):
        self.assertEqual(commerce_mod.legal_name(), "Nisaba LLC")
        self.assertIn("64/124,027", commerce_mod.patent_display())
        self.assertEqual(commerce_mod.support_email(), "hello@velaru.xyz")
        self.assertIn("business day", commerce_mod.support_sla())

    def test_well_known_commerce_and_security(self):
        r = self.c.get("/.well-known/commerce.json")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data["legal_name"], "Nisaba LLC")
        ids = [row["id"] for row in data["ladder"]]
        self.assertIn("bind_room", ids)
        s = self.c.get("/.well-known/security.txt")
        self.assertEqual(s.status_code, 200)
        body = s.get_data(as_text=True)
        self.assertIn("Contact:", body)
        self.assertIn("hello@velaru.xyz", body)

    def test_buyer_pages_have_og_and_security_headers(self):
        for path in ("/", "/pricing", "/bind-room", "/privacy", "/terms"):
            r = self.c.get(path)
            self.assertEqual(r.status_code, 200, path)
            html = r.get_data(as_text=True)
            self.assertIn("og:title", html, path)
            self.assertIn("og:image", html, path)
            self.assertIn("64/124,027", html)
            self.assertIn("Strict-Transport-Security", r.headers)
            self.assertIn("Content-Security-Policy", r.headers)

    def test_404_is_designed(self):
        r = self.c.get("/no-such-institutional-page")
        self.assertEqual(r.status_code, 404)
        html = r.get_data(as_text=True)
        self.assertIn("Bind Room", html)
        self.assertIn("Pricing", html)

    def test_no_borrowed_clearinghouse_names_on_buyer_chrome(self):
        for path in ("/", "/pricing", "/bind-room", "/positioning"):
            html = self.c.get(path).get_data(as_text=True)
            self.assertNotIn("DTCC", html, path)
            self.assertNotIn("SWIFT", html, path)


if __name__ == "__main__":
    unittest.main()
