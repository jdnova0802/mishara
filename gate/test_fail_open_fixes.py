"""Regression suite for the three fail-open fixes (Builds #1-#3).

Build #1  x402: payment requirements are server-authoritative — a buyer cannot
          name their own price — and each settled payload is single-use (replay
          rejected).
Build #2  Self-minted/demo receipts are signed but never action a live rail, and a
          live receipt is single-use (one jti, one spend).
Build #3  Card/push rails fail closed with no mandate (decline on no-mandate), the
          daily_cap is a true rolling 24h sum, and every decision is recorded and
          deduped by authorization id (Stripe webhook retries do not double-count).

Run from gate/: python3 -m pytest test_fail_open_fixes.py
"""
from __future__ import annotations

import base64
import json
import os
import tempfile
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from unittest import mock

# Isolate DB + dev env before importing app modules.
os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(
    tempfile.gettempdir(), f"gate-test-fail-open-{uuid.uuid4().hex}.db"
)
os.environ.pop("RENDER_EXTERNAL_URL", None)
os.environ.pop("RENDER_EXTERNAL_HOSTNAME", None)

# Receipt signing keys so prefinality mints verifiable receipts in-process.
try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import (
        Encoding,
        NoEncryption,
        PrivateFormat,
        PublicFormat,
    )

    _priv = Ed25519PrivateKey.generate()
    _priv_bytes = _priv.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    _pub_bytes = _priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    os.environ["GATE_RECEIPT_PRIVATE_KEY"] = base64.b64encode(_priv_bytes).decode("utf-8")
    os.environ["GATE_RECEIPT_PUBLIC_KEY"] = base64.b64encode(_pub_bytes).decode("utf-8")
except Exception:
    pass

import db as gate_db  # noqa: E402
import prefinality as prefinality_mod  # noqa: E402
import rtp_adapter as rtp_mod  # noqa: E402
import x402_challenge as x402_mod  # noqa: E402

PUBLIC_URL = "https://gate.example"


def _iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat()


