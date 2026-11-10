"""Items 50–55 + CDPI 75–79."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-agent-bureau.db")
os.environ["GATE_AGENTS_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-agents.json")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import agent_bureau as bureau  # noqa: E402
import app as app_mod  # noqa: E402


class BureauLogicTests(unittest.TestCase):
    def test_did_persists_and_is_not_a_session(self):
        a = bureau.register_agent(public_key_b64="cHVibGljLWtleS1hYWFhYWFhYWE=", fuse_id="fuse_a", label="A")
        b = bureau.register_agent(public_key_b64="cHVibGljLWtleS1hYWFhYWFhYWE=", fuse_id="fuse_a")
        self.assertEqual(a["did"], b["did"])
        self.assertFalse(a["session"])
        self.assertTrue(a["did"].startswith("did:gate:"))
        other = bureau.register_agent(public_key_b64="cHVibGljLWtleS1iYmJiYmJiYmI=")
        self.assertNotEqual(a["did"], other["did"])

    def test_decay_freezes_while_disputed(self):
        self.assertAlmostEqual(bureau.decay_weight(90, disputed=False), 0.5)
        self.assertEqual(bureau.decay_weight(90, disputed=True), 1.0)

    def test_cdpi_is_not_static_100_without_resolutions(self):
        score = bureau.score_agent([{"id": "e1", "decision": "BLOCK", "created_at": "2026-11-01T00:00:00+00:00"}])
        self.assertIsNone(score["accuracy"])
        self.assertIsNone(score["composite"])
        self.assertFalse(score["static_100"])

    def test_closed_dispute_scores_accuracy_and_keeps_history(self):
        events = [
            {"id": "e1", "decision": "BLOCK", "created_at": "2026-11-01T00:00:00+00:00"},
            {"id": "e2", "decision": "BLOCK", "created_at": "2026-11-02T00:00:00+00:00"},
        ]
        d1 = bureau.file_dispute(event_id="e1", reason="wrong mark")
        d2 = bureau.file_dispute(event_id="e2", reason="also wrong")
        bureau.resolve_dispute(d1["id"], "OVERTURNED")
        bureau.resolve_dispute(d2["id"], "UPHELD")
        score = bureau.score_agent(events, bureau.list_disputes())
        self.assertEqual(score["accuracy"], 0.5)
        self.assertIsNotNone(score["composite"])
        self.assertFalse(any(d["history_erased"] for d in bureau.list_disputes()))

    def test_zk_and_registration_are_honest(self):
        self.assertFalse(bureau.zk_stub()["built"])
        spec = bureau.registration_spec()
        self.assertEqual(spec["adopters"], [])


class BureauFlaskTests(unittest.TestCase):
    def setUp(self):
        self.client = app_mod.app.test_client()

    def test_pages_200(self):
        for path in ("/agents", "/cdpi", "/disputes", "/zk", "/agent-registration"):
            self.assertEqual(self.client.get(path).status_code, 200, path)

    def test_register_and_lookup(self):
        r = self.client.post(
            "/v1/agents/register",
            json={"public_key_b64": "cHVibGljLWtleS1jY2NjY2NjY2M=", "fuse_id": "fuse_lookup"},
        )
        self.assertEqual(r.status_code, 201)
        did = r.get_json()["did"]
        rec = self.client.get("/v1/trust-record?did=" + did)
        self.assertEqual(rec.status_code, 200)
        body = rec.get_json()
        self.assertTrue(body["pay_per_query"])
        self.assertTrue(body["demo"])
        self.assertFalse(body["cdpi"]["static_100"])
        self.assertFalse(body["zk_linkage"]["built"])

    def test_dispute_api_keeps_row(self):
        r = self.client.post("/v1/disputes", json={"event_id": "evt_keep", "reason": "not me"})
        self.assertEqual(r.status_code, 201)
        self.assertFalse(r.get_json()["history_erased"])
        self.assertEqual(r.get_json()["status"], "OPEN")

    def test_zk_and_adopters_json(self):
        zk = self.client.get("/.well-known/zk-linkage.json").get_json()
        self.assertFalse(zk["built"])
        reg = self.client.get("/.well-known/agent-registration.json").get_json()
        self.assertEqual(reg["adopters"], [])


if __name__ == "__main__":
    unittest.main()
