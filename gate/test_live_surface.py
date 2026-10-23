"""Live strip, watcher roster, and the floor dead-hand box."""
from __future__ import annotations

import base64
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-live-surface.db")
os.environ.pop("RENDER_EXTERNAL_URL", None)
os.environ.pop("RENDER_EXTERNAL_HOSTNAME", None)

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat

_priv = Ed25519PrivateKey.generate()
_priv_b = _priv.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
_pub_b = _priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
os.environ["GATE_RECEIPT_PRIVATE_KEY"] = base64.b64encode(_priv_b).decode("utf-8")
os.environ["GATE_RECEIPT_PUBLIC_KEY"] = base64.b64encode(_pub_b).decode("utf-8")
PUB_B64 = os.environ["GATE_RECEIPT_PUBLIC_KEY"]

if os.path.exists(os.environ["GATE_DB_PATH"]):
    os.remove(os.environ["GATE_DB_PATH"])

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import db  # noqa: E402
import liturgy  # noqa: E402
import receipt  # noqa: E402


class LiveSurfaceTests(unittest.TestCase):
    def setUp(self):
        self.client = app_mod.app.test_client()

    def test_next_mass_skips_to_the_following_sunday_when_today_is_sunday(self):
        wed = datetime(2026, 10, 21, 15, 0, tzinfo=timezone.utc)
        self.assertEqual(liturgy.next_mass_start(wed).date().isoformat(), "2026-10-25")
        sun = datetime(2026, 10, 25, 15, 0, tzinfo=timezone.utc)
        self.assertEqual(liturgy.next_mass_start(sun).date().isoformat(), "2026-11-01")
        self.assertEqual(liturgy.stopped_write_count([]), 0)

    def test_pages_show_the_live_strip_and_an_empty_roster(self):
        home = self.client.get("/")
        self.assertEqual(home.status_code, 200)
        self.assertIn(b"Evidence head", home.data)
        self.assertNotIn(b"0 irreversible writes stopped", home.data)
        self.assertIn(b"This counter records blocked binds", home.data)
        self.assertIn(b"data-mass-countdown", home.data)
        self.assertNotIn(b"protocol-doors", home.data)
        self.assertNotIn(b"What you can call now", home.data)
        self.assertNotIn(b"Already built", home.data)
        self.assertNotIn(b"What happens in one link", home.data)
        self.assertNotIn(b"See a blocked bind", home.data)
        self.assertNotIn(b"Book Bind Room", home.data)
        self.assertEqual(home.data.count(b"btn-primary"), 1)
        self.assertIn(b"Open Bind Room", home.data)
        self.assertIn(b"Why the CGL does not cover it", home.data)
        self.assertIn(b"data-receipt-lookup", home.data)
        self.assertIn(b"data-merkle-strip", home.data)
        self.assertIn(b"Museum until you paste a real id", home.data)
        self.assertIn(b"No published Base root", home.data)
        self.assertIn(b"live_proof.js", home.data)
        self.assertIn(b"Not a volume ticker", home.data)
        self.assertNotIn(b"/v1/seal?event_id", home.data)
        self.assertIn(b"Empty tree, not a customer", home.data)
        self.assertEqual(home.data.count(b"btn-primary"), 1)
        docs = self.client.get("/docs")
        self.assertEqual(docs.status_code, 200)
        self.assertIn(b"protocol-doors", docs.data)
        self.assertIn(b"What you can call now", docs.data)
        self.assertIn(b"See a blocked bind", docs.data)
        self.assertIn(b"openapi.json", docs.data)
        self.assertIn(b"mcp.json", docs.data)
        self.assertIn(b"x402.json", docs.data)
        self.assertNotIn(b"lab fuse", home.data)
        self.assertNotIn(b"exclusive-door", home.data)
        self.assertNotIn(b">Stair</a>", home.data)

        built = self.client.get("/.well-known/already-built.json")
        self.assertEqual(built.status_code, 200)
        card = built.get_json()
        self.assertEqual(card["spec"], "gate-already-built-v1")
        self.assertEqual([d["id"] for d in card["doors"]], ["mcp", "openapi", "x402", "cli"])
        self.assertNotIn("their_production", card)
        gate = self.client.get("/.well-known/gate.json").get_json()
        self.assertTrue(gate["already_built"].endswith("/.well-known/already-built.json"))
        openapi = self.client.get("/openapi.json").get_json()
        self.assertEqual(openapi["openapi"], "3.1.0")
        self.assertIn("/v1/prefinality/evaluate", openapi["paths"])
        llms = self.client.get("/llms.txt").get_data(as_text=True)
        self.assertIn("already-built.json", llms)

        floor = self.client.get("/floor")
        self.assertEqual(floor.status_code, 200)
        self.assertIn(b"dead-hand", floor.data)
        self.assertIn(b"Public key you already hold", floor.data)
        self.assertNotIn(b"curl -s", floor.data)
        self.assertIn(b"loader", floor.data)
        self.assertIn(b"toast", floor.data)
        self.assertIn(b"offline_verify.py", floor.data)

        mass = self.client.get("/mass")
        self.assertEqual(mass.status_code, 200)
        self.assertIn(b"Independent watchers", mass.data)
        self.assertIn(b"does not count", mass.data)
        self.assertIn(b"No stranger has registered a fresh check.", mass.data)
        self.assertIn(b"0 fresh", mass.data)
        self.assertIn(b"badge-halt", mass.data)
        self.assertIn(b"Empty is the log, not missing software", mass.data)

    def test_roster_lists_a_stranger_who_registered(self):
        head = self.client.get("/.well-known/evidence-head.json").get_json()
        reg = self.client.post(
            "/v1/evidence-watch/register",
            json={
                "handle": "stranger-lab",
                "homepage": "https://example.com/watch",
                "tree_size": head["tree_size"],
                "root_hash": head["root_hash"],
            },
        )
        self.assertEqual(reg.status_code, 200, reg.get_data(as_text=True))
        mass = self.client.get("/mass").get_data(as_text=True)
        self.assertIn("stranger-lab", mass)
        self.assertIn("https://example.com/watch", mass)
        self.assertNotIn("No stranger has registered a fresh check.", mass)

    def test_stopped_writes_count_real_halts_only(self):
        before = self.client.get("/").get_data(as_text=True)
        db.record_bind_event(
            fuse_id="fuse_velaru_drill",
            decision="HALT",
            job_id="pc:stopped-1",
            verify_url="https://velaru.xyz/verify?r=stopped-1",
            hop={"state": "DEAD", "halt": True, "verdict": "HALT"},
            acted=False,
        )
        after = self.client.get("/").get_data(as_text=True)
        self.assertIn("This counter records blocked binds", before)
        self.assertNotIn("0 irreversible writes stopped", before)
        self.assertIn("1 irreversible write stopped", after)

    def test_floor_verify_valid_invalid_and_does_not_open_a_path(self):
        issued = receipt.issue_receipt(
            event_id="evt-floor-1",
            fuse_id="fuse_velaru_drill",
            job_id="pc:DEMO",
            decision="BLOCK",
            acted=False,
            verify_url="https://gate.velaru.xyz/verify/evt-floor-1",
            created_at="2026-10-21T14:00:00+00:00",
            hop={"state": "halt", "halt": True, "verdict": "BLOCK"},
            prev_receipt_hash=None,
        )
        canonical = json.loads(issued["canonical_receipt_json"])
        payload = {
            "canonical_receipt": canonical,
            "canonical_receipt_json": issued["canonical_receipt_json"],
            "receipt_hash": issued["receipt_hash"],
            "receipt_signature": issued["receipt_signature"],
            "receipt_public_key_fingerprint": issued["receipt_public_key_fingerprint"],
        }
        ok = self.client.post("/floor/verify", json={"receipt": payload, "public_key": PUB_B64})
        body = ok.get_json()
        self.assertEqual(ok.status_code, 200)
        self.assertEqual(body["verdict"], "valid")
        self.assertNotIn(PUB_B64, json.dumps(body))
        self.assertNotIn("public_key", body)

        payload["canonical_receipt"]["decision"] = "ALLOW"
        bad = self.client.post("/floor/verify", json={"receipt": payload, "public_key": PUB_B64})
        self.assertEqual(bad.get_json()["verdict"], "invalid")

        key_path = os.path.join(tempfile.gettempdir(), "gate-live-surface-pubkey.txt")
        with open(key_path, "w", encoding="utf-8") as fh:
            fh.write(PUB_B64)
        leaked = self.client.post(
            "/floor/verify",
            json={"receipt": payload, "public_key": key_path},
        )
        self.assertEqual(leaked.get_json()["verdict"], "invalid")
        self.assertIn("bad_public_key", leaked.get_json()["reasons"])


if __name__ == "__main__":
    unittest.main()
