"""Operator cosign — machine key is not a mouth."""
from __future__ import annotations

import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from gate import cosign as cosign_mod


class CosignWitnessTests(unittest.TestCase):
    def test_unpinned_is_gap_not_halt(self):
        out = cosign_mod.witness(
            machine_fpr="aa",
            operator_fpr=None,
            verified=False,
            required=False,
            signature_present=False,
        )
        self.assertEqual(out["status"], "GAP")
        self.assertFalse(out["halt"])
        self.assertTrue(out["gap"])

    def test_required_unsigned_is_hold(self):
        out = cosign_mod.witness(
            machine_fpr="aa",
            operator_fpr="bb",
            verified=False,
            required=True,
            signature_present=False,
        )
        self.assertEqual(out["status"], "HOLD")
        self.assertTrue(out["halt"])
        self.assertEqual(out["reason"], "operator_unsigned")

    def test_same_fingerprint_is_substitution(self):
        out = cosign_mod.witness(
            machine_fpr="aa",
            operator_fpr="aa",
            verified=True,
            required=True,
            signature_present=True,
        )
        self.assertEqual(out["status"], "BAD")
        self.assertTrue(out["halt"])
        self.assertEqual(out["reason"], "role_substitution")
        self.assertFalse(out["verified"])

    def test_sign_and_verify(self):
        from cryptography.hazmat.primitives.serialization import (
            Encoding,
            NoEncryption,
            PrivateFormat,
            PublicFormat,
        )

        key = Ed25519PrivateKey.generate()
        priv = key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
        pub = key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        claims = {
            "fp": "abc",
            "dec": "EXIST",
            "act": "wire.send",
            "sink": "bank.rtp",
            "owh": "0" * 64,
            "agc": "ACT",
            "nst": "SAT",
            "stl": None,
            "mut": "ABSENT",
            "iaa": "UNKNOWN",
            "chn": "CLEAN",
            "cma": "ACT",
            "ugp": "OK",
        }
        sig = cosign_mod.sign(claims=claims, private_key=priv)
        self.assertTrue(cosign_mod.verify_sig(claims=claims, signature=sig, public_key=pub))
        claims["dec"] = "NONEXIST"
        self.assertFalse(cosign_mod.verify_sig(claims=claims, signature=sig, public_key=pub))


if __name__ == "__main__":
    unittest.main()
