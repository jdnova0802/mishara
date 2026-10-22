"""Release MAY — filmable will-not-release. Not delivery."""
from __future__ import annotations

import base64
import json
import os
import sys
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat

os.environ.setdefault("GATE_DEV_MODE", "0")
if not os.environ.get("REL_RECEIPT_PRIVATE_KEY"):
    _key = Ed25519PrivateKey.generate()
    os.environ["REL_RECEIPT_PRIVATE_KEY"] = base64.b64encode(
        _key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    ).decode()
    os.environ["REL_RECEIPT_PUBLIC_KEY"] = base64.b64encode(
        _key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    ).decode()

from rel import receipt as receipt_mod  # noqa: E402
from rel import release as rel_mod  # noqa: E402


def _bill(**extra):
    body = {"id": "BL-1", "state": "SURRENDERED", "set": "3/3"}
    body.update(extra)
    return body


def _authority(**extra):
    body = {
        "kind": "owner",
        "owner": "owner:line",
        "human_principal_id": "human:owner-line",
        "written_instruction": {"text": "release to consignee X at port P"},
    }
    body.update(extra)
    return body


def _expected_authority_hash(authority=None):
    a = authority or _authority()
    return rel_mod.authority_hash(a)


def _complete(**extra):
    body = {"bill": _bill(), "authority": _authority()}
    body.update(extra)
    return body


class RelWitnessTests(unittest.TestCase):
    def test_absent_bill_is_gap_not_halt(self):
        out = rel_mod.witness()
        self.assertEqual(out["decision"], "GAP")
        self.assertFalse(out["halt"])
        self.assertEqual(out["gap_reason"], "missing_bill")

    def test_complete_surrendered_file_may_release(self):
        out = rel_mod.witness(bill=_bill(), authority=_authority())
        self.assertEqual(out["decision"], "EXIST")
        self.assertFalse(out["halt"])
        self.assertIsNotNone(out["instrument_hash"])
        self.assertIsNotNone(out["authority_hash"])
        self.assertNotIn("released", out)
        self.assertNotIn("telex_ok", out)

    def test_missing_principal_holds(self):
        out = rel_mod.witness(bill=_bill(), authority={"kind": "owner", "owner": "owner:line"})
        self.assertEqual(out["decision"], "HOLD")
        self.assertEqual(out["reason"], "missing_principal")
        self.assertTrue(out["halt"])

    def test_independent_telex_without_principal_holds(self):
        out = rel_mod.witness(
            bill=_bill(),
            telex={
                "channel": "independent",
                "inbound_from": "fraud@example",
                "confirm_to": "agent.genoa@line.example",
            },
        )
        self.assertEqual(out["decision"], "HOLD")
        self.assertEqual(out["reason"], "missing_principal")

    def test_machine_mouth_is_substitution(self):
        out = rel_mod.from_body(
            {
                "release": {
                    "bill": _bill(),
                    "authority": _authority(),
                    "authorized": True,
                }
            }
        )
        self.assertEqual(out["decision"], "NONEXIST")
        self.assertEqual(out["reason"], "mouth_substitution")
        self.assertIn("authorized", out["mouth_keys"])

    def test_stuffed_instruction_hash_is_mouth_substitution(self):
        out = rel_mod.witness(
            bill=_bill(),
            authority={
                "kind": "owner",
                "human_principal_id": "human:owner-line",
                "written_instruction": {"text": "release to consignee X at port P"},
                "instruction_hash": "a" * 64,
            },
        )
        self.assertEqual(out["decision"], "NONEXIST")
        self.assertEqual(out["reason"], "mouth_substitution")
        self.assertIn("instruction_hash", out["mouth_keys"])
        self.assertNotEqual(out["authority_hash"], "a" * 64)

    def test_caller_hash_alone_is_not_authority(self):
        out = rel_mod.witness(
            bill=_bill(),
            authority={"kind": "owner", "instruction_hash": "b" * 64},
        )
        self.assertEqual(out["decision"], "NONEXIST")
        self.assertEqual(out["reason"], "mouth_substitution")
        self.assertIsNone(out["authority_hash"])

    def test_written_body_without_named_human_holds(self):
        out = rel_mod.witness(
            bill=_bill(),
            authority={
                "kind": "owner",
                "owner": "owner:line",
                "written_instruction": {"text": "release to consignee X at port P"},
            },
        )
        self.assertEqual(out["decision"], "HOLD")
        self.assertEqual(out["reason"], "missing_principal")
        self.assertIsNone(out["authority_hash"])

    def test_authority_hash_is_principal_plus_writing(self):
        a = _authority()
        digest = rel_mod.authority_hash(a)
        again = rel_mod.authority_hash(a)
        stuffed = rel_mod.authority_hash({**a, "instruction_hash": "f" * 64})
        self.assertEqual(digest, again)
        self.assertEqual(digest, stuffed)
        self.assertEqual(len(digest), 64)
        self.assertNotEqual(digest, "a" * 64)


