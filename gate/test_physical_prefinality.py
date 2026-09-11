"""Physical Prefinality — park absolute kinetic writes before actuators."""
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
from gate import mandate as mandate_mod  # noqa: E402
from gate import physical_prefinality as phys_mod  # noqa: E402
from gate import sinks as sinks_mod  # noqa: E402
from gate import subject as subject_mod  # noqa: E402


class PhysicalPrefinalityTests(unittest.TestCase):
    def setUp(self):
        mandate_mod._reset_for_tests()
        admit_mod._reset_for_tests()
        subject_mod._reset_for_tests()
        phys_mod._reset_for_tests()
        sinks_mod._reset_for_tests()

    def test_absolute_physical_sinks_seeded(self):
        for sid in (
            "device.actuate",
            "vehicle.control",
            "drone.actuate",
            "grid.switch",
            "industrial.plc",
            "medical.actuate",
        ):
            lane = phys_mod.is_absolute_physical(sid)
            self.assertTrue(lane["absolute_physical"], sid)

        soft = phys_mod.is_absolute_physical("email.send")
        self.assertFalse(soft["absolute_physical"])

    def test_park_without_human_root(self):
        out = phys_mod.evaluate(
            {
                "action": "drive.forward",
                "sink": "vehicle.control",
                "actor": "agent:fleet",
            },
            public_url="https://gate.test",
        )
        self.assertEqual(out["outcome"], "PARKED")
        self.assertEqual(out["reason"], "human_root_required")
        self.assertTrue(out["park_id"])
        self.assertTrue(phys_mod.get_park(out["park_id"]))

    def test_park_without_at_risk_subject(self):
        out = phys_mod.evaluate(
            {
                "action": "drive.forward",
                "sink": "vehicle.control",
                "actor": "agent:fleet",
                "human_principal_id": "human:ops",
                "mandate_id": "mandate_missing",
            },
            public_url="https://gate.test",
        )
        self.assertEqual(out["outcome"], "PARKED")
        self.assertEqual(out["reason"], "at_risk_subject_required")

    def test_admittance_halts_on_absolute_physical_park(self):
        halted = admit_mod.admit(
            {
                "action": "arm.extend",
                "sink": "device.actuate",
                "actor": "agent:robot",
                "human_principal_id": "human:ops",
            },
            public_url="https://gate.test",
        )
        self.assertEqual(halted["outcome"], "HALTED")
        self.assertTrue(str(halted["reason"]).startswith("physical_"))
        self.assertTrue(halted.get("park_id") or (halted.get("physical") or {}).get("park_id"))

    def test_cleared_absolute_physical_then_admit(self):
        root = mandate_mod.issue_root(
            human_principal_id="human:ops",
            agent_id="agent:robot",
            scope={
                "actions": ["arm.extend"],
                "sinks": ["device.actuate"],
                "max_amount": 1,
            },
            approval_bytes="move",
        )
        mid = root["mandate"]["mandate_id"]
        subject_mod.register(subject_id="human:bystander")
        clr = subject_mod.clear(
            subject_id="human:bystander",
            action="arm.extend",
            sink="device.actuate",
            actor="agent:robot",
        )
        self.assertTrue(clr["ok"], clr)

        phys = phys_mod.evaluate(
            {
                "action": "arm.extend",
                "sink": "device.actuate",
                "actor": "agent:robot",
                "human_principal_id": "human:ops",
                "mandate_id": mid,
                "subject_id": "human:bystander",
                "subject_clearance_id": clr["clearance"]["clearance_id"],
            },
            public_url="https://gate.test",
        )
        self.assertEqual(phys["outcome"], "CLEARED", phys)

        admitted = admit_mod.admit(
            {
                "action": "arm.extend",
                "sink": "device.actuate",
                "actor": "agent:robot",
                "human_principal_id": "human:ops",
                "mandate_id": mid,
                "subject_id": "human:bystander",
                "subject_clearance_id": clr["clearance"]["clearance_id"],
            },
            public_url="https://gate.test",
        )
        self.assertEqual(admitted["outcome"], "ADMITTED", admitted)


if __name__ == "__main__":
    unittest.main()
