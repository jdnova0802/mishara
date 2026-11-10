"""Items 58–68 — live map filters, edges, roles, palette, notes."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-live-map.db")
os.environ["GATE_MAP_NOTES_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-map-notes.json")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import live_map  # noqa: E402


ROWS = [
    {
        "id": "a",
        "decision": "BLOCK",
        "created_at": "2026-11-10T10:00:00+00:00",
        "fuse_id": "fuse_mine",
        "receipt_hash": "h1",
        "prev_receipt_hash": None,
        "hop": {"state": "CO", "line": "GL", "vertical": "insurance"},
    },
    {
        "id": "b",
        "decision": "BLOCK",
        "created_at": "2026-11-10T11:00:00+00:00",
        "fuse_id": "fuse_other",
        "receipt_hash": "h2",
        "prev_receipt_hash": "h1",
        "hop": {"state": "CO", "vertical": "fleet"},
    },
]


class LiveMapLogicTests(unittest.TestCase):
    def test_edges_follow_prev_hash(self):
        payload = live_map.view(ROWS, {})
        self.assertEqual(len(payload["points"]), 2)
        self.assertEqual(len(payload["edges"]), 1)
        self.assertEqual(payload["edges"][0]["from"], "a")
        self.assertEqual(payload["edges"][0]["to"], "b")

    def test_mine_hides_network(self):
        payload = live_map.view(ROWS, {"org": "fuse_mine", "view": "mine"})
        self.assertEqual([p["id"] for p in payload["points"]], ["a"])

    def test_insurer_role_filters_fleet(self):
        payload = live_map.view(ROWS, {"role": "insurer"})
        ids = [p["id"] for p in payload["points"]]
        self.assertIn("a", ids)
        self.assertNotIn("b", ids)

    def test_watch_and_until(self):
        only_ny = live_map.view(ROWS, {"watch": "NY"})
        self.assertEqual(only_ny["points"], [])
        early = live_map.view(ROWS, {"until": "2026-11-10T10:30:00+00:00"})
        self.assertEqual([p["id"] for p in early["points"]], ["a"])

    def test_colorblind_palette_and_deep_link(self):
        payload = live_map.view(ROWS, {"palette": "cb", "cx": 10, "cy": 20, "z": 2})
        self.assertEqual(payload["palette"], "cb")
        self.assertTrue(payload["deep_link"].startswith("/map?"))
        self.assertIn("palette=cb", payload["deep_link"])

    def test_threshold_hides_short_chains(self):
        payload = live_map.view(ROWS, {"min_chain": 2})
        self.assertEqual([p["id"] for p in payload["points"]], ["b"])

    def test_notes_org_only_hidden_from_insurer(self):
        live_map.add_note(event_id="a", text="internal only", org_only=True)
        pub = live_map.view(ROWS, {"role": "insurer"})
        self.assertEqual(pub["notes"], [])
        inn = live_map.view(ROWS, {"role": "internal"})
        self.assertTrue(inn["notes"])


class LiveMapFlaskTests(unittest.TestCase):
    def setUp(self):
        self.client = app_mod.app.test_client()

    def test_map_page_has_pan_surface(self):
        r = self.client.get("/map")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"live-map", r.data)
        self.assertIn(b"Colorblind", r.data)

    def test_api_accepts_deep_link_query(self):
        r = self.client.get("/v1/restraint-map?role=regulator&palette=cb")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["spec"], "gate-live-map-v1")


if __name__ == "__main__":
    unittest.main()
