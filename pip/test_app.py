"""Standalone Pip origin — no family brands, MP4 encode, integrity copy."""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest

from app import app

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
    "gate.velaru",
)


class PipStandaloneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()

    def test_index_is_pip_not_family(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        body = r.get_data(as_text=True)
        self.assertIn("<h1>Pip</h1>", body)
        self.assertIn("export fingerprint", body)
        self.assertIn("file integrity", body)
        self.assertIn("not a live-chat proof", body)
        self.assertIn("/encode", body)
        self.assertIn("pip-clip.mp4", body)
        self.assertNotIn("PolicyCenter", body)
        for token in FORBIDDEN:
            self.assertNotIn(token, body)

    def test_health_ok(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.get_json()["ok"])

    def test_encode_rejects_empty(self):
        r = self.client.post("/encode", data=b"", content_type="video/webm")
        self.assertEqual(r.status_code, 413)

    @unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg not installed")
    def test_encode_webm_to_mp4(self):
        td = tempfile.mkdtemp(prefix="pip-ff-")
        src = os.path.join(td, "in.webm")
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-y",
                    "-f",
                    "lavfi",
                    "-i",
                    "color=c=orange:s=64x64:d=0.3",
                    "-c:v",
                    "libvpx",
                    src,
                ],
                check=True,
                timeout=20,
            )
            with open(src, "rb") as f:
                raw = f.read()
            r = self.client.post("/encode", data=raw, content_type="video/webm")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.mimetype, "video/mp4")
            body = r.get_data()
            self.assertGreater(len(body), 32)
            self.assertIn(b"ftyp", body[:32])
        finally:
            shutil.rmtree(td, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
