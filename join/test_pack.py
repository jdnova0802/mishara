"""Two halves, same hash. Draft, same-half, dead window never GO."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from join.pack import SPEC, attach_join, join_sha256, reasons_not_go, verdict  # noqa: E402

NOW = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
STARTER = "starter-half-alpha"
SEALER = "sealer-half-bravo"


def good_raw() -> dict:
    return {
        "spec": SPEC,
        "what": "boom",
        "not_before": "2026-01-01T00:00:00+00:00",
        "not_after": "2026-12-31T23:59:59+00:00",
        "starter_id": "watch-a",
        "sealer_id": "watch-b",
    }


class JoinTests(unittest.TestCase):
    def test_two_people_same_hash(self) -> None:
        a = attach_join(good_raw(), STARTER, SEALER)
        b = attach_join(good_raw(), STARTER, SEALER)
        self.assertEqual(a["join_sha256"], b["join_sha256"])
        self.assertEqual(join_sha256(a, STARTER, SEALER), a["join_sha256"])

    def test_go_when_complete(self) -> None:
        pack = attach_join(good_raw(), STARTER, SEALER)
        self.assertEqual(verdict(pack, STARTER, SEALER, NOW), "GO")
        self.assertEqual(reasons_not_go(pack, STARTER, SEALER, NOW), [])

    def test_draft_is_no(self) -> None:
        pack = good_raw()
        self.assertEqual(verdict(pack, STARTER, SEALER, NOW), "NO")
        self.assertTrue(any("draft" in w for w in reasons_not_go(pack, STARTER, SEALER, NOW)))

    def test_same_half_is_no(self) -> None:
        pack = attach_join(good_raw(), STARTER, STARTER)
        self.assertEqual(verdict(pack, STARTER, STARTER, NOW), "NO")
        self.assertTrue(any("differ" in w for w in reasons_not_go(pack, STARTER, STARTER, NOW)))

    def test_same_ids_is_no(self) -> None:
        raw = good_raw()
        raw["sealer_id"] = raw["starter_id"]
        pack = attach_join(raw, STARTER, SEALER)
        self.assertEqual(verdict(pack, STARTER, SEALER, NOW), "NO")

    def test_dead_window_is_no(self) -> None:
        pack = attach_join(good_raw(), STARTER, SEALER)
        late = datetime(2027, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(verdict(pack, STARTER, SEALER, late), "NO")
        self.assertTrue(any("dead" in w for w in reasons_not_go(pack, STARTER, SEALER, late)))

    def test_tamper_breaks_hash(self) -> None:
        pack = attach_join(good_raw(), STARTER, SEALER)
        pack["what"] = "pad"
        self.assertEqual(verdict(pack, STARTER, SEALER, NOW), "NO")
        self.assertTrue(any("mismatch" in w for w in reasons_not_go(pack, STARTER, SEALER, NOW)))

    def test_wrong_half_is_no(self) -> None:
        pack = attach_join(good_raw(), STARTER, SEALER)
        self.assertEqual(verdict(pack, STARTER, "nope-half-zzzz", NOW), "NO")

    def test_cli_boom_go(self) -> None:
        pack = attach_join(good_raw(), STARTER, SEALER)
        with tempfile.TemporaryDirectory() as td:
            pack_path = os.path.join(td, "pack.json")
            a = os.path.join(td, "a.half")
            b = os.path.join(td, "b.half")
            with open(pack_path, "w", encoding="utf-8") as f:
                json.dump(pack, f)
            with open(a, "w", encoding="utf-8") as f:
                f.write(STARTER + "\n")
            with open(b, "w", encoding="utf-8") as f:
                f.write(SEALER + "\n")
            r = subprocess.run(
                [sys.executable, "-m", "join.pack", "boom", a, b, pack_path],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(r.stdout.strip(), "GO")
            self.assertEqual(r.returncode, 0)

    def test_cli_boom_draft_no(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            pack_path = os.path.join(td, "draft.json")
            a = os.path.join(td, "a.half")
            b = os.path.join(td, "b.half")
            with open(pack_path, "w", encoding="utf-8") as f:
                json.dump(good_raw(), f)
            with open(a, "w", encoding="utf-8") as f:
                f.write(STARTER + "\n")
            with open(b, "w", encoding="utf-8") as f:
                f.write(SEALER + "\n")
            r = subprocess.run(
                [sys.executable, "-m", "join.pack", "boom", a, b, pack_path],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(r.stdout.strip(), "NO")
            self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
