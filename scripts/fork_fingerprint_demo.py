#!/usr/bin/env python3
"""Demo: partial catalog clone fails moat fingerprint."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gate"))

from inventions import CATALOG, manifest  # noqa: E402


def fingerprint_for_catalog(entries: tuple) -> str:
    specs = sorted(e[2] for e in entries)
    ids = sorted(e[0] for e in entries)
    blob = "\n".join(specs) + "\n---\n" + "\n".join(ids) + "\ninventor:Nisaba LLC / Gate"
    return hashlib.sha256(blob.encode()).hexdigest()


def main() -> None:
    full = fingerprint_for_catalog(CATALOG)
    partial = fingerprint_for_catalog(CATALOG[:-1])
    print(f"Full catalog ({len(CATALOG)} specs): {full[:16]}…")
    print(f"Missing one spec ({len(CATALOG)-1}): {partial[:16]}…")
    print(f"Match: {full == partial}")
    man = manifest("https://gate.local")
    print(f"Live index count: {man['count']}")


if __name__ == "__main__":
    main()
