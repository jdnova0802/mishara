"""Tests for Mishara three-product surface."""
from __future__ import annotations

import os
import tempfile
import unittest
from unittest import mock

_fd, _db = tempfile.mkstemp(suffix=".db")
os.close(_fd)
os.environ["MISHARA_DB_PATH"] = _db
os.environ["MISHARA_PAYMENTS"] = "dev"
os.environ["MISHARA_ALLOW_DEV_PAY"] = "1"
os.environ.pop("STRIPE_SECRET_KEY", None)

import mishara_app as app  # noqa: E402

FAKE_VELARU = {
    "user": {"classification": "VIOLATION", "reason": "No adverse action notice", "confidence": 0.91},
    "ai": {},
    "user_entry_hash": "testhash001abc",
    "user_signature": "sig",
    "user_timestamp": "2026-09-11T12:00:00Z",
    "verify_url": "https://velaru.xyz/verify",
    "permalink": "https://velaru.xyz/r/testhash001abc",
    "rfc3161_authority": "freetsa.org",
    "anchor_status": "published",
}


class MisharaProductsTest(unittest.TestCase):
    def setUp(self):
        app.PAYMENTS_MODE = "dev"
        app.DB_PATH = _db
        app.init_db()
        self.c = app.app.test_client()

    def test_products_json_has_three_skus(self):
        r = self.c.get("/products.json")
        self.assertEqual(r.status_code, 200)
        ids = [p["id"] for p in r.get_json()["products"]]
        self.assertEqual(ids, ["harm_receipt", "demand_pack", "advocate_bundle"])

    def test_health(self):
        r = self.c.get("/health")
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(body["service"], "mishara")
        self.assertEqual(body["products"], ["harm_receipt", "demand_pack", "advocate_bundle"])

    def test_home_and_about_render(self):
        self.assertEqual(self.c.get("/").status_code, 200)
        self.assertEqual(self.c.get("/about").status_code, 200)
        text = self.c.get("/").get_data(as_text=True)
        self.assertIn("Harm Receipt", text)
        self.assertIn("Demand Pack", text)
        self.assertIn("Advocate Bundle", text)

    def _submit(self):
        with mock.patch.object(app, "velaru_classify", return_value=(FAKE_VELARU, None)):
            with mock.patch.object(
                app, "plain_english_explanation", return_value="Here is what you should know."
            ):
                return self.c.post(
                    "/submit",
                    json={
                        "description": "Automated tenant screening denied my rental with no adverse action notice.",
                        "platform": "SafeRent Test",
                        "harm_type": "housing",
                        "incident_date": "2026-08-01",
                        "contribute_pattern": True,
                    },
                )

    def test_harm_receipt_submit(self):
        r = self._submit()
        self.assertEqual(r.status_code, 200, r.get_data(as_text=True))
        data = r.get_json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["product"]["id"], "harm_receipt")
        self.assertEqual(data["receipt"]["hash"], "testhash001abc")
        self.assertIn("verify_url", data["receipt"])
        self.assertEqual(self.c.get(f"/receipt/{data['receipt']['hash']}").status_code, 200)

    def test_demand_pack_dev_checkout_and_letter(self):
        receipt = self._submit().get_json()["receipt"]
        with mock.patch.object(app, "generate_demand_letter", return_value="DEMAND LETTER"):
            ch = self.c.post(
                "/checkout", json={"product_id": "demand_pack", "receipt_hash": receipt["hash"]}
            )
            self.assertEqual(ch.status_code, 200, ch.get_data(as_text=True))
            payload = ch.get_json()
            self.assertEqual(payload["mode"], "dev")
            token = payload["unlock_token"]
            page = self.c.get(f"/unlock/{token}")
            self.assertEqual(page.status_code, 200, page.get_data(as_text=True)[:400])
            self.assertIn("Demand Pack", page.get_data(as_text=True))
            fulfilled = self.c.post(
                f"/unlock/{token}",
                json={
                    "description": "Automated tenant screening denied my rental with no adverse action notice."
                },
                headers={"Accept": "application/json"},
            )
            self.assertEqual(fulfilled.status_code, 200, fulfilled.get_data(as_text=True))
            body = fulfilled.get_json()
            self.assertEqual(body["letter"], "DEMAND LETTER")
            self.assertNotIn("export", body)

    def test_advocate_bundle_export(self):
        receipt = self._submit().get_json()["receipt"]
        with mock.patch.object(app, "generate_demand_letter", return_value="DEMAND LETTER"):
            ch = self.c.post(
                "/checkout",
                json={"product_id": "advocate_bundle", "receipt_hash": receipt["hash"]},
            )
            token = ch.get_json()["unlock_token"]
            fulfilled = self.c.post(
                f"/unlock/{token}",
                json={
                    "description": "Automated tenant screening denied my rental with no adverse action notice.",
                    "email": "counsel@example.com",
                },
                headers={"Accept": "application/json"},
            )
            self.assertEqual(fulfilled.status_code, 200, fulfilled.get_data(as_text=True))
            body = fulfilled.get_json()
            self.assertIn("export", body)
            self.assertIn("export_txt", body)
            self.assertEqual(body["export"]["spec"], "mishara-advocate-export-v1")

    def test_paid_gate_on_demand_letter(self):
        r = self.c.post("/demand-letter", json={"unlock_token": "nope", "description": "x" * 40})
        self.assertEqual(r.status_code, 402)

    def test_denial_receipt_face(self):
        r = self.c.get("/denial-receipt")
        self.assertEqual(r.status_code, 200)
        html = r.get_data(as_text=True)
        self.assertIn("Denial Receipt", html)
        self.assertIn("Free", html)
        self.assertNotIn("DTCC", html)
        self.assertNotIn("SWIFT", html)
        sm = self.c.get("/sitemap.xml").get_data(as_text=True)
        self.assertIn("/denial-receipt", sm)
        llms = self.c.get("/llms.txt").get_data(as_text=True)
        self.assertIn("denial-receipt", llms)


if __name__ == "__main__":
    unittest.main()
