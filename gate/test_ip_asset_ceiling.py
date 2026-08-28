"""Smoke tests for IP Asset Ceiling batch (24 experimental inventions)."""
from __future__ import annotations

import unittest

import app as gate_app
import ip_asset_ceiling as ic


class IPAssetCeilingTests(unittest.TestCase):
    def setUp(self):
        gate_app.app.config["TESTING"] = True
        self.client = gate_app.app.test_client()

    def test_catalog(self):
        r = self.client.get("/.well-known/ip-asset-ceiling.json")
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(body["count"], 24)
        self.assertEqual(body["family"], "ip-asset-ceiling")
        self.assertEqual(body["tier"], "IP-X")

    def test_upside_ladder(self):
        r = self.client.get("/.well-known/ip-asset-ceiling-ladder.json")
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(body["spec"], "gate-ip-asset-ceiling-ladder-v1")
        self.assertGreaterEqual(len(body["rungs"]), 6)
        self.assertEqual(body["rungs"][1]["label"], "$300M start")

    def test_premium_bps_300m_illustrative(self):
        r = self.client.post(
            "/demo/pas/premium-bps-meter",
            json={
                "premium_volume_usd": 97_100_000_000,
                "bps": 31,
                "premium_meter_licensed": True,
            },
        )
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertAlmostEqual(body["illustrative_ceiling_usd"], 300_910_000, delta=1_000_000)

    def test_trillion_qic_step_ladder(self):
        r = self.client.post(
            "/demo/pas/trillion-qic-step-ladder",
            json={"laq": 1_000_000_000_000},
        )
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertGreater(body["illustrative_ceiling_usd"], 1_000_000_000)

    def test_agent_field_rcc_deny(self):
        r = self.client.post(
            "/demo/pas/agent-runtime-field-license",
            json={"licensed_field_b": True, "multi_spend_tickets": True},
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["verdict"], "RCC_REQUIRED_DENY")

    def test_all_manifests_unique_spec(self):
        specs = set()
        for slug in ic.SLUGS:
            r = self.client.get(f"/.well-known/{ic.slug_to_kebab(slug)}.json")
            self.assertEqual(r.status_code, 200, slug)
            spec = r.get_json()["spec"]
            self.assertNotIn(spec, specs, slug)
            specs.add(spec)


if __name__ == "__main__":
    unittest.main()
