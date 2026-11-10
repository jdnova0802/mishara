"""Items 139 / 140 — inbound poisoning checks; PIR + feedback without silent 133 retune."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-inbound.db")
os.environ["GATE_INBOUND_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-inbound.json")
os.environ["GATE_IDO_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-ido.json")
os.environ["GATE_CAMPAIGN_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-camp-inb.json")
os.environ["GATE_CASE_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-case-inb.json")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import campaign  # noqa: E402
import case_file  # noqa: E402
import ido  # noqa: E402
import inbound  # noqa: E402


class InboundTests(unittest.TestCase):
    def setUp(self):
        for key in ("GATE_INBOUND_PATH", "GATE_CAMPAIGN_PATH"):
            path = os.environ[key]
            if os.path.exists(path):
                os.remove(path)

    def test_reject_needs_cluster(self):
        lone = inbound.check(
            signal_type="harm_report",
            signal_id="harm_1",
            submitted_by="anon",
            disposition="REJECTED",
        )
        self.assertEqual(lone["error"], "coordination_required")
        cl = campaign.open_cluster(
            cohort_vertical="Insurance",
            member_operator_ids=["op_a", "op_b"],
            source_anomaly_flag_ids=["flag:1"],
        )
        ok = inbound.check(
            signal_type="calibration_resolution",
            signal_id="cal_1",
            submitted_by="op_a",
            correlation_cluster_id=cl["campaign_cluster_id"],
            disposition="REJECTED",
        )
        self.assertTrue(ok["ok"])
        self.assertTrue(ok["suspicious_coordination_flag"])
        self.assertTrue(ok["never_auto_acted"])


class IdoTests(unittest.TestCase):
    def setUp(self):
        for key in ("GATE_IDO_PATH", "GATE_CASE_PATH"):
            path = os.environ[key]
            if os.path.exists(path):
                os.remove(path)

    def test_empty_table_and_satisfy_needs_closed_case(self):
        self.assertTrue(ido.catalog()["empty_is_unused_table"])
        pir = ido.state_requirement(stated_by="compliance", question="Is this cohort coordinating binds?")
        self.assertEqual(pir["status"], "ACTIVE")
        early = ido.satisfy(requirement_id=pir["requirement_id"], case_id="missing")
        self.assertEqual(early["error"], "closed_case_required")
        case = case_file.open_case(
            opened_by="desk",
            hypothesis="shared integration",
            linked_receipt_ids=["r1"],
        )
        case_file.add_hypothesis(
            case_id=case["case_id"],
            hypothesis_text="Staged to mislead.",
            is_deception_hypothesis=True,
            weight=0.0,
        )
        case_file.set_status(case_id=case["case_id"], status="CLOSED", resolution="Not coordination.")
        done = ido.satisfy(requirement_id=pir["requirement_id"], case_id=case["case_id"])
        self.assertEqual(done["status"], "SATISFIED")
        fb = ido.feedback(source="case_file", source_id=case["case_id"], updated_baseline_id="pretend")
        self.assertFalse(fb["baseline_retuned"])
        self.assertIsNone(fb["updated_baseline_id"])


class InboundFlaskTests(unittest.TestCase):
    def setUp(self):
        for key in ("GATE_INBOUND_PATH", "GATE_IDO_PATH", "GATE_CAMPAIGN_PATH", "GATE_CASE_PATH"):
            path = os.environ[key]
            if os.path.exists(path):
                os.remove(path)
        self.client = app_mod.app.test_client()

    def test_pages(self):
        page = self.client.get("/ido")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"unused table", page.data)
        posted = self.client.post(
            "/v1/ido",
            json={"stated_by": "buyer", "question": "Watch DISARM T0013 on Grid."},
        )
        self.assertEqual(posted.status_code, 201)


if __name__ == "__main__":
    unittest.main()
