"""Item 104 — T&S vertical on 120 tiers + 122 assumptions. No CV."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-tns.db")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import tns  # noqa: E402


class TnsLogicTests(unittest.TestCase):
    def test_flat_harm_refused(self):
        out = tns.evaluate(extra={"harm_detected": True})
        self.assertFalse(out["ok"])
        self.assertEqual(out["error"], "flat_harm_refused")

    def test_classifier_cannot_auto_act(self):
        out = tns.evaluate(abuse_tier="classifier", auto_act=True)
        self.assertFalse(out["ok"])
        self.assertEqual(out["error"], "classifier_never_auto_act")

    def test_exact_match_and_provenance_stay_split(self):
        out = tns.evaluate(
            abuse_tier="exact_match",
            match_hash="deadbeef",
            auto_act=True,
            generated_tier="provenance",
        )
        self.assertTrue(out["ok"])
        self.assertTrue(out["auto_act"])
        self.assertEqual(out["abuse"]["tier"], "exact_match")
        self.assertEqual(out["generated"]["tier"], "provenance")
        self.assertEqual(out["generated"]["disposition"], "ORTHOGONAL")
        self.assertFalse(out["cv_model"])

    def test_verified_needs_assumptions(self):
        out = tns.evaluate(abuse_tier="classifier", verified=True)
        self.assertFalse(out["ok"])
        self.assertEqual(out["error"], "assumptions_required")


class TnsFlaskTests(unittest.TestCase):
    def setUp(self):
        self.client = app_mod.app.test_client()

    def test_page_and_post(self):
        page = self.client.get("/tns")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"cv_model", page.data)
        bad = self.client.post("/v1/tns", json={"harm_detected": True})
        self.assertEqual(bad.status_code, 409)
        good = self.client.post("/v1/tns", json={"abuse_tier": "classifier"})
        self.assertEqual(good.status_code, 200)
        self.assertFalse(good.get_json()["auto_act"])


if __name__ == "__main__":
    unittest.main()
