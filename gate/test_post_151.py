"""Items 152–158, 161–162 — reversible playbooks through velocity breaker.

154/159/160 are relationship-blocked and are not built here.
153 records measurements and refuses to mint a proof.
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-post-151.db")
for key, name in (
    ("GATE_AUTO_RESPONSE_PATH", "auto.json"),
    ("GATE_CASE_PATH", "case.json"),
    ("GATE_VRS_PATH", "vrs.json"),
    ("GATE_ONTOLOGY_PATH", "ont.json"),
    ("GATE_REVOCATION_PATH", "rev.json"),
    ("GATE_BRIDGING_PATH", "br.json"),
    ("GATE_LIVE_CHANNEL_PATH", "lc.json"),
    ("GATE_POP_BREAKER_PATH", "pb.json"),
    ("GATE_ZKML_PATH", "zk.json"),
    ("GATE_EXPOSURE_BOND_PATH", "bond.json"),
):
    os.environ[key] = os.path.join(tempfile.gettempdir(), f"gate-test-post-151-{name}")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import auto_response  # noqa: E402
import bridging  # noqa: E402
import case_file  # noqa: E402
import live_channel  # noqa: E402
import ontology_links  # noqa: E402
import pop_breaker  # noqa: E402
import revocation  # noqa: E402
import vrs  # noqa: E402
import zkml_spike  # noqa: E402
from link_graph import ReceiptRecord  # noqa: E402


def _wipe():
    for key in (
        "GATE_AUTO_RESPONSE_PATH",
        "GATE_CASE_PATH",
        "GATE_VRS_PATH",
        "GATE_ONTOLOGY_PATH",
        "GATE_REVOCATION_PATH",
        "GATE_BRIDGING_PATH",
        "GATE_LIVE_CHANNEL_PATH",
        "GATE_POP_BREAKER_PATH",
        "GATE_ZKML_PATH",
        "GATE_EXPOSURE_BOND_PATH",
    ):
        path = os.environ[key]
        if os.path.exists(path):
            os.remove(path)


class PlaybookTests(unittest.TestCase):
    def setUp(self):
        _wipe()

    def test_refuses_irreversible_and_enqueues_triage(self):
        bad = auto_response.register(
            name="nuke",
            trigger_source="anomaly_flag",
            action="confirm",
            created_by="desk",
        )
        self.assertEqual(bad["error"], "action_not_reversible")
        pb = auto_response.register(
            name="queue hot flags",
            trigger_source="anomaly_flag",
            action="enqueue_triage",
            created_by="desk",
            trigger_condition={"deviation_sigma": 3.0},
        )
        self.assertTrue(pb["ok"])
        miss = auto_response.fire(
            playbook_id=pb["playbook_id"],
            trigger_ref_id="flag:1",
            payload={"deviation_sigma": 2.1},
        )
        self.assertEqual(miss["error"], "condition_not_met")
        hit = auto_response.fire(
            playbook_id=pb["playbook_id"],
            trigger_ref_id="flag:1",
            payload={"deviation_sigma": 3.2},
        )
        self.assertTrue(hit["ok"])
        self.assertTrue(hit["receipt_id"])
        self.assertIsNone(hit["overridden_by"])
        self.assertEqual(len(case_file.list_triage()), 1)
        ov = auto_response.override(execution_id=hit["execution_id"], overridden_by="analyst")
        self.assertEqual(ov["overridden_by"], "analyst")

    def test_temp_brake_requires_duration(self):
        miss = auto_response.register(
            name="brake",
            trigger_source="campaign_cluster",
            action="rate_limit_temporary",
            created_by="desk",
        )
        self.assertEqual(miss["error"], "max_duration_required")


class VrsTests(unittest.TestCase):
    def setUp(self):
        _wipe()

    def test_empty_directory_and_no_answer(self):
        cat = vrs.catalog()
        self.assertTrue(cat["empty_directory_is_valid"])
        self.assertTrue(cat["empty"])
        req = vrs.request_verify(requesting_receipt_id="r1", target_org_id="acme")
        self.assertEqual(req["response"], "no_answer")
        self.assertIsNone(req["routed_to"])
        vrs.register(operator_org_id="acme", responder_endpoint="https://acme.example/vrs")
        req2 = vrs.request_verify(requesting_receipt_id="r1", target_org_id="acme")
        ans = vrs.answer(request_id=req2["request_id"], response="confirmed")
        self.assertEqual(ans["response"], "confirmed")


class OntologyTests(unittest.TestCase):
    def setUp(self):
        _wipe()

    def test_property_match_edges(self):
        lt = ontology_links.register_link_type(
            name="shared_device_fingerprint",
            from_object_type_id="receipt",
            to_object_type_id="receipt",
            resolution="property_match",
            match_property="device_fingerprint",
            registered_by="desk",
        )
        self.assertTrue(lt["ok"])
        records = [
            ReceiptRecord(
                receipt_id="a",
                operator_id="op1",
                org_id="org",
                cohort_vertical="fintech",
                ingredients=[],
                co_signers=[],
                metrics={},
                created_at="2026-11-11T00:00:00+00:00",
                properties={"device_fingerprint": "dev-9"},
            ),
            ReceiptRecord(
                receipt_id="b",
                operator_id="op2",
                org_id="org",
                cohort_vertical="fintech",
                ingredients=[],
                co_signers=[],
                metrics={},
                created_at="2026-11-11T00:00:01+00:00",
                properties={"device_fingerprint": "dev-9"},
            ),
            ReceiptRecord(
                receipt_id="c",
                operator_id="op3",
                org_id="org",
                cohort_vertical="fintech",
                ingredients=[],
                co_signers=[],
                metrics={},
                created_at="2026-11-11T00:00:02+00:00",
                properties={"device_fingerprint": "other"},
            ),
        ]
        edges = ontology_links.match_edges(records, lt)
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]["edge_type"], "shared_device_fingerprint")


class RevocationTests(unittest.TestCase):
    def setUp(self):
        _wipe()

    def test_schema_without_check_logic(self):
        cat = revocation.catalog()
        self.assertFalse(cat["mechanism_executed"])
        reg = revocation.open_registry(issuer_org_id="nisaba", mechanism="bitstring_status_list")
        ent = revocation.track(
            registry_id=reg["registry_id"],
            attestation_type="transparency_log_entry",
            attestation_ref_id="tree_1",
        )
        self.assertEqual(ent["current_status"], "valid")
        changed = revocation.set_status(entry_id=ent["entry_id"], current_status="revoked")
        self.assertEqual(changed["current_status"], "revoked")
        self.assertFalse(revocation.lookup(attestation_ref_id="tree_1")["mechanism_executed"])


class BridgingTests(unittest.TestCase):
    def setUp(self):
        _wipe()

    def test_dormant_until_second_org(self):
        bridging.rate(flag_id="flag:1", reviewer_org_id="org_a", rating="confirmed")
        one = bridging.score(flag_id="flag:1")
        self.assertTrue(one["dormant"])
        self.assertIsNone(one["helpfulness_factor"])
        bridging.rate(flag_id="flag:1", reviewer_org_id="org_b", rating="false_positive")
        two = bridging.score(flag_id="flag:1")
        self.assertFalse(two["dormant"])
        self.assertIn("org_a", two["org_polarity_factors"])


class LiveChannelTests(unittest.TestCase):
    def setUp(self):
        _wipe()

    def test_gate_requires_passed_challenge(self):
        denied = live_channel.issue_challenge(
            claimed_identity_ref="ceo",
            channel="voice_call",
        )
        self.assertEqual(denied["error"], "identity_not_on_file")
        live_channel.register_contact(
            claimed_identity_ref="ceo",
            callback="+15550100",
            legal_person="Hospital Corp",
        )
        ch = live_channel.issue_challenge(claimed_identity_ref="ceo", channel="voice_call")
        blocked = live_channel.gate_instruction(
            challenge_id=ch["challenge_id"],
            instruction_type="wire_transfer",
            amount="4800000",
        )
        self.assertEqual(blocked["error"], "passed_challenge_required")
        bad = live_channel.respond(challenge_id=ch["challenge_id"], nonce="nope")
        self.assertEqual(bad["error"], "nonce_mismatch")
        ok = live_channel.respond(challenge_id=ch["challenge_id"], nonce=ch["challenge_nonce"])
        self.assertTrue(ok["response_verified"])
        media = live_channel.gate_instruction(
            challenge_id=ch["challenge_id"],
            instruction_type="wire_transfer",
            amount="4800000",
            media_evidence_claimed=True,
        )
        self.assertEqual(media["error"], "media_is_not_evidence")
        thin = live_channel.gate_instruction(
            challenge_id=ch["challenge_id"],
            instruction_type="wire_transfer",
            amount="4800000",
        )
        self.assertEqual(thin.get("error"), "underbonded")
        import exposure_bond

        bond = exposure_bond.post(legal_person="Hospital Corp", posted="4800000", covers_ref=ch["challenge_id"])
        gated = live_channel.gate_instruction(
            challenge_id=ch["challenge_id"],
            instruction_type="wire_transfer",
            amount="4800000",
            bond_id=bond["bond_id"],
        )
        self.assertTrue(gated["ok"])


class PopBreakerTests(unittest.TestCase):
    def setUp(self):
        _wipe()

    def test_level_3_needs_named_resume(self):
        th = pop_breaker.set_threshold(
            metric="anomaly_flags_per_minute",
            scope="global",
            level_1_threshold=2,
            level_1_pause_ms=1000,
            level_2_threshold=4,
            level_2_pause_ms=2000,
            level_3_threshold=6,
        )
        now = datetime(2026, 11, 11, 12, 0, tzinfo=timezone.utc)
        ticks = [
            {"metric": "anomaly_flags_per_minute", "at": (now - timedelta(seconds=10)).isoformat()}
            for _ in range(6)
        ]
        ev = pop_breaker.evaluate(ticks, threshold_id=th["threshold_id"], now=now)
        self.assertEqual(ev["level"], 3)
        self.assertIsNone(ev["paused_until"])
        auto = pop_breaker.resume(event_id=ev["event_id"], resumed_by="")
        self.assertEqual(auto["error"], "resumed_by_required")
        human = pop_breaker.resume(event_id=ev["event_id"], resumed_by="desk")
        self.assertEqual(human["resumed_by"], "desk")


class ZkmlTests(unittest.TestCase):
    def setUp(self):
        _wipe()

    def test_spike_refuses_unmeasured_proof(self):
        cat = zkml_spike.catalog()
        self.assertFalse(cat["proof_generation_shipped"])
        miss = zkml_spike.record_measurement(
            classifier_model_id="atlas-t0043",
            proof_generation_time_ms=None,
            output_drift=None,
            gpu_acceleration_cleared=None,
        )
        self.assertEqual(miss["error"], "three_numbers_required")
        logged = zkml_spike.record_measurement(
            classifier_model_id="atlas-t0043",
            proof_generation_time_ms=12000,
            output_drift=0.04,
            gpu_acceleration_cleared=False,
        )
        self.assertTrue(logged["ok"])
        self.assertFalse(logged["ships_prover"])
        proof = zkml_spike.attach_proof(receipt_id="r1", classifier_model_id="atlas-t0043")
        self.assertEqual(proof["error"], "prover_not_shipped")


class ApiSmoke(unittest.TestCase):
    def setUp(self):
        _wipe()
        self.c = app_mod.app.test_client()

    def test_empty_vrs_and_zkml_proof_409(self):
        empty = self.c.get("/v1/vrs")
        self.assertEqual(empty.status_code, 200)
        self.assertTrue(empty.get_json()["empty_directory_is_valid"])
        proof = self.c.post("/v1/zkml/proof", json={"receipt_id": "r1", "classifier_model_id": "m"})
        self.assertEqual(proof.status_code, 409)
        spec = self.c.get("/openapi.full.json")
        paths = spec.get_json()["paths"]
        self.assertIn("/v1/playbooks", paths)
        self.assertIn("/v1/live-channel", paths)


if __name__ == "__main__":
    unittest.main()
