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


class InstitutionalTwistTests(unittest.TestCase):
    def setUp(self):
        gate_app.app.config["TESTING"] = True
        self.client = gate_app.app.test_client()

    def test_institutional_manifests(self):
        specs = {
            "/.well-known/exhibit-d-snare.json": "gate-exhibit-d-snare-v1",
            "/.well-known/protracted-outage-order.json": "gate-protracted-outage-order-v1",
            "/.well-known/black-box-epoch.json": "gate-black-box-epoch-v1",
            "/.well-known/mariana-pause-latch.json": "gate-mariana-pause-latch-v1",
            "/.well-known/nss-finality-stamp.json": "gate-nss-finality-stamp-v1",
            "/.well-known/agora-atomic-bind.json": "gate-agora-atomic-bind-v1",
            "/.well-known/ambest-shutdown-seat.json": "gate-ambest-shutdown-seat-v1",
        }
        for path, spec in specs.items():
            r = self.client.get(path)
            self.assertEqual(r.status_code, 200, path)
            body = r.get_json()
            self.assertEqual(body["spec"], spec, path)
            self.assertIn("real_institution", body)

    def test_black_box_rejects_admin(self):
        r = self.client.post(
            "/demo/pas/black-box-epoch/withdraw",
            json={"impostor_admin": True},
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["verdict"], "DENIED")

    def test_mariana_pause_no_self_unpause(self):
        r = self.client.post(
            "/demo/pas/mariana-pause-latch",
            json={"paused": True, "self_unpause_attempt": True},
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["verdict"], "PAUSE_STICKS")

    def test_exhibit_d_haunts_empty_program(self):
        r = self.client.post(
            "/demo/pas/exhibit-d-snare",
            json={"ais_program_claimed": True},
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["verdict"], "EXAMINER_HAUNTED")


class STierInventionTests(unittest.TestCase):
    def setUp(self):
        gate_app.app.config["TESTING"] = True
        self.client = gate_app.app.test_client()

    def test_s_tier_manifests(self):
        specs = {
            "/.well-known/algedonic-relay.json": "gate-algedonic-relay-v1",
            "/.well-known/smpag-may-quorum.json": "gate-smpag-may-quorum-v1",
            "/.well-known/iaea-acquisition-path.json": "gate-iaea-acquisition-path-v1",
            "/.well-known/doomsday-bind-hand.json": "gate-doomsday-bind-hand-v1",
            "/.well-known/long-now-chime.json": "gate-long-now-chime-v1",
            "/.well-known/dark-forest-restraint.json": "gate-dark-forest-restraint-v1",
            "/.well-known/great-filter-gate.json": "gate-great-filter-gate-v1",
            "/.well-known/psychohistory-seldon-line.json": "gate-psychohistory-seldon-line-v1",
            "/.well-known/sophon-lock.json": "gate-sophon-lock-v1",
            "/.well-known/who-shadow-bind-report.json": "gate-who-shadow-bind-report-v1",
        }
        for path, spec in specs.items():
            r = self.client.get(path)
            self.assertEqual(r.status_code, 200, path)
            body = r.get_json()
            self.assertEqual(body["spec"], spec, path)
            self.assertEqual(body["tier"], "S", path)

    def test_sophon_lock_rejects_client_theater(self):
        r = self.client.post(
            "/demo/pas/sophon-lock",
            json={"client_proof_only": True, "server_redeem_ok": False},
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["verdict"], "PROTON_LOCK")

    def test_smpag_quorum_missing_on_sacred(self):
        r = self.client.post(
            "/demo/pas/smpag-may-quorum",
            json={"mass_class": "sacred", "single_desk_strike": True},
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["verdict"], "SMPAG_QUORUM_MISSING")

    def test_dark_forest_broadcast_choke(self):
        r = self.client.post(
            "/demo/pas/dark-forest-restraint",
            json={"broadcast_bind_intent": True, "server_redeem_proved": False},
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["verdict"], "DARK_FOREST_BROADCAST")

    def test_doomsday_hand_moves_on_ghost(self):
        r = self.client.post(
            "/demo/pas/doomsday-bind-hand",
            json={"ghost_events": 3, "restraint_proved": 0},
        )
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertLess(body["bind_hand_seconds_to_midnight"], body["baseline_2026_seconds"])


if __name__ == "__main__":
    unittest.main()
