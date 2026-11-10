"""Analyst desk UI wired to merged 132–151 APIs — no mock Palantir data."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-desk.db")
os.environ["GATE_ATLAS_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-desk-atlas.json")
os.environ["GATE_CASE_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-desk-cases.json")
os.environ["GATE_CAMPAIGN_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-desk-camp.json")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import atlas  # noqa: E402


class DeskPageTests(unittest.TestCase):
    def setUp(self):
        self.client = app_mod.app.test_client()

    def test_screens_render_real_endpoints(self):
        for path in ("/desk", "/graph", "/anomaly", "/cases", "/triage", "/atlas", "/campaigns", "/tlog", "/verify"):
            page = self.client.get(path)
            self.assertEqual(page.status_code, 200, path)
            self.assertIn(b"class=\"desk\"", page.data)
        graph = self.client.get("/graph")
        self.assertIn(b"shared_counterparty", graph.data)
        self.assertIn(b"/v1/link-graph", graph.data)
        anom = self.client.get("/anomaly")
        self.assertIn(b"min_sample", anom.data)
        self.assertIn(b"/v1/anomaly-flags", anom.data)
        cases = self.client.get("/cases")
        self.assertIn(b"/v1/cases", cases.data)
        self.assertIn(b"hypothesis", cases.data)
        triage = self.client.get("/triage")
        self.assertIn(b"/v1/triage/enrich", triage.data)
        self.assertIn(b"/v1/triage/dispose", triage.data)
        atlas_page = self.client.get("/atlas")
        self.assertIn(b"classified_by", atlas_page.data)
        self.assertIn(b"AML.T0043", atlas_page.data)
        camp = self.client.get("/campaigns")
        self.assertIn(b"/v1/campaigns/fimi", camp.data)
        self.assertIn(b"unattributed", camp.data)
        tlog = self.client.get("/tlog")
        self.assertIn(b"evidence-head.json", tlog.data)
        verify = self.client.get("/verify")
        self.assertIn(b"/v1/verify", verify.data)
        self.assertIn(b"proof.json", verify.data)

    def test_fonts_and_dot_grid(self):
        css = self.client.get("/static/desk.css")
        self.assertEqual(css.status_code, 200)
        self.assertIn(b"Space Grotesk", css.data)
        self.assertIn(b"IBM Plex Mono", css.data)
        self.assertIn(b"Inter", css.data)
        self.assertIn(b"radial-gradient", css.data)

    def test_thin_apis(self):
        roots = self.client.get("/v1/link-graph/roots")
        self.assertEqual(roots.status_code, 200)
        self.assertTrue(roots.get_json()["empty"])
        posted = self.client.post(
            "/v1/atlas-ref",
            json={
                "receipt_id": "abc",
                "atlas_technique_id": "AML.T0043",
                "classified_by": "human_analyst",
                "classification_confidence": 0.7,
            },
        )
        self.assertEqual(posted.status_code, 201)
        self.assertEqual(posted.get_json()["classified_by"], "human_analyst")
        self.assertEqual(atlas.list_refs()[-1]["atlas_technique_id"], "AML.T0043")
        inspect = self.client.get("/v1/link-graph/inspect")
        self.assertEqual(inspect.status_code, 400)


if __name__ == "__main__":
    unittest.main()
