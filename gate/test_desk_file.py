"""The desk file: a mandate, a swipe inside it, a swipe that edits the cap."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_REQUIRE_RECEIPT_KEYS", "0")

from gate import desk_file  # noqa: E402


HERE = os.path.dirname(os.path.abspath(__file__))


class DeskFileTests(unittest.TestCase):
    def test_page_and_both_receipts_verify_offline(self):
        with tempfile.TemporaryDirectory() as directory:
            out = desk_file.build(directory, agent_id="desk_agent_test")
            with open(out["page"], encoding="utf-8") as handle:
                page = handle.read()
            self.assertIn(out["mandate_id"], page)
            self.assertIn("SWIPE INSIDE THE YES", page)
            self.assertIn("SWIPE THAT EDITS THE CAP", page)
            self.assertEqual(out["within_decision"], "GO")
            self.assertEqual(out["edited_decision"], "NO_GO")
            self.assertEqual(out["edited_signal"], "mandate_diverged")
            self.assertIn("This file is not the dollar.", page)

            env = os.environ.copy()
            env["PYTHONPATH"] = os.path.dirname(HERE) + os.pathsep + env.get("PYTHONPATH", "")
            for name in ("within.json", "edited.json"):
                run = subprocess.run(
                    [
                        sys.executable,
                        os.path.join(HERE, "offline_verify.py"),
                        os.path.join(directory, name),
                        "--public-key",
                        out["public_key"],
                    ],
                    capture_output=True,
                    text=True,
                    env=env,
                    check=False,
                )
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertEqual(run.stdout.strip(), "valid")


if __name__ == "__main__":
    unittest.main()
