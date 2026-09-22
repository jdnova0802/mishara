"""Append-only evidence seal — detect truncation / rewrite of the receipt log.

Each new receipt_hash is appended as one line:
  <seq> <receipt_hash> <sha256(prev_seal_line || receipt_hash)>

A stranger (or diligence eng) can recompute the seal chain and prove the log
only grew. Not cloud WORM — solo-max tamper evidence on local/persistent disk.
"""

from __future__ import annotations

import hashlib
import os
from typing import Any


SPEC = "gate-evidence-seal-v1"
GENESIS = "gate-evidence-seal-genesis"


def seal_path() -> str:
    return (
        os.getenv("GATE_EVIDENCE_SEAL_PATH", "").strip()
        or os.getenv("GATE_DB_PATH", "").strip().replace(".db", ".seal")
        or "/var/data/gate.seal"
    )


def _line_digest(prev_digest: str, receipt_hash: str) -> str:
    return hashlib.sha256(f"{prev_digest}:{receipt_hash}".encode("utf-8")).hexdigest()


def append_receipt_hash(receipt_hash: str) -> dict[str, Any] | None:
    h = (receipt_hash or "").strip()
    if not h:
        return None
    path = seal_path()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    prev = GENESIS
    seq = 0
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                parts = line.strip().split()
                if len(parts) >= 3:
                    seq = int(parts[0])
                    prev = parts[2]
    seq += 1
    digest = _line_digest(prev, h)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(f"{seq} {h} {digest}\n")
    return {"seq": seq, "receipt_hash": h, "seal_digest": digest, "path": path}


def verify_seal(path: str | None = None) -> dict[str, Any]:
    p = path or seal_path()
    if not os.path.isfile(p):
        return {
            "spec": SPEC,
            "ok": True,
            "empty": True,
            "size": 0,
            "path": p,
            "reason": "no_seal_file",
        }
    prev = GENESIS
    expected_seq = 0
    last_hash = None
    last_digest = None
    with open(p, "r", encoding="utf-8") as fh:
        for i, line in enumerate(fh, start=1):
            parts = line.strip().split()
            if len(parts) < 3:
                return {
                    "spec": SPEC,
                    "ok": False,
                    "empty": False,
                    "path": p,
                    "reason": "malformed_line",
                    "line": i,
                }
            try:
                seq = int(parts[0])
            except ValueError:
                return {
                    "spec": SPEC,
                    "ok": False,
                    "reason": "bad_seq",
                    "line": i,
                    "path": p,
                }
            receipt_hash, digest = parts[1], parts[2]
            expected_seq += 1
            if seq != expected_seq:
                return {
                    "spec": SPEC,
                    "ok": False,
                    "reason": "seq_gap_or_rewrite",
                    "line": i,
                    "expected_seq": expected_seq,
                    "got_seq": seq,
                    "path": p,
                }
            want = _line_digest(prev, receipt_hash)
            if digest != want:
                return {
                    "spec": SPEC,
                    "ok": False,
                    "reason": "seal_digest_mismatch",
                    "line": i,
                    "path": p,
                }
            prev = digest
            last_hash = receipt_hash
            last_digest = digest
    return {
        "spec": SPEC,
        "ok": True,
        "empty": expected_seq == 0,
        "size": expected_seq,
        "head_receipt_hash": last_hash,
        "head_seal_digest": last_digest,
        "path": p,
        "append_only": True,
    }
