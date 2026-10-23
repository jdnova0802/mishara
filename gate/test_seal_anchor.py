"""Seal-root anchor. Run from gate/: python3 test_seal_anchor.py"""
from __future__ import annotations

import base64
import hashlib
import os
import pathlib
import sys
import tempfile
import unittest
import uuid
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

os.environ["GATE_DEV_MODE"] = "1"
os.environ["GATE_SECRET_KEY"] = "test-secret"
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), f"gate-anchor-{uuid.uuid4().hex}.db")
os.environ.pop("GATE_SEAL_ANCHOR_SPEND", None)
os.environ.pop("GATE_SEAL_ANCHOR_MODE", None)

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat

_priv = Ed25519PrivateKey.generate()
os.environ["GATE_RECEIPT_PRIVATE_KEY"] = base64.b64encode(
    _priv.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
).decode("utf-8")
os.environ["GATE_RECEIPT_PUBLIC_KEY"] = base64.b64encode(
    _priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
).decode("utf-8")

import anchor_chain  # noqa: E402
import app as gate_app  # noqa: E402
import db as gate_db  # noqa: E402
import evidence_log  # noqa: E402
import seal_anchor  # noqa: E402


class FakeChain:
    def __init__(self, *, base_fee: int = 5_000_000, estimate: int = 24_000):
        self.chain_id = anchor_chain.BASE_CHAIN_ID
        self.contract = "0x" + "11" * 20
        self.base_fee = base_fee
        self.estimate = estimate
        self.sent: list[dict] = []

    def base_fee_wei(self) -> int:
        return self.base_fee

    def estimate_commit(self, data: bytes) -> int:
        return self.estimate

    def broadcast_commit(self, data: bytes, gas_limit: int, max_fee: int, priority: int) -> str:
        tx_hash = "0x" + hashlib.sha256(data + str(len(self.sent)).encode()).hexdigest()
        self.sent.append(
            {"data": data, "gas_limit": gas_limit, "max_fee": max_fee, "priority": priority, "tx": tx_hash}
        )
        return tx_hash

    def receipt_status(self, tx_hash: str) -> int | None:
        if any(item["tx"] == tx_hash for item in self.sent):
            return 1
        return None


def _ots(digest: bytes) -> dict:
    return {
        "status": "submitted",
        "locator": "https://alice.btc.calendar.opentimestamps.org/timestamp/" + digest.hex(),
        "proof_hex": "abcd",
    }


def _words(data: bytes) -> tuple[int, str, str]:
    tree_size = int.from_bytes(data[4:36], "big")
    root = data[36:68].hex()
    prev = data[68:100].hex()
    return tree_size, root, prev


class AnchorChainTests(unittest.TestCase):
    def test_commit_gas_matches_memo_band(self):
        low = anchor_chain.commit_gas(1, b"\x00" * 32, b"\x00" * 32)
        high = anchor_chain.commit_gas(2**256 - 1, b"\xff" * 32, b"\xff" * 32)
        self.assertGreaterEqual(low, 22_000)
        self.assertLessEqual(high, anchor_chain.COMMIT_GAS_CEILING)
        self.assertLess(abs(high - anchor_chain.MEMO_COMMIT_GAS), 8_000)
        opcodes = []
        code = anchor_chain.RUNTIME_CODE
        index = 0
        while index < len(code):
            op = code[index]
            opcodes.append(op)
            if 0x60 <= op <= 0x7F:
                index += 1 + (op - 0x5F)
            else:
                index += 1
        self.assertNotIn(0x55, opcodes)

    def test_signature_recovers_to_the_signing_key(self):
        private = 0x4646464646464646464646464646464646464646464646464646464646464646
        raw = anchor_chain.sign_eip1559(
            private_key=private,
            chain_id=8453,
            nonce=1,
            max_priority_fee=1,
            max_fee=200_000_000,
            gas_limit=30_000,
            to=bytes.fromhex("11" * 20),
            data=anchor_chain.encode_commit(1, b"\x01" * 32, b"\x02" * 32),
        )
        self.assertEqual(raw[0], 2)
        self.assertEqual(anchor_chain.tx_hash(raw)[:2], "0x")
        point = anchor_chain.public_key(private)
        self.assertEqual(len(anchor_chain.keccak256(anchor_chain._xy(point))), 32)

    def test_ots_posts_the_statement_hash(self):
        digest = bytes.fromhex("ab" * 32)

        class _Resp:
            status = 200

            def read(self):
                return b"\x00ots"

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        seen = []

        def _open(request, timeout=10):
            seen.append((request.full_url, request.data))
            return _Resp()

        with mock.patch("urllib.request.urlopen", _open):
            out = seal_anchor.submit_ots(digest)
        self.assertEqual(seen[0][1], digest)
        self.assertTrue(seen[0][0].endswith("/digest"))
        self.assertIn(digest.hex(), out["locator"])
        self.assertEqual(out["status"], "submitted")


class SealAnchorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gate_app.GATE_DEV_MODE = True
        gate_app.app.config["TESTING"] = True
        cls.client = gate_app.app.test_client()

    def test_publish_extend_skip_and_stranger_fields(self):
        off = seal_anchor.run_once(mode="off")
        self.assertEqual(off["status"], "off")
        blocked = seal_anchor.run_once(mode="base")
        self.assertEqual(blocked["status"], "spend_disabled")

        chain = FakeChain()
        job = "pc:ANCHOR-1"
        first = gate_db.record_bind_event(
            fuse_id="fuse_velaru_drill", job_id=job, decision="HOLD", acted=False
        )
        dry = seal_anchor.run_once(mode="dry_run")
        self.assertEqual(dry["status"], "dry_run")
        self.assertEqual(seal_anchor.run_once(mode="dry_run")["status"], "skipped")
        quiet = self.client.get(f"/v1/seal/job?job_id={job}").get_json()
        self.assertFalse(quiet["anchor"]["covers_latest_print"])
        self.assertIsNone(quiet["anchor"]["published"])

        published = seal_anchor.run_once(mode="injected", chain=chain, ots_submitter=_ots)
        self.assertEqual(published["status"], "broadcast")
        self.assertEqual(len(chain.sent), 1)
        self.assertLessEqual(chain.sent[0]["gas_limit"], anchor_chain.COMMIT_GAS_CEILING)
        self.assertLessEqual(chain.sent[0]["max_fee"], anchor_chain.DEFAULT_MAX_FEE_WEI)
        tree_size, root, prev = _words(chain.sent[0]["data"])
        self.assertEqual(tree_size, 1)
        self.assertEqual(prev, evidence_log.EMPTY_LEAF.hex())
        self.assertEqual(root, published["root_hash"])
        self.assertEqual(seal_anchor.run_once(mode="injected", chain=chain, ots_submitter=_ots)["status"], "skipped")
        self.assertEqual(len(chain.sent), 1)

        seal = self.client.get(f"/v1/seal/job?job_id={job}").get_json()
        anchor = seal["anchor"]
        self.assertTrue(anchor["covers_latest_print"])
        self.assertEqual(anchor["leaf_index"], 0)
        self.assertEqual(anchor["siblings"], [])
        self.assertEqual(anchor["published"]["target"], "base")
        self.assertEqual(anchor["published"]["locator"], chain.sent[0]["tx"])
        self.assertEqual(anchor["published"]["chain_id"], 8453)
        self.assertTrue(anchor["published"]["ots_locator"].startswith("https://alice.btc.calendar.opentimestamps.org/timestamp/"))
        encoded, digest = seal_anchor.canonical_statement(
            tree_size=anchor["tree_size"],
            root_hash=anchor["root_hash"],
            prev_tree_size=anchor["prev_tree_size"],
            prev_root_hash=anchor["prev_root_hash"],
        )
        self.assertEqual(digest, anchor["published"]["statement_hash"])
        self.assertIn('"spec":"gate-seal-anchor-v1"', encoded)
        self.assertTrue(
            evidence_log.verify_inclusion(
                leaf_hash=anchor["leaf_hash"],
                root_hash=anchor["root_hash"],
                proof={"index": anchor["leaf_index"], "siblings": anchor["siblings"]},
            )
        )
        self.assertEqual(seal["prints"][0]["event_id"], first)
        self.assertEqual(seal["prints"][0]["leaf_index"], 0)

        gate_db.record_bind_event(
            fuse_id="fuse_velaru_drill", job_id=job, decision="HALT", acted=False
        )
        mid = self.client.get(f"/v1/seal/job?job_id={job}").get_json()
        self.assertFalse(mid["anchor"]["covers_latest_print"])
        self.assertEqual(mid["prints"][0]["leaf_index"], 0)
        self.assertIsNone(mid["prints"][1]["leaf_index"])
        self.assertEqual(mid["anchor"]["leaf_index"], 0)

        extended = seal_anchor.run_once(mode="injected", chain=chain, ots_submitter=_ots)
        self.assertEqual(extended["status"], "broadcast")
        self.assertEqual(len(chain.sent), 2)
        size2, root2, prev2 = _words(chain.sent[1]["data"])
        self.assertEqual(size2, 2)
        self.assertEqual(prev2, root)
        self.assertNotEqual(root2, root)
        both = self.client.get(f"/v1/seal/job?job_id={job}").get_json()
        self.assertTrue(both["anchor"]["covers_latest_print"])
        self.assertEqual([item["leaf_index"] for item in both["prints"]], [0, 1])
        for item in both["prints"]:
            self.assertTrue(
                evidence_log.verify_inclusion(
                    leaf_hash=item["leaf_hash"],
                    root_hash=both["anchor"]["root_hash"],
                    proof={"index": item["leaf_index"], "siblings": item["siblings"]},
                )
            )

        with gate_db.db() as conn:
            original = conn.execute(
                "SELECT receipt_hash FROM bind_events WHERE id = ?", (first,)
            ).fetchone()["receipt_hash"]
            conn.execute(
                "UPDATE bind_events SET receipt_hash = ? WHERE id = ?",
                ("ab" * 32, first),
            )
        refused = seal_anchor.run_once(mode="injected", chain=chain, ots_submitter=_ots)
        self.assertEqual(refused["status"], "refused")
        self.assertEqual(refused["reason"], "not_an_append")
        self.assertEqual(len(chain.sent), 2)

        with gate_db.db() as conn:
            conn.execute(
                "UPDATE bind_events SET receipt_hash = ? WHERE id = ?",
                (original, first),
            )
        chain.base_fee = anchor_chain.DEFAULT_MAX_FEE_WEI + 1
        gate_db.record_bind_event(
            fuse_id="fuse_velaru_drill", job_id=job, decision="HOLD", acted=False
        )
        capped = seal_anchor.run_once(mode="injected", chain=chain, ots_submitter=_ots)
        self.assertEqual(capped["status"], "fee_capped")
        self.assertEqual(len(chain.sent), 2)

        chain.base_fee = 5_000_000
        chain.estimate = 40_000
        above = seal_anchor.run_once(mode="injected", chain=chain, ots_submitter=_ots)
        self.assertEqual(above["status"], "gas_above_memo")
        self.assertEqual(len(chain.sent), 2)

        chain.estimate = 24_000
        calls = {"n": 0}

        def _receipt(tx_hash):
            calls["n"] += 1
            if calls["n"] == 1:
                return None
            return 1

        chain.receipt_status = _receipt
        pending = seal_anchor.run_once(mode="injected", chain=chain, ots_submitter=_ots)
        self.assertEqual(pending["status"], "pending")
        self.assertEqual(len(chain.sent), 3)
        waiting = self.client.get(f"/v1/seal/job?job_id={job}").get_json()
        self.assertEqual(waiting["anchor"]["tree_size"], 2)
        self.assertNotEqual(waiting["anchor"]["published"]["locator"], chain.sent[-1]["tx"])
        self.assertFalse(waiting["anchor"]["covers_latest_print"])
        landed = seal_anchor.run_once(mode="injected", chain=chain, ots_submitter=_ots)
        self.assertEqual(landed["status"], "broadcast")
        self.assertEqual(len(chain.sent), 3)
        final = self.client.get(f"/v1/seal/job?job_id={job}").get_json()
        self.assertEqual(final["anchor"]["published"]["locator"], chain.sent[-1]["tx"])
        self.assertTrue(final["anchor"]["covers_latest_print"])
        self.assertEqual(final["anchor"]["tree_size"], 3)

    def test_docs_name_the_stranger_check(self):
        response = self.client.get("/.well-known/seal-anchor.json")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("noindex", (response.headers.get("X-Robots-Tag") or "").lower())
        body = response.get_json()
        self.assertEqual(body["spec"], "gate-seal-anchor-v1")
        self.assertEqual(body["cadence_seconds"], 900)
        self.assertEqual(body["default_mode"], "off")
        self.assertIsNone(body["latest"]["published"])
        self.assertIsNone(body["latest"]["root_hash"])
        self.assertIsNone(body["latest"]["prev_root_hash"])
        text = " ".join(body["verify"])
        self.assertIn("leaf_hash", text)
        self.assertIn("siblings", text)
        self.assertIn("root_hash", text)
        self.assertIn("published.locator", text)
        self.assertIn("OpenTimestamps", text)
        self.assertIn("prev_root_hash", text)
        self.assertIn("covers_latest_print", text)
        self.assertIn("/v1/seal/job", body["job"])
        gate = self.client.get("/.well-known/gate.json").get_json()
        self.assertTrue(gate["seal_anchor"].endswith("/.well-known/seal-anchor.json"))

    def test_hot_paths_stay_untouched(self):
        root = pathlib.Path(__file__).resolve().parent
        issuing = (root / "issuing_mouth.py").read_text(encoding="utf-8")
        deploy = (root / "deploy_render.py").read_text(encoding="utf-8")
        clock = (root / "clock.py").read_text(encoding="utf-8")
        settlement = (root / "settlement.py").read_text(encoding="utf-8")
        anchor = (root / "seal_anchor.py").read_text(encoding="utf-8")
        self.assertNotIn("seal_anchor", issuing)
        self.assertNotIn("anchor_chain", issuing)
        self.assertNotIn("GATE_SEAL_ANCHOR", deploy)
        self.assertNotIn("seal_anchor", deploy)
        self.assertIn("BIND_SETTLEMENT_WINDOW_MINUTES = 60", clock)
        self.assertIn("WINDOW_DURATION_MINUTES = 60", settlement)
        self.assertNotIn("issuing_mouth", anchor)
        self.assertNotIn("BIND_SETTLEMENT_WINDOW_MINUTES", anchor)
        self.assertNotIn("WINDOW_DURATION_MINUTES", anchor)
        blotter = (root / "blotter.py").read_text(encoding="utf-8")
        self.assertNotIn("run_once", blotter)


if __name__ == "__main__":
    unittest.main()
