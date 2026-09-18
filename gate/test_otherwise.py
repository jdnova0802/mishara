"""Otherwise witness — agency requires a live other write."""
from __future__ import annotations

import unittest

from gate import otherwise as otherwise_mod


class OtherwiseWitnessTests(unittest.TestCase):
    def test_one_open_is_non_act(self):
        out = otherwise_mod.witness(
            live=[
                {
                    "action": "wire.send",
                    "sink": "bank.rtp",
                    "fingerprint": "aa",
                    "exists": True,
                }
            ]
        )
        self.assertEqual(out["agency"], "NON-ACT")
        self.assertTrue(out["settled"])
        self.assertEqual(out["open_count"], 1)

    def test_two_open_is_act(self):
        out = otherwise_mod.witness(
            live=[
                {
                    "action": "wire.send",
                    "sink": "bank.rtp",
                    "fingerprint": "aa",
                    "exists": True,
                },
                {
                    "action": "wire.hold",
                    "sink": "bank.rtp",
                    "fingerprint": "bb",
                    "exists": True,
                },
            ]
        )
        self.assertEqual(out["agency"], "ACT")
        self.assertFalse(out["settled"])
        self.assertEqual(out["open_count"], 2)

    def test_thoughts_without_exists_do_not_count(self):
        out = otherwise_mod.witness(
            live=[
                {
                    "action": "wire.send",
                    "sink": "bank.rtp",
                    "fingerprint": "aa",
                    "exists": True,
                },
                {
                    "action": "thought",
                    "sink": "model",
                    "fingerprint": "cc",
                    "exists": False,
                },
            ]
        )
        self.assertEqual(out["agency"], "NON-ACT")
        self.assertEqual(out["open_count"], 1)

    def test_dedupe_fingerprint(self):
        out = otherwise_mod.witness(
            live=[
                {
                    "action": "wire.send",
                    "sink": "bank.rtp",
                    "fingerprint": "aa",
                    "exists": True,
                },
                {
                    "action": "wire.send",
                    "sink": "bank.rtp",
                    "fingerprint": "aa",
                    "exists": True,
                },
            ]
        )
        self.assertEqual(out["open_count"], 1)


if __name__ == "__main__":
    unittest.main()
