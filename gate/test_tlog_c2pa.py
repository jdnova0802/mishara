"""Items 150 / 151 — RFC 9162 tlog objects + C2PA soft nulls."""
from __future__ import annotations

import hashlib
import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-tlog.db")
os.environ["GATE_TLOG_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-tlog.json")
os.environ["GATE_MEDIA_PROVENANCE_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-c2pa.json")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import media_provenance  # noqa: E402
import tlog  # noqa: E402


def _h(n: str) -> str:
    return hashlib.sha256(n.encode()).hexdigest()


class TlogTests(unittest.TestCase):
    def setUp(self):
        path = os.environ["GATE_TLOG_PATH"]
        if os.path.exists(path):
            os.remove(path)

    def test_inclusion_consistency_and_outside_gossip(self):
        a, b, c = _h("a"), _h("b"), _h("c")
        old = tlog.snapshot(receipt_hashes=[a, b])
        new = tlog.snapshot(receipt_hashes=[a, b, c])
        inc = tlog.prove_inclusion(tree_id=old["tree_id"], receipt_id=a)
        self.assertTrue(inc["verified"])
        missing = tlog.prove_inclusion(tree_id=old["tree_id"], receipt_id=c)
        self.assertEqual(missing["error"], "leaf_not_in_tree")
        con = tlog.prove_consistency(old_tree_id=old["tree_id"], new_tree_id=new["tree_id"])
        self.assertTrue(con["verified"])
        self.assertTrue(con["prefix"])
        mirror = tlog.gossip(
            tree_id=old["tree_id"],
            observed_root_hash=old["root_hash"],
            observed_by="Nisaba ops",
        )
        self.assertEqual(mirror["error"], "outside_party_required")
        split = tlog.gossip(
            tree_id=old["tree_id"],
            observed_root_hash=_h("other-root"),
            observed_by="isac-partner",
        )
        self.assertFalse(split["matches_published_root"])


class C2paTests(unittest.TestCase):
    def setUp(self):
        path = os.environ["GATE_MEDIA_PROVENANCE_PATH"]
        if os.path.exists(path):
            os.remove(path)

    def test_nulls_without_manifest(self):
        rec = media_provenance.check(receipt_id="r1", media_hash=_h("img"))
        self.assertTrue(rec["ok"])
        self.assertFalse(rec["c2pa_manifest_present"])
        self.assertIsNone(rec["c2pa_signature_valid"])
        self.assertIsNone(rec["hard_binding_intact"])
        present = media_provenance.check(
            receipt_id="r1",
            media_hash=_h("img"),
            c2pa_manifest_present=True,
            c2pa_signature_valid=True,
            hard_binding_intact=False,
        )
        self.assertTrue(present["c2pa_manifest_present"])
        self.assertTrue(present["c2pa_signature_valid"])
        self.assertFalse(present["hard_binding_intact"])


class FlaskTests(unittest.TestCase):
    def setUp(self):
        for key in ("GATE_TLOG_PATH", "GATE_MEDIA_PROVENANCE_PATH"):
            path = os.environ[key]
            if os.path.exists(path):
                os.remove(path)
        self.client = app_mod.app.test_client()

    def test_page(self):
        page = self.client.get("/tlog")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"RFC 9162", page.data)
        posted = self.client.post("/v1/media-provenance", json={"receipt_id": "r", "media_hash": _h("x")})
        self.assertEqual(posted.status_code, 201)
        self.assertIsNone(posted.get_json()["c2pa_signature_valid"])


if __name__ == "__main__":
    unittest.main()
