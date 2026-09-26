"""Issuing auth mouth — Stripe agent cards → Gate Clear."""
from __future__ import annotations

import os
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_REQUIRE_RECEIPT_KEYS", "0")

from gate import app as gate_app  # noqa: E402
from gate import issuing_mouth as mouth  # noqa: E402
from gate import prefinality as pf  # noqa: E402


class IssuingMouthTests(unittest.TestCase):
    def setUp(self):
        self.client = gate_app.app.test_client()
        self._env_keys = (
            "GATE_ISSUING_ENABLED",
            "STRIPE_SECRET_KEY",
            "STRIPE_ISSUING_WEBHOOK_SECRET",
            "STRIPE_WEBHOOK_SECRET",
        )
        self._env_prev = {k: os.environ.get(k) for k in self._env_keys}
        # Unsigned webhook dogfood path needs no issuing webhook secret
        for k in ("STRIPE_ISSUING_WEBHOOK_SECRET", "STRIPE_WEBHOOK_SECRET"):
            os.environ.pop(k, None)

    def tearDown(self):
        for k, v in self._env_prev.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_issuing_is_prefinality_rail(self):
        self.assertIn("issuing", pf.RAILS)
        m = pf.manifest("https://gate.example")
        ids = [r["id"] for r in m["rails"]]
        self.assertIn("issuing", ids)

    def test_authorization_maps_cents_and_mandate(self):
        auth = mouth.dogfood_authorization(
            amount_cents=4200,
            merchant="Acme Supplies",
            agent_id="agent_a",
            max_amount="50.00",
            expected_merchant="Acme Supplies",
        )
        body = mouth.authorization_to_evaluate_body(auth)
        self.assertEqual(body["rail"], "issuing")
        self.assertEqual(body["transfer"]["amount"], "42.00")
        self.assertEqual(body["transfer"]["counterparty"], "Acme Supplies")
        self.assertEqual(body["mandate"]["agent_id"], "agent_a")
        self.assertEqual(body["mandate"]["max_amount"], "50.00")
        self.assertEqual(body["mandate"]["expected_counterparty"], "Acme Supplies")

    def test_decide_go_within_timeout(self):
        auth = mouth.dogfood_authorization(amount_cents=2500, max_amount="50.00")

        def evaluate_fn(body):
            return pf.evaluate(body, public_url="https://gate.example")

        out = mouth.decide(auth, evaluate_fn=evaluate_fn)
        self.assertTrue(out["approved"])
        self.assertEqual(out["decision"], "GO")
        self.assertTrue(out["within_stripe_timeout"])
        self.assertEqual(out["stripe_response"], {"approved": True})
        self.assertFalse(out["gate_holds_funds"])

    def test_decide_never_on_cap_breach(self):
        auth = mouth.dogfood_authorization(force_breach=True, max_amount="50.00")

        def evaluate_fn(body):
            return pf.evaluate(body, public_url="https://gate.example")

        out = mouth.decide(auth, evaluate_fn=evaluate_fn)
        self.assertFalse(out["approved"])
        self.assertEqual(out["decision"], "NO_GO")
        self.assertIn("amount_exceeds_cap", out["gate"]["signals"])
        self.assertEqual(out["stripe_response"], {"approved": False})

    def test_demo_endpoint_go(self):
        r = self.client.post(
            "/demo/issuing/mouth",
            json={"amount_cents": 1200, "max_amount": "50.00", "agent_id": "t1"},
        )
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertTrue(body["approved"])
        self.assertTrue(body["demo"])
        self.assertEqual(body["spec"], "gate-issuing-mouth-v1")

    def test_demo_endpoint_never(self):
        r = self.client.post("/demo/issuing/mouth", json={"force_breach": True})
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertFalse(body["approved"])
        self.assertEqual(body["decision"], "NO_GO")

    def test_well_known_and_page(self):
        m = self.client.get("/.well-known/issuing-mouth.json")
        self.assertEqual(m.status_code, 200)
        self.assertEqual(m.get_json()["spec"], "gate-issuing-mouth-v1")
        page = self.client.get("/issuing-mouth")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"Auth mouth", page.data)

    def test_health_lists_issuing_mouth(self):
        h = self.client.get("/health")
        self.assertEqual(h.status_code, 200)
        body = h.get_json()
        self.assertIn("issuing_mouth", body)
        self.assertIn("dogfood", body["issuing_mouth"])

    def test_webhook_dev_mode_unsigned(self):
        auth = mouth.dogfood_authorization(amount_cents=900, max_amount="50.00")
        r = self.client.post("/v1/issuing/authorization", json=auth)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json(), {"approved": True})

    def test_readiness_not_spendable_without_float(self):
        class _Bal:
            issuing = {"available": [{"amount": 0, "currency": "usd"}]}

        class _List:
            def __init__(self, n):
                self.data = [{"id": f"x{i}", "status": "active"} for i in range(n)]

        class _Issuing:
            class Cardholder:
                @staticmethod
                def list(limit=100):
                    return _List(1)

            class Card:
                @staticmethod
                def list(limit=100):
                    return _List(1)

        class _Stripe:
            class Balance:
                @staticmethod
                def retrieve():
                    return _Bal()

            issuing = _Issuing()

            class Topup:
                @staticmethod
                def list(limit=20):
                    return _List(0)

        os.environ["GATE_ISSUING_ENABLED"] = "1"
        os.environ["STRIPE_SECRET_KEY"] = "sk_test_x"
        os.environ["STRIPE_ISSUING_WEBHOOK_SECRET"] = "whsec_x"
        out = mouth.readiness(stripe_mod=_Stripe)
        self.assertFalse(out["spendable"])
        self.assertEqual(out["steps"]["issuing_available_cents"], 0)
        self.assertTrue(any("Add funds" in s for s in out["next"]))

    def test_readiness_spendable_when_float_and_card(self):
        class _Bal:
            issuing = {"available": [{"amount": 500, "currency": "usd"}]}

        class _List:
            def __init__(self, rows):
                self.data = rows

        class _Issuing:
            class Cardholder:
                @staticmethod
                def list(limit=100):
                    return _List([{"id": "ich_1"}])

            class Card:
                @staticmethod
                def list(limit=100):
                    return _List([{"id": "ic_1", "status": "active"}])

        class _Stripe:
            class Balance:
                @staticmethod
                def retrieve():
                    return _Bal()

            issuing = _Issuing()

            class Topup:
                @staticmethod
                def list(limit=20):
                    return _List([])

        os.environ["GATE_ISSUING_ENABLED"] = "1"
        os.environ["STRIPE_SECRET_KEY"] = "sk_test_x"
        os.environ["STRIPE_ISSUING_WEBHOOK_SECRET"] = "whsec_x"
        out = mouth.readiness(stripe_mod=_Stripe)
        self.assertTrue(out["spendable"])
        self.assertEqual(out["steps"]["cards_active"], 1)

    def test_ops_issuing_status_dev_mode(self):
        r = self.client.get("/ops/issuing-status")
        # GATE_DEV_MODE=1 → _ops_authorized without token
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(body["spec"], "gate-issuing-readiness-v1")
        self.assertIn("spendable", body)
        self.assertIn("ops_readiness", mouth.manifest("https://gate.example"))

    def test_workflow_category_allow_passes_to_clear(self):
        auth = mouth.dogfood_authorization(
            amount_cents=2500,
            max_amount="50.00",
            merchant_category="computer_software_stores",
            allowed_categories=["computer_software_stores", "electronic_sales"],
            platform_allowed_categories=["computer_software_stores"],
            job_id="job_wf_1",
        )
        check = mouth.workflow_category_check(auth)
        self.assertTrue(check["configured"])
        self.assertTrue(check["ok"])
        self.assertEqual(check["spec"], mouth.WORKFLOW_SPEC)
        self.assertIsNone(check["signal"])

        called = {"n": 0}

        def evaluate_fn(body):
            called["n"] += 1
            self.assertEqual(
                body["mandate"]["allowed_categories"],
                ["computer_software_stores", "electronic_sales"],
            )
            self.assertEqual(body["mandate"]["job_id"], "job_wf_1")
            self.assertEqual(body["context"]["workflow_lock"], mouth.WORKFLOW_SPEC)
            return pf.evaluate(body, public_url="https://gate.example")

        out = mouth.decide(auth, evaluate_fn=evaluate_fn)
        self.assertEqual(called["n"], 1)
        self.assertTrue(out["approved"])
        self.assertTrue(out["workflow_lock"]["ok"])
        self.assertEqual(out["decision"], "GO")

    def test_workflow_category_deny_before_clear(self):
        auth = mouth.dogfood_authorization(
            amount_cents=2500,
            max_amount="50.00",
            merchant_category="eating_places_restaurants",
            allowed_categories=["automated_fuel_dispensers"],
            platform_allowed_categories=["automated_fuel_dispensers", "eating_places_restaurants"],
        )
        called = {"n": 0}

        def evaluate_fn(body):
            called["n"] += 1
            return {"decision": "GO"}  # must never run

        out = mouth.decide(auth, evaluate_fn=evaluate_fn)
        self.assertEqual(called["n"], 0)
        self.assertFalse(out["approved"])
        self.assertEqual(out["decision"], "NO_GO")
        self.assertEqual(out["stripe_response"], {"approved": False})
        self.assertEqual(out["workflow_lock"]["signal"], "workflow_category_denied")
        self.assertIn("workflow_category_denied", out["gate"]["signals"])
        self.assertIn("claim_scope", out)
        scope = out["claim_scope"]
        self.assertEqual(scope["boundary"], "gate_issuing_workflow_category_lock")
        self.assertTrue(scope["not_global"])
        self.assertTrue(scope.get("mcc_is_not_cart"))
        self.assertIn("signed_claim", out)
        self.assertEqual(
            out["signed_claim"]["canonical_claim"]["claim_scope"]["boundary"],
            "gate_issuing_workflow_category_lock",
        )

    def test_workflow_category_missing_fail_closed(self):
        auth = mouth.dogfood_authorization(
            amount_cents=1000,
            max_amount="50.00",
            merchant_category="",
            allowed_categories=["computer_software_stores"],
        )
        # strip category so observed is empty
        auth["merchant_data"]["category"] = ""
        auth["merchant_data"]["category_code"] = ""

        def evaluate_fn(body):
            self.fail("Clear must not run when category missing under allowlist")

        out = mouth.decide(auth, evaluate_fn=evaluate_fn)
        self.assertFalse(out["approved"])
        self.assertEqual(out["workflow_lock"]["signal"], "workflow_category_missing")
        self.assertEqual(out["claim_scope"]["boundary"], "gate_issuing_workflow_category_lock")

    def test_no_allowlist_skips_workflow_lock(self):
        auth = mouth.dogfood_authorization(amount_cents=2500, max_amount="50.00")
        check = mouth.workflow_category_check(auth)
        self.assertFalse(check["configured"])
        self.assertTrue(check["ok"])

        def evaluate_fn(body):
            return pf.evaluate(body, public_url="https://gate.example")

        out = mouth.decide(auth, evaluate_fn=evaluate_fn)
        self.assertTrue(out["approved"])
        self.assertFalse(out["workflow_lock"]["configured"])

    def test_manifest_documents_workflow_lock(self):
        m = mouth.manifest("https://gate.example")
        self.assertEqual(m["workflow_lock"]["spec"], mouth.WORKFLOW_SPEC)
        self.assertIn("allowed_categories", m["workflow_lock"]["metadata_keys"])
        cfg = mouth.config()
        self.assertIn("gate_workflow_lock", cfg["layers"])
        self.assertIn("not_sku_grade", cfg["layers"])

    def test_demo_workflow_category_deny(self):
        r = self.client.post(
            "/demo/issuing/mouth",
            json={
                "amount_cents": 1200,
                "max_amount": "50.00",
                "merchant_category": "eating_places_restaurants",
                "allowed_categories": ["automated_fuel_dispensers"],
            },
        )
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertFalse(body["approved"])
        self.assertTrue(body["workflow_lock"]["configured"])
        self.assertEqual(body["workflow_lock"]["signal"], "workflow_category_denied")
        self.assertEqual(
            body["claim_scope"]["boundary"], "gate_issuing_workflow_category_lock"
        )


if __name__ == "__main__":
    unittest.main()
