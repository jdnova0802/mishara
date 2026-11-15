"""Executor sandbox + report mapping. Local Gate only."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

from report import build_report, public_word  # noqa: E402
from sandbox import SandboxError, assert_executor_env_clean, assert_mouth_allowed  # noqa: E402
import executor  # noqa: E402


class SandboxTests(unittest.TestCase):
    def test_refuses_production_gate(self):
        with self.assertRaises(SandboxError) as ctx:
            assert_mouth_allowed("https://gate.velaru.xyz/demo/issuing/mouth")
        self.assertIn("production", str(ctx.exception).lower())

    def test_refuses_velaru_apex(self):
        with self.assertRaises(SandboxError):
            assert_mouth_allowed("https://velaru.xyz/demo/issuing/mouth")

    def test_allows_loopback(self):
        assert_mouth_allowed("http://127.0.0.1:5001/demo/issuing/mouth")
        assert_mouth_allowed("http://localhost:5001/demo/issuing/mouth")

    def test_refuses_stripe_keys_in_executor_env(self):
        with self.assertRaises(SandboxError):
            assert_executor_env_clean({"STRIPE_SECRET_KEY": "sk_live_x"})

    def test_public_word_maps_nogo_to_never(self):
        self.assertEqual(public_word("NO_GO"), "NEVER")
        self.assertEqual(public_word("GO"), "GO")
        self.assertEqual(public_word("HOLD"), "NEVER")


class ReportTests(unittest.TestCase):
    def test_never_pass_on_cap_breach(self):
        fixture = json.loads((HERE / "fixture.json").read_text(encoding="utf-8"))
        report = build_report(
            fixture=fixture,
            mouth_url="http://127.0.0.1:5001/demo/issuing/mouth",
            mouth_config={"money_real": False, "spec": "gate-issuing-mouth-v1"},
            body={
                "spec": "gate-issuing-mouth-v1",
                "approved": False,
                "decision": "NO_GO",
                "halt": True,
                "demo": True,
                "write_executed": False,
                "gate_holds_funds": False,
                "agent_id": "drill_agent",
                "gate": {
                    "evaluation_id": "evt_test",
                    "verify_url": "http://127.0.0.1:5001/v1/prefinality/verify",
                    "signals": ["amount_exceeds_cap"],
                    "receipt": "eyJ.test",
                    "fingerprint": "ab",
                    "message": "cap",
                },
            },
        )
        self.assertEqual(report["word"], "NEVER")
        self.assertTrue(report["pass"])
        self.assertFalse(report["money_real"])


class LiveLocalMouthTests(unittest.TestCase):
    """Hits an in-process Gate. Skips if Gate cannot import."""

    @classmethod
    def setUpClass(cls):
        os.environ.setdefault("GATE_DEV_MODE", "1")
        os.environ.setdefault("GATE_REQUIRE_RECEIPT_KEYS", "0")
        os.environ.pop("STRIPE_SECRET_KEY", None)
        os.environ.pop("STRIPE_ISSUING_WEBHOOK_SECRET", None)
        os.environ.pop("STRIPE_WEBHOOK_SECRET", None)
        os.environ.pop("GATE_RECEIPT_PRIVATE_KEY", None)
        try:
            from gate import app as gate_app
        except Exception as exc:  # pragma: no cover
            raise unittest.SkipTest(f"gate import failed: {exc}") from exc
        cls._app = gate_app.app
        cls._app.config["TESTING"] = True
        cls._server = None
        cls._thread = None
        cls.base = None
        try:
            from werkzeug.serving import make_server

            cls._server = make_server("127.0.0.1", 0, cls._app)
            cls.base = f"http://127.0.0.1:{cls._server.server_port}"
            cls._thread = threading.Thread(target=cls._server.serve_forever, daemon=True)
            cls._thread.start()
        except Exception as exc:  # pragma: no cover
            raise unittest.SkipTest(f"could not bind local Gate: {exc}") from exc

    @classmethod
    def tearDownClass(cls):
        if cls._server is not None:
            cls._server.shutdown()

    def test_fixture_never_against_local_mouth(self):
        out = Path(tempfile.mkdtemp())
        mouth = f"{self.base}/demo/issuing/mouth"
        report = executor.run(
            fixture_path=HERE / "fixture.json",
            mouth_url=mouth,
            out_dir=out,
        )
        self.assertEqual(report["word"], "NEVER")
        self.assertTrue(report["pass"])
        self.assertFalse(report["approved"])
        self.assertFalse(report["money_real"])
        self.assertTrue((out / "latest.html").is_file())
        html = (out / "latest.html").read_text(encoding="utf-8")
        self.assertIn(">NEVER<", html)
        self.assertNotIn("Buy now", html)


if __name__ == "__main__":
    unittest.main()
