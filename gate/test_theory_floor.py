"""Theory-floor hardening — claim_scope, witness cosign, IN_FLIGHT write_state."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-theory-floor.db")

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption, PublicFormat

    _priv = Ed25519PrivateKey.generate()
    _priv_bytes = _priv.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    _pub_bytes = _priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    os.environ["GATE_RECEIPT_PRIVATE_KEY"] = base64.b64encode(_priv_bytes).decode("utf-8")
    os.environ["GATE_RECEIPT_PUBLIC_KEY"] = base64.b64encode(_pub_bytes).decode("utf-8")

    _wpriv = Ed25519PrivateKey.generate()
    _wpriv_bytes = _wpriv.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    _wpub_bytes = _wpriv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    os.environ["GATE_WITNESS_PRIVATE_KEY"] = base64.b64encode(_wpriv_bytes).decode("utf-8")
    os.environ["GATE_WITNESS_PUBLIC_KEY"] = base64.b64encode(_wpub_bytes).decode("utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import claim_scope  # noqa: E402
import clear_ui  # noqa: E402
import db  # noqa: E402
import deny_registry  # noqa: E402
import evidence_log  # noqa: E402
import exclusion  # noqa: E402
import mouths  # noqa: E402
import never_ui  # noqa: E402
import prefinality  # noqa: E402
import write_state  # noqa: E402


class ClaimScopeNeverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.init_db()

    def test_never_absent_has_signed_claim_scope(self):
        out = never_ui.clear_job("job-never-scope-absent")
        self.assertEqual(out["word"], "NEVER")
        self.assertIn("claim_scope", out)
        scope = out["claim_scope"]
        self.assertEqual(scope["spec"], "gate-claim-scope-v1")
        self.assertEqual(scope["boundary"], "gate_redeemed_ticket_spend_map")
        self.assertTrue(scope["not_global"])
        self.assertIn("bind_tickets.consumed_at", scope["logs"])
        self.assertIn("signed_claim", out)
        sc = out["signed_claim"]
        self.assertTrue(sc.get("claim_hash"))
        self.assertTrue(sc.get("claim_signature"))
        self.assertEqual(sc["canonical_claim"]["claim_scope"]["boundary"], scope["boundary"])
        self.assertEqual(out["spend_phase"], "ABSENT")

    def test_never_in_flight_distinct_from_absent(self):
        jid = "job-never-inflight-1"
        now = datetime.now(timezone.utc)
        tid = "ticket-inflight-1"
        db.insert_bind_ticket(
            ticket_id=tid,
            job_id=jid,
            fuse_id="fuse_t",
            event_id="evt_t",
            receipt_hash=None,
            token_hash="abc",
            not_before=now.isoformat(),
            not_after=(now + timedelta(seconds=60)).isoformat(),
        )
        out = never_ui.clear_job(jid)
        self.assertEqual(out["word"], "NEVER")
        self.assertEqual(out["spend_phase"], "IN_FLIGHT")
        self.assertTrue(out["in_flight"])
        self.assertIn("IN_FLIGHT", out["plain"])
        self.assertEqual(out["write_state"]["phase"], "IN_FLIGHT")
        self.assertTrue(out["write_state"]["cancellable"])


class ClaimScopeClearSealGoMouthTests(unittest.TestCase):
    def test_clear_deny_signed_scope(self):
        h = deny_registry.payout_fingerprint(
            rail="ach",
            amount="10.00",
            currency="USD",
            destination="acct_test_scope",
        )
        deny_registry.register_deny(payout_hash=h, reason_code="test_deny", rail="ach")
        out = clear_ui.clear_deny(h)
        self.assertEqual(out["word"], "DENIED")
        self.assertEqual(out["claim_scope"]["boundary"], "gate_deny_registry")
        self.assertTrue(out["signed_claim"]["claim_signature"])

    def test_clear_not_denied_still_scoped(self):
        h = "a" * 64
        out = clear_ui.clear_deny(h)
        self.assertEqual(out["word"], "NOT DENIED")
        self.assertIn("deny_entries", out["claim_scope"]["logs"][0])
        self.assertTrue(out["signed_claim"]["claim_hash"])

    def test_clear_rail_surfaces_window_not_binary(self):
        out = clear_ui.clear_rail("ach")
        self.assertIsNotNone(out)
        self.assertEqual(out["write_state"]["phase"], "IN_FLIGHT")
        self.assertTrue(out["write_state"]["detail"]["already_handled"])

    def test_go_nogo_scope_inside_jwt(self):
        raw = prefinality.evaluate(
            {
                "rail": "issuing",
                "transfer": {"amount": "9999.00", "currency": "USD", "counterparty": "X"},
                "mandate": {"max_amount": "10.00", "expected_counterparty": "X"},
            },
            public_url="https://gate.example",
        )
        self.assertEqual(raw["decision"], "NO_GO")
        self.assertIn("claim_scope", raw)
        self.assertEqual(raw["claim_scope"]["boundary"], "gate_prefinality_evaluate")
        self.assertEqual(raw["write_state"]["phase"], "CLEARANCE")
        token = raw["receipt"]
        self.assertTrue(token)
        verified = prefinality.verify_receipt_jwt(token, expected_fingerprint=raw["fingerprint"])
        self.assertTrue(verified["valid"])
        self.assertIn("scope", verified["payload"])
        self.assertEqual(
            verified["payload"]["scope"]["boundary"],
            "gate_prefinality_evaluate",
        )

    def test_fednow_never_signed_scope(self):
        out = mouths.evaluate(
            "fednow-prepush",
            {
                "rail": "fednow",
                "payee_sealed": "no",
                "first_time_payee": "no",
                "fraud_suspected": "no",
            },
        )
        self.assertEqual(out["word"], "NEVER")
        self.assertEqual(out["claim_scope"]["keys_checked"]["mouth_id"], "fednow-prepush")
        self.assertTrue(out["signed_claim"]["claim_signature"])
        self.assertEqual(out["write_state"]["phase"], "N_A")

    def test_positive_clear_no_signed_scope(self):
        out = mouths.evaluate(
            "positive-clear",
            {"kind": "payroll", "authority_live": "no"},
        )
        self.assertEqual(out["word"], "NO")
        self.assertIn("claim_scope", out)
        self.assertTrue(out["signed_claim"]["claim_hash"])

    def test_scenario3_does_not_match_scoped(self):
        out = mouths.evaluate(
            "scenario-3",
            {"known_supplier": True, "email_only": False, "new_account": False, "name_mismatch": False},
        )
        self.assertEqual(out["word"], "DOES NOT MATCH")
        self.assertTrue(out["signed_claim"]["claim_signature"])

    def test_nacha_and_cl7_never_scoped(self):
        nacha = mouths.evaluate(
            "nacha-false-pretenses",
            {
                "role": "odfi",
                "false_pretenses_suspected": "yes",
                "who_what_payee_sealed": "no",
            },
        )
        self.assertEqual(nacha["word"], "NEVER")
        self.assertTrue(nacha["signed_claim"]["claim_signature"])
        cl7 = mouths.evaluate(
            "cl7-handoff",
            {"ais_ecdis_handoff": "yes", "written_notice_15d": "no"},
        )
        self.assertEqual(cl7["word"], "NEVER")
        self.assertTrue(cl7["signed_claim"]["claim_signature"])


class WitnessCosignTests(unittest.TestCase):
    def test_tree_head_has_witness_block(self):
        leaves = [hashlib.sha256(b"a").hexdigest(), hashlib.sha256(b"b").hexdigest()]
        head = evidence_log.signed_tree_head(leaves)
        self.assertIn("witness", head)
        w = head["witness"]
        self.assertEqual(w["spec"], "gate-evidence-witness-v1")
        self.assertTrue(w["configured"])
        self.assertTrue(w["signed"])
        self.assertTrue(w["distinct_from_gate_key"])
        self.assertTrue(w["signature"])
        self.assertTrue(
            evidence_log.verify_witness_signature(
                head_hash=head["head_hash"],
                signature_b64=w["signature"],
            )
        )
        # Gate primary signature still present.
        self.assertTrue(head["head_signature"])

    def test_witness_absent_still_exposes_capacity(self):
        saved = {
            "priv": os.environ.pop("GATE_WITNESS_PRIVATE_KEY", None),
            "pub": os.environ.pop("GATE_WITNESS_PUBLIC_KEY", None),
        }
        try:
            head = evidence_log.signed_tree_head([hashlib.sha256(b"c").hexdigest()])
            w = head["witness"]
            self.assertFalse(w["configured"])
            self.assertFalse(w["signed"])
            self.assertIsNone(w["signature"])
            self.assertFalse(w["required"])
        finally:
            if saved["priv"]:
                os.environ["GATE_WITNESS_PRIVATE_KEY"] = saved["priv"]
            if saved["pub"]:
                os.environ["GATE_WITNESS_PUBLIC_KEY"] = saved["pub"]


class WriteStateUnitTests(unittest.TestCase):
    def test_phases(self):
        self.assertEqual(write_state.for_spend_map(spent=True, in_flight=False)["phase"], "SPENT")
        self.assertEqual(write_state.for_spend_map(spent=False, in_flight=True)["phase"], "IN_FLIGHT")
        self.assertEqual(write_state.for_spend_map(spent=False, in_flight=False)["phase"], "ABSENT")
        self.assertEqual(write_state.for_clearance_mouth(decision="NO_GO", rail="issuing")["phase"], "CLEARANCE")


if __name__ == "__main__":
    unittest.main()
