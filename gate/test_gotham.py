"""Items 123–124 — custody graph over ingredients; monospace machine-truth."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-gotham.db")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import gotham  # noqa: E402
import receipt  # noqa: E402


def _row(event_id, prev=None, **hop):
    issued = receipt.issue_receipt(
        event_id=event_id,
        fuse_id="fuse_x",
        job_id=None,
        decision="BLOCK",
        acted=False,
        verify_url="https://example/verify",
        created_at="2026-11-10T16:00:00+00:00",
        hop=hop or {"reason": "premium_exceeds_authority", "state": "DEAD"},
        prev_receipt_hash=prev,
    )
    return {
        "id": event_id,
        "decision": "BLOCK",
        "created_at": "2026-11-10T16:00:00+00:00",
        "hop": hop or {"reason": "premium_exceeds_authority", "state": "DEAD"},
        "prev_receipt_hash": prev,
        "receipt_hash": issued["receipt_hash"],
        "fuse_id": "fuse_x",
        "acted": False,
        "verify_url": "https://example/verify",
        "job_id": None,
        "receipt_signature": issued["receipt_signature"],
        "receipt_public_key_fingerprint": issued["receipt_public_key_fingerprint"],
    }


class GothamLogicTests(unittest.TestCase):
    def test_ingredient_edge_links_gate_nodes(self):
        a = _row("a")
        b = _row("b", prev=a["receipt_hash"])
        payload = gotham.view([a, b], event_id="b")
        kinds = {e["kind"] for e in payload["edges"]}
        self.assertIn("ingredient", kinds)
        roles = {n["role"] for n in payload["nodes"]}
        self.assertIn("gate", roles)
        self.assertIn("erra", roles)
        self.assertIn("verra", roles)


class GothamFlaskTests(unittest.TestCase):
    def setUp(self):
        self.client = app_mod.app.test_client()

    def test_graph_page_and_css_machine_truth(self):
        page = self.client.get("/custody-graph")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"gotham-graph", page.data)
        chain = self.client.get("/chain")
        self.assertIn(b"/custody-graph", chain.data)
        css = self.client.get("/static/style.css")
        self.assertIn(b".machine-truth", css.data)
        self.assertIn(b"font-family: var(--mono)", css.data)
        self.assertIn(b"font-family: var(--sans)", css.data)


if __name__ == "__main__":
    unittest.main()
