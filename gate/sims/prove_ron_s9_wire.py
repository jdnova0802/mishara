#!/usr/bin/env python3
"""Prove S8↔S9 wire: hostile watch session vs local appearance as separate paths."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gate.sims import mouth_watch as mw  # noqa: E402
from gate.sims import ron_attest_refuse as ron  # noqa: E402
from gate.sims.lab_invariant import assert_all_receipts_lab  # noqa: E402
from gate.sims.verify_http import stranger_fetch, stranger_verify  # noqa: E402


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> None:
    ron.reset()
    mw.reset()

    # Baseline: local synthetic REFUSE — not a threat object
    s0 = ron.open_session(
        signatory_id="sig-0",
        doc_hash="doc-0",
        appearance="synthetic_suspect",
    )
    a0 = ron.attest(s0["session_id"])
    expect(a0["decision"] == "REFUSE", f"a0 {a0}")
    expect(a0["reason_code"] == "appearance_synthetic_suspect", f"a0 reason {a0}")
    expect(a0["receipt_class"] == "clearance", "a0 class")
    expect(a0["watch_block"] is False, "a0 no watch")
    expect(a0["threat_receipt_id"] is None, "a0 no threat")

    # Scenario B: session appearance live, S9 watch hostile → REFUSE + linked threat
    s1 = ron.open_session(
        signatory_id="sig-1",
        doc_hash="doc-1",
        appearance="live",
    )
    blocked = ron.attest(
        s1["session_id"],
        expected_doc_hash="doc-1",
        watch_session={
            "appearance": "synthetic_suspect",
            "device_trust": "known",
            "network_risk": "low",
        },
    )
    expect(blocked["decision"] == "REFUSE", f"blocked {blocked}")
    expect(blocked["reason_code"] == "watch_blocked", f"blocked reason {blocked}")
    expect(blocked["watch_block"] is True, "blocked watch_block")
    expect(blocked["threat_class"] == "session_integrity", f"blocked class {blocked}")
    tid = blocked["threat_receipt_id"]
    expect(tid is not None, "blocked threat id")
    threat = mw.get_receipt(tid)
    expect(threat["receipt_class"] == "threat", "linked threat")
    expect(threat["threat_class"] == "session_integrity", "threat kind")

    # deny-this-actus only: same session, clean watch → ALLOW
    after = ron.attest(
        s1["session_id"],
        expected_doc_hash="doc-1",
        watch_session={
            "appearance": "live",
            "device_trust": "known",
            "network_risk": "low",
        },
    )
    expect(after["decision"] == "ALLOW", f"after {after}")
    expect(after["reason_code"] == "attested", "after attested")
    expect(after["threat_receipt_id"] is None, "after no threat")

    with stranger_verify() as srv:
        http_refuse = stranger_fetch(srv.base_url, blocked["receipt_url"])
        expect(http_refuse["receipt_class"] == "clearance", "http clearance")
        expect(http_refuse["watch_block"] is True, "http watch")
        http_threat = stranger_fetch(srv.base_url, blocked["result"]["threat_receipt_url"])
        expect(http_threat["receipt_class"] == "threat", "http threat")

    assert_all_receipts_lab(ron)
    assert_all_receipts_lab(mw)

    print("RON_S9_WIRE_PROVE_OK")
    print(
        {
            "local_synthetic": a0["reason_code"],
            "watch_hostile": blocked["reason_code"],
            "after_allow": after["reason_code"],
            "stranger_http_verify": True,
            "their_production": False,
        }
    )


if __name__ == "__main__":
    main()
