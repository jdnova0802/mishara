"""Items 21–27 — triple vote, chain, rules, widget, ARP, badge/CLI, MCP verify."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-medium-features.db")
os.environ["GATE_RULES_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-medium-rules.json")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import arp  # noqa: E402
import gate_rules  # noqa: E402
import mcp_server  # noqa: E402
import triple_vote  # noqa: E402


class TripleVoteTests(unittest.TestCase):
    def test_three_allow_agree(self):
        v = triple_vote.grade(
            hop={"verdict": True, "state": "LIVE"},
            plan={"reasons": [], "result": "ALLOW"},
            breaker={"open": False},
        )
        self.assertTrue(v["agreed"])
        self.assertEqual(v["result"], "ALLOW")
        self.assertEqual(set(v["votes"].values()), {"ALLOW"})

    def test_split_votes_hold_and_do_not_upgrade(self):
        v = triple_vote.grade(
            hop={"verdict": True, "state": "LIVE"},
            plan={"reasons": ["premium_exceeds_authority"], "result": "BLOCK"},
            breaker={"open": False},
        )
        self.assertFalse(v["agreed"])
        self.assertEqual(v["votes"]["hop"], "ALLOW")
        self.assertEqual(v["votes"]["constraints"], "BLOCK")
        self.assertEqual(v["result"], "HOLD")


class RulesTests(unittest.TestCase):
    def setUp(self):
        p = Path(os.environ["GATE_RULES_PATH"])
        if p.exists():
            p.unlink()

    def test_preview_blocks_over_limit(self):
        rule = gate_rules.add_rule(name="cap", field="premium", op="gt", value=1000, action="BLOCK")
        out = gate_rules.preview({"premium": 5000}, [rule])
        self.assertEqual(out["action"], "BLOCK")
        self.assertEqual(len(out["hits"]), 1)


class SurfaceTests(unittest.TestCase):
    def setUp(self):
        self.client = app_mod.app.test_client()

    def test_chain_page(self):
        r = self.client.get("/chain")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"Signed receipts", r.data)
        api = self.client.get("/v1/chain")
        self.assertEqual(api.status_code, 200)
        self.assertEqual(api.get_json()["spec"], "gate-chain-explorer-v1")

    def test_rules_page_and_preview_api(self):
        self.assertEqual(self.client.get("/rules").status_code, 200)
        prev = self.client.post("/v1/gate-rules/preview", json={"premium": 1})
        self.assertEqual(prev.status_code, 200)
        self.assertIn(prev.get_json()["action"], ("ALLOW", "BLOCK", "HOLD"))

    def test_embed_widget(self):
        js = self.client.get("/embed/trust.js")
        self.assertEqual(js.status_code, 200)
        self.assertIn(b"GateTrustWidget", js.data)
        js_json = self.client.get("/embed/trust.json")
        self.assertEqual(js_json.status_code, 200)
        self.assertEqual(js_json.get_json()["spec"], "gate-trust-widget-v1")

    def test_arp_v0_1(self):
        spec = self.client.get("/.well-known/agent-receipt-protocol.json")
        self.assertEqual(spec.status_code, 200)
        body = spec.get_json()
        self.assertEqual(body["spec"], arp.SPEC)
        self.assertEqual(body["dated"], "2026-11-10")
        md = self.client.get("/spec/agent-receipt-protocol/v0.1.md")
        self.assertEqual(md.status_code, 200)
        self.assertIn(b"Agent Receipt Protocol v0.1", md.data)

    def test_badge_unsigned_without_event(self):
        r = self.client.get("/badge/verify.svg")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"unsigned", r.data)

    def test_mcp_lists_verify_receipt(self):
        body, status = mcp_server.handle_message(
            {"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
            public_url="https://example.test",
            call_tool=lambda n, a: {},
        )
        self.assertEqual(status, 200)
        names = {t["name"] for t in body["result"]["tools"]}
        self.assertIn("verify_receipt", names)

    def test_mcp_verify_missing_event(self):
        r = self.client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 9,
                "method": "tools/call",
                "params": {"name": "verify_receipt", "arguments": {"event_id": "nope"}},
            },
        )
        self.assertEqual(r.status_code, 200)
        payload = json.loads(r.get_json()["result"]["content"][0]["text"])
        self.assertEqual(payload["error"]["code"], "not_found")


if __name__ == "__main__":
    unittest.main()
