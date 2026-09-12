"""Finder + sinks + continuity + mortality federation — the Google that never happened."""
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

from gate import continuity as continuity_mod  # noqa: E402
from gate import finder as finder_mod  # noqa: E402
from gate import mandate as mandate_mod  # noqa: E402
from gate import right_to_act as rta  # noqa: E402
from gate import sinks as sinks_mod  # noqa: E402


class FinderStackTests(unittest.TestCase):
    def setUp(self):
        mandate_mod._reset_for_tests()
        continuity_mod._reset_for_tests()
        finder_mod._reset_for_tests()
        sinks_mod._reset_for_tests()

    def test_sink_registry_types_consequence(self):
        row = sinks_mod.get("bank.rtp")
        self.assertIsNotNone(row)
        self.assertEqual(row["class"], "monetary")
        self.assertEqual(row["irreversibility"], "hard")
        self.assertTrue(row["burn_required"])

        unknown = sinks_mod.require_for_act("totally.unknown.sink")
        self.assertFalse(unknown["known"])
        self.assertTrue(unknown["burn_required"])
        self.assertEqual(unknown["irreversibility"], "hard")

        custom = sinks_mod.register(
            sink_id="robot.grip.release",
            sink_class="physical",
            irreversibility="absolute",
            description="Release industrial gripper",
        )
        self.assertTrue(custom["ok"], custom)
        hits = finder_mod.search("robot.grip", kind="sink")
        self.assertGreaterEqual(hits["count"], 1)
        self.assertTrue(any(r.get("sink_id") == "robot.grip.release" for r in hits["results"]))

    def test_refusal_and_death_are_searchable(self):
        root = mandate_mod.issue_root(
            human_principal_id="human:finder",
            agent_id="agent:ops",
            scope={"actions": ["wire.send"], "sinks": ["bank.rtp"], "max_amount": 20},
            approval_bytes="approve finder",
        )
        self.assertTrue(root["ok"], root)
        mid = root["mandate"]["mandate_id"]

        denied = rta.evaluate(
            {
                "action": "wire.send",
                "sink": "bank.rtp",
                "actor": "agent:ops",
                "args": {"amount": 999},
                "mandate_id": mid,
                "policy": {"require_mandate": True, "max_amount": 5},
            },
            public_url="https://gate.test",
        )
        self.assertEqual(denied["decision"], "NONEXIST", denied)
        self.assertTrue(denied.get("refusal_digest"))

        refusals = finder_mod.search("wire.send", kind="refusal")
        self.assertGreaterEqual(refusals["count"], 1)

        death = mandate_mod.die(
            mandate_id=mid, reason="finder test", public_url="https://gate.test"
        )
        self.assertTrue(death["ok"], death)
        deaths = finder_mod.search("finder test", kind="death")
        self.assertGreaterEqual(deaths["count"], 1)
        death_id = death["death_certificate"]["death_id"]
        self.assertTrue(any(r.get("death_id") == death_id for r in deaths["results"]))

    def test_continuity_cascades_and_indexes(self):
        root = mandate_mod.issue_root(
            human_principal_id="human:leaving",
            agent_id="agent:ops",
            scope={"actions": ["wire.send"], "sinks": ["bank.rtp"], "max_amount": 10},
            approval_bytes="approve",
        )
        self.assertTrue(root["ok"], root)

        cont = continuity_mod.record(
            human_principal_id="human:leaving",
            event="departure",
            reason="left the company",
            public_url="https://gate.test",
        )
        self.assertTrue(cont["ok"], cont)
        status = continuity_mod.is_non_authorizing("human:leaving")
        self.assertTrue(status["non_authorizing"], status)

        hits = finder_mod.search("departure", kind="continuity")
        self.assertGreaterEqual(hits["count"], 1)

        refused = mandate_mod.issue_root(
            human_principal_id="human:leaving",
            agent_id="agent:ops2",
            scope={"actions": ["wire.send"], "sinks": ["bank.rtp"], "max_amount": 5},
            approval_bytes="should fail",
        )
        self.assertFalse(refused["ok"])

    def test_mortality_federation_ingest(self):
        live = mandate_mod.issue_root(
            human_principal_id="human:fed",
            agent_id="agent:fed",
            scope={"actions": ["wire.send"], "sinks": ["bank.rtp"], "max_amount": 10},
            approval_bytes="fed",
        )
        self.assertTrue(live["ok"], live)
        d2 = mandate_mod.die(agent_id="agent:fed", reason="federate")
        self.assertTrue(d2["ok"], d2)
        cert2 = d2["death_certificate"]

        exported = mandate_mod.export_deaths()
        self.assertGreaterEqual(exported["count"], 1)
        self.assertTrue(any(c.get("death_id") == cert2["death_id"] for c in exported["deaths"]))

        # Peer node: fresh store, live mandate under same agent, then ingest foreign death.
        mandate_mod._reset_for_tests()
        peer_live = mandate_mod.issue_root(
            human_principal_id="human:fed",
            agent_id="agent:fed",
            scope={"actions": ["wire.send"], "sinks": ["bank.rtp"], "max_amount": 10},
            approval_bytes="fed-again",
        )
        self.assertTrue(peer_live["ok"], peer_live)

        ingested = mandate_mod.ingest_death(cert2, peer="https://peer.gate.test")
        self.assertTrue(ingested["ok"], ingested)

        dead = mandate_mod.is_dead(agent_id="agent:fed")
        self.assertTrue(dead.get("dead"), dead)

        recon = mandate_mod.reconstruct(
            mandate_id=peer_live["mandate"]["mandate_id"],
            action="wire.send",
            sink="bank.rtp",
            amount=1,
            agent_id="agent:fed",
        )
        self.assertEqual(recon["outcome"], "DENY")
        self.assertEqual(recon["reason"], "dead")


if __name__ == "__main__":
    unittest.main()
