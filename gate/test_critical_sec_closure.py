"""Regression suite for the second security-closure batch (#4 SSRF, #5 auth) + demo-key separation.

#4  x402 audit SSRF guard: block private/loopback/link-local/reserved targets,
    reject embedded credentials, never follow redirects, rate limit.
#5  Auth/scoping: X-Forwarded-For client IP cannot be spoofed to mint fresh rate
    buckets; license kill-switch/charge are scoped to the owning account; the
    inbound OCT webhook and deny-registry writes require auth.
Demo key: demo receipts are signed by a separate key the live rails do not trust,
    so a demo receipt is refused even if its demo=true flag is stripped.

Run from gate/: python3 -m pytest test_critical_sec_closure.py
"""
from __future__ import annotations

import base64
import json
import os
import tempfile
import time
import unittest
import uuid
from datetime import datetime, timezone
from unittest import mock

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(
    tempfile.gettempdir(), f"gate-test-critsec-{uuid.uuid4().hex}.db"
)
os.environ.pop("RENDER_EXTERNAL_URL", None)
os.environ.pop("RENDER_EXTERNAL_HOSTNAME", None)

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import (
        Encoding,
        NoEncryption,
        PrivateFormat,
        PublicFormat,
    )

    def _gen_keypair() -> tuple[str, str]:
        k = Ed25519PrivateKey.generate()
        priv = k.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
        pub = k.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        return base64.b64encode(priv).decode(), base64.b64encode(pub).decode()

    _PRIV, _PUB = _gen_keypair()
    os.environ["GATE_RECEIPT_PRIVATE_KEY"] = _PRIV
    os.environ["GATE_RECEIPT_PUBLIC_KEY"] = _PUB
except Exception:  # pragma: no cover
    def _gen_keypair():
        return "", ""

import demo_limit  # noqa: E402
import license_fuse as license_fuse_mod  # noqa: E402
import prefinality as prefinality_mod  # noqa: E402
import receipt as receipt_mod  # noqa: E402
import rtp_adapter as rtp_mod  # noqa: E402
import x402_audit as x402_audit_mod  # noqa: E402

PUBLIC_URL = "https://gate.example"


class FakeReq:
    def __init__(self, xff=None, remote="9.9.9.9"):
        self.headers = {} if xff is None else {"X-Forwarded-For": xff}
        self.remote_addr = remote


# ----------------------------------------------------------------------------- #
# #4 — SSRF guard
# ----------------------------------------------------------------------------- #
class SsrfGuardTests(unittest.TestCase):
    def setUp(self):
        self._env = mock.patch.dict(os.environ, {"GATE_ALLOW_LOCAL": "0"}, clear=False)
        self._env.start()

    def tearDown(self):
        self._env.stop()

    def _assert_blocked(self, url):
        out = x402_audit_mod.audit_endpoint(url)
        self.assertFalse(out.get("ok"))
        self.assertEqual(out.get("error"), "blocked_target", out)
        codes = {f.get("code") for f in out.get("findings", [])}
        self.assertIn("ssrf_blocked", codes)

    def test_blocks_cloud_metadata(self):
        self._assert_blocked("http://169.254.169.254/latest/meta-data/")

    def test_blocks_loopback(self):
        self._assert_blocked("http://127.0.0.1/health")
        self._assert_blocked("http://[::1]/health")

    def test_blocks_private_ranges(self):
        for u in ("http://10.0.0.5/x", "http://192.168.1.1/x", "http://172.16.9.9/x"):
            self._assert_blocked(u)

    def test_blocks_localhost_hostname(self):
        self._assert_blocked("http://localhost/v1/prefinality/evaluate")

    def test_rejects_embedded_credentials(self):
        out = x402_audit_mod.audit_endpoint("http://user:pass@169.254.169.254/")
        self.assertFalse(out.get("ok"))
        self.assertEqual(out.get("error"), "invalid_url")

    def test_allow_local_flag_permits_probe(self):
        with mock.patch.dict(os.environ, {"GATE_ALLOW_LOCAL": "1"}, clear=False):
            out = x402_audit_mod.audit_endpoint("http://127.0.0.1:9/x")
        # Not blocked by SSRF guard; the probe itself fails (nothing listening).
        self.assertNotEqual(out.get("error"), "blocked_target")

    def test_redirects_are_not_followed(self):
        class Resp:
            status_code = 302
            headers = {"Location": "http://169.254.169.254/", "Content-Type": "text/plain"}

            def json(self):
                raise json.JSONDecodeError("x", "", 0)

        with mock.patch.dict(os.environ, {"GATE_ALLOW_LOCAL": "1"}, clear=False):
            with mock.patch.object(x402_audit_mod, "requests") as rq:
                rq.get.return_value = Resp()
                rq.post.return_value = Resp()
                rq.RequestException = Exception
                out = x402_audit_mod.audit_endpoint("http://127.0.0.1/x")
        codes = {f.get("code") for f in out.get("findings", [])}
        self.assertIn("redirect_not_followed", codes)
        self.assertFalse(out.get("ok"))


