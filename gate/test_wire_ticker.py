"""Items 87–90 — mixed wire ticker, docket context, monitor, dateline."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-wire-ticker.db")
os.environ["GATE_DOCKET_WATCH_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-docket-watch.json")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import wire  # noqa: E402

DOCKETS = [
    {
        "id": "naic_v5_written",
        "label": "NAIC AI Risk Evaluation Supplement v5.0 — written comment",
        "status": "draft_in_repo",
        "deadline": "COB Tuesday, September 29, 2026",
        "path": "docs/naic/NAIC_AI_RISK_EVAL_SUPPLEMENT_V5_COMMENT_DRAFT.md",
        "url": None,
        "plain": "Four asks live in this draft.",
    },
    {
        "id": "hmt_q15",
        "label": "HM Treasury Q15",
        "status": "draft_ready",
        "url": "https://www.gov.uk/government/consultations/modernising-payment-services-regulation",
        "plain": "Agentic authentication / consent / liability.",
    },
]

ROWS = [
    {
        "id": "evt_ins",
        "decision": "BLOCK",
        "created_at": "2026-11-10T16:00:00+00:00",
        "hop": {"vertical": "insurance", "state": "CO", "reason": "premium_exceeds_authority"},
    },
    {
        "id": "evt_pay",
        "decision": "HOLD",
        "created_at": "2026-11-10T15:00:00+00:00",
        "hop": {"vertical": "payments", "rail": "rtp", "reason": "rtp"},
    },
    {
        "id": "evt_other",
        "decision": "ALLOW",
        "created_at": "2026-11-10T14:00:00+00:00",
        "hop": {"vertical": "hiring", "reason": "unmapped_rule"},
    },
]


class WireLogicTests(unittest.TestCase):
    def test_dateline_is_wire_copy(self):
        when = datetime(2026, 11, 10, 16, 0, tzinfo=timezone.utc)
        text = wire.dateline(
            jurisdiction="Kansas City",
            source="NAIC",
            when=when,
            text="Four asks live in this draft.",
        )
        self.assertEqual(
            text,
            "KANSAS CITY (NAIC) — Nov. 10, 2026 — Four asks live in this draft.",
        )

    def test_feed_mixes_internal_and_named_dockets(self):
        payload = wire.feed(ROWS, DOCKETS)
        self.assertEqual(payload["spec"], "gate-wire-ticker-v1")
        self.assertFalse(payload["scraped"])
        self.assertFalse(payload["reuters"])
        kinds = {r["kind"] for r in payload["rows"]}
        self.assertIn("internal", kinds)
        self.assertIn("external", kinds)
        ins = next(r for r in payload["rows"] if r["event_id"] == "evt_ins")
        self.assertEqual(ins["decision"], "BLOCK")
        self.assertTrue(ins["reason_text"].startswith("CO (Gate)"))
        self.assertEqual(ins["regulatory_context"]["docket_id"], "naic_v5_written")
        self.assertTrue(ins["regulatory_context"]["present"])

    def test_vertical_filter(self):
        only = wire.feed(ROWS, DOCKETS, vertical="insurance")
        verts = {r["vertical"] for r in only["rows"]}
        self.assertTrue(all("insurance" in v for v in verts))
        self.assertTrue(any(r["event_id"] == "evt_ins" for r in only["rows"]))
        self.assertFalse(any(r["event_id"] == "evt_pay" for r in only["rows"]))

    def test_unmapped_rule_has_no_invented_docket(self):
        payload = wire.feed(ROWS, DOCKETS)
        other = next(r for r in payload["rows"] if r["event_id"] == "evt_other")
        self.assertIsNone(other["regulatory_context"])

    def test_monitor_flags_a_changed_docket_and_its_vertical(self):
        first = wire.monitor(DOCKETS, persist=False, previous={})
        self.assertFalse(first["scraped"])
        self.assertEqual(first["changed"], [])
        fps = {d["id"]: wire._fingerprint(d) for d in DOCKETS}
        fps.update({w["id"]: wire._fingerprint(w) for w in wire.WATCHES})
        mutated = [dict(d) for d in DOCKETS]
        mutated[0] = dict(mutated[0], status="filed")
        second = wire.monitor(mutated, persist=False, previous=fps)
        changed_ids = [c["id"] for c in second["changed"]]
        self.assertIn("naic_v5_written", changed_ids)
        naic = next(c for c in second["changed"] if c["id"] == "naic_v5_written")
        self.assertEqual(naic["vertical"], "insurance")

    def test_drilldown_ties_rule_to_bulletin(self):
        hit = wire.drilldown("evt_ins", ROWS, DOCKETS)
        self.assertIsNotNone(hit)
        self.assertEqual(hit["regulatory_context"]["docket_id"], "naic_v5_written")
        self.assertIn("NAIC", hit["regulatory_context"]["label"])


class WireFlaskTests(unittest.TestCase):
    def setUp(self):
        self.client = app_mod.app.test_client()

    def test_pages_200(self):
        for path in ("/wire", "/wire?vertical=insurance", "/radar"):
            r = self.client.get(path)
            self.assertEqual(r.status_code, 200, path)

    def test_api_is_not_a_newswire(self):
        r = self.client.get("/v1/wire")
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertFalse(body["scraped"])
        self.assertFalse(body["reuters"])
        self.assertIn("named dockets", body["plain"])

    def test_monitor_api(self):
        r = self.client.get("/v1/wire/monitor")
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertFalse(body["scraped"])
        self.assertIn("Not a live scrape", body["plain"])

    def test_radar_shows_monitor_flags(self):
        page = self.client.get("/radar")
        self.assertIn(b"docket-monitor", page.data)
        self.assertIn(b"Not a live scrape", page.data)


if __name__ == "__main__":
    unittest.main()
