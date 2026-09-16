"""Same bytes, same hash. Blanks never YES."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from check.pack import SPEC, attach_hash, pack_sha256, reasons_not_yes, verdict  # noqa: E402

BEFORE = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
AFTER = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"


def good_raw() -> dict:
    return {
        "spec": SPEC,
        "task": "add fail-closed pack",
        "git_sha_before": BEFORE,
        "git_sha_after": AFTER,
        "commands_run": [{"argv": ["python", "-m", "check.test_pack"], "exit_code": 0}],
        "tests_run": [{"name": "test_yes_when_complete", "passed": True}],
        "tests_pass": True,
        "files_touched": ["check/pack.py"],
        "claims": ["verify prints YES only when tests_pass"],
        "what_it_did_not_do": ["did not merge", "did not call it LGTM"],
    }


class PackTests(unittest.TestCase):
    def test_two_people_same_hash(self) -> None:
        a = attach_hash(good_raw())
        b = attach_hash(good_raw())
        self.assertEqual(a["pack_sha256"], b["pack_sha256"])
        self.assertEqual(pack_sha256(a), a["pack_sha256"])

    def test_yes_when_complete(self) -> None:
        pack = attach_hash(good_raw())
        self.assertEqual(verdict(pack), "YES")
        self.assertEqual(reasons_not_yes(pack), [])

    def test_blank_task_is_no(self) -> None:
        raw = good_raw()
        raw["task"] = "  "
        pack = attach_hash(raw)
        self.assertEqual(verdict(pack), "NO")
        self.assertTrue(any("task" in w for w in reasons_not_yes(pack)))

    def test_empty_tests_is_no(self) -> None:
        raw = good_raw()
        raw["tests_run"] = []
        pack = attach_hash(raw)
        self.assertEqual(verdict(pack), "NO")

    def test_lgtm_without_tests_pass_is_no(self) -> None:
        raw = good_raw()
        raw["tests_pass"] = False
        pack = attach_hash(raw)
        self.assertEqual(verdict(pack), "NO")

    def test_tests_pass_lie_is_no(self) -> None:
        raw = good_raw()
        raw["tests_run"] = [{"name": "x", "passed": False}]
        raw["tests_pass"] = True
        pack = attach_hash(raw)
        self.assertEqual(verdict(pack), "NO")

    def test_moved_commit_no_files_is_no(self) -> None:
        raw = good_raw()
        raw["files_touched"] = []
        pack = attach_hash(raw)
        self.assertEqual(verdict(pack), "NO")

    def test_tamper_breaks_hash(self) -> None:
        pack = attach_hash(good_raw())
        pack["claims"] = ["tampered"]
        self.assertEqual(verdict(pack), "NO")
        self.assertTrue(any("mismatch" in w for w in reasons_not_yes(pack)))

    def test_cli_verify_yes(self) -> None:
        pack = attach_hash(good_raw())
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "pack.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(pack, f)
            r = subprocess.run(
                [sys.executable, "-m", "check.pack", "verify", path],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(r.stdout.strip(), "YES")
            self.assertEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
