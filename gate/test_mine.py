"""Mine OS — self money machine tests."""
from __future__ import annotations

import os
import tempfile
import unittest
import uuid
from unittest import mock

os.environ["GATE_DB_PATH"] = os.path.join(
    tempfile.gettempdir(), f"gate-mine-{uuid.uuid4().hex}.db"
)
os.environ["GATE_DEV_MODE"] = "1"

import app as gate_app  # noqa: E402
from mine import risk as mine_risk  # noqa: E402
from mine import spread as mine_spread  # noqa: E402
import mine as mine_mod  # noqa: E402


class MineOsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_mine_catalog(self):
        r = self.client.get("/.well-known/mine.json")
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(body.get("spec"), mine_mod.SPEC)
        ids = [m["id"] for m in body.get("mines") or []]
        self.assertIn("liquidation", ids)
        self.assertIn("funding", ids)
        self.assertIn("commerce_spread", ids)

    def test_clear_gate_refuses_zero_edge(self):
        out = mine_mod.clear_gate(
            mine_id="funding",
            notional_usd=10000,
            expected_edge_bps=0,
            max_loss_usd=200,
            public_url="https://example.test",
        )
        self.assertEqual(out["decision"], "NO_GO")
        self.assertIn("nonpositive_edge", out["signals"])

    def test_risk_passport_liquidatable(self):
        card = mine_risk.passport(collateral_usd=10000, debt_usd=12000, liquidation_threshold=0.825)
        self.assertEqual(card["status"], "LIQUIDATABLE")
        self.assertTrue(card["liquidatable"])

    def test_spread_plan_hf(self):
        plan = mine_spread.plan(
            sku_id="hf_risk_passport",
            monthly_calls=10_000,
            public_url="https://example.test",
        )
        self.assertTrue(plan["ok"])
        self.assertGreater(plan["projected_gross_margin_usd"], 0)

    def test_risk_402_when_payto(self):
        payto = "0x00000000000000000000000000000000000000dd"
        with mock.patch.object(gate_app.x402_challenge_mod, "payto", return_value=payto):
            with mock.patch.object(gate_app.x402_challenge_mod, "payto_configured", return_value=True):
                r = self.client.post(
                    "/api/x402/risk",
                    json={"collateral_usd": 10000, "debt_usd": 9000},
                )
        self.assertEqual(r.status_code, 402)
        accepts = r.get_json().get("accepts") or []
        self.assertEqual(accepts[0].get("amount"), "50000")

    def test_risk_delivers_on_verified(self):
        with mock.patch.object(
            gate_app.x402_challenge_mod,
            "payment_verified",
            return_value={"ok": True, "reason": "test", "paid": True},
        ):
            r = self.client.post(
                "/api/x402/risk",
                json={"collateral_usd": 10000, "debt_usd": 5000},
                headers={"X-Payment": "test"},
            )
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(body.get("spec"), "gate-mine-risk-passport-v1")
        self.assertIn(body.get("status"), ("HEALTHY", "ELEVATED", "CRITICAL", "LIQUIDATABLE", "NO_DEBT"))

    def test_funding_scan_mocked(self):
        fake = {"lastFundingRate": "0.0004", "markPrice": "60000"}
        # Patch where the function lives — app imports mine_funding_mod
        target = gate_app.mine_funding_mod._fetch_binance_premium
        with mock.patch.object(
            gate_app.mine_funding_mod, "_fetch_binance_premium", return_value=fake
        ) as patched:
            self.assertIs(patched, gate_app.mine_funding_mod._fetch_binance_premium)
            r = self.client.get(
                "/v1/mine/funding/scan",
                query_string={"notional_usd": "10000", "max_loss_usd": "200"},
            )
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertTrue(body.get("ok"))
        # 0.0004 = 4 bps/8h — below 25 bps enter → stand_down
        self.assertEqual(body.get("proposed_action"), "stand_down")
        self.assertAlmostEqual(body.get("rate_bps_8h"), 4.0, places=2)
        self.assertIn("gate", body)

    def test_funding_scan_open_when_hot(self):
        fake = {"lastFundingRate": "0.0010", "markPrice": "60000"}  # 10 bps... still < 25
        hot = {"lastFundingRate": "0.0030", "markPrice": "60000"}  # 30 bps ≥ 25
        with mock.patch.object(
            gate_app.mine_funding_mod, "_fetch_binance_premium", return_value=hot
        ):
            r = self.client.get("/v1/mine/funding/scan")
        body = r.get_json()
        self.assertTrue(body.get("ok"))
        self.assertEqual(body.get("proposed_action"), "open_short_perp_long_spot")

    def test_x402_catalog_lists_risk(self):
        cat = self.client.get("/.well-known/x402.json")
        resources = [x.get("resource") for x in cat.get_json().get("resources", [])]
        self.assertTrue(any("/api/x402/risk" in (u or "") for u in resources))

    def test_health_lists_mine(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        self.assertIn("mine", r.get_json())


if __name__ == "__main__":
    unittest.main()
