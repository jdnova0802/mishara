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
        self.assertEqual(out["agency"], "NON-ACT")
        self.assertTrue(out["otherwise"]["settled"])
        self.assertEqual(out["otherwise"]["open_count"], 1)
        self.assertFalse(out["delegated"])
        self.assertTrue(out["nested_stit"]["nested_possible"])
        self.assertIsNotNone(out["settler"])
        self.assertEqual(out["settler"]["kind"], "allowlist")
        self.assertFalse(out["settler"]["owned"])
        verified_gap = rta.verify_receipt_jwt(out["receipt"])
        self.assertEqual(verified_gap["payload"]["stl"], "GAP")

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


    def test_two_live_writes_is_an_act(self):
        out = rta.evaluate(
            {
                "action": "wire.send",
                "sink": "bank.rtp",
                "actor": "agent-1",
                "args": {"amount": 5},
                "policy": {
                    "max_amount": 10,
                    "allowed_actions": ["wire.send", "wire.hold"],
                },
            },
            public_url="https://gate.test",
        )
        self.assertEqual(out["decision"], "EXIST")
        self.assertEqual(out["agency"], "ACT")
        self.assertFalse(out["otherwise"]["settled"])
        self.assertEqual(out["otherwise"]["open_count"], 2)
        verified = rta.verify_receipt_jwt(out["receipt"])
        self.assertTrue(verified["valid"])
        self.assertEqual(verified["payload"]["agc"], "ACT")
        self.assertEqual(verified["payload"]["owh"], out["otherwise"]["open_hash"])
        self.assertIsNone(out["settler"])
        self.assertEqual(verified["payload"]["nst"], "SAT")

    def test_open_writes_must_be_executable_not_thoughts(self):
        out = rta.evaluate(
            {
                "action": "wire.send",
                "sink": "bank.rtp",
                "args": {"amount": 5},
                "policy": {"max_amount": 10, "allowed_actions": ["wire.send"]},
                "open_writes": [
                    "the model also considered refund",
                    {
                        "action": "wire.refund",
                        "sink": "bank.rtp",
                        "args": {"amount": 5},
                    },
                ],
            },
            public_url="https://gate.test",
        )
        self.assertEqual(out["decision"], "EXIST")
        self.assertEqual(out["agency"], "ACT")
        actions = {row["action"] for row in out["otherwise"]["live"]}
        self.assertEqual(actions, {"wire.send", "wire.refund"})

    def test_settled_nonexist_is_not_an_act(self):
        out = rta.evaluate(
            {
                "action": "wire.send",
                "sink": "bank.rtp",
                "args": {"amount": 500},
                "policy": {"max_amount": 1, "allowed_actions": ["wire.send"]},
            },
            public_url="https://gate.test",
        )
        self.assertEqual(out["decision"], "NONEXIST")
        self.assertEqual(out["agency"], "NON-ACT")
        self.assertEqual(out["otherwise"]["open_count"], 0)
        self.assertEqual(out["settler"]["kind"], "policy")
        self.assertTrue(out["settler"]["gap"])

    def test_nested_stit_two_agents_is_misfire(self):
        out = rta.evaluate(
            {
                "action": "wire.send",
                "sink": "bank.rtp",
                "actor": "agent-1",
                "human_principal_id": "human:uw",
                "nested_stit": True,
                "args": {"amount": 5},
                "policy": {
                    "max_amount": 10,
                    "allowed_actions": ["wire.send", "wire.hold"],
                },
            },
            public_url="https://gate.test",
        )
        self.assertEqual(out["decision"], "EXIST")
        self.assertEqual(out["agency"], "ACT")
        self.assertFalse(out["delegated"])
        self.assertTrue(out["nested_stit"]["misfire"])
        self.assertFalse(out["nested_stit"]["nested_possible"])
        verified = rta.verify_receipt_jwt(out["receipt"])
        self.assertEqual(verified["payload"]["nst"], "UNSAT")

    def test_named_settler_on_non_act(self):
        out = rta.evaluate(
            {
                "action": "wire.send",
                "sink": "bank.rtp",
                "actor": "agent-1",
                "args": {"amount": 5},
                "settler_id": "charge:bind-1",
                "policy": {"max_amount": 10, "allowed_actions": ["wire.send"]},
            },
            public_url="https://gate.test",
        )
        self.assertEqual(out["agency"], "NON-ACT")
        self.assertEqual(out["settler"]["settler_id"], "charge:bind-1")
        verified = rta.verify_receipt_jwt(out["receipt"])
        self.assertEqual(verified["payload"]["stl"], "charge:bind-1")
        self.assertTrue(out["settler"]["owned"])
        self.assertFalse(out["settler"]["gap"])

    def test_signing_down_still_exist(self):
        out = rta.evaluate(
            {
                "action": "wire.send",
                "sink": "bank.rtp",
                "actor": "agent-1",
                "args": {"amount": 5},
                "written_line": {"share": 40, "class": "cargo"},
                "signed_line": {"share": 15, "class": "cargo"},
                "authority": {"inside": True, "at": "2026-09-18T12:00:00Z"},
                "policy": {
                    "max_amount": 10,
                    "allowed_actions": ["wire.send", "wire.hold"],
                },
            },
            public_url="https://gate.test",
        )
        self.assertEqual(out["decision"], "EXIST")
        self.assertEqual(out["signed_line"]["mutation"], "DOWN")
        self.assertEqual(out["signed_line"]["in_authority"], "IN")
        self.assertFalse(out["signed_line"]["halt"])
        verified = rta.verify_receipt_jwt(out["receipt"])
        self.assertEqual(verified["payload"]["mut"], "DOWN")
        self.assertEqual(verified["payload"]["iaa"], "IN")
        self.assertEqual(verified["payload"]["wlh"], out["signed_line"]["written_hash"])
        self.assertEqual(verified["payload"]["slh"], out["signed_line"]["signed_hash"])
        self.assertNotEqual(verified["payload"]["wlh"], verified["payload"]["slh"])

    def test_out_of_authority_is_nonexist(self):
        out = rta.evaluate(
            {
                "action": "wire.send",
                "sink": "bank.rtp",
                "actor": "agent-1",
                "args": {"amount": 5},
                "written_line": {"share": 25},
                "signed_line": {"share": 25},
                "authority": {"inside": False, "at": "2026-09-18T12:00:00Z"},
                "policy": {"max_amount": 10, "allowed_actions": ["wire.send"]},
            },
            public_url="https://gate.test",
        )
        self.assertEqual(out["decision"], "NONEXIST")
        self.assertIn("signed_line_out_of_authority", out["signals"])
        self.assertIsNone(out["ticket_id"])
        self.assertTrue(out["signed_line"]["halt"])
        verified = rta.verify_receipt_jwt(out["receipt"])
        self.assertEqual(verified["payload"]["iaa"], "OUT")
        self.assertEqual(verified["payload"]["mut"], "SAME")

    def test_unpinned_operator_is_gap_still_exist(self):
        out = rta.evaluate(
            {
                "action": "wire.send",
                "sink": "bank.rtp",
                "args": {"amount": 5},
                "policy": {"max_amount": 10, "allowed_actions": ["wire.send", "wire.hold"]},
            },
            public_url="https://gate.test",
        )
        self.assertEqual(out["decision"], "EXIST")
        self.assertEqual(out["cosign"]["status"], "GAP")
        verified = rta.verify_receipt_jwt(out["receipt"])
        self.assertEqual(verified["payload"]["ops"], "GAP")

    def test_pinned_operator_holds_then_exist(self):
        from gate import cosign as cosign_mod

        op = Ed25519PrivateKey.generate()
        op_priv = op.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
        op_pub = op.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        prev = os.environ.get("GATE_OPERATOR_PUBLIC_KEY")
        os.environ["GATE_OPERATOR_PUBLIC_KEY"] = base64.b64encode(op_pub).decode()
        body = {
            "action": "wire.send",
            "sink": "bank.rtp",
            "actor": "agent-1",
            "args": {"amount": 5},
            "policy": {
                "max_amount": 10,
                "allowed_actions": ["wire.send", "wire.hold"],
            },
        }
        try:
            held = rta.evaluate(body, public_url="https://gate.test")
            self.assertEqual(held["decision"], "HOLD")
            self.assertIsNone(held["ticket_id"])
            self.assertIn("operator_unsigned", held["signals"])
            sig = cosign_mod.sign_preimage(
                bytes.fromhex(held["cosign"]["sign_over"]), op_priv
            )
            body["operator_sig"] = sig
            ok = rta.evaluate(body, public_url="https://gate.test")
            self.assertEqual(ok["decision"], "EXIST")
            self.assertEqual(ok["cosign"]["status"], "OK")
            self.assertTrue(ok["ticket_id"])
            verified = rta.verify_receipt_jwt(ok["receipt"])
            self.assertTrue(verified["valid"])
            self.assertEqual(verified["payload"]["ops"], "OK")
        finally:
            if prev is None:
                os.environ.pop("GATE_OPERATOR_PUBLIC_KEY", None)
            else:
                os.environ["GATE_OPERATOR_PUBLIC_KEY"] = prev

    def test_machine_key_cannot_be_operator(self):
        from gate import cosign as cosign_mod

        machine_pub = base64.b64decode(os.environ["GATE_RECEIPT_PUBLIC_KEY"] + "==")
        machine_priv = base64.b64decode(os.environ["GATE_RECEIPT_PRIVATE_KEY"] + "==")
        prev = os.environ.get("GATE_OPERATOR_PUBLIC_KEY")
        os.environ["GATE_OPERATOR_PUBLIC_KEY"] = os.environ["GATE_RECEIPT_PUBLIC_KEY"]
        body = {
            "action": "wire.send",
            "sink": "bank.rtp",
            "args": {"amount": 5},
            "policy": {"max_amount": 10, "allowed_actions": ["wire.send", "wire.hold"]},
        }
        try:
            held = rta.evaluate(body, public_url="https://gate.test")
            sig = cosign_mod.sign_preimage(
                bytes.fromhex(held["cosign"]["sign_over"]), machine_priv
            )
            body["operator_sig"] = sig
            out = rta.evaluate(body, public_url="https://gate.test")
            self.assertEqual(out["decision"], "NONEXIST")
            self.assertEqual(out["cosign"]["reason"], "role_substitution")
            self.assertIn("role_substitution", out["signals"])
            self.assertIsNone(out["ticket_id"])
        finally:
            if prev is None:
                os.environ.pop("GATE_OPERATOR_PUBLIC_KEY", None)
            else:
                os.environ["GATE_OPERATOR_PUBLIC_KEY"] = prev
            _ = machine_pub


if __name__ == "__main__":
    unittest.main()
