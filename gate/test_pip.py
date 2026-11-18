"""Pip — unbranded chat clip. No Gate identity. No messenger clone. No Verify."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-pip.db")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as gate_app  # noqa: E402


FORBIDDEN = (
    "iMessage",
    "WhatsApp",
    "iOS",
    "#007AFF",
    "#34C759",
    "#25D366",
    "Nisaba",
    "Velaru",
    "Mishara",
    "Gate",
    "Verify",
    "receipt",
)


class PipPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_pip_page_serves_renderer(self):
        r = self.client.get("/pip")
        self.assertEqual(r.status_code, 200)
        body = r.get_data(as_text=True)
        self.assertIn("<h1>Pip</h1>", body)
        self.assertIn("sha256", body)
        self.assertIn("720", body)
        self.assertIn("15000", body)
        self.assertIn("drawTyping", body)
        self.assertIn("AudioContext", body)
        self.assertIn("captureStream", body)
        self.assertIn("MediaRecorder", body)
        self.assertNotIn("PolicyCenter", body)
        self.assertNotIn("Bind Room", body)
        for token in FORBIDDEN:
            self.assertNotIn(token, body)

    def test_gate_json_does_not_list_pip(self):
        r = self.client.get("/.well-known/gate.json")
        self.assertEqual(r.status_code, 200)
        payload = r.get_json()
        self.assertNotIn("pip", payload)
        self.assertNotIn("/pip", str(payload))

    def test_csp_allows_blob_media(self):
        r = self.client.get("/pip")
        csp = r.headers.get("Content-Security-Policy") or ""
        self.assertIn("media-src 'self' blob:", csp)


if __name__ == "__main__":
    unittest.main()
