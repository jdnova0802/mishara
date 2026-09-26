"""Regulator adjacency page — stranger verify + NAIC/HMT mapping."""
from __future__ import annotations

import base64
import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret-regulator")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-regulator.db")
os.environ.setdefault("GATE_REQUIRE_RECEIPT_KEYS", "0")

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

_priv = Ed25519PrivateKey.generate()
_priv_bytes = _priv.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
_pub_bytes = _priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
os.environ["GATE_RECEIPT_PRIVATE_KEY"] = base64.b64encode(_priv_bytes).decode("utf-8")
os.environ["GATE_RECEIPT_PUBLIC_KEY"] = base64.b64encode(_pub_bytes).decode("utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from gate import app as gate_app  # noqa: E402
from gate import regulator as regulator_mod  # noqa: E402


class RegulatorSurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        from gate import db as gate_db

        gate_db.init_db()

    def setUp(self):
        self.client = gate_app.app.test_client()
        # Ensure DB ready even when calling regulator_mod directly.
        from gate import db as gate_db

        gate_db.init_db()

    def test_manifest_maps_four_asks_and_q15(self):
        m = regulator_mod.manifest("https://gate.example")
        self.assertEqual(m["spec"], "gate-regulator-v1")
        self.assertEqual(m["audience"], "regulators_and_policy_staff")
        self.assertIn("bind_room", m["not"])
        self.assertEqual(len(m["naic_asks"]), 4)
        ids = [a["id"] for a in m["naic_asks"]]
        self.assertEqual(
            ids,
            [
                "agentic_irreversible",
                "exhibit_b_3p",
                "materiality_enforceable",
                "exhibit_a_decision_paths",
            ],
        )
        q15 = m["hmt_q15"]
        self.assertIn("Question 15", q15["question"])
        self.assertEqual(
            q15["submit_email"], "Modernisingpaymentservices@hmtreasury.gov.uk"
        )
        docket_ids = [d["id"] for d in m["docket"]]
        self.assertIn("naic_v5_written", docket_ids)
        self.assertIn("gaaia", docket_ids)
        gaaia = next(d for d in m["docket"] if d["id"] == "gaaia")
        self.assertEqual(gaaia["status"], "channel_open_no_filed_copy_in_repo")

    def test_page_and_well_known(self):
        page = self.client.get("/regulator")
        self.assertEqual(page.status_code, 200)
        body = page.get_data(as_text=True)
        self.assertIn("Regulator verify", body)
        self.assertIn("NAIC four asks", body)
        self.assertIn("Question 15", body)
        self.assertIn("Mint checkable receipt", body)
        self.assertNotIn("/bind-room/checkout", body)
        man = self.client.get("/.well-known/regulator.json")
        self.assertEqual(man.status_code, 200)
        data = man.get_json()
        self.assertTrue(data["page"].endswith("/regulator"))
        gate = self.client.get("/.well-known/gate.json").get_json()
        self.assertTrue(gate["regulator"].endswith("/regulator"))

    def test_mint_and_verify_e2e(self):
        miss = self.client.get("/v1/regulator/verify")
        self.assertEqual(miss.status_code, 400)
        missing = self.client.get("/v1/regulator/verify?event_id=not-real")
        self.assertEqual(missing.status_code, 404)

        minted = self.client.post("/demo/regulator/mint", json={})
        self.assertEqual(minted.status_code, 200)
        body = minted.get_json()
        self.assertTrue(body["minted"])
        self.assertFalse(body["money_real"])
        self.assertEqual(body["decision"], "NO_GO")
        eid = body["event_id"]
        self.assertTrue(eid)
        self.assertIn("claim_scope", body)
        self.assertEqual(body["claim_scope"]["boundary"], "gate_regulator_sample")

        receipt = self.client.get(f"/.well-known/receipt/{eid}.json")
        self.assertEqual(receipt.status_code, 200)
        proof = self.client.get(f"/.well-known/receipt/{eid}/proof.json")
        self.assertEqual(proof.status_code, 200)
        proof_body = proof.get_json()
        self.assertEqual(proof_body["spec"], "gate-evidence-proof-v1")
        self.assertGreaterEqual(proof_body["inclusion"]["tree_size"], 1)

        checked = self.client.get(f"/v1/regulator/verify?event_id={eid}")
        self.assertEqual(checked.status_code, 200)
        out = checked.get_json()
        self.assertTrue(out["ok"])
        self.assertTrue(out["checks"]["receipt_signature"])
        self.assertTrue(out["checks"]["inclusion_proof"])
        self.assertFalse(out["money_real"])

        page = self.client.get(f"/regulator?event_id={eid}")
        self.assertEqual(page.status_code, 200)
        self.assertIn(eid, page.get_data(as_text=True))

    def test_honest_no_sept14_invention(self):
        m = regulator_mod.manifest("https://gate.example")
        naic = next(d for d in m["docket"] if d["id"] == "naic_v5_written")
        self.assertIn("Sept 14", naic["plain"])
        self.assertEqual(naic["status"], "draft_in_repo")


if __name__ == "__main__":
    unittest.main()
