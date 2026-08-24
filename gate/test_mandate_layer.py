"""Tests for Mandate Layer (L3) — Nisaba stack above may."""
from __future__ import annotations

import unittest

try:
    from gate import mandate_layer as ml
except ImportError:
    import mandate_layer as ml


class MandateLayerTests(unittest.TestCase):
    def test_meta_sheath_deny_revoked(self):
        r = ml.meta_sheath_license_evaluate(
            would_mint_mouth=True,
            revoked=True,
            license_live=True,
            coordinator_attested=True,
        )
        self.assertEqual(r["verdict"], "LICENSE_DENY")
        self.assertFalse(r["may_proceed"])

    def test_meta_sheath_choke_unattested(self):
        r = ml.meta_sheath_license_evaluate(
            would_mint_mouth=True,
            license_live=True,
            coordinator_attested=False,
        )
        self.assertEqual(r["verdict"], "LICENSE_CHOKE")
        self.assertFalse(r["may_proceed"])

    def test_meta_sheath_live(self):
        r = ml.meta_sheath_license_evaluate(
            would_mint_mouth=True,
            license_live=True,
            coordinator_attested=True,
            issuer_id="nisaba",
            licensee_id="plant-a",
        )
        self.assertEqual(r["verdict"], "LICENSE_LIVE")
        self.assertTrue(r["may_proceed"])

    def test_restraint_clearing_settled(self):
        r = ml.restraint_clearing_evaluate(
            rho_mass=3.5,
            settle=True,
            window_id="w1",
            desk_id="d1",
        )
        self.assertEqual(r["verdict"], "CLEARING_SETTLED")
        self.assertTrue(r["clearing_id"].startswith("clr_"))

    def test_restraint_clearing_empty(self):
        r = ml.restraint_clearing_evaluate(rho_mass=0, settle=True)
        self.assertEqual(r["verdict"], "CLEARING_EMPTY")
        self.assertFalse(r["may_proceed"])

    def test_principal_ghost_may(self):
        r = ml.principal_continuity_evaluate(
            principal_dead=True,
            may_hooks_live=True,
        )
        self.assertEqual(r["verdict"], "GHOST_MAY")
        self.assertFalse(r["may_proceed"])

    def test_principal_handoff_forged(self):
        r = ml.principal_continuity_evaluate(
            handoff=True,
            stranger_attested=False,
            from_principal="a",
            to_principal="b",
        )
        self.assertEqual(r["verdict"], "HANDOFF_FORGED")

    def test_principal_continuity_live(self):
        r = ml.principal_continuity_evaluate(
            handoff=True,
            stranger_attested=True,
            from_principal="a",
            to_principal="b",
        )
        self.assertEqual(r["verdict"], "CONTINUITY_LIVE")
        self.assertTrue(r["continuity_id"].startswith("cont_"))

    def test_mouth_registry(self):
        r = ml.mouth_registry_stamp(
            mouth_id="mouth-1",
            semver="gate-mouth-v1",
            funeral_state="live",
        )
        self.assertEqual(r["verdict"], "REGISTERED")
        self.assertTrue(r["stranger_auditable"])

    def test_attach_blocks_mint(self):
        plan = {
            "decision": "ALLOW",
            "allow_bind": True,
            "would_mint_mouth": True,
            "meta_license_live": False,
            "meta_license_revoked": True,
        }
        ml.attach(plan, public_url="https://gate.example")
        self.assertIn("meta_sheath_license", plan["mandate_layer"]["blockers"])
        self.assertEqual(plan.get("decision"), "HALT")
        self.assertFalse(plan.get("allow_bind"))

    def test_manifest_pillars(self):
        m = ml.manifest("https://gate.example")
        self.assertEqual(len(m["pillars"]), 4)
        self.assertTrue(m["ahead_of_time"])
        self.assertIn("mandate-layer.json", m["well_known"])

    def test_stack_manifest(self):
        s = ml.stack_manifest("https://gate.example")
        self.assertIn("L3_mandate", s["layers"])
        self.assertTrue(s["layers"]["L2_may"]["ours"])
        self.assertFalse(s["layers"]["L0_can"]["ours"])


if __name__ == "__main__":
    unittest.main()
