"""Bind-only intercept and the public CCB/SVO finding. Run from gate/."""
from __future__ import annotations

import base64
import os
import sys
import tempfile
import unittest
import uuid
from datetime import datetime, timezone
from unittest import mock

import requests

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(
    tempfile.gettempdir(), f"gate-test-bind-only-{uuid.uuid4().hex}.db"
)
os.environ.pop("GATE_POLICYCENTER_BASE_URL", None)
os.environ.pop("RENDER_EXTERNAL_URL", None)

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
import finding_ccb  # noqa: E402
import spend_protocol  # noqa: E402
import ticket as ticket_mod  # noqa: E402


def _ticket(job_id: str) -> dict:
    write = spend_protocol.write(job_id=job_id)
    issued = ticket_mod.issue(
        job_id=job_id,
        fuse_id="fuse_velaru_drill",
        event_id=str(uuid.uuid4()),
        receipt_hash=None,
        redeem_url="https://example.test/redeem",
        spend_write=write,
    )
    bearer = issued["bearer"]
    return {
        "X-Gate-Ticket-Id": bearer["ticket_id"],
        "X-Gate-Ticket-Token": bearer["token"],
        "X-Gate-Spend-Fingerprint": bearer["spend_fingerprint"],
        "X-Gate-Now": datetime.now(timezone.utc).isoformat(),
        "Authorization": "Bearer pc-test",
    }


class BindOnlyInterceptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gate_db.init_db()
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_upstream_unset_does_not_consume_or_bind(self):
        os.environ.pop("GATE_POLICYCENTER_BASE_URL", None)
        job_id = "pc:unset-" + uuid.uuid4().hex[:8]
        headers = _ticket(job_id)
        response = self.client.post(f"/job/v1/jobs/{job_id}/bind-only", headers=headers)
        self.assertEqual(response.status_code, 409)
        body = response.get_json()
        self.assertFalse(body["bound"])
        self.assertFalse(body["forwarded"])
        self.assertNotIn("their_production", body)
        self.assertEqual(body["reason"], "policycenter_upstream_unset")
        again = ticket_mod.redeem(
            ticket_id=headers["X-Gate-Ticket-Id"],
            token=headers["X-Gate-Ticket-Token"],
            job_id=job_id,
            method="POST",
            path=spend_protocol.bind_only_path(job_id),
            spend_fingerprint=headers["X-Gate-Spend-Fingerprint"],
            now=headers["X-Gate-Now"],
        )
        self.assertTrue(again.get("allow_bind"), again)

    def test_missing_ticket_does_not_forward(self):
        os.environ["GATE_POLICYCENTER_BASE_URL"] = "https://pc.example"
        job_id = "pc:noticket"
        with mock.patch("bind_only_intercept.requests.post") as post:
            response = self.client.post(f"/job/v1/jobs/{job_id}/bind-only")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json()["reason"], "ticket_required")
        post.assert_not_called()

    def test_timeout_does_not_report_bound(self):
        os.environ["GATE_POLICYCENTER_BASE_URL"] = "https://pc.example"
        job_id = "pc:slow-" + uuid.uuid4().hex[:8]
        headers = _ticket(job_id)
        with mock.patch(
            "bind_only_intercept.requests.post",
            side_effect=requests.Timeout("slow"),
        ) as post:
            response = self.client.post(f"/job/v1/jobs/{job_id}/bind-only", headers=headers)
        self.assertEqual(response.status_code, 503)
        body = response.get_json()
        self.assertFalse(body["bound"])
        self.assertTrue(body["halt"])
        self.assertNotIn("their_production", body)
        self.assertEqual(body["reason"], "policycenter_timeout")
        post.assert_called_once()
        self.assertEqual(post.call_args.kwargs.get("data"), b"")
        self.assertTrue(post.call_args.args[0].endswith(f"/job/v1/jobs/{job_id}/bind-only"))

    def test_upstream_2xx_forwards_once_and_stays_not_their_production(self):
        os.environ["GATE_POLICYCENTER_BASE_URL"] = "https://pc.example"
        job_id = "pc:4040"
        headers = _ticket(job_id)

        class Response:
            status_code = 201
            text = "{}"

        with mock.patch("bind_only_intercept.requests.post", return_value=Response()) as post:
            response = self.client.post(f"/job/v1/jobs/{job_id}/bind-only", headers=headers)
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertTrue(body["bound"])
        self.assertTrue(body["forwarded"])
        self.assertNotIn("their_production", body)
        self.assertEqual(body["upstream_status"], 201)
        post.assert_called_once()
        self.assertNotIn("Bearer pc-test", response.get_data(as_text=True))

    def test_other_writes_are_not_forwarded(self):
        os.environ["GATE_POLICYCENTER_BASE_URL"] = "https://pc.example"
        with mock.patch("bind_only_intercept.requests.post") as post:
            bind = self.client.post("/job/v1/jobs/pc:4040/bind-and-issue")
            issue = self.client.post("/policy/v1/policies/pc:9/issue")
        self.assertEqual(bind.status_code, 403)
        self.assertEqual(issue.status_code, 403)
        self.assertEqual(bind.get_json()["reason"], "not_this_write")
        post.assert_not_called()


class FindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gate_db.init_db()
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_public_finding_verifies_and_names_the_drop(self):
        response = self.client.get("/.well-known/finding/ccb-svo.json")
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["dated"], "2026-10-27")
        self.assertTrue(body["prior_on_list"])
        self.assertFalse(body["current_on_list"])
        self.assertNotIn("their_production", body)
        self.assertIn("Model 786", body["grandfather"])
        self.assertTrue(finding_ccb.verifies(body), body.get("signature"))
        flipped = dict(body)
        flipped["current_on_list"] = True
        self.assertFalse(finding_ccb.verifies(flipped))


if __name__ == "__main__":
    unittest.main()
