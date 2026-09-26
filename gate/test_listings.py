"""Public URL lock + listing/MCP dating tests. Run from gate/: python3 test_listings.py"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
import uuid
import base64
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from unittest import mock

# Isolate env before importing app.
os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-listings.db")
os.environ.pop("RENDER_EXTERNAL_URL", None)
os.environ.pop("RENDER_EXTERNAL_HOSTNAME", None)

# Receipt signing keys for evidence custody.
try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption, PublicFormat

    _priv = Ed25519PrivateKey.generate()
    _priv_bytes = _priv.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    _pub_bytes = _priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    os.environ["GATE_RECEIPT_PRIVATE_KEY"] = base64.b64encode(_priv_bytes).decode("utf-8")
    os.environ["GATE_RECEIPT_PUBLIC_KEY"] = base64.b64encode(_pub_bytes).decode("utf-8")
except Exception:
    # Tests can still run without signing if receipt keys are missing.
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)


def _now():
    return datetime.now(timezone.utc).isoformat()

import public_url  # noqa: E402
import listings  # noqa: E402
import mcp_server  # noqa: E402
import fields  # noqa: E402
import weld  # noqa: E402
import bind_room  # noqa: E402
import bound  # noqa: E402
import exclusive  # noqa: E402
import floor  # noqa: E402
import particular  # noqa: E402
import liturgy  # noqa: E402
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
        self.assertIn("bind_room", m)
        self.assertIn("operator_invoice", m)
        self.assertTrue(m["operator_invoice"]["licensed_only"])
        self.assertIn("bound_answer", m)
        self.assertIn("exclusive_timing", m)
        self.assertIn("floor", m)
        self.assertIn("particular", m)
        self.assertIn("capture", m)
        self.assertIn("inhabitant", m["floor"])
        self.assertIn("commit_auth", m)
        self.assertIn("spend_protocol", m)
        self.assertIn("command_radiation", m)
        self.assertIn("license_fuse", m)
        self.assertIn("restraint", m)
        self.assertIn("register", m)
        self.assertIn("liturgy", m)
        self.assertFalse(m["particular"]["tuesday_moved"])
        self.assertIn("policycenter", m["welds"])
        self.assertIn("PII", " ".join(m["refuse"]))
        self.assertIn("track_record", m)
        self.assertTrue(m["track_record"]["page"].endswith("/record"))

    def test_mcp_stateless_tools_list(self):
        body, status = mcp_server.handle_message(
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            public_url="https://example.test",
            call_tool=lambda n, a: {},
        )
        self.assertEqual(status, 200)
        names = {t["name"] for t in body["result"]["tools"]}
        self.assertEqual(
            names,
            {
                "fuse_lookup",
                "fuse_hop",
                "welded_act",
                "pas_bind_check",
                "policycenter_pre_bind",
                "mga_authority",
            },
        )


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
        pkt = r.get_json()
        self.assertIn("qusar", pkt)
        self.assertIn("/for/qusar", pkt["qusar"]["plate"])
        self.assertIn("Qusar agents draft", pkt["one_liner"])
        self.assertEqual(pkt["money"]["bind_room"], "$1,750")
        self.assertIn("policycenter_pre_bind", pkt["demo"]["mcp_tools"])
        self.assertEqual(pkt["company"], "Nisaba LLC")
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
        self.assertFalse(inner.get("write_executed", True))
        self.assertTrue(inner.get("clearance_only") or inner.get("acted") is not None)

    def test_nav_and_clickable_pages_are_not_broken(self):
        # Home uses bind-surface chrome; buyer chrome lives on operator pages.
        home = self.client.get("/").get_data(as_text=True)
        self.assertIn('href="/clear"', home)
        self.assertIn(">Clear</a>", home)
        self.assertIn('href="/seal"', home)
        self.assertIn(">Seal</a>", home)
        self.assertIn('href="/go"', home)
        self.assertIn(">Go</a>", home)
        self.assertIn('href="/never"', home)
        self.assertIn(">Never</a>", home)
        self.assertIn('href="/trust"', home)
        self.assertNotIn('href="/action-os"', home)
        self.assertNotIn('href="/science"', home)
        self.assertNotIn('href="/family"', home)

        buyer = self.client.get("/pricing").get_data(as_text=True)
        chrome = buyer.split("<footer>", 1)[0]
        self.assertIn('href="/operator"', chrome)
        self.assertIn(">Weld</a>", chrome)
        self.assertIn('href="/clear"', chrome)
        self.assertIn(">Clear</a>", chrome)
        self.assertIn('href="/seal"', chrome)
        self.assertIn(">Seal</a>", chrome)
        self.assertIn('href="/go"', chrome)
        self.assertIn('href="/never"', chrome)
        self.assertIn('href="/live"', chrome)
        self.assertIn(">Live</a>", chrome)
        self.assertIn('href="/register"', chrome)
        self.assertIn(">Fees</a>", chrome)
        self.assertIn(">Pricing</a>", chrome)
        # Buyer chrome only — no doctrine / family / lab in nav or footer
        self.assertNotIn(">Action OS</a>", chrome)
        self.assertNotIn(">Scanner</a>", chrome)
        self.assertNotIn(">Uplink</a>", chrome)
        for path in (
            "/",
            "/start",
            "/scanner",
            "/uplink",
            "/capture",
            "/this",
            "/docs",
            "/for/carriers",
            "/for/qusar",
            "/for/consumers",
            "/signup",
            "/login",
            "/pricing",
            "/install",
            "/register",
            "/operator",
            "/clear",
            "/seal",
            "/go",
            "/never",
            "/positive-clear",
            "/scenario-3",
            "/uapa-seal",
            "/admt",
            "/trusted-contact",
            "/stair",
            "/live",
            "/privacy",
            "/terms",
            "/bind-room",
            "/for/operators",
            "/action-os",
            "/science",
            "/focus",
            "/positioning",
            "/scorecard",
            "/production-skin",
            "/proof",
            "/runbook",
            "/dogfood",
            "/production-weld",
        ):
            r = self.client.get(path)
            self.assertEqual(r.status_code, 200, path)
        carriers = self.client.get("/for/carriers").get_data(as_text=True)
        self.assertNotIn('href="/v1/pas/policycenter/pre-bind"', carriers)
        self.assertIn('href="/for/qusar"', carriers)
        self.assertIn("Qusar", carriers)
        qusar = self.client.get("/for/qusar").get_data(as_text=True)
        self.assertIn("Qusar agents draft", qusar)
        self.assertIn('href="/bind-room"', qusar)
        self.assertIn("guidewire-partnerconnect.json", qusar)
        consumers = self.client.get("/for/consumers").get_data(as_text=True)
        self.assertNotIn("Open Mishara", consumers)
        self.assertIn("Open Gate", consumers)

        aos = self.client.get("/.well-known/action-os.json").get_json()
        self.assertEqual(aos["spec"], "nisaba-action-os-v2")
        self.assertIn("DENY", aos["formula"])
        self.assertTrue(aos["category_includes_force"])
        self.assertFalse(aos["force_production_weld"])
        self.assertNotIn("their_production", aos)
        self.assertIn("playbook", aos)

        gate = self.client.get("/.well-known/gate.json").get_json()
        self.assertIn("formula", gate)
        self.assertIn("action_os", gate)
        self.assertIn("scorecard", gate)
        self.assertIn("DENY", gate["formula"])

        import db as gate_db

        with gate_db.db() as conn:
            gate_db._ensure_dogfood_table(conn)
            gate_db._ensure_third_party_welds(conn)
            conn.execute("DELETE FROM dogfood_welds")
            conn.execute("DELETE FROM third_party_welds")

        sc = self.client.get("/.well-known/scorecard.json").get_json()
        self.assertEqual(sc["spec"], "nisaba-scorecard-v2")
        self.assertEqual(len(sc["family"]), 5)
        # Proof ladder: all_pass → L2 deploy 7.5; their_production still false without weld
        self.assertNotIn("their_production", sc)
        self.assertEqual(sc["mode"], "pre_rev_maxed")
        deploy = sc["gate"]["dimensions"]["deployability"]
        self.assertGreaterEqual(deploy, 7.0)
        self.assertLess(deploy, 8.0)
        self.assertGreaterEqual(sc["gate"]["dimensions"]["voice"], 9.0)
        self.assertTrue(all(p["maxed"] for p in sc["family"] if p["id"] != "gate"))
        self.assertIn("family", gate)
        self.assertEqual(self.client.get("/family").status_code, 200)
        self.assertNotIn("/family", self.client.get("/").get_data(as_text=True))


class BoundAnswerTests(unittest.TestCase):
    def test_dead_hop_holds(self):
        ba = bound.from_payload(
            {"verdict": False, "halt": True, "state": "DEAD", "verify_url": "https://velaru.xyz/verify?r=1"},
            200,
        )
        self.assertFalse(ba["answer"])
        self.assertTrue(ba["holds"])
        self.assertTrue(ba["tests"]["enforced"])
        self.assertTrue(ba["tests"]["provable"])
        self.assertEqual(ba["prize"], "a no that holds")

    def test_live_yes_is_bound_not_the_prize(self):
        ba = bound.from_payload(
            {"verdict": True, "state": "LIVE", "verify_url": "https://velaru.xyz/verify?r=1"},
            200,
        )
        self.assertTrue(ba["answer"])
        self.assertFalse(ba["holds"])
        self.assertEqual(ba["prize"], "a bound yes")

    def test_dead_that_still_acted_does_not_hold(self):
        ba = bound.from_payload(
            {"verdict": False, "state": "DEAD", "acted": True, "halt": True},
            200,
        )
        self.assertFalse(ba["holds"])
        self.assertFalse(ba["tests"]["enforced"])

    def test_pc_block_holds_on_write_path(self):
        plan = weld.policycenter_plan("pc:1", {"verdict": False, "halt": True, "state": "DEAD"}, 200)
        ba = bound.from_payload(plan, 200)
        self.assertTrue(ba["holds"])
        self.assertIn("bind-only", ba["write_path"] or "")


class ExclusiveTimingTests(unittest.TestCase):
    def test_demo_hop_is_museum(self):
        ba = bound.from_payload(
            {"verdict": False, "halt": True, "state": "DEAD", "verify_url": "https://velaru.xyz/verify"},
            200,
        )
        ex = exclusive.classify({"demo": True}, ba, demo=True)
        self.assertTrue(ex["museum"])
        self.assertFalse(ex["exclusive"])
        self.assertFalse(ex["their_production"])
        self.assertIsNone(ex["product"])

    def test_closed_world_dead_is_non_event(self):
        payload = {
            "spec": "gate-welded-act-v1",
            "closed_world": True,
            "acted": False,
            "halt": True,
            "hop": {"verdict": False, "halt": True, "state": "DEAD", "verify_url": "https://velaru.xyz/verify"},
        }
        ba = bound.from_payload(payload, 200)
        ex = exclusive.classify(payload, ba, closed_world=True)
        self.assertFalse(ex["museum"])
        self.assertTrue(ex["exclusive"])
        self.assertTrue(ex["non_event"])
        self.assertEqual(ex["product"], "the irreversible that didn't occur")
        self.assertIsNone(ex["winner"])
        self.assertFalse(ex["crown_the_miss"])
        self.assertFalse(ex["their_production"])

    def test_pc_honor_required_not_their_prod(self):
        plan = weld.policycenter_plan("pc:1", {"verdict": False, "halt": True, "state": "DEAD"}, 200)
        ba = bound.from_payload(plan, 200)
        ex = exclusive.classify(plan, ba)
        self.assertTrue(ex["exclusive_if_honored"])
        self.assertFalse(ex["exclusive"])
        self.assertFalse(ex["their_production"])
        self.assertTrue(ex["non_event"])


class FloorTests(unittest.TestCase):
    def test_no_cleverer_layer(self):
        m = floor.manifesto("https://example.test")
        self.assertIsNone(m["cleverer_layer"])
        self.assertIsNone(m["winner"])
        self.assertFalse(m["crown_the_miss"])
        self.assertIn("did occur", m["not_in_contest"])
        self.assertIn("Escape is still from something", m["escape_is_still_from_something"])
        names = [x["is"] for x in m["layers"]]
        self.assertEqual(names, ["talk", "a fact", "control", "a clean timeline"])

    def test_museum_does_not_treat_as_real(self):
        s = floor.stamp({"museum": True})
        self.assertFalse(s["treat_as_real"])
        self.assertIsNone(s["cleverer_layer"])
        self.assertTrue(s["dead_over_live"])

    def test_exclusive_treats_as_real(self):
        s = floor.stamp({"museum": False})
        self.assertTrue(s["treat_as_real"])


class ParticularTests(unittest.TestCase):
    def test_hop_without_job_is_philosophizing(self):
        payload = {"verdict": False, "halt": True, "state": "DEAD", "fuse_id": "fuse_velaru_drill"}
        ba = bound.from_payload(payload, 200)
        ex = exclusive.classify({"demo": True}, ba, demo=True)
        p = particular.classify(payload, ba, ex, demo=True)
        self.assertTrue(p["philosophizing"])
        self.assertFalse(p["particular"])
        self.assertFalse(p["tuesday_moved"])

    def test_named_job_on_prebind_is_particular(self):
        plan = weld.policycenter_plan("pc:THIS", {"verdict": False, "halt": True, "state": "DEAD"}, 200)
        plan["fuse_id"] = "fuse_velaru_drill"
        plan["job_id"] = "pc:THIS"
        ba = bound.from_payload(plan, 200)
        ex = exclusive.classify(plan, ba)
        p = particular.classify(plan, ba, ex)
        self.assertTrue(p["particular"])
        self.assertFalse(p["philosophizing"])
        self.assertTrue(p["this_one_tried"])
        self.assertEqual(p["name_one"]["not"], "AI")
        self.assertFalse(p["tuesday_moved"])

    def test_refuses_to_name_ai(self):
        named = particular.name_one({"fuse_id": "AI", "job_id": "x"})
        self.assertIsNone(named["fuse_id"])


class FieldAndWeldTests(unittest.TestCase):
    def test_pii_rejected(self):
        err = fields.pii_error({"fuse_id": "fuse_velaru_drill", "ssn": "000-00-0000"})
        self.assertIsNotNone(err)
        self.assertEqual(err["error"]["code"], "no_pii")
        self.assertIn("ssn", err["error"]["rejected_keys"])

    def test_allowlist_drops_unknown(self):
        cleaned = fields.allowlist_pas({"fuse_id": "x", "job_id": "j1", "named_insured": "nope", "extra": 1})
        self.assertEqual(cleaned, {"fuse_id": "x", "job_id": "j1"})

    def test_license_id_is_not_license_number(self):
        self.assertIn("license_number", fields.PII_KEYS)
        self.assertNotIn("license_id", fields.PII_KEYS)
        self.assertIn("license_id", fields.ALLOWED_PAS_KEYS)
        err = fields.pii_error({"fuse_id": "fuse_velaru_drill", "license_number": "AB-123"})
        self.assertIsNotNone(err)
        cleaned = fields.allowlist_pas(
            {"fuse_id": "x", "job_id": "j1", "license_id": "lic:CO-1", "license_number": "nope"}
        )
        self.assertEqual(cleaned, {"fuse_id": "x", "job_id": "j1", "license_id": "lic:CO-1"})

    def test_pc_dead_raises_uw_issue(self):
        hop = {"verdict": False, "halt": True, "state": "DEAD"}
        plan = weld.policycenter_plan("pc:1", hop, 200)
        self.assertFalse(plan["allow_bind"])
        self.assertIn("uw-issues", plan["raise_uw_issue"]["path"])
        self.assertEqual(plan["raise_uw_issue"]["blocking_point_required"], "Binding")
        self.assertIn("bind-only", plan["do_not_call"]["path"])
        paths = [w["path"] for w in plan["do_not_call_all"]]
        self.assertTrue(any("bind-and-issue" in p for p in paths))
        self.assertTrue(any("bind-only" in p for p in paths))

    def test_pc_live_allows_bind(self):
        hop = {"verdict": True, "state": "LIVE"}
        plan = weld.policycenter_plan("pc:1", hop, 200)
        self.assertTrue(plan["allow_bind"])
        self.assertIsNone(plan["raise_uw_issue"])
        self.assertIn("bind-only", plan["next"]["path"])
        self.assertNotIn("bind-and-issue", plan["next"]["path"])

    def test_mga_premium_blocks(self):
        hop = {"verdict": True, "state": "LIVE"}
        plan = weld.mga_authority(
            hop,
            200,
            premium=60000,
            authority_limit=50000,
            line="GL",
            state="CO",
            allowed_lines=None,
            allowed_states=None,
        )
        self.assertEqual(plan["result"], "BLOCK")
        self.assertIn("premium_exceeds_authority", plan["reasons"])
        self.assertFalse(plan["bind_allowed"])

    def test_officer_pack_has_5a2(self):
        pack = bind_room.officer_pack("https://example.test", "hello@velaru.xyz")
        ids = [s["id"] for s in pack["sections"]]
        self.assertIn("5.A.2", ids)
        self.assertIn("5.A.1", ids)
        self.assertIn("5.A.13", ids)


class BindRoomFlaskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_no_pii_on_demo_pre_bind(self):
        r = self.client.post(
            "/demo/pas/policycenter/pre-bind",
            json={"fuse_id": "fuse_velaru_drill", "ssn": "000-00-0000", "job_id": "pc:1"},
        )
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.get_json()["error"]["code"], "no_pii")

    def test_pc_pre_bind_blocks_and_raises_uw(self):
        dead = {
            "ok": True,
            "verdict": False,
            "halt": True,
            "state": "DEAD",
            "verify_url": "https://velaru.xyz/verify?r=demo",
        }
        with mock.patch.object(gate_app, "velaru_fuse", return_value=(dead, 200, {})):
            r = self.client.post(
                "/demo/pas/policycenter/pre-bind",
                json={"fuse_id": "fuse_velaru_drill", "job_id": "pc:1"},
            )
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertFalse(data["allow_bind"])
        self.assertIn("uw-issues", data["raise_uw_issue"]["path"])
        self.assertIn("bind-only", data["do_not_call"]["path"])
        paths = [w["path"] for w in data["do_not_call_all"]]
        self.assertTrue(any("bind-and-issue" in p for p in paths))
        self.assertTrue(data["particular"]["particular"])
        self.assertTrue(data["particular"]["this_one_tried"])
        self.assertFalse(data["particular"]["tuesday_moved"])

    def test_mga_premium_over_limit_blocks(self):
        live = {"ok": True, "verdict": True, "state": "LIVE"}
        with mock.patch.object(gate_app, "velaru_fuse", return_value=(live, 200, {})):
            r = self.client.post(
                "/demo/pas/mga-authority",
                json={
                    "fuse_id": "fuse_velaru_drill",
                    "premium": 60000,
                    "authority_limit": 50000,
                },
            )
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data["result"], "BLOCK")
        self.assertIn("premium_exceeds_authority", data["reasons"])

    def test_officer_pack_route(self):
        r = self.client.get("/bind-room/officer-pack.json")
        self.assertEqual(r.status_code, 200)
        ids = [s["id"] for s in r.get_json()["sections"]]
        self.assertIn("5.A.2", ids)

    def test_control_not_model_listing(self):
        r = self.client.get("/listings/control-not-model.json")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIn("Not ECDIS", data["classification"])
        self.assertIn("bind-appendix", data["audit_rights"])

    def test_bind_room_page(self):
        r = self.client.get("/bind-room")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"Officer pack", r.data)

    def test_diligence_surfaces(self):
        page = self.client.get("/diligence")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"irreversible write", page.data)
        self.assertIn(b"2,500", page.data)
        self.assertIn(b"Free 72h REVIEW", page.data)
        self.assertIn(b"Reply REVIEW", page.data)
        offer = self.client.get("/diligence/offer.json")
        self.assertEqual(offer.status_code, 200)
        data = offer.get_json()
        self.assertEqual(data["price"]["deposit"], "$2,500")
        self.assertEqual(data["ask"], "Reply REVIEW")
        self.assertEqual(data["paths"]["free_review"]["price"], "$0")
        self.assertIn("/diligence", data["urls"]["page"])
        one = self.client.get("/diligence/one-pager.txt")
        self.assertEqual(one.status_code, 200)
        self.assertIn(b"REVIEW", one.data)
        self.assertIn(b"DEPOSIT", one.data)
        self.assertEqual(one.content_type.split(";")[0], "text/plain")

    def test_diligence_checkout_dev(self):
        r = self.client.post(
            "/diligence/checkout",
            data={"email": "ops@example.com"},
            follow_redirects=False,
        )
        self.assertEqual(r.status_code, 302)
        self.assertIn("/install/success", r.headers.get("Location", ""))

    def test_bind_room_paid_writes_spend_map_never_spent_twice(self):
        import db as gate_db
        from urllib.parse import parse_qs, urlparse

        r = self.client.post(
            "/bind-room/checkout",
            data={"email": "cuo@example.test"},
            follow_redirects=False,
        )
        self.assertIn(r.status_code, (302, 303))
        loc = r.headers.get("Location", "")
        self.assertIn("/install/success", loc)
        session_id = parse_qs(urlparse(loc).query).get("session_id", [""])[0]
        self.assertTrue(session_id)
        order = dict(gate_db.get_install_order_by_session(session_id))
        job_id = f"br:{order['id']}"
        first = self.client.get(f"/v1/never?job_id={job_id}")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.get_json()["word"], "SPENT")
        self.assertTrue(first.get_json()["spent"])
        self.assertNotIn("their_production", first.get_json())
        second = self.client.get(f"/v1/never?job_id={job_id}")
        self.assertEqual(second.get_json()["word"], "SPENT")
        again = self.client.get(f"/v1/never?job_id={job_id}")
        self.assertEqual(again.get_json()["word"], "SPENT")
        job = self.client.get("/bind-room/job.json")
        self.assertEqual(job.status_code, 200)
        self.assertIn(job_id, job.get_json().get("job_ids") or [])
        spec = self.client.get("/.well-known/spend-protocol.json").get_json()
        self.assertEqual(spec["bind_room"]["redeem"].rstrip("/").split("/")[-1], "redeem")
        self.assertIn("/v1/pas/bind-ticket/redeem", spec["bind_room"]["redeem"])
        self.assertIn("/demo/", spec["bind_room"]["not_demo"])

    def test_bound_page_and_manifest(self):
        r = self.client.get("/bound")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"A no that holds", r.data)
        r2 = self.client.get("/.well-known/bound-answer.json")
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.get_json()["more_valuable_than_a_question"], "a no that holds")

    def test_only_page_and_manifest(self):
        r = self.client.get("/only")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"never happens", r.data)
        r2 = self.client.get("/.well-known/exclusive-timing.json")
        self.assertEqual(r2.status_code, 200)
        self.assertNotIn("their_production", r2.get_json())
        self.assertTrue(r2.get_json()["receipt_is_not_the_product"])
        self.assertIsNone(r2.get_json()["winner"])
        self.assertFalse(r2.get_json()["crown_the_miss"])

    def test_floor_page_and_manifest(self):
        r = self.client.get("/floor")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"cleverer", r.data)
        r2 = self.client.get("/.well-known/floor.json")
        self.assertEqual(r2.status_code, 200)
        self.assertIsNone(r2.get_json()["cleverer_layer"])
        self.assertIsNone(r2.get_json()["winner"])
        self.assertIn(b"not in this contest", r.data)

    def test_this_page_and_manifest(self):
        r = self.client.get("/this")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"This one", r.data)
        r2 = self.client.get("/.well-known/particular.json")
        self.assertEqual(r2.status_code, 200)
        self.assertTrue(r2.get_json()["not_a_deeper_idea"])
        self.assertFalse(r2.get_json()["tuesday_moved"])

    def test_capture_page_and_manifest(self):
        r = self.client.get("/capture")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"bind-only", r.data)
        self.assertIn(b"guidewire-gosu-prebind.gs", r.data)
        r2 = self.client.get("/.well-known/capture.json")
        self.assertEqual(r2.status_code, 200)
        data = r2.get_json()
        self.assertNotIn("their_production", data)
        paths = [w["path"] for w in data["cloud_api_spend_writes"]]
        self.assertTrue(any("bind-only" in p for p in paths))
        self.assertIn("quote", data["uw_issue"]["not_sufficient_why"].lower())
        self.assertIn("verify_url", data["halt_always_includes"])
        self.assertIn("inhabitant_url", data["halt_always_includes"])
        self.assertIn("guidewire-gosu-prebind.gs", data["in_house_paste"]["ui_bind"])
        self.assertIn("guidewire-renewal-prebind.gs", data["in_house_paste"]["renewal_auto_bind"])
        self.assertIn("tpm_hsm", data["later"])
        doors = [d["door"] for d in data["other_doors"]]
        self.assertTrue(any("UI Bind" in d for d in doors))

    def test_gosu_listings_and_worker_receipt(self):
        r = self.client.get("/listings/guidewire-gosu-prebind.gs")
        self.assertEqual(r.status_code, 200)
        text = r.get_data(as_text=True)
        self.assertIn("assertBindAllowed", text)
        self.assertIn("VelaruBlocksBind", text)
        self.assertIn("does not charge", text.lower())
        r2 = self.client.get("/listings/guidewire-renewal-prebind.gs")
        self.assertEqual(r2.status_code, 200)
        self.assertIn("assertBeforeAutoBind", r2.get_data(as_text=True))
        worker = self.client.get("/listings/cloudflare-worker-bind.js").get_data(as_text=True)
        self.assertIn("haltResponse", worker)
        self.assertIn("verify_url", worker)
        self.assertIn("inhabitant_url", worker)
        self.assertIn("bind-ticket/redeem", worker)
        self.assertIn("spend_fingerprint", worker)
        self.assertIn("LICENSE_ID", worker)
        self.assertIn("counterpart_id", worker)
        self.assertIn("spend_write_not_in_protocol", worker)
        self.assertIn("toISOString", worker)
        generic = self.client.get("/listings/cloudflare-worker.js").get_data(as_text=True)
        self.assertIn("haltResponse", generic)

    def test_prebind_halt_always_has_verify_url(self):
        plan = weld.policycenter_plan("pc:1", {"verdict": False, "halt": True, "state": "DEAD"}, 200)
        self.assertEqual(plan["verify_url"], weld.DEFAULT_VERIFY)
        plan2 = weld.policycenter_plan(
            "pc:1",
            {"verdict": False, "halt": True, "verify_url": "https://velaru.xyz/verify?r=1"},
            200,
        )
        self.assertIn("r=1", plan2["verify_url"])

    def test_liturgy_trilogy(self):
        mass = liturgy.stranger_mass("https://example.test", [])
        self.assertEqual(mass["spec"], "gate-stranger-mass-v1")
        self.assertIn("verify_url", mass)
        self.assertTrue(mass["not_marketing"])
        relics = liturgy.relics_manifest("https://example.test", [])
        self.assertGreaterEqual(relics["count"], 1)
        refusal = liturgy.refusal_pack("https://example.test", "hello@velaru.xyz", "$7,500")
        self.assertIn("non-entity", refusal["product"])
        tattoo = liturgy.weld_tattoo_manifest("https://example.test")
        self.assertIn("cloudflare-worker-bind.js", tattoo["worker"])
        self.assertFalse(tattoo["their_production"])

    def test_mass_refusal_tattoo_pages(self):
        r = self.client.get("/mass")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"non-event", r.data)
        r2 = self.client.get("/.well-known/mass.json")
        self.assertEqual(r2.status_code, 200)
        self.assertIn("relic", r2.get_json())
        r3 = self.client.get("/refusal")
        self.assertEqual(r3.status_code, 200)
        self.assertIn(b"non-entity", r3.data)
        r4 = self.client.get("/refusal/certificate.schema.json")
        self.assertIsNone(r4.get_json()["proof_of_absence"]["fuse_id"])
        r5 = self.client.get("/tattoo")
        self.assertEqual(r5.status_code, 200)
        self.assertIn(b"Stigmata", r5.data)
        r6 = self.client.get("/.well-known/tattoo.json")
        self.assertEqual(r6.get_json()["spec"], "gate-weld-tattoo-v1")

    def test_demo_hop_attaches_bound_answer(self):
        dead = {
            "ok": True,
            "verdict": False,
            "halt": True,
            "state": "DEAD",
            "verify_url": "https://velaru.xyz/verify?r=demo",
        }
        with mock.patch.object(gate_app, "velaru_fuse", return_value=(dead, 200, {})):
            r = self.client.post("/demo/hop", json={"fuse_id": "fuse_velaru_drill"})
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        ba = body["bound_answer"]
        self.assertTrue(ba["holds"])
        self.assertFalse(ba["answer"])
        self.assertTrue(body["exclusive_timing"]["museum"])
        self.assertNotIn("their_production", body.get("exclusive_timing") or {})
        self.assertIn("stakes", body)
        self.assertIsNone(body["stakes"]["cleverer_layer"])
        self.assertFalse(body["stakes"]["treat_as_real"])

    def test_public_receipt_endpoint_signed_and_chained(self):
        # Create at least one bind event via the demo Pre-Bind door.
        r = self.client.post(
            "/demo/pas/policycenter/pre-bind",
            json={"fuse_id": "fuse_velaru_drill", "job_id": "pc:DEMO-RECEIPT"},
        )
        self.assertEqual(r.status_code, 200)

        import db as gate_db

        latest = gate_db.list_bind_events(None, limit=1)[0]
        event_id = latest["id"]
        self.assertIsNotNone(latest.get("receipt_hash"))

        r2 = self.client.get(f"/.well-known/receipt/{event_id}.json")
        self.assertEqual(r2.status_code, 200)
        payload = r2.get_json()
        self.assertEqual(payload["event_id"], event_id)
        self.assertEqual(payload["receipt_hash"], latest["receipt_hash"])
        # Signing key should exist in tests; if it doesn't, receipt_signature can be null.
        self.assertIn("receipt_signature", payload)
        self.assertIn("prev_receipt_hash", payload)

    def test_evidence_packet_bundle_endpoint(self):
        # Create at least one bind event via the demo Pre-Bind door.
        r = self.client.post(
            "/demo/pas/policycenter/pre-bind",
            json={"fuse_id": "fuse_velaru_drill", "job_id": "pc:DEMO-EVIDENCE-PACKET"},
        )
        self.assertEqual(r.status_code, 200)

        import db as gate_db

        latest = gate_db.list_bind_events(None, limit=1)[0]
        event_id = latest["id"]
        self.assertIsNotNone(latest.get("receipt_hash"))

        spec_url = f"/.well-known/evidence-packet/{event_id}.json"
        r2 = self.client.get(spec_url)
        self.assertEqual(r2.status_code, 200)
        body = r2.get_json()

        self.assertEqual(body["spec"], "gate-evidence-packet-v1")
        self.assertEqual(body["event_id"], event_id)

        self.assertIn("receipt", body)
        self.assertEqual(body["receipt"]["event_id"], event_id)
        self.assertEqual(body["receipt"]["receipt_hash"], latest["receipt_hash"])

        self.assertIn("receipt_inclusion_proof", body)
        self.assertEqual(body["receipt_inclusion_proof"]["spec"], "gate-evidence-proof-v1")
        self.assertEqual(body["receipt_inclusion_proof"]["event_id"], event_id)
        self.assertEqual(
            body["receipt_inclusion_proof"]["receipt_hash"],
            latest["receipt_hash"],
        )

    def test_counterfactual_spend_on_halt_receipt(self):
        dead = {
            "ok": True,
            "verdict": False,
            "halt": True,
            "state": "DEAD",
            "verify_url": "https://velaru.xyz/verify?r=cf",
        }
        with mock.patch.object(gate_app, "velaru_fuse", return_value=(dead, 200, {})):
            r = self.client.post(
                "/demo/pas/policycenter/pre-bind",
                json={"fuse_id": "fuse_velaru_drill", "job_id": "pc:DEMO-CF"},
            )
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertFalse(body.get("allow_bind"))

        import db as gate_db

        latest = gate_db.list_bind_events(None, limit=1)[0]
        event_id = latest["id"]

        r2 = self.client.get(f"/.well-known/receipt/{event_id}.json")
        self.assertEqual(r2.status_code, 200)
        payload = r2.get_json()
        cf = payload.get("counterfactual_spend")
        self.assertIsNotNone(cf)
        self.assertEqual(cf["spec"], "gate-counterfactual-spend-v1")
        self.assertEqual(cf["type"], "INACTION")
        self.assertIn(cf["decision"], ("HALT", "BLOCK"))
        self.assertTrue(cf["forbidden_transitions"])
        self.assertIn("bind-only", cf["forbidden_transitions"][0]["path"])
        self.assertIn("PATH", cf["types"])
        self.assertIsNone(cf["winner"])
        self.assertFalse(cf["crown_the_miss"])

        inh = payload.get("inhabitant")
        self.assertIsNotNone(inh)
        self.assertTrue(inh["they_did_not_have_to_ask"])
        self.assertTrue(inh["spared"])
        self.assertIsNone(inh["name"])
        self.assertFalse(inh["pii"])
        self.assertIn("/inhabitant/", body["inhabitant_url"])

        r_page = self.client.get(f"/inhabitant/{event_id}")
        self.assertEqual(r_page.status_code, 200)
        self.assertIn(b"did not happen", r_page.data)
        r_json = self.client.get(f"/.well-known/inhabitant/{event_id}.json")
        self.assertEqual(r_json.status_code, 200)
        self.assertEqual(r_json.get_json()["audience"], "the someone who has to live there")
        self.assertIsNone(r_json.get_json()["expires"])
        self.assertTrue(r_json.get_json()["including_later"])
        self.assertEqual(r_json.get_json()["consent_of_inhabitant"], "absent")

        missing = self.client.get("/inhabitant/not-a-real-event")
        self.assertEqual(missing.status_code, 404)
        self.assertIn(b"will not invent", missing.data)
        missing_json = self.client.get("/.well-known/inhabitant/not-a-real-event.json")
        self.assertEqual(missing_json.status_code, 404)
        self.assertTrue(missing_json.get_json()["missing"])
        self.assertFalse(missing_json.get_json()["invented_no"])

        afterward = self.client.get("/afterward")
        self.assertEqual(afterward.status_code, 200)
        self.assertIn(b"Including later", afterward.data)

        r3 = self.client.get("/.well-known/counterfactual-spend.json")
        self.assertEqual(r3.status_code, 200)
        manifest = r3.get_json()
        self.assertEqual(manifest["spec"], "gate-counterfactual-spend-v1")
        self.assertIn("evidence_log", manifest)

    def test_evidence_merkle_inclusion_proof(self):
        import evidence_log as evidence_log_mod

        for i in range(3):
            r = self.client.post(
                "/demo/pas/policycenter/pre-bind",
                json={"fuse_id": "fuse_velaru_drill", "job_id": f"pc:DEMO-MERKLE-{i}"},
            )
            self.assertEqual(r.status_code, 200)

        import db as gate_db

        rows = gate_db.list_bind_events_chronological()
        self.assertGreaterEqual(len(rows), 3)
        event_id = rows[-1]["id"]
        receipt_hash = rows[-1]["receipt_hash"]
        leaves = evidence_log_mod.log_from_rows(rows)
        idx = len(leaves) - 1
        proof = evidence_log_mod.inclusion_proof(leaves, idx)
        self.assertTrue(
            evidence_log_mod.verify_inclusion(
                leaf_hash=receipt_hash,
                root_hash=proof["root_hash"],
                proof=proof,
            )
        )

        r_head = self.client.get("/.well-known/evidence-head.json")
        self.assertEqual(r_head.status_code, 200)
        head = r_head.get_json()
        self.assertEqual(head["spec"], "gate-evidence-log-v1")
        self.assertEqual(head["tree_size"], len(leaves))
        self.assertEqual(head["root_hash"], proof["root_hash"])
        self.assertIn("head_signature", head)

        r_proof = self.client.get(f"/.well-known/receipt/{event_id}/proof.json")
        self.assertEqual(r_proof.status_code, 200)
        bundle = r_proof.get_json()
        self.assertEqual(bundle["event_id"], event_id)
        self.assertEqual(bundle["receipt_hash"], receipt_hash)
        self.assertEqual(bundle["tree_head"]["root_hash"], head["root_hash"])
        self.assertTrue(
            evidence_log_mod.verify_inclusion(
                leaf_hash=bundle["receipt_hash"],
                root_hash=bundle["tree_head"]["root_hash"],
                proof=bundle["inclusion"],
            )
        )

    def test_bind_ticket_commit_time_and_replay(self):
        live = {
            "ok": True,
            "verdict": True,
            "state": "LIVE",
            "verify_url": "https://velaru.xyz/verify?r=ticket",
        }
        with mock.patch.object(gate_app, "velaru_fuse", return_value=(live, 200, {})):
            r = self.client.post(
                "/demo/pas/policycenter/pre-bind",
                json={"fuse_id": "fuse_velaru_drill", "job_id": "pc:TICKET-1"},
            )
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertTrue(body["allow_bind"])
        ticket = body["bind_ticket"]
        self.assertEqual(ticket["spec"], "gate-bind-ticket-v1")
        self.assertTrue(ticket["stale_hop_cannot_spend"])
        self.assertIn("token", ticket)
        self.assertIn("spend_fingerprint", ticket)
        self.assertEqual(ticket["spend_write"]["path"], "/job/v1/jobs/pc:TICKET-1/bind-only")
        self.assertTrue(body["commit_time_authorization"]["bind_ticket_required"])
        self.assertTrue(body["commit_time_authorization"]["spend_fingerprint_required"])

        redeem = self.client.post(
            "/demo/pas/bind-ticket/redeem",
            json={
                "ticket_id": ticket["ticket_id"],
                "token": ticket["token"],
                "job_id": "pc:TICKET-1",
                "method": "POST",
                "path": "/job/v1/jobs/pc:TICKET-1/bind-only",
                "spend_fingerprint": ticket["spend_fingerprint"],
                "now": _now(),
            },
        )
        self.assertEqual(redeem.status_code, 200)
        self.assertTrue(redeem.get_json()["ok"])
        self.assertTrue(redeem.get_json()["radiated"])

        replay = self.client.post(
            "/demo/pas/bind-ticket/redeem",
            json={
                "ticket_id": ticket["ticket_id"],
                "token": ticket["token"],
                "job_id": "pc:TICKET-1",
                "method": "POST",
                "path": "/job/v1/jobs/pc:TICKET-1/bind-only",
                "spend_fingerprint": ticket["spend_fingerprint"],
                "now": _now(),
            },
        )
        self.assertEqual(replay.status_code, 403)
        self.assertEqual(replay.get_json()["reason"], "ticket_replay")

        spent = self.client.get("/.well-known/exclusion.json?job_id=pc:TICKET-1")
        self.assertEqual(spent.status_code, 200)
        self.assertTrue(spent.get_json()["spent"])

    def test_spend_protocol_fingerprint_and_mismatch(self):
        import spend_protocol as spend_protocol_mod

        live = {
            "ok": True,
            "verdict": True,
            "state": "LIVE",
            "verify_url": "https://velaru.xyz/verify?r=scan",
        }
        married = spend_protocol_mod.intended_policycenter(job_id="pc:SCAN-1")
        self.assertEqual(married["path"], "/job/v1/jobs/pc:SCAN-1/bind-only")
        self.assertIsNone(
            spend_protocol_mod.intended_policycenter(job_id="pc:SCAN-1", action="bind-and-issue")
        )
        self.assertIsNone(
            spend_protocol_mod.intended_policycenter(
                job_id="pc:SCAN-1", path="/job/v1/jobs/pc:SCAN-1/bind-and-issue"
            )
        )

        with mock.patch.object(gate_app, "velaru_fuse", return_value=(live, 200, {})):
            r = self.client.post(
                "/demo/pas/policycenter/pre-bind",
                json={"fuse_id": "fuse_velaru_drill", "job_id": "pc:SCAN-1"},
            )
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        ticket = body["bind_ticket"]
        fp = ticket["spend_fingerprint"]
        self.assertEqual(fp, spend_protocol_mod.fingerprint(married))
        self.assertEqual(body["spend_protocol"]["fingerprint"], fp)

        missing_now = self.client.post(
            "/demo/pas/bind-ticket/redeem",
            json={
                "ticket_id": ticket["ticket_id"],
                "token": ticket["token"],
                "job_id": "pc:SCAN-1",
            },
        )
        self.assertEqual(missing_now.status_code, 403)
        self.assertEqual(missing_now.get_json()["reason"], "command_now_required")
        self.assertTrue(missing_now.get_json()["radiation_abort"])

        missing = self.client.post(
            "/demo/pas/bind-ticket/redeem",
            json={
                "ticket_id": ticket["ticket_id"],
                "token": ticket["token"],
                "job_id": "pc:SCAN-1",
                "now": _now(),
            },
        )
        self.assertEqual(missing.status_code, 403)
        self.assertEqual(missing.get_json()["reason"], "spend_write_required")

        wrong_path = self.client.post(
            "/demo/pas/bind-ticket/redeem",
            json={
                "ticket_id": ticket["ticket_id"],
                "token": ticket["token"],
                "job_id": "pc:SCAN-1",
                "method": "POST",
                "path": "/job/v1/jobs/pc:SCAN-1/bind-and-issue",
                "spend_fingerprint": fp,
                "now": _now(),
            },
        )
        self.assertEqual(wrong_path.status_code, 403)
        self.assertEqual(wrong_path.get_json()["reason"], "ticket_spend_mismatch")

        ok = self.client.post(
            "/demo/pas/bind-ticket/redeem",
            json={
                "ticket_id": ticket["ticket_id"],
                "token": ticket["token"],
                "job_id": "pc:SCAN-1",
                "method": "POST",
                "path": "/job/v1/jobs/pc:SCAN-1/bind-only",
                "now": _now(),
            },
        )
        self.assertEqual(ok.status_code, 200)
        self.assertTrue(ok.get_json()["ok"])
        self.assertTrue(ok.get_json()["radiated"])

    def test_bind_and_issue_is_not_printed(self):
        live = {
            "ok": True,
            "verdict": True,
            "state": "LIVE",
            "verify_url": "https://velaru.xyz/verify?r=not-printed",
        }
        job = f"pc:SCAN-BAI-{uuid.uuid4().hex[:8]}"
        with mock.patch.object(gate_app, "velaru_fuse", return_value=(live, 200, {})):
            r = self.client.post(
                "/demo/pas/policycenter/pre-bind",
                json={
                    "fuse_id": "fuse_velaru_drill",
                    "job_id": job,
                    "action": "bind-and-issue",
                },
            )
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertFalse(body["allow_bind"])
        self.assertTrue(body["halt"])
        self.assertEqual(body["reason"], "spend_write_not_in_protocol")
        self.assertNotIn("bind_ticket", body)

        spec = self.client.get("/.well-known/spend-protocol.json")
        self.assertEqual(spec.status_code, 200)
        data = spec.get_json()
        self.assertEqual(data["spec"], "gate-spend-protocol-v1")
        self.assertIn("bind-only", data["married_write"]["path"])
        self.assertTrue(data["redeem"]["fail_closed"])
        page = self.client.get("/scanner")
        self.assertEqual(page.status_code, 200)
        self.assertIn("Fingerprint or no print", page.get_data(as_text=True))

    def test_command_radiation_requires_shared_now(self):
        live = {
            "ok": True,
            "verdict": True,
            "state": "LIVE",
            "verify_url": "https://velaru.xyz/verify?r=uplink",
        }
        with mock.patch.object(gate_app, "velaru_fuse", return_value=(live, 200, {})):
            r = self.client.post(
                "/demo/pas/policycenter/pre-bind",
                json={"fuse_id": "fuse_velaru_drill", "job_id": "pc:UPLINK-1"},
            )
        self.assertEqual(r.status_code, 200)
        ticket = r.get_json()["bind_ticket"]
        stale = (datetime.now(timezone.utc) - timedelta(seconds=120)).isoformat()
        skewed = self.client.post(
            "/demo/pas/bind-ticket/redeem",
            json={
                "ticket_id": ticket["ticket_id"],
                "token": ticket["token"],
                "job_id": "pc:UPLINK-1",
                "method": "POST",
                "path": "/job/v1/jobs/pc:UPLINK-1/bind-only",
                "now": stale,
            },
        )
        self.assertEqual(skewed.status_code, 403)
        body = skewed.get_json()
        self.assertEqual(body["reason"], "command_now_invalid")
        self.assertTrue(body["radiation_abort"])

        garbage = self.client.post(
            "/demo/pas/bind-ticket/redeem",
            json={
                "ticket_id": ticket["ticket_id"],
                "token": ticket["token"],
                "job_id": "pc:UPLINK-1",
                "method": "POST",
                "path": "/job/v1/jobs/pc:UPLINK-1/bind-only",
                "now": "not-a-clock",
            },
        )
        self.assertEqual(garbage.status_code, 403)
        self.assertEqual(garbage.get_json()["reason"], "command_now_invalid")
        self.assertTrue(garbage.get_json()["radiation_abort"])

        still = self.client.post(
            "/demo/pas/bind-ticket/redeem",
            json={
                "ticket_id": ticket["ticket_id"],
                "token": ticket["token"],
                "job_id": "pc:UPLINK-1",
                "method": "POST",
                "path": "/job/v1/jobs/pc:UPLINK-1/bind-only",
                "now": _now(),
            },
        )
        self.assertEqual(still.status_code, 200)
        self.assertTrue(still.get_json()["radiated"])

        spec = self.client.get("/.well-known/command-radiation.json")
        self.assertEqual(spec.status_code, 200)
        spec_body = spec.get_json()
        self.assertEqual(spec_body["spec"], "gate-command-radiation-v1")
        self.assertTrue(spec_body["now"]["required"])
        spend = self.client.get("/.well-known/spend-protocol.json")
        self.assertIn("now", spend.get_json()["redeem"]["required"])
        page = self.client.get("/uplink")
        self.assertEqual(page.status_code, 200)
        self.assertIn("This vehicle. This now.", page.get_data(as_text=True))

    def test_epoch_lock_requires_charge_id(self):
        dead = {
            "ok": True,
            "verdict": False,
            "halt": True,
            "state": "DEAD",
            "verify_url": "https://velaru.xyz/verify?r=epoch",
        }
        live = {
            "ok": True,
            "verdict": True,
            "state": "LIVE",
            "verify_url": "https://velaru.xyz/verify?r=epoch-live",
        }
        job = f"pc:EPOCH-{uuid.uuid4().hex[:8]}"
        with mock.patch.object(gate_app, "velaru_fuse", return_value=(dead, 200, {})):
            r1 = self.client.post(
                "/demo/pas/policycenter/pre-bind",
                json={"fuse_id": "fuse_velaru_drill", "job_id": job},
            )
        self.assertEqual(r1.status_code, 200)
        self.assertFalse(r1.get_json()["allow_bind"])

        with mock.patch.object(gate_app, "velaru_fuse", return_value=(live, 200, {})):
            r2 = self.client.post(
                "/demo/pas/policycenter/pre-bind",
                json={"fuse_id": "fuse_velaru_drill", "job_id": job},
            )
        self.assertEqual(r2.status_code, 200)
        locked = r2.get_json()
        self.assertFalse(locked["allow_bind"])
        self.assertTrue(locked["commit_time_authorization"]["epoch"]["locked"])
        self.assertEqual(locked["commit_time_authorization"]["epoch"]["reason"], "prior_halt_requires_charge")

        with mock.patch.object(gate_app, "velaru_fuse", return_value=(live, 200, {})):
            r3 = self.client.post(
                "/demo/pas/policycenter/pre-bind",
                json={
                    "fuse_id": "fuse_velaru_drill",
                    "job_id": job,
                    "charge_id": f"chg_test_epoch_{uuid.uuid4().hex[:8]}",
                },
            )
        self.assertEqual(r3.status_code, 200)
        opened = r3.get_json()
        self.assertTrue(opened["allow_bind"])
        self.assertFalse(opened["commit_time_authorization"]["epoch"]["locked"])
        self.assertIn("bind_ticket", opened)

    def test_exclusion_and_consistency_proofs(self):
        import exclusion as exclusion_mod
        import evidence_log as evidence_log_mod
        import db as gate_db

        proof = exclusion_mod.prove("pc:NEVER-SPENT", spent_ids=["pc:AAA", "pc:ZZZ"])
        self.assertFalse(proof["spent"])
        self.assertEqual(proof["neighbors"]["left"]["job_id"], "pc:AAA")
        self.assertEqual(proof["neighbors"]["right"]["job_id"], "pc:ZZZ")
        self.assertTrue(exclusion_mod.verify_exclusion(proof))

        r = self.client.get("/.well-known/exclusion.json?job_id=pc:NEVER-SPENT")
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertFalse(body["spent"])
        self.assertTrue(exclusion_mod.verify_exclusion(body))

        rows = gate_db.list_bind_events_chronological()
        leaves = evidence_log_mod.log_from_rows(rows)
        old = max(0, len(leaves) - 1)
        cons = evidence_log_mod.consistency_proof(old, leaves)
        self.assertTrue(cons["valid"])
        self.assertTrue(
            evidence_log_mod.verify_consistency(
                old_size=old,
                old_root=cons["old_root"],
                new_root=cons["new_root"],
                leaf_hashes_hex=leaves,
            )
        )
        r2 = self.client.get(f"/.well-known/evidence-consistency.json?old_size={old}")
        self.assertEqual(r2.status_code, 200)
        self.assertTrue(r2.get_json()["valid"])

        r3 = self.client.get("/.well-known/commit-auth.json")
        self.assertEqual(r3.status_code, 200)
        self.assertTrue(r3.get_json()["stale_hop_cannot_spend"])

    def test_constraint_counterfactual_on_mga_block(self):
        live = {"ok": True, "verdict": True, "state": "LIVE"}
        with mock.patch.object(gate_app, "velaru_fuse", return_value=(live, 200, {})):
            r = self.client.post(
                "/demo/pas/mga-authority",
                json={
                    "fuse_id": "fuse_velaru_drill",
                    "job_id": "pc:MGA-CONSTRAINT-1",
                    "premium": 60000,
                    "authority_limit": 50000,
                },
            )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["result"], "BLOCK")
        import db as gate_db

        latest = gate_db.list_bind_events(None, limit=1)[0]
        payload = self.client.get(f"/.well-known/receipt/{latest['id']}.json").get_json()
        cf = payload["counterfactual_spend"]
        self.assertIn("CONSTRAINT", cf["types"])
        self.assertIn("premium_exceeds_authority", cf["constraint"]["reasons"])

    def test_listings_still_health(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        self.assertIn("bind_room", r.get_json())
        self.assertIn("operator", r.get_json())
        self.assertIn("scanner", r.get_json())
        self.assertIn("uplink", r.get_json())
        self.assertIn("mass", r.get_json())
        r2 = self.client.get("/.well-known/listings.json")
        self.assertEqual(r2.status_code, 200)
        self.assertIn("welds", r2.get_json())
        self.assertIn("operator_invoice", r2.get_json())
        self.assertIn("license_fuse", r2.get_json())
        self.assertIn("restraint", r2.get_json())
        fuse = self.client.get("/.well-known/license-fuse.json")
        self.assertEqual(fuse.status_code, 200)
        self.assertTrue(fuse.get_json()["children_cannot_outlive_parent"])
        self.assertNotIn("their_production", fuse.get_json())
        nos = self.client.get("/.well-known/restraint.json")
        self.assertEqual(nos.status_code, 200)
        self.assertFalse(nos.get_json()["pii"])
        self.assertFalse(nos.get_json()["demo"])


class OperatorInvoiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_formula_floor_wins_on_sleepy_desk(self):
        import operator_invoice as oi

        billed = oi.invoice(cleared_cents=120_000_000, hop_count=8_000)
        self.assertEqual(billed["billed_cents"], 500_000)
        self.assertEqual(billed["winner"], "floor")
        self.assertEqual(billed["legs_cents"]["bps"], 120_000)

    def test_formula_bps_wins_on_fat_flow(self):
        import operator_invoice as oi

        billed = oi.invoice(cleared_cents=2_000_000_000, hop_count=1_000)
        self.assertEqual(billed["billed_cents"], 2_000_000)
        self.assertEqual(billed["winner"], "bps")

    def test_formula_per_hop_wins_on_chatty_tiny_dollars(self):
        import operator_invoice as oi

        billed = oi.invoice(cleared_cents=1_000_000, hop_count=200_000)
        self.assertEqual(billed["billed_cents"], 2_000_000)
        self.assertEqual(billed["winner"], "per_hop")

    def test_fund_style_register_stacks_management_and_flow(self):
        import operator_invoice as oi

        reg = oi.register_invoice(
            cleared_cents=100_000_000_000,
            hop_count=1_000,
            welded_writes=10,
            live_parents=25,
        )
        self.assertEqual(reg["management"]["total_cents"], 175_000_00)  # 35 * $5k
        self.assertGreater(reg["flow"]["billed_cents"], 0)
        self.assertEqual(
            reg["total_cents"],
            reg["management"]["total_cents"] + reg["flow"]["billed_cents"],
        )

    def test_carry_above_hurdle(self):
        import operator_invoice as oi

        below = oi.flow_register(cleared_cents=10_000_000_000)  # $100M
        above = oi.flow_register(cleared_cents=100_000_000_000)  # $1B
        self.assertEqual(below["carry_cents"], 0)
        self.assertGreater(above["carry_cents"], 0)
        self.assertGreater(above["billed_cents"], below["billed_cents"])

    def test_manifest_is_one_write_licensed(self):
        import operator_invoice as oi

        m = oi.manifest("https://example.test", "hello@velaru.xyz")
        self.assertTrue(m["one_write_per_weld"])
        self.assertTrue(m["licensed_only"])
        self.assertTrue(m["not_a_new_engine"])
        self.assertEqual(m["skus"]["weld"]["amount_cents"], 2_500_000)
        self.assertEqual(m["skus"]["floor_per_mouth"]["amount_cents"], 500_000)
        self.assertTrue(m["not_saas"])
        self.assertIn("register_fees", m)
        self.assertIn("potential", m["register_fees"])
        self.assertIn("year", m["invoice"])
        self.assertEqual(m["invoice"]["year"][-1]["through"], "$1T")
        ids = {w["id"] for w in m["writes"]}
        self.assertEqual(ids, {"withdraw", "bind_only"})

    def test_operator_page_and_well_known(self):
        page = self.client.get("/operator")
        self.assertEqual(page.status_code, 200)
        body = page.get_data(as_text=True)
        self.assertIn("$25,000", body)
        self.assertIn("$5,000/mo", body)
        self.assertIn("management", body.lower())
        self.assertNotIn("Weld without the minimum", body)
        self.assertIn("Unlicensed", body)
        spec = self.client.get("/.well-known/operator.json")
        self.assertEqual(spec.status_code, 200)
        data = spec.get_json()
        self.assertTrue(data["licensed_only"])
        listing = self.client.get("/listings/operator.json")
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(listing.get_json()["spec"], "gate-operator-invoice-v1")

    def test_register_page_and_manifest(self):
        import register as register_mod

        page = self.client.get("/register")
        self.assertEqual(page.status_code, 200)
        body = page.get_data(as_text=True)
        self.assertIn("Fee schedule", body)
        self.assertIn("cleared flow", body.lower())
        self.assertIn("$1,000,000,000", body)
        self.assertNotIn("scarcity is the DENY", body)
        self.assertNotIn("Anthropophagy", body)
        self.assertNotIn("Cybersyn", body)
        spec = self.client.get("/.well-known/register.json")
        self.assertEqual(spec.status_code, 200)
        data = spec.get_json()
        self.assertEqual(data["spec"], "gate-register-v1")
        self.assertNotIn("their_production", data)
        self.assertIn("SaaS", data["not"])
        self.assertIn("register_fees", data)
        self.assertIn("civilization", data)
        self.assertIn("potential", data["scale"])
        m = register_mod.manifest("https://example.test", "hello@velaru.xyz")
        self.assertIn("civilization", m)
        self.assertIn("management", m["equations"])
        self.assertIn("10 bps", m["equations"]["flow"])
        self.assertEqual(m["scale"]["potential"]["mouths"]["welded_writes"], 100)

    def test_positioning_manifest_and_page(self):
        import positioning as positioning_mod

        page = self.client.get("/positioning")
        self.assertEqual(page.status_code, 200)
        body = page.get_data(as_text=True)
        self.assertIn("noindex", body)
        self.assertIn("Buyer facts", body)
        self.assertNotIn("their_production: false", body.lower())
        self.assertNotIn("Cybersyn", body)
        self.assertNotIn("Anthropophagy", body)

        spec = self.client.get("/.well-known/positioning.json")
        self.assertEqual(spec.status_code, 200)
        data = spec.get_json()
        self.assertEqual(data["spec"], "gate-positioning-v1")
        self.assertIn("ops_philosophy", data)
        self.assertIn("narrative_brand", data)
        self.assertIn("cybernetics_cybersyn", data["ops_philosophy"])
        self.assertIn("anthropophagy", data["narrative_brand"])
        self.assertNotIn("their_production", data)

        reg = self.client.get("/.well-known/register.json").get_json()
        self.assertIn("positioning", reg)

        cards = positioning_mod.page_cards()
        self.assertEqual(len(cards), 7)
        self.assertEqual(cards[0]["tag"], "Nature")

        aos = self.client.get("/.well-known/action-os.json")
        self.assertEqual(aos.status_code, 200)
        aos_data = aos.get_json()
        self.assertEqual(aos_data["spec"], "nisaba-action-os-v2")
        self.assertIn("everybody", aos_data["thesis"].lower())
        self.assertIn("DENY", aos_data["formula"])
        self.assertTrue(aos_data["category_includes_force"])
        self.assertFalse(aos_data["force_production_weld"])
        self.assertNotIn("their_production", aos_data)

        aos_page = self.client.get("/action-os")
        self.assertEqual(aos_page.status_code, 200)
        aos_body = aos_page.get_data(as_text=True)
        self.assertIn("Clearance before irreversible write", aos_body)
        self.assertIn("Weld a path", aos_body)
        self.assertIn("noindex", aos_body)

        gate = self.client.get("/.well-known/gate.json").get_json()
        self.assertIn("action_os", gate)
        self.assertIn("formula", gate)

        home = self.client.get("/").get_data(as_text=True)
        self.assertNotIn("/action-os", home)
        self.assertNotIn(">Action OS</a>", home)
        self.assertNotIn("scarcity is the DENY", home)
        self.assertIn("Your CGL will not cover the agent", home)
        self.assertNotIn("/science", home)
        self.assertIn("/trust", home)
        self.assertIn("Fail closed", home)
        self.assertNotIn("their_production: false", home.lower())

        import db as gate_db

        with gate_db.db() as conn:
            gate_db._ensure_dogfood_table(conn)
            gate_db._ensure_third_party_welds(conn)
            conn.execute("DELETE FROM dogfood_welds")
            conn.execute("DELETE FROM third_party_welds")

        sc = self.client.get("/.well-known/scorecard.json")
        self.assertEqual(sc.status_code, 200)
        sc_data = sc.get_json()
        self.assertEqual(sc_data["spec"], "nisaba-scorecard-v2")
        self.assertNotIn("their_production", sc_data)
        self.assertEqual(sc_data["mode"], "pre_rev_maxed")
        self.assertIn("family", sc_data)
        self.assertEqual(len(sc_data["family"]), 5)
        self.assertIn("DENY", sc_data["formula"])
        # L2 proof-green deploy without their_production / dogfood
        self.assertGreaterEqual(sc_data["dimensions"]["deployability"], 7.0)
        self.assertLess(sc_data["dimensions"]["deployability"], 8.0)
        self.assertIn("proof_readiness", sc_data)
        self.assertEqual(sc_data["proof_readiness"]["level"], 2)
        # Non-Gate siblings fully maxed at pre-rev ceiling
        for p in sc_data["family"]:
            self.assertTrue(p["market_problem"])
            self.assertTrue(p["buyer"])
            self.assertIn("market_bite", p["dimensions"])
            if p["id"] != "gate":
                self.assertTrue(p["maxed"], p["id"])
                self.assertGreaterEqual(p["dimensions"]["voice"], 9.0)
                self.assertGreaterEqual(p["dimensions"]["public_face"], 9.0)
                self.assertGreaterEqual(p["dimensions"]["copy_pitch"], 9.0)
                self.assertGreaterEqual(p["dimensions"]["economics_model"], 9.0)
                self.assertGreaterEqual(p["dimensions"]["deployability"], 9.0)
            else:
                self.assertGreaterEqual(p["dimensions"]["deployability"], 7.0)
                self.assertLess(p["dimensions"]["deployability"], 8.0)
                self.assertTrue(p.get("proof_maxed"))
                self.assertFalse(p["maxed"])
                self.assertGreaterEqual(p["dimensions"]["voice"], 9.0)
                self.assertGreaterEqual(p["dimensions"]["market_bite"], 9.0)

        fam = self.client.get("/.well-known/family.json")
        self.assertEqual(fam.status_code, 200)
        fam_data = fam.get_json()
        self.assertEqual(fam_data["spec"], "nisaba-family-voices-v1")
        self.assertEqual(len(fam_data["family"]), 5)
        erra = self.client.get("/.well-known/family/erra.json").get_json()
        self.assertIn("EIOPA", erra["market_problem"])
        self.assertTrue(erra["citations"])
        verra = self.client.get("/.well-known/family/verra.json").get_json()
        self.assertIn("bind-only", verra["market_problem"])
        mish = self.client.get("/.well-known/family/mishara.json").get_json()
        self.assertIn("FCRA", mish["market_problem"])
        paste = self.client.get("/family/erra/paste.txt")
        self.assertEqual(paste.status_code, 200)
        self.assertIn("Should we act?", paste.get_data(as_text=True))
        self.assertEqual(self.client.get("/family").status_code, 200)
        self.assertEqual(self.client.get("/family/verra").status_code, 200)

        skin = self.client.get("/.well-known/production-skin.json")
        self.assertEqual(skin.status_code, 200)
        skin_data = skin.get_json()
        self.assertNotIn("their_production", skin_data)
        self.assertEqual(skin_data["spec"], "gate-production-skin-v2")
        self.assertIn("checklist", skin_data)
        self.assertIn("dogfood_weld", skin_data)

        proof = self.client.get("/.well-known/proof-suite.json")
        self.assertEqual(proof.status_code, 200)
        proof_data = proof.get_json()
        self.assertTrue(proof_data["all_pass"])
        self.assertGreaterEqual(proof_data["pass_count"], 5)
        self.assertEqual(proof_data["spec"], "gate-proof-suite-v2")
        self.assertEqual(proof_data["readiness"]["level"], 2)

        for path in ("/scorecard", "/production-skin", "/proof", "/runbook", "/dogfood", "/production-weld", "/science"):
            self.assertEqual(self.client.get(path).status_code, 200, path)

        rb = self.client.get("/.well-known/runbook.json")
        self.assertEqual(rb.status_code, 200)
        self.assertEqual(rb.get_json()["spec"], "gate-runbook-v1")

        sci = self.client.get("/.well-known/science-pri.json")
        self.assertEqual(sci.status_code, 200)
        sci_data = sci.get_json()
        self.assertEqual(sci_data["spec"], "nisaba-science-pri-v1")
        self.assertFalse(sci_data["own_tier_s"])
        self.assertFalse(sci_data["force_production_weld"])
        self.assertIn("Contribute massively", sci_data["motive"])
        self.assertGreaterEqual(len(sci_data["science"]), 4)
        self.assertGreaterEqual(len(sci_data["tech"]), 5)
        self.assertEqual(sci_data["first_weld"]["write"], "withdraw")
        self.assertIn("can and may", sci_data["tech_thesis"])
        tech_ids = {t["id"] for t in sci_data["tech"]}
        self.assertTrue(
            {"agent_control", "grid_forming", "leo_mesh", "tee_mpc_hsm", "pd_kinetic"}.issubset(tech_ids)
        )
        self.assertIn("science_pri", self.client.get("/.well-known/gate.json").get_json())

        legal = self.client.get("/.well-known/legal.json")
        self.assertEqual(legal.status_code, 200)
        legal_data = legal.get_json()
        self.assertEqual(legal_data["spec"], "gate-legal-stubs-v1")
        self.assertTrue(legal_data["ads_floor"]["pixels"]["default_off"])
        self.assertIn("/privacy", legal_data["privacy"]["url"])
        self.assertIn("/terms", legal_data["terms"]["url"])
        privacy_html = self.client.get("/privacy").get_data(as_text=True)
        self.assertIn("What we collect", privacy_html)
        terms_html = self.client.get("/terms").get_data(as_text=True)
        self.assertNotIn("their_production: false", terms_html.lower())
        op_html = self.client.get("/operator").get_data(as_text=True)
        self.assertNotIn("their_production: false", op_html.lower())
        self.assertIn("First weld", op_html)
        self.assertIn("href=\"/privacy\"", op_html)
        self.assertIn("href=\"/terms\"", op_html)
        op_json = self.client.get("/.well-known/operator.json").get_json()
        self.assertEqual(op_json["first_weld"]["write"], "withdraw")
        self.assertNotIn("their_production", op_json.get("ads_floor") or {})

        # Dogfood lifts to L3 without flipping their_production
        dog = self.client.post(
            "/dogfood",
            data={
                "write_path": "/v1/act → withdraw dogfood",
                "operator": "proof@nisaba.io",
                "note": "test dogfood",
            },
            follow_redirects=True,
        )
        self.assertEqual(dog.status_code, 200)
        proof2 = self.client.get("/.well-known/proof-suite.json").get_json()
        self.assertEqual(proof2["readiness"]["level"], 3)
        self.assertTrue(proof2["readiness"]["dogfood_weld"])
        self.assertNotIn("their_production", proof2)
        sc2 = self.client.get("/.well-known/scorecard.json").get_json()
        self.assertAlmostEqual(sc2["dimensions"]["deployability"], 8.5, places=1)
        self.assertNotIn("their_production", sc2)

        # Production weld without confirm must not flip
        refuse = self.client.post(
            "/production-weld",
            data={
                "write_path": "POST /job/v1/jobs/x/bind-only",
                "counterparty": "ops@carrier.example",
                "note": "their customer bind write",
                "exclusive_door_url": "https://carrier.example/gate-worker",
                "door_kind": "cloudflare_worker",
                "exclusivity_confirm": "1",
            },
            follow_redirects=True,
        )
        self.assertEqual(refuse.status_code, 200)
        self.assertNotIn("their_production", self.client.get("/.well-known/production-skin.json").get_json())

        # Confirmed third-party weld without exclusivity door must not flip
        no_door = self.client.post(
            "/production-weld",
            data={
                "write_path": "POST /job/v1/jobs/x/bind-only",
                "counterparty": "ops@carrier.example",
                "note": "their customer bind write cleared",
                "confirm": "1",
                "exclusivity_confirm": "1",
            },
            follow_redirects=True,
        )
        self.assertEqual(no_door.status_code, 200)
        self.assertNotIn("their_production", self.client.get("/.well-known/production-skin.json").get_json())

        # Confirmed third-party weld + exclusivity → L4
        prod = self.client.post(
            "/production-weld",
            data={
                "write_path": "POST /job/v1/jobs/x/bind-only",
                "counterparty": "ops@carrier.example",
                "note": "their customer bind write cleared",
                "confirm": "1",
                "exclusivity_confirm": "1",
                "exclusive_door_url": "https://carrier.example/gate-worker",
                "door_kind": "cloudflare_worker",
                "worker_fingerprint": "wrangler-deploy-test",
            },
            follow_redirects=True,
        )
        self.assertEqual(prod.status_code, 200)
        proof3 = self.client.get("/.well-known/proof-suite.json").get_json()
        self.assertEqual(proof3["readiness"]["level"], 4)
        self.assertTrue(proof3["their_production"])
        sc3 = self.client.get("/.well-known/scorecard.json").get_json()
        self.assertAlmostEqual(sc3["dimensions"]["deployability"], 9.0, places=1)
        self.assertTrue(sc3["their_production"])

        gate = self.client.get("/.well-known/gate.json").get_json()
        self.assertIn("scorecard", gate)
        self.assertIn("production_skin", gate)
        self.assertIn("proof_suite", gate)
        self.assertIn("runbook", gate)
        self.assertIn("production_weld", gate)

    def test_homepage_leads_register_not_saas(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        body = r.get_data(as_text=True)
        self.assertIn("Bind Room", body)
        self.assertIn("/bind-room", body)
        self.assertIn("/trust", body)
        self.assertIn("/operator", body)
        self.assertNotIn("scarcity is the DENY", body)
        self.assertNotIn("Weld a door", body)
        self.assertNotIn("Own the DENY", body)
        self.assertNotIn("their_production: false", body.lower())

    def test_no_momo_and_archive_buried(self):
        import db as gate_db

        with gate_db.db() as conn:
            gate_db._ensure_dogfood_table(conn)
            gate_db._ensure_third_party_welds(conn)
            conn.execute("DELETE FROM dogfood_welds")
            conn.execute("DELETE FROM third_party_welds")

        op = self.client.get("/operator").get_data(as_text=True)
        self.assertNotIn("/mo/mo", op)
        self.assertNotIn("their_production: false", op.lower())
        for path in ("/this", "/bound", "/positioning", "/scanner", "/science", "/dogfood"):
            r = self.client.get(path)
            self.assertEqual(r.status_code, 200, path)
            blob = r.headers.get("X-Robots-Tag", "") + r.get_data(as_text=True)
            self.assertIn("noindex", blob, path)
        robots = self.client.get("/robots.txt").get_data(as_text=True)
        self.assertIn("Disallow: /this", robots)
        self.assertIn("Disallow: /production-weld", robots)
        import app as gate_app

        prev, prev_tok = gate_app.GATE_DEV_MODE, gate_app.OPS_TOKEN
        try:
            gate_app.GATE_DEV_MODE = False
            gate_app.OPS_TOKEN = "secret-ops"
            refuse = self.client.post(
                "/production-weld",
                data={
                    "write_path": "POST /v1/payouts/x/release",
                    "counterparty": "ops@carrier.example",
                    "note": "their customer payout",
                    "confirm": "1",
                },
                follow_redirects=True,
            )
            self.assertEqual(refuse.status_code, 200)
            self.assertIn("Ops token required", refuse.get_data(as_text=True))
            self.assertNotIn(
                "their_production",
                self.client.get("/.well-known/production-skin.json").get_json(),
            )
        finally:
            gate_app.GATE_DEV_MODE = prev
            gate_app.OPS_TOKEN = prev_tok

    def test_zero_saas_stench_on_money_surfaces(self):
        """Public money face must not smell like Free/Pro seat SaaS or API basement."""
        banned = (
            "Get API key",
            "Get free API",
            "free API key",
            "no API key",
            "Sign up → Pro",
            "Upgrade to Pro",
            "Cancel anytime",
            "Free tier",
            "1,000 hops / month",
            "1,000,000 hops",
            "Lab docs",
            "Lab login",
            "Lab account",
            "Open lab account",
            "Weld a door",
            "Mouth economics",
            "scarcity is the DENY",
            "Own the DENY",
            "DEAD kills",
            "Anthropophagy",
            "Cybersyn",
        )
        for path in ("/", "/pricing", "/operator", "/register", "/trust"):
            body = self.client.get(path).get_data(as_text=True)
            for phrase in banned:
                self.assertNotIn(phrase, body, f"{path} still has banned phrase: {phrase}")
        home = self.client.get("/").get_data(as_text=True)
        self.assertIn("Your CGL will not cover the agent", home)
        self.assertIn("Bind Room", home)
        self.assertIn("Operator path", home)
        chrome = home.split("<footer>", 1)[0]
        for phrase in (
            "Lab docs",
            "Lab login",
            "Lab account",
            "Get API key",
            "no API key",
            "free API key",
            "Action OS",
        ):
            self.assertNotIn(phrase, chrome, f"chrome still shows {phrase}")
        # Lean chrome: doctrine links are footer-only
        self.assertNotIn(">Family</a>", chrome)
        self.assertNotIn(">Stack</a>", chrome)
        self.assertNotIn(">Status</a>", chrome)
        self.assertIn(">Bind Room</a>", chrome)
        pricing = self.client.get("/pricing").get_data(as_text=True)
        self.assertIn("Weld", pricing)
        self.assertIn("bps", pricing.lower())
        self.assertNotIn(">Free</h3>", pricing)
        self.assertNotIn(">Pro</h3>", pricing)
        self.assertNotIn("Open lab account", pricing)
        self.assertNotIn("Lab hop docs", pricing)
        self.assertNotIn("Get API key", home)
        opp = self.client.get("/.well-known/opportunities.json")
        if opp.status_code == 200:
            self.assertTrue(opp.get_json().get("not_saas"))
        import audiences as audiences_mod

        for plate in audiences_mod.plate_list():
            blob = " ".join(
                str(plate.get(k, ""))
                for k in ("offer", "price", "cta_label", "subhead", "headline")
            )
            self.assertNotRegex(blob, r"(?i)get (free )?api key")
            self.assertNotRegex(blob, r"(?i)free tier")
            self.assertNotRegex(blob, r"(?i)\$99\s*/\s*mo")
            self.assertNotIn("scarcity is the DENY", blob)
            self.assertNotIn("Own the DENY", blob)
            self.assertNotIn("Weld a door", blob)

    def test_dev_checkout_weld_does_not_eat_install_slots(self):
        import db as gate_db

        before = gate_db.install_slots_remaining()
        r = self.client.post(
            "/operator/checkout",
            data={"email": "ops@example.test", "write": "withdraw", "include_floor": "1"},
            follow_redirects=False,
        )
        self.assertEqual(r.status_code, 302)
        self.assertIn("/install/success", r.headers.get("Location", ""))
        self.assertEqual(gate_db.install_slots_remaining(), before)

    def test_dev_operator_checkout_is_idempotent(self):
        idem = "idem-ops-weld-1"
        r1 = self.client.post(
            "/operator/checkout",
            data={
                "email": "ops@example.test",
                "write": "withdraw",
                "include_floor": "1",
                "idempotency_key": idem,
            },
            follow_redirects=False,
        )
        self.assertEqual(r1.status_code, 302)
        loc1 = r1.headers.get("Location", "")
        self.assertIn("/install/success", loc1)

        r2 = self.client.post(
            "/operator/checkout",
            data={
                "email": "ops@example.test",
                "write": "withdraw",
                "include_floor": "1",
                "idempotency_key": idem,
            },
            follow_redirects=False,
        )
        self.assertEqual(r2.status_code, 302)
        loc2 = r2.headers.get("Location", "")

        # Must be the exact same booking outcome.
        self.assertEqual(loc1, loc2)

    def test_checkout_rejects_unknown_write(self):
        r = self.client.post(
            "/operator/checkout",
            data={"email": "ops@example.test", "write": "memecoin", "include_floor": "0"},
            follow_redirects=False,
        )
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r.headers.get("Location", "").endswith("/operator"))


class LicenseFuseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def _live(self, tag):
        return {
            "ok": True,
            "verdict": True,
            "state": "LIVE",
            "verify_url": f"https://velaru.xyz/verify?r={tag}",
        }

    def test_unsigned_parent_prints_no_ticket(self):
        lid = f"lic:CO-UNSIGNED-{uuid.uuid4().hex[:8]}"
        job = f"pc:FUSE-UNSIGNED-{uuid.uuid4().hex[:8]}"
        with mock.patch.object(gate_app, "velaru_fuse", return_value=(self._live("unsigned"), 200, {})):
            r = self.client.post(
                "/demo/pas/policycenter/pre-bind",
                json={
                    "fuse_id": "fuse_velaru_drill",
                    "job_id": job,
                    "license_id": lid,
                },
            )
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertFalse(body["allow_bind"])
        self.assertTrue(body["halt"])
        self.assertEqual(body["reason"], "license_parent_not_live")
        self.assertNotIn("bind_ticket", body)
        self.assertEqual(body["license_fuse"]["stored"], "UNSIGNED")

    def test_charge_only_live_then_children_die_with_parent(self):
        lid = f"lic:CO-PARENT-{uuid.uuid4().hex[:8]}"
        job = f"pc:FUSE-PARENT-{uuid.uuid4().hex[:8]}"
        missing = self.client.post(f"/demo/pas/licenses/{lid}/charge", json={})
        self.assertEqual(missing.status_code, 403)
        self.assertEqual(missing.get_json()["reason"], "charge_id_required")

        charged = self.client.post(
            f"/demo/pas/licenses/{lid}/charge",
            json={"charge_id": f"chg_parent_{uuid.uuid4().hex[:8]}"},
        )
        self.assertEqual(charged.status_code, 200)
        self.assertEqual(charged.get_json()["state"], "LIVE")

        with mock.patch.object(gate_app, "velaru_fuse", return_value=(self._live("parent"), 200, {})):
            r = self.client.post(
                "/demo/pas/policycenter/pre-bind",
                json={
                    "fuse_id": "fuse_velaru_drill",
                    "job_id": job,
                    "license_id": lid,
                },
            )
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertTrue(body["allow_bind"])
        ticket = body["bind_ticket"]
        self.assertEqual(ticket["license_id"], lid)
        self.assertTrue(ticket["children_cannot_outlive_parent"])
        armed = self.client.get(f"/demo/pas/licenses/{lid}")
        self.assertEqual(armed.status_code, 200)
        self.assertEqual(armed.get_json()["state"], "ARMED")

        blown = self.client.post(f"/demo/pas/licenses/{lid}/dead", json={})
        self.assertEqual(blown.status_code, 200)
        self.assertEqual(blown.get_json()["state"], "DEAD")

        dead_redeem = self.client.post(
            "/demo/pas/bind-ticket/redeem",
            json={
                "ticket_id": ticket["ticket_id"],
                "token": ticket["token"],
                "job_id": job,
                "method": "POST",
                "path": f"/job/v1/jobs/{job}/bind-only",
                "license_id": lid,
                "now": _now(),
            },
        )
        self.assertEqual(dead_redeem.status_code, 403)
        dead_body = dead_redeem.get_json()
        self.assertEqual(dead_body["reason"], "license_parent_not_live")
        self.assertTrue(dead_body["radiation_abort"])

        resurrected = self.client.post(
            f"/demo/pas/licenses/{lid}/charge",
            json={"charge_id": f"chg_parent_{uuid.uuid4().hex[:8]}"},
        )
        self.assertEqual(resurrected.status_code, 200)
        self.assertEqual(resurrected.get_json()["state"], "LIVE")

        ok = self.client.post(
            "/demo/pas/bind-ticket/redeem",
            json={
                "ticket_id": ticket["ticket_id"],
                "token": ticket["token"],
                "job_id": job,
                "method": "POST",
                "path": f"/job/v1/jobs/{job}/bind-only",
                "license_id": lid,
                "now": _now(),
            },
        )
        self.assertEqual(ok.status_code, 200)
        self.assertTrue(ok.get_json()["ok"])

    def test_counterpart_fingerprint_is_optional_and_fail_closed(self):
        job_partial = f"pc:FUSE-CP-PARTIAL-{uuid.uuid4().hex[:8]}"
        job_ok = f"pc:FUSE-CP-OK-{uuid.uuid4().hex[:8]}"
        with mock.patch.object(gate_app, "velaru_fuse", return_value=(self._live("cp-partial"), 200, {})):
            partial = self.client.post(
                "/demo/pas/policycenter/pre-bind",
                json={
                    "fuse_id": "fuse_velaru_drill",
                    "job_id": job_partial,
                    "counterpart_kind": "payout_rail",
                },
            )
        self.assertEqual(partial.status_code, 200)
        self.assertTrue(partial.get_json()["halt"])
        self.assertEqual(partial.get_json()["reason"], "counterpart_id_required")
        self.assertNotIn("bind_ticket", partial.get_json())

        with mock.patch.object(gate_app, "velaru_fuse", return_value=(self._live("cp"), 200, {})):
            r = self.client.post(
                "/demo/pas/policycenter/pre-bind",
                json={
                    "fuse_id": "fuse_velaru_drill",
                    "job_id": job_ok,
                    "counterpart_id": "rail:ACH-9",
                    "counterpart_kind": "payout_rail",
                },
            )
        self.assertEqual(r.status_code, 200)
        ticket = r.get_json()["bind_ticket"]
        self.assertTrue(ticket["counterpart_fingerprint"])
        self.assertEqual(ticket["counterpart"]["counterpart_id"], "rail:ACH-9")

        missing = self.client.post(
            "/demo/pas/bind-ticket/redeem",
            json={
                "ticket_id": ticket["ticket_id"],
                "token": ticket["token"],
                "job_id": job_ok,
                "method": "POST",
                "path": f"/job/v1/jobs/{job_ok}/bind-only",
                "now": _now(),
            },
        )
        self.assertEqual(missing.status_code, 403)
        self.assertEqual(missing.get_json()["reason"], "counterpart_mismatch")

        wrong = self.client.post(
            "/demo/pas/bind-ticket/redeem",
            json={
                "ticket_id": ticket["ticket_id"],
                "token": ticket["token"],
                "job_id": job_ok,
                "method": "POST",
                "path": f"/job/v1/jobs/{job_ok}/bind-only",
                "counterpart_id": "rail:WIRE-0",
                "counterpart_kind": "payout_rail",
                "now": _now(),
            },
        )
        self.assertEqual(wrong.status_code, 403)
        self.assertEqual(wrong.get_json()["reason"], "counterpart_mismatch")

        ok = self.client.post(
            "/demo/pas/bind-ticket/redeem",
            json={
                "ticket_id": ticket["ticket_id"],
                "token": ticket["token"],
                "job_id": job_ok,
                "method": "POST",
                "path": f"/job/v1/jobs/{job_ok}/bind-only",
                "counterpart_id": "rail:ACH-9",
                "counterpart_kind": "payout_rail",
                "now": _now(),
            },
        )
        self.assertEqual(ok.status_code, 200)
        self.assertTrue(ok.get_json()["ok"])

    def test_restraint_inventory_is_production_nos_without_pii(self):
        import db as gate_db
        import uuid

        email = f"restraint-{uuid.uuid4().hex[:8]}@example.test"
        aid = gate_db.create_account(email, "hash")
        demo_id = gate_db.record_bind_event(
            fuse_id="fuse_velaru_drill",
            decision="HALT",
            job_id="pc:DEMO-NO-SECRET",
            account_id=None,
            acted=False,
            hop={"reason": "prior_halt_requires_charge"},
        )
        allow_id = gate_db.record_bind_event(
            fuse_id="fuse_velaru_drill",
            decision="ALLOW",
            job_id="pc:PROD-YES",
            account_id=aid,
            acted=True,
            hop={"reason": "should_not_list"},
        )
        prod_id = gate_db.record_bind_event(
            fuse_id="fuse_velaru_drill",
            decision="HALT",
            job_id="pc:PROD-NO-SECRET",
            account_id=aid,
            acted=False,
            hop={
                "reason": "license_parent_not_live",
                "ssn": "000-00-0000",
                "named_insured": "nope",
            },
        )
        r = self.client.get("/.well-known/restraint.json")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data["spec"], "gate-restraint-v1")
        self.assertFalse(data["pii"])
        self.assertFalse(data["demo"])
        self.assertNotIn("their_production", data)
        ids = {e["event_id"] for e in data["events"]}
        self.assertIn(prod_id, ids)
        self.assertNotIn(demo_id, ids)
        self.assertNotIn(allow_id, ids)
        blob = json.dumps(data)
        self.assertNotIn("000-00-0000", blob)
        self.assertNotIn("pc:PROD-NO-SECRET", blob)
        self.assertNotIn("named_insured", blob)
        self.assertNotIn("pc:DEMO-NO-SECRET", blob)
        hit = next(e for e in data["events"] if e["event_id"] == prod_id)
        self.assertEqual(hit["decision"], "HALT")
        self.assertEqual(hit["reason"], "license_parent_not_live")
        self.assertNotIn("job_id", hit)
        self.assertNotIn("hop", hit)

    def test_license_number_on_redeem_is_still_pii(self):
        r = self.client.post(
            "/demo/pas/bind-ticket/redeem",
            json={
                "ticket_id": "x",
                "token": "y",
                "job_id": "pc:PII",
                "license_number": "AB-123",
                "now": _now(),
            },
        )
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.get_json()["error"]["code"], "no_pii")


class SettlementEngineTests(unittest.TestCase):
    """DTCC-shaped settlement: netting, windows, waterfall, margin, reporting."""

    @classmethod
    def setUpClass(cls):
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_netting_collapses_gross_to_net(self):
        import settlement as s

        obligations = [
            s.Obligation(member_id="A", counterparty_id="B", gross_cents=1_000_000, direction="pay", asset_class="withdraw"),
            s.Obligation(member_id="A", counterparty_id="C", gross_cents=500_000, direction="receive", asset_class="withdraw"),
            s.Obligation(member_id="B", counterparty_id="A", gross_cents=700_000, direction="pay", asset_class="withdraw"),
            s.Obligation(member_id="B", counterparty_id="C", gross_cents=300_000, direction="receive", asset_class="withdraw"),
        ]
        positions = s.compute_net_positions(obligations)
        self.assertGreater(len(positions), 0)
        a_pos = next(p for p in positions if p.member_id == "A")
        self.assertEqual(a_pos.gross_pay_cents, 1_000_000)
        self.assertEqual(a_pos.gross_receive_cents, 500_000)
        self.assertEqual(a_pos.net_cents, 500_000)

        ratio = s.netting_ratio(positions)
        self.assertEqual(ratio["spec"], "gate-netting-v1")
        self.assertGreater(ratio["reduction_ratio"], 0)
        self.assertLessEqual(ratio["reduction_ratio"], 1.0)

    def test_settlement_window_lifecycle(self):
        import settlement as s

        window = s.open_window()
        self.assertEqual(window.state, "OPEN")
        self.assertIsNotNone(window.cutoff_at)

        window.obligations = [
            asdict(s.Obligation(member_id="X", counterparty_id="Y", gross_cents=100_000, direction="pay")),
            asdict(s.Obligation(member_id="Y", counterparty_id="X", gross_cents=80_000, direction="pay")),
        ]
        closed = s.close_window(window)
        self.assertIn(closed.state, ("SETTLED", "DEFAULTED"))
        self.assertIsNotNone(closed.finality_hash)
        self.assertGreater(len(closed.net_positions), 0)

    def test_default_waterfall_layers(self):
        import settlement as s

        steps = s.run_waterfall(
            loss_cents=20_000_000_00,
            defaulter_margin_cents=2_000_000_00,
            mutualized_fund_cents=10_000_000_00,
            gate_capital_cents=5_000_000_00,
        )
        self.assertEqual(steps[0].source, "defaulter_margin")
        self.assertEqual(steps[0].consumed_cents, 2_000_000_00)
        self.assertEqual(steps[1].source, "mutualized_fund")
        self.assertGreater(steps[1].consumed_cents, 0)
        self.assertEqual(steps[2].source, "gate_capital")
        total_consumed = sum(st.consumed_cents for st in steps if st.source != "loss_allocation_to_surviving_members")
        self.assertEqual(total_consumed, 17_000_000_00)
        self.assertEqual(steps[-1].remaining_loss_cents, 3_000_000_00)

    def test_default_waterfall_pro_rata_allocation_consumes_remaining(self):
        import settlement as s

        # Supply surviving net exposures so the engine must allocate the remaining loss.
        surviving = {
            "M-A": 2_000_000_00,
            "M-B": 1_000_000_00,
        }
        steps = s.run_waterfall(
            loss_cents=20_000_000_00,
            defaulter_margin_cents=2_000_000_00,
            mutualized_fund_cents=10_000_000_00,
            gate_capital_cents=5_000_000_00,
            surviving_net_exposures_cents=surviving,
        )

        self.assertEqual(steps[0].source, "defaulter_margin")
        self.assertEqual(steps[1].source, "mutualized_fund")
        self.assertEqual(steps[2].source, "gate_capital")
        self.assertEqual(steps[-1].source, "loss_allocation_to_surviving_members")
        self.assertEqual(steps[-1].remaining_loss_cents, 0)
        self.assertIsInstance(steps[-1].allocations, dict)
        allocated = sum((steps[-1].allocations or {}).values())
        self.assertEqual(allocated, 3_000_000_00)

    def test_margin_adequacy(self):
        import settlement as s

        obs = [s.Obligation(member_id="M1", gross_cents=10_000_000)]
        adequate = s.compute_margin(ob_list=obs, member_id="M1", posted_cents=600_000)
        self.assertTrue(adequate.adequate)

        inadequate = s.compute_margin(ob_list=obs, member_id="M1", posted_cents=100_000)
        self.assertFalse(inadequate.adequate)

    def test_multi_asset_class_netting(self):
        import settlement as s

        obligations = [
            s.Obligation(member_id="A", gross_cents=500_000, direction="pay", asset_class="withdraw"),
            s.Obligation(member_id="A", gross_cents=300_000, direction="pay", asset_class="bind_only"),
            s.Obligation(member_id="A", gross_cents=200_000, direction="receive", asset_class="withdraw"),
        ]
        positions = s.compute_net_positions(obligations)
        withdraw_pos = next(p for p in positions if p.asset_class == "withdraw")
        bind_pos = next(p for p in positions if p.asset_class == "bind_only")
        self.assertEqual(withdraw_pos.net_cents, 300_000)
        self.assertEqual(bind_pos.net_cents, 300_000)

    def test_regulatory_report_structure(self):
        import settlement as s

        window = s.open_window()
        window.obligations = [
            asdict(s.Obligation(member_id="R1", gross_cents=1_000_000, direction="pay", asset_class="withdraw")),
            asdict(s.Obligation(member_id="R1", gross_cents=500_000, direction="pay", asset_class="payout")),
        ]
        s.close_window(window)
        report = s.regulatory_report(window)
        self.assertEqual(report["spec"], "gate-regulatory-report-v1")
        self.assertEqual(report["obligation_count"], 2)
        self.assertIn("withdraw", report["gross_by_asset_class_cents"])
        self.assertIn("payout", report["gross_by_asset_class_cents"])
        self.assertIsNotNone(report["finality_hash"])
        self.assertFalse(report["their_production"])

    def test_settlement_well_known_endpoint(self):
        r = self.client.get("/.well-known/settlement.json")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data["spec"], "gate-settlement-v1")
        self.assertIn("netting", data["components"])
        self.assertIn("default_waterfall", data["components"])
        self.assertIn("member_registry", data["components"])
        self.assertIn("cutoff_schedule", data["components"])
        self.assertIn("margin", data["components"])
        self.assertIn("settlement_windows", data["components"])
        self.assertIn("asset_classes", data["components"])
        self.assertIn("regulatory_reporting", data["components"])
        self.assertTrue(data["fail_closed"])

    def test_settlement_members_endpoint(self):
        r = self.client.get("/.well-known/settlement-members.json")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data["spec"], "gate-settlement-members-v1")
        self.assertIn("members", data)
        self.assertIsInstance(data["members"], list)
        # Seeded in db.init_db() so this should exist in a fresh test DB.
        member_ids = {m.get("member_id") for m in data["members"] if isinstance(m, dict)}
        self.assertIn("gate", member_ids)

    def test_settlement_windows_endpoint(self):
        r = self.client.get("/.well-known/settlement-windows.json")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data["spec"], "gate-settlement-windows-v1")
        self.assertIn("windows", data)
        self.assertIsInstance(data["windows"], list)

    def test_finality_hash_deterministic(self):
        import settlement as s

        window = s.open_window()
        window.obligations = [
            asdict(s.Obligation(member_id="D", gross_cents=50_000, direction="pay")),
        ]
        s.close_window(window)
        hash1 = window.finality_hash
        hash2 = s._finality_hash(window)
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)

    def test_kappa_register_conservation(self):
        import kappa as kappa_mod

        events = [
            {"decision": "HALT", "acted": False, "created_at": datetime.now(timezone.utc).isoformat()},
            {"decision": "HALT", "acted": False, "created_at": datetime.now(timezone.utc).isoformat()},
            {"decision": "ALLOW", "acted": True, "created_at": datetime.now(timezone.utc).isoformat()},
        ]
        reg = kappa_mod.register_from_events(events, public_url="https://gate.test")
        self.assertEqual(reg["spec"], "gate-kappa-register-v1")
        self.assertTrue(reg["conserved"])
        self.assertEqual(reg["mass"]["M_cf"], 2)
        self.assertEqual(reg["mass"]["M_live"], 1)
        self.assertEqual(reg["mass"]["M_total"], 3)
        self.assertAlmostEqual(reg["kappa"], 2 / 3, places=5)
        self.assertIsNotNone(reg["velocity"]["V_hops_per_day"])
        self.assertIsNotNone(reg["tension"]["tau"])

    def test_schism_at_cutoff(self):
        import kappa as kappa_mod
        import settlement as s

        w1 = s.open_window()
        w2 = s.open_window()
        cutoff = datetime.fromisoformat(w1.cutoff_at.replace("Z", "+00:00"))
        opened = datetime.fromisoformat(w1.opened_at.replace("Z", "+00:00"))
        late = s.Obligation(
            member_id="M1",
            gross_cents=100_00,
            created_at=(cutoff + timedelta(seconds=30)).isoformat(),
        )
        routed, schism = s.route_obligation_with_schism(
            obligation=late,
            current_window=w1,
            next_window=w2,
        )
        self.assertIsNotNone(schism)
        self.assertEqual(schism["spec"], "gate-schism-v1")
        self.assertEqual(schism["timeline_a"]["window_id"], w1.id)
        self.assertEqual(schism["timeline_b"]["window_id"], w2.id)
        self.assertEqual(routed.id, w2.id)
        self.assertEqual(len(w2.obligations), 1)

        on_time = s.Obligation(
            member_id="M2",
            gross_cents=50_00,
            created_at=(opened + timedelta(minutes=1)).isoformat(),
        )
        routed2, schism2 = s.route_obligation_with_schism(
            obligation=on_time,
            current_window=w1,
            next_window=w2,
        )
        self.assertIsNone(schism2)
        self.assertEqual(routed2.id, w1.id)
        self.assertEqual(len(w1.obligations), 1)

        none = kappa_mod.schism_at_cutoff(
            obligation_id="x",
            obligation_at=w1.opened_at,
            cutoff_at=w1.cutoff_at or "",
            would_window_id=w1.id,
            actual_window_id=w2.id,
        )
        self.assertIsNone(none)

    def test_kappa_well_known_endpoints(self):
        import db as gate_db
        import uuid

        email = f"kappa-{uuid.uuid4().hex[:8]}@example.test"
        aid = gate_db.create_account(email, "hash")
        gate_db.record_bind_event(
            fuse_id="fuse_velaru_drill",
            decision="HALT",
            job_id="pc:KAPPA-CF",
            account_id=aid,
            acted=False,
        )
        gate_db.record_bind_event(
            fuse_id="fuse_velaru_drill",
            decision="ALLOW",
            job_id="pc:KAPPA-LIVE",
            account_id=aid,
            acted=True,
        )

        r = self.client.get("/.well-known/kappa.json")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data["spec"], "gate-kappa-register-v1")
        self.assertTrue(data["conserved"])
        self.assertGreaterEqual(data["mass"]["M_total"], 2)

        r2 = self.client.get("/.well-known/schism.json")
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.get_json()["spec"], "gate-schism-v1")

        gate = self.client.get("/.well-known/gate.json")
        self.assertIn("kappa_register", gate.get_json())


class ArchitectureHardTests(unittest.TestCase):
    """Control-plane locks for exclusive door, charge authority, act honesty, ledger, receipts."""

    @classmethod
    def setUpClass(cls):
        import db as gate_db

        gate_db.init_db()
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_welded_act_never_executes_write(self):
        live = {
            "ok": True,
            "verdict": True,
            "state": "LIVE",
            "verify_url": "https://velaru.xyz/verify?r=act",
        }
        with mock.patch.object(gate_app, "velaru_fuse", return_value=(live, 200, {})):
            r = self.client.post(
                "/demo/act",
                json={"fuse_id": "fuse_velaru_drill", "action": "payout"},
            )
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertTrue(body["acted"])
        self.assertFalse(body["write_executed"])
        self.assertTrue(body["clearance_only"])
        self.assertFalse(body["side_effect"])
        self.assertEqual(r.headers.get("X-Gate-Write-Executed"), "0")

    def test_charge_rejects_freeform_outside_dev(self):
        import license_fuse as lf

        prev = os.environ.get("GATE_DEV_MODE")
        try:
            os.environ["GATE_DEV_MODE"] = "0"
            bad = lf.charge(license_id="lic:HARD-1", charge_id="chg_should_fail")
            self.assertFalse(bad["ok"])
            self.assertEqual(bad["reason"], "charge_authority_invalid")
        finally:
            if prev is None:
                os.environ.pop("GATE_DEV_MODE", None)
            else:
                os.environ["GATE_DEV_MODE"] = prev

    def test_charge_hmac_and_replay(self):
        import charge_authority as ca
        import license_fuse as lf

        token = ca.mint_hmac(purpose="license", subject="lic:HARD-HMAC")
        self.assertTrue(token and token.startswith("sig:"))
        ok = lf.charge(license_id="lic:HARD-HMAC", charge_id=token)
        self.assertTrue(ok["ok"])
        self.assertEqual(ok["charge_authority"], "hmac_sig")
        replay = lf.charge(license_id="lic:HARD-HMAC", charge_id=token)
        self.assertFalse(replay["ok"])
        self.assertEqual(replay["reason"], "charge_authority_replay")

    def test_production_requires_exclusive_door(self):
        import production_skin as skin

        refuse = skin.record_production_weld(
            write_path="POST /v1/payouts/x/release",
            counterparty="ops@carrier.example",
            note="their customer",
            confirm=True,
        )
        self.assertFalse(refuse["ok"])
        self.assertIn("exclusive_door", (refuse.get("error") or "").lower())

        ok = skin.record_production_weld(
            write_path="POST /v1/payouts/x/release",
            counterparty="ops@carrier.example",
            note="their customer",
            confirm=True,
            exclusive_door_url="https://carrier.example/worker",
            door_kind="cloudflare_worker",
        )
        self.assertTrue(ok["ok"])
        self.assertTrue(ok["their_production"])
        self.assertTrue(skin.their_production())

    def test_checkout_creates_weld_order_and_cleared_ledger(self):
        import db as gate_db

        r = self.client.post(
            "/operator/checkout",
            data={"email": "ops@example.test", "write": "withdraw", "include_floor": "1"},
            follow_redirects=False,
        )
        self.assertIn(r.status_code, (302, 303))
        # Dev checkout marks paid → weld_orders row
        with gate_db.db() as conn:
            gate_db._ensure_weld_orders_table(conn)
            n = conn.execute("SELECT COUNT(*) AS n FROM weld_orders").fetchone()["n"]
        self.assertGreaterEqual(n, 1)
        # Cleared flow requires ops; in GATE_DEV_MODE empty token is authorized
        cleared = self.client.post(
            "/v1/register/cleared",
            json={"cleared_cents": 12_000_000, "hop_count": 3, "install_session_id": "missing"},
        )
        # missing session still records if weld_order_id/session provided — session optional with note
        # Our API requires one of the ids; "missing" is fine as opaque id
        self.assertEqual(cleared.status_code, 200)
        self.assertTrue(cleared.get_json()["ok"])
        totals = self.client.get("/.well-known/cleared-flow.json").get_json()["totals"]
        self.assertGreaterEqual(totals["cleared_cents"], 12_000_000)

    def test_receipt_unsigned_halts_outside_dev(self):
        import receipt as receipt_mod

        prev = os.environ.get("GATE_DEV_MODE")
        priv = os.environ.get("GATE_RECEIPT_PRIVATE_KEY")
        pub = os.environ.get("GATE_RECEIPT_PUBLIC_KEY")
        try:
            os.environ["GATE_DEV_MODE"] = "0"
            os.environ.pop("GATE_RECEIPT_PRIVATE_KEY", None)
            os.environ.pop("GATE_RECEIPT_PUBLIC_KEY", None)
            out = receipt_mod.issue_receipt(
                event_id="e1",
                fuse_id="fuse_x",
                job_id="j1",
                decision="HALT",
                acted=False,
                verify_url=None,
                created_at="2026-01-01T00:00:00+00:00",
                hop={},
                prev_receipt_hash=None,
            )
            self.assertTrue(out.get("unsigned_halt"))
        finally:
            if prev is None:
                os.environ.pop("GATE_DEV_MODE", None)
            else:
                os.environ["GATE_DEV_MODE"] = prev
            if priv:
                os.environ["GATE_RECEIPT_PRIVATE_KEY"] = priv
            if pub:
                os.environ["GATE_RECEIPT_PUBLIC_KEY"] = pub


class LiveDeskTests(unittest.TestCase):
    """Civilizational clearance clock + bypass canaries."""

    @classmethod
    def setUpClass(cls):
        import db as gate_db

        gate_db.init_db()
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_live_json_and_page(self):
        import db as gate_db

        with gate_db.db() as conn:
            gate_db._ensure_dogfood_table(conn)
            gate_db._ensure_third_party_welds(conn)
            conn.execute("DELETE FROM dogfood_welds")
            conn.execute("DELETE FROM third_party_welds")
        j = self.client.get("/.well-known/live.json")
        self.assertEqual(j.status_code, 200)
        data = j.get_json()
        self.assertEqual(data["spec"], "gate-live-desk-v1")
        self.assertIn("Can this irreversible write still execute right now?", data["question"])
        self.assertIn("SaaS status page", data["not"])
        self.assertNotIn("their_production", data)
        self.assertIn("surface_updated_at", data)
        page = self.client.get("/live")
        self.assertEqual(page.status_code, 200)
        body = page.get_data(as_text=True)
        self.assertIn("Gate", body)
        self.assertIn("Live", body)
        self.assertIn("Can this irreversible write still execute right now?", body)
        self.assertNotIn("Get API key", body)
        self.assertNotIn("Free tier", body)
        self.assertIn("Fraunces", body)

    def test_canary_bypass_requires_ops_and_confirm(self):
        import db as gate_db

        gate_app.GATE_DEV_MODE = True
        refuse = self.client.post(
            "/v1/canary/bypass",
            json={
                "write_path": "POST /v1/payouts/x/release",
                "job_id": f"pc:CANARY-{uuid.uuid4().hex[:8]}",
                "reporter": "ops@carrier.example",
            },
        )
        self.assertEqual(refuse.status_code, 400)
        self.assertFalse(refuse.get_json()["ok"])

        job = f"pc:CANARY-{uuid.uuid4().hex[:8]}"
        ok = self.client.post(
            "/v1/canary/bypass",
            json={
                "write_path": "POST /v1/payouts/x/release",
                "job_id": job,
                "reporter": "ops@carrier.example",
                "note": "shadow rail suspected",
                "confirm": True,
            },
        )
        self.assertEqual(ok.status_code, 200)
        body = ok.get_json()
        self.assertTrue(body["ok"])
        self.assertTrue(body["evaluation"]["bypass_suspected"])
        self.assertEqual(body["severity"], "BYPASS")

        live = self.client.get("/.well-known/live.json").get_json()
        self.assertGreaterEqual(live["canaries"]["open_alarms"], 1)

        canary = self.client.get("/.well-known/canary.json").get_json()
        self.assertEqual(canary["spec"], "gate-bypass-canary-v1")
        self.assertGreaterEqual(canary["open_alarms"], 1)

        # Parent kill path
        lid = f"lic:CANARY-{uuid.uuid4().hex[:8]}"
        gate_db.upsert_license_parent(license_id=lid, state="LIVE", charge_id="chg_seed")
        killed = self.client.post(
            "/v1/canary/bypass",
            json={
                "write_path": "POST /job/v1/jobs/x/bind-only",
                "job_id": f"pc:KILL-{uuid.uuid4().hex[:8]}",
                "reporter": "ops@carrier.example",
                "license_id": lid,
                "kill_parent": True,
                "confirm": True,
            },
        )
        self.assertEqual(killed.status_code, 200)
        self.assertEqual(killed.get_json()["parent"]["state"], "DEAD")


class PrefinalityTests(FlaskListingTests):
    PAYTO = "0x0000000000000000000000000000000000000001"

    def test_manifest_and_jwks(self):
        m = self.client.get("/.well-known/prefinality.json")
        self.assertEqual(m.status_code, 200)
        body = m.get_json()
        self.assertEqual(body["spec"], "gate-prefinality-v1")
        self.assertIn("x402", [r["id"] for r in body["rails"]])
        self.assertIn("rtp", [r["id"] for r in body["rails"]])
        jwks = self.client.get("/.well-known/prefinality-jwks.json")
        self.assertEqual(jwks.status_code, 200)
        self.assertTrue(jwks.get_json().get("keys"))

    def test_demo_x402_go_and_verify(self):
        r = self.client.post(
            "/demo/prefinality/evaluate",
            json={
                "rail": "x402",
                "transfer": {"amount": "0.002", "currency": "USDC", "counterparty": self.PAYTO},
                "mandate": {"agent_id": "test-agent", "max_amount": "1.00"},
            },
        )
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data["decision"], "GO")
        self.assertTrue(data.get("receipt"))
        self.assertFalse(data.get("halt"))
        v = self.client.post(
            "/v1/prefinality/verify",
            json={
                "receipt": data["receipt"],
                "rail": "x402",
                "transfer": {"amount": "0.002", "currency": "USDC", "counterparty": self.PAYTO},
            },
        )
        self.assertEqual(v.status_code, 200)
        self.assertTrue(v.get_json().get("valid"))

    def test_routing_anomaly_blocks(self):
        r = self.client.post(
            "/demo/prefinality/evaluate",
            json={
                "rail": "x402",
                "transfer": {"amount": "0.50", "currency": "USDC", "counterparty": self.PAYTO},
                "mandate": {
                    "agent_id": "test-agent",
                    "expected_payto": "0x0000000000000000000000000000000000000002",
                },
            },
        )
        data = r.get_json()
        self.assertEqual(data["decision"], "NO_GO")
        self.assertIn("routing_anomaly", data.get("signals", []))

    def test_rtp_evaluate_and_gate(self):
        r = self.client.post(
            "/demo/prefinality/evaluate",
            json={
                "rail": "rtp",
                "transfer": {
                    "amount": "100.00",
                    "currency": "USD",
                    "routing_number": "021000021",
                    "account_number": "123456789",
                },
                "mandate": {"agent_id": "treasury-bot", "max_amount": "500.00"},
            },
        )
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data["decision"], "GO")
        receipt = data["receipt"]
        gate = self.client.post(
            "/v1/prefinality/rtp/gate",
            json={
                "receipt": receipt,
                "payment_order": {
                    "type": "rtp",
                    "amount": 10000,
                    "currency": "USD",
                    "routing_number": "021000021",
                    "account_number": "123456789",
                },
            },
        )
        self.assertEqual(gate.status_code, 200)
        self.assertTrue(gate.get_json().get("allow"))

    def test_x402_catalog_lists_prefinality(self):
        cat = self.client.get("/.well-known/x402.json")
        self.assertEqual(cat.status_code, 200)
        body = cat.get_json()
        self.assertIn("prefinality", body)
        resources = [x.get("resource") for x in body.get("resources", [])]
        self.assertTrue(any("/v1/prefinality/evaluate" in (u or "") for u in resources))


    def test_x402_fanout_lists_prefinality(self):
        r = self.client.get("/.well-known/x402")
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(body.get("version"), 1)
        resources = body.get("resources") or []
        self.assertTrue(any("prefinality/evaluate" in u for u in resources))

    def test_prefinality_evaluate_402_when_payto_configured(self):
        payto = "0x00000000000000000000000000000000000000aa"
        with mock.patch.object(gate_app.x402_challenge_mod, "payto", return_value=payto):
            with mock.patch.object(gate_app.x402_challenge_mod, "payto_configured", return_value=True):
                with mock.patch.object(
                    gate_app.x402_challenge_mod,
                    "payment_required_response",
                    wraps=gate_app.x402_challenge_mod.payment_required_response,
                ):
                    r = self.client.post(
                        "/v1/prefinality/evaluate",
                        json={
                            "rail": "x402",
                            "transfer": {
                                "amount": "0.002",
                                "currency": "USDC",
                                "counterparty": "0x0000000000000000000000000000000000000001",
                            },
                        },
                    )
        self.assertEqual(r.status_code, 402)
        data = r.get_json()
        self.assertEqual(data.get("x402Version"), 2)
        accepts = data.get("accepts") or []
        self.assertTrue(accepts)
        self.assertEqual(accepts[0].get("payTo"), payto)
        self.assertIn("Payment-Required", r.headers)

    def test_prefinality_evaluate_get_402_when_payto_configured(self):
        payto = "0x00000000000000000000000000000000000000aa"
        with mock.patch.object(gate_app.x402_challenge_mod, "payto", return_value=payto):
            with mock.patch.object(gate_app.x402_challenge_mod, "payto_configured", return_value=True):
                r = self.client.get("/v1/prefinality/evaluate")
        self.assertEqual(r.status_code, 402)
        self.assertEqual((r.get_json().get("accepts") or [{}])[0].get("payTo"), payto)
        self.assertIn("Payment-Required", r.headers)

    def test_payto_reads_demo_env(self):
        payto = "0x00000000000000000000000000000000000000aa"
        with mock.patch.dict(
            os.environ,
            {"GATE_X402_PAYTO": "", "GATE_X402_PAY_TO": "", "GATE_X402_DEMO_PAYTO": payto},
            clear=False,
        ):
            self.assertEqual(gate_app.x402_challenge_mod.payto(), payto)
            self.assertTrue(gate_app.x402_challenge_mod.payto_configured())
            dbg = gate_app.x402_challenge_mod.payto_debug()
            self.assertTrue(dbg["configured"])
            self.assertEqual(dbg["env_key"], "GATE_X402_DEMO_PAYTO")


class X402AuditWireTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_audit_page_renders(self):
        r = self.client.get("/audit")
        self.assertEqual(r.status_code, 200)
        body = r.get_data(as_text=True)
        self.assertIn("x402 endpoint audit", body)

    def test_audit_page_with_url(self):
        r = self.client.get(
            "/audit",
            query_string={"url": "http://localhost/v1/prefinality/evaluate"},
        )
        self.assertEqual(r.status_code, 200)
        body = r.get_data(as_text=True)
        self.assertIn("Grade", body)

    def test_audit_api_redirects_browsers_without_url(self):
        r = self.client.get("/api/x402/audit", headers={"Accept": "text/html"})
        self.assertEqual(r.status_code, 302)
        self.assertIn("/audit", r.headers.get("Location", ""))

    def test_audit_requires_url(self):
        r = self.client.get("/api/x402/audit")
        self.assertEqual(r.status_code, 400)

    def test_audit_free_local_evaluate(self):
        r = self.client.get(
            "/api/x402/audit",
            query_string={"url": "http://localhost/v1/prefinality/evaluate"},
        )
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(body.get("spec"), "gate-x402-audit-v1")
        self.assertIn("score", body)
        self.assertIsInstance(body.get("ok"), bool)

    def test_wire_requires_domain_email(self):
        r = self.client.get("/api/x402/wire")
        self.assertEqual(r.status_code, 400)

    def test_wire_402_when_payto_configured(self):
        payto = "0x00000000000000000000000000000000000000bb"
        with mock.patch.object(gate_app.x402_challenge_mod, "payto", return_value=payto):
            with mock.patch.object(gate_app.x402_challenge_mod, "payto_configured", return_value=True):
                r = self.client.get(
                    "/api/x402/wire",
                    query_string={"domain": "example.com", "email": "a@example.com"},
                )
        self.assertEqual(r.status_code, 402)
        data = r.get_json()
        accepts = data.get("accepts") or []
        self.assertEqual(accepts[0].get("amount"), "497000000")

    def test_wire_delivers_bundle_on_payment_header(self):
        # Header presence alone must NOT unlock — facilitator verify required.
        with mock.patch.object(gate_app.x402_challenge_mod, "payto", return_value="0x" + "11" * 20):
            with mock.patch.object(gate_app.x402_challenge_mod, "payto_configured", return_value=True):
                forged = self.client.get(
                    "/api/x402/wire",
                    query_string={"domain": "example.com", "email": "a@example.com"},
                    headers={"X-Payment": "not-a-real-payment"},
                )
        self.assertEqual(forged.status_code, 402)
        self.assertEqual(
            (forged.get_json() or {}).get("x402_verify", {}).get("ok"),
            False,
        )
        # Verified path (dev escape mocked) still delivers.
        with mock.patch.object(
            gate_app.x402_challenge_mod,
            "payment_verified",
            return_value={"ok": True, "reason": "test_verified", "paid": True},
        ):
            r = self.client.get(
                "/api/x402/wire",
                query_string={"domain": "example.com", "email": "a@example.com"},
                headers={"X-Payment": "test"},
            )
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertTrue(body.get("paid"))
        self.assertIn("deploy_checklist", body)
        self.assertIn("bundle_id", body)

    def test_x402_fanout_lists_audit_and_wire(self):
        r = self.client.get("/.well-known/x402")
        body = r.get_json()
        resources = body.get("resources") or []
        self.assertTrue(any("/api/x402/wire" in u for u in resources))
        free = body.get("free_resources") or []
        self.assertTrue(any("/audit" in u for u in free))
        self.assertTrue(any("/api/x402/audit" in u for u in free))


class RailTruthAndDenyRegistryTests(unittest.TestCase):
    """Settlement truth atoms: finality oracle, loss allocation, negative deny registry."""

    @classmethod
    def setUpClass(cls):
        os.environ["GATE_DB_PATH"] = os.path.join(
            tempfile.gettempdir(), f"gate-rail-truth-{uuid.uuid4().hex}.db"
        )
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_rail_truth_manifest_and_lookup(self):
        m = self.client.get("/.well-known/rail-truth.json")
        self.assertEqual(m.status_code, 200)
        body = m.get_json()
        self.assertEqual(body["spec"], "gate-rail-truth-v1")
        self.assertIn("ach", body["rails"])
        self.assertIn("fednow", body["rails"])
        self.assertIn("wire", body["rails"])

        ach = self.client.get("/v1/rail-truth/ach")
        self.assertEqual(ach.status_code, 200)
        data = ach.get_json()
        self.assertIn("finality", data)
        self.assertIn("loss", data)
        self.assertEqual(data["loss"]["machine_label"], "originator_heavy")
        self.assertEqual(
            data["finality"]["agent_safe_default"],
            "treat_as_reversible_until_return_window_closed",
        )

        fin = self.client.get("/v1/rail-truth/wire/finality")
        self.assertEqual(fin.status_code, 200)
        self.assertEqual(fin.get_json()["agent_safe_default"], "treat_as_final_after_accept")

        loss = self.client.get("/v1/rail-truth/card/loss")
        self.assertEqual(loss.status_code, 200)
        self.assertEqual(loss.get_json()["machine_label"], "reason_code_split")

        missing = self.client.get("/v1/rail-truth/not-a-rail")
        self.assertEqual(missing.status_code, 404)

        gate = self.client.get("/.well-known/gate.json").get_json()
        self.assertIn("rail_truth", gate)
        self.assertIn("deny_registry", gate)

    def test_deny_registry_fingerprint_register_lookup(self):
        fp = self.client.post(
            "/v1/deny-registry/fingerprint",
            json={
                "rail": "wire",
                "amount": "100.00",
                "currency": "USD",
                "destination": "acct_demo_1",
                "agent_id": "agent_x",
            },
        )
        self.assertEqual(fp.status_code, 200)
        payout_hash = fp.get_json()["payout_hash"]
        self.assertEqual(len(payout_hash), 64)

        before = self.client.get(f"/v1/deny-registry/{payout_hash}")
        self.assertEqual(before.status_code, 200)
        self.assertFalse(before.get_json()["denied"])

        reg = self.client.post(
            "/v1/deny-registry",
            json={
                "payout_hash": payout_hash,
                "reason_code": "destination_mismatch",
                "rail": "wire",
            },
        )
        self.assertEqual(reg.status_code, 201)
        self.assertEqual(reg.get_json()["payout_hash"], payout_hash)

        after = self.client.get(f"/v1/deny-registry/{payout_hash}")
        self.assertTrue(after.get_json()["denied"])
        self.assertGreaterEqual(after.get_json()["count"], 1)

        man = self.client.get("/.well-known/deny-registry.json")
        self.assertEqual(man.status_code, 200)
        self.assertEqual(man.get_json()["spec"], "gate-deny-registry-v1")

    def test_clear_page_and_api(self):
        page = self.client.get("/clear")
        self.assertEqual(page.status_code, 200)
        html = page.get_data(as_text=True)
        self.assertIn("Gate", html)
        self.assertIn("Clear", html)
        self.assertIn("this money can still come back", html.lower())
        self.assertIn("don't send", html.lower())
        self.assertIn('data-rail="ach"', html)

        man = self.client.get("/.well-known/clear.json")
        self.assertEqual(man.status_code, 200)
        self.assertEqual(man.get_json()["spec"], "gate-clear-v1")
        self.assertIn("ach", man.get_json()["rails"])

        bare = self.client.get("/v1/clear")
        self.assertEqual(bare.status_code, 200)
        self.assertEqual(bare.get_json()["spec"], "gate-clear-v1")

        ach = self.client.get("/v1/clear?rail=ach")
        self.assertEqual(ach.status_code, 200)
        body = ach.get_json()
        self.assertEqual(body["word"], "REVERSIBLE")
        self.assertIn("pulled", body["plain"].lower())
        self.assertNotIn("their_production", body)

        wire = self.client.get("/v1/clear?rail=wire")
        self.assertEqual(wire.status_code, 200)
        self.assertEqual(wire.get_json()["word"], "FINAL")

        missing = self.client.get("/v1/clear?rail=not-a-rail")
        self.assertEqual(missing.status_code, 404)

        bad = self.client.get("/v1/clear?payout_hash=abc")
        self.assertEqual(bad.status_code, 400)

        fp = self.client.post(
            "/v1/deny-registry/fingerprint",
            json={
                "rail": "ach",
                "amount": "1.00",
                "currency": "USD",
                "destination": "acct_clear_demo",
            },
        )
        payout_hash = fp.get_json()["payout_hash"]
        before = self.client.get(f"/v1/clear?payout_hash={payout_hash}")
        self.assertEqual(before.get_json()["word"], "NOT DENIED")
        self.client.post(
            "/v1/deny-registry",
            json={"payout_hash": payout_hash, "reason_code": "clear_ui_test", "rail": "ach"},
        )
        after = self.client.get(f"/v1/clear?payout_hash={payout_hash}")
        self.assertEqual(after.get_json()["word"], "DENIED")

        gate = self.client.get("/.well-known/gate.json").get_json()
        self.assertIn("clear", gate)
        self.assertIn("clear_api", gate)

        sm = self.client.get("/sitemap.xml").get_data(as_text=True)
        self.assertIn("/clear", sm)


class SealUiTests(unittest.TestCase):
    """Apple-simple seal over signed receipt + Merkle inclusion."""

    @classmethod
    def setUpClass(cls):
        os.environ["GATE_DB_PATH"] = os.path.join(
            tempfile.gettempdir(), f"gate-seal-{uuid.uuid4().hex}.db"
        )
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_seal_page_manifest_and_holds(self):
        page = self.client.get("/seal")
        self.assertEqual(page.status_code, 200)
        html = page.get_data(as_text=True)
        self.assertIn("Seal", html)
        self.assertIn("receipt id", html.lower())

        man = self.client.get("/.well-known/seal.json")
        self.assertEqual(man.status_code, 200)
        self.assertEqual(man.get_json()["spec"], "gate-seal-v1")

        missing = self.client.get("/v1/seal?event_id=not-a-real-event")
        self.assertEqual(missing.status_code, 200)
        self.assertEqual(missing.get_json()["word"], "MISSING")

        r = self.client.post(
            "/demo/pas/policycenter/pre-bind",
            json={"fuse_id": "fuse_velaru_drill", "job_id": "pc:SEAL-UI"},
        )
        self.assertEqual(r.status_code, 200)
        import db as gate_db

        latest = gate_db.list_bind_events(None, limit=1)[0]
        event_id = latest["id"]
        self.assertTrue(latest.get("receipt_hash"))

        sealed = self.client.get(f"/v1/seal?event_id={event_id}")
        self.assertEqual(sealed.status_code, 200)
        body = sealed.get_json()
        self.assertIn(body["word"], ("HOLDS", "UNSIGNED"))
        self.assertTrue(body["checks"]["hash"])
        self.assertTrue(body["checks"]["inclusion"])
        if latest.get("receipt_signature"):
            self.assertEqual(body["word"], "HOLDS")
            self.assertTrue(body["checks"]["signature"])

        prefilled = self.client.get(f"/seal?event_id={event_id}")
        self.assertEqual(prefilled.status_code, 200)
        self.assertIn(event_id, prefilled.get_data(as_text=True))

        gate = self.client.get("/.well-known/gate.json").get_json()
        self.assertIn("seal", gate)
        self.assertIn("seal_api", gate)


class GoAndNeverUiTests(unittest.TestCase):
    """Apple-simple Go + Never over prefinality and exclusion."""

    PAYTO = "0x0000000000000000000000000000000000000001"

    @classmethod
    def setUpClass(cls):
        os.environ["GATE_DB_PATH"] = os.path.join(
            tempfile.gettempdir(), f"gate-go-never-{uuid.uuid4().hex}.db"
        )
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_go_page_and_api(self):
        page = self.client.get("/go")
        self.assertEqual(page.status_code, 200)
        self.assertIn("Go", page.get_data(as_text=True))
        self.assertIn("Don't send more than", page.get_data(as_text=True))

        man = self.client.get("/.well-known/go.json")
        self.assertEqual(man.status_code, 200)
        self.assertEqual(man.get_json()["spec"], "gate-go-v1")

        go = self.client.post(
            "/v1/go",
            json={
                "rail": "x402",
                "transfer": {
                    "amount": "0.002",
                    "currency": "USDC",
                    "counterparty": self.PAYTO,
                },
                "mandate": {"agent_id": "go-test", "max_amount": "1.00"},
            },
        )
        self.assertEqual(go.status_code, 200)
        body = go.get_json()
        self.assertEqual(body["word"], "GO")
        self.assertEqual(body["decision"], "GO")
        self.assertNotIn("their_production", body)

        nogo = self.client.post(
            "/v1/go",
            json={
                "rail": "x402",
                "transfer": {
                    "amount": "5.00",
                    "currency": "USDC",
                    "counterparty": self.PAYTO,
                },
                "mandate": {"agent_id": "go-test", "max_amount": "1.00"},
            },
        )
        self.assertEqual(nogo.get_json()["word"], "NO GO")
        self.assertEqual(nogo.get_json()["decision"], "NO_GO")

        gate = self.client.get("/.well-known/gate.json").get_json()
        self.assertIn("go", gate)
        self.assertIn("go_api", gate)

    def test_never_page_and_api(self):
        page = self.client.get("/never")
        self.assertEqual(page.status_code, 200)
        self.assertIn("Never", page.get_data(as_text=True))

        man = self.client.get("/.well-known/never.json")
        self.assertEqual(man.status_code, 200)
        self.assertEqual(man.get_json()["spec"], "gate-never-v1")

        bare = self.client.get("/v1/never")
        self.assertEqual(bare.get_json()["spec"], "gate-never-v1")

        never = self.client.get("/v1/never?job_id=pc:NEVER-FRESH")
        self.assertEqual(never.status_code, 200)
        self.assertEqual(never.get_json()["word"], "NEVER")
        self.assertFalse(never.get_json()["spent"])
        self.assertTrue(never.get_json()["verified"])

        live = {
            "ok": True,
            "verdict": True,
            "state": "LIVE",
            "verify_url": "https://velaru.xyz/verify?r=never",
        }
        with mock.patch.object(gate_app, "velaru_fuse", return_value=(live, 200, {})):
            r = self.client.post(
                "/demo/pas/policycenter/pre-bind",
                json={"fuse_id": "fuse_velaru_drill", "job_id": "pc:NEVER-SPENT"},
            )
        self.assertEqual(r.status_code, 200)
        ticket = r.get_json()["bind_ticket"]
        redeem = self.client.post(
            "/demo/pas/bind-ticket/redeem",
            json={
                "ticket_id": ticket["ticket_id"],
                "token": ticket["token"],
                "job_id": "pc:NEVER-SPENT",
                "method": "POST",
                "path": "/job/v1/jobs/pc:NEVER-SPENT/bind-only",
                "spend_fingerprint": ticket["spend_fingerprint"],
                "now": _now(),
            },
        )
        self.assertEqual(redeem.status_code, 200)

        spent = self.client.get("/v1/never?job_id=pc:NEVER-SPENT")
        self.assertEqual(spent.get_json()["word"], "SPENT")
        self.assertTrue(spent.get_json()["spent"])

        gate = self.client.get("/.well-known/gate.json").get_json()
        self.assertIn("never", gate)
        self.assertIn("never_api", gate)

        sm = self.client.get("/sitemap.xml").get_data(as_text=True)
        self.assertIn("/go", sm)
        self.assertIn("/never", sm)

    def test_bind_room_commit_spend_not_demo_second_lookup_spent(self):
        import bind_room as bind_room_mod

        job_id = "br:bind-room-isolated"
        before = self.client.get(f"/v1/never?job_id={job_id}")
        self.assertEqual(before.get_json()["word"], "NEVER")
        out = bind_room_mod.commit_spend(
            job_id=job_id,
            redeem_url="https://gate.velaru.xyz/v1/pas/bind-ticket/redeem",
        )
        self.assertTrue(out.get("ok"))
        self.assertFalse(out.get("demo"))
        self.assertEqual(out.get("word"), "SPENT")
        first = self.client.get(f"/v1/never?job_id={job_id}")
        self.assertEqual(first.get_json()["word"], "SPENT")
        second = self.client.get(f"/v1/never?job_id={job_id}")
        self.assertEqual(second.get_json()["word"], "SPENT")
        replay = bind_room_mod.commit_spend(
            job_id=job_id,
            redeem_url="https://gate.velaru.xyz/v1/pas/bind-ticket/redeem",
        )
        self.assertTrue(replay.get("already"))


class MouthsPackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["GATE_DB_PATH"] = os.path.join(
            tempfile.gettempdir(), f"gate-mouths-{uuid.uuid4().hex}.db"
        )
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_pages_and_words(self):
        for path in (
            "/positive-clear",
            "/scenario-3",
            "/uapa-seal",
            "/admt",
            "/trusted-contact",
            "/stair",
        ):
            r = self.client.get(path)
            self.assertEqual(r.status_code, 200, path)
            self.assertIn("Gate", r.get_data(as_text=True))

        pc = self.client.post(
            "/v1/positive-clear",
            json={"kind": "mga_bind", "authority_live": "yes"},
        )
        self.assertEqual(pc.get_json()["word"], "PROCEED")

        s3 = self.client.post(
            "/v1/scenario-3",
            json={
                "known_supplier": True,
                "email_only": True,
                "new_account": True,
                "name_mismatch": False,
            },
        )
        self.assertEqual(s3.get_json()["word"], "MATCHES")
        self.assertIn("FIN-2016-A003", s3.get_json()["advisory"])

        uapa = self.client.post(
            "/v1/uapa-seal",
            json={
                "already_sent": "yes",
                "authorized": "yes",
                "induced": "yes",
                "rtp_native": "yes",
            },
        )
        self.assertEqual(uapa.get_json()["word"], "REPORTABLE")

        admt = self.client.post(
            "/v1/admt",
            json={
                "decision_class": "financial",
                "uses_admt": "yes",
                "pre_use_notice": "no",
            },
        )
        self.assertEqual(admt.get_json()["word"], "NOTICE DUE")
        self.assertIn("7200", admt.get_json()["cite"])

        miss = self.client.post("/v1/trusted-contact", json={"account_id": "acct-demo-1"})
        self.assertEqual(miss.get_json()["word"], "NO HOLD")
        sealed = self.client.post(
            "/v1/trusted-contact",
            json={"account_id": "acct-demo-1", "action": "seal"},
        )
        self.assertEqual(sealed.get_json()["word"], "HOLD")
        again = self.client.post("/v1/trusted-contact", json={"account_id": "acct-demo-1"})
        self.assertEqual(again.get_json()["word"], "HOLD")

        gate = self.client.get("/.well-known/gate.json").get_json()
        for k in (
            "positive_clear",
            "scenario_3",
            "uapa_seal",
            "admt",
            "trusted_contact",
            "stair",
        ):
            self.assertIn(k, gate)

        stair = self.client.post("/v1/stair", json={"kind": "egress_lock"})
        self.assertEqual(stair.get_json()["word"], "NEVER")
        money = self.client.post("/v1/stair", json={"kind": "money_or_bind"})
        self.assertEqual(money.get_json()["word"], "NOT THIS")

        nos = self.client.get("/.well-known/restraint.json").get_json()
        standing = nos.get("standing") or []
        self.assertTrue(any(s.get("id") == "occupied-egress" for s in standing))

        op = self.client.get("/operator").get_data(as_text=True)
        self.assertIn("Not occupied egress", op)
        inv = self.client.get("/.well-known/operator.json").get_json()
        self.assertTrue(any("occupied egress" in x for x in inv.get("refuse") or []))


if __name__ == "__main__":
    unittest.main()


class BuyerCredibilityTests(unittest.TestCase):
    """Prospect-facing surface: no demo smell, branded 404, security headers."""

    @classmethod
    def setUpClass(cls):
        import db as gate_db

        gate_db.init_db()
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_no_their_production_false_on_buyer_surfaces(self):
        import db as gate_db

        with gate_db.db() as conn:
            gate_db._ensure_dogfood_table(conn)
            gate_db._ensure_third_party_welds(conn)
            conn.execute("DELETE FROM dogfood_welds")
            conn.execute("DELETE FROM third_party_welds")
        paths = (
            "/",
            "/trust",
            "/live",
            "/operator",
            "/pricing",
            "/diligence",
            "/diligence/offer.json",
            "/diligence/one-pager.txt",
            "/.well-known/live.json",
            "/.well-known/production-skin.json",
            "/.well-known/operator.json",
            "/.well-known/spend-protocol.json",
            "/.well-known/clear.json",
            "/record",
            "/.well-known/record.json",
            "/.well-known/incidents.json",
            "/.well-known/red-team.json",
            "/.well-known/uptime.json",
            "/.well-known/evidence-watch.json",
        )
        for path in paths:
            r = self.client.get(path)
            self.assertEqual(r.status_code, 200, path)
            body = r.get_data(as_text=True)
            self.assertNotIn("their_production: false", body.lower(), path)
            if path.endswith(".json"):
                data = r.get_json()
                self.assertNotIn("their_production", data, path)

    def test_branded_404(self):
        r = self.client.get("/this-path-does-not-exist-credibility")
        self.assertEqual(r.status_code, 404)
        body = r.get_data(as_text=True)
        self.assertIn("This path is not on the desk", body)
        self.assertNotIn("The requested URL was not found on the server", body)
        self.assertEqual(r.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(r.headers.get("X-Frame-Options"), "DENY")
        self.assertIn("default-src", r.headers.get("Content-Security-Policy", ""))

    def test_trust_shows_surface_updated(self):
        r = self.client.get("/trust")
        self.assertEqual(r.status_code, 200)
        body = r.get_data(as_text=True)
        self.assertIn("Surface updated", body)
        self.assertNotIn("their_production: false", body.lower())

    def test_live_shows_surface_updated(self):
        r = self.client.get("/live")
        self.assertEqual(r.status_code, 200)
        body = r.get_data(as_text=True)
        self.assertIn("Surface updated", body)
        self.assertNotIn("their_production: false", body.lower())

    def test_security_headers_on_home(self):
        r = self.client.get("/", headers={"X-Forwarded-Proto": "https"})
        self.assertEqual(r.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(r.headers.get("X-Frame-Options"), "DENY")
        self.assertTrue(r.headers.get("Content-Security-Policy"))
        self.assertTrue(r.headers.get("Strict-Transport-Security"))


class RedTeamHardeningTests(unittest.TestCase):
    """Adversarial fixes: x402 fail-closed; job-level single spend."""

    @classmethod
    def setUpClass(cls):
        import db as gate_db

        gate_db.init_db()
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_x402_forged_header_does_not_unlock_prefinality(self):
        payto = "0x" + "ab" * 20
        with mock.patch.object(gate_app.x402_challenge_mod, "payto", return_value=payto):
            with mock.patch.object(gate_app.x402_challenge_mod, "payto_configured", return_value=True):
                r = self.client.post(
                    "/v1/prefinality/evaluate",
                    json={
                        "rail": "x402",
                        "transfer": {
                            "amount": "0.002",
                            "currency": "USDC",
                            "counterparty": payto,
                        },
                        "mandate": {"agent_id": "rt", "max_amount": "1.00"},
                    },
                    headers={"Payment-Signature": "not-a-real-payment"},
                )
        self.assertEqual(r.status_code, 402)
        body = r.get_json() or {}
        self.assertNotEqual((body.get("x402") or {}).get("paid"), True)

    def test_second_ticket_same_job_cannot_allow_bind(self):
        import ticket as ticket_mod
        import spend_protocol

        jid = f"rt:job-{uuid.uuid4().hex[:10]}"
        write = spend_protocol.write(job_id=jid)
        a = ticket_mod.issue(
            job_id=jid,
            fuse_id="fuse_velaru_drill",
            event_id=str(uuid.uuid4()),
            receipt_hash=None,
            redeem_url="https://example.test/redeem",
            spend_write=write,
        )
        b = ticket_mod.issue(
            job_id=jid,
            fuse_id="fuse_velaru_drill",
            event_id=str(uuid.uuid4()),
            receipt_hash=None,
            redeem_url="https://example.test/redeem",
            spend_write=write,
        )
        now = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()
        first = ticket_mod.redeem(
            ticket_id=a["bearer"]["ticket_id"],
            token=a["bearer"]["token"],
            job_id=jid,
            method=write["method"],
            path=write["path"],
            spend_fingerprint=a["bearer"]["spend_fingerprint"],
            now=now,
        )
        self.assertTrue(first.get("ok"))
        self.assertTrue(first.get("allow_bind"))
        second = ticket_mod.redeem(
            ticket_id=b["bearer"]["ticket_id"],
            token=b["bearer"]["token"],
            job_id=jid,
            method=write["method"],
            path=write["path"],
            spend_fingerprint=b["bearer"]["spend_fingerprint"],
            now=now,
        )
        self.assertFalse(second.get("ok"))
        self.assertFalse(second.get("allow_bind"))
        self.assertEqual(second.get("reason"), "job_already_spent")


class NewMouthsShipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import db as gate_db

        gate_db.init_db()
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_fednow_nacha_cl7_pages_and_evaluate(self):
        for path in (
            "/fednow-prepush",
            "/nacha-false-pretenses",
            "/cl7-handoff",
            "/.well-known/fednow-prepush.json",
            "/.well-known/nacha-false-pretenses.json",
            "/.well-known/cl7-handoff.json",
        ):
            self.assertEqual(self.client.get(path).status_code, 200, path)

        never = self.client.post(
            "/v1/fednow-prepush",
            json={
                "rail": "fednow",
                "payee_sealed": "no",
                "first_time_payee": "no",
                "fraud_suspected": "no",
            },
        )
        self.assertEqual(never.status_code, 200)
        self.assertEqual(never.get_json()["word"], "NEVER")

        fp = self.client.post(
            "/v1/nacha-false-pretenses",
            json={
                "role": "odfi",
                "false_pretenses_suspected": "yes",
                "who_what_payee_sealed": "no",
            },
        )
        self.assertEqual(fp.get_json()["word"], "NEVER")

        cl7 = self.client.post(
            "/v1/cl7-handoff",
            json={"ais_ecdis_handoff": "yes", "written_notice_15d": "no"},
        )
        self.assertEqual(cl7.get_json()["word"], "NEVER")

        import mouths as mouths_mod

        self.assertEqual(len(mouths_mod.PARKED_MOUTHS), 1)
        self.assertEqual(mouths_mod.PARKED_MOUTHS[0]["id"], "visa-agentic-chargebacks")


class TrackRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import db as gate_db

        gate_db.init_db()
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_record_page_posts_x402_and_race(self):
        r = self.client.get("/record")
        self.assertEqual(r.status_code, 200)
        body = r.get_data(as_text=True)
        self.assertIn("x402 treated a payment header as paid", body)
        self.assertIn("Two tickets could spend the same job_id", body)
        self.assertIn("Surface updated", body)
        self.assertIn("Zero independent watchers", body)
        self.assertIn("hello@velaru.xyz", body)
        self.assertNotIn("their_production: false", body.lower())

    def test_incidents_json_and_footer(self):
        data = self.client.get("/.well-known/incidents.json").get_json()
        ids = {i["id"] for i in data["incidents"]}
        self.assertIn("2026-09-24-x402-header-paid", ids)
        self.assertIn("2026-09-24-spend-map-race", ids)
        home = self.client.get("/").get_data(as_text=True)
        self.assertIn('href="/record"', home)
        alias = self.client.get("/incidents")
        self.assertIn(alias.status_code, (301, 302))
        watch = self.client.get("/.well-known/evidence-watch.json").get_json()
        self.assertEqual(watch["first_party"]["independent"], False)
        self.assertEqual(watch["independent_watchers"], [])
        cadence = self.client.get("/.well-known/red-team.json").get_json()
        self.assertEqual(cadence["cadence"], "monthly")
        self.assertEqual(cadence["next"], "2026-10-24")

    def test_consistency_old_root_mismatch_fails(self):
        r = self.client.get(
            "/.well-known/evidence-consistency.json",
            query_string={"old_size": "0", "old_root": "deadbeef"},
        )
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertFalse(body.get("cached_old_root_matches"))
        self.assertFalse(body.get("valid"))

    def test_watch_check_rejects_shrink(self):
        import watch_evidence_head as watch

        ok = watch.check_cached_head({"tree_size": 2, "root_hash": "aa"}, None)
        self.assertTrue(ok["ok"])
        bad = watch.check_cached_head(
            {"tree_size": 1, "root_hash": "bb"},
            {"tree_size": 2, "root_hash": "aa"},
        )
        self.assertFalse(bad["ok"])
        rewrite = watch.check_cached_head(
            {"tree_size": 2, "root_hash": "cc"},
            {"tree_size": 2, "root_hash": "aa"},
        )
        self.assertFalse(rewrite["ok"])

    def test_uptime_does_not_invent_sla(self):
        data = self.client.get("/.well-known/uptime.json").get_json()
        self.assertIn("SLA", " ".join(data["not"]))
        if data["samples"] < 20:
            self.assertIsNone(data["pct_up"])

    def test_watch_script_served(self):
        r = self.client.get("/watch/evidence-head.py")
        self.assertEqual(r.status_code, 200)
        self.assertIn("tree only grows", r.get_data(as_text=True).lower())

    def test_shared_failure_named(self):
        data = self.client.get("/.well-known/record.json").get_json()
        self.assertIn("sqlite", data["shared_failure"]["answer"].lower())
        self.assertFalse(data["shared_failure"]["category_tested"])
        self.assertIn("backup", data["first_bottleneck"]["answer"].lower())


class X402FacilitatorUnlockTests(unittest.TestCase):
    """CDP facilitator verify+settle unlocks paid routes; forged stays 402."""

    @classmethod
    def setUpClass(cls):
        import db as gate_db

        gate_db.init_db()
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def setUp(self):
        # Isolate facilitator env per test.
        self._env = mock.patch.dict(
            os.environ,
            {
                "GATE_X402_ACCEPT_UNVERIFIED": "0",
                "GATE_DEV_MODE": "1",
                "CDP_API_KEY_ID": "",
                "CDP_API_KEY_SECRET": "",
                "GATE_X402_FACILITATOR_URL": "",
            },
            clear=False,
        )
        self._env.start()

    def tearDown(self):
        self._env.stop()

    def _ed25519_cdp_secret(self) -> str:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from cryptography.hazmat.primitives import serialization
        import base64

        key = Ed25519PrivateKey.generate()
        seed = key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
        pub = key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        return base64.b64encode(seed + pub).decode("ascii")

    def _v2_payload(self, payto: str, amount: str = "2000") -> dict:
        return {
            "x402Version": 2,
            "accepted": {
                "scheme": "exact",
                "network": "eip155:8453",
                "amount": amount,
                "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
                "payTo": payto,
                "maxTimeoutSeconds": 300,
                "extra": {"name": "USD Coin", "version": "2"},
            },
            "payload": {
                "signature": "0x" + "ab" * 65,
                "authorization": {
                    "from": "0x" + "11" * 20,
                    "to": payto,
                    "value": amount,
                    "validAfter": "0",
                    "validBefore": "9999999999",
                    "nonce": "0x" + "cd" * 32,
                },
            },
            "resource": {
                "url": "https://gate.example/v1/prefinality/evaluate",
                "description": "test",
                "mimeType": "application/json",
            },
        }

    def test_forged_header_still_402_with_cdp_keys(self):
        import base64
        import json

        payto = "0x" + "ab" * 20
        secret = self._ed25519_cdp_secret()
        with mock.patch.dict(
            os.environ,
            {
                "CDP_API_KEY_ID": "test-key-id",
                "CDP_API_KEY_SECRET": secret,
                "GATE_X402_FACILITATOR_URL": "https://api.cdp.coinbase.com/platform/v2/x402",
            },
        ):
            with mock.patch.object(gate_app.x402_challenge_mod, "payto", return_value=payto):
                with mock.patch.object(
                    gate_app.x402_challenge_mod, "payto_configured", return_value=True
                ):
                    # Garbage header must not unlock (decode fails → 402).
                    r = self.client.post(
                        "/v1/prefinality/evaluate",
                        json={
                            "rail": "x402",
                            "transfer": {
                                "amount": "0.002",
                                "currency": "USDC",
                                "counterparty": payto,
                            },
                            "mandate": {"agent_id": "rt", "max_amount": "1.00"},
                        },
                        headers={"Payment-Signature": "not-a-real-payment"},
                    )
        self.assertEqual(r.status_code, 402)

        # Valid-shaped payload but facilitator rejects → still 402.
        payload = self._v2_payload(payto)
        encoded = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")

        def fake_post(url, headers=None, json=None, timeout=None):  # noqa: A002
            class Resp:
                status_code = 200

                def json(self):
                    if url.endswith("/verify"):
                        return {
                            "isValid": False,
                            "invalidReason": "invalid_payload",
                            "invalidMessage": "bad sig",
                        }
                    return {"success": False}

            return Resp()

        with mock.patch.dict(
            os.environ,
            {
                "CDP_API_KEY_ID": "test-key-id",
                "CDP_API_KEY_SECRET": secret,
            },
        ):
            with mock.patch("x402_facilitator.requests.post", side_effect=fake_post):
                with mock.patch.object(gate_app.x402_challenge_mod, "payto", return_value=payto):
                    with mock.patch.object(
                        gate_app.x402_challenge_mod, "payto_configured", return_value=True
                    ):
                        r2 = self.client.post(
                            "/v1/prefinality/evaluate",
                            json={
                                "rail": "x402",
                                "transfer": {
                                    "amount": "0.002",
                                    "currency": "USDC",
                                    "counterparty": payto,
                                },
                                "mandate": {"agent_id": "rt", "max_amount": "1.00"},
                            },
                            headers={"Payment-Signature": encoded},
                        )
        self.assertEqual(r2.status_code, 402)

    def test_mocked_facilitator_unlocks_prefinality(self):
        import base64
        import json

        payto = "0x" + "cd" * 20
        secret = self._ed25519_cdp_secret()
        payload = self._v2_payload(payto)
        encoded = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")

        calls = []

        def fake_post(url, headers=None, json=None, timeout=None):  # noqa: A002
            calls.append(url)

            class Resp:
                status_code = 200

                def json(self_inner):
                    if url.rstrip("/").endswith("/verify"):
                        return {"isValid": True, "payer": "0x" + "11" * 20}
                    return {
                        "success": True,
                        "payer": "0x" + "11" * 20,
                        "transaction": "0x" + "ee" * 32,
                        "network": "eip155:8453",
                        "amount": "2000",
                    }

            return Resp()

        with mock.patch.dict(
            os.environ,
            {
                "CDP_API_KEY_ID": "test-key-id",
                "CDP_API_KEY_SECRET": secret,
                "GATE_X402_FACILITATOR_URL": "https://api.cdp.coinbase.com/platform/v2/x402",
            },
        ):
            with mock.patch("x402_facilitator.requests.post", side_effect=fake_post):
                with mock.patch.object(gate_app.x402_challenge_mod, "payto", return_value=payto):
                    with mock.patch.object(
                        gate_app.x402_challenge_mod, "payto_configured", return_value=True
                    ):
                        r = self.client.post(
                            "/v1/prefinality/evaluate",
                            json={
                                "rail": "x402",
                                "transfer": {
                                    "amount": "0.002",
                                    "currency": "USDC",
                                    "counterparty": payto,
                                },
                                "mandate": {"agent_id": "buyer", "max_amount": "1.00"},
                            },
                            headers={"Payment-Signature": encoded},
                        )
        self.assertEqual(r.status_code, 200, r.get_data(as_text=True)[:500])
        body = r.get_json() or {}
        self.assertTrue((body.get("x402") or {}).get("paid"))
        self.assertEqual((body.get("x402") or {}).get("reason"), "facilitator_settled")
        self.assertTrue(any(u.endswith("/verify") for u in calls))
        self.assertTrue(any(u.endswith("/settle") for u in calls))

    def test_payto_mismatch_fails_closed(self):
        import base64
        import json

        our = "0x" + "aa" * 20
        other = "0x" + "bb" * 20
        secret = self._ed25519_cdp_secret()
        payload = self._v2_payload(other)
        encoded = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")

        with mock.patch.dict(
            os.environ,
            {"CDP_API_KEY_ID": "test-key-id", "CDP_API_KEY_SECRET": secret},
        ):
            with mock.patch.object(gate_app.x402_challenge_mod, "payto", return_value=our):
                result = gate_app.x402_challenge_mod.payment_verified(
                    {"Payment-Signature": encoded}
                )
        self.assertFalse(result.get("ok"))
        self.assertEqual(result.get("reason"), "payto_mismatch")

    def test_cdp_jwt_builds_uris_claim(self):
        import base64
        import json

        secret = self._ed25519_cdp_secret()
        with mock.patch.dict(
            os.environ,
            {"CDP_API_KEY_ID": "kid-123", "CDP_API_KEY_SECRET": secret},
        ):
            import x402_facilitator as fac

            token = fac.build_cdp_jwt(
                method="POST",
                host="api.cdp.coinbase.com",
                path="/platform/v2/x402/verify",
            )
        parts = token.split(".")
        self.assertEqual(len(parts), 3)
        pad = "=" * (-len(parts[0]) % 4)
        header = json.loads(base64.urlsafe_b64decode(parts[0] + pad))
        pad = "=" * (-len(parts[1]) % 4)
        claims = json.loads(base64.urlsafe_b64decode(parts[1] + pad))
        self.assertEqual(header.get("alg"), "EdDSA")
        self.assertEqual(header.get("kid"), "kid-123")
        self.assertEqual(claims.get("iss"), "cdp")
        self.assertEqual(
            claims.get("uris"),
            ["POST api.cdp.coinbase.com/platform/v2/x402/verify"],
        )

    def test_health_exposes_facilitator_ready_bool(self):
        r = self.client.get("/health")
        body = r.get_json() or {}
        self.assertIn("facilitator_ready", body.get("x402") or {})
        self.assertIsInstance((body.get("x402") or {}).get("facilitator_ready"), bool)

