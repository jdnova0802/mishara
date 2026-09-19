"""Subject Sovereignty — meterable clear / refuse / verify."""
from __future__ import annotations

import base64
import os
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

os.environ["GATE_DEV_MODE"] = "0"
_key = Ed25519PrivateKey.generate()
_priv = _key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
_pub = _key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
os.environ["GATE_RECEIPT_PRIVATE_KEY"] = base64.b64encode(_priv).decode()
os.environ["GATE_RECEIPT_PUBLIC_KEY"] = base64.b64encode(_pub).decode()

from gate import admittance as admit_mod  # noqa: E402
from gate import finder as finder_mod  # noqa: E402
from gate import mandate as mandate_mod  # noqa: E402
from gate import subject as subject_mod  # noqa: E402


class SubjectSovereigntyTests(unittest.TestCase):
    def setUp(self):
        mandate_mod._reset_for_tests()
        finder_mod._reset_for_tests()
        admit_mod._reset_for_tests()
        subject_mod._reset_for_tests()

    def test_refuse_verify_and_block_clearance(self):
        ref = subject_mod.refuse(
            subject_id="human:payee",
            action="wire.send",
            sink="bank.rtp",
            actor="agent:ops",
            reason="do_not_write_me",
            public_url="https://gate.test",
        )
        self.assertTrue(ref["ok"], ref)
        self.assertTrue(ref["meter"]["billable"])
        self.assertTrue(ref["refusal"]["refusal_digest"])

        verified = subject_mod.verify(ref["refusal"])
        self.assertTrue(verified["valid"], verified)
        self.assertTrue(verified["meter"]["billable"])

        blocked = subject_mod.clear(
            subject_id="human:payee",
            action="wire.send",
            sink="bank.rtp",
            actor="agent:ops",
        )
        self.assertFalse(blocked["ok"])
        self.assertEqual(blocked["reason"], "subject_refused")

    def test_clearance_required_for_admit_against_subject(self):
        root = mandate_mod.issue_root(
            human_principal_id="human:payer",
            agent_id="agent:ops",
            scope={
                "actions": ["wire.send"],
                "sinks": ["bank.rtp"],
                "max_amount": 20,
            },
            approval_bytes="pay",
        )
        mid = root["mandate"]["mandate_id"]

        denied = admit_mod.admit(
            {
                "action": "wire.send",
                "sink": "bank.rtp",
                "actor": "agent:ops",
                "args": {"amount": 5},
                "mandate_id": mid,
                "subject_id": "human:payee",
            },
            public_url="https://gate.test",
        )
        self.assertEqual(denied["outcome"], "REFUSED", denied)
        self.assertEqual(denied["reason"], "subject_clearance_required")

        clr = subject_mod.clear(
            subject_id="human:payee",
            action="wire.send",
            sink="bank.rtp",
            actor="agent:ops",
            public_url="https://gate.test",
        )
        self.assertTrue(clr["ok"], clr)

        ok = admit_mod.admit(
            {
                "action": "wire.send",
                "sink": "bank.rtp",
                "actor": "agent:ops",
                "args": {"amount": 5},
                "mandate_id": mid,
                "subject_id": "human:payee",
                "subject_clearance_id": clr["clearance"]["clearance_id"],
            },
            public_url="https://gate.test",
        )
        self.assertEqual(ok["outcome"], "ADMITTED", ok)
        self.assertTrue((ok.get("meter") or {}).get("billable"))


if __name__ == "__main__":
    unittest.main()
