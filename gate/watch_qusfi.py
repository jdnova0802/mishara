#!/usr/bin/env python3
"""Watch the public SVO QUSFI PDF. Monthly publication. Stdlib only.

SVO updates the list in real time internally and publishes the PDF monthly
(https://content.naic.org/sites/default/files/svo-qusfi-faq.pdf Q.9).
Gate vendors the dated SHA-256. This script fetches the live PDF and fails
if the bytes moved — that is a new list, not a credit score.

  python3 gate/watch_qusfi.py
  python3 gate/watch_qusfi.py --url https://staspoprodcus01.blob.core.windows.net/svo/svo_qusfi_list.pdf

Exit 0 if the live hash matches the vendored current list.
Exit 2 if the hash moved or the fetch failed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data" / "qusfi_lists.json"
DEFAULT_URL = "https://staspoprodcus01.blob.core.windows.net/svo/svo_qusfi_list.pdf"


def vendored_current() -> dict:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    lists = payload.get("lists") or []
    if not lists:
        raise SystemExit("no lists in gate/data/qusfi_lists.json")
    return max(lists, key=lambda row: str(row.get("as_of") or ""))


def fetch_sha256(url: str, timeout: int = 60) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "gate-qusfi-watch/1", "Accept": "application/pdf"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return hashlib.sha256(resp.read()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Watch the public SVO QUSFI PDF hash")
    parser.add_argument("--url", default="", help="Override live PDF URL")
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args(argv)
    current = vendored_current()
    expected = (current.get("pdf_sha256") or "").strip().lower()
    url = (args.url or current.get("source_url") or DEFAULT_URL).strip()
    try:
        live = fetch_sha256(url, timeout=args.timeout)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print("FAIL fetch", url, exc, file=sys.stderr)
        return 2
    if live != expected:
        print(
            "FAIL qusfi pdf moved",
            {"as_of": current.get("as_of"), "expected": expected, "live": live, "url": url},
            file=sys.stderr,
        )
        return 2
    print(
        json.dumps(
            {
                "ok": True,
                "event": "hash_match",
                "as_of": current.get("as_of"),
                "pdf_sha256": live,
                "url": url,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
