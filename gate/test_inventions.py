"""Invention spine tests: sink, hard license, dual-charge, canary auto-DEAD, register bill."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
import uuid
from datetime import datetime, timezone
from unittest import mock

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-inventions.db")
os.environ.pop("GATE_LICENSE_REQUIRED", None)

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import finality_sink as sink  # noqa: E402
import license_fuse as lf  # noqa: E402
import dual_charge as dc  # noqa: E402
import canary  # noqa: E402
import register_bill as rb  # noqa: E402
import db as gate_db  # noqa: E402
import app as gate_app  # noqa: E402


def _now():
    return datetime.now(timezone.utc).isoformat()


class FinalitySinkTests(unittest.TestCase):
    def test_live_ok(self):
        out = sink.recheck(
            fuse_id="fuse_x",
            fuse_lookup=lambda _fid: {"state": "LIVE", "verdict": True, "halt": False},
        )
        self.assertTrue(out["ok"])
        self.assertFalse(out["halt"])

    def test_dead_halts(self):
        out = sink.recheck(
            fuse_id="fuse_x",
            fuse_lookup=lambda _fid: {"state": "DEAD", "verdict": False, "halt": True},
        )
        self.assertFalse(out["ok"])
        self.assertIn(out["reason"], (sink.REASON_FUSE_NOT_LIVE, sink.REASON_FUSE_HALT))

    def test_missing_callback_fails_closed(self):
        out = sink.recheck(fuse_id="fuse_x", fuse_lookup=None)
        self.assertFalse(out["ok"])
        self.assertEqual(out["reason"], sink.REASON_FUSE_UNREACHABLE)


class LicenseHardRequireTests(unittest.TestCase):
    def test_omit_ok_when_soft(self):
        with mock.patch.dict(os.environ, {"GATE_LICENSE_REQUIRED": "0"}, clear=False):
            self.assertTrue(lf.presented(None)["ok"])
            self.assertFalse(lf.presented(None)["fused"])

    def test_omit_fails_when_required(self):
        with mock.patch.dict(os.environ, {"GATE_LICENSE_REQUIRED": "1"}, clear=False):
            out = lf.presented(None)
            self.assertFalse(out["ok"])
            self.assertEqual(out["reason"], lf.REASON_REQUIRED)

    def test_weld_presented_always_requires(self):
        out = lf.presented_for_weld(None)
        self.assertFalse(out["ok"])
        self.assertEqual(out["reason"], lf.REASON_REQUIRED)


class DualChargeTests(unittest.TestCase):
    def test_rejects_same_charge_id_for_both_gates(self):
        lid = f"lic_dual_{uuid.uuid4().hex[:8]}"
        cid = f"chg_same_{uuid.uuid4().hex[:8]}"
        out = dc.unlock(
            license_id=lid,
            job_id=f"pc:DUAL-{uuid.uuid4().hex[:8]}",
            license_charge_id=cid,
            epoch_charge_id=cid,
        )
        self.assertFalse(out["ok"])
        self.assertEqual(out["reason"], dc.REASON_BOTH)

    def test_license_only_leg(self):
        lid = f"lic_only_{uuid.uuid4().hex[:8]}"
        cid = f"chg_lic_{uuid.uuid4().hex[:8]}"
        out = dc.unlock(
            license_id=lid,
            job_id=None,
            license_charge_id=cid,
            epoch_charge_id=None,
            require_epoch=False,
            require_license=True,
        )
        self.assertTrue(out["ok"])
        self.assertEqual(out["license"]["state"], "LIVE")


class CanaryAutoDeadTests(unittest.TestCase):
    def test_auto_kills_parent_on_bypass(self):
        lid = f"lic_canary_{uuid.uuid4().hex[:8]}"
        gate_db.upsert_license_parent(license_id=lid, state="LIVE", charge_id="chg_setup")
        job = f"pc:CANARY-AUTO-{uuid.uuid4().hex[:8]}"
        out = canary.report(
            write_path="POST /v1/payouts/x/release",
            job_id=job,
            reporter="ops@test",
            license_id=lid,
            confirm=True,
        )
        self.assertTrue(out["ok"])
        self.assertTrue(out["killed_parent"])
        self.assertEqual(out["parent"]["state"], "DEAD")
        snap = lf.snapshot(lid)
        self.assertEqual(snap["stored"], "DEAD")


class RegisterBillTests(unittest.TestCase):
    def test_bill_from_ledger(self):
        gate_db.record_cleared_flow(
            cleared_cents=12_000_000,
            hop_count=2,
            install_session_id=f"cs_test_{uuid.uuid4().hex[:8]}",
            note="invention test",
        )
        bill = rb.from_ledger(welded_writes=1, live_parents=0)
        self.assertTrue(bill["ok"])
        self.assertIn("invoice", bill)
        self.assertGreaterEqual(bill["invoice"]["total_cents"], 0)


class AppInventionRoutes(unittest.TestCase):
    def setUp(self):
        gate_app.app.config["TESTING"] = True
        self.client = gate_app.app.test_client()
        gate_app.GATE_DEV_MODE = True

    def test_well_known_sink_and_dual(self):
        s = self.client.get("/.well-known/finality-sink.json")
        self.assertEqual(s.status_code, 200)
        self.assertEqual(s.get_json()["spec"], "gate-finality-sink-v1")
        d = self.client.get("/.well-known/dual-charge.json")
        self.assertEqual(d.status_code, 200)
        self.assertEqual(d.get_json()["spec"], "gate-dual-charge-v1")
        inv = self.client.get("/.well-known/inventions.json")
        self.assertEqual(inv.status_code, 200)
        body = inv.get_json()
        self.assertEqual(body["spec"], "gate-inventions-v1")
        self.assertGreaterEqual(len(body["inventions"]), 6)
        self.assertTrue(body["overrides_killed"])

    def test_register_bill_ops(self):
        with mock.patch.object(gate_app, "_ops_authorized", return_value=True):
            r = self.client.post("/v1/register/bill", json={"welded_writes": 1})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.get_json()["ok"])

    def test_settlement_write_ops(self):
        with mock.patch.object(gate_app, "_ops_authorized", return_value=True):
            opened = self.client.post("/v1/settlement/window/open", json={})
        self.assertEqual(opened.status_code, 200)
        wid = opened.get_json()["window"]["id"]
        with mock.patch.object(gate_app, "_ops_authorized", return_value=True):
            settled = self.client.post(
                f"/v1/settlement/window/{wid}/settle",
                json={
                    "obligations": [
                        {
                            "member_id": "m1",
                            "counterparty_id": "m2",
                            "asset_class": "bind_only",
                            "gross_cents": 1000,
                            "direction": "pay",
                        }
                    ]
                },
            )
        self.assertEqual(settled.status_code, 200)
        self.assertTrue(settled.get_json()["ok"])
        self.assertIn(settled.get_json()["window"]["state"], ("SETTLED", "DEFAULTED"))


class ExclusiveHardenTests(unittest.TestCase):
    def test_closed_world_hardens(self):
        import exclusive as ex

        out = ex.classify(
            {"welded": True, "spec": "gate-welded-act-v2"},
            {"holds": True, "write_path": "POST /v1/act"},
            demo=False,
            closed_world=True,
        )
        self.assertTrue(out["exclusive"])
        self.assertTrue(out["hardened"])
        self.assertFalse(out["museum"])
        self.assertFalse(out["their_production"])
        self.assertTrue(out["bypass_must_cost_more"])


if __name__ == "__main__":
    unittest.main()
