"""Tests for remaining applicable-now Bind Room inventions."""
from __future__ import annotations

import time
import unittest

try:
    from gate import payout_throat as payout_mod
    from gate import twin_diode as twin_mod
    from gate import agent_passport_weld as passport_mod
    from gate import bypass_canary as canary_mod
    from gate import restraint_invoice as invoice_mod
    from gate import desk_quorum_fob as quorum_mod
    from gate import panic_latch as panic_mod
    from gate import receipt_mirror as mirror_mod
    from gate import deadman_echo as deadman_mod
    from gate import witness_seat as witness_mod
    from gate import throat as throat_mod
except ImportError:
    import payout_throat as payout_mod
    import twin_diode as twin_mod
    import agent_passport_weld as passport_mod
    import bypass_canary as canary_mod
    import restraint_invoice as invoice_mod
    import desk_quorum_fob as quorum_mod
    import panic_latch as panic_mod
    import receipt_mirror as mirror_mod
    import deadman_echo as deadman_mod
    import witness_seat as witness_mod
    import throat as throat_mod


class PayoutThroatTests(unittest.TestCase):
    def test_timeout_chokes_payout(self):
        r = payout_mod.evaluate(write_kind="payout", timeout=True, decision="ALLOW")
        self.assertTrue(r["applicable"])
        self.assertEqual(r["state"], throat_mod.CHOKE)

    def test_non_payout_aside(self):
        r = payout_mod.evaluate(write_kind="bind", decision="ALLOW", allow_payout=True)
        self.assertFalse(r["applicable"])


class TwinDiodeTests(unittest.TestCase):
    def test_read_passes(self):
        r = twin_mod.evaluate(direction="read")
        self.assertEqual(r["verdict"], twin_mod.VERDICT_PASS)
        self.assertTrue(r["may_proceed"])

    def test_write_without_macro_blocks(self):
        r = twin_mod.evaluate(direction="write", would_actuate=True)
        self.assertEqual(r["verdict"], twin_mod.VERDICT_BLOCK)
        self.assertFalse(r["may_proceed"])

    def test_write_with_macro_and_live(self):
        r = twin_mod.evaluate(
            direction="write",
            would_actuate=True,
            secure_write_macro=True,
            live_cleared=True,
        )
        self.assertEqual(r["verdict"], twin_mod.VERDICT_PASS)


class AgentPassportTests(unittest.TestCase):
    def test_password_forged(self):
        r = passport_mod.evaluate(tool_class="wire", password_as_auth=True)
        self.assertEqual(r["verdict"], passport_mod.VERDICT_FORGED)
        self.assertFalse(r["may_proceed"])

    def test_mint_and_clear(self):
        import os

        os.environ["GATE_DEV_MODE"] = "1"
        minted = passport_mod.mint_passport(agent_id="a1", tool_class="wire")
        r = passport_mod.evaluate(
            tool_class="wire",
            agent_id="a1",
            passport=minted["passport"],
            decision="ALLOW",
        )
        self.assertTrue(r["may_proceed"] or r["verdict"] in (passport_mod.VERDICT_CLEAR, throat_mod.OPEN))


class BypassCanaryTests(unittest.TestCase):
    def test_drills(self):
        report = canary_mod.drills()
        self.assertTrue(report["all_ok"], report["drills"])


class RestraintInvoiceTests(unittest.TestCase):
    def test_billable_on_halt(self):
        inv = invoice_mod.draft(decision="HALT", acted=False, job_id="pc:1")
        self.assertTrue(inv["billable"])
        self.assertEqual(inv["sku"], invoice_mod.SKU)


class DeskQuorumTests(unittest.TestCase):
    def test_sacred_short(self):
        r = quorum_mod.evaluate(mass_class="sacred", uw_approvals=1, charge_present=False)
        self.assertEqual(r["verdict"], quorum_mod.VERDICT_SHORT)
        self.assertFalse(r["may_proceed"])

    def test_light_not_required(self):
        r = quorum_mod.evaluate(mass_class="light")
        self.assertEqual(r["verdict"], quorum_mod.VERDICT_NOT_REQUIRED)


class PanicLatchTests(unittest.TestCase):
    def test_panic_denies_commit(self):
        r = panic_mod.evaluate(incident_declared=True, would_commit=True)
        self.assertIn(r["verdict"], (panic_mod.VERDICT_DENY, panic_mod.VERDICT_ESCALATE))
        self.assertFalse(r["may_proceed"])

    def test_normal_clear(self):
        r = panic_mod.evaluate(would_commit=True)
        self.assertEqual(r["verdict"], panic_mod.VERDICT_CLEAR)


class ReceiptMirrorTests(unittest.TestCase):
    def test_split_no_pii(self):
        m = mirror_mod.mirror(event_id="e1", job_id="pc:x", decision="HALT", public_url="https://g")
        self.assertTrue(m["split"])
        self.assertFalse(m["public"]["pii"])


class DeadmanEchoTests(unittest.TestCase):
    def test_stale_chokes(self):
        r = deadman_mod.evaluate(last_live_at=time.time() - 9999, soft_continue=True)
        self.assertIn(r["verdict"], (deadman_mod.VERDICT_STALE, deadman_mod.VERDICT_CHOKE))
        self.assertFalse(r["may_proceed"])

    def test_fresh_live(self):
        r = deadman_mod.evaluate(last_live_at=time.time(), soft_continue=True)
        self.assertEqual(r["verdict"], deadman_mod.VERDICT_LIVE)


class WitnessSeatTests(unittest.TestCase):
    def test_witness_cannot_live(self):
        r = witness_mod.evaluate(role="witness", would_live=True)
        self.assertEqual(r["verdict"], witness_mod.VERDICT_FORGED_LIVE)
        self.assertFalse(r["may_live"])


if __name__ == "__main__":
    unittest.main()
