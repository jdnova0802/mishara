"""Items 132/133 — link graph intern registry + sample-size gated anomaly flags."""
from __future__ import annotations

import math
import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-link-graph.db")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import anomaly_detection as ad  # noqa: E402
import app as app_mod  # noqa: E402
import link_graph as lg  # noqa: E402


def _rec(**kwargs):
    defaults = dict(
        receipt_id="r",
        operator_id="op",
        org_id="org",
        cohort_vertical="fintech",
        ingredients=[],
        co_signers=[],
        metrics={"block_rate": 0.05},
        created_at="2026-02-01T00:00:00Z",
    )
    defaults.update(kwargs)
    return lg.ReceiptRecord(**defaults)


class LinkGraphTests(unittest.TestCase):
    def test_underscore_receipt_ids_stay_intact(self):
        records = [
            _rec(receipt_id="dec_c100", operator_id="op_alice", ingredients=[]),
            _rec(
                receipt_id="dec_c200",
                operator_id="op_alice",
                ingredients=[{"ingredient_receipt_id": "dec_c100", "ingredient_hash": "h1"}],
                co_signers=["op_bob"],
            ),
            _rec(
                receipt_id="dec_c300",
                operator_id="op_bob",
                ingredients=[{"ingredient_receipt_id": "dec_c200", "ingredient_hash": "h2"}],
            ),
            _rec(receipt_id="dec_c900", operator_id="op_zed", cohort_vertical="healthcare"),
        ]
        result = lg.LinkGraphBuilder(records).expand(
            root_type="receipt_id",
            root_id="dec_c300",
            max_hops=3,
            edge_types=["ingredient", "co_signer"],
        )
        refs = {n["entity_ref"]: n for n in result["nodes"]}
        self.assertIn("dec_c300", refs)
        self.assertEqual(refs["dec_c300"]["entity_type"], "receipt_id")
        self.assertIn("dec_c100", refs)
        self.assertIn("op_bob", refs)
        self.assertNotIn("dec_c900", refs)
        self.assertFalse(any(n["entity_ref"] == "dec" for n in result["nodes"]))

    def test_api_requires_root_id(self):
        client = app_mod.app.test_client()
        res = client.get("/v1/link-graph")
        self.assertEqual(res.status_code, 400)
        spec = client.get("/.well-known/link-graph.json")
        self.assertEqual(spec.status_code, 200)
        self.assertEqual(spec.get_json()["spec"], "gate-link-graph-v1")


class AnomalyTests(unittest.TestCase):
    def test_sample_size_gate_and_outlier_mask(self):
        records = []
        for i in range(25):
            records.append(
                _rec(
                    receipt_id=f"dec_norm_{i}",
                    operator_id=f"op_normal_{i}",
                    metrics={"block_rate": 0.05 + math.sin(i) * 0.01},
                )
            )
        records.append(_rec(receipt_id="out1", operator_id="op_outlier_1", metrics={"block_rate": 0.95}))
        records.append(_rec(receipt_id="out2", operator_id="op_outlier_2", metrics={"block_rate": 0.01}))
        for i in range(5):
            records.append(
                _rec(
                    receipt_id=f"small_{i}",
                    operator_id=f"op_small_{i}",
                    cohort_vertical="niche",
                    metrics={"block_rate": 0.99 if i == 0 else 0.02},
                )
            )
        base = ad.compute_baseline(records, cohort_vertical="fintech", metric="block_rate")
        self.assertGreaterEqual(base["sample_size"], ad.MIN_SAMPLE_SIZE)
        flags = ad.flag_anomalies(records, base)
        self.assertEqual(len(flags), 1)
        self.assertEqual(flags[0]["operator_id"], "op_outlier_1")
        self.assertIsNone(flags[0]["disposition"])
        self.assertFalse(flags[0]["reviewed"])
        small = ad.compute_baseline(records, cohort_vertical="niche", metric="block_rate")
        self.assertEqual(small["sample_size"], 5)
        self.assertEqual(ad.flag_anomalies(records, small), [])

    def test_api_empty_population(self):
        client = app_mod.app.test_client()
        res = client.get("/v1/anomaly-flags?cohort=fintech&metric=block_rate")
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertTrue(body["ok"])
        self.assertEqual(body["flags"], [])


if __name__ == "__main__":
    unittest.main()
