"""Smoke tests for Civilizational Deep batch 4 (32 inventions)."""
from __future__ import annotations

import unittest

import app as gate_app
import civilizational_deep as civ


class CivilizationalDeepTests(unittest.TestCase):
    def setUp(self):
        gate_app.app.config["TESTING"] = True
        self.client = gate_app.app.test_client()

    def test_catalog_manifest(self):
        r = self.client.get("/.well-known/civilizational-deep.json")
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(body["count"], 32)
        self.assertEqual(len(body["slugs"]), 32)
        self.assertEqual(body["spec"], "gate-civilizational-deep-catalog-v1")

    def test_all_well_known_manifests(self):
        for slug in civ.SLUGS:
            kebab = civ.slug_to_kebab(slug)
            path = f"/.well-known/{kebab}.json"
            r = self.client.get(path)
            self.assertEqual(r.status_code, 200, path)
            body = r.get_json()
            self.assertEqual(body["spec"], civ.manifest("", slug)["spec"], path)
            self.assertEqual(body["tier"], "S+")
            self.assertEqual(body["family"], "civilizational-deep")

    def test_pal_lockout(self):
        r = self.client.post(
            "/demo/pas/pal-limited-try",
            json={"override_tries": 99, "try_limit": 3},
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["verdict"], "PAL_LOCKOUT")

    def test_cap_partition_deny(self):
        r = self.client.post(
            "/demo/pas/cap-partition-deny",
            json={"partitioned": True, "allow_bind": True},
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["verdict"], "PARTITION_DENY")

    def test_asilomar_moratorium_sacred(self):
        r = self.client.post(
            "/demo/pas/asilomar-bind-moratorium",
            json={"mass_class": "sacred", "containment_proven": False},
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["verdict"], "MORATORIUM_DEFER")

    def test_von_neumann_replication_deny(self):
        r = self.client.post(
            "/demo/pas/von-neumann-replication-gate",
            json={"self_replicate": True, "attested_exit": False},
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["verdict"], "REPLICATION_DENY")

    def test_no_duplicate_slugs_in_registry(self):
        self.assertEqual(len(civ.SLUGS), len(set(civ.SLUGS)))
        self.assertEqual(set(civ.REGISTRY.keys()), set(civ.SLUGS))


if __name__ == "__main__":
    unittest.main()
