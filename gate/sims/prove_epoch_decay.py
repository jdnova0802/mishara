#!/usr/bin/env python3
"""Prove S16 Epoch/Decay — freshness re-checked at actus time."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gate.sims import epoch_decay as ed  # noqa: E402
from gate.sims.lab_invariant import assert_all_receipts_lab  # noqa: E402


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> None:
    ed.reset()

    e1 = ed.rotate_epoch({"max_pay_cents": 5000, "rails": ["rtp"]})
    expect(e1["live"] is True, f"e1 {e1}")
    digest = "a" * 64
    g = ed.bind_grant(digest)
    expect("grant_id" in g, f"g {g}")

    ok = ed.check_grant(g["grant_id"], digest)
    expect(ok["decision"] == "ALLOW" and ok["reason_code"] == "epoch_fresh", f"ok {ok}")
    expect(ok["receipt_class"] == "epoch", "ok class")

    # Rotate policy epoch — prior grant must DENY at actus time
    e2 = ed.rotate_epoch({"max_pay_cents": 1000, "rails": ["rtp"]})
    expect(e2["epoch_id"] != e1["epoch_id"], "epoch rotated")
    dead = ed.check_grant(g["grant_id"], digest)
    expect(dead["decision"] == "DENY", f"dead {dead}")
    expect(dead["reason_code"] in ("epoch_decayed", "epoch_rotated"), f"dead reason {dead}")

    # Fresh bind on new epoch ALLOW
    g2 = ed.bind_grant(digest)
    ok2 = ed.check_grant(g2["grant_id"], digest)
    expect(ok2["decision"] == "ALLOW", f"ok2 {ok2}")
    expect(ed.get_receipt(ok2["receipt_id"]) is not None, "stranger")
    expect(ok2["their_production"] is False, "production")

    # Digest mismatch DENY
    bad = ed.check_grant(g2["grant_id"], "b" * 64)
    expect(bad["decision"] == "DENY" and bad["reason_code"] == "grant_digest_mismatch", f"bad {bad}")

    assert_all_receipts_lab(ed)

    print("EPOCH_DECAY_PROVE_OK")
    print(
        {
            "fresh_allow": ok["reason_code"],
            "after_rotate_deny": dead["reason_code"],
            "rebinding_allow": ok2["reason_code"],
            "their_production": False,
        }
    )


if __name__ == "__main__":
    main()
