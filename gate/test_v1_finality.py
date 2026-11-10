"""Items 91–94 — V1 formula, finality_event, UNDO window, map gauge."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-v1-finality.db")
os.environ["GATE_V1_UNDO_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-v1-undos.json")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import bind_room_demo  # noqa: E402
import receipt  # noqa: E402
import v1  # noqa: E402


class V1FormulaTests(unittest.TestCase):
    def test_insurance_over_limit_is_computed_not_looked_up(self):
        snap = v1.compute(
            "insurance",
            {
                "premium_usd": 62400,
                "delegation_limit_usd": 50000,
                "remaining_seconds": 150,
                "ttl_seconds": 300,
            },
        )
        self.assertFalse(snap["lookup_table"])
        self.assertEqual(snap["finality_event"], "pas_bind_commit")
        self.assertEqual(snap["derived"]["over_limit_usd"], 12400)
        self.assertAlmostEqual(snap["v1_distance"], 0.5)
        self.assertTrue(snap["undo_open"])
        self.assertFalse(snap["crossed"])

    def test_crossed_bind_closes_undo_and_distance_is_zero(self):
        snap = v1.compute("insurance", {"premium_usd": 1, "delegation_limit_usd": 2, "bound": True})
        self.assertTrue(snap["crossed"])
        self.assertEqual(snap["v1_distance"], 0.0)
        self.assertFalse(snap["undo_open"])
        denied = v1.undo("evt_done", snap)
        self.assertFalse(denied["ok"])
        self.assertEqual(denied["error"], "v1_crossed")

    def test_fleet_over_cap_is_nodes_minus_cap(self):
        snap = v1.compute("fleet", {"nodes_in_cascade": 14, "fleet_cap": 8, "remaining_seconds": 300})
        self.assertEqual(snap["vertical"], "network")
        self.assertEqual(snap["derived"]["over_cap"], 6)
        self.assertEqual(snap["finality_event"], "fleet_deploy_commit")

    def test_grid_shortfall_is_floor_minus_projected(self):
        snap = v1.compute("grid", {"reserve_floor_mw": 120, "projected_mw": 91, "remaining_seconds": 60, "ttl_seconds": 120})
        self.assertEqual(snap["derived"]["reserve_shortfall_mw"], 29)
        self.assertAlmostEqual(snap["v1_distance"], 0.5)

    def test_undo_records_while_open(self):
        snap = v1.compute("hiring", {"remaining_seconds": 10, "ttl_seconds": 100})
        out = v1.undo("evt_open", snap)
        self.assertTrue(out["ok"])
        self.assertTrue(v1.undone("evt_open"))


class BindRoomFormulaTests(unittest.TestCase):
    def test_demo_derives_over_limit(self):
        status, body = bind_room_demo.run(domain="insurance", company="Acme", public_url="https://gate.example")
        self.assertEqual(status, 200)
        gate = body["step3_json"]
        self.assertEqual(gate["over_limit_usd"], 12400)
        self.assertEqual(gate["finality_event"], "pas_bind_commit")
        self.assertTrue(gate["undo_open"])
        self.assertFalse(gate.get("lookup_table"))


class ReceiptFinalityTests(unittest.TestCase):
    def test_public_payload_names_finality_event(self):
        issued = receipt.issue_receipt(
            event_id="evt-v1",
            fuse_id="fuse_x",
            job_id=None,
            decision="BLOCK",
            acted=False,
            verify_url="https://example/verify",
            created_at="2026-11-10T16:00:00+00:00",
            hop={
                "vertical": "insurance",
                "premium_usd": 62400,
                "delegation_limit_usd": 50000,
                "remaining_seconds": 300,
            },
            prev_receipt_hash=None,
        )
        row = {
            "id": "evt-v1",
            "hop": issued.get("hop")
            or {
                "vertical": "insurance",
                "premium_usd": 62400,
                "delegation_limit_usd": 50000,
                "remaining_seconds": 300,
            },
            "decision": "BLOCK",
            "receipt_hash": issued["receipt_hash"],
        }
        payload = receipt.receipt_to_public_payload(receipt_row=row, public_url="https://example")
        env = payload["finality"]
        self.assertEqual(env["finality_event"], "pas_bind_commit")
        self.assertFalse(env["in_signed_canonical"])


class V1FlaskTests(unittest.TestCase):
    def setUp(self):
        self.client = app_mod.app.test_client()

    def test_gauge_page(self):
        r = self.client.get("/v1-gauge")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"V1-distance", r.data)

    def test_map_exposes_distance(self):
        r = self.client.get("/v1/restraint-map")
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertIn("v1", body)
        self.assertFalse(body["v1"]["lookup_table"])

    def test_undo_api_rejects_crossed(self):
        r = self.client.post(
            "/v1/v1/undo",
            json={"event_id": "x", "vertical": "insurance", "bound": True},
        )
        self.assertEqual(r.status_code, 409)
        self.assertEqual(r.get_json()["error"], "v1_crossed")


if __name__ == "__main__":
    unittest.main()
