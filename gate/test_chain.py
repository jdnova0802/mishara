"""Chain witness — weakest parent claim wins."""
from __future__ import annotations

import unittest

from gate import chain as chain_mod


class ChainWitnessTests(unittest.TestCase):
    def test_no_upstream_is_clean(self):
        out = chain_mod.witness(
            current={"agency": "NON-ACT", "decision": "EXIST", "mutation": "ABSENT"}
        )
        self.assertEqual(out["grade"], "CLEAN")
        self.assertFalse(out["halt"])
        self.assertEqual(out["upstream_count"], 0)
        self.assertFalse(out["upstream_gap"])

    def test_parent_non_act_stains_not_halt(self):
        out = chain_mod.witness(
            current={"agency": "ACT", "decision": "EXIST", "mutation": "SAME", "in_authority": "IN"},
            upstream=[
                {"agency": "NON-ACT", "decision": "EXIST", "mutation": "ABSENT", "in_authority": "IN"}
            ],
        )
        self.assertEqual(out["grade"], "STAINED")
        self.assertEqual(out["min_agency"], "NON-ACT")
        self.assertFalse(out["halt"])

    def test_parent_signing_down_stains(self):
        out = chain_mod.witness(
            current={"agency": "ACT", "decision": "EXIST", "mutation": "SAME", "in_authority": "IN"},
            upstream=[
                {
                    "agc": "ACT",
                    "dec": "EXIST",
                    "mut": "DOWN",
                    "iaa": "IN",
                }
            ],
        )
        self.assertEqual(out["grade"], "STAINED")
        self.assertEqual(out["mutation"], "DOWN")
        self.assertFalse(out["halt"])

    def test_parent_nonexist_is_rotten(self):
        floor = chain_mod.floor(
            [chain_mod.claim_from_payload({"dec": "NONEXIST", "agc": "NON-ACT"})]
        )
        self.assertTrue(floor["halt"])
        out = chain_mod.witness(
            current={"agency": "ACT", "decision": "EXIST", "in_authority": "IN"},
            upstream=[chain_mod.claim_from_payload({"dec": "NONEXIST"})],
        )
        self.assertEqual(out["grade"], "ROTTEN")
        self.assertTrue(out["halt"])

    def test_unverified_parent_is_rotten(self):
        claims = chain_mod.collect(["not-a-jwt"], decode=lambda _t: {"valid": False})
        self.assertTrue(chain_mod.floor(claims)["halt"])
        self.assertTrue(claims[0]["unverified"])


if __name__ == "__main__":
    unittest.main()