class X402PriceForgeryTests(unittest.TestCase):
    """Build #1 — the buyer never names the price, and a payload is single-use."""

    @classmethod
    def setUpClass(cls):
        gate_db.init_db()

    def _ed25519_cdp_secret(self) -> str:
        from cryptography.hazmat.primitives import serialization

        key = Ed25519PrivateKey.generate()
        seed = key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
        pub = key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        return base64.b64encode(seed + pub).decode("ascii")

    def _payload(self, *, payto: str, amount: str, asset: str, network: str, nonce: str) -> str:
        payload = {
            "x402Version": 2,
            "accepted": {
                "scheme": "exact",
                "network": network,
                "amount": amount,
                "asset": asset,
                "payTo": payto,
                "maxTimeoutSeconds": 300,
            },
            "payload": {
                "signature": "0x" + "ab" * 65,
                "authorization": {
                    "from": "0x" + "11" * 20,
                    "to": payto,
                    "value": amount,
                    "nonce": nonce,
                },
            },
        }
        return base64.b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")

    def test_buyer_cannot_name_a_lower_price(self):
        """Buyer echoes a cheaper amount than the route price → requirements_mismatch."""
        our = "0x" + "aa" * 20
        secret = self._ed25519_cdp_secret()
        # Server price is 2000 atomic; buyer tries to pay 1.
        forged = self._payload(
            payto=our,
            amount="1",
            asset=x402_mod.USDC_BASE,
            network=x402_mod.NETWORK_BASE,
            nonce="0x" + "01" * 32,
        )
        with mock.patch.dict(
            os.environ,
            {"CDP_API_KEY_ID": "test-key-id", "CDP_API_KEY_SECRET": secret},
        ):
            with mock.patch.object(x402_mod, "payto", return_value=our):
                with mock.patch.dict(os.environ, {"GATE_X402_AMOUNT_ATOMIC": "2000"}):
                    result = x402_mod.payment_verified({"Payment-Signature": forged})
        self.assertFalse(result.get("ok"))
        self.assertFalse(result.get("paid"))
        self.assertEqual(result.get("reason"), "requirements_mismatch")
        self.assertIn("amount", (result.get("mismatch") or {}))

    def test_buyer_cannot_swap_asset_or_network(self):
        our = "0x" + "aa" * 20
        secret = self._ed25519_cdp_secret()
        forged = self._payload(
            payto=our,
            amount="2000",
            asset="0x" + "de" * 20,  # not USDC
            network="eip155:1",  # not Base
            nonce="0x" + "02" * 32,
        )
        with mock.patch.dict(
            os.environ,
            {"CDP_API_KEY_ID": "test-key-id", "CDP_API_KEY_SECRET": secret},
        ):
            with mock.patch.object(x402_mod, "payto", return_value=our):
                with mock.patch.dict(os.environ, {"GATE_X402_AMOUNT_ATOMIC": "2000"}):
                    result = x402_mod.payment_verified({"Payment-Signature": forged})
        self.assertFalse(result.get("ok"))
        self.assertEqual(result.get("reason"), "requirements_mismatch")
        mismatch = result.get("mismatch") or {}
        self.assertIn("asset", mismatch)
        self.assertIn("network", mismatch)

    def test_payment_payload_is_single_use(self):
        """The same settled payload cannot be replayed into a second unlock."""
        our = "0x" + "aa" * 20
        secret = self._ed25519_cdp_secret()
        good = self._payload(
            payto=our,
            amount="2000",
            asset=x402_mod.USDC_BASE,
            network=x402_mod.NETWORK_BASE,
            nonce="0x" + "03" * 32,
        )

        def fake_post(url, headers=None, json=None, timeout=None):  # noqa: A002
            class Resp:
                status_code = 200

                def json(self_inner):
                    if url.rstrip("/").endswith("/verify"):
                        return {"isValid": True, "payer": "0x" + "11" * 20}
                    return {
                        "success": True,
                        "payer": "0x" + "11" * 20,
                        "transaction": "0x" + "ee" * 32,
                        "network": x402_mod.NETWORK_BASE,
                        "amount": "2000",
                    }

            return Resp()

        with mock.patch.dict(
            os.environ,
            {
                "CDP_API_KEY_ID": "test-key-id",
                "CDP_API_KEY_SECRET": secret,
                "GATE_X402_AMOUNT_ATOMIC": "2000",
            },
        ):
            with mock.patch("x402_facilitator.requests.post", side_effect=fake_post):
                with mock.patch.object(x402_mod, "payto", return_value=our):
                    first = x402_mod.payment_verified({"Payment-Signature": good})
                    second = x402_mod.payment_verified({"Payment-Signature": good})

        self.assertTrue(first.get("ok"), first)
        self.assertTrue(first.get("paid"))
        self.assertFalse(second.get("ok"))
        self.assertEqual(second.get("reason"), "payment_replayed")

    def test_reserve_x402_payment_primitive_is_race_safe(self):
        nonce = "nonce_" + uuid.uuid4().hex
        self.assertTrue(gate_db.reserve_x402_payment(nonce=nonce, resource="r", amount="2000"))
        self.assertFalse(gate_db.reserve_x402_payment(nonce=nonce, resource="r", amount="2000"))
        # A reservation that never settles can be released so a genuine retry proceeds.
        gate_db.release_x402_payment(nonce)
        self.assertTrue(gate_db.reserve_x402_payment(nonce=nonce, resource="r", amount="2000"))
        # Once settled, release is a no-op (payment stays claimed forever).
        gate_db.mark_x402_settled(nonce)
        gate_db.release_x402_payment(nonce)
        self.assertFalse(gate_db.reserve_x402_payment(nonce=nonce, resource="r", amount="2000"))


