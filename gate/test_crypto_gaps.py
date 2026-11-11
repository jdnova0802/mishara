"""R1/R2/R3/R6/R7/142 — key directory, absence, policy transcript, exclusive door, signed 161."""
from __future__ import annotations

import base64
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-crypto-gaps.db")
for key, name in (
    ("GATE_KEYDIR_PATH", "keydir.json"),
    ("GATE_CUSTODY_PATH", "custody.json"),
    ("GATE_LIVE_CHANNEL_PATH", "lc.json"),
    ("GATE_EXPOSURE_BOND_PATH", "bond.json"),
):
    os.environ[key] = os.path.join(tempfile.gettempdir(), f"gate-test-crypto-gaps-{name}")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import absence  # noqa: E402
import app as app_mod  # noqa: E402
import exclusive_session  # noqa: E402
import exposure_bond  # noqa: E402
import key_transparency  # noqa: E402
import live_channel  # noqa: E402
import policy_transcript  # noqa: E402
import signing_custody  # noqa: E402


def _wipe():
    for key in (
        "GATE_KEYDIR_PATH",
        "GATE_CUSTODY_PATH",
        "GATE_LIVE_CHANNEL_PATH",
        "GATE_EXPOSURE_BOND_PATH",
    ):
        path = os.environ[key]
        if os.path.exists(path):
            os.remove(path)


class KeydirTests(unittest.TestCase):
    def setUp(self):
        _wipe()

    def test_equivocation_and_inclusion(self):
        a = key_transparency.publish(epoch="2026-11", fingerprint="aa" * 16)
        self.assertTrue(a["ok"])
        inc = key_transparency.prove_inclusion(fingerprint=a["fingerprint"])
        self.assertTrue(inc["verified"])
        miss = key_transparency.prove_absence(epoch="2026-11", fingerprint="bb" * 16)
        self.assertTrue(miss["absent"])
        key_transparency.publish(epoch="2026-11", fingerprint="cc" * 16)
        eq = key_transparency.equivocation()
        self.assertTrue(eq["equivocation"])
        cat = key_transparency.catalog()
        self.assertFalse(cat["hsm"])
        self.assertTrue(cat["single_admin"])


class AbsenceTests(unittest.TestCase):
    def test_window_has_no_allow(self):
        t0 = "2026-01-01T00:00:00+00:00"
        t1 = "2026-01-02T00:00:00+00:00"
        rows = [
            {
                "id": "e1",
                "fuse_id": "fuse_a",
                "job_id": "job_1",
                "decision": "HOLD",
                "receipt_hash": "11" * 32,
                "created_at": "2026-01-01T12:00:00+00:00",
            }
        ]
        rec = absence.prove(rows, fuse_id="fuse_a", job_id="job_1", t0=t0, t1=t1)
        self.assertTrue(rec["absent"])
        rows.append(
            {
                "id": "e2",
                "fuse_id": "fuse_a",
                "job_id": "job_1",
                "decision": "ALLOW",
                "receipt_hash": "22" * 32,
                "created_at": "2026-01-01T13:00:00+00:00",
            }
        )
        hot = absence.prove(rows, fuse_id="fuse_a", job_id="job_1", t0=t0, t1=t1)
        self.assertFalse(hot["absent"])


class PolicyTests(unittest.TestCase):
    def test_replay_not_zk(self):
        rec = policy_transcript.evaluate(public_inputs={"amount": "1"})
        self.assertFalse(rec["zk_circuit"])
        self.assertEqual(rec["verdict"], "ALLOW")
        self.assertTrue(policy_transcript.verify(rec)["match"])
        fake = dict(rec)
        fake["verdict"] = "BLOCK"
        self.assertFalse(policy_transcript.verify(fake)["ok"])


class SignedChallengeTests(unittest.TestCase):
    def setUp(self):
        _wipe()

    def test_signed_key_on_file(self):
        priv = Ed25519PrivateKey.generate()
        pub = base64.b64encode(priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)).decode()
        live_channel.register_contact(
            claimed_identity_ref="cfo",
            callback="+15550199",
            legal_person="Hospital Corp",
            public_key_b64=pub,
        )
        denied = live_channel.issue_challenge(
            claimed_identity_ref="cfo",
            channel="voice_call",
            out_of_band_method="signed_key_on_file",
        )
        self.assertTrue(denied.get("ok"))
        bad = live_channel.respond_signed(challenge_id=denied["challenge_id"], signature_b64="AAAA")
        self.assertEqual(bad["error"], "signature_mismatch")
        sig = base64.b64encode(priv.sign(denied["challenge_nonce"].encode())).decode()
        ok = live_channel.respond_signed(challenge_id=denied["challenge_id"], signature_b64=sig)
        self.assertTrue(ok["signed_response"])


