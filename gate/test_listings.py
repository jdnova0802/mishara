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
import fields  # noqa: E402
import weld  # noqa: E402
import bind_room  # noqa: E402
import bound  # noqa: E402
import exclusive  # noqa: E402
import floor  # noqa: E402
import particular  # noqa: E402
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
        self.assertIn("bound_answer", m)
        self.assertIn("exclusive_timing", m)
        self.assertIn("floor", m)
        self.assertIn("particular", m)
        self.assertIn("capture", m)
        self.assertFalse(m["particular"]["tuesday_moved"])
        self.assertIn("policycenter", m["welds"])
        self.assertIn("PII", " ".join(m["refuse"]))

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
        self.assertIn("bind-and-issue", plan["next"]["path"])

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
        self.assertFalse(r2.get_json()["their_production"])
        self.assertTrue(r2.get_json()["receipt_is_not_the_product"])

    def test_floor_page_and_manifest(self):
        r = self.client.get("/floor")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"cleverer", r.data)
        r2 = self.client.get("/.well-known/floor.json")
        self.assertEqual(r2.status_code, 200)
        self.assertIsNone(r2.get_json()["cleverer_layer"])

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
        r2 = self.client.get("/.well-known/capture.json")
        self.assertEqual(r2.status_code, 200)
        data = r2.get_json()
        self.assertFalse(data["their_production"])
        paths = [w["path"] for w in data["cloud_api_spend_writes"]]
        self.assertTrue(any("bind-only" in p for p in paths))
        self.assertIn("quote", data["uw_issue"]["not_sufficient_why"].lower())

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
        self.assertFalse(body["exclusive_timing"]["their_production"])
        self.assertIn("stakes", body)
        self.assertIsNone(body["stakes"]["cleverer_layer"])
        self.assertFalse(body["stakes"]["treat_as_real"])

    def test_listings_still_health(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        self.assertIn("bind_room", r.get_json())
        r2 = self.client.get("/.well-known/listings.json")
        self.assertEqual(r2.status_code, 200)
        self.assertIn("welds", r2.get_json())


if __name__ == "__main__":
    unittest.main()
