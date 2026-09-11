"""Admittance — three-civilization compressor tests."""
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
from gate import continuity as continuity_mod  # noqa: E402
from gate import finder as finder_mod  # noqa: E402
from gate import mandate as mandate_mod  # noqa: E402


class AdmittanceTests(unittest.TestCase):
    def setUp(self):
        mandate_mod._reset_for_tests()
        continuity_mod._reset_for_tests()
        finder_mod._reset_for_tests()
        admit_mod._reset_for_tests()

    def _root(self, principal="human:mega", agent="agent:ops", amount=50):
        root = mandate_mod.issue_root(
            human_principal_id=principal,
            agent_id=agent,
            scope={
                "actions": ["wire.send"],
                "sinks": ["bank.rtp"],
                "max_amount": amount,
            },
            approval_bytes="approve civilization compressor",
        )
        self.assertTrue(root["ok"], root)
        return root["mandate"]

    def test_admit_mints_world_fact(self):
        m = self._root()
        out = admit_mod.admit(
            {
                "action": "wire.send",
                "sink": "bank.rtp",
                "actor": "agent:ops",
                "args": {"amount": 10},
                "mandate_id": m["mandate_id"],
                "human_principal_id": "human:mega",
                "lineage_id": "lineage:mega",
            },
            public_url="https://gate.test",
        )
        self.assertEqual(out["outcome"], "ADMITTED", out)
        self.assertTrue(out["ok"])
        self.assertTrue(out["fact"]["fact_id"])
        self.assertEqual(out["fact"]["lineage_id"], "lineage:mega")
        got = admit_mod.get_fact(out["fact"]["fact_id"])
        self.assertIsNotNone(got)
        hits = finder_mod.search("worldwrite", limit=10)
        self.assertGreaterEqual(hits["count"], 1)

    def test_subject_refusal_blocks_world_write(self):
        m = self._root()
        out = admit_mod.admit(
            {
                "action": "wire.send",
                "sink": "bank.rtp",
                "actor": "agent:ops",
                "args": {"amount": 5},
                "mandate_id": m["mandate_id"],
                "subject_id": "human:payee",
                "subject_refuse": True,
            },
            public_url="https://gate.test",
        )
        self.assertEqual(out["outcome"], "REFUSED", out)
        self.assertIn(out["reason"], ("subject_refused", "subject_refuse"))

    def test_death_makes_admittance_dead(self):
        m = self._root()
        death = mandate_mod.die(mandate_id=m["mandate_id"], reason="compressor")
        self.assertTrue(death["ok"], death)
        out = admit_mod.admit(
            {
                "action": "wire.send",
                "sink": "bank.rtp",
                "actor": "agent:ops",
                "args": {"amount": 1},
                "mandate_id": m["mandate_id"],
            },
            public_url="https://gate.test",
        )
        self.assertEqual(out["outcome"], "DEAD", out)

    def test_continuity_departure_kills_new_admits(self):
        m = self._root(principal="human:leaving")
        cont = continuity_mod.record(
            human_principal_id="human:leaving",
            event="departure",
            reason="left",
            public_url="https://gate.test",
        )
        self.assertTrue(cont["ok"], cont)
        out = admit_mod.admit(
            {
                "action": "wire.send",
                "sink": "bank.rtp",
                "actor": "agent:ops",
                "args": {"amount": 1},
                "mandate_id": m["mandate_id"],
                "human_principal_id": "human:leaving",
            },
            public_url="https://gate.test",
        )
        self.assertEqual(out["outcome"], "DEAD", out)


if __name__ == "__main__":
    unittest.main()
