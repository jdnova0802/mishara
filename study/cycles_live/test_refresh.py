"""Unit tests for the live-points refresher. Network is mocked."""

from __future__ import annotations

import io
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

import yaml

import refresh


MIN_CFG = {
    "user_agent": "test-agent",
    "sleep_seconds": 0,
    "points": [
        {
            "id": "1.6.mpv_annual_killings",
            "crest_id": "1.6",
            "label": "police killings",
            "source_url": "https://example.invalid/mpv",
            "fetch_method": "manual_flag",
            "fetcher": None,
            "last_known_value": 1365,
            "last_pulled_date": "2026-11-14",
            "threshold": 50,
            "threshold_mode": "abs",
        },
        {
            "id": "3.3.giss_annual_anomaly",
            "crest_id": "3.3",
            "label": "GISS",
            "source_url": "https://example.invalid/giss.csv",
            "fetch_method": "api",
            "fetcher": "giss_annual_jd",
            "last_known_value": 1.19,
            "last_pulled_date": "2026-11-14",
            "threshold": 0.10,
            "threshold_mode": "abs",
        },
    ],
}

GISS_OK = """Land-Ocean: Global Means
Year,Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec,J-D,D-N,DJF,MAM,JJA,SON
2024,1.25,1.43,1.39,1.32,1.16,1.23,1.20,1.30,1.21,1.34,1.29,1.26,1.28,1.29,1.35,1.29,1.25,1.28
2025,1.37,1.25,1.36,1.24,1.07,1.06,1.02,1.17,1.24,1.19,1.21,1.05,1.19,1.20,1.30,1.23,1.08,1.21
2026,1.08,1.23,1.30,1.16,1.13,1.18,1.24,1.42,1.39,1.55,***,***,***,***,1.12,1.20,1.28,***
"""

GISS_BROKEN = """not a giss file
foo,bar
"""


def _resp(text: str, status: int = 200, url: str = "https://example.invalid") -> MagicMock:
    r = MagicMock()
    r.status_code = status
    r.text = text
    r.content = text.encode()
    r.url = url
    r.headers = {"Content-Type": "text/csv"}
    return r


class ThresholdTests(unittest.TestCase):
    def test_abs_threshold(self):
        p = {"threshold": 2.0, "threshold_mode": "abs"}
        self.assertFalse(refresh.is_large(82.7, 83.5, p))
        self.assertTrue(refresh.is_large(82.7, 85.0, p))

    def test_none_old_is_not_large(self):
        self.assertFalse(refresh.is_large(None, 100, {"threshold": 1, "threshold_mode": "abs"}))


class FailLoudTests(unittest.TestCase):
    def test_giss_structure_change_raises(self):
        sess = MagicMock()
        sess.get.return_value = _resp(GISS_BROKEN)
        with self.assertRaises(refresh.FetchError):
            refresh.fetch_giss_annual_jd(sess, {"source_url": "https://example.invalid/giss.csv"})

    def test_giss_parses_complete_year_skips_stars(self):
        sess = MagicMock()
        sess.get.return_value = _resp(GISS_OK)
        got = refresh.fetch_giss_annual_jd(sess, {"source_url": "https://example.invalid/giss.csv"})
        self.assertEqual(got.as_of, "2025")
        self.assertAlmostEqual(got.value, 1.19)


class RunTests(unittest.TestCase):
    def test_failed_fetch_does_not_overwrite(self):
        with TemporaryDirectory() as td:
            path = Path(td) / "live_points.yaml"
            path.write_text(yaml.safe_dump(MIN_CFG, sort_keys=False), encoding="utf-8")
            sess = MagicMock()
            sess.get.return_value = _resp(GISS_BROKEN, status=200)
            with patch.object(refresh, "session_for", return_value=sess), patch("sys.stdout", io.StringIO()):
                code = refresh.main(["--config", str(path)])
            self.assertEqual(code, 1)
            saved = yaml.safe_load(path.read_text())
            giss = next(p for p in saved["points"] if p["id"] == "3.3.giss_annual_anomaly")
            self.assertEqual(giss["last_known_value"], 1.19)
            self.assertEqual(giss["last_pulled_date"], "2026-11-14")

    def test_dry_run_does_not_write_success(self):
        with TemporaryDirectory() as td:
            path = Path(td) / "live_points.yaml"
            path.write_text(yaml.safe_dump(MIN_CFG, sort_keys=False), encoding="utf-8")
            sess = MagicMock()
            sess.get.return_value = _resp(GISS_OK)
            buf = io.StringIO()
            with patch.object(refresh, "session_for", return_value=sess), patch("sys.stdout", buf):
                code = refresh.main(["--dry-run", "--config", str(path)])
            self.assertEqual(code, 0)
            self.assertIn("dry-run", buf.getvalue())
            saved = yaml.safe_load(path.read_text())
            giss = next(p for p in saved["points"] if p["id"] == "3.3.giss_annual_anomaly")
            self.assertEqual(giss["last_known_value"], 1.19)

    def test_success_updates_only_fetched_point(self):
        with TemporaryDirectory() as td:
            path = Path(td) / "live_points.yaml"
            path.write_text(yaml.safe_dump(MIN_CFG, sort_keys=False), encoding="utf-8")
            sess = MagicMock()
            sess.get.return_value = _resp(GISS_OK)
            with patch.object(refresh, "session_for", return_value=sess), patch("sys.stdout", io.StringIO()):
                code = refresh.main(["--config", str(path)])
            self.assertEqual(code, 0)
            saved = yaml.safe_load(path.read_text())
            manual = next(p for p in saved["points"] if p["id"] == "1.6.mpv_annual_killings")
            giss = next(p for p in saved["points"] if p["id"] == "3.3.giss_annual_anomaly")
            self.assertEqual(manual["last_known_value"], 1365)
            self.assertEqual(giss["last_known_value"], 1.19)
            self.assertEqual(giss["last_as_of"], "2025")

    def test_manual_flag_listed_not_fetched(self):
        sess = MagicMock()
        cfg = {"sleep_seconds": 0, "points": [MIN_CFG["points"][0]]}
        buf = io.StringIO()
        with patch.object(refresh, "session_for", return_value=sess), patch("sys.stdout", buf):
            code = refresh.run(cfg, dry_run=True, config_path=Path("/tmp/unused.yaml"))
        self.assertEqual(code, 0)
        sess.get.assert_not_called()
        self.assertIn("Needs manual check", buf.getvalue())
        self.assertIn("https://example.invalid/mpv", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
