"""QUSFI lookup, confirmation-channel HALT, Nacha Phase 2 stamp."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

os.environ.setdefault("GATE_DEV_MODE", "1")
os.environ.setdefault("GATE_SECRET_KEY", "test-secret")
os.environ["GATE_DB_PATH"] = os.path.join(tempfile.gettempdir(), "gate-test-qusfi.db")
os.environ.pop("RENDER_EXTERNAL_URL", None)
os.environ.pop("RENDER_EXTERNAL_HOSTNAME", None)

if os.path.exists(os.environ["GATE_DB_PATH"]):
    os.remove(os.environ["GATE_DB_PATH"])

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import app as app_mod  # noqa: E402
import mouths as mouths_mod  # noqa: E402
import qusfi  # noqa: E402


class QusfiTests(unittest.TestCase):
    def setUp(self):
        self.client = app_mod.app.test_client()

    def test_head_hashes_and_forbids_bank_score(self):
        r = self.client.get("/.well-known/qusfi.json")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data["spec"], "gate-qusfi-v1")
        self.assertEqual(data["current"]["as_of"], "2026-09-30")
        self.assertEqual(
            data["current"]["pdf_sha256"],
            "0b1f3503d12ae8899cb7966515cf5f33277781051d075104fa1cbfd48dd75d8d",
        )
        self.assertEqual(data["prior"]["as_of"], "2025-12-31")
        self.assertEqual(
            data["prior"]["pdf_sha256"],
            "d989ac5a588a69339ce8a8fb646b9a8b443b82535e8f341656d45bbdd12c6c69",
        )
        self.assertIn("not a general bank creditworthiness score", data["scope"].lower())
        self.assertFalse(data["confirmation"]["call_to_confirm_path"])
        self.assertIn("/v1/qusfi/diff", data["urls"]["diff"])
        self.assertEqual(data["clocks"]["lloyds_six_month_confirm"]["bulletin"], "Y5410")
        self.assertIn("not naic", data["clocks"]["lloyds_six_month_confirm"]["scope"].lower())
        self.assertNotIn("their_production", data)

    def test_ccb_off_current_on_prior(self):
        r = self.client.get("/v1/qusfi?aba=26014685")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertFalse(data["current"]["on_list"])
        self.assertTrue(data["prior"]["on_list"])
        self.assertIn("China Construction Bank", data["prior"]["institution"]["label"])
        self.assertEqual(
            data["claim"],
            "This issuer is off the current list, so the next evergreen/renewal cannot "
            "support surplus credit.",
        )
        self.assertIn("not automatically dead", data["not_a_claim"])

    def test_boc_and_abc_remain_on_both(self):
        for aba in (qusfi.BOC_NY_ABA, qusfi.ABC_NY_ABA):
            data = self.client.get(f"/v1/qusfi?aba={aba}").get_json()
            self.assertTrue(data["current"]["on_list"], aba)
            self.assertTrue(data["prior"]["on_list"], aba)

    def test_phone_and_email_halt_even_for_on_list_issuer(self):
        for channel in ("phone", "email_on_instrument", "voice", "call"):
            r = self.client.post(
                "/v1/qusfi/check",
                json={
                    "aba": qusfi.BOC_NY_ABA,
                    "confirmation_channel": channel,
                    "event": "renewal",
                },
            )
            body = r.get_json()
            self.assertEqual(body["word"], "HALT", channel)
            self.assertTrue(body["halt"], channel)
            self.assertFalse(body["call_to_confirm_path"])

    def test_mt760_renewal_halts_when_off_current_list(self):
        body = self.client.post(
            "/v1/qusfi/check",
            json={
                "aba": "26014685",
                "confirmation_channel": "advised_mt760_via_own_bank",
                "event": "renewal",
            },
        ).get_json()
        self.assertEqual(body["word"], "HALT")
        self.assertIn("next evergreen/renewal cannot support surplus credit", body["reason"])

    def test_grandfathered_existing_letter_is_hold_not_dead(self):
        body = self.client.post(
            "/v1/qusfi/check",
            json={
                "aba": "26014685",
                "confirmation_channel": "advised_mt760_via_own_bank",
                "event": "existing",
            },
        ).get_json()
        self.assertEqual(body["word"], "HOLD")
        self.assertFalse(body["halt"])
        self.assertIn("not automatically dead", body["not_a_claim"])

    def test_y5410_empty_confirm_halts_fal_not_surplus_credit(self):
        body = self.client.post(
            "/v1/qusfi/check",
            json={
                "aba": qusfi.BOC_NY_ABA,
                "confirmation_channel": "advised_mt760_via_own_bank",
                "event": "existing",
                "lloyds_fal": "yes",
                "as_of": "2026-10-27",
            },
        ).get_json()
        self.assertEqual(body["word"], "HALT")
        self.assertTrue(body["halt"])
        self.assertTrue(body["lloyds_y5410"]["applied"])
        self.assertFalse(body["lloyds_y5410"]["ok"])
        self.assertIn("Funds at Lloyd's", body["reason"])
        self.assertIn("not NAIC", body["not_a_claim_y5410"])
        skipped = self.client.post(
            "/v1/qusfi/check",
            json={
                "aba": qusfi.BOC_NY_ABA,
                "confirmation_channel": "advised_mt760_via_own_bank",
                "event": "existing",
            },
        ).get_json()
        self.assertEqual(skipped["word"], "CLEAR")
        self.assertFalse(skipped["lloyds_y5410"]["applied"])

    def test_y5410_fresh_confirm_clears_when_qusfi_clears(self):
        body = self.client.post(
            "/v1/qusfi/check",
            json={
                "aba": qusfi.BOC_NY_ABA,
                "confirmation_channel": "advised_mt760_via_own_bank",
                "event": "existing",
                "lloyds_fal": "yes",
                "issuing_bank_confirm_at": "2026-04-27",
                "as_of": "2026-10-27",
            },
        ).get_json()
        self.assertEqual(body["word"], "CLEAR")
        self.assertEqual(body["lloyds_y5410"]["due"], "2026-10-27")
        late = self.client.post(
            "/v1/qusfi/check",
            json={
                "aba": qusfi.BOC_NY_ABA,
                "confirmation_channel": "advised_mt760_via_own_bank",
                "event": "existing",
                "lloyds_fal": "yes",
                "issuing_bank_confirm_at": "2026-04-26",
                "as_of": "2026-10-27",
            },
        ).get_json()
        self.assertEqual(late["word"], "HALT")
        self.assertEqual(late["lloyds_y5410"]["due"], "2026-10-26")

    def test_diff_drops_ccb_and_keeps_boc(self):
        r = self.client.get("/v1/qusfi/diff?from=2025-12-31&to=2026-09-30")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        dropped_ids = [row["id"] for row in data["dropped"]]
        added_ids = [row["id"] for row in data["added"]]
        self.assertIn("26014685", dropped_ids)
        self.assertEqual(data["example"]["id"], "26014685")
        self.assertIn("next evergreen/renewal cannot support surplus credit", data["claim_when_dropped"])
        self.assertNotIn("26003269", dropped_ids)
        self.assertNotIn("133951245", dropped_ids)
        self.assertNotIn("26003269", added_ids)
        self.assertIn("not a credit rating", data["not_a_score"].lower())
        bad = self.client.get("/v1/qusfi/diff?from=1999-01-01")
        self.assertEqual(bad.status_code, 400)

    def test_no_qusfi_html_pitch_page(self):
        self.assertEqual(self.client.get("/qusfi").status_code, 404)

    def test_diligence_keeps_grandfather_and_refuses_call_to_confirm(self):
        html = self.client.get("/diligence").get_data(as_text=True).lower()
        self.assertIn("next evergreen/renewal cannot support surplus credit", html)
        self.assertIn("model 786", html)
        self.assertIn("y5410", html)
        self.assertIn("funds at lloyd", html)
        self.assertIn("not naic surplus credit", html)
        self.assertNotIn("call to confirm", html)
        self.assertNotIn('href="tel:', html)

    def test_nacha_phase2_practical_june_22(self):
        wk = self.client.get("/.well-known/nacha-false-pretenses.json").get_json()
        self.assertEqual(wk["phase2_rule_date"], "2026-06-19")
        self.assertEqual(wk["phase2_practical_effective"], "2026-06-22")
        fp = self.client.post(
            "/v1/nacha-false-pretenses",
            json={
                "role": "odfi",
                "false_pretenses_suspected": "yes",
                "who_what_payee_sealed": "no",
            },
        ).get_json()
        self.assertEqual(fp["word"], "NEVER")
        self.assertEqual(fp["phase2_practical_effective"], "2026-06-22")
        self.assertIn("Jun 22, 2026", mouths_mod.evaluate_nacha_false_pretenses.__doc__)


if __name__ == "__main__":
    unittest.main()
