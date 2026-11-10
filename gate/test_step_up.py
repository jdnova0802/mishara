"""Items 121–122 — 3DS2-style step-up without ACS numbers; named assumptions."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-step-up.db")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import assumptions  # noqa: E402
import dfir  # noqa: E402
import receipt  # noqa: E402
import step_up  # noqa: E402


class StepUpTests(unittest.TestCase):
    def test_exact_match_high_is_frictionless(self):
        out = step_up.evaluate(tier="exact_match", match_hash="abc", match_strength="HIGH")
        self.assertTrue(out["ok"])
        self.assertEqual(out["flow"], step_up.FRICTIONLESS)
        self.assertFalse(out["liability_shift"])
        self.assertFalse(out["acs"])

    def test_classifier_always_challenges(self):
        out = step_up.evaluate(tier="classifier", match_strength="HIGH")
        self.assertEqual(out["flow"], step_up.CHALLENGE)
        self.assertTrue(out["liability_shift"])

    def test_numeric_acs_refused(self):
        out = step_up.evaluate(tier="exact_match", extra={"acs_score": 12})
        self.assertFalse(out["ok"])
        self.assertEqual(out["error"], "acs_score_refused")


class AssumptionTests(unittest.TestCase):
    def test_bare_verified_true_refused(self):
        out = assumptions.claim(verified=True, under_assumptions=None)
        self.assertFalse(out["ok"])
        self.assertFalse(out["verified"])
        self.assertEqual(out["error"], "assumptions_required")

    def test_empty_list_is_vacuous(self):
        out = assumptions.claim(verified=True, under_assumptions=[])
        self.assertEqual(out["error"], "assumptions_empty")

    def test_named_list_verifies_and_flags_missing_steelman(self):
        out = assumptions.claim(
            verified=True,
            under_assumptions=["hop halt is DEAD", "circuit closed is not a BLOCK ballot"],
            kind="proof",
            steelman_cited=False,
        )
        self.assertTrue(out["ok"])
        self.assertTrue(out["verified"])
        self.assertTrue(out["vacuous_visible"])
        self.assertEqual(len(out["under_assumptions"]), 2)

    def test_public_verify_does_not_stamp_verified_without_assumptions(self):
        issued = receipt.issue_receipt(
            event_id="e1",
            fuse_id="fuse_x",
            job_id=None,
            decision="BLOCK",
            acted=False,
            verify_url="https://example/verify",
            created_at="2026-11-10T17:00:00+00:00",
            hop={"reason": "premium_exceeds_authority", "state": "DEAD"},
            prev_receipt_hash=None,
        )
        row = {
            "id": "e1",
            "decision": "BLOCK",
            "created_at": "2026-11-10T17:00:00+00:00",
            "hop": {"reason": "premium_exceeds_authority", "state": "DEAD"},
            "receipt_hash": issued["receipt_hash"],
            "receipt_signature": issued["receipt_signature"],
            "fuse_id": "fuse_x",
            "acted": False,
            "verify_url": "https://example/verify",
            "job_id": None,
            "prev_receipt_hash": None,
        }
        out = dfir.public_verify(row, public_url="https://example")
        self.assertTrue(out["hash_matches"])
        self.assertFalse(out["verified"])
        self.assertEqual(out["assumption_claim"]["error"], "assumptions_required")


class StepUpFlaskTests(unittest.TestCase):
    def setUp(self):
        self.client = app_mod.app.test_client()

    def test_pages_and_apis(self):
        self.assertEqual(self.client.get("/step-up").status_code, 200)
        self.assertEqual(self.client.get("/assumptions").status_code, 200)
        bad = self.client.post("/v1/step-up", json={"tier": "exact_match", "acs_score": 0.9})
        self.assertEqual(bad.status_code, 409)
        good = self.client.post(
            "/v1/step-up",
            json={"tier": "exact_match", "match_hash": "h", "match_strength": "HIGH"},
        )
        self.assertEqual(good.status_code, 200)
        self.assertEqual(good.get_json()["flow"], "FRICTIONLESS")
        bare = self.client.post("/v1/assumptions", json={"verified": True})
        self.assertEqual(bare.status_code, 409)
        named = self.client.post(
            "/v1/assumptions",
            json={"verified": True, "under_assumptions": ["item 21 split is HOLD"], "kind": "test"},
        )
        self.assertEqual(named.status_code, 200)
        self.assertTrue(named.get_json()["verified"])


if __name__ == "__main__":
    unittest.main()
