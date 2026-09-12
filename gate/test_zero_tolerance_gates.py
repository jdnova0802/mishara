"""CI-facing wrapper around scripts/scorecard_gates/run_gates.py."""
from __future__ import annotations

import importlib.util
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


def _load_runner():
    spec = importlib.util.spec_from_file_location("scorecard_run_gates", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


class ZeroToleranceGateTests(unittest.TestCase):
    def test_all_dims_pass_on_tree(self):
        proc = _run()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_dim11_prove_fail(self):
        proc = _run("--prove-fail", "11")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_dim11_api_liveness_is_not_mere_not_404(self):
        """POST≠404 is a loophole — only documented sensible codes count as live."""
        gates = _load_runner()
        ok, code, why = gates.api_path_is_live(200)
        self.assertTrue(ok)
        self.assertEqual(code, 200)
        for auth in (401, 403, 405):
            ok, code, why = gates.api_path_is_live(auth)
            self.assertTrue(ok, why)
            self.assertEqual(code, auth)
        # POST-only: allowlisted challenge / validation / success only
        for post in (200, 400, 401, 403, 405, 415, 422):
            ok, code, why = gates.api_path_is_live(404, post)
            self.assertTrue(ok, why)
            self.assertEqual(code, post)
        # Loophole cases that must FAIL
        ok, code, why = gates.api_path_is_live(404)  # bare GET 404, no POST probe
        self.assertFalse(ok, why)
        ok, code, why = gates.api_path_is_live(404, 404)
        self.assertFalse(ok, why)
        ok, code, why = gates.api_path_is_live(404, 500)  # broken endpoint ≠ live
        self.assertFalse(ok, why)
        ok, code, why = gates.api_path_is_live(404, 502)
        self.assertFalse(ok, why)
        ok, code, why = gates.api_path_is_live(404, -1)
        self.assertFalse(ok, why)
        ok, code, why = gates.api_path_is_live(500)
        self.assertFalse(ok, why)
        ok, code, why = gates.api_path_is_live(301)  # pages follow redirects; raw 301 not API-live
        self.assertFalse(ok, why)

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
