"""Right-to-Act substrate — EXIST / NONEXIST + refusal digests + ticket burn."""
from __future__ import annotations

import base64
import os
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat

os.environ["GATE_DEV_MODE"] = "0"

_key = Ed25519PrivateKey.generate()
_priv = _key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
_pub = _key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
os.environ["GATE_RECEIPT_PRIVATE_KEY"] = base64.b64encode(_priv).decode()
os.environ["GATE_RECEIPT_PUBLIC_KEY"] = base64.b64encode(_pub).decode()

from gate import right_to_act as rta  # noqa: E402


class RightToActTests(unittest.TestCase):
    def test_exist_mints_ticket_and_burns_once(self):
        out = rta.evaluate(
            {
                "action": "wire.send",
                "sink": "bank.rtp",
                "actor": "agent-1",
                "args": {"amount": 5},
                "policy": {"max_amount": 10, "allowed_actions": ["wire.send"]},
            },
            public_url="https://gate.test",
        )
        self.assertEqual(out["decision"], "EXIST")
        self.assertTrue(out["receipt"])
        self.assertTrue(out["ticket_id"])
        self.assertIsNone(out["refusal_digest"])

        burned = rta.burn_ticket(
            out["ticket_id"], fingerprint=out["fingerprint"], sink="bank.rtp"
        )
        self.assertTrue(burned["ok"])

        again = rta.burn_ticket(
            out["ticket_id"], fingerprint=out["fingerprint"], sink="bank.rtp"
        )
        self.assertFalse(again["ok"])
        self.assertEqual(again["reason"], "already_burned")

    def test_nonexist_refusal_digest_verifies(self):
        out = rta.evaluate(
            {
                "action": "wire.send",
                "sink": "bank.rtp",
                "args": {"amount": 500},
                "policy": {"max_amount": 1},
            },
            public_url="https://gate.test",
        )
        self.assertEqual(out["decision"], "NONEXIST")
        self.assertTrue(out["refusal_digest"])
        self.assertTrue(out["receipt"])
        self.assertIsNone(out["ticket_id"])

        verified = rta.verify_receipt_jwt(out["receipt"])
        self.assertTrue(verified["valid"])
        self.assertEqual(verified["decision"], "NONEXIST")
        self.assertEqual(verified["refusal_digest"], out["refusal_digest"])

    def test_missing_sink_is_nonexist(self):
        out = rta.evaluate(
            {"action": "wire.send", "args": {"amount": 1}},
            public_url="https://gate.test",
        )
        self.assertEqual(out["decision"], "NONEXIST")
        self.assertIn("missing_sink", out["signals"])


if __name__ == "__main__":
    unittest.main()