class CustodyTests(unittest.TestCase):
    def setUp(self):
        _wipe()

    def test_ceremony_does_not_flip_hsm(self):
        st = signing_custody.status()
        self.assertTrue(st["single_admin"])
        self.assertTrue(st["online"])
        self.assertFalse(st["hsm"])
        rec = signing_custody.record_ceremony(
            custodians=["alice", "bob", "carol"],
            m=2,
            n=3,
            note="intent only",
        )
        self.assertTrue(rec["ok"])
        self.assertFalse(rec["hsm"])
        self.assertFalse(rec["quorum_active"])
        after = signing_custody.status()
        self.assertFalse(after["hsm"])
        self.assertIsNone(after["quorum_m"])


class ExclusiveTests(unittest.TestCase):
    def setUp(self):
        _wipe()

    def test_abort_then_clear_without_write(self):
        t0 = (datetime.now(timezone.utc) - timedelta(hours=1)).replace(microsecond=0).isoformat()
        t1 = (datetime.now(timezone.utc) + timedelta(hours=1)).replace(microsecond=0).isoformat()
        first = exclusive_session.open_session(
            [],
            fuse_id="fuse_x",
            job_id="job_x",
            challenge_id="missing",
            bond_id="",
            amount="100",
            public_inputs={},
            t0=t0,
            t1=t1,
        )
        self.assertFalse(first["ok"])
        self.assertEqual(first["abort"], "challenge")
        self.assertFalse(first["write_executed"])

        live_channel.register_contact(
            claimed_identity_ref="cfo",
            callback="+15550199",
            legal_person="Hospital Corp",
        )
        ch = live_channel.issue_challenge(claimed_identity_ref="cfo", channel="voice_call")
        live_channel.respond(challenge_id=ch["challenge_id"], nonce=ch["challenge_nonce"])
        bond = exposure_bond.post(legal_person="Hospital Corp", posted="100", covers_ref=ch["challenge_id"])
        media = exclusive_session.open_session(
            [],
            fuse_id="fuse_x",
            job_id="job_x",
            challenge_id=ch["challenge_id"],
            bond_id=bond["bond_id"],
            amount="100",
            public_inputs={},
            t0=t0,
            t1=t1,
            media_evidence_claimed=True,
        )
        self.assertEqual(media["abort"], "media")

        clear = exclusive_session.open_session(
            [],
            fuse_id="fuse_x",
            job_id="job_x",
            challenge_id=ch["challenge_id"],
            bond_id=bond["bond_id"],
            amount="100",
            public_inputs={},
            t0=t0,
            t1=t1,
        )
        self.assertTrue(clear["ok"])
        self.assertFalse(clear["write_executed"])
        self.assertTrue(clear["clearance_only"])


class HttpSmoke(unittest.TestCase):
    def setUp(self):
        _wipe()
        self.c = app_mod.app.test_client()

    def test_routes(self):
        self.assertEqual(self.c.get("/v1/signing-custody").status_code, 200)
        body = self.c.get("/v1/signing-custody").get_json()
        self.assertFalse(body["hsm"])
        self.assertTrue(body["single_admin"])
        pub = self.c.post(
            "/v1/keydir",
            json={"epoch": "2026-11", "fingerprint": "dd" * 16},
        )
        self.assertEqual(pub.status_code, 201)
        eq = self.c.get("/v1/keydir/equivocation").get_json()
        self.assertFalse(eq["equivocation"])
        pol = self.c.get("/v1/policy-transcript").get_json()
        self.assertFalse(pol["zk_circuit"])
        absn = self.c.post(
            "/v1/absence",
            json={
                "fuse_id": "fuse_none",
                "t0": "2026-01-01T00:00:00+00:00",
                "t1": "2026-01-02T00:00:00+00:00",
            },
        )
        self.assertEqual(absn.status_code, 200)
        self.assertTrue(absn.get_json()["absent"])
        cer = self.c.post(
            "/v1/signing-custody",
            json={"custodians": ["a", "b"], "m": 2, "n": 2, "note": "paper"},
        )
        self.assertEqual(cer.status_code, 201)
        self.assertFalse(cer.get_json()["hsm"])
        self.assertFalse(cer.get_json()["status_after"]["hsm"])
        hops = self.c.get("/v1/stranger-graph?root_id=x&max_hops=2")
        self.assertEqual(hops.status_code, 200)


if __name__ == "__main__":
    unittest.main()
