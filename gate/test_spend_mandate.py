"""Bound spend mandate — prior write, then the issuing mouth evaluates it."""
from __future__ import annotations

import os
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_REQUIRE_RECEIPT_KEYS", "0")

from gate import app as gate_app  # noqa: E402
from gate import issuing_mouth as mouth  # noqa: E402
from gate import spend_mandate as mandate  # noqa: E402


def _eval_go(body: dict) -> dict:
    cap = body.get("mandate", {}).get("max_amount")
    amount = body.get("transfer", {}).get("amount")
    try:
        over = float(amount) > float(cap)
    except (TypeError, ValueError):
        over = True
    if over:
        return {"decision": "NO_GO", "signals": ["amount_exceeds_cap"], "message": "over"}
    return {"decision": "GO", "signals": [], "message": "within bound cap"}


class SpendMandateTests(unittest.TestCase):
    def setUp(self):
        self.client = gate_app.app.test_client()

    def test_demo_bind_and_stranger_read(self):
        res = self.client.post(
            "/demo/mandate/bind",
            json={
                "agent_id": "agent_mandate_1",
                "max_amount": "40.00",
                "expected_merchant": "Acme Supplies",
                "allowed_categories": ["computer_software_stores"],
                "ttl_seconds": 86400,
            },
        )
        self.assertEqual(res.status_code, 200, res.get_json())
        body = res.get_json()
        self.assertTrue(body["mandate_id"].startswith("gmd_"))
        self.assertEqual(body["status"], "bound")
        self.assertTrue(body["demo"])
        self.assertIn("signed_claim", body)
        self.assertEqual(body["terms"]["max_amount"], "40.00")

        read = self.client.get(f"/v1/mandate/{body['mandate_id']}")
        self.assertEqual(read.status_code, 200)
        self.assertEqual(read.get_json()["fingerprint"], body["fingerprint"])

        missing = self.client.get("/v1/mandate/gmd_0123456789abcdef")
        self.assertEqual(missing.status_code, 404)

    def test_mouth_uses_bound_cap_not_a_higher_metadata_edit(self):
        bound = mandate.bind(
            {
                "agent_id": "agent_mandate_2",
                "max_amount": "25.00",
                "expected_counterparty": "Acme Supplies",
            },
            demo=True,
        )
        auth = mouth.dogfood_authorization(
            amount_cents=3000,
            merchant="Acme Supplies",
            agent_id="agent_mandate_2",
            max_amount="500.00",
            expected_merchant="Acme Supplies",
            mandate_id=bound["mandate_id"],
        )
        out = mouth.decide(auth, evaluate_fn=_eval_go)
        self.assertFalse(out["approved"])
        self.assertEqual(out["decision"], "NO_GO")
        self.assertEqual(out["mandate_bind"]["signal"], "mandate_diverged")
        self.assertIn("max_amount", out["mandate_bind"]["diverged"])
        self.assertEqual(out["claim_scope"]["boundary"], "gate_spend_mandate")

    def test_matching_metadata_evaluates_bound_terms(self):
        bound = mandate.bind(
            {
                "agent_id": "agent_mandate_3",
                "max_amount": "50.00",
                "expected_counterparty": "Acme Supplies",
                "allowed_categories": ["computer_software_stores"],
            },
            demo=True,
        )
        auth = mouth.dogfood_authorization(
            amount_cents=2500,
            merchant="Acme Supplies",
            agent_id="agent_mandate_3",
            max_amount="50.00",
            expected_merchant="Acme Supplies",
            allowed_categories=["computer_software_stores"],
            mandate_id=bound["mandate_id"],
            card_id="ic_mandate_3",
        )
        seen = {}

        def _eval(body):
            seen["mandate"] = body["mandate"]
            return _eval_go(body)

        out = mouth.decide(auth, evaluate_fn=_eval)
        self.assertTrue(out["approved"], out)
        self.assertEqual(seen["mandate"]["max_amount"], "50.00")
        self.assertEqual(seen["mandate"]["mandate_id"], bound["mandate_id"])
        self.assertTrue(out["mandate_bind"]["applied"])
        stored = mandate.fetch(bound["mandate_id"])
        self.assertEqual(stored["card_id"], "ic_mandate_3")
        stripped = mouth.dogfood_authorization(
            amount_cents=2500,
            max_amount="500.00",
            card_id="ic_mandate_3",
        )
        stripped["card"]["metadata"].pop("agent_id", None)
        again = mouth.decide(stripped, evaluate_fn=_eval_go)
        self.assertFalse(again["approved"])
        self.assertEqual(again["mandate_bind"]["signal"], "mandate_omitted")

    def test_unknown_and_revoked_fail_closed(self):
        auth = mouth.dogfood_authorization(mandate_id="gmd_deadbeefdeadbeef")
        out = mouth.decide(auth, evaluate_fn=_eval_go)
        self.assertFalse(out["approved"])
        self.assertEqual(out["mandate_bind"]["signal"], "mandate_unknown")

        bound = mandate.bind({"agent_id": "agent_mandate_4", "max_amount": "10.00"}, demo=True)
        revoked = mandate.revoke(bound["mandate_id"])
        self.assertEqual(revoked["status"], "revoked")
        auth = mouth.dogfood_authorization(
            agent_id="agent_mandate_4",
            max_amount="10.00",
            mandate_id=bound["mandate_id"],
        )
        out = mouth.decide(auth, evaluate_fn=_eval_go)
        self.assertEqual(out["mandate_bind"]["signal"], "mandate_revoked")

    def test_omitted_id_fails_when_agent_is_already_bound(self):
        bound = mandate.bind(
            {"agent_id": "agent_mandate_omit", "max_amount": "25.00"},
            demo=True,
        )
        auth = mouth.dogfood_authorization(
            amount_cents=3000,
            agent_id="agent_mandate_omit",
            max_amount="500.00",
            card_id="ic_mandate_omit",
        )
        out = mouth.decide(auth, evaluate_fn=_eval_go)
        self.assertFalse(out["approved"])
        self.assertEqual(out["mandate_bind"]["signal"], "mandate_omitted")
        self.assertEqual(out["mandate_bind"]["mandate_id"], bound["mandate_id"])
        self.assertEqual(out["claim_scope"]["boundary"], "gate_spend_mandate")

    def test_card_id_at_bind_blocks_a_swipe_that_strips_both_ids(self):
        bound = mandate.bind(
            {
                "agent_id": "agent_mandate_card",
                "max_amount": "25.00",
                "card_id": "ic_mandate_card",
            },
            demo=True,
        )
        self.assertEqual(bound["card_id"], "ic_mandate_card")
        auth = mouth.dogfood_authorization(
            amount_cents=3000,
            agent_id="",
            max_amount="500.00",
            card_id="ic_mandate_card",
        )
        # dogfood always writes agent_id into metadata; blank must stay blank.
        auth["card"]["metadata"].pop("agent_id", None)
        out = mouth.decide(auth, evaluate_fn=_eval_go)
        self.assertFalse(out["approved"])
        self.assertEqual(out["mandate_bind"]["signal"], "mandate_omitted")
        self.assertEqual(out["mandate_bind"]["mandate_id"], bound["mandate_id"])

    def test_stripping_both_ids_on_an_unanchored_card_stays_metadata(self):
        mandate.bind(
            {"agent_id": "agent_mandate_loose", "max_amount": "25.00"},
            demo=True,
        )
        auth = mouth.dogfood_authorization(
            amount_cents=2500,
            max_amount="50.00",
            card_id="ic_never_stored",
        )
        auth["card"]["metadata"].pop("agent_id", None)
        auth["card"]["metadata"].pop("gate_mandate_id", None)
        out = mouth.decide(auth, evaluate_fn=_eval_go)
        self.assertTrue(out["approved"], out)
        self.assertIsNone(out["mandate_bind"])

    def test_metadata_only_path_unchanged(self):
        auth = mouth.dogfood_authorization(amount_cents=2500, max_amount="50.00")
        out = mouth.decide(auth, evaluate_fn=_eval_go)
        self.assertTrue(out["approved"])
        self.assertIsNone(out["mandate_bind"])

    def test_well_known(self):
        res = self.client.get("/.well-known/spend-mandate.json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["spec"], mandate.SPEC)
        self.assertEqual(res.get_json()["card_metadata_key"], "gate_mandate_id")
        self.assertIn("still_metadata_path", res.get_json()["enforcement"])
        self.assertIn("mandate_omitted", res.get_json()["enforcement"]["omission"])

    def test_bind_requires_a_cap(self):
        res = self.client.post("/demo/mandate/bind", json={"agent_id": "nobody"})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.get_json()["error"], "max_amount_or_daily_cap_required")


if __name__ == "__main__":
    unittest.main()
