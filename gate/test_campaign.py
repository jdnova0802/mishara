"""Items 137 / 144 — DISARM cluster; CONFIRMED gated on confounder review."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-campaign.db")
os.environ["GATE_CAMPAIGN_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-campaigns.json")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import campaign  # noqa: E402


class CampaignTests(unittest.TestCase):
    def setUp(self):
        path = os.environ["GATE_CAMPAIGN_PATH"]
        if os.path.exists(path):
            os.remove(path)

    def test_ttp_needs_evidence_and_confirm_needs_confounder(self):
        cl = campaign.open_cluster(
            cohort_vertical="Insurance",
            member_operator_ids=["op_a", "op_b"],
            source_anomaly_flag_ids=["flag:1"],
        )
        self.assertEqual(cl["status"], "SUSPECTED")
        self.assertFalse(cl["hard_binding"])
        empty = campaign.attach_ttp(
            campaign_cluster_id=cl["campaign_cluster_id"],
            disarm_technique_id="T0013",
            evidence_receipt_ids=[],
        )
        self.assertEqual(empty["error"], "evidence_required")
        campaign.attach_ttp(
            campaign_cluster_id=cl["campaign_cluster_id"],
            disarm_technique_id="T0013",
            evidence_receipt_ids=["rec_1"],
        )
        blocked = campaign.set_status(campaign_cluster_id=cl["campaign_cluster_id"], status="CONFIRMED")
        self.assertEqual(blocked["error"], "confounder_gate")
        vacuous = campaign.review_edge(
            link_graph_edge_id="edge:1",
            claimed_relationship="causal",
            confounder_considered=[],
            confounder_ruled_out=True,
            reviewed_by="desk",
            campaign_cluster_id=cl["campaign_cluster_id"],
        )
        self.assertEqual(vacuous["error"], "vacuous_confounder")
        campaign.review_edge(
            link_graph_edge_id="edge:1",
            claimed_relationship="causal",
            confounder_considered=["same third-party integration"],
            confounder_ruled_out=True,
            reviewed_by="desk",
            campaign_cluster_id=cl["campaign_cluster_id"],
        )
        ok = campaign.set_status(campaign_cluster_id=cl["campaign_cluster_id"], status="CONFIRMED")
        self.assertEqual(ok["status"], "CONFIRMED")


class CampaignFlaskTests(unittest.TestCase):
    def setUp(self):
        path = os.environ["GATE_CAMPAIGN_PATH"]
        if os.path.exists(path):
            os.remove(path)
        self.client = app_mod.app.test_client()

    def test_page_and_post(self):
        self.assertEqual(self.client.get("/campaigns").status_code, 200)
        created = self.client.post(
            "/v1/campaigns",
            json={
                "cohort_vertical": "Grid",
                "member_operator_ids": ["a", "b"],
                "source_link_graph_query_id": "q1",
            },
        )
        self.assertEqual(created.status_code, 201)
        cid = created.get_json()["campaign_cluster_id"]
        confirm = self.client.post("/v1/campaigns/status", json={"campaign_cluster_id": cid, "status": "CONFIRMED"})
        self.assertEqual(confirm.status_code, 409)


if __name__ == "__main__":
    unittest.main()
