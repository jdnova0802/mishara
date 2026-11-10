"""Items 95–99 — incident receipts, ATC hearback, feed liveness, corrections, XSS."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-dogfood-xss.db")
os.environ["GATE_CORRECTIONS_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-corrections.json")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import dfir  # noqa: E402
import dogfood  # noqa: E402
import readback  # noqa: E402
import sanitize  # noqa: E402
import trust_corrections  # noqa: E402


class SanitizeTests(unittest.TestCase):
    def test_script_tags_are_stripped(self):
        raw = '<script>alert(1)</script>premium_exceeds_authority'
        out = sanitize.strip_agent(raw)
        self.assertNotIn("<script>", out)
        self.assertIn("premium_exceeds_authority", out)

    def test_dfir_does_not_keep_markup(self):
        out = dfir.classify_reason('<img src=x onerror=alert(1)>fuse_dead_or_halt')
        self.assertEqual(out["reason_code"], "FUSE")
        self.assertNotIn("<img", out["reason_text"])


class IncidentTests(unittest.TestCase):
    def test_incidents_are_chained_receipts(self):
        payload = dogfood.incident_receipts(verify_url="https://gate.example/check")
        self.assertTrue(payload["rows"])
        self.assertTrue(all(r.get("receipt_hash") for r in payload["rows"]))
        self.assertEqual(payload["rows"][1]["prev_receipt_hash"], payload["rows"][0]["receipt_hash"])


class LivenessTests(unittest.TestCase):
    def test_signed_feed_is_not_stale_and_names_ots_calendars(self):
        live = dogfood.feed_liveness(
            [{"event_id": "e1"}],
            generated_at="2026-11-10T16:00:00+00:00",
        )
        self.assertFalse(live["stale"])
        self.assertTrue(live["digest"])
        self.assertTrue(live["ots"]["rfc3161"])
        self.assertFalse(live["ots"]["submitted"])
        self.assertTrue(any("opentimestamps.org" in c for c in live["ots"]["calendars"]))


class HearbackTests(unittest.TestCase):
    def test_run_does_not_gate_until_confirm(self):
        client = app_mod.app.test_client()
        run = client.post("/demo/bind-room/run", json={"domain": "insurance", "company": "Acme"}).get_json()
        self.assertFalse(run["gated"])
        self.assertFalse(run["hearback_confirmed"])
        self.assertIn("I heard", run["hearback"]["paraphrase"])
        bad = client.post(
            "/demo/bind-room/confirm",
            json={"domain": "insurance", "company": "Acme", "confirm_token": "nope"},
        )
        self.assertEqual(bad.status_code, 409)
        good = client.post(
            "/demo/bind-room/confirm",
            json={
                "domain": "insurance",
                "company": "Acme",
                "confirm_token": run["hearback"]["confirm_token"],
            },
        )
        self.assertEqual(good.status_code, 200)
        body = good.get_json()
        self.assertTrue(body["gated"])
        self.assertTrue(body["hearback_confirmed"])


class CorrectionsTests(unittest.TestCase):
    def test_verra_retired_keeps_history(self):
        ledger = trust_corrections.ledger()
        verra = ledger["verra_retired"]
        self.assertIsNotNone(verra)
        self.assertFalse(verra["history_erased"])
        rec = trust_corrections.append_version(
            "verra-name-retired",
            status="open_until_demo_copy_clears",
            note="still live on velaru.xyz",
        )
        self.assertGreaterEqual(len(rec["versions"]), 2)
        self.assertFalse(rec["history_erased"])


class FlaskSurfaceTests(unittest.TestCase):
    def setUp(self):
        self.client = app_mod.app.test_client()

    def test_check_shows_liveness_and_incident_hash(self):
        page = self.client.get("/check")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"gate-feed-liveness-v1", page.data)
        self.assertIn(b"opentimestamps", page.data)
        api = self.client.get("/v1/incident-receipts").get_json()
        self.assertTrue(api["rows"][0]["receipt_hash"])

    def test_corrections_page_versions(self):
        page = self.client.get("/trust/corrections")
        self.assertIn(b"verra-name-retired", page.data)
        self.assertIn(b"history is never erased", page.data)

    def test_xss_does_not_land_in_html(self):
        page = self.client.get("/check")
        self.assertNotIn(b"<script>alert", page.data)


if __name__ == "__main__":
    unittest.main()
