"""Pip is not served from Gate. Own origin only."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-pip-gone.db")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as gate_app  # noqa: E402


class PipDetachedFromGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_gate_does_not_serve_pip(self):
        r = self.client.get("/pip")
        self.assertEqual(r.status_code, 404)

    def test_gate_json_does_not_list_pip(self):
        r = self.client.get("/.well-known/gate.json")
        self.assertEqual(r.status_code, 200)
        payload = r.get_json()
        self.assertNotIn("pip", payload)
        blob = str(payload)
        self.assertNotIn("/pip", blob)
        self.assertNotIn("Pip", blob)
