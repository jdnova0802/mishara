"""Items 56–57 — precedence engine and specimen lineage."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-precedence-custody.db")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import custody  # noqa: E402
import precedence  # noqa: E402
import receipt  # noqa: E402


class PrecedenceTests(unittest.TestCase):
    def test_ot_beats_house_policy(self):
        out = precedence.resolve({"vertical": "ot"})
        self.assertEqual(out["winner"]["id"], "iec_61511")

    def test_house_policy_is_last(self):
        out = precedence.resolve({})
        self.assertEqual(out["winner"]["id"], "house_policy")

    def test_model_225_beats_house(self):
        out = precedence.resolve({"mga_contract_terminated": "yes"})
        self.assertEqual(out["winner"]["id"], "naic_model_225")


class CustodyTests(unittest.TestCase):
    def test_walks_prev_hash_and_flags_unsigned(self):
        rows = [
            {"id": "a", "receipt_hash": "h1", "prev_receipt_hash": None, "receipt_public_key_fingerprint": "fp", "receipt_signature": "sig"},
            {"id": "b", "receipt_hash": "h2", "prev_receipt_hash": "h1", "receipt_public_key_fingerprint": None, "receipt_signature": None},
        ]
        lin = custody.lineage(rows, start_event_id="b")
        self.assertEqual(lin["length"], 2)
        self.assertEqual(lin["handlers"][0]["event_id"], "a")
        self.assertTrue(lin["contamination"])
        self.assertEqual(lin["handlers"][1]["responsible_identity"], "UNSIGNED")

    def test_dfir_names_responsible_identity(self):
        env = receipt.dfir_envelope(
            {"id": "e", "receipt_hash": "h", "receipt_public_key_fingerprint": "fp", "receipt_signature": "s", "hop": {}},
            {},
        )
        self.assertEqual(env["chain_of_handlers"][0]["responsible_identity"], "fp")


class FlaskTests(unittest.TestCase):
    def setUp(self):
        self.client = app_mod.app.test_client()

    def test_pages(self):
        self.assertEqual(self.client.get("/precedence").status_code, 200)
        self.assertEqual(self.client.get("/custody").status_code, 200)
        r = self.client.post("/v1/precedence", json={"state": "KS"})
        self.assertEqual(r.get_json()["winner"]["id"], "ks_40_2133")


if __name__ == "__main__":
    unittest.main()
