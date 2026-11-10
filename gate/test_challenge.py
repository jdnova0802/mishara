"""Items 109–111 — counter-case, harm clusters, joint-freshness DEFERRED."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-challenge.db")
os.environ["GATE_COUNTER_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-counter.json")
os.environ["GATE_HARM_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-harm.json")
os.environ["GATE_HARM_ADJ_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-harm-adj.json")
os.environ.pop("GATE_STALENESS_WINDOW_MS", None)

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import challenge  # noqa: E402


HOP = {"reason": "premium_exceeds_authority", "state": "DEAD", "vertical": "insurance"}


class CounterCaseTests(unittest.TestCase):
    def test_empty_evidence_is_strawman_and_review(self):
        rec = challenge.lock_decision(verdict="ACT", hop=HOP, evidence_cited=[], persist=False)
        self.assertTrue(rec["counter_case_score"]["strawman_flag"])
        self.assertTrue(rec["review"])
        self.assertLessEqual(rec["counter_case"]["constructed_at"], rec["verdict_locked_at"])

    def test_cited_hop_fields_engage(self):
        rec = challenge.lock_decision(
            verdict="HOLD",
            hop=HOP,
            evidence_cited=["premium_exceeds_authority", "DEAD"],
            persist=False,
        )
        self.assertFalse(rec["counter_case_score"]["strawman_flag"])
        self.assertGreaterEqual(rec["counter_case_score"]["engagement_score"], 0.5)
        self.assertFalse(rec["review"])


class HarmTests(unittest.TestCase):
    def test_same_fingerprint_clusters_and_tighten_auto_applies(self):
        fp = "sig-aaa"
        for i in range(3):
            challenge.report_harm(
                harm_description="near miss",
                preceding_signals=[
                    {
                        "signal_id": f"s{i}",
                        "gate_verdict_at_time": "ALLOW",
                        "signal_fingerprint": fp,
                        "sub_threshold_score": 0.4,
                    }
                ],
            )
        last = challenge.list_harms()[-1]
        cid = last["fingerprint_cluster_id"]
        self.assertGreaterEqual(challenge.cluster_counts()[cid], 3)
        out = challenge.propose_adjustment(
            erra_rule_id="rule_x",
            old_threshold=0.9,
            new_threshold=0.7,
            cluster_id=cid,
        )
        self.assertTrue(out["ok"])
        self.assertTrue(out["auto_applied"])
        self.assertTrue(out["receipt_hash"])

    def test_loosen_without_human_is_refused(self):
        out = challenge.propose_adjustment(
            erra_rule_id="rule_x",
            old_threshold=0.5,
            new_threshold=0.9,
            cluster_id="clus_none",
        )
        self.assertFalse(out["ok"])
        self.assertEqual(out["error"], "loosen_needs_human")


class FreshnessTests(unittest.TestCase):
    def test_unset_window_is_deferred_not_block(self):
        os.environ.pop("GATE_STALENESS_WINDOW_MS", None)
        out = challenge.freshness_check(
            bind_id="b1",
            erra_signal={"value": "A", "hlc": {"logical": 1, "wall_ms": 1000}},
            velaru_proof={"value": "LIVE", "hlc": {"logical": 1, "wall_ms": 1010}},
        )
        self.assertIsNone(out["staleness_window_ms"])
        self.assertEqual(out["bind_result"], "DEFERRED")
        self.assertIsNone(out["freshness_check"]["within_window"])

    def test_tuned_window_allows_close_pair_and_defers_stale(self):
        os.environ["GATE_STALENESS_WINDOW_MS"] = "50"
        try:
            close = challenge.freshness_check(
                bind_id="b2",
                erra_signal={"value": "A", "hlc": {"logical": 4, "wall_ms": 1000}},
                velaru_proof={"value": "LIVE", "hlc": {"logical": 5, "wall_ms": 1020}},
            )
            self.assertEqual(close["bind_result"], "ALLOW")
            stale = challenge.freshness_check(
                bind_id="b3",
                erra_signal={"value": "A", "hlc": {"logical": 4, "wall_ms": 1000}},
                velaru_proof={"value": "LIVE", "hlc": {"logical": 5, "wall_ms": 2000}},
            )
            self.assertEqual(stale["bind_result"], "DEFERRED")
            self.assertFalse(stale["freshness_check"]["within_window"])
        finally:
            os.environ.pop("GATE_STALENESS_WINDOW_MS", None)


class ChallengeFlaskTests(unittest.TestCase):
    def setUp(self):
        self.client = app_mod.app.test_client()

    def test_pages_200(self):
        for path in ("/counter-case", "/harm", "/freshness"):
            r = self.client.get(path)
            self.assertEqual(r.status_code, 200, path)

    def test_freshness_api_does_not_invent_a_window(self):
        r = self.client.post(
            "/v1/freshness",
            json={
                "bind_id": "b",
                "erra_signal": {"value": 1, "hlc": {"logical": 1, "wall_ms": 1}},
                "velaru_proof": {"value": 1, "hlc": {"logical": 1, "wall_ms": 1}},
            },
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["bind_result"], "DEFERRED")
        self.assertIsNone(r.get_json()["staleness_window_ms"])


if __name__ == "__main__":
    unittest.main()
