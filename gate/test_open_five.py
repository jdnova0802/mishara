"""Items 163–167 — inventions against tonight's actual unsolved gaps."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-open-five.db")
for key, name in (
    ("GATE_EXPOSURE_BOND_PATH", "bond.json"),
    ("GATE_HEAD_LEASE_PATH", "lease.json"),
    ("GATE_HINGE_PATH", "hinge.json"),
):
    os.environ[key] = os.path.join(tempfile.gettempdir(), f"gate-test-open-five-{name}")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import exposure_bond  # noqa: E402
import head_lease  # noqa: E402
import hinge  # noqa: E402
import media_untrusted  # noqa: E402
import stranger_graph  # noqa: E402


def _wipe():
    for key in ("GATE_EXPOSURE_BOND_PATH", "GATE_HEAD_LEASE_PATH", "GATE_HINGE_PATH"):
        path = os.environ[key]
        if os.path.exists(path):
            os.remove(path)


class ExposureTests(unittest.TestCase):
    def setUp(self):
        _wipe()

    def test_underbond_fails_closed_forfeit_is_not_profit(self):
        b = exposure_bond.post(legal_person="Acme", posted="8", covers_ref="att_1")
        miss = exposure_bond.covers(bond_id=b["bond_id"], value_at_risk="20")
        self.assertFalse(miss["covers"])
        self.assertEqual(miss["error"], "underbonded")
        ok = exposure_bond.covers(bond_id=b["bond_id"], value_at_risk="8")
        self.assertTrue(ok["covers"])
        f = exposure_bond.forfeit(bond_id=b["bond_id"], reason="attestation lied")
        self.assertEqual(f["forfeited"], "8")
        self.assertFalse(f["profit_recovered"])


class LeaseTests(unittest.TestCase):
    def setUp(self):
        _wipe()

    def test_head_move_and_refresh_new_id(self):
        ls = head_lease.issue(subject_ref="org:acme", head_hash="aaa", ttl_ms=60_000)
        self.assertTrue(head_lease.verify(lease_id=ls["lease_id"], current_head_hash="aaa")["ok"])
        moved = head_lease.verify(lease_id=ls["lease_id"], current_head_hash="bbb")
        self.assertEqual(moved["error"], "head_moved")
        nxt = head_lease.refresh(lease_id=ls["lease_id"], head_hash="bbb")
        self.assertNotEqual(nxt["lease_id"], ls["lease_id"])
        self.assertEqual(nxt["prior_lease_id"], ls["lease_id"])
        expired = head_lease.verify(
            lease_id=nxt["lease_id"],
            current_head_hash="bbb",
            now=datetime.now(timezone.utc) + timedelta(hours=2),
        )
        self.assertEqual(expired["error"], "expired")


class HingeTests(unittest.TestCase):
    def setUp(self):
        _wipe()

    def test_falsifier_and_small_n_shapes(self):
        miss = hinge.rate(
            flag_id="f1",
            reviewer_org_id="org_a",
            rating="confirmed",
            falsifier="",
        )
        self.assertEqual(miss["error"], "falsifier_required")
        hinge.rate(flag_id="old", reviewer_org_id="org_b", rating="false_positive", falsifier="a closed case")
        hinge.rate(flag_id="f1", reviewer_org_id="org_a", rating="confirmed", falsifier="receipt missing")
        one = hinge.adjudicate(flag_id="f1")
        self.assertEqual(one["verdict"], "dormant")
        hinge.rate(flag_id="f1", reviewer_org_id="org_b", rating="confirmed", falsifier="receipt missing")
        hinged = hinge.adjudicate(flag_id="f1")
        self.assertEqual(hinged["verdict"], "hinged")
        self.assertIsNone(hinged["helpfulness_factor"])
        hinge.rate(flag_id="f2", reviewer_org_id="org_a", rating="confirmed", falsifier="x")
        hinge.rate(flag_id="f2", reviewer_org_id="org_b", rating="false_positive", falsifier="y")
        hold = hinge.adjudicate(flag_id="f2")
        self.assertEqual(hold["verdict"], "hold")


class StrangerTests(unittest.TestCase):
    def test_refuses_multi_hop_and_does_not_color_sigma(self):
        too = stranger_graph.breath({"query": {"max_hops": 3}, "edges": [{}]})
        self.assertEqual(too["error"], "too_much_graph")
        card = stranger_graph.breath(
            {
                "query": {"max_hops": 1},
                "edges": [
                    {
                        "from_node_id": "receipt_id:aaa",
                        "to_node_id": "receipt_id:bbb",
                        "edge_type": "shared_device_fingerprint",
                        "source_receipt_id": "aaa",
                    }
                ],
            },
            flags=[{"disposition": None}],
        )
        self.assertTrue(card["ok"])
        self.assertFalse(card["sigma_colored"])
        self.assertIn("not a finding of coordination", card["sentence"])
        self.assertIn("not a verdict", card["flag_line"])
        self.assertTrue(card["card_sha256"])


class MediaTests(unittest.TestCase):
    def test_doctrine_not_detector(self):
        st = media_untrusted.stance()
        self.assertFalse(st["detector_built"])
        self.assertEqual(st["call_status"], "untrusted_by_doctrine")
        block = media_untrusted.refuse_media_claim(media_evidence_claimed=True)
        self.assertEqual(block["error"], "media_is_not_evidence")
        self.assertIsNone(media_untrusted.refuse_media_claim(media_evidence_claimed=False))


class PageSmoke(unittest.TestCase):
    def test_stranger_page_has_no_svg(self):
        c = app_mod.app.test_client()
        page = c.get("/stranger")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"One hop", page.data)
        self.assertNotIn(b"desk-svg", page.data)
        empty = c.get("/v1/stranger-graph")
        self.assertEqual(empty.status_code, 200)
        self.assertIn("Empty is empty", empty.get_json()["sentence"])
        hops = c.get("/v1/stranger-graph?root_id=x&max_hops=4")
        self.assertEqual(hops.status_code, 409)


if __name__ == "__main__":
    unittest.main()
