#!/usr/bin/env python3
"""Prove S13 Deny Federation STUB — in-process only, no network."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gate.sims import deny_federation as df  # noqa: E402
from gate.sims.lab_invariant import assert_all_receipts_lab  # noqa: E402


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> None:
    df.reset()
    df.assert_in_process_only()

    digest = "c" * 64
    clear = df.check_digest(digest)
    expect(clear["decision"] == "ALLOW" and clear["reason_code"] == "no_foreign_deny", f"clear {clear}")
    expect(clear["foreign_block"] is False, "no foreign block")
    expect(clear["receipt_class"] == "clearance", "clearance class")

    planted = df.plant_foreign_deny(
        digest,
        source_mouth="edgar_disclose_seal",
        receipt_class="threat",
    )
    blocked = df.check_digest(digest)
    expect(blocked["decision"] == "DENY" and blocked["reason_code"] == "foreign_deny", f"blocked {blocked}")
    expect(blocked["foreign_block"] is True, "foreign_block")
    expect(blocked["foreign_receipt_id"] == planted["foreign_receipt_id"], "link")
    expect(blocked["source_mouth"] == "edgar_disclose_seal", "source")
    expect(df.get_receipt(blocked["receipt_id"]) is not None, "stranger")
    expect(blocked["their_production"] is False, "production")

    # Different digest unaffected
    other = df.check_digest("d" * 64)
    expect(other["decision"] == "ALLOW", f"other {other}")

    df.assert_in_process_only()
    assert_all_receipts_lab(df)

    print("DENY_FEDERATION_STUB_PROVE_OK")
    print(
        {
            "in_process_only": True,
            "foreign_deny_reason": blocked["reason_code"],
            "foreign_receipt_id": blocked["foreign_receipt_id"],
            "their_production": False,
        }
    )


if __name__ == "__main__":
    main()
