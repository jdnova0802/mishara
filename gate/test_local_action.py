"""Local action gate: sign first, exec only if the signature exists."""
from __future__ import annotations

import json
import subprocess
import unittest

import local_action as la


class LocalActionTests(unittest.TestCase):
    def test_allowlist_runs_and_receipt_verifies(self):
        signer = la.EphemeralSigner()
        outcome = la.act(["echo", "ok"], "operator", signer)
        self.assertTrue(outcome["executed"])
        self.assertEqual(outcome["stdout"].strip(), "ok")
        self.assertFalse(outcome["fail_closed"])
        verdict = la.verify_authorization(outcome["authorization"], signer)
        self.assertEqual(verdict["verdict"], "valid")
        body = outcome["authorization"]["canonical_receipt"]
        self.assertEqual(body["decision"], "allow")
        self.assertEqual(body["rule_id"], "echo-ok")
        self.assertTrue(body["signed_before_exec"])
        self.assertFalse(body["executed"])
        self.assertIn("that the command was reasonable", body["not_claimed"])
        result = la.verify_authorization(outcome["result"], signer)
        self.assertEqual(result["verdict"], "valid")
        self.assertEqual(
            outcome["result"]["canonical_receipt"]["authorization_hash"],
            outcome["authorization"]["receipt_hash"],
        )

    def test_command_off_the_list_does_not_run(self):
        signer = la.EphemeralSigner()
        calls = []

        def runner(argv):
            calls.append(argv)
            return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

        outcome = la.act(["rm", "-rf", "/"], "operator", signer, runner=runner)
        self.assertEqual(calls, [])
        self.assertFalse(outcome["executed"])
        self.assertEqual(outcome["reason"], "not_on_allowlist")
        body = outcome["authorization"]["canonical_receipt"]
        self.assertEqual(body["decision"], "refused")
        self.assertEqual(la.verify_authorization(outcome["authorization"], signer)["verdict"], "valid")

    def test_string_argv_is_not_a_shell(self):
        signer = la.EphemeralSigner()
        outcome = la.act("echo ok", "operator", signer)
        self.assertFalse(outcome["executed"])
        self.assertEqual(outcome["reason"], "argv_not_a_list")
        self.assertIsNone(outcome["authorization"])

    def test_signer_down_does_not_run_the_allowlisted_command(self):
        calls = []

        def runner(argv):
            calls.append(argv)
            return subprocess.CompletedProcess(argv, 0, stdout="ok\n", stderr="")

        outcome = la.act(["echo", "ok"], "operator", la.BrokenSigner(), runner=runner)
        self.assertEqual(calls, [])
        self.assertFalse(outcome["executed"])
        self.assertTrue(outcome["fail_closed"])
        self.assertEqual(outcome["reason"], "signer_unavailable")
        self.assertIsNone(outcome["authorization"])

    def test_tampered_receipt_fails_verification(self):
        signer = la.EphemeralSigner()
        outcome = la.act(["echo", "ok"], "operator", signer)
        raw = outcome["authorization"]["canonical_receipt_json"]
        parsed = json.loads(raw)
        parsed["decision"] = "refused"
        rewritten = la.receipt_mod.canonical_dumps(parsed)
        outcome["authorization"]["canonical_receipt_json"] = rewritten
        outcome["authorization"]["canonical_receipt"] = parsed
        verdict = la.verify_authorization(outcome["authorization"], signer)
        self.assertEqual(verdict["verdict"], "invalid")
        self.assertIn("signature_invalid", verdict["reasons"])


if __name__ == "__main__":
    unittest.main()
