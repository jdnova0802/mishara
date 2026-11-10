"""PATRIOT Act § 314(b) share-pack mouth."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-314b.db")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import mouths  # noqa: E402
import app as gate_app  # noqa: E402


class Share314bMouthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = gate_app.app.test_client()

    def test_manifest_and_page(self):
        wk = self.client.get("/.well-known/314b-share.json")
        self.assertEqual(wk.status_code, 200)
        self.assertEqual(wk.get_json()["spec"], "gate-314b-share-v1")
        page = self.client.get("/314b-share")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"314(b)", page.data)
        gate = self.client.get("/.well-known/gate.json").get_json()
        self.assertIn("share_314b", gate)

    def test_shareable_packs_no_transmit(self):
        out = mouths.evaluate(
            "314b-share",
            {
                "sharer_is_bsa_fi": "yes",
                "sharer_314b_registered": "yes",
                "peer_314b_verified": "yes",
                "purpose_fraud_or_ml": "yes",
                "includes_sar_or_sar_existence": "no",
                "has_underlying_facts": "yes",
            },
        )
        self.assertEqual(out["word"], "SHAREABLE")
        pack = out["share_pack"]
        self.assertFalse(pack["gate_transmits_to_peers"])
        self.assertFalse(pack["gate_registers_for_you"])
        self.assertIn("deny_registry.payout_hash", " ".join(pack["suggested_payload_fields"]))
        self.assertTrue(out["signed_claim"]["claim_hash"])
        self.assertTrue(out["not_a_bounty"])

    def test_not_this_when_not_fi(self):
        out = mouths.evaluate(
            "314b-share",
            {
                "sharer_is_bsa_fi": "no",
                "sharer_314b_registered": "no",
                "peer_314b_verified": "no",
                "purpose_fraud_or_ml": "yes",
                "includes_sar_or_sar_existence": "no",
                "has_underlying_facts": "yes",
            },
        )
        self.assertEqual(out["word"], "NOT THIS")

    def test_hold_when_sar_in_packet(self):
        out = mouths.evaluate(
            "314b-share",
            {
                "sharer_is_bsa_fi": "yes",
                "sharer_314b_registered": "yes",
                "peer_314b_verified": "yes",
                "purpose_fraud_or_ml": "yes",
                "includes_sar_or_sar_existence": "yes",
                "has_underlying_facts": "yes",
            },
        )
        self.assertEqual(out["word"], "HOLD")
        self.assertIn("sar", out["share_pack"]["blocked_reason"])


if __name__ == "__main__":
    unittest.main()
