"""Items 141 / 147 — STIX 2.1 bundle; ATT&CK↔DISARM SROs need evidence."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-stix.db")
os.environ["GATE_STIX_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-stix.json")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import stix_export  # noqa: E402


class StixTests(unittest.TestCase):
    def setUp(self):
        path = os.environ["GATE_STIX_PATH"]
        if os.path.exists(path):
            os.remove(path)

    def test_empty_and_unknown_refused(self):
        self.assertEqual(stix_export.export_bundle(source_receipt_ids=[])["error"], "receipts_required")
        self.assertEqual(
            stix_export.export_bundle(source_receipt_ids=["r1"], atlas_technique_ids=["NOPE"])["error"],
            "atlas_unknown",
        )
        self.assertEqual(
            stix_export.link(
                source_ref="T1566",
                target_ref="T0013",
                relationship_type="facilitates",
                evidence_receipt_ids=[],
            )["error"],
            "evidence_required",
        )

    def test_stable_attack_pattern_ids_and_sro(self):
        rel = stix_export.link(
            source_ref="T1566",
            target_ref="T0013",
            relationship_type="precedes",
            evidence_receipt_ids=["r1", "r2"],
        )
        self.assertTrue(rel["ok"])
        a = stix_export.export_bundle(
            source_receipt_ids=["r1", "r2"],
            attack_technique_ids=["T1566"],
            disarm_technique_ids=["T0013"],
            shared_with=["example-isac"],
        )
        b = stix_export.export_bundle(
            source_receipt_ids=["r1", "r2"],
            attack_technique_ids=["T1566"],
            disarm_technique_ids=["T0013"],
        )
        self.assertEqual(a["stix_version"], "2.1")
        self.assertFalse(a["taxii"])
        self.assertEqual(a["bundle_object"]["type"], "bundle")
        ids_a = {o["id"] for o in a["bundle_object"]["objects"] if o["type"] == "attack-pattern"}
        ids_b = {o["id"] for o in b["bundle_object"]["objects"] if o["type"] == "attack-pattern"}
        self.assertEqual(ids_a, ids_b)
        sros = [o for o in a["bundle_object"]["objects"] if o["type"] == "relationship"]
        self.assertEqual(len(sros), 1)
        self.assertEqual(sros[0]["relationship_type"], "precedes")
        self.assertIn(rel["relationship_id"], a["relationship_ids"])


class StixFlaskTests(unittest.TestCase):
    def setUp(self):
        path = os.environ["GATE_STIX_PATH"]
        if os.path.exists(path):
            os.remove(path)
        self.client = app_mod.app.test_client()

    def test_page_and_export(self):
        page = self.client.get("/stix")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"Not a TAXII", page.data)
        posted = self.client.post(
            "/v1/stix",
            json={
                "source_receipt_ids": ["abc"],
                "atlas_technique_ids": ["AML.T0043"],
            },
        )
        self.assertEqual(posted.status_code, 201)
        body = posted.get_json()
        self.assertEqual(body["bundle_object"]["spec_version"], "2.1")


if __name__ == "__main__":
    unittest.main()
