"""Tests for Bone Law — unextractable may."""
from __future__ import annotations

import unittest

try:
    from gate import bone_law as bl
except ImportError:
    import bone_law as bl


class BoneLawTests(unittest.TestCase):
    def test_bonded(self):
        r = bl.evaluate(
            mouth_in_bones=True,
            coordinator_bond_live=True,
            would_irreversible_write=True,
            surface_id="surf-1",
        )
        self.assertEqual(r["verdict"], "BONDED")
        self.assertTrue(r["unextractable"])
        self.assertTrue(r["may_proceed"])

    def test_sidecar_forged(self):
        r = bl.evaluate(
            sidecar_policy=True,
            would_irreversible_write=True,
        )
        self.assertEqual(r["verdict"], "SIDECAR_FORGED")
        self.assertFalse(r["may_proceed"])

    def test_amputated_on_extraction(self):
        r = bl.evaluate(
            extraction_attempted=True,
            mouth_in_bones=False,
            would_irreversible_write=True,
        )
        self.assertEqual(r["verdict"], "AMPUTATED")
        self.assertFalse(r["may_proceed"])

    def test_extraction_attempted_while_bonded(self):
        r = bl.evaluate(
            extraction_attempted=True,
            bypass_path=True,
            mouth_in_bones=True,
            would_irreversible_write=True,
        )
        self.assertEqual(r["verdict"], "EXTRACTION_ATTEMPTED")
        self.assertFalse(r["may_proceed"])

    def test_attach_halts_sidecar(self):
        plan = {
            "decision": "ALLOW",
            "allow_bind": True,
            "sidecar_policy": True,
            "would_bind": True,
        }
        bl.attach(plan, public_url="https://gate.example")
        self.assertEqual(plan["bone_law"]["verdict"], "SIDECAR_FORGED")
        self.assertEqual(plan.get("decision"), "HALT")
        self.assertFalse(plan.get("allow_bind"))

    def test_manifest(self):
        m = bl.manifest("https://gate.example")
        self.assertTrue(m["invisible_force"])
        self.assertIn("bone-law.json", m["well_known"])


if __name__ == "__main__":
    unittest.main()
