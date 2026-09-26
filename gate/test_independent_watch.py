"""Independent watcher self-register tests."""
from __future__ import annotations

import base64
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-ind-watch.db")

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption, PublicFormat

    _priv = Ed25519PrivateKey.generate()
    _priv_bytes = _priv.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    _pub_bytes = _priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    os.environ["GATE_RECEIPT_PRIVATE_KEY"] = base64.b64encode(_priv_bytes).decode("utf-8")
    os.environ["GATE_RECEIPT_PUBLIC_KEY"] = base64.b64encode(_pub_bytes).decode("utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import db  # noqa: E402
import independent_watch as iw  # noqa: E402

# Fresh DB
if os.path.exists(os.environ["GATE_DB_PATH"]):
    os.remove(os.environ["GATE_DB_PATH"])
db.init_db()


class IndependentWatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.init_db()

    def setUp(self):
        # Isolate roster between cases (shared temp DB file).
        with db.db() as conn:
            iw._ensure_table(conn)
            conn.execute("DELETE FROM independent_watchers")

    def test_register_requires_live_head_match(self):
        head = iw.live_head()
        bad = iw.register(
            {
                "handle": "alice-ops",
                "tree_size": head["tree_size"],
                "root_hash": "00" * 32,
            }
        )
        self.assertFalse(bad["ok"])
        self.assertEqual(bad["error"], "head_mismatch")

        good = iw.register(
            {
                "handle": "alice-ops",
                "tree_size": head["tree_size"],
                "root_hash": head["root_hash"],
                "homepage": "https://example.com/watch",
                "note": "cron from home lab",
                "sampled_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        self.assertTrue(good["ok"], good)
        self.assertEqual(good["event"], "registered")
        listed = iw.list_watchers()
        self.assertEqual(len(listed), 1)
        self.assertEqual(listed[0]["handle"], "alice-ops")
        self.assertTrue(listed[0]["fresh"])
        self.assertFalse(listed[0]["paid_by_gate"])

        again = iw.register(
            {
                "handle": "alice-ops",
                "tree_size": head["tree_size"],
                "root_hash": head["root_hash"],
            }
        )
        self.assertTrue(again["ok"])
        self.assertEqual(again["event"], "refreshed")
        self.assertEqual(iw.list_watchers()[0]["sample_count"], 2)

    def test_flask_routes(self):
        import app as gate_app

        c = gate_app.app.test_client()
        head = c.get("/.well-known/evidence-head.json").get_json()
        r = c.post(
            "/v1/evidence-watch/register",
            json={
                "handle": "bob-lab",
                "tree_size": head["tree_size"],
                "root_hash": head["root_hash"],
            },
        )
        self.assertEqual(r.status_code, 200, r.get_json())
        watch = c.get("/.well-known/evidence-watch.json").get_json()
        handles = [w["handle"] for w in watch.get("independent_watchers") or []]
        self.assertIn("bob-lab", handles)
        self.assertIn("/v1/evidence-watch/register", watch.get("register") or "")


if __name__ == "__main__":
    unittest.main()
