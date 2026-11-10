"""Item 136 — ATLAS refs are soft labels, not receipt hashes."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-atlas.db")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import atlas  # noqa: E402


class AtlasTests(unittest.TestCase):
    def test_jailbreak_maps_to_craft_adversarial_data(self):
        ref = atlas.classify_event(
            {
                "id": "evt_1",
                "receipt_hash": "abc_def",
                "decision": "BLOCK",
                "hop": {"reason": "jailbreak prompt injection"},
            }
        )
        self.assertEqual(ref["classified_by"], "rule")
        self.assertFalse(ref["hard_binding"])
        self.assertEqual(ref["evidentiary_weight"], "CORROBORATING_ONLY")
        self.assertEqual(ref["atlas"]["atlas_technique_id"], "AML.T0043")

    def test_unlabeled_block_is_not_a_fake_pattern(self):
        ref = atlas.classify_event({"id": "evt_2", "decision": "BLOCK", "hop": {"reason": "premium_over_limit"}})
        self.assertIsNone(ref["atlas"])
        self.assertIn("unlabeled", ref["note"].lower())

    def test_api_requires_event_id(self):
        client = app_mod.app.test_client()
        self.assertEqual(client.get("/v1/atlas-ref").status_code, 400)
        self.assertEqual(client.get("/v1/atlas-ref?event_id=missing").status_code, 404)
        spec = client.get("/.well-known/atlas.json").get_json()
        self.assertEqual(spec["spec"], "gate-atlas-ref-v1")
        self.assertFalse(spec["hard_binding"])


if __name__ == "__main__":
    unittest.main()
