"""Attack the receipt. Green happy-path tests are not this file."""
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

from gate import right_to_act as rta  # noqa: E402


def _body(**extra):
    base = {
        "action": "wire.send",
        "sink": "bank.rtp",
        "actor": "agent-1",
        "args": {"amount": 5},
        "policy": {
            "max_amount": 10,
            "allowed_actions": ["wire.send", "wire.hold"],
        },
    }
    base.update(extra)
    return base


class ReceiptAdversaryTests(unittest.TestCase):
    def test_decoy_thought_write_cannot_mint_act(self):
        out = rta.evaluate(
            _body(
                policy={
                    "max_amount": 10,
                    "allowed_actions": ["wire.send", "thought.consider", "model.nbest"],
                }
            ),
            public_url="https://gate.test",
        )
        self.assertEqual(out["decision"], "EXIST")
        self.assertEqual(out["agency"], "NON-ACT")
        self.assertEqual(out["otherwise"]["open_count"], 1)
        verified = rta.verify_receipt_jwt(out["receipt"])
        self.assertEqual(verified["payload"]["agc"], "NON-ACT")

    def test_self_named_settler_cannot_dodge_gap(self):
        out = rta.evaluate(
            {
                "action": "wire.send",
                "sink": "bank.rtp",
                "args": {"amount": 5},
                "settler_id": "policy:allowlist:wire.send",
                "policy": {"max_amount": 10, "allowed_actions": ["wire.send"]},
            },
            public_url="https://gate.test",
        )
        self.assertEqual(out["settler"]["kind"], "spoof")
        self.assertTrue(out["settler"]["gap"])
        self.assertFalse(out["settler"]["owned"])
        verified = rta.verify_receipt_jwt(out["receipt"])
        self.assertEqual(verified["payload"]["stl"], "GAP")

    def test_act_never_pairs_with_settled(self):
        out = rta.evaluate(_body(), public_url="https://gate.test")
        if out["agency"] == "ACT":
            self.assertFalse(out["otherwise"]["settled"])
            self.assertGreaterEqual(out["otherwise"]["open_count"], 2)
        verified = rta.verify_receipt_jwt(out["receipt"])
        if verified["payload"]["agc"] == "ACT":
            self.assertGreaterEqual(out["otherwise"]["open_count"], 2)

    def test_upstream_nonexist_blocks_child_exist(self):
        parent = rta.evaluate(
            {
                "action": "wire.send",
                "sink": "bank.rtp",
                "args": {"amount": 500},
                "policy": {"max_amount": 1, "allowed_actions": ["wire.send"]},
            },
            public_url="https://gate.test",
        )
        self.assertEqual(parent["decision"], "NONEXIST")
        child = rta.evaluate(
            _body(upstream=[parent["receipt"]]),
            public_url="https://gate.test",
        )
        self.assertEqual(child["decision"], "NONEXIST")
        self.assertIn("chain_rotten", child["signals"])
        self.assertIsNone(child["ticket_id"])
        self.assertEqual(child["chain"]["grade"], "ROTTEN")
        verified = rta.verify_receipt_jwt(child["receipt"])
        self.assertEqual(verified["payload"]["chn"], "ROTTEN")

    def test_upstream_down_stains_child_still_exist(self):
        parent = rta.evaluate(
            _body(
                written_line={"share": 40},
                signed_line={"share": 10},
                authority={"inside": True, "at": "2026-09-18T12:00:00Z"},
            ),
            public_url="https://gate.test",
        )
        self.assertEqual(parent["decision"], "EXIST")
        self.assertEqual(parent["signed_line"]["mutation"], "DOWN")
        child = rta.evaluate(
            _body(upstream=[parent["receipt"]]),
            public_url="https://gate.test",
        )
        self.assertEqual(child["decision"], "EXIST")
        self.assertTrue(child["ticket_id"])
        self.assertEqual(child["chain"]["grade"], "STAINED")
        self.assertEqual(child["chain"]["min_agency"], "ACT")
        verified = rta.verify_receipt_jwt(child["receipt"])
        self.assertEqual(verified["payload"]["chn"], "STAINED")
        self.assertEqual(verified["payload"]["ugp"], "OK")

    def test_garbage_upstream_jwt_is_rotten(self):
        child = rta.evaluate(
            _body(upstream=["aaa.bbb.ccc"]),
            public_url="https://gate.test",
        )
        self.assertEqual(child["decision"], "NONEXIST")
        self.assertEqual(child["chain"]["grade"], "ROTTEN")

    def test_three_mouths_cannot_nested_stit(self):
        out = rta.evaluate(
            _body(
                human_principal_id="human:cuo",
                principals=["agent-mid", "human:board"],
            ),
            public_url="https://gate.test",
        )
        self.assertEqual(out["decision"], "EXIST")
        self.assertFalse(out["delegated"])
        self.assertTrue(out["nested_stit"]["misfire"])
        self.assertGreaterEqual(out["nested_stit"]["depth"], 3)
        verified = rta.verify_receipt_jwt(out["receipt"])
        self.assertEqual(verified["payload"]["nst"], "UNSAT")

    def test_expired_authority_without_at_is_out(self):
        out = rta.evaluate(
            _body(
                written_line={"share": 25},
                signed_line={"share": 25},
                authority={
                    "inside": True,
                    "window_end": "2020-01-01T00:00:00Z",
                },
            ),
            public_url="https://gate.test",
        )
        self.assertEqual(out["decision"], "NONEXIST")
        self.assertEqual(out["signed_line"]["in_authority"], "OUT")
        self.assertEqual(out["signed_line"]["valid_until"], "2020-01-01T00:00:00Z")
        verified = rta.verify_receipt_jwt(out["receipt"])
        self.assertEqual(verified["payload"]["iaa"], "OUT")
        self.assertEqual(verified["payload"]["iau"], "2020-01-01T00:00:00Z")

    def test_machine_cannot_wear_supplier_mouth(self):
        out = rta.evaluate(
            _body(
                rely={
                    "cert": {
                        "id": "cert-1",
                        "supplier_id": "acme",
                        "ein": "12-3456789",
                        "signed_under_penalty": True,
                        "determination": "compliant",
                    },
                    "questionnaire": {"asked": True},
                    "sourcing_map": {"tier1": "acme"},
                }
            ),
            public_url="https://gate.test",
        )
        self.assertEqual(out["decision"], "NONEXIST")
        self.assertEqual(out["rely"]["reason"], "mouth_substitution")
        self.assertIsNone(out["ticket_id"])
        verified = rta.verify_receipt_jwt(out["receipt"])
        self.assertEqual(verified["payload"]["rly"], "NONEXIST")
        self.assertEqual(verified["payload"]["rtk"], "TRIP")


if __name__ == "__main__":
    unittest.main()
