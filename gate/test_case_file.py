"""Items 134–135 — case bundle + triage enrich-before-disposition."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-case.db")
os.environ["GATE_CASE_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-cases.json")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import case_file  # noqa: E402


class CaseTests(unittest.TestCase):
    def setUp(self):
        path = os.environ["GATE_CASE_PATH"]
        if os.path.exists(path):
            os.remove(path)

    def test_empty_bundle_refused_and_close_needs_resolution(self):
        empty = case_file.open_case(opened_by="a", hypothesis="maybe collusion")
        self.assertEqual(empty["error"], "nothing_to_bundle")
        opened = case_file.open_case(
            opened_by="a",
            hypothesis="shared counterparty, not a coincidence",
            linked_receipt_ids=["r1", "r2"],
            linked_anomaly_flag_ids=["flag:x"],
        )
        self.assertTrue(opened["ok"])
        self.assertEqual(opened["status"], "OPEN")
        closed = case_file.set_status(case_id=opened["case_id"], status="CLOSED")
        self.assertEqual(closed["error"], "deception_hypothesis_required")
        escalated = case_file.set_status(case_id=opened["case_id"], status="ESCALATED")
        self.assertEqual(escalated["error"], "deception_hypothesis_required")
        case_file.add_hypothesis(
            case_id=opened["case_id"],
            hypothesis_text="This cluster was staged to mislead the desk.",
            is_deception_hypothesis=True,
            diagnostic_evidence_against=["r1"],
            weight=0.0,
        )
        still = case_file.set_status(case_id=opened["case_id"], status="CLOSED")
        self.assertEqual(still["error"], "resolution_required")
        done = case_file.set_status(
            case_id=opened["case_id"],
            status="CLOSED",
            resolution="Same popular integration, not coordination.",
        )
        self.assertEqual(done["status"], "CLOSED")
        self.assertTrue(done["resolution"])

    def test_osint_is_soft_and_needs_an_anchor(self):
        opened = case_file.open_case(
            opened_by="a",
            hypothesis="public posts match the cluster",
            linked_receipt_ids=["r9"],
        )
        floating = case_file.add_osint(
            finding="same handle on two platforms",
            source_category="social_media",
            source_url="https://example.com/post",
            independence_verified=True,
        )
        self.assertEqual(floating["error"], "anchor_required")
        ok = case_file.add_osint(
            finding="same handle on two platforms",
            source_category="social_media",
            source_url="https://example.com/post",
            independence_verified=True,
            case_id=opened["case_id"],
        )
        self.assertTrue(ok["ok"])
        self.assertEqual(ok["evidentiary_weight"], "CORROBORATING_ONLY")
        self.assertFalse(ok["hard_binding"])


class TriageTests(unittest.TestCase):
    def setUp(self):
        path = os.environ["GATE_CASE_PATH"]
        if os.path.exists(path):
            os.remove(path)

    def test_ingest_has_no_severity_and_silent_close_refused(self):
        raw = case_file.ingest_triage(source="anomaly_flag", source_id="flag:1", extra={"severity": "CRITICAL"})
        self.assertEqual(raw["error"], "severity_at_ingest_refused")
        item = case_file.ingest_triage(source="counter_case_score", source_id="erra-abc")
        self.assertIsNone(item["severity"])
        self.assertTrue(item["never_auto_acted"])
        early = case_file.dispose_triage(
            triage_id=item["triage_id"],
            disposition="CLOSE_NON_ACTIONABLE",
            disposition_reason="noise",
        )
        self.assertEqual(early["error"], "enrich_first")
        silent = case_file.enrich_triage(triage_id=item["triage_id"], severity="LOW")
        self.assertEqual(silent["severity"], "LOW")
        blank = case_file.dispose_triage(
            triage_id=item["triage_id"],
            disposition="CLOSE_NON_ACTIONABLE",
            disposition_reason=" ",
        )
        self.assertEqual(blank["error"], "disposition_reason_required")
        done = case_file.dispose_triage(
            triage_id=item["triage_id"],
            disposition="MONITOR",
            disposition_reason="strawman counter-case, watch the next lock",
        )
        self.assertEqual(done["disposition"], "MONITOR")


class CaseFlaskTests(unittest.TestCase):
    def setUp(self):
        path = os.environ["GATE_CASE_PATH"]
        if os.path.exists(path):
            os.remove(path)
        self.client = app_mod.app.test_client()

    def test_pages_and_apis(self):
        self.assertEqual(self.client.get("/cases").status_code, 200)
        created = self.client.post(
            "/v1/cases",
            json={
                "opened_by": "desk",
                "hypothesis": "one cluster",
                "linked_receipt_ids": ["abc"],
            },
        )
        self.assertEqual(created.status_code, 201)
        tri = self.client.post("/v1/triage", json={"source": "kudurru_watch", "source_id": "watch_1"})
        self.assertEqual(tri.status_code, 201)
        self.assertIsNone(tri.get_json()["severity"])
        cid = created.get_json()["case_id"]
        blocked = self.client.post("/v1/cases/status", json={"case_id": cid, "status": "ESCALATED"})
        self.assertEqual(blocked.status_code, 409)
        hyp = self.client.post(
            "/v1/cases/hypotheses",
            json={
                "case_id": cid,
                "hypothesis_text": "Could this be staged?",
                "is_deception_hypothesis": True,
                "weight": 0.1,
            },
        )
        self.assertEqual(hyp.status_code, 201)


if __name__ == "__main__":
    unittest.main()