class AuditRateLimitTests(unittest.TestCase):
    def test_audit_limiter_trips_after_cap(self):
        demo_limit._audit_hits.clear()
        req = FakeReq(remote="203.0.113.7")
        with mock.patch.object(demo_limit, "AUDIT_LIMIT", 3):
            results = [demo_limit.allow_audit(req)[0] for _ in range(5)]
        self.assertEqual(results, [True, True, True, False, False])


# ----------------------------------------------------------------------------- #
# #5 — spoof-resistant client IP
# ----------------------------------------------------------------------------- #
class ClientIpTests(unittest.TestCase):
    def test_takes_rightmost_trusted_hop_not_spoofed_leftmost(self):
        with mock.patch.object(demo_limit, "TRUSTED_PROXY_HOPS", 1):
            ip = demo_limit._client_ip(FakeReq(xff="1.2.3.4, 5.6.7.8"))
        self.assertEqual(ip, "5.6.7.8")

    def test_spoofed_leftmost_cannot_mint_fresh_rate_buckets(self):
        demo_limit._hits.clear()
        with mock.patch.object(demo_limit, "TRUSTED_PROXY_HOPS", 1):
            with mock.patch.object(demo_limit, "DEMO_LIMIT", 2):
                # Attacker varies the leftmost (spoofed) IP each call; the real edge
                # IP is the rightmost and constant, so the bucket does not reset.
                allowed = []
                for i in range(4):
                    req = FakeReq(xff=f"10.0.0.{i}, 5.6.7.8")
                    allowed.append(demo_limit.allow_demo(req)[0])
        self.assertEqual(allowed, [True, True, False, False])

    def test_falls_back_to_remote_addr_when_no_xff(self):
        self.assertEqual(demo_limit._client_ip(FakeReq(remote="8.8.8.8")), "8.8.8.8")

    def test_ignores_garbage_xff(self):
        with mock.patch.object(demo_limit, "TRUSTED_PROXY_HOPS", 1):
            ip = demo_limit._client_ip(FakeReq(xff="not-an-ip", remote="8.8.8.8"))
        self.assertEqual(ip, "8.8.8.8")


# ----------------------------------------------------------------------------- #
# #5 — license kill-switch scoped to owner
# ----------------------------------------------------------------------------- #
class LicenseOwnershipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import db as gate_db

        gate_db.init_db()

    def _charge(self, lid, account_id):
        return license_fuse_mod.charge(
            license_id=lid,
            charge_id=f"chg_{uuid.uuid4().hex[:12]}",
            account_id=account_id,
        )

    def test_demo_cannot_kill_owned_license(self):
        lid = f"lic:OWNED-{uuid.uuid4().hex[:8]}"
        self.assertEqual(self._charge(lid, "acct_A").get("state"), "LIVE")
        # Demo / anonymous caller (account_id=None) must be refused.
        blocked = license_fuse_mod.dead(license_id=lid, account_id=None)
        self.assertFalse(blocked.get("ok"))
        self.assertEqual(blocked.get("reason"), "license_not_owned")
        # Still LIVE.
        self.assertEqual(license_fuse_mod.snapshot(lid).get("stored"), "LIVE")

    def test_other_account_cannot_kill(self):
        lid = f"lic:OWNED2-{uuid.uuid4().hex[:8]}"
        self._charge(lid, "acct_A")
        blocked = license_fuse_mod.dead(license_id=lid, account_id="acct_B")
        self.assertFalse(blocked.get("ok"))
        self.assertEqual(blocked.get("reason"), "license_not_owned")

    def test_owner_can_kill(self):
        lid = f"lic:OWNED3-{uuid.uuid4().hex[:8]}"
        self._charge(lid, "acct_A")
        ok = license_fuse_mod.dead(license_id=lid, account_id="acct_A")
        self.assertTrue(ok.get("ok"))
        self.assertEqual(ok.get("state"), "DEAD")

    def test_unowned_license_killable_by_demo(self):
        lid = f"lic:UNOWNED-{uuid.uuid4().hex[:8]}"
        self._charge(lid, None)  # demo charge → no owner bound
        ok = license_fuse_mod.dead(license_id=lid, account_id=None)
        self.assertTrue(ok.get("ok"))
        self.assertEqual(ok.get("state"), "DEAD")

    def test_other_account_cannot_recharge(self):
        lid = f"lic:OWNED4-{uuid.uuid4().hex[:8]}"
        self._charge(lid, "acct_A")
        license_fuse_mod.dead(license_id=lid, account_id="acct_A")
        blocked = self._charge(lid, "acct_B")
        self.assertFalse(blocked.get("ok"))
        self.assertEqual(blocked.get("reason"), "license_not_owned")


