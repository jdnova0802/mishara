"""x402 agent payment demo tests."""
from __future__ import annotations

import os
import unittest

try:
    from gate.app import app
    from gate import x402_challenge as x402
except ImportError:
    from app import app  # type: ignore
    import x402_challenge as x402  # type: ignore


class X402AgentDemoTests(unittest.TestCase):
    def setUp(self):
        self.c = app.test_client()
        os.environ["GATE_X402_DEMO"] = "1"
        os.environ.pop("GATE_X402_PAYTO", None)
        os.environ.pop("GATE_X402_PAY_TO", None)

    def tearDown(self):
        os.environ.pop("GATE_X402_DEMO", None)

    def test_demo_payto_marks_configured(self):
        dbg = x402.payto_debug()
        self.assertTrue(dbg["configured"])
        self.assertTrue(dbg["demo"])
        self.assertTrue(x402.payto_configured())

    def test_agent_pay_go_when_demo_configured(self):
        r = self.c.post(
            "/demo/x402/agent-pay",
            json={
                "agent_id": "demo-agent-01",
                "amount_usdc": "0.25",
                "destination": "0x0000000000000000000000000000000000000001",
            },
        )
        self.assertEqual(r.status_code, 200, r.get_data(as_text=True))
        body = r.get_json()
        self.assertEqual(body["decision"], "GO")
        self.assertIn("receipt_id", body)
        self.assertIn("fingerprint", body)
        self.assertIn("x402_challenge", body)

    def test_agent_pay_no_go_over_cap(self):
        r = self.c.post(
            "/demo/x402/agent-pay",
            json={
                "agent_id": "demo-agent-01",
                "amount_usdc": "50.00",
                "destination": "0x0000000000000000000000000000000000000001",
            },
        )
        self.assertEqual(r.status_code, 403)
        body = r.get_json()
        self.assertEqual(body["decision"], "NO_GO")
        self.assertIn("amount_over_mandate_cap", body["reasons"])

    def test_page_renders(self):
        r = self.c.get("/demo/x402/agent-pay")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"Agent attempts payment", r.data)


if __name__ == "__main__":
    unittest.main()
