"""Public /clip page — paste → ≤15s chat video, not a PAS weld."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-chat-clip.db")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as gate_app  # noqa: E402


class ChatClipPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_clip_page_serves_renderer(self):
        r = self.client.get("/clip")
        self.assertEqual(r.status_code, 200)
        body = r.get_data(as_text=True)
        self.assertIn("Render clip", body)
        self.assertIn("sha256", body)
        self.assertIn("720", body)
        self.assertIn("15000", body)
        self.assertNotIn("PolicyCenter", body)
        self.assertNotIn("Bind Room", body)

    def test_gate_json_lists_clip(self):
        r = self.client.get("/.well-known/gate.json")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.get_json()["chat_clip"].endswith("/clip"))

    def test_issuing_mouth_points_at_clip(self):
        r = self.client.get("/issuing-mouth")
        self.assertEqual(r.status_code, 200)
        self.assertIn("/clip", r.get_data(as_text=True))

    def test_csp_allows_blob_media(self):
        r = self.client.get("/clip")
        csp = r.headers.get("Content-Security-Policy") or ""
        self.assertIn("media-src 'self' blob:", csp)


if __name__ == "__main__":
    unittest.main()
