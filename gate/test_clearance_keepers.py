"""Clearance keepers — Gate-shaped mining tests."""
from __future__ import annotations

import os
import tempfile
import unittest
import uuid

# Isolate keeper DB before importing modules that read GATE_DB_PATH.
_TEST_DB = os.path.join(tempfile.gettempdir(), f"gate-keepers-test-{uuid.uuid4().hex}.db")
os.environ["GATE_DB_PATH"] = _TEST_DB
os.environ["GATE_DEV_MODE"] = "1"

import clearance_keepers as ck  # noqa: E402
import app as gate_app  # noqa: E402


PAYTO = "0x00000000000000000000000000000000000000aa"
WRONG = "0x00000000000000000000000000000000000000bb"


class ClearanceKeepersUnitTests(unittest.TestCase):
    def test_dogfood_drill_pays_keeper(self):
        out = ck.dogfood_drill(keeper_id="unit_keeper")
        self.assertFalse(out["money_real"])
        self.assertFalse(out["gate_holds_funds"])
        self.assertTrue(out["liquidate"]["ok"])
        self.assertEqual(out["liquidate"]["word"], "LIQUIDATED")
        self.assertEqual(out["liquidate"]["bounty"], "5")
        self.assertFalse(out["liquidate"]["money_real"])
        self.assertIn("execution_packet", out["liquidate"])
        self.assertEqual(out["liquidate"]["residual_to_principal"], "95")
        self.assertEqual(out["liquidate"]["position"]["status"], "LIQUIDATED")

    def test_foreign_custody_catalog_and_onchain_binding(self):
        import foreign_custody as fc

        cat = fc.catalog()
        self.assertFalse(cat["doctrine"]["demo_is_money"])
        self.assertFalse(cat["doctrine"]["gate_holds_funds"])
        rank = cat["massive_ingress"]
        self.assertEqual(rank[0]["venue"], "onchain_usdc")
        self.assertFalse(rank[0]["money_can_enter_now"])  # no env deploy yet

        opened = ck.open_position(
            principal_id="p_onchain",
            escrow_amount="10",
            mandate={"max_amount": "1.00", "expected_payto": PAYTO},
            custody={
                "venue": "onchain_usdc",
                "venue_ref": "0x0000000000000000000000000000000000000esc",
                "escrow_id": "escrow_demo_1",
            },
        )
        # Without GATE_ESCROW_* env, money_real stays false even if venue named onchain
        self.assertTrue(opened["ok"])
        self.assertFalse(opened["money_real"])
        self.assertFalse(opened["gate_holds_funds"])
        self.assertEqual(opened["position"]["custody"]["venue"], "onchain_usdc")

    def test_open_observe_scan_liquidate_race(self):
        opened = ck.open_position(
            principal_id="p1",
            agent_id="a1",
            escrow_amount="50",
            bounty_bps=1000,
            mandate={"max_amount": "1.00", "expected_payto": PAYTO, "agent_id": "a1"},
        )
        self.assertTrue(opened["ok"])
        pid = opened["position"]["position_id"]

        # Valid GO-shaped transfer does not liquidate.
        ok_obs = ck.observe(
            position_id=pid,
            executed=True,
            transfer={"amount": "0.50", "currency": "USDC", "counterparty": PAYTO},
        )
        self.assertTrue(ok_obs["ok"])
        self.assertFalse(ok_obs["liquidatable"])
        self.assertEqual(ok_obs["position"]["status"], "OPEN")

        bad = ck.observe(
            position_id=pid,
            executed=True,
            transfer={"amount": "9.00", "currency": "USDC", "counterparty": WRONG},
        )
        self.assertTrue(bad["ok"])
        self.assertTrue(bad["liquidatable"])
        self.assertEqual(bad["position"]["status"], "BREACHED")
        self.assertIn(bad["verdict"]["decision"], ("NO_GO", "HOLD"))

        mempool = ck.scan()
        self.assertGreaterEqual(mempool["count"], 1)
        ids = {x["position_id"] for x in mempool["liquidatable"]}
        self.assertIn(pid, ids)

        first = ck.liquidate(position_id=pid, keeper_id="keeper_a")
        self.assertTrue(first["ok"])
        self.assertEqual(first["bounty"], "5")  # 10% of 50

        second = ck.liquidate(position_id=pid, keeper_id="keeper_b")
        self.assertFalse(second["ok"])
        self.assertEqual(second["error"], "already_liquidated")
        self.assertEqual(second["winner"], "keeper_a")

    def test_release_on_clear_no_bounty(self):
        opened = ck.open_position(
            principal_id="p2",
            escrow_amount="20",
            mandate={"max_amount": "5.00", "expected_payto": PAYTO},
        )
        pid = opened["position"]["position_id"]
        released = ck.release_on_clear(
            position_id=pid,
            transfer={"amount": "2.00", "currency": "USDC", "counterparty": PAYTO},
        )
        self.assertTrue(released["ok"])
        self.assertEqual(released["word"], "RELEASED")
        self.assertEqual(released["position"]["status"], "RELEASED")

    def test_cannot_liquidate_without_breach(self):
        opened = ck.open_position(
            principal_id="p3",
            escrow_amount="10",
            mandate={"max_amount": "5.00", "expected_payto": PAYTO},
        )
        pid = opened["position"]["position_id"]
        fail = ck.liquidate(position_id=pid, keeper_id="k")
        self.assertFalse(fail["ok"])
        self.assertEqual(fail["error"], "no_breach_evidence")


class ClearanceKeepersHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_manifest_page_and_dogfood(self):
        man = self.client.get("/.well-known/clearance-keepers.json")
        self.assertEqual(man.status_code, 200)
        body = man.get_json()
        self.assertEqual(body["spec"], "gate-clearance-keepers-v1")
        self.assertIn("mining", body)

        page = self.client.get("/keepers")
        self.assertEqual(page.status_code, 200)
        html = page.get_data(as_text=True)
        self.assertIn("Keepers", html)
        self.assertIn("dogfood", html.lower())

        gate = self.client.get("/.well-known/gate.json").get_json()
        self.assertIn("keepers", gate)
        self.assertIn("keepers_json", gate)

        drill = self.client.post("/demo/keepers/dogfood", json={"keeper_id": "http_keeper"})
        self.assertEqual(drill.status_code, 200)
        payload = drill.get_json()
        self.assertTrue(payload["liquidate"]["ok"])
        self.assertFalse(payload["money_real"])
        self.assertEqual(payload["liquidate"]["bounty"], "5")

        fc = self.client.get("/.well-known/foreign-custody.json")
        self.assertEqual(fc.status_code, 200)
        self.assertEqual(fc.get_json()["spec"], "gate-foreign-custody-v1")
        self.assertFalse(fc.get_json()["doctrine"]["demo_is_money"])

    def test_http_open_scan_liquidate(self):
        opened = self.client.post(
            "/demo/keepers/open",
            json={
                "principal_id": "http_p",
                "escrow": "40",
                "bounty_bps": 500,
                "mandate": {
                    "agent_id": "http_agent",
                    "max_amount": "1.00",
                    "expected_payto": PAYTO,
                },
            },
        )
        self.assertEqual(opened.status_code, 200)
        pid = opened.get_json()["position"]["position_id"]

        obs = self.client.post(
            "/demo/keepers/observe",
            json={
                "position_id": pid,
                "executed": True,
                "transfer": {
                    "amount": "8.00",
                    "currency": "USDC",
                    "counterparty": WRONG,
                },
            },
        )
        self.assertEqual(obs.status_code, 200)
        self.assertTrue(obs.get_json()["liquidatable"])

        scan = self.client.get("/demo/keepers/scan").get_json()
        self.assertTrue(any(x["position_id"] == pid for x in scan["liquidatable"]))

        liq = self.client.post(
            "/demo/keepers/liquidate",
            json={"position_id": pid, "keeper_id": "http_k"},
        )
        self.assertEqual(liq.status_code, 200)
        self.assertTrue(liq.get_json()["ok"])
        self.assertEqual(liq.get_json()["bounty"], "2")


if __name__ == "__main__":
    unittest.main()