class RelFilmFixtures(unittest.TestCase):
    def test_telex_reply_to_is_nonexist(self):
        out = rel_mod.evaluate(
            {
                "release": {
                    "bill": _bill(),
                    "authority": _authority(),
                    "telex": {
                        "channel": "reply_to",
                        "inbound_from": "attacker@example",
                        "confirm_to": "attacker@example",
                    },
                }
            }
        )
        self.assertEqual(out["decision"], "NONEXIST")
        self.assertEqual(out["release"]["reason"], "telex_reply_to")
        self.assertIsNone(out["release_id"])
        verified = receipt_mod.verify_receipt_jwt(out["receipt"])
        self.assertTrue(verified["valid"])
        self.assertEqual(verified["payload"]["rel"], "NONEXIST")
        self.assertEqual(verified["payload"]["rsn"], "telex_reply_to")
        self.assertFalse(verified["payload"]["exists"])

    def test_switch_while_first_set_live_is_nonexist(self):
        out = rel_mod.evaluate(
            {
                "release": {
                    "bill": _bill(state="SURRENDERED"),
                    "authority": _authority(),
                    "switch": True,
                    "first_set": "LIVE",
                }
            }
        )
        self.assertEqual(out["decision"], "NONEXIST")
        self.assertEqual(out["release"]["reason"], "two_live_sets")
        self.assertIsNone(out["release_id"])
        verified = receipt_mod.verify_receipt_jwt(out["receipt"])
        self.assertEqual(verified["payload"]["rel"], "NONEXIST")
        self.assertFalse(verified["payload"]["exists"])

    def test_ebl_control_a_mouth_b_is_nonexist(self):
        out = rel_mod.evaluate(
            {
                "release": {
                    "bill": _bill(state="EBL_CONTROL"),
                    "authority": _authority(),
                    "control": {"platform": "wavebl", "party": "bank:one"},
                    "instruction": {"platform": "cargox", "party": "agent:genoa"},
                }
            }
        )
        self.assertEqual(out["decision"], "NONEXIST")
        self.assertEqual(out["release"]["reason"], "control_platform_mismatch")
        self.assertIsNone(out["release_id"])
        verified = receipt_mod.verify_receipt_jwt(out["receipt"])
        self.assertEqual(verified["payload"]["rel"], "NONEXIST")
        self.assertEqual(verified["payload"]["ctr"], "wavebl")
        self.assertFalse(verified["payload"]["exists"])


class RelEvaluateTests(unittest.TestCase):
    def test_gap_does_not_mint_release_id(self):
        out = rel_mod.evaluate({})
        self.assertEqual(out["decision"], "GAP")
        self.assertIsNone(out["release_id"])
        verified = receipt_mod.verify_receipt_jwt(out["receipt"])
        self.assertEqual(verified["payload"]["rel"], "GAP")
        self.assertFalse(verified["payload"]["exists"])

    def test_complete_exist_and_jwt(self):
        out = rel_mod.evaluate({"release": _complete()})
        self.assertEqual(out["decision"], "EXIST")
        self.assertTrue(out["release_id"])
        verified = receipt_mod.verify_receipt_jwt(out["receipt"])
        self.assertTrue(verified["valid"])
        self.assertEqual(verified["payload"]["rel"], "EXIST")
        self.assertTrue(verified["payload"]["exists"])
        self.assertEqual(verified["payload"]["inh"], out["release"]["instrument_hash"])
        self.assertEqual(verified["payload"]["ah"], out["release"]["authority_hash"])
        self.assertEqual(verified["payload"]["ah"], _expected_authority_hash())

    def test_charterer_only_switch_nonexist(self):
        out = rel_mod.evaluate(
            {
                "release": {
                    "bill": _bill(),
                    "authority": {
                        "kind": "charterer",
                        "charterer_only": True,
                        "human_principal_id": "human:charterer",
                        "written_instruction": {"text": "deliver without originals"},
                    },
                    "switch": True,
                    "first_set": "CANCELLED",
                }
            }
        )
        self.assertEqual(out["decision"], "NONEXIST")
        self.assertEqual(out["release"]["reason"], "charterer_only")

    def test_matched_ebl_control_may_exist(self):
        out = rel_mod.evaluate(
            {
                "release": {
                    "bill": _bill(state="EBL_CONTROL"),
                    "authority": _authority(),
                    "control": {"platform": "wavebl", "party": "bank:one"},
                    "instruction": {"platform": "wavebl", "party": "bank:one"},
                }
            }
        )
        self.assertEqual(out["decision"], "EXIST")
        self.assertTrue(out["release_id"])


class RelReceiptAdversaryTests(unittest.TestCase):
    def test_substituted_mouth_cannot_print_exist(self):
        out = rel_mod.evaluate(
            {
                "release": {
                    "bill": _bill(),
                    "authority": _authority(),
                    "released": True,
                    "telex_ok": True,
                }
            }
        )
        self.assertEqual(out["decision"], "NONEXIST")
        self.assertEqual(out["release"]["reason"], "mouth_substitution")
        self.assertIsNone(out["release_id"])
        verified = receipt_mod.verify_receipt_jwt(out["receipt"])
        self.assertTrue(verified["valid"])
        self.assertEqual(verified["payload"]["rel"], "NONEXIST")
        self.assertFalse(verified["payload"]["exists"])
        self.assertNotEqual(verified["payload"]["dec"], "EXIST")

    def test_tampered_exist_bit_fails_signature(self):
        out = rel_mod.evaluate(
            {"release": {"bill": _bill(), "authority": _authority(), "authorized": True}}
        )
        self.assertEqual(out["decision"], "NONEXIST")
        parts = out["receipt"].split(".")
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=="))
        payload["dec"] = "EXIST"
        payload["rel"] = "EXIST"
        payload["exists"] = True
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        tampered = (
            parts[0]
            + "."
            + base64.urlsafe_b64encode(raw).rstrip(b"=").decode()
            + "."
            + parts[2]
        )
        verified = receipt_mod.verify_receipt_jwt(tampered)
        self.assertFalse(verified["valid"])
        self.assertEqual(verified["reason"], "bad_signature")

    def test_package_does_not_import_gate(self):
        banned = [name for name in sys.modules if name == "gate" or name.startswith("gate.")]
        self.assertEqual(banned, [])


if __name__ == "__main__":
    unittest.main()