class SelfMintReceiptTests(unittest.TestCase):
    """Build #2 — demo receipts never action a live rail; live receipts are single-use."""

    @classmethod
    def setUpClass(cls):
        gate_db.init_db()

    def _rtp_fixtures(self):
        transfer = {
            "amount": "100.00",
            "currency": "USD",
            "routing_number": "021000021",
            "account_number": "123456789",
            "upstream_id": "po_failopen_1",
        }
        order = {
            "type": "rtp",
            "amount": 10000,
            "currency": "USD",
            "routing_number": "021000021",
            "account_number": "123456789",
            "id": "po_failopen_1",
        }
        return transfer, order

    def test_demo_receipt_refused_by_live_gate(self):
        transfer, order = self._rtp_fixtures()
        demo = prefinality_mod.evaluate(
            {
                "rail": "rtp",
                "transfer": transfer,
                "mandate": {"agent_id": "treasury-bot", "max_amount": "500.00"},
            },
            public_url=PUBLIC_URL,
            demo=True,
        )
        self.assertEqual(demo["decision"], "GO")
        receipt = demo["receipt"]
        # It is a genuine, stranger-verifiable signature...
        verified = prefinality_mod.verify_receipt_jwt(receipt)
        self.assertTrue(verified["valid"])
        self.assertTrue(verified["demo"])
        # ...but the live money rail refuses it.
        gate = rtp_mod.gate_payment_order(receipt_jwt=receipt, payment_order=order)
        self.assertFalse(gate["allow"])
        self.assertEqual(gate["reason"], "demo_receipt_refused")

    def test_live_receipt_is_single_use(self):
        transfer, order = self._rtp_fixtures()
        live = prefinality_mod.evaluate(
            {
                "rail": "rtp",
                "transfer": transfer,
                "mandate": {"agent_id": "treasury-bot", "max_amount": "500.00"},
            },
            public_url=PUBLIC_URL,
            demo=False,
        )
        self.assertEqual(live["decision"], "GO")
        receipt = live["receipt"]
        first = rtp_mod.gate_payment_order(receipt_jwt=receipt, payment_order=order)
        self.assertTrue(first["allow"], first)
        second = rtp_mod.gate_payment_order(receipt_jwt=receipt, payment_order=order)
        self.assertFalse(second["allow"])
        self.assertEqual(second["reason"], "receipt_already_used")

    def test_consume_receipt_primitive(self):
        jti = "pf_" + uuid.uuid4().hex
        self.assertTrue(gate_db.consume_receipt(jti=jti, rail="rtp", fingerprint="fp"))
        self.assertFalse(gate_db.consume_receipt(jti=jti, rail="rtp", fingerprint="fp"))


class NoMandateDeclineTests(unittest.TestCase):
    """Build #3 — card/push rails fail closed when no spend bound is present."""

    @classmethod
    def setUpClass(cls):
        gate_db.init_db()

    def test_issuing_no_mandate_declines(self):
        out = prefinality_mod.evaluate(
            {
                "rail": "issuing",
                "transfer": {"amount": "42.00", "currency": "USD", "counterparty": "Acme"},
                "mandate": {"agent_id": "agent_a"},
            },
            public_url=PUBLIC_URL,
        )
        self.assertEqual(out["decision"], "NO_GO")
        self.assertIn("mandate_required", out["signals"])

    def test_oct_no_mandate_declines(self):
        out = prefinality_mod.evaluate(
            {
                "rail": "oct",
                "transfer": {"amount": "42.00", "currency": "USD", "counterparty": "payer"},
                "mandate": {"agent_id": "agent_a"},
            },
            public_url=PUBLIC_URL,
        )
        self.assertEqual(out["decision"], "NO_GO")
        self.assertIn("mandate_required", out["signals"])

    def test_issuing_daily_cap_only_is_enough_mandate(self):
        # A daily_cap with no per-auth max is a valid bound → not mandate_required.
        out = prefinality_mod.evaluate(
            {
                "rail": "issuing",
                "transfer": {
                    "amount": "10.00",
                    "currency": "USD",
                    "counterparty": "Acme",
                    "upstream_id": "iauth_cap_only",
                },
                "mandate": {"agent_id": "cap_only_agent_" + uuid.uuid4().hex, "daily_cap": "100.00"},
            },
            public_url=PUBLIC_URL,
        )
        self.assertEqual(out["decision"], "GO")
        self.assertNotIn("mandate_required", out["signals"])

    def test_rtp_x402_unaffected_by_mandate_guard(self):
        # The no-mandate guard is scoped to card/push rails; rtp with a cap still clears.
        out = prefinality_mod.evaluate(
            {
                "rail": "rtp",
                "transfer": {
                    "amount": "100.00",
                    "currency": "USD",
                    "routing_number": "021000021",
                    "account_number": "123456789",
                    "upstream_id": "po_mandate_guard",
                },
                "mandate": {"agent_id": "treasury-bot", "max_amount": "500.00"},
            },
            public_url=PUBLIC_URL,
        )
        self.assertEqual(out["decision"], "GO")


