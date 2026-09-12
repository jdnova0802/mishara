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
        self.assertEqual(commerce_mod.fee_label("operator_hop"), "$0.10/hop")
        self.assertEqual(commerce_mod.fee("operator_carry")["bps"], 5)

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

    def test_residual_bind_room_price_not_hand_typed(self):
        """Dim 14 residual list — dollars live only in ladder.json (and tests asserting SSOT)."""
        from pathlib import Path
        import re

        root = Path(__file__).resolve().parent
        allowed = {
            root / "commerce" / "ladder.json",
            root / "test_commerce.py",
            root / "test_faces.py",
            root / "test_hustle_doors.py",
            root / "test_listings.py",
        }
        # CWV artifacts are historical measurements; not product copy.
        skip_dirs = {"__pycache__", ".git", "cwv"}
        pattern = re.compile(r"\$1,?750|175000")
        offenders = []
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in skip_dirs for part in path.parts):
                continue
            if path.suffix.lower() not in {".py", ".html", ".md", ".yml", ".yaml", ".json", ".txt", ".example"}:
                continue
            # .env.example must not carry ladder dollars either (Stripe IDs only).
            if path.name.startswith(".env") and path.suffix == ".example":
                pass  # still scanned
            elif path.name.startswith(".env"):
                continue
            if path.resolve() in {p.resolve() for p in allowed}:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if pattern.search(text):
                offenders.append(str(path.relative_to(root)))
        self.assertEqual(offenders, [], f"hand-typed Bind Room price: {offenders}")

    def test_bind_room_meta_uses_ssot_label(self):
        html = self.c.get("/bind-room").get_data(as_text=True)
        label = commerce_mod.price_label("bind_room")
        self.assertIn(f"Bind Room · {label}", html)
        self.assertIn(f"{label} officer pack", html)
        openapi = self.c.get("/openapi.full.json").get_json()
        summary = openapi["paths"]["/bind-room"]["get"]["summary"]
        self.assertIn(label, summary)


if __name__ == "__main__":
    unittest.main()
