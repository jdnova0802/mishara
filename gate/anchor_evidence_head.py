#!/usr/bin/env python3
"""Periodic OpenTimestamps anchor for Gate evidence-head.

Usage:
  # Stamp live production head (submit real hash to public calendars):
  python3 gate/anchor_evidence_head.py stamp-url --url https://gate.velaru.xyz

  # Upgrade pending proofs once calendars land in Bitcoin:
  python3 gate/anchor_evidence_head.py upgrade --tree-size N --root-hash HEX

  # Status:
  python3 gate/anchor_evidence_head.py status

Cron (example — every 6h stamp + upgrade):
  0 */6 * * * cd /app && python3 gate/anchor_evidence_head.py stamp-url && \\
    python3 -c "import json,ots_anchor; a=ots_anchor.latest_anchor(); \\
    ots_anchor.upgrade_proof(tree_size=a['tree_size'], root_hash=a['root_hash']) if a else None"
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import ots_anchor  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(ots_anchor.main())
