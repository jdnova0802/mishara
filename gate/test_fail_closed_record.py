"""Locks the fail-closed cases already posted on /record.

(a) A forged Payment-Signature or X-Payment header never unlocks the paid route.
(b) Two tickets for one job_id cannot both redeem, including when they race.
(c) Timeout or an unreachable upstream is HALT, never ALLOW, on every mouth that
    can allow a bind: bind-check, PolicyCenter pre-bind, Duck Creek pre-bind,
    and the welded act. The evidence witness, which does not call the network,
    stays unsigned when its key is missing or signing throws.

There is no QUSFI fetch in this process. Nothing here can ALLOW because that
list timed out. A check that does not exist cannot fail open.

Run from gate/: python3 test_fail_closed_record.py
"""
from __future__ import annotations

import base64
import os
import sys
import tempfile
import threading
import unittest
import uuid
from datetime import datetime, timezone
from unittest import mock

import requests

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(
    tempfile.gettempdir(), f"gate-test-fail-closed-{uuid.uuid4().hex}.db"
)
os.environ.pop("RENDER_EXTERNAL_URL", None)
os.environ.pop("RENDER_EXTERNAL_HOSTNAME", None)

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat

    _priv = Ed25519PrivateKey.generate()
    os.environ["GATE_RECEIPT_PRIVATE_KEY"] = base64.b64encode(
        _priv.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    ).decode("utf-8")
    os.environ["GATE_RECEIPT_PUBLIC_KEY"] = base64.b64encode(
        _priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    ).decode("utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as gate_app  # noqa: E402
import db as gate_db  # noqa: E402
import evidence_log  # noqa: E402
import ticket as ticket_mod  # noqa: E402
import spend_protocol  # noqa: E402


def _not_allow(body: dict) -> None:
    if not isinstance(body, dict):
        raise AssertionError(body)
    if body.get("decision") == "ALLOW":
        raise AssertionError(body)
    if body.get("allow_bind") is True:
        raise AssertionError(body)
    if body.get("clearance_allows") is True:
        raise AssertionError(body)
    if (body.get("x402") or {}).get("paid") is True:
        raise AssertionError(body)


class ForgedPaymentHeaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gate_db.init_db()
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def _post(self, headers: dict):
        payto = "0x" + "ab" * 20
        with mock.patch.object(gate_app.x402_challenge_mod, "payto", return_value=payto):
            with mock.patch.object(gate_app.x402_challenge_mod, "payto_configured", return_value=True):
                return self.client.post(
                    "/v1/prefinality/evaluate",
                    json={
                        "rail": "x402",
                        "transfer": {
                            "amount": "0.002",
                            "currency": "USDC",
                            "counterparty": payto,
                        },
                        "mandate": {"agent_id": "rt", "max_amount": "1.00"},
                    },
                    headers=headers,
                )

    def test_forged_payment_signature_stays_402(self):
        response = self._post({"Payment-Signature": "not-a-real-payment"})
        self.assertEqual(response.status_code, 402)
        body = response.get_json() or {}
        _not_allow(body)
        self.assertNotEqual(response.status_code, 200)

    def test_forged_x_payment_stays_402(self):
        response = self._post({"X-Payment": "not-a-real-payment"})
        self.assertEqual(response.status_code, 402)
        _not_allow(response.get_json() or {})


class SpendMapRaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gate_db.init_db()

    def _pair(self):
        job_id = f"rt:job-{uuid.uuid4().hex[:10]}"
        write = spend_protocol.write(job_id=job_id)
        issued = []
        for _ in range(2):
            issued.append(
                ticket_mod.issue(
                    job_id=job_id,
                    fuse_id="fuse_velaru_drill",
                    event_id=str(uuid.uuid4()),
                    receipt_hash=None,
                    redeem_url="https://example.test/redeem",
                    spend_write=write,
                )
            )
        return job_id, write, issued

    def _redeem(self, job_id, write, issued, now):
        return ticket_mod.redeem(
            ticket_id=issued["bearer"]["ticket_id"],
            token=issued["bearer"]["token"],
            job_id=job_id,
            method=write["method"],
            path=write["path"],
            spend_fingerprint=issued["bearer"]["spend_fingerprint"],
            now=now,
        )

    def test_second_ticket_same_job_cannot_allow_bind(self):
        job_id, write, issued = self._pair()
        now = datetime.now(timezone.utc).isoformat()
        first = self._redeem(job_id, write, issued[0], now)
        second = self._redeem(job_id, write, issued[1], now)
        self.assertTrue(first.get("ok"))
        self.assertTrue(first.get("allow_bind"))
        self.assertFalse(second.get("ok"))
        self.assertFalse(second.get("allow_bind"))
        self.assertEqual(second.get("reason"), "job_already_spent")

    def test_concurrent_redeem_allows_one(self):
        job_id, write, issued = self._pair()
        now = datetime.now(timezone.utc).isoformat()
        barrier = threading.Barrier(2)
        results: list[dict] = []

        def go(one):
            barrier.wait(timeout=5)
            results.append(self._redeem(job_id, write, one, now))

        threads = [threading.Thread(target=go, args=(one,)) for one in issued]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
        self.assertEqual(len(results), 2)
        allowed = [row for row in results if row.get("ok") and row.get("allow_bind")]
        denied = [row for row in results if not row.get("allow_bind")]
        self.assertEqual(len(allowed), 1)
        self.assertEqual(len(denied), 1)
        self.assertFalse(denied[0].get("ok"))
        self.assertEqual(denied[0].get("reason"), "job_already_spent")


class UpstreamHaltTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gate_db.init_db()
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_velaru_fuse_timeout_and_unreachable_halt(self):
        for exc in (requests.Timeout("slow"), requests.ConnectionError("down")):
            with mock.patch.object(gate_app.requests, "request", side_effect=exc):
                data, status, headers = gate_app.velaru_fuse(
                    "POST", "/pas/v1/bind-check/demo", fuse_id="fuse_velaru_drill"
                )
            self.assertEqual(status, 503)
            self.assertEqual(headers.get("X-Gate-Halt"), "1")
            self.assertTrue(data.get("halt"))
            self.assertTrue(data.get("fail_closed"))
            self.assertFalse(data.get("verdict"))
            _not_allow(data)

    def test_upstream_500_halts(self):
        class Response:
            status_code = 500

            def json(self):
                return {"verdict": True}

        with mock.patch.object(gate_app.requests, "request", return_value=Response()):
            data, status, _headers = gate_app.velaru_fuse("GET", "/api/v1/fuse/lookup")
        self.assertEqual(status, 503)
        self.assertTrue(data.get("halt"))
        self.assertFalse(data.get("verdict"))
        _not_allow(data)

    def test_bind_check_timeout_halts(self):
        with mock.patch.object(gate_app.requests, "request", side_effect=requests.Timeout("slow")):
            response = self.client.post(
                "/demo/pas/bind-check",
                json={"job_id": "job-timeout", "fuse_id": "fuse_velaru_drill"},
            )
        self.assertEqual(response.status_code, 503)
        body = response.get_json() or {}
        self.assertTrue(body.get("halt"))
        self.assertFalse(body.get("verdict"))
        _not_allow(body)

    def test_policycenter_and_duckcreek_timeout_halt(self):
        body = {"fuse_id": "fuse_velaru_drill", "job_id": "job-timeout"}
        with mock.patch.object(gate_app.requests, "request", side_effect=requests.Timeout("slow")):
            pc, pc_status, _extra = gate_app.run_policycenter_pre_bind(dict(body))
            dc, dc_status, _extra = gate_app.run_duckcreek_pre_bind(dict(body))
        for plan, status in ((pc, pc_status), (dc, dc_status)):
            self.assertGreaterEqual(status, 500)
            self.assertTrue(plan.get("halt"))
            self.assertFalse(plan.get("allow_bind"))
            self.assertNotIn("bind_ticket", plan)
            _not_allow(plan)

    def test_welded_act_unreachable_does_not_clear(self):
        with mock.patch.object(gate_app.requests, "request", side_effect=requests.ConnectionError("down")):
            hop, status, _extra = gate_app.run_welded_act("fuse_velaru_drill", "bind")
        self.assertEqual(status, 503)
        self.assertTrue(hop.get("halt"))
        self.assertFalse(hop.get("acted"))
        _not_allow(hop)

    def test_evidence_witness_unsigned_when_key_missing_or_sign_throws(self):
        with mock.patch.dict(os.environ, {"GATE_WITNESS_PRIVATE_KEY": "", "GATE_WITNESS_PUBLIC_KEY": ""}):
            head = evidence_log.signed_tree_head([])
        self.assertFalse(head["witness"]["signed"])
        self.assertFalse(head["witness"]["configured"])
        self.assertIsNone(head["witness"]["signature"])

        class Boom:
            def sign(self, _payload):
                raise RuntimeError("down")

        with mock.patch.object(evidence_log, "_witness_private_key", return_value=Boom()):
            self.assertIsNone(evidence_log._sign_witness("ab" * 32))

        with mock.patch.object(evidence_log, "witness_public_key_fingerprint", return_value="abc"):
            with mock.patch.object(evidence_log, "_sign_witness", return_value=None):
                with mock.patch.object(evidence_log, "witness_configured", return_value=True):
                    with mock.patch.object(evidence_log, "witness_public_key_b64", return_value="k"):
                        head = evidence_log.signed_tree_head(["aa" * 32])
        self.assertFalse(head["witness"]["signed"])
        self.assertIsNone(head["witness"]["signature"])


class OutreachSrcTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gate_db.init_db()
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_diligence_src_is_counted_and_junk_is_dropped(self):
        before = self.client.get("/.well-known/visits.json").get_json()
        prior = (before["pages"]["/diligence"].get("sources") or {}).get("batch-ccb-svo-v2", 0)
        tagged = self.client.get(
            "/diligence?src=batch-ccb-svo-v2",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        self.assertEqual(tagged.status_code, 200)
        junk = self.client.get(
            "/diligence?src=../../etc/passwd",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        self.assertEqual(junk.status_code, 200)
        after = self.client.get("/.well-known/visits.json").get_json()
        sources = after["pages"]["/diligence"]["sources"]
        self.assertEqual(sources.get("batch-ccb-svo-v2", 0), prior + 1)
        self.assertNotIn("../../etc/passwd", sources)
        self.assertNotIn("passwd", json_sources(sources))


def json_sources(sources: dict) -> str:
    return " ".join(sources)


if __name__ == "__main__":
    unittest.main()
