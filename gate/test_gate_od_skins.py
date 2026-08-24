"""Tests for Gate-O / Gate-D skins + LARP gap pack."""
from __future__ import annotations

import unittest

try:
    from gate import gate_od_skins as skins
except ImportError:
    import gate_od_skins as skins


class GateODSkinsTests(unittest.TestCase):
    def test_civil_default(self):
        r = skins.classify(skin=None, edge_id="bind_issue")
        self.assertEqual(r["skin"], skins.SKIN_CIVIL)
        self.assertEqual(r["name"], "Gate-C")
        self.assertFalse(r["may_mint_weapon"])

    def test_defensive_panic_haunt(self):
        r = skins.classify(
            skin="gate_d",
            edge_id="protective_release",
            panic=True,
        )
        self.assertEqual(r["skin"], skins.SKIN_DEFENSIVE)
        self.assertEqual(r["mass_class"], skins.CLASS_SACRED)
        self.assertIn("panic_soft_yes", r["haunts"])
        self.assertTrue(r["charge_required"])

    def test_offensive_charisma_haunt(self):
        r = skins.classify(
            skin="o",
            edge_id="strike_release",
            boss_said_go=True,
        )
        self.assertEqual(r["skin"], skins.SKIN_OFFENSIVE)
        self.assertIn("charisma_soft_yes", r["haunts"])
        self.assertIn("charge_bride", r["invention_stack"])

    def test_loss_of_link_anti_perimeter(self):
        r = skins.classify(skin="gate_d", loss_of_link=True)
        self.assertIn("anti_perimeter_deny", r["haunts"])

    def test_stick_raises_mass(self):
        r = skins.classify(skin="gate_c", edge_id="bind_issue", stick_score=80)
        self.assertEqual(r["mass_class"], skins.CLASS_SACRED)

    def test_attach_raises_mass_tag_floor(self):
        plan = {
            "gate_skin": "gate_o",
            "edge_id": "charisma_go",
            "boss_said_go": True,
            "mass_tag": {"tag": "light", "mass_class": "light"},
        }
        skins.attach(plan, public_url="https://gate.example")
        self.assertEqual(plan["gate_od_skins"]["skin"], skins.SKIN_OFFENSIVE)
        self.assertEqual(plan["mass_tag"]["mass_class"], skins.CLASS_SACRED)
        self.assertIn("larp_gap_pack", plan["gate_od_skins"])

    def test_larp_gap_pack(self):
        pack = skins.larp_gap_pack("https://gate.example")
        firms = [g["firm"] for g in pack["gaps"]]
        self.assertEqual(firms, ["Lockheed", "Anduril", "Raytheon", "Palantir"])
        self.assertTrue(any("Sight" in g["gate_gap"] for g in pack["gaps"]))

    def test_manifest(self):
        m = skins.manifest("https://gate.example")
        self.assertEqual(m["spec"], skins.SPEC)
        self.assertIn("gate_d", m["skins"])
        self.assertIn("mass_table", m["manufactures"])


if __name__ == "__main__":
    unittest.main()
