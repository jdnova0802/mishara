"""C2SP tlog-witness subset — checkpoint + add-checkpoint after consistency."""
from __future__ import annotations

import base64
import hashlib
import os
import sys
import tempfile
import unittest
import uuid

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-tlog-witness.db")
os.environ.pop("RENDER_EXTERNAL_URL", None)
os.environ.pop("RENDER_EXTERNAL_HOSTNAME", None)
os.environ["GATE_TLOG_ORIGIN"] = "gate.velaru.xyz/evidence"

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

if os.path.exists(os.environ["GATE_DB_PATH"]):
    os.remove(os.environ["GATE_DB_PATH"])

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import evidence_log  # noqa: E402
import tlog_witness  # noqa: E402


def _leaves(*labels: bytes) -> list[str]:
    return [hashlib.sha256(x).hexdigest() for x in labels]


class TlogWitnessTests(unittest.TestCase):
    def setUp(self):
        self._db = os.path.join(tempfile.gettempdir(), f"gate-tlog-{uuid.uuid4().hex}.db")
        os.environ["GATE_DB_PATH"] = self._db
        path = tlog_witness._state_path()
        if os.path.exists(path):
            os.remove(path)
        self.client = app_mod.app.test_client()

    def tearDown(self):
        path = tlog_witness._state_path()
        for p in (path, self._db):
            if p and os.path.exists(p):
                os.remove(p)

    def test_head_exposes_c2sp_spec_without_free_cosign(self):
        leaves = _leaves(b"a", b"b")
        head = evidence_log.signed_tree_head(leaves)
        self.assertEqual(head["c2sp"]["spec"], tlog_witness.SPEC)
        self.assertTrue(head["c2sp"]["checkpoint"].startswith("gate.velaru.xyz/evidence\n"))
        self.assertIsNone(head["c2sp"]["cosignature"])
        self.assertEqual(head["witness"]["spec"], "gate-evidence-witness-v1")
        self.assertTrue(head["witness"]["signed"])

    def test_add_checkpoint_first_old_size_zero_then_skip_fails(self):
        leaves = _leaves(b"a", b"b")
        first = tlog_witness.add_checkpoint(leaves=leaves, old_size=0)
        self.assertTrue(first["ok"], first)
        self.assertEqual(first["tree_size"], 2)
        self.assertTrue(
            tlog_witness.verify_cosignature(
                checkpoint=first["checkpoint"],
                timestamp=first["cosignature"]["timestamp"],
                signature_b64=first["cosignature"]["signature"],
            )
        )
        skip = tlog_witness.add_checkpoint(leaves=leaves, old_size=0)
        self.assertFalse(skip["ok"])
        self.assertEqual(skip["error"], "old_size_must_equal_last_checkpoint")
        grown = leaves + _leaves(b"c")
        again = tlog_witness.add_checkpoint(leaves=grown, old_size=2)
        self.assertTrue(again["ok"], again)
        self.assertEqual(again["tree_size"], 3)
        attached = evidence_log.signed_tree_head(grown)
        self.assertEqual(attached["c2sp"]["cosignature"]["signature"], again["cosignature"]["signature"])

    def test_flask_witness_manifest_and_add_checkpoint(self):
        wk = self.client.get("/.well-known/evidence-witness.json")
        self.assertEqual(wk.status_code, 200)
        body = wk.get_json()
        self.assertEqual(body["spec"], tlog_witness.SPEC)
        self.assertTrue(body["configured"])
        self.assertNotIn("their_production", body)
        gate = self.client.get("/.well-known/gate.json").get_json()
        self.assertIn("evidence-witness.json", gate["evidence_witness"])
        head = self.client.get("/.well-known/evidence-head.json").get_json()
        self.assertEqual(head["c2sp"]["spec"], tlog_witness.SPEC)
        first = self.client.post("/v1/evidence-witness/add-checkpoint", json={"old_size": 0})
        self.assertEqual(first.status_code, 200, first.get_json())
        self.assertTrue(first.get_json()["ok"])
        skip = self.client.post("/v1/evidence-witness/add-checkpoint", json={"old_size": 99})
        self.assertEqual(skip.status_code, 400)
        self.assertFalse(skip.get_json()["ok"])


if __name__ == "__main__":
    unittest.main()
