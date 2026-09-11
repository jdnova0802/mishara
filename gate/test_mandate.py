"""Mandate + reconstructive authority at Right-to-Act burn time."""
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

from gate import mandate as mandate_mod  # noqa: E402
from gate import right_to_act as rta  # noqa: E402


class MandateTests(unittest.TestCase):
    def setUp(self):
        mandate_mod._reset_for_tests()

    def test_root_attenuate_revoke_cascade(self):
        root = mandate_mod.issue_root(
            human_principal_id="human:demond",
            agent_id="agent:ops",
            scope={
                "actions": ["wire.send", "wire.schedule"],
                "sinks": ["bank.rtp", "bank.ach"],
                "max_amount": 100,
            },
            ttl_seconds=3600,
            approval_bytes="I approve agent:ops within policy v1",
        )
        self.assertTrue(root["ok"], root)
        mid = root["mandate"]["mandate_id"]

        child = mandate_mod.attenuate(
            parent_id=mid,
            scope={"actions": ["wire.send"], "sinks": ["bank.rtp"], "max_amount": 25},
        )
        self.assertTrue(child["ok"], child)

        widen = mandate_mod.attenuate(
            parent_id=mid,
            scope={"actions": ["wire.send"], "sinks": ["bank.rtp"], "max_amount": 500},
        )
        self.assertFalse(widen["ok"])
        self.assertEqual(widen["reason"], "widening_forbidden")

        admit = mandate_mod.reconstruct(
            mandate_id=child["mandate"]["mandate_id"],
            action="wire.send",
            sink="bank.rtp",
            amount=10,
            agent_id="agent:ops",
        )
        self.assertEqual(admit["outcome"], "ADMIT")

        deny = mandate_mod.reconstruct(
            mandate_id=child["mandate"]["mandate_id"],
            action="wire.send",
            sink="bank.rtp",
            amount=50,
            agent_id="agent:ops",
        )
        self.assertEqual(deny["outcome"], "DENY")

        revoked = mandate_mod.revoke(mid, reason="compromise")
        self.assertTrue(revoked["ok"])
        self.assertIn(child["mandate"]["mandate_id"], revoked["revoked"])

        after = mandate_mod.reconstruct(
            mandate_id=child["mandate"]["mandate_id"],
            action="wire.send",
            sink="bank.rtp",
            amount=5,
            agent_id="agent:ops",
        )
        self.assertEqual(after["outcome"], "DENY")
        self.assertEqual(after["reason"], "revoked")

    def test_right_to_act_requires_living_mandate_at_burn(self):
        root = mandate_mod.issue_root(
            human_principal_id="human:demond",
            agent_id="agent:ops",
            scope={"actions": ["wire.send"], "sinks": ["bank.rtp"], "max_amount": 20},
            approval_bytes="approve",
        )
        mid = root["mandate"]["mandate_id"]

        go = rta.evaluate(
            {
                "action": "wire.send",
                "sink": "bank.rtp",
                "actor": "agent:ops",
                "args": {"amount": 5},
                "mandate_id": mid,
                "policy": {"require_mandate": True},
            },
            public_url="https://gate.test",
        )
        self.assertEqual(go["decision"], "EXIST", go)
        self.assertTrue(go["ticket_id"])
        self.assertEqual(go["reconstruction"]["outcome"], "ADMIT")

        burned = rta.burn_ticket(
            go["ticket_id"], fingerprint=go["fingerprint"], sink="bank.rtp"
        )
        self.assertTrue(burned["ok"], burned)
        self.assertEqual(burned["reconstruction"]["outcome"], "ADMIT")

        # Fresh EXIST then revoke before burn → burn HALT/DENY
        go2 = rta.evaluate(
            {
                "action": "wire.send",
                "sink": "bank.rtp",
                "actor": "agent:ops",
                "args": {"amount": 5},
                "mandate_id": mid,
                "policy": {"require_mandate": True},
            },
            public_url="https://gate.test",
        )
        self.assertEqual(go2["decision"], "EXIST", go2)
        mandate_mod.revoke(mid, reason="kill")
        blocked = rta.burn_ticket(
            go2["ticket_id"], fingerprint=go2["fingerprint"], sink="bank.rtp"
        )
        self.assertFalse(blocked["ok"])
        self.assertIn(
            blocked["reason"],
            ("mandate_revoked", "mandate_denied", "mandate_halt"),
        )


    def test_mortality_blocks_burn_and_stranger_verifies(self):
        root = mandate_mod.issue_root(
            human_principal_id="human:demond",
            agent_id="agent:ops",
            scope={"actions": ["wire.send"], "sinks": ["bank.rtp"], "max_amount": 20},
            approval_bytes="approve mortality",
        )
        self.assertTrue(root["ok"], root)
        mid = root["mandate"]["mandate_id"]
        child = mandate_mod.attenuate(
            parent_id=mid,
            scope={"actions": ["wire.send"], "sinks": ["bank.rtp"], "max_amount": 10},
        )
        self.assertTrue(child["ok"], child)
        child_id = child["mandate"]["mandate_id"]

        go = rta.evaluate(
            {
                "action": "wire.send",
                "sink": "bank.rtp",
                "actor": "agent:ops",
                "args": {"amount": 5},
                "mandate_id": child_id,
                "policy": {"require_mandate": True},
            },
            public_url="https://gate.test",
        )
        self.assertEqual(go["decision"], "EXIST", go)

        death = mandate_mod.die(mandate_id=mid, reason="compromise", public_url="https://gate.test")
        self.assertTrue(death["ok"], death)
        cert = death["death_certificate"]
        self.assertEqual(cert["spec"], mandate_mod.DEATH_SPEC)
        self.assertIn(child_id, death["cascade_killed"])
        self.assertTrue(death["well_known"].endswith(f"/.well-known/deaths/{cert['death_id']}.json"))

        verified = mandate_mod.verify_death(cert)
        self.assertTrue(verified["valid"], verified)
        by_id = mandate_mod.verify_death(death_id=cert["death_id"])
        self.assertTrue(by_id["valid"], by_id)

        after = mandate_mod.reconstruct(
            mandate_id=child_id,
            action="wire.send",
            sink="bank.rtp",
            amount=5,
            agent_id="agent:ops",
        )
        self.assertEqual(after["outcome"], "DENY")
        self.assertEqual(after["reason"], "dead")

        blocked = rta.burn_ticket(
            go["ticket_id"], fingerprint=go["fingerprint"], sink="bank.rtp"
        )
        self.assertFalse(blocked["ok"])
        self.assertEqual(blocked["reason"], "mandate_dead")

        # Sibling tree under a different root/agent stays alive when only this mandate died.
        other = mandate_mod.issue_root(
            human_principal_id="human:other",
            agent_id="agent:other",
            scope={"actions": ["wire.send"], "sinks": ["bank.rtp"], "max_amount": 5},
            approval_bytes="other root",
        )
        self.assertTrue(other["ok"], other)

        # Dead agent cannot receive new roots.
        agent_death = mandate_mod.die(agent_id="agent:ops", reason="agent mortality")
        self.assertTrue(agent_death["ok"], agent_death)
        refused = mandate_mod.issue_root(
            human_principal_id="human:demond",
            agent_id="agent:ops",
            scope={"actions": ["wire.send"], "sinks": ["bank.rtp"], "max_amount": 5},
            approval_bytes="should fail",
        )
        self.assertFalse(refused["ok"])
        self.assertEqual(refused["reason"], "dead_agent")


if __name__ == "__main__":
    unittest.main()
