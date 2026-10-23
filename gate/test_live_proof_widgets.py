"""Homepage lookup, merkle strip, Bind Room countdown, counsel card, receipt OG."""
from __future__ import annotations

import os
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-live-proof-widgets.db")
os.environ.pop("RENDER_EXTERNAL_URL", None)
os.environ.pop("RENDER_EXTERNAL_HOSTNAME", None)

if os.path.exists(os.environ["GATE_DB_PATH"]):
    os.remove(os.environ["GATE_DB_PATH"])

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import db  # noqa: E402
import evidence_log  # noqa: E402
import receipt_card  # noqa: E402


class LiveProofWidgetTests(unittest.TestCase):
    def setUp(self):
        self.client = app_mod.app.test_client()

    def test_client_js_folds_inclusion_and_does_not_treat_seal_as_proof(self):
        js = (pathlib.Path(HERE) / "static" / "live_proof.js").read_text(encoding="utf-8")
        self.assertIn("verifyInclusion", js)
        self.assertIn("idx % 2 === 0", js)
        self.assertIn("/.well-known/evidence-head.json", js)
        self.assertIn("/proof.json", js)
        self.assertIn("/.well-known/seal-anchor.json", js)
        self.assertIn("/v1/blotter", js)
        self.assertNotIn("/v1/seal?event_id", js)
        self.assertIn("AUTHORIZE", js)
        self.assertIn("DECLINE", js)
        self.assertIn("LATE", js)
        self.assertIn("HOLDS", js)

    def test_homepage_empty_states_are_server_rendered(self):
        home = self.client.get("/")
        self.assertEqual(home.status_code, 200)
        self.assertEqual(home.data.count(b"btn-primary"), 1)
        text = home.get_data(as_text=True)
        self.assertIn("Museum until you paste a real id", text)
        self.assertIn("No published Base root", text)
        self.assertIn("does not pulse a tx that did not land", text)
        self.assertIn("Check inclusion", text)
        self.assertNotIn("btn-primary\">Check", text)
        self.assertIn("Empty tree, not a customer", text)
        self.assertIn("sha256(leaf ‖ sib)", text)
        self.assertIn("data-museum-hop", text)
        self.assertNotIn("their_production", text.lower())

    def test_public_proof_is_enough_for_the_widget(self):
        event_id = db.record_bind_event(
            fuse_id="fuse_velaru_drill",
            decision="HALT",
            job_id="pc:widget-1",
            verify_url="https://velaru.xyz/verify?r=widget-1",
            hop={"state": "DEAD", "halt": True, "verdict": "HALT"},
            acted=False,
        )
        proof = self.client.get(f"/.well-known/receipt/{event_id}/proof.json").get_json()
        head = self.client.get("/.well-known/evidence-head.json").get_json()
        receipt = self.client.get(f"/.well-known/receipt/{event_id}.json").get_json()
        self.assertEqual(receipt["decision"], "HALT")
        self.assertTrue(
            evidence_log.verify_inclusion(
                leaf_hash=proof["receipt_hash"],
                root_hash=head["root_hash"],
                proof=proof["inclusion"],
            )
        )
        missing = self.client.get("/.well-known/receipt/does-not-exist/proof.json")
        self.assertEqual(missing.status_code, 404)

    def test_seal_anchor_latest_stays_null_when_unpublished(self):
        body = self.client.get("/.well-known/seal-anchor.json").get_json()
        self.assertEqual(body["latest"]["published"], None)
        self.assertEqual(body["cadence_seconds"], 900)

    def test_bind_room_countdown_empty_copy(self):
        page = self.client.get("/bind-room").get_data(as_text=True)
        self.assertIn("due_at − now()", page)
        self.assertIn("Empty is the log, not missing product", page)
        book = self.client.get("/v1/blotter").get_json()
        self.assertEqual(book["window_minutes"], 60)
        self.assertNotIn("their_production", book)
        self.assertIn("Copy counsel object", page)
        self.assertIn("counsel_copy.js", page)
        self.assertNotIn("their_production", page.lower())

    def test_demo_hop_mints_counsel_object_and_og_card(self):
        dead = {
            "ok": True,
            "verdict": False,
            "halt": True,
            "state": "DEAD",
            "verify_url": "https://velaru.xyz/verify?r=counsel",
        }
        with mock.patch.object(app_mod, "velaru_fuse", return_value=(dead, 200, {})):
            hop = self.client.post("/demo/hop", json={"fuse_id": "fuse_velaru_drill"})
        self.assertEqual(hop.status_code, 200)
        body = hop.get_json()
        self.assertNotIn("their_production", body)
        self.assertTrue(body["counsel"]["museum"])
        event_id = body["event_id"]
        self.assertEqual(body["counsel"]["word"], "BLOCK")
        self.assertIn(event_id, body["counsel"]["proof"])
        self.assertIn("/?hop=" + event_id, body["check_url"])
        self.assertIn("proof.json", body["counsel"]["text"])
        proof = self.client.get(f"/.well-known/receipt/{event_id}/proof.json")
        self.assertEqual(proof.status_code, 200)
        page = self.client.get(f"/receipt/{event_id}")
        self.assertEqual(page.status_code, 200)
        html = page.get_data(as_text=True)
        self.assertIn("og:image", html)
        self.assertIn("Museum hop", html)
        self.assertIn(body["counsel"]["word"], html)
        self.assertNotIn("their_production", html.lower())
        png = self.client.get(f"/receipt/{event_id}/og.png")
        self.assertEqual(png.status_code, 200)
        self.assertEqual(png.content_type, "image/png")
        self.assertTrue(png.data.startswith(b"\x89PNG"))
        self.assertGreater(len(png.data), 400)
        docs = self.client.get("/docs").get_data(as_text=True)
        self.assertIn("Check inclusion on homepage", docs)
        self.assertIn("counsel_copy.js", docs)
        self.assertIn('id="demo-check-link"', docs)

    def test_og_png_omits_production_flag(self):
        png = receipt_card.render_og_png(word="BLOCK", hash_short="abc123…def456", museum=True)
        self.assertTrue(png.startswith(b"\x89PNG"))
        self.assertNotIn(b"their_production", png)


if __name__ == "__main__":
    unittest.main()
