"""Policy-as-code: expected outcomes run against the real Right-to-Act engine."""
from __future__ import annotations

import base64
import json
import os
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat

os.environ["GATE_DEV_MODE"] = "0"

_key = Ed25519PrivateKey.generate()
_priv = _key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
_pub = _key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
os.environ["GATE_RECEIPT_PRIVATE_KEY"] = base64.b64encode(_priv).decode()
os.environ["GATE_RECEIPT_PUBLIC_KEY"] = base64.b64encode(_pub).decode()

from gate import right_to_act as rta  # noqa: E402

CASES_PATH = Path(__file__).resolve().parent / "policy_cases.yaml"


class PolicyAsCodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = json.loads(CASES_PATH.read_text(encoding="utf-8"))

    def test_precedence_constant(self):
        self.assertEqual(list(rta.POLICY_PRECEDENCE), self.bundle["precedence"])

    def test_cases(self):
        for case in self.bundle["cases"]:
            with self.subTest(case["name"]):
                out = rta.evaluate(
                    {
                        "action": case["action"],
                        "sink": case["sink"],
                        "actor": case.get("actor"),
                        "human_principal_id": case.get("human_principal_id"),
                        "args": case.get("args"),
                        "policy": case.get("policy") or {},
                    },
                    public_url="https://gate.test",
                )
                self.assertEqual(out["decision"], case["expect"], out)
                if case.get("signal"):
                    self.assertIn(case["signal"], out["signals"], out)
                if case.get("human_principal_id") and out.get("receipt"):
                    verified = rta.verify_receipt_jwt(out["receipt"])
                    payload = verified["payload"] or {}
                    self.assertEqual(payload.get("agt"), case.get("actor"))
                    self.assertEqual(payload.get("prn"), case.get("human_principal_id"))
                    self.assertNotEqual(payload.get("agt"), payload.get("prn"))
                forbid = case.get("forbid_in_receipt")
                if forbid:
                    self.assertNotIn(forbid, json.dumps(out.get("args_redacted")))
                    self.assertNotIn(forbid, out.get("receipt") or "")
                    self.assertTrue(str(out["args_redacted"].get("api_key", "")).startswith("sha256:"))


if __name__ == "__main__":
    unittest.main()
