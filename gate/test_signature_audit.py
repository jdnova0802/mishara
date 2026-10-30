"""Receipt signature audit and the hybrid signer. Run from gate/."""
from __future__ import annotations

import base64
import os
import sys
import tempfile
import unittest
import uuid

from cryptography import x509
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(
    tempfile.gettempdir(), f"gate-sig-audit-{uuid.uuid4().hex}.db"
)

_priv = Ed25519PrivateKey.generate()
os.environ["GATE_RECEIPT_PRIVATE_KEY"] = base64.b64encode(
    _priv.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
).decode("ascii")
os.environ["GATE_RECEIPT_PUBLIC_KEY"] = base64.b64encode(
    _priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
).decode("ascii")
os.environ.pop("GATE_RECEIPT_ML_DSA_SEED", None)
os.environ.pop("GATE_RECEIPT_CA_PRIVATE_KEY", None)

import app as gate_app  # noqa: E402
import prefinality  # noqa: E402
import receipt as receipt_mod  # noqa: E402
import signature_audit  # noqa: E402


def _raw_b64(key: Ed25519PrivateKey) -> str:
    return base64.b64encode(
        key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    ).decode("ascii")


class SignatureAuditTests(unittest.TestCase):
    def tearDown(self):
        os.environ.pop("GATE_RECEIPT_ML_DSA_SEED", None)
        os.environ.pop("GATE_RECEIPT_CA_PRIVATE_KEY", None)

    def test_public_audit_does_not_claim_quantum_safe(self):
        gate_app.app.config["TESTING"] = True
        client = gate_app.app.test_client()
        response = client.get("/.well-known/signature-audit.json")
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["spec"], "gate-signature-audit-v1")
        self.assertFalse(body["live"]["quantum_safe"])
        self.assertEqual(body["live"]["signature"], "Ed25519")
        self.assertFalse(body["live"]["ml_dsa"])
        self.assertFalse(body["live"]["certificate_chain"])
        self.assertIn("draft-stone-aivs-01", body["compared_to"])
        page = client.get("/signature")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"not quantum-safe", page.data)

    def test_ed25519_only_receipt_still_verifies(self):
        issued = receipt_mod.issue_receipt(
            event_id="evt-ed",
            fuse_id="fuse",
            job_id=None,
            decision="NO_GO",
            acted=False,
            verify_url=None,
            created_at="2026-10-30T13:00:00Z",
            hop=None,
            prev_receipt_hash=None,
        )
        self.assertNotIn("receipt_signature_ml_dsa", issued)
        self.assertTrue(
            signature_audit.verify_receipt_signatures(
                receipt_hash=issued["receipt_hash"],
                signature_b64=issued["receipt_signature"],
            )
        )

    def test_hybrid_verifies_and_rejects_a_tampered_second_signature(self):
        from cryptography.hazmat.primitives.asymmetric.mldsa import MLDSA65PrivateKey

        seed = MLDSA65PrivateKey.generate().private_bytes_raw()
        os.environ["GATE_RECEIPT_ML_DSA_SEED"] = base64.b64encode(seed).decode("ascii")
        issued = receipt_mod.issue_receipt(
            event_id="evt-hy",
            fuse_id="fuse",
            job_id=None,
            decision="NO_GO",
            acted=False,
            verify_url=None,
            created_at="2026-10-30T13:00:00Z",
            hop=None,
            prev_receipt_hash=None,
        )
        second = issued["receipt_signature_ml_dsa"]
        self.assertTrue(
            signature_audit.verify_receipt_signatures(
                receipt_hash=issued["receipt_hash"],
                signature_b64=issued["receipt_signature"],
                ml_dsa_b64=second,
            )
        )
        self.assertFalse(
            signature_audit.verify_receipt_signatures(
                receipt_hash=issued["receipt_hash"],
                signature_b64=issued["receipt_signature"],
                ml_dsa_b64=base64.b64encode(b"not-a-signature").decode("ascii"),
            )
        )
        body = signature_audit.publish()
        self.assertTrue(body["live"]["ml_dsa"])
        self.assertFalse(body["live"]["quantum_safe"])

    def test_identity_cert_binds_the_receipt_key(self):
        os.environ["GATE_RECEIPT_CA_PRIVATE_KEY"] = _raw_b64(Ed25519PrivateKey.generate())
        chain = signature_audit.certificate_chain_der()
        self.assertEqual(len(chain), 2)
        leaf = x509.load_der_x509_certificate(chain[0])
        identity = x509.load_der_x509_certificate(chain[1])
        self.assertEqual(leaf.subject.rfc4514_string(), "CN=gate.velaru.xyz")
        self.assertEqual(leaf.issuer, identity.subject)
        self.assertEqual(
            leaf.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw),
            receipt_mod._ed25519_public_key_bytes(),
        )
        jwks = prefinality.jwks()
        prod = next(key for key in jwks["keys"] if key.get("gate_key_class") != "demo")
        self.assertEqual(len(prod["x5c"]), 2)
        audit = signature_audit.publish()
        self.assertTrue(audit["live"]["certificate_chain"])
        self.assertFalse(audit["live"]["quantum_safe"])


if __name__ == "__main__":
    unittest.main()
