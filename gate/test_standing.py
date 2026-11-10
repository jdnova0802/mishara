"""Items 112–116 — FRE 902 packet, identity, ingredients, redaction, binding."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-standing.db")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import agent_bureau as bureau  # noqa: E402
import receipt  # noqa: E402
import standing  # noqa: E402


def _issued_row(event_id: str, prev: str | None = None, **hop):
    issued = receipt.issue_receipt(
        event_id=event_id,
        fuse_id="fuse_x",
        job_id=None,
        decision="BLOCK",
        acted=False,
        verify_url="https://example/verify",
        created_at="2026-11-10T16:00:00+00:00",
        hop={"reason": "premium_exceeds_authority", **hop},
        prev_receipt_hash=prev,
    )
    return {
        "id": event_id,
        "fuse_id": "fuse_x",
        "job_id": None,
        "decision": "BLOCK",
        "acted": False,
        "verify_url": "https://example/verify",
        "created_at": "2026-11-10T16:00:00+00:00",
        "hop": {"reason": "premium_exceeds_authority", **hop},
        "prev_receipt_hash": prev,
        "receipt_hash": issued["receipt_hash"],
        "receipt_signature": issued["receipt_signature"],
        "receipt_public_key_fingerprint": issued["receipt_public_key_fingerprint"],
    }


class StandingLogicTests(unittest.TestCase):
    def test_packet_does_not_mint_a_live_cert(self):
        row = _issued_row("evt_a")
        pkt = standing.certification_packet(row)
        self.assertFalse(pkt["live_fre_902_cert"])
        self.assertFalse(pkt["legal_advice"])
        self.assertFalse(pkt["opposing_party_notice_ready"])
        self.assertTrue(pkt["hash_proof"]["match"])
        self.assertEqual(pkt["responsible_identity"], row["receipt_public_key_fingerprint"] or "UNSIGNED")

    def test_ingredients_embed_upstream_manifest(self):
        a = _issued_row("evt_a")
        b = _issued_row("evt_b", prev=a["receipt_hash"])
        ings = standing.ingredients(b, [a, b])
        self.assertEqual(len(ings["ingredients"]), 1)
        item = ings["ingredients"][0]
        self.assertEqual(item["ingredient_receipt_id"], "evt_a")
        self.assertTrue(item["hard_binding"])
        self.assertEqual(item["carried_manifest"]["canonical_receipt"]["id"], "evt_a")

    def test_redacting_verdict_is_rejected(self):
        check = standing.validate_redaction(["decision", "reason"])
        self.assertFalse(check["ok"])
        self.assertIn("decision", check["forbidden"])
        ok = standing.validate_redaction(["reason"])
        self.assertTrue(ok["ok"])
        rec = standing.redaction_event(event_id="evt_a", fields=["reason"], actor="fp")
        self.assertTrue(rec["logged"])
        self.assertTrue(rec["receipt_hash"])
        self.assertEqual(rec["decision"], "HOLD")

    def test_cdpi_is_soft_not_a_hash(self):
        score = bureau.score_agent([], [])
        self.assertFalse(score["hard_binding"])
        self.assertEqual(score["binding"], "soft")
        audit = standing.binding_audit()
        self.assertFalse(audit["interchangeable"])
        self.assertTrue(any(x["path"] == "cdpi.composite" for x in audit["soft"]))
        self.assertTrue(any(x["path"] == "receipt_hash" for x in audit["hard"]))


class StandingFlaskTests(unittest.TestCase):
    def setUp(self):
        self.client = app_mod.app.test_client()

    def test_pages(self):
        page = self.client.get("/standing")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"live FRE 902", page.data)
        api = self.client.get("/v1/standing")
        self.assertFalse(api.get_json()["live_fre_902_cert"])

    def test_redact_api_rejects_created_at(self):
        r = self.client.post("/v1/standing/redact", json={"event_id": "x", "fields": ["created_at"]})
        self.assertEqual(r.status_code, 409)


if __name__ == "__main__":
    unittest.main()
