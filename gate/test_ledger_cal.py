"""Items 125 and 130 — billing ledger idempotency; Brier sample-size gate."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-ledger-cal.db")
os.environ["GATE_LEDGER_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-ledger.json")
os.environ["GATE_CALIBRATION_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-cal.json")
os.environ.pop("GATE_CALIBRATION_MIN_SAMPLE", None)

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import calibration  # noqa: E402
import ledger  # noqa: E402


class LedgerTests(unittest.TestCase):
    def setUp(self):
        path = os.environ["GATE_LEDGER_PATH"]
        if os.path.exists(path):
            os.remove(path)

    def test_idempotent_retry_same_entry(self):
        a = ledger.post(
            idempotency_key="k1",
            receipt_id="r1",
            debit_account="org_a",
            credit_account="nisaba",
            amount="12.50",
        )
        b = ledger.post(
            idempotency_key="k1",
            receipt_id="r1",
            debit_account="org_a",
            credit_account="nisaba",
            amount="12.50",
        )
        self.assertEqual(a["entry_id"], b["entry_id"])
        self.assertTrue(b["replayed"])
        self.assertFalse(a["duplicates_receipt"])
        self.assertEqual(len(ledger.list_entries()), 1)

    def test_fee_split_refused(self):
        out = ledger.post(
            idempotency_key="k2",
            receipt_id="r2",
            debit_account="org_a",
            credit_account="nisaba",
            amount=1,
            extra={"fee_split": {"platform": 0.3}},
        )
        self.assertFalse(out["ok"])
        self.assertEqual(out["error"], "not_schema")


class CalibrationTests(unittest.TestCase):
    def setUp(self):
        path = os.environ["GATE_CALIBRATION_PATH"]
        if os.path.exists(path):
            os.remove(path)
        os.environ.pop("GATE_CALIBRATION_MIN_SAMPLE", None)

    def test_brier_and_unset_floor_does_not_feed(self):
        rec = calibration.resolve(
            operator_id="op1",
            receipt_id="r1",
            stated_confidence=0.8,
            actual_outcome="CORRECT",
        )
        self.assertAlmostEqual(rec["brier_component"], 0.04)
        sc = calibration.score("op1")
        self.assertEqual(sc["sample_size"], 1)
        self.assertFalse(sc["feeds_kudurru"])
        self.assertIsNone(sc["min_sample"])

    def test_named_floor_gates_kudurru(self):
        os.environ["GATE_CALIBRATION_MIN_SAMPLE"] = "2"
        calibration.resolve(operator_id="op2", receipt_id="a", stated_confidence=1, actual_outcome="CORRECT")
        self.assertFalse(calibration.score("op2")["feeds_kudurru"])
        calibration.resolve(operator_id="op2", receipt_id="b", stated_confidence=1, actual_outcome="CORRECT")
        sc = calibration.score("op2")
        self.assertTrue(sc["feeds_kudurru"])
        self.assertEqual(sc["sample_size"], 2)
        self.assertEqual(sc["mean_brier_score"], 0.0)


class LedgerCalFlaskTests(unittest.TestCase):
    def setUp(self):
        for key in ("GATE_LEDGER_PATH", "GATE_CALIBRATION_PATH"):
            path = os.environ[key]
            if os.path.exists(path):
                os.remove(path)
        self.client = app_mod.app.test_client()

    def test_pages_and_post(self):
        self.assertEqual(self.client.get("/ledger").status_code, 200)
        self.assertEqual(self.client.get("/calibration").status_code, 200)
        posted = self.client.post(
            "/v1/ledger",
            json={
                "idempotency_key": "ik",
                "receipt_id": "rcpt",
                "debit_account": "buyer",
                "credit_account": "nisaba",
                "amount": 3,
            },
        )
        self.assertEqual(posted.status_code, 201)
        again = self.client.post(
            "/v1/ledger",
            json={
                "idempotency_key": "ik",
                "receipt_id": "rcpt",
                "debit_account": "buyer",
                "credit_account": "nisaba",
                "amount": 3,
            },
        )
        self.assertEqual(again.get_json()["entry_id"], posted.get_json()["entry_id"])
        cal = self.client.post(
            "/v1/calibration",
            json={
                "operator_id": "opx",
                "receipt_id": "r",
                "stated_confidence": 0.5,
                "actual_outcome": "INCORRECT",
            },
        )
        self.assertEqual(cal.status_code, 201)
        sc = self.client.get("/v1/calibration?operator_id=opx")
        self.assertFalse(sc.get_json()["feeds_kudurru"])


if __name__ == "__main__":
    unittest.main()
