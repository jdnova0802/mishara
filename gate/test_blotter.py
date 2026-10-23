"""Open-act blotter and GATE.SEAL(job_id). Run from gate/: python3 test_blotter.py"""
from __future__ import annotations

import base64
import os
import sys
import tempfile
import unittest
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

os.environ["GATE_DEV_MODE"] = "1"
os.environ["GATE_SECRET_KEY"] = "test-secret"
os.environ["GATE_DB_PATH"] = os.path.join(
    tempfile.gettempdir(), f"gate-blotter-{uuid.uuid4().hex}.db"
)

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat

_priv = Ed25519PrivateKey.generate()
os.environ["GATE_RECEIPT_PRIVATE_KEY"] = base64.b64encode(
    _priv.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
).decode("utf-8")
os.environ["GATE_RECEIPT_PUBLIC_KEY"] = base64.b64encode(
    _priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
).decode("utf-8")

import app as gate_app  # noqa: E402
import db as gate_db  # noqa: E402


class BlotterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_late_row_then_deny_closes_it(self):
        page = self.client.get("/blotter")
        self.assertEqual(page.status_code, 200)
        html = page.get_data(as_text=True)
        self.assertIn("GATE.SEAL", html)
        self.assertIn("No open acts.", html)

        job_id = "pc:BLOTTER-1"
        gate_db.record_bind_event(
            fuse_id="fuse_velaru_drill",
            job_id=job_id,
            decision="HOLD",
            acted=False,
            hop={
                "clock": {
                    "started_at": "2020-01-01T00:00:00+00:00",
                    "due_at": "2020-01-01T01:00:00+00:00",
                    "disposition": "open",
                }
            },
        )
        book = self.client.get("/v1/blotter").get_json()
        self.assertEqual(book["spec"], "gate-blotter-v1")
        self.assertEqual(book["window_minutes"], 60)
        match = [row for row in book["rows"] if row["job_id"] == job_id]
        self.assertEqual(len(match), 1)
        self.assertEqual(match[0]["composite"], "LATE")
        self.assertTrue(match[0]["flash"])
        self.assertEqual(match[0]["print_count"], 1)

        seal = self.client.get(f"/v1/seal/job?job_id={job_id}").get_json()
        self.assertEqual(seal["formula"], "GATE.SEAL")
        self.assertEqual(seal["composite"], "LATE")
        self.assertNotIn("documents", seal)

        denied = self.client.post(
            "/v1/blotter/act",
            json={"job_id": job_id, "decision": "HALT"},
        )
        self.assertEqual(denied.status_code, 200)
        body = denied.get_json()
        self.assertTrue(body["ok"])
        self.assertEqual(body["print_count"], 2)
        self.assertEqual(body["disposition"], "denied")
        self.assertEqual(body["reason_code"], "HALT")
        self.assertEqual(body["composite"], "HOLDS")
        self.assertEqual(len(body["prints"]), 2)

        again = self.client.get("/v1/blotter").get_json()
        self.assertFalse(any(row["job_id"] == job_id for row in again["rows"]))

        bad = self.client.post(
            "/v1/blotter/act",
            json={"job_id": job_id, "decision": "GO"},
        )
        self.assertEqual(bad.status_code, 400)


if __name__ == "__main__":
    unittest.main()
