"""Items 118 and 120 — empty Erra curve; Thorn harm tiers. No 121/122."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-grounded.db")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import erra_curve  # noqa: E402
import harm_tiers  # noqa: E402


class CurveTests(unittest.TestCase):
    def test_empty_curve_null_operating_point(self):
        c = erra_curve.curve("insurance")
        self.assertEqual(c["points"], [])
        self.assertIsNone(c["operating_point"])
        self.assertFalse(c["live_labels"])
        self.assertEqual(c["disclosure"], "banded")
        self.assertTrue(all(b["precision_band"] is None and b["recall_band"] is None for b in c["bands"]))
        blob = str(c).lower()
        self.assertNotIn("0.868", blob)
        self.assertNotIn("0.905", blob)

    def test_refuses_numeric_cutoff(self):
        refused = erra_curve.reject_numeric_cutoff({"precision": 0.868, "threshold": 0.9})
        self.assertIsNotNone(refused)
        self.assertEqual(refused["error"], "live_labels_required")
        self.assertIn("precision", refused["refused"])


class HarmTierTests(unittest.TestCase):
    def test_classifier_never_auto_acts(self):
        bad = harm_tiers.classify(tier="classifier", auto_act=True)
        self.assertFalse(bad["ok"])
        self.assertEqual(bad["error"], "classifier_never_auto_act")
        self.assertEqual(bad["disposition"], harm_tiers.HUMAN)
        self.assertFalse(bad["auto_act"])

    def test_exact_match_needs_hash_for_auto(self):
        missing = harm_tiers.classify(tier="exact_match", auto_act=True)
        self.assertFalse(missing["ok"])
        hashed = harm_tiers.classify(tier="hash", auto_act=True, match_hash="abc")
        self.assertTrue(hashed["ok"])
        self.assertEqual(hashed["disposition"], harm_tiers.AUTO)

    def test_provenance_is_orthogonal(self):
        out = harm_tiers.classify(tier="watermark", auto_act=True)
        self.assertTrue(out["ok"])
        self.assertEqual(out["disposition"], harm_tiers.ORTHOGONAL)
        self.assertFalse(out["auto_act"])


class GroundedFlaskTests(unittest.TestCase):
    def setUp(self):
        self.client = app_mod.app.test_client()

    def test_curve_page_and_refuse_post(self):
        page = self.client.get("/erra-curve")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"live_labels", page.data)
        self.assertNotIn(b"0.868", page.data)
        js = self.client.get("/v1/erra-curve?vertical=insurance")
        self.assertIsNone(js.get_json()["operating_point"])
        posted = self.client.post("/v1/erra-curve", json={"precision": 0.868, "vertical": "insurance"})
        self.assertEqual(posted.status_code, 409)
        self.assertEqual(posted.get_json()["error"], "live_labels_required")

    def test_harm_tiers_page_and_classifier_post(self):
        page = self.client.get("/harm-tiers")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"never_auto_act_on_classifier_only", page.data)
        posted = self.client.post("/v1/harm-tiers", json={"tier": "classifier", "auto_act": True})
        self.assertEqual(posted.status_code, 409)
        self.assertEqual(posted.get_json()["error"], "classifier_never_auto_act")


if __name__ == "__main__":
    unittest.main()
