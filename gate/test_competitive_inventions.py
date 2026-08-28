"""Smoke tests for Aug 28 competitive-response inventions."""
from __future__ import annotations

import unittest

import app as gate_app


class CompetitiveInventionTests(unittest.TestCase):
    def setUp(self):
        gate_app.app.config["TESTING"] = True
        self.client = gate_app.app.test_client()

    def test_well_known_manifests(self):
        specs = {
            "/.well-known/halt-cemetery.json": "gate-halt-cemetery-v1",
            "/.well-known/cold-standby-mirror.json": "gate-cold-standby-mirror-v1",
            "/.well-known/renewal-day-throat.json": "gate-renewal-day-throat-v1",
            "/.well-known/ghost-renewal-snare.json": "gate-ghost-renewal-snare-v1",
            "/.well-known/refuse-ledger.json": "gate-refuse-ledger-v1",
            "/.well-known/override-impossibility.json": "gate-override-impossibility-v1",
            "/.well-known/bind-weather.json": "gate-bind-weather-v1",
        }
        for path, spec in specs.items():
            r = self.client.get(path)
            self.assertEqual(r.status_code, 200, path)
            self.assertEqual(r.get_json()["spec"], spec, path)

    def test_cold_standby_cannot_mint_live(self):
        r = self.client.get("/demo/pas/cold-standby-mirror?outage=1")
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertFalse(body["may_mint_live"])
        self.assertFalse(body["may_consume_ticket"])

    def test_override_impossibility_forged_paths(self):
        r = self.client.get("/demo/pas/override-impossibility?epoch_locked=1")
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertGreater(body["forged_count"], 0)
        self.assertEqual(body["real_count"], 1)

    def test_renewal_day_throat_chokes_stale_ticket(self):
        r = self.client.post(
            "/demo/pas/renewal-day-throat",
            json={
                "sticks": [
                    {
                        "job_id": "pc:RENEW-1",
                        "auto_renew": True,
                        "fresh_ticket_id": "t-old",
                        "prior_policy_ticket": "t-old",
                    }
                ]
            },
        )
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(body["verdict"], "RENEWAL_CHOKE")
        self.assertFalse(body["may_batch_stick"])

    def test_ghost_renewal_snare_haunts(self):
        r = self.client.post(
            "/demo/pas/ghost-renewal-snare",
            json={"auto_renew": True, "batch_renew": True, "skip_redeem": True},
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["verdict"], "HAUNTED")


if __name__ == "__main__":
    unittest.main()
