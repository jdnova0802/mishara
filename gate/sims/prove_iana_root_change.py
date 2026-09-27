#!/usr/bin/env python3
"""Prove Z3 IANA Root Change — intent ≠ root-zone write. Lab only."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gate.sims import iana_root_change as rz  # noqa: E402
from gate.sims.lab_invariant import assert_all_receipts_lab  # noqa: E402
from gate.sims.verify_http import stranger_fetch, stranger_verify  # noqa: E402


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> None:
    rz.reset()
    rz.register_tld("example")

    # 1) bad DS tech check → DENY (cannot apply)
    bad = rz.submit_change(
        tld="example",
        change_type="ds",
        payload={
            "keytag": "99999",
            "algorithm": 1,
            "digest_type": 1,
            "digest": "dead",
            "matches_child_dnskey": False,
        },
    )
    expect(bad["decision"] == "DENY" and bad["reason_code"] == "tech_check_failed", f"bad {bad}")
    expect("bad_keytag" in bad["result"]["failures"], f"bad failures {bad}")
    expect(bad["receipt_class"] == "clearance", "bad class")

    # apply on failed tech → still DENY
    apply_bad = rz.apply_root_change(bad["change_id"])
    expect(apply_bad["reason_code"] == "tech_check_failed", f"apply_bad {apply_bad}")

    # 2) unverified DS ↔ DNSKEY → DENY
    unverified = rz.submit_change(
        tld="example",
        change_type="ds",
        payload={
            "keytag": "12345",
            "algorithm": 13,
            "digest_type": 2,
            "digest": "a" * 64,
            # matches_child_dnskey omitted → unverified
        },
    )
    expect(unverified["reason_code"] == "tech_check_failed", f"unverified {unverified}")
    expect("ds_dnskey_unverified" in unverified["result"]["failures"], "unverified fail")

    # 3) insufficient NS → DENY
    ns_bad = rz.submit_change(
        tld="example",
        change_type="ns",
        payload={"ns": ["only.one.example"]},
    )
    expect(ns_bad["reason_code"] == "tech_check_failed", f"ns_bad {ns_bad}")

    # 4) clean DS + maintainer nack → DENY
    good = rz.submit_change(
        tld="example",
        change_type="ds",
        payload={
            "keytag": "12345",
            "algorithm": 13,
            "digest_type": 2,
            "digest": "ab" * 32,
            "matches_child_dnskey": True,
        },
    )
    expect("change_id" in good and good.get("tech_ok") is True, f"good {good}")
    nack = rz.apply_root_change(good["change_id"], maintainer_ack=False)
    expect(nack["reason_code"] == "maintainer_nack", f"nack {nack}")

    # 5) clean DS + maintainer ack → ALLOW root update
    ok = rz.apply_root_change(good["change_id"], maintainer_ack=True)
    expect(ok["decision"] == "ALLOW" and ok["reason_code"] == "root_zone_updated", f"ok {ok}")
    expect(ok["result"]["real_root"] is False, "ok lab")
    expect(ok["result"]["pti_verisign_shaped"] is True, "ok shaped")
    expect(rz.get_receipt(ok["receipt_id"]) is not None, "ok store")

    # 6) unknown TLD → DENY
    unk = rz.submit_change(
        tld="nope",
        change_type="ns",
        payload={"ns": ["a.nope", "b.nope"]},
    )
    expect(unk["reason_code"] == "unknown_tld", f"unk {unk}")

    with stranger_verify() as srv:
        http_deny = stranger_fetch(srv.base_url, bad["receipt_url"])
        expect(http_deny["reason_code"] == "tech_check_failed", "http tech deny")
        http_ok = stranger_fetch(srv.base_url, ok["receipt_url"])
        expect(http_ok["reason_code"] == "root_zone_updated", "http root ok")

    assert_all_receipts_lab(rz)

    print("IANA_ROOT_CHANGE_PROVE_OK")
    print(
        {
            "denies": [
                bad["reason_code"],
                unverified["reason_code"],
                ns_bad["reason_code"],
                nack["reason_code"],
                unk["reason_code"],
            ],
            "root_receipt": ok["receipt_id"],
            "stranger_http_verify": True,
            "their_production": False,
        }
    )


if __name__ == "__main__":
    main()
