"""Public URL lock + listing/MCP dating tests. Run from gate/: python3 test_listings.py"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from unittest import mock

# Isolate env before importing app.
os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-listings.db")
os.environ.pop("RENDER_EXTERNAL_URL", None)
os.environ.pop("RENDER_EXTERNAL_HOSTNAME", None)

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import public_url  # noqa: E402
import listings  # noqa: E402
import mcp_server  # noqa: E402
import app as gate_app  # noqa: E402


class ResolveTests(unittest.TestCase):
    def test_localhost_is_local(self):
        self.assertTrue(public_url.is_local_url("http://localhost:5001"))
        self.assertTrue(public_url.is_local_url("http://127.0.0.1:5001"))
        self.assertFalse(public_url.is_local_url("https://gate-api.onrender.com"))

    def test_render_lifts_localhost(self):
        with mock.patch.dict(
            os.environ,
            {
                "GATE_PUBLIC_URL": "http://localhost:5001",
                "RENDER_EXTERNAL_URL": "https://gate-api.onrender.com",
                "GATE_DEV_MODE": "0",
            },
            clear=False,
        ):
            self.assertEqual(public_url.resolve_public_url(), "https://gate-api.onrender.com")

    def test_explicit_https_wins(self):
        with mock.patch.dict(
            os.environ,
            {
                "GATE_PUBLIC_URL": "https://gate.velaru.xyz",
                "RENDER_EXTERNAL_URL": "https://gate-api.onrender.com",
            },
            clear=False,
        ):
            self.assertEqual(public_url.resolve_public_url(), "https://gate.velaru.xyz")

    def test_assert_prod_refuses_local(self):
        with mock.patch.dict(
            os.environ,
            {
                "GATE_PUBLIC_URL": "http://localhost:5001",
                "GATE_DEV_MODE": "0",
                "GATE_ALLOW_LOCAL": "0",
                "GATE_DB_PATH": "/var/data/gate.db",
            },
            clear=False,
        ):
            os.environ.pop("RENDER_EXTERNAL_URL", None)
            os.environ.pop("RENDER_EXTERNAL_HOSTNAME", None)
            with self.assertRaises(SystemExit):
                public_url.assert_prod_public()


class ManifestTests(unittest.TestCase):
    def test_listings_have_all_dates(self):
        m = listings.listings_manifest("https://example.test", "hello@velaru.xyz")
        self.assertEqual(m["rule"], "Date all. Marry one write path.")
        for key in ("mcp_gateways", "cloudflare", "x402", "guidewire", "duckcreek"):
            self.assertIn(key, m["dates"])
        self.assertIn("google", m["do_not_date"])

    def test_mcp_stateless_tools_list(self):
        body, status = mcp_server.handle_message(
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            public_url="https://example.test",
            call_tool=lambda n, a: {},
        )
        self.assertEqual(status, 200)
        names = {t["name"] for t in body["result"]["tools"]}
        self.assertEqual(names, {"fuse_lookup", "fuse_hop", "welded_act", "pas_bind_check"})


class FlaskListingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_health_ok_in_dev(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data["service"], "gate-api")
        self.assertIn("mcp", data)

    def test_health_503_when_prod_local(self):
        prev = gate_app.GATE_DEV_MODE
        gate_app.GATE_DEV_MODE = False
        try:
            with mock.patch.dict(
                os.environ,
                {"GATE_PUBLIC_URL": "http://localhost:5001", "GATE_DEV_MODE": "0"},
                clear=False,
            ):
                os.environ.pop("RENDER_EXTERNAL_URL", None)
                os.environ.pop("RENDER_EXTERNAL_HOSTNAME", None)
                r = self.client.get("/health")
                self.assertEqual(r.status_code, 503)
                self.assertEqual(r.get_json()["status"], "not_public")
        finally:
            gate_app.GATE_DEV_MODE = prev

    def test_well_known_listings(self):
        r = self.client.get("/.well-known/listings.json")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIn("dates", data)
        self.assertIn("guidewire", data["dates"])

    def test_mcp_initialize_and_tools(self):
        r = self.client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1"},
                },
            },
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn("Mcp-Session-Id", r.headers)
        self.assertEqual(r.get_json()["result"]["protocolVersion"], "2025-03-26")

        r2 = self.client.post("/mcp", json={"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        self.assertEqual(r2.status_code, 200)
        tools = r2.get_json()["result"]["tools"]
        self.assertGreaterEqual(len(tools), 4)

    def test_listing_packets(self):
        r = self.client.get("/listings/guidewire-partnerconnect.json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["company"], "Nisaba LLC")
        r2 = self.client.get("/listings/duckcreek-partner.json")
        self.assertIn("Paymentus", r2.get_json()["do_not_confuse"])
        r3 = self.client.get("/listings/kong-mcp.yaml")
        self.assertEqual(r3.status_code, 200)
        self.assertIn("/mcp", r3.get_data(as_text=True))

    def test_mcp_welded_act_demo(self):
        r = self.client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "welded_act", "arguments": {"fuse_id": "fuse_velaru_drill", "action": "test"}},
            },
        )
        self.assertEqual(r.status_code, 200)
        payload = r.get_json()
        self.assertEqual(payload.get("jsonrpc"), "2.0")
        text = payload["result"]["content"][0]["text"]
        inner = json.loads(text)
        self.assertIn("acted", inner)
        self.assertIsInstance(inner["acted"], bool)


if __name__ == "__main__":
    unittest.main()
