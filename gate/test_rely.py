"""Reliance gate — named cert, not a credit-clean stamp."""
from __future__ import annotations

import base64
import os
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat

os.environ.setdefault("GATE_DEV_MODE", "0")
if not os.environ.get("GATE_RECEIPT_PRIVATE_KEY"):
    _key = Ed25519PrivateKey.generate()
    os.environ["GATE_RECEIPT_PRIVATE_KEY"] = base64.b64encode(
        _key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    ).decode()
    os.environ["GATE_RECEIPT_PUBLIC_KEY"] = base64.b64encode(
        _key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    ).decode()

from gate import rely as rely_mod  # noqa: E402
from gate import right_to_act as rta  # noqa: E402


def _cert(**extra):
    body = {
        "id": "cert-1",
        "supplier_id": "acme-mod",
        "ein": "12-3456789",
        "signed_under_penalty": True,
        "text": "not PFE produced",
    }
    body.update(extra)
    return body


class RelyWitnessTests(unittest.TestCase):
    def test_absent_cert_is_gap_not_halt(self):
        out = rely_mod.witness()
        self.assertEqual(out["decision"], "GAP")
        self.assertFalse(out["halt"])
        self.assertEqual(out["rtk"], "GAP")

    def test_complete_file_may_rely(self):
        out = rely_mod.witness(
            cert=_cert(),
            questionnaire={"asked": True},
            sourcing_map={"tier1": "acme-mod"},
        )
        self.assertEqual(out["decision"], "EXIST")
        self.assertFalse(out["halt"])
        self.assertEqual(out["rtk"], "CLEAN")
        self.assertNotIn("pfe_status", out)
        self.assertNotIn("credit_clean", out)

    def test_missing_questionnaire_holds(self):
        out = rely_mod.witness(
            cert=_cert(),
            sourcing_map={"tier1": "acme-mod"},
        )
        self.assertEqual(out["decision"], "HOLD")
        self.assertEqual(out["reason"], "missing_questionnaire")
        self.assertTrue(out["halt"])

    def test_public_collision_is_reason_to_know(self):
        out = rely_mod.witness(
            cert=_cert(),
            questionnaire={"asked": True},
            sourcing_map={"tier1": "acme-mod"},
            public_collision=["covered-nation incorporation"],
        )
        self.assertEqual(out["decision"], "NONEXIST")
        self.assertEqual(out["reason"], "reason_to_know")
        self.assertEqual(out["rtk"], "TRIP")

    def test_machine_mouth_is_substitution(self):
        out = rely_mod.from_body(
            {
                "rely": {
                    "cert": _cert(),
                    "questionnaire": {"asked": True},
                    "sourcing_map": {"tier1": "x"},
                    "determination": "compliant",
                }
            }
        )
        self.assertEqual(out["decision"], "NONEXIST")
        self.assertEqual(out["reason"], "mouth_substitution")
        self.assertIn("determination", out["mouth_keys"])

    def test_tables_moved_holds(self):
        out = rely_mod.from_body(
            {
                "rely": {
                    "cert": _cert(),
                    "questionnaire": {"asked": True},
                    "sourcing_map": {"tier1": "x"},
                    "tables_id": "notice-2025-08",
                    "tables_current": "notice-2026-99",
                }
            }
        )
        self.assertEqual(out["decision"], "HOLD")
        self.assertEqual(out["reason"], "tables_moved")


class RelyEvaluateTests(unittest.TestCase):
    def test_remaining_charge_untouched_without_cert(self):
        out = rta.evaluate(
            {
                "action": "wire.send",
                "sink": "bank.rtp",
                "args": {"amount": 5},
                "policy": {
                    "max_amount": 10,
                    "allowed_actions": ["wire.send", "wire.hold"],
                },
            },
            public_url="https://gate.test",
        )
        self.assertEqual(out["decision"], "EXIST")
        self.assertEqual(out["rely"]["status"], "GAP")
        verified = rta.verify_receipt_jwt(out["receipt"])
        self.assertEqual(verified["payload"]["rly"], "GAP")
        self.assertEqual(verified["payload"]["rtk"], "GAP")

    def test_complete_cert_exist_and_jwt(self):
        out = rta.evaluate(
            {
                "action": "wire.send",
                "sink": "bank.rtp",
                "args": {"amount": 5},
                "rely": {
                    "cert": _cert(),
                    "questionnaire": {"asked": True},
                    "sourcing_map": {"tier1": "acme-mod"},
                },
                "policy": {
                    "max_amount": 10,
                    "allowed_actions": ["wire.send", "wire.hold"],
                },
            },
            public_url="https://gate.test",
        )
        self.assertEqual(out["decision"], "EXIST")
        self.assertEqual(out["rely"]["decision"], "EXIST")
        verified = rta.verify_receipt_jwt(out["receipt"])
        self.assertEqual(verified["payload"]["rly"], "EXIST")
        self.assertEqual(verified["payload"]["rtk"], "CLEAN")
        self.assertEqual(verified["payload"]["rch"], out["rely"]["cert_hash"])

    def test_missing_map_holds_no_ticket(self):
        out = rta.evaluate(
            {
                "action": "wire.send",
                "sink": "bank.rtp",
                "args": {"amount": 5},
                "rely": {
                    "cert": _cert(),
                    "questionnaire": {"asked": True},
                },
                "policy": {"max_amount": 10, "allowed_actions": ["wire.send"]},
            },
            public_url="https://gate.test",
        )
        self.assertEqual(out["decision"], "HOLD")
        self.assertIsNone(out["ticket_id"])
        self.assertIn("missing_map", out["signals"])

    def test_reason_to_know_nonexist(self):
        out = rta.evaluate(
            {
                "action": "wire.send",
                "sink": "bank.rtp",
                "args": {"amount": 5},
                "rely": {
                    "cert": _cert(),
                    "questionnaire": {"asked": True},
                    "sourcing_map": {"tier1": "x"},
                    "known_inaccurate": True,
                },
                "policy": {"max_amount": 10, "allowed_actions": ["wire.send"]},
            },
            public_url="https://gate.test",
        )
        self.assertEqual(out["decision"], "NONEXIST")
        self.assertIn("reason_to_know", out["signals"])
        self.assertIsNone(out["ticket_id"])


if __name__ == "__main__":
    unittest.main()
