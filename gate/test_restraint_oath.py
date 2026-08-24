"""Tests for Restraint Unit (ρ) and Oath Compiler."""
from __future__ import annotations

import unittest

try:
    from gate import restraint_unit as ru
    from gate import oath_compiler as oc
except ImportError:
    import restraint_unit as ru
    import oath_compiler as oc


class RestraintUnitTests(unittest.TestCase):
    def test_mint_sacred_halt(self):
        r = ru.mint(decision="HALT", acted=False, mass_class="sacred")
        self.assertTrue(r["minted"])
        self.assertEqual(r["rho_raw"], 1)
        self.assertEqual(r["rho_mass"], 9)

    def test_mint_allow_zero(self):
        r = ru.mint(decision="ALLOW", acted=True, mass_class="sacred")
        self.assertFalse(r["minted"])
        self.assertEqual(r["rho_mass"], 0)

    def test_ledger_joins_kappa(self):
        led = ru.ledger(
            [
                {"decision": "HALT", "acted": False, "mass_class": "heavy"},
                {"decision": "ALLOW", "acted": True, "mass_class": "light"},
            ]
        )
        self.assertEqual(led["rho_raw_total"], 1)
        self.assertEqual(led["rho_mass_total"], 3)
        self.assertEqual(led["kappa"], 0.5)

    def test_attach_on_halt_plan(self):
        plan = {
            "decision": "HALT",
            "acted": False,
            "halt": True,
            "allow_bind": False,
            "mass_tag": {"tag": "sacred", "mass_class": "sacred"},
        }
        ru.attach(plan, public_url="https://gate.example")
        self.assertTrue(plan["restraint_unit"]["minted"])
        self.assertEqual(plan["restraint_unit"]["rho_mass"], 9)

    def test_manifest(self):
        m = ru.manifest("https://gate.example")
        self.assertEqual(m["symbol"], "ρ")
        self.assertIn("rho_mass", m["formula"])


class OathCompilerTests(unittest.TestCase):
    def test_pas_bind_preset(self):
        g = oc.compile_preset("pas_bind")
        self.assertTrue(g["executable"])
        self.assertEqual(g["preset"], "pas_bind")
        self.assertGreaterEqual(g["node_count"], 6)

    def test_force_roe_preset(self):
        g = oc.compile_preset("force_roe")
        self.assertTrue(g["executable"])
        self.assertEqual(g["preset"], "force_roe_seed")

    def test_unknown_clause_chokes(self):
        g = oc.compile_clauses([{"kind": "not_a_real_kind", "label": "bogus"}])
        self.assertTrue(g["errors"])
        self.assertFalse(g["executable"])
        ops = [n["op"] for n in g["nodes"] if n.get("source_clause") == "not_a_real_kind"]
        self.assertIn(oc.OP_CHOKE, ops)

    def test_quorum_clause(self):
        g = oc.compile_clauses(
            [{"id": "q1", "kind": "require_quorum", "n": 2, "label": "two mouths"}]
        )
        self.assertTrue(g["executable"])
        req = [n for n in g["nodes"] if n.get("op") == oc.OP_REQUIRE]
        self.assertTrue(req)

    def test_attach_default_pas(self):
        plan = {"job_id": "pc:1"}
        oc.attach(plan, public_url="https://gate.example")
        self.assertIn("oath_compiler", plan)
        self.assertEqual(plan["oath_compiler"]["preset"], "pas_bind")

    def test_manifest(self):
        m = oc.manifest("https://gate.example")
        self.assertEqual(m["spec"], oc.SPEC)
        self.assertIn("require_quorum", m["clause_kinds"])


if __name__ == "__main__":
    unittest.main()
