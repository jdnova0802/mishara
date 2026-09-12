"""CI-facing wrapper around scripts/scorecard_gates/run_gates.py."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNNER = REPO / "scripts" / "scorecard_gates" / "run_gates.py"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(RUNNER), *args],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        check=False,
    )


class ZeroToleranceGateTests(unittest.TestCase):
    def test_all_dims_pass_on_tree(self):
        proc = _run()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_dim11_prove_fail(self):
        proc = _run("--prove-fail", "11")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_dim12_prove_fail(self):
        proc = _run("--prove-fail", "12")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_dim13_prove_fail(self):
        proc = _run("--prove-fail", "13")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_dim14_prove_fail(self):
        proc = _run("--prove-fail", "14")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
