"""Gate primary chrome must not mutate across stranger surfaces."""
from __future__ import annotations

import re
import unittest

from app import app


PRIMARY = [
    "Bind Room",
    "Faces",
    "Weld",
    "Live",
    "Fees",
    "Pricing",
    "Verify",
    "Trust",
]


class GateNavContinuityTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_primary_nav_stable_across_money_surfaces(self):
        for path in ("/", "/bind-room", "/diligence", "/refusal", "/faces", "/pricing", "/trust", "/start"):
            with self.subTest(path=path):
                r = self.client.get(path)
                self.assertEqual(r.status_code, 200, path)
                m = re.search(br'class="nav-links">([\s\S]*?)</div>', r.data)
                self.assertIsNotNone(m, path)
                labels = [a.decode() for a in re.findall(br">([^<]+)</a>", m.group(1))]
                primary = labels[:-1]
                cta = labels[-1]
                self.assertEqual(primary, PRIMARY, f"{path} -> {labels}")
                self.assertTrue(cta.startswith("Bind Room ·"), labels)
                self.assertFalse(cta.startswith("Book ·"), labels)


if __name__ == "__main__":
    unittest.main()
