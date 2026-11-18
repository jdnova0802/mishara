"""Caller-owned live write: real halt on deny, no PAS backdoor, /v1/act default unchanged."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from unittest import mock

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-owned-write.db")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import owned_write  # noqa: E402
import app as gate_app  # noqa: E402


LIVE_HOP = {
    "ok": True,
    "verdict": True,
    "state": "LIVE",
    "halt": False,
    "verify_url": "https://velaru.xyz/verify?r=owned",
}
DEAD_HOP = {
    "ok": True,
    "verdict": False,
    "state": "DEAD",
    "halt": True,
    "verify_url": "https://velaru.xyz/verify?r=owned-dead",
}


class ClassifyTests(unittest.TestCase):
    def test_policycenter_host_blocked(self):
        out = owned_write.classify_target(
            "https://pc.guidewire.com/jobs/bind",
            allow_loopback=False,
        )
        self.assertFalse(out["ok"])
        self.assertEqual(out["code"], "pas_write_forbidden")

    def test_duckcreek_path_blocked(self):
        out = owned_write.classify_target(
            "https://example.com/v1/pas/duckcreek/pre-bind",
            allow_loopback=False,
        )
        self.assertFalse(out["ok"])
        self.assertEqual(out["code"], "pas_write_forbidden")

    def test_http_non_loopback_blocked(self):
        out = owned_write.classify_target("http://example.com/payout", allow_loopback=True)
        self.assertFalse(out["ok"])


class OwnedActTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import db as gate_db

        gate_db.init_db()
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_clearance_only_unchanged_without_write_url(self):
        with mock.patch.object(gate_app, "velaru_fuse", return_value=(LIVE_HOP, 200, {})):
            hop, status, extra = gate_app.run_welded_act("fuse_velaru_drill", "payout")
        self.assertEqual(status, 200)
        self.assertTrue(hop["acted"])
        self.assertFalse(hop["write_executed"])
        self.assertTrue(hop["clearance_only"])
        self.assertEqual(extra.get("X-Gate-Write-Executed"), "0")

    def test_deny_does_not_invoke(self):
        post = mock.Mock()
        with mock.patch.object(gate_app, "velaru_fuse", return_value=(DEAD_HOP, 200, {})):
            with mock.patch.object(owned_write, "invoke", wraps=owned_write.invoke) as inv:
                with mock.patch("requests.post", post):
                    hop, status, extra = gate_app.run_welded_act(
                        "fuse_velaru_drill",
                        "payout",
                        write_url="http://127.0.0.1:9/payout",
                        exclusive_owned=True,
                        allow_invoke=True,
                    )
        self.assertFalse(hop.get("acted"))
        self.assertFalse(hop.get("write_executed"))
        self.assertFalse(hop.get("write_invoked"))
        post.assert_not_called()
        inv.assert_not_called()
        self.assertEqual(extra.get("X-Gate-Write-Executed"), "0")
        self.assertIn("bound_answer", hop)

    def test_allow_invokes_owned_function(self):
        resp = mock.Mock(status_code=204)
        with mock.patch.object(gate_app, "velaru_fuse", return_value=(LIVE_HOP, 200, {})):
            with mock.patch("requests.post", return_value=resp) as post:
                hop, status, extra = gate_app.run_welded_act(
                    "fuse_velaru_drill",
                    "payout",
                    write_url="http://127.0.0.1:9/payout",
                    exclusive_owned=True,
                    allow_invoke=True,
                )
        self.assertEqual(status, 200)
        self.assertTrue(hop["acted"])
        self.assertTrue(hop["write_invoked"])
        self.assertTrue(hop["write_executed"])
        self.assertFalse(hop["their_production"])
        self.assertFalse(hop["clearance_only"])
        self.assertEqual(extra.get("X-Gate-Write-Executed"), "1")
        post.assert_called_once()
        self.assertIn("bound_answer", hop)

    def test_pas_url_refused_without_hop(self):
        fuse = mock.Mock()
        with mock.patch.object(gate_app, "velaru_fuse", fuse):
            hop, status, _extra = gate_app.run_welded_act(
                "fuse_velaru_drill",
                "bind",
                write_url="https://tenant.policycenter.guidewire.com/job/bind",
                exclusive_owned=True,
                allow_invoke=True,
            )
        self.assertEqual(status, 400)
        self.assertTrue(hop["pas_write_forbidden"])
        self.assertFalse(hop["write_executed"])
        fuse.assert_not_called()

    def test_missing_exclusive_flag_refused(self):
        fuse = mock.Mock()
        with mock.patch.object(gate_app, "velaru_fuse", fuse):
            hop, status, _extra = gate_app.run_welded_act(
                "fuse_velaru_drill",
                "payout",
                write_url="http://127.0.0.1:9/payout",
                exclusive_owned=False,
                allow_invoke=True,
            )
        self.assertEqual(status, 400)
        self.assertEqual(hop["error"]["code"], "exclusive_owned_required")
        fuse.assert_not_called()

    def test_demo_rejects_write_url(self):
        r = self.client.post(
            "/demo/act",
            json={
                "fuse_id": "fuse_velaru_drill",
                "action": "payout",
                "write_url": "http://127.0.0.1:9/payout",
                "exclusive_owned": True,
            },
        )
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.get_json()["error"]["code"], "owned_write_key_required")

    def test_well_known_owned_write(self):
        r = self.client.get("/.well-known/owned-write.json")
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(body["spec"], "gate-owned-write-v1")
        self.assertTrue(body["demo_refuses_invoke"])
        self.assertIn("Does not flip their_production", body["not"])


if __name__ == "__main__":
    unittest.main()
