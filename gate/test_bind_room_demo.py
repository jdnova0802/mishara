"""Bugs 3–11: vertical demo, domain validation, corrections, registry, SKU names."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-bind-room-demo.db")
os.environ.pop("RENDER_EXTERNAL_URL", None)
os.environ.pop("RENDER_EXTERNAL_HOSTNAME", None)

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import bind_room_demo  # noqa: E402


class BindRoomDemoTests(unittest.TestCase):
    def setUp(self):
        self.client = app_mod.app.test_client()

    def test_unknown_domain_is_400_not_insurance(self):
        res = self.client.post(
            "/demo/bind-room/run",
            json={"domain": "zzzznotreal", "company": "Acme"},
        )
        self.assertEqual(res.status_code, 400)
        body = res.get_json()
        self.assertEqual(body["error"], "unknown_domain")
        self.assertNotEqual(body.get("domain"), "insurance")

    def test_query_param_garbage_is_400(self):
        res = self.client.get("/demo/bind-room?domain=not-a-vertical")
        self.assertEqual(res.status_code, 400)
        self.assertIn(b"Unknown domain", res.data)
        self.assertNotIn('class="domain-btn active" data-domain="insurance"', res.data.decode())

    def test_fleet_alias_is_network_not_insurance(self):
        res = self.client.post("/demo/bind-room/run", json={"domain": "fleet"})
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertEqual(body["domain"], "network")
        self.assertIn("Fleet", body["domain_label"])
        self.assertNotIn("DEMO-PAS-2026-001", json.dumps(body["step3_json"]))
        self.assertNotIn("actuarial ACT threshold", body["signal"]["reason"])

    def test_six_verticals_have_real_check_copy(self):
        keys = {
            "actuarial": "Reinsurance",
            "biology": "Clinical",
            "institutional": "Board",
            "network": "Fleet",
            "climate": "Grid",
            "epistemics": "Counsel",
        }
        for domain, needle in keys.items():
            with self.subTest(domain=domain):
                res = self.client.post("/demo/bind-room/run", json={"domain": domain})
                self.assertEqual(res.status_code, 200)
                body = res.get_json()
                self.assertIn(needle, body["domain_label"])
                for lens in body["domain_lenses"]:
                    title = (lens.get("profile") or {}).get("title") or ""
                    desc = (lens.get("profile") or {}).get("description") or ""
                    self.assertTrue(title)
                    self.assertNotEqual(title, lens["lens"])
                    self.assertTrue(desc)
                    self.assertNotEqual(desc, lens["lens"])

    def test_step_json_is_domain_specific(self):
        ins = self.client.post("/demo/bind-room/run", json={"domain": "insurance"}).get_json()
        cli = self.client.post("/demo/bind-room/run", json={"domain": "biology"}).get_json()
        self.assertIn("premium", json.dumps(ins["step3_json"]))
        self.assertIn("protocol_id", json.dumps(cli["step3_json"]))
        self.assertNotEqual(ins["step2_json"]["reason"], cli["step2_json"]["reason"])

    def test_corrections_names_verra_retired(self):
        res = self.client.get("/trust/corrections")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Verra is retired", res.data)
        self.assertIn(b"Bind Room", res.data)

    def test_mandate_registry_is_not_insurance(self):
        res = self.client.get("/compliance/mandate-registry", follow_redirects=False)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Mandate registry", res.data)
        self.assertIn(b"spend-mandate.json", res.data)
        self.assertNotIn(b"Carrier wedge", res.data)

    def test_check_feed_has_generation_timestamp(self):
        res = self.client.get("/check")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Last restraint feed", res.data)
        self.assertIn(b"datetime=", res.data)
        self.assertNotIn(b"2026-10-28T20:24:04Z", res.data)

    def test_pricing_reconciles_49_dollar_names(self):
        res = self.client.get("/pricing")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"canonical name", res.data)
        self.assertIn(b"Instant receipt", res.data)
        self.assertIn(b"Paper Check", res.data)

    def test_cmdk_includes_vertical_alias(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'try \xe2\x80\x9cvertical\xe2\x80\x9d', res.data)
        self.assertIn(b"Verticals / industries", res.data)
        self.assertIn(b'href="/verticals"', res.data)
        self.assertIn(b"animal_welfare", res.data)
        self.assertIn(b">Verticals</a>", res.data)
        self.assertIn(b"See industries", res.data)
        self.assertNotIn(b">Bind demo</a>", res.data)

    def test_verticals_and_industries_urls_are_the_picker(self):
        bounced = self.client.get("/industries", follow_redirects=False)
        self.assertEqual(bounced.status_code, 302)
        self.assertTrue(bounced.headers["Location"].endswith("/verticals"))
        for path in ("/verticals", "/demo/bind-room"):
            with self.subTest(path=path):
                res = self.client.get(path)
                self.assertEqual(res.status_code, 200)
                self.assertIn(b"Pick an industry", res.data)
                self.assertIn(b"Reinsurance", res.data)
                self.assertIn(b"Clinical", res.data)
                self.assertIn(b"Counsel", res.data)

    def test_session_id_is_not_verra_prefix(self):
        body = self.client.post("/demo/bind-room/run", json={"domain": "insurance"}).get_json()
        self.assertTrue(body["session_id"].startswith("bind-"))
        self.assertFalse(body["session_id"].startswith("verra-"))

    def test_normalize_aliases(self):
        self.assertEqual(bind_room_demo.normalize_domain("Counsel"), "epistemics")
        self.assertEqual(bind_room_demo.normalize_domain("iacuc"), "animal_welfare")
        self.assertEqual(bind_room_demo.normalize_domain("animal_welfare"), "animal_welfare")
        self.assertIsNone(bind_room_demo.normalize_domain("nope"))

    def test_animal_welfare_is_not_insurance_bind(self):
        page = self.client.get("/demo/bind-room?domain=animal_welfare")
        self.assertEqual(page.status_code, 200)
        html = page.data.decode()
        self.assertIn("Animal welfare", html)
        self.assertIn('class="domain-btn active" data-domain="animal_welfare"', html)
        self.assertNotIn('class="domain-btn active" data-domain="insurance"', html)
        for slug in ("iacuc", "awa", "olaw", "animal"):
            with self.subTest(slug=slug):
                res = self.client.post("/demo/bind-room/run", json={"domain": slug})
                self.assertEqual(res.status_code, 200)
                body = res.get_json()
                gate = body["step3_json"]
                self.assertEqual(body["domain"], "animal_welfare")
                self.assertIn("IACUC", body["domain_label"])
                self.assertEqual(gate["protocol_id"], "IACUC-2026-014")
                self.assertEqual(gate["action"], "animal_procedure")
                self.assertNotIn("premium_usd", gate)
                self.assertNotIn("policy_number", gate)
                self.assertNotIn("DEMO-PAS", json.dumps(gate))
                self.assertNotEqual(gate.get("finality_event"), "policy_bind")


if __name__ == "__main__":
    unittest.main()
