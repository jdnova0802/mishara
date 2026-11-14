#!/usr/bin/env python3
"""Re-pull live splitters for docs/study/CYCLES_OF_CONTENTION.md.

Only points listed in live_points.yaml are touched. Historical crests are not.

  python refresh.py
  python refresh.py --dry-run
  python refresh.py --config /path/to/live_points.yaml
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urljoin

import requests
import yaml
from openpyxl import load_workbook

HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG = HERE / "live_points.yaml"
MONTHS = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}


class FetchError(RuntimeError):
    """Page/API structure changed, or the source refused a clean read."""


@dataclass
class FetchResult:
    value: float
    as_of: str
    display: str
    extra: str = ""


@dataclass
class Row:
    status: str
    point_id: str
    crest_id: str
    label: str
    old_value: Any
    old_date: Any
    new_value: Any
    new_date: Any
    large: bool
    detail: str
    result: FetchResult | None = None


def load_config(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict) or "points" not in data:
        raise FetchError(f"{path} is not a live_points config (missing points)")
    return data


def session_for(cfg: dict) -> requests.Session:
    s = requests.Session()
    s.headers["User-Agent"] = cfg.get(
        "user_agent",
        "CyclesLiveRefresh/0.1 (jdnova0802/mishara study map)",
    )
    s.headers["Accept"] = "*/*"
    return s


def require_ok(resp: requests.Response, what: str) -> None:
    if resp.status_code != 200:
        raise FetchError(f"{what}: HTTP {resp.status_code} from {resp.url}")


def fetch_giss_annual_jd(sess: requests.Session, point: dict) -> FetchResult:
    url = point["source_url"]
    resp = sess.get(url, timeout=30)
    require_ok(resp, "GISS")
    text = resp.text
    if "J-D" not in text:
        raise FetchError("GISS CSV has no J-D column — structure changed")
    reader = csv.reader(io.StringIO(text))
    header = None
    for row in reader:
        if row and "J-D" in row and "Year" in row:
            header = row
            break
    if header is None:
        raise FetchError("GISS CSV header missing Year / J-D — structure changed")
    jd = header.index("J-D")
    year_i = header.index("Year")
    last: tuple[int, float] | None = None
    for row in reader:
        if not row or not row[0].isdigit():
            continue
        cell = row[jd].strip()
        if cell in ("***", "", "NA"):
            continue
        last = (int(row[year_i]), float(cell))
    if last is None:
        raise FetchError("GISS CSV has no complete J-D year")
    year, val = last
    return FetchResult(val, f"{year}", f"{val:.2f}°C ({year} J-D)", extra="1951-1980 baseline")


def fetch_bls_weekly_earnings_ratio(sess: requests.Session, point: dict) -> FetchResult:
    women_id = "LEU0252881500"
    men_id = "LEU0252882400"
    payload = {"seriesid": [women_id, men_id]}
    resp = sess.post(
        "https://api.bls.gov/publicAPI/v2/timeseries/data/",
        json=payload,
        timeout=30,
    )
    require_ok(resp, "BLS")
    body = resp.json()
    if body.get("status") != "REQUEST_SUCCEEDED":
        raise FetchError(f"BLS status={body.get('status')!r} message={body.get('message')!r}")
    series = {s["seriesID"]: s.get("data") or [] for s in body.get("Results", {}).get("series", [])}
    if women_id not in series or men_id not in series:
        raise FetchError(f"BLS missing series. got={list(series)}")
    if not series[women_id] or not series[men_id]:
        raise FetchError("BLS returned empty series")
    w = series[women_id][0]
    m = series[men_id][0]
    if w.get("year") != m.get("year") or w.get("period") != m.get("period"):
        raise FetchError(f"BLS women/men periods mismatch: {w} vs {m}")
    wv, mv = float(w["value"]), float(m["value"])
    if mv == 0:
        raise FetchError("BLS men weekly earnings is 0")
    ratio = round(100.0 * wv / mv, 1)
    as_of = f"{w['year']} {w.get('periodName') or w.get('period')}"
    return FetchResult(ratio, as_of, f"{ratio}% ({as_of})", extra=f"women ${wv:.0f} / men ${mv:.0f}")


def fetch_eurostat_asylum_first(sess: requests.Session, point: dict) -> FetchResult:
    params = {
        "format": "JSON",
        "lang": "EN",
        "geo": "EU27_2020",
        "applicant": "FRST",
        "sex": "T",
        "age": "TOTAL",
        "citizen": "TOTAL",
        "lastTimePeriod": "8",
    }
    resp = sess.get(point["source_url"], params=params, timeout=45)
    require_ok(resp, "Eurostat")
    body = resp.json()
    dims = body.get("dimension") or {}
    if dims.get("applicant", {}).get("category", {}).get("index") != {"FRST": 0} and "FRST" not in (
        dims.get("applicant", {}).get("category", {}).get("index") or {}
    ):
        raise FetchError(f"Eurostat applicant dim is not FRST: {dims.get('applicant')}")
    times = list((dims.get("time") or {}).get("category", {}).get("index") or {})
    values = body.get("value") or {}
    if not times or not values:
        raise FetchError("Eurostat empty time/value — query or structure changed")
    # JSON-stat: one observation per time index in this filtered query
    pairs: list[tuple[str, float]] = []
    for i, year in enumerate(times):
        key = str(i)
        if key not in values:
            continue
        pairs.append((year, float(values[key])))
    if not pairs:
        raise FetchError("Eurostat had years but no numeric values")
    year, val = pairs[-1]
    return FetchResult(val, year, f"{int(val):,} first-time ({year})", extra="EU27_2020 FRST TOTAL")


def fetch_cdc_overdose_12mo(sess: requests.Session, point: dict) -> FetchResult:
    params = {
        "state": "US",
        "indicator": "Number of Drug Overdose Deaths",
        "$limit": "400",
        "$order": "year DESC",
    }
    resp = sess.get(point["source_url"], params=params, timeout=30)
    require_ok(resp, "CDC VSRR")
    rows = resp.json()
    if not isinstance(rows, list) or not rows:
        raise FetchError("CDC VSRR returned no rows")
    scored: list[tuple[int, int, dict]] = []
    for row in rows:
        if row.get("period") != "12 month-ending":
            continue
        if "data_value" not in row:
            continue
        month = MONTHS.get(row.get("month") or "")
        try:
            year = int(row["year"])
        except (KeyError, TypeError, ValueError):
            continue
        if month is None:
            continue
        scored.append((year, month, row))
    if not scored:
        raise FetchError("CDC VSRR: no 12-month-ending US rows with data_value")
    scored.sort(key=lambda t: (t[0], t[1]))
    year, month, row = scored[-1]
    val = float(row["data_value"])
    as_of = f"{year}-{month:02d}"
    return FetchResult(
        val,
        as_of,
        f"{int(val):,} (12-month-ending {row.get('month')} {year})",
        extra=f"complete={row.get('percent_complete')}",
    )


def fetch_wapo_fatal_shootings_year(sess: requests.Session, point: dict) -> FetchResult:
    resp = sess.get(point["source_url"], timeout=60)
    require_ok(resp, "WaPo Fatal Force")
    reader = csv.DictReader(io.StringIO(resp.text))
    if not reader.fieldnames or "date" not in reader.fieldnames:
        raise FetchError(f"WaPo CSV missing date column: {reader.fieldnames!r}")
    counts: dict[int, int] = {}
    for row in reader:
        d = (row.get("date") or "")[:10]
        if len(d) < 4 or not d[:4].isdigit():
            raise FetchError(f"WaPo CSV date unparseable: {row.get('date')!r}")
        year = int(d[:4])
        counts[year] = counts.get(year, 0) + 1
    if not counts:
        raise FetchError("WaPo CSV had no dated rows")
    latest = max(counts)
    year = latest
    if year == date.today().year and (year - 1) in counts:
        year = year - 1
    val = float(counts[year])
    return FetchResult(val, str(year), f"{int(val)} shootings ({year})", extra=f"csv_max_year={latest}")


def fetch_eeoc_table_e2c_receipts(sess: requests.Session, point: dict) -> FetchResult:
    listing = point["source_url"]
    resp = sess.get(listing, timeout=30)
    require_ok(resp, "EEOC listing")
    hrefs = [
        h.strip()
        for h in _hrefs(resp.text)
        if "Table_E2c" in h and h.lower().endswith(".xlsx")
    ]
    if not hrefs:
        raise FetchError(
            "EEOC listing has no Table_E2c .xlsx link — page structure changed. "
            f"See {listing}"
        )
    xlsx_url = urljoin(listing, hrefs[0].replace(" ", "%20"))
    xresp = sess.get(xlsx_url, timeout=30)
    require_ok(xresp, "EEOC E2c xlsx")
    if "spreadsheet" not in (xresp.headers.get("Content-Type") or "") and not xresp.content.startswith(b"PK"):
        raise FetchError(f"EEOC E2c did not return xlsx (type={xresp.headers.get('Content-Type')})")
    wb = load_workbook(io.BytesIO(xresp.content), data_only=True)
    ws = wb.active
    header = None
    receipts = None
    for row in ws.iter_rows(max_row=20, values_only=True):
        cells = list(row)
        if header is None and any(isinstance(c, str) and c.startswith("FY ") for c in cells):
            header = cells
        if cells and cells[0] == "Receipts":
            receipts = cells
            break
    if not header or not receipts:
        raise FetchError("EEOC E2c sheet missing FY header or Receipts row")
    pairs: list[tuple[str, float]] = []
    for h, v in zip(header, receipts):
        if not isinstance(h, str) or not h.startswith("FY "):
            continue
        if v is None:
            continue
        try:
            pairs.append((h, float(v)))
        except (TypeError, ValueError) as e:
            raise FetchError(f"EEOC Receipts cell for {h} is not numeric: {v!r}") from e
    if not pairs:
        raise FetchError("EEOC E2c header/receipts had no FY columns")
    fy, val = pairs[-1]
    return FetchResult(val, fy, f"{int(val):,} receipts ({fy})", extra=xlsx_url)


def _hrefs(html: str) -> list[str]:
    out: list[str] = []
    needle = "href="
    i = 0
    lower = html
    while True:
        j = lower.find(needle, i)
        if j < 0:
            break
        q = html[j + 5 : j + 6]
        if q not in ('"', "'"):
            i = j + 5
            continue
        k = html.find(q, j + 6)
        if k < 0:
            break
        out.append(html[j + 6 : k])
        i = k + 1
    return out


FETCHERS: dict[str, Callable[[requests.Session, dict], FetchResult]] = {
    "giss_annual_jd": fetch_giss_annual_jd,
    "bls_weekly_earnings_ratio": fetch_bls_weekly_earnings_ratio,
    "eurostat_asylum_first": fetch_eurostat_asylum_first,
    "cdc_overdose_12mo": fetch_cdc_overdose_12mo,
    "wapo_fatal_shootings_year": fetch_wapo_fatal_shootings_year,
    "eeoc_table_e2c_receipts": fetch_eeoc_table_e2c_receipts,
}


def is_large(old: Any, new: float, point: dict) -> bool:
    if old is None:
        return False
    try:
        old_f = float(old)
    except (TypeError, ValueError):
        return False
    delta = abs(new - old_f)
    mode = point.get("threshold_mode") or "abs"
    thr = float(point.get("threshold") or 0)
    if mode == "pct":
        if old_f == 0:
            return delta > 0
        return (delta / abs(old_f)) * 100.0 >= thr
    return delta >= thr


def fmt(v: Any) -> str:
    if v is None:
        return "—"
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    return str(v)


def render(rows: list[Row]) -> str:
    lines = [
        "# Cycles live pull",
        "",
        f"Run date: {date.today().isoformat()}",
        "",
        "| crest | id | label | old (date) | new (date) | large vs falsifier | status |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        old = f"{fmt(r.old_value)} ({r.old_date or '—'})"
        new = f"{fmt(r.new_value)} ({r.new_date or '—'})"
        flag = "YES" if r.large else "—"
        lines.append(
            f"| {r.crest_id} | `{r.point_id}` | {r.label} | {old} | {new} | {flag} | {r.status} |"
        )
    lines.append("")
    manuals = [r for r in rows if r.status == "manual_flag"]
    fails = [r for r in rows if r.status == "FAIL"]
    if manuals:
        lines.append("## Needs manual check")
        for r in manuals:
            lines.append(f"- `{r.point_id}` ({r.crest_id}) {r.label} — {r.detail}")
        lines.append("")
    if fails:
        lines.append("## Failed fetches (config not updated)")
        for r in fails:
            lines.append(f"- `{r.point_id}`: {r.detail}")
        lines.append("")
    return "\n".join(lines) + "\n"


def apply_updates(cfg: dict, rows: list[Row]) -> None:
    by_id = {p["id"]: p for p in cfg["points"]}
    today = date.today().isoformat()
    for r in rows:
        if r.status != "ok" or r.result is None:
            continue
        p = by_id[r.point_id]
        p["last_known_value"] = r.result.value
        p["last_pulled_date"] = today
        p["last_as_of"] = r.result.as_of
        p["last_display"] = r.result.display


def run(cfg: dict, *, dry_run: bool, config_path: Path) -> int:
    sess = session_for(cfg)
    sleep = float(cfg.get("sleep_seconds") or 0)
    rows: list[Row] = []
    exit_code = 0
    first = True
    for point in cfg["points"]:
        if not first:
            time.sleep(sleep)
        first = False
        method = point.get("fetch_method")
        pid = point["id"]
        if method == "manual_flag":
            rows.append(
                Row(
                    "manual_flag",
                    pid,
                    str(point["crest_id"]),
                    point["label"],
                    point.get("last_known_value"),
                    point.get("last_pulled_date"),
                    None,
                    None,
                    False,
                    point.get("source_url") or "",
                )
            )
            continue
        fetcher_name = point.get("fetcher")
        fn = FETCHERS.get(fetcher_name or "")
        if fn is None:
            rows.append(
                Row(
                    "FAIL",
                    pid,
                    str(point["crest_id"]),
                    point["label"],
                    point.get("last_known_value"),
                    point.get("last_pulled_date"),
                    None,
                    None,
                    False,
                    f"unknown fetcher {fetcher_name!r}",
                )
            )
            exit_code = 1
            continue
        try:
            result = fn(sess, point)
        except (FetchError, requests.RequestException, KeyError, ValueError, json.JSONDecodeError) as e:
            rows.append(
                Row(
                    "FAIL",
                    pid,
                    str(point["crest_id"]),
                    point["label"],
                    point.get("last_known_value"),
                    point.get("last_pulled_date"),
                    None,
                    None,
                    False,
                    str(e),
                )
            )
            exit_code = 1
            continue
        large = is_large(point.get("last_known_value"), result.value, point)
        rows.append(
            Row(
                "ok",
                pid,
                str(point["crest_id"]),
                point["label"],
                point.get("last_known_value"),
                point.get("last_pulled_date"),
                result.value,
                result.as_of,
                large,
                result.extra,
                result=result,
            )
        )
    report = render(rows)
    sys.stdout.write(report)
    if dry_run:
        sys.stdout.write("(dry-run: config not written)\n")
        return exit_code
    apply_updates(cfg, rows)
    with config_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False, allow_unicode=True)
    sys.stdout.write(f"wrote {config_path}\n")
    return exit_code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refresh live Cycles of Contention numbers.")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and diff; do not write the config.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args(argv)
    cfg = load_config(args.config)
    return run(cfg, dry_run=args.dry_run, config_path=args.config)


if __name__ == "__main__":
    raise SystemExit(main())
