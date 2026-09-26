"""Tests for OpenTimestamps evidence-head anchor (no live calendar required)."""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")

import evidence_log  # noqa: E402
import ots_anchor  # noqa: E402


class OtsAnchorUnitTests(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.ots_dir = Path(self._td.name)
        os.environ["GATE_OTS_DIR"] = str(self.ots_dir)
        os.environ["GATE_OTS_ENABLED"] = "1"

    def tearDown(self):
        self._td.cleanup()

    def test_commitment_canonical_and_digest(self):
        raw = ots_anchor.commitment_bytes(tree_size=0, root_hash="AbCd")
        self.assertTrue(raw.endswith(b"\n"))
        obj = json.loads(raw)
        self.assertEqual(obj["spec"], "gate-ots-commitment-v1")
        self.assertEqual(obj["tree_size"], 0)
        self.assertEqual(obj["root_hash"], "abcd")
        # Sorted keys
        self.assertEqual(list(obj.keys()), ["root_hash", "spec", "tree_size"])
        d = ots_anchor.commitment_digest_hex(tree_size=0, root_hash="abcd")
        self.assertEqual(d, hashlib.sha256(raw).hexdigest())

    def test_stamp_idempotent_with_fake_cli(self):
        root = evidence_log.merkle_root([])
        fake_ots = b"\x00OTSFAKEPROOF\x00"

        def fake_cli_stamp(commitment_path, ots_path):
            ots_path.parent.mkdir(parents=True, exist_ok=True)
            ots_path.write_bytes(fake_ots)
            return {"ok": True, "method": "fake"}

        with mock.patch.object(ots_anchor, "_stamp_via_cli", side_effect=fake_cli_stamp):
            with mock.patch.object(
                ots_anchor, "_stamp_via_library", return_value={"ok": False}
            ):
                first = ots_anchor.stamp_root(tree_size=0, root_hash=root)
                second = ots_anchor.stamp_root(tree_size=0, root_hash=root)

        self.assertTrue(first["ok"])
        self.assertEqual(first["event"], "stamped")
        self.assertTrue(second["ok"])
        self.assertEqual(second["event"], "already_stamped")
        self.assertTrue(Path(first["ots_path"]).exists())
        self.assertEqual(Path(first["ots_path"]).read_bytes(), fake_ots)

        head = evidence_log.signed_tree_head([])
        self.assertIn("opentimestamps", head)
        ots = head["opentimestamps"]
        self.assertTrue(ots.get("configured"))
        self.assertTrue(ots.get("matches_this_head"))
        self.assertEqual(ots.get("status"), "pending")

    def test_parse_info_bitcoin_height(self):
        sample = """
File sha256 hash: abc
Timestamp:
verify PendingAttestation('https://alice.btc.calendar.opentimestamps.org')
verify BitcoinBlockHeaderAttestation(840000)
"""
        parsed = ots_anchor._parse_info(sample)
        self.assertEqual(parsed["status"], "bitcoin_confirmed")
        self.assertEqual(parsed["bitcoin_block_height"], 840000)

    def test_attach_unanchored_capacity(self):
        head = {"tree_size": 0, "root_hash": "00" * 32}
        out = ots_anchor.attach_to_tree_head(head)
        self.assertEqual(out["opentimestamps"]["configured"], False)
        self.assertEqual(out["opentimestamps"]["status"], "unanchored")


if __name__ == "__main__":
    unittest.main()
