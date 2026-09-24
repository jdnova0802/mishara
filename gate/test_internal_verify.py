"""Internal verify: SCVD battery + mouth verdicts + tonight's corrections."""
from __future__ import annotations

import base64
import json
import os
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest import mock

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(
    tempfile.gettempdir(), f"gate-internal-verify-{uuid.uuid4().hex}.db"
)
os.environ["GATE_X402_DEMO_PAYTO"] = "0x00000000000000000000000000000000000000aa"
os.environ.pop("RENDER_EXTERNAL_URL", None)
os.environ.pop("RENDER_EXTERNAL_HOSTNAME", None)

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import app as gate_app  # noqa: E402
import internal_verify as iv  # noqa: E402
import x402_challenge as x402_challenge_mod  # noqa: E402


class ScvdBatteryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_named_checks_match_scvd_crawler(self):
        r = self.client.get("/v1/prefinality/evaluate")
        report = iv.scvd_from_flask(r)
        names = [c["name"] for c in report["checks"]]
        self.assertEqual(report["verdict"], "ready")
        for required in (
            "status-402",
            "payment-required-header",
            "x402-version",
            "accepts",
            "bazaar-extension",
        ):
            self.assertIn(required, names, report)
            row = next(c for c in report["checks"] if c["name"] == required)
            self.assertTrue(row["ok"], row)

    def test_get_and_post_both_402(self):
        get = self.client.get("/v1/prefinality/evaluate")
        post = self.client.post("/v1/prefinality/evaluate", json={"rail": "x402"})
        self.assertEqual(get.status_code, 402)
        self.assertEqual(post.status_code, 402)
        self.assertEqual(iv.scvd_from_flask(get)["verdict"], "ready")
        self.assertEqual(iv.scvd_from_flask(post)["verdict"], "ready")

    def test_body_only_402_fails_header_check(self):
        class Fake:
            status_code = 402
            headers = {"Content-Type": "application/json"}

        report = iv.scvd_from_flask(Fake())
        header = next(c for c in report["checks"] if c["name"] == "payment-required-header")
        self.assertFalse(header["ok"])
        self.assertEqual(report["verdict"], "not_ready")

    def test_200_is_listed_but_functionally_absent(self):
        class Fake:
            status_code = 200
            headers = {}

        report = iv.scvd_from_flask(Fake())
        status = next(c for c in report["checks"] if c["name"] == "status-402")
        self.assertFalse(status["ok"])
        self.assertIn("functionally absent", status["detail"])

    def test_header_must_be_base64_json_not_body(self):
        payload = {
            "x402Version": 2,
            "accepts": [
                {
                    "scheme": "exact",
                    "network": "eip155:8453",
                    "amount": "2000",
                    "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
                    "payTo": "0x00000000000000000000000000000000000000aa",
                }
            ],
            "extensions": {"bazaar": {"info": {"input": {"type": "http"}}}},
        }
        encoded = base64.b64encode(json.dumps(payload).encode()).decode("ascii")

        class Fake:
            status_code = 402
            headers = {"PAYMENT-REQUIRED": encoded}

        self.assertEqual(iv.scvd_from_flask(Fake())["verdict"], "ready")


class MouthVerdictSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_every_live_mouth_returns_the_word(self):
        get, post, page = iv.flask_transport(self.client)
        rows = iv.mouth_verdicts(get, post, page)
        failed = [r for r in rows if not r.get("ok")]
        self.assertFalse(failed, failed)


class TonightCorrectionsTests(unittest.TestCase):
    def test_demo_payto_is_a_real_payto_env(self):
        self.assertIn("GATE_X402_DEMO_PAYTO", x402_challenge_mod._PAYTO_ENVS)
        self.assertEqual(tuple(x402_challenge_mod._PAYTO_ENVS), iv.PAYTO_ENVS)
        self.assertEqual(x402_challenge_mod.payto(), os.environ["GATE_X402_DEMO_PAYTO"])

    def test_puct_dockets_are_not_mixed(self):
        self.assertEqual(iv.PUCT["batch_zero_pgrr_145"], "59142")
        self.assertEqual(iv.PUCT["crusoe_ensign_sb6_net_metering"], "59220")
        self.assertNotEqual(
            iv.PUCT["batch_zero_pgrr_145"],
            iv.PUCT["crusoe_ensign_sb6_net_metering"],
        )

    def test_repo_does_not_call_59220_batch_zero(self):
        skip = {"test_internal_verify.py", "internal_verify.py"}
        bad = []
        for path in list(HERE.glob("*.py")) + list(HERE.glob("*.md")):
            if path.name in skip:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for i, line in enumerate(text.splitlines(), 1):
                low = line.lower()
                if "59220" in line and ("batch zero" in low or "pgrr 145" in low):
                    bad.append(f"{path.name}:{i}:{line.strip()}")
        self.assertEqual(bad, [])

    def test_401_when_payto_missing_is_the_bug_we_caught(self):
        with mock.patch.dict(
            os.environ,
            {"GATE_X402_PAYTO": "", "GATE_X402_PAY_TO": "", "GATE_X402_DEMO_PAYTO": ""},
            clear=False,
        ):
            self.assertIsNone(x402_challenge_mod.payto())
            client = gate_app.app.test_client()
            r = client.get("/v1/prefinality/evaluate")
            self.assertEqual(r.status_code, 401)
            report = iv.scvd_from_flask(r)
            self.assertEqual(report["verdict"], "not_ready")
            status = next(c for c in report["checks"] if c["name"] == "status-402")
            self.assertFalse(status["ok"])

    def test_citations_pinned(self):
        self.assertEqual(iv.CITATIONS["scenario_3"], "FIN-2016-A003")
        self.assertEqual(iv.CITATIONS["admt"], "11 CCR § 7200(b)")
        self.assertIn("up.codes", iv.CITATIONS["stair_source"])


if __name__ == "__main__":
    unittest.main()
