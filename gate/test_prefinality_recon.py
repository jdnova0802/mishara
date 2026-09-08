"""Prefinality reconstruction-as-law tests."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from unittest import mock

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-prefinality-recon.db")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import prefinality_recon as recon  # noqa: E402
import app as gate_app  # noqa: E402


class DescriptorTests(unittest.TestCase):
    def test_payout_write_fingerprint_stable(self):
        a = recon.payout_write_fingerprint(payout_id="pay_1")
        b = recon.payout_write_fingerprint(payout_id="pay_1")
        self.assertEqual(a, b)
        self.assertNotEqual(a, recon.payout_write_fingerprint(payout_id="pay_2"))

    def test_reconstruct_descriptor_non_pii(self):
        d = recon.reconstruct_descriptor(
            rail="x402",
            transfer={
                "amount": "12.50",
                "currency": "USDC",
                "counterparty": "0x" + "ab" * 20,
            },
            boundary=recon.BOUNDARY_PAYOUT,
            payout_id="pay_abc",
            fuse_id="fuse_x",
        )
        self.assertEqual(d["boundary"], recon.BOUNDARY_PAYOUT)
        self.assertTrue(d["transfer_fingerprint"])
        self.assertTrue(d["write_fingerprint"])
        self.assertNotIn("license_number", d)
        self.assertFalse(d["their_production"])


class MeetAndBlowUpTests(unittest.TestCase):
    def test_meet_fail_closed(self):
        m = recon.meet(
            [
                {"id": "a", "ok": True},
                {"id": "b", "ok": False, "reason": "x"},
            ]
        )
        self.assertFalse(m["ok"])
        self.assertEqual(m["failed"], ["b"])

    def test_blow_up_when_spent_without_clear(self):
        report = recon.blow_up_report(
            write_path="POST /v1/payouts/pay_1/release",
            clear_result={"clear": False},
            spent=True,
        )
        self.assertTrue(report["blow_up"])


class ClearLawTests(unittest.TestCase):
    def test_missing_receipt_halts(self):
        out = recon.clear(
            rail="x402",
            transfer={
                "amount": "1",
                "currency": "USDC",
                "counterparty": "0x" + "cd" * 20,
            },
            receipt=None,
            require_fuse=False,
            payout_id="pay_x",
        )
        self.assertFalse(out["clear"])
        self.assertTrue(out["halt"])
        self.assertTrue(out.get("authority_blow_up_class"))

    def test_clear_ok_with_valid_receipt_and_live_fuse(self):
        transfer = {
            "amount": "1.00",
            "currency": "USDC",
            "counterparty": "0x" + "11" * 20,
        }
        import prefinality as pf

        fp = pf.transfer_fingerprint(rail="x402", transfer=transfer)
        fake_verify = {
            "valid": True,
            "decision": "GO",
            "reason": None,
            "payload": {"fp": fp, "dec": "GO"},
        }
        with mock.patch.object(pf, "verify_receipt_jwt", return_value=fake_verify):
            out = recon.clear(
                rail="x402",
                transfer=transfer,
                receipt="header.payload.sig",
                presented_fingerprint=fp,
                fuse_id="fuse_live",
                fuse_lookup=lambda _fid: {"state": "LIVE", "verdict": True, "halt": False},
                require_fuse=True,
                payout_id="pay_ok",
            )
        self.assertTrue(out["clear"])
        self.assertFalse(out["halt"])
        self.assertTrue(out["composition"]["ok"])

    def test_dead_fuse_blocks_even_with_go_receipt(self):
        transfer = {
            "amount": "1.00",
            "currency": "USDC",
            "counterparty": "0x" + "22" * 20,
        }
        import prefinality as pf

        fp = pf.transfer_fingerprint(rail="x402", transfer=transfer)
        fake_verify = {
            "valid": True,
            "decision": "GO",
            "reason": None,
            "payload": {"fp": fp, "dec": "GO"},
        }
        with mock.patch.object(pf, "verify_receipt_jwt", return_value=fake_verify):
            out = recon.clear(
                rail="x402",
                transfer=transfer,
                receipt="header.payload.sig",
                presented_fingerprint=fp,
                fuse_id="fuse_dead",
                fuse_lookup=lambda _fid: {"state": "DEAD", "verdict": False, "halt": True},
                require_fuse=True,
            )
        self.assertFalse(out["clear"])
        self.assertIn("fuse_sink", out["composition"]["failed"])


class AppReconRoutes(unittest.TestCase):
    def setUp(self):
        gate_app.app.config["TESTING"] = True
        self.client = gate_app.app.test_client()
        gate_app.GATE_DEV_MODE = True

    def test_well_known(self):
        r = self.client.get("/.well-known/prefinality-reconstruction.json")
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(body["spec"], "gate-prefinality-reconstruction-v1")
        self.assertIn("Clear", body["law"])
        self.assertEqual(body["second_boundary"]["id"], "peg_out_withdraw")
        self.assertEqual(body["door_order"][1]["id"], "peg_out_withdraw")

    def test_peg_out_fingerprint(self):
        a = recon.peg_out_write_fingerprint(bridge_id="br_1", withdraw_id="wd_1")
        b = recon.peg_out_write_fingerprint(bridge_id="br_1", withdraw_id="wd_1")
        self.assertEqual(a, b)
        self.assertIsNone(recon.peg_out_write_fingerprint(bridge_id="br_1", withdraw_id=None))

    def test_inventions_lists_recon(self):
        r = self.client.get("/.well-known/inventions.json")
        specs = {i["spec"] for i in r.get_json()["inventions"]}
        self.assertIn("gate-prefinality-reconstruction-v1", specs)


if __name__ == "__main__":
    unittest.main()
