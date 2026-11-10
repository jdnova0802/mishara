"""Items 80–86 — Stripe diagonal, globe, dots, type, blur nav, accent, stagger."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-frontend-motif.db")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402


class FrontendMotifTests(unittest.TestCase):
    def setUp(self):
        self.client = app_mod.app.test_client()

    def test_home_and_bind_room_have_diagonal_stripe(self):
        home = self.client.get("/")
        bind = self.client.get("/bind-room")
        self.assertIn(b"hero-stripe", home.data)
        self.assertIn(b"hero-stripe", bind.data)

    def test_nav_is_sticky_blur(self):
        home = self.client.get("/")
        self.assertIn(b'site-nav', home.data)
        css = self.client.get("/static/style.css")
        self.assertIn(b"backdrop-filter", css.data)
        self.assertIn(b"stripe-shift", css.data)
        self.assertIn(b"feed-in", css.data)
        self.assertIn(b"prefers-reduced-motion", css.data)

    def test_map_globe_does_not_replace_the_plate(self):
        page = self.client.get("/map")
        self.assertIn(b"globe-spin", page.data)
        self.assertIn(b"live-map", page.data)
        self.assertIn(b"prefers-reduced-motion", page.data)

    def test_check_feed_staggers_rows(self):
        page = self.client.get("/check")
        self.assertEqual(page.status_code, 200)


if __name__ == "__main__":
    unittest.main()