# ----------------------------------------------------------------------------- #
# Demo signing-key separation
# ----------------------------------------------------------------------------- #
class DemoKeySeparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import db as gate_db

        gate_db.init_db()
        cls._demo_priv, cls._demo_pub = _gen_keypair()

    def _with_demo_key(self):
        return mock.patch.dict(
            os.environ,
            {
                "GATE_RECEIPT_DEMO_PRIVATE_KEY": self._demo_priv,
                "GATE_RECEIPT_DEMO_PUBLIC_KEY": self._demo_pub,
            },
            clear=False,
        )

    def _rtp(self):
        transfer = {
            "amount": "100.00",
            "currency": "USD",
            "routing_number": "021000021",
            "account_number": "123456789",
        }
        order = {
            "type": "rtp",
            "amount": 10000,
            "currency": "USD",
            "routing_number": "021000021",
            "account_number": "123456789",
        }
        return transfer, order

    def test_demo_receipt_signed_by_demo_key(self):
        transfer, _ = self._rtp()
        with self._with_demo_key():
            out = prefinality_mod.evaluate(
                {"rail": "rtp", "transfer": transfer, "mandate": {"agent_id": "a", "max_amount": "500"}},
                public_url=PUBLIC_URL,
                demo=True,
            )
            verified = prefinality_mod.verify_receipt_jwt(out["receipt"])
        self.assertTrue(verified["valid"])
        self.assertEqual(verified["key_class"], "demo")
        self.assertTrue(verified["demo"])

    def test_live_receipt_signed_by_prod_key(self):
        transfer, _ = self._rtp()
        with self._with_demo_key():
            out = prefinality_mod.evaluate(
                {"rail": "rtp", "transfer": transfer, "mandate": {"agent_id": "a", "max_amount": "500"}},
                public_url=PUBLIC_URL,
                demo=False,
            )
            verified = prefinality_mod.verify_receipt_jwt(out["receipt"])
        self.assertEqual(verified["key_class"], "prod")
        self.assertFalse(verified["demo"])

    def test_demo_key_receipt_refused_even_without_flag(self):
        # White-box: build a GO receipt signed by the demo key but WITHOUT the
        # demo=true flag; it must still verify as demo (key_class) and be refused.
        transfer, order = self._rtp()
        fp = prefinality_mod.transfer_fingerprint(rail="rtp", transfer=transfer)
        with self._with_demo_key():
            key = prefinality_mod._signing_key(demo=True)
            now = int(datetime.now(timezone.utc).timestamp())
            payload = {
                "spec": prefinality_mod.SPEC,
                "jti": f"pf_{uuid.uuid4().hex}",
                "iss": "gate.example",
                "sub": "a",
                "iat": now,
                "exp": now + 300,
                "rail": "rtp",
                "dec": "GO",
                "fp": fp,
                "sig": [],
                # deliberately NO "demo" flag
            }
            header = {"alg": "EdDSA", "typ": "JWT", "kid": prefinality_mod.key_id(demo=True)}
            hb = prefinality_mod._b64url(prefinality_mod._canonical_json(header).encode())
            pb = prefinality_mod._b64url(prefinality_mod._canonical_json(payload).encode())
            signature = key.sign(f"{hb}.{pb}".encode())
            token = f"{hb}.{pb}.{prefinality_mod._b64url(signature)}"

            verified = prefinality_mod.verify_receipt_jwt(token, expected_fingerprint=fp)
            self.assertTrue(verified["valid"])
            self.assertEqual(verified["key_class"], "demo")
            self.assertTrue(verified["demo"], "demo-key receipt must read as demo even with no flag")

            gate = rtp_mod.gate_payment_order(receipt_jwt=token, payment_order=order)
        self.assertFalse(gate["allow"])
        self.assertEqual(gate["reason"], "demo_receipt_refused")

    def test_jwks_publishes_both_keys_when_demo_configured(self):
        with self._with_demo_key():
            ks = prefinality_mod.jwks()["keys"]
        classes = {k.get("gate_key_class", "prod") for k in ks}
        self.assertIn("prod", classes)
        self.assertIn("demo", classes)

    def test_without_demo_key_falls_back_to_prod(self):
        # No demo key provisioned → demo receipts still mint (signed by prod key) and
        # remain refused by the live gate via the demo=true flag.
        transfer, order = self._rtp()
        env = {k: os.environ.get(k) for k in ("GATE_RECEIPT_DEMO_PRIVATE_KEY", "GATE_RECEIPT_DEMO_PUBLIC_KEY")}
        for k in env:
            os.environ.pop(k, None)
        try:
            out = prefinality_mod.evaluate(
                {"rail": "rtp", "transfer": transfer, "mandate": {"agent_id": "a", "max_amount": "500"}},
                public_url=PUBLIC_URL,
                demo=True,
            )
            verified = prefinality_mod.verify_receipt_jwt(out["receipt"])
            self.assertEqual(verified["key_class"], "prod")
            self.assertTrue(verified["demo"])  # via payload flag
            gate = rtp_mod.gate_payment_order(receipt_jwt=out["receipt"], payment_order=order)
            self.assertFalse(gate["allow"])
            self.assertEqual(gate["reason"], "demo_receipt_refused")
        finally:
            for k, v in env.items():
                if v is not None:
                    os.environ[k] = v


