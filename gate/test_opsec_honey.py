"""Items 138 / 145 — OPSEC review; canary receipts never scored."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-opsec.db")
os.environ["GATE_OPSEC_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-opsec.json")
os.environ["GATE_HONEY_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-honey.json")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import honey_receipt  # noqa: E402
import opsec  # noqa: E402


class OpsecTests(unittest.TestCase):
    def setUp(self):
        path = os.environ["GATE_OPSEC_PATH"]
        if os.path.exists(path):
            os.remove(path)

    def test_118_banding_is_applied_and_five_steps_required(self):
        rows = opsec.list_reviews()
        self.assertTrue(any(r["surface"] == "item_118_threshold_curve" and r["countermeasure_status"] == "APPLIED" for r in rows))
        bad = opsec.record(
            surface="item_74_verify_api",
            critical_info_identified="",
            threat_actor="mapper",
            vulnerability="hash oracle",
            risk_rank="LOW",
            countermeasure="rate limit",
        )
        self.assertEqual(bad["error"], "five_steps_required")
        ok = opsec.record(
            surface="item_74_verify_api",
            critical_info_identified="Which event_ids exist",
            threat_actor="boundary mapper",
            vulnerability="unauthenticated verify",
            risk_rank="MEDIUM",
            countermeasure="canary receipts on verify",
            countermeasure_status="PROPOSED",
        )
        self.assertTrue(ok["ok"])


class HoneyTests(unittest.TestCase):
    def setUp(self):
        path = os.environ["GATE_HONEY_PATH"]
        if os.path.exists(path):
            os.remove(path)

    def test_real_receipt_id_stays_null_and_probe_trips(self):
        planted = honey_receipt.plant(disguised_as="near_threshold_case")
        self.assertIsNone(planted["real_receipt_id"])
        self.assertTrue(planted["never_counted_in_scores"])
        self.assertNotEqual(planted["spec"], honey_receipt.BYPASS_SPEC)
        hit = honey_receipt.probe(
            canary_id=planted["canary_id"],
            accessed_by="stranger",
            access_method="verify_api",
        )
        self.assertTrue(hit["tripped"])
        self.assertIsNone(hit["real_receipt_id"])
        self.assertTrue(hit["never_counted_in_scores"])


class OpsecFlaskTests(unittest.TestCase):
    def setUp(self):
        for key in ("GATE_OPSEC_PATH", "GATE_HONEY_PATH"):
            path = os.environ[key]
            if os.path.exists(path):
                os.remove(path)
        self.client = app_mod.app.test_client()

    def test_pages_and_probe_via_verify(self):
        self.assertEqual(self.client.get("/opsec").status_code, 200)
        planted = self.client.post("/v1/canary-receipts", json={"disguised_as": "weak_operator"})
        self.assertEqual(planted.status_code, 201)
        cid = planted.get_json()["canary_id"]
        verify = self.client.get(f"/v1/verify?event_id={cid}")
        self.assertEqual(verify.status_code, 200)
        body = verify.get_json()
        self.assertTrue(body.get("canary"))
        self.assertTrue(body.get("tripped"))
        self.assertFalse(body.get("verified"))


if __name__ == "__main__":
    unittest.main()
