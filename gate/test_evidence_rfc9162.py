"""RFC 9162 domain separation — second-preimage class must fail."""
from __future__ import annotations

import hashlib
import unittest

from gate import evidence_log as evidence_log_mod


class Rfc9162DomainSeparationTests(unittest.TestCase):
    def test_internal_node_cannot_be_replayed_as_leaf(self):
        h0 = hashlib.sha256(b"leaf-a").hexdigest()
        h1 = hashlib.sha256(b"leaf-b").hexdigest()
        root2 = evidence_log_mod.merkle_root([h0, h1])

        left = evidence_log_mod.rfc9162_leaf_hash(bytes.fromhex(h0))
        right = evidence_log_mod.rfc9162_leaf_hash(bytes.fromhex(h1))
        internal = evidence_log_mod.node_hash(left, right)
        self.assertEqual(internal.hex(), root2)

        # Pre-RFC construction: a 1-leaf tree's root WAS the leaf bytes, so
        # merkle_root([root2]) == root2. Domain separation must break that.
        one = evidence_log_mod.merkle_root([internal.hex()])
        self.assertNotEqual(one, root2)
        self.assertNotEqual(one, internal.hex())

        proof = evidence_log_mod.inclusion_proof([h0, h1], 0)
        self.assertTrue(
            evidence_log_mod.verify_inclusion(
                leaf_hash=h0, root_hash=root2, proof=proof
            )
        )
        self.assertFalse(
            evidence_log_mod.verify_inclusion(
                leaf_hash=internal.hex(),
                root_hash=root2,
                proof={"index": 0, "siblings": []},
            )
        )

    def test_leaf_and_node_prefixes_differ(self):
        blob = b"\x01" + (b"x" * 32) + (b"y" * 32)
        as_leaf = evidence_log_mod.rfc9162_leaf_hash(blob)
        as_node = evidence_log_mod.node_hash(b"x" * 32, b"y" * 32)
        self.assertNotEqual(as_leaf, as_node)


if __name__ == "__main__":
    unittest.main()