# ----------------------------------------------------------------------------- #
# #5 — endpoint auth (sink/oct webhook, deny-registry write)
# ----------------------------------------------------------------------------- #
class EndpointAuthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import app as gate_app

        cls.gate_app = gate_app
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_sink_oct_open_in_dev(self):
        # Dev mode (module default) with no secret → allowed (existing behavior).
        with mock.patch.object(self.gate_app, "GATE_DEV_MODE", True):
            with mock.patch.dict(os.environ, {"GATE_SINK_WEBHOOK_SECRET": ""}, clear=False):
                r = self.client.post("/v1/sink/oct", json={"amount": 100})
        self.assertNotEqual(r.status_code, 401)

    def test_sink_oct_requires_secret_in_prod(self):
        with mock.patch.object(self.gate_app, "GATE_DEV_MODE", False):
            with mock.patch.dict(os.environ, {"GATE_SINK_WEBHOOK_SECRET": ""}, clear=False):
                r = self.client.post("/v1/sink/oct", json={"amount": 100})
        self.assertEqual(r.status_code, 401)
        self.assertEqual(r.get_json()["error"]["code"], "sink_auth_required")

    def test_sink_oct_accepts_correct_secret_in_prod(self):
        with mock.patch.object(self.gate_app, "GATE_DEV_MODE", False):
            with mock.patch.dict(os.environ, {"GATE_SINK_WEBHOOK_SECRET": "s3cret"}, clear=False):
                bad = self.client.post("/v1/sink/oct", json={"amount": 100}, headers={"X-Sink-Token": "wrong"})
                good = self.client.post("/v1/sink/oct", json={"amount": 100}, headers={"X-Sink-Token": "s3cret"})
        self.assertEqual(bad.status_code, 401)
        self.assertIn(good.status_code, (200, 403))  # authorized → real decision

    def test_deny_registry_write_requires_auth_in_prod(self):
        payout_hash = "a" * 64
        with mock.patch.object(self.gate_app, "GATE_DEV_MODE", False):
            with mock.patch.object(self.gate_app, "OPS_TOKEN", ""):
                r = self.client.post(
                    "/v1/deny-registry",
                    json={"payout_hash": payout_hash, "reason_code": "x", "rail": "ach"},
                )
        self.assertEqual(r.status_code, 401)
        self.assertEqual(r.get_json()["error"]["code"], "auth_required")

    def test_deny_registry_write_allows_ops_token_in_prod(self):
        payout_hash = "b" * 64
        with mock.patch.object(self.gate_app, "GATE_DEV_MODE", False):
            with mock.patch.object(self.gate_app, "OPS_TOKEN", "ops-xyz"):
                r = self.client.post(
                    "/v1/deny-registry",
                    json={"payout_hash": payout_hash, "reason_code": "x", "rail": "ach"},
                    headers={"X-Ops-Token": "ops-xyz"},
                )
        self.assertEqual(r.status_code, 201)

    def test_deny_registry_lookup_stays_public(self):
        with mock.patch.object(self.gate_app, "GATE_DEV_MODE", False):
            with mock.patch.object(self.gate_app, "OPS_TOKEN", ""):
                r = self.client.get("/v1/deny-registry/" + ("c" * 64))
        self.assertEqual(r.status_code, 200)


if __name__ == "__main__":
    unittest.main()
