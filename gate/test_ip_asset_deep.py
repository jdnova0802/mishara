"""Smoke tests for IP Asset Deep batch (32 inventions)."""
from __future__ import annotations

import unittest

import app as gate_app
import ip_asset_deep as ip


class IPAssetDeepTests(unittest.TestCase):
    def setUp(self):
        gate_app.app.config["TESTING"] = True
        self.client = gate_app.app.test_client()

    def test_catalog(self):
        r = self.client.get("/.well-known/ip-asset-deep.json")
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(body["count"], 32)
        self.assertEqual(body["family"], "ip-asset-deep")
        self.assertEqual(body["tier"], "IP-S+")

    def test_steamboat_split(self):
        r = self.client.get("/.well-known/steamboat-willie-split.json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["tier"], "IP-S+")

    def test_bowie_bond_recurring_analog(self):
        r = self.client.post("/demo/pas/bowie-bond-securitization", json={"catalog_depth": 25})
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertIn("recurring_income_analog", body)

    def test_frand_sep_blocks_unfair(self):
        r = self.client.post(
            "/demo/pas/frand-sep-choke",
            json={"standard_essential": True, "frand_offered": False},
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["verdict"], "FRAND_CHOKE_DENY")

    def test_copyleft_contamination(self):
        r = self.client.post(
            "/demo/pas/copyleft-contamination-snare",
            json={"gpl_linked": True, "proprietary_ship": True},
        )
        self.assertEqual(r.status_code, 200)
        verdict = r.get_json()["verdict"]
        self.assertTrue("CONTAMIN" in verdict or "COPYLEFT" in verdict or verdict.endswith("_DENY"))

    def test_all_manifests_unique_spec(self):
        specs = set()
        for slug in ip.SLUGS:
            r = self.client.get(f"/.well-known/{ip.slug_to_kebab(slug)}.json")
            self.assertEqual(r.status_code, 200, slug)
            spec = r.get_json()["spec"]
            self.assertNotIn(spec, specs, slug)
            specs.add(spec)


if __name__ == "__main__":
    unittest.main()