class RollingDailyCapTests(unittest.TestCase):
    """Build #3 — daily_cap is a true rolling 24h sum, not a per-transaction limit."""

    @classmethod
    def setUpClass(cls):
        gate_db.init_db()

    def test_cumulative_spend_trips_daily_cap(self):
        agent = "rolling_agent_" + uuid.uuid4().hex
        mandate = {"agent_id": agent, "max_amount": "100.00", "daily_cap": "150.00"}

        def one(amount: str, auth: str):
            return prefinality_mod.evaluate(
                {
                    "rail": "issuing",
                    "transfer": {
                        "amount": amount,
                        "currency": "USD",
                        "counterparty": "Acme",
                        "authorization_id": auth,
                    },
                    "mandate": mandate,
                },
                public_url=PUBLIC_URL,
            )

        # Each is under the per-auth cap (100), but they sum past the 150 daily cap.
        first = one("80.00", "iauth_1")
        self.assertEqual(first["decision"], "GO")
        second = one("60.00", "iauth_2")  # 80 + 60 = 140, still under 150
        self.assertEqual(second["decision"], "GO")
        third = one("30.00", "iauth_3")  # 140 + 30 = 170 > 150
        self.assertEqual(third["decision"], "NO_GO")
        self.assertIn("daily_cap_exceeded", third["signals"])

    def test_approved_amount_window_excludes_authorization(self):
        agent = "window_agent_" + uuid.uuid4().hex
        since = _iso(datetime.now(timezone.utc) - timedelta(hours=24))
        gate_db.record_prefinality_evaluation(
            evaluation_id="pf_" + uuid.uuid4().hex,
            account_id=None,
            rail="issuing",
            decision="GO",
            fingerprint="fp1",
            agent_id=agent,
            signals=[],
            receipt_jwt=None,
            created_at=_iso(datetime.now(timezone.utc)),
            amount=40.0,
            authorization_id="iauth_x",
        )
        total = gate_db.approved_amount_in_window(agent_id=agent, rail="issuing", since=since)
        self.assertEqual(total, 40.0)
        # Excluding the same authorization (Stripe retry) recomputes the window sans it.
        excluded = gate_db.approved_amount_in_window(
            agent_id=agent, rail="issuing", since=since, exclude_authorization_id="iauth_x"
        )
        self.assertEqual(excluded, 0.0)


class WebhookDedupeTests(unittest.TestCase):
    """Build #3 — a Stripe retry of the same authorization does not double-count."""

    @classmethod
    def setUpClass(cls):
        gate_db.init_db()

    def test_duplicate_authorization_id_recorded_once(self):
        agent = "dedupe_agent_" + uuid.uuid4().hex
        auth = "iauth_dup_" + uuid.uuid4().hex
        since = _iso(datetime.now(timezone.utc) - timedelta(hours=24))

        def record():
            gate_db.record_prefinality_evaluation(
                evaluation_id="pf_" + uuid.uuid4().hex,
                account_id=None,
                rail="issuing",
                decision="GO",
                fingerprint="fp",
                agent_id=agent,
                signals=[],
                receipt_jwt=None,
                created_at=_iso(datetime.now(timezone.utc)),
                amount=25.0,
                authorization_id=auth,
            )

        record()
        record()  # Stripe retry of the same authorization.
        record()

        # Only one row survived (unique index on authorization_id)...
        total = gate_db.approved_amount_in_window(agent_id=agent, rail="issuing", since=since)
        self.assertEqual(total, 25.0)

    def test_null_authorization_ids_do_not_collide(self):
        # Many decisions with no authorization id must still all be recorded.
        agent = "null_auth_agent_" + uuid.uuid4().hex
        since = _iso(datetime.now(timezone.utc) - timedelta(hours=24))
        for _ in range(3):
            gate_db.record_prefinality_evaluation(
                evaluation_id="pf_" + uuid.uuid4().hex,
                account_id=None,
                rail="issuing",
                decision="GO",
                fingerprint="fp",
                agent_id=agent,
                signals=[],
                receipt_jwt=None,
                created_at=_iso(datetime.now(timezone.utc)),
                amount=10.0,
                authorization_id=None,
            )
        total = gate_db.approved_amount_in_window(agent_id=agent, rail="issuing", since=since)
        self.assertEqual(total, 30.0)


if __name__ == "__main__":
    unittest.main()
