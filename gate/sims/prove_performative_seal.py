#!/usr/bin/env python3
"""Prove S3 Performative Seal DENY paths + P0 EFSP block-transmit + stranger HTTP.

Lab only. Not Westlaw/Lexis checkers — file/transmit mouth.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gate.sims import performative_seal as ps  # noqa: E402
from gate.sims.lab_invariant import assert_all_receipts_lab  # noqa: E402
from gate.sims.verify_http import stranger_fetch, stranger_verify  # noqa: E402


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> None:
    ps.reset()

    # 1) planted fake case → seal DENY → cannot file OR transmit
    fake = ps.create_brief(
        [
            {
                "cite_key": "Varges v. FakeCite, 999 F.4th 1",
                "quoted_text": "This holding does not exist",
            }
        ]
    )
    s1 = ps.seal_brief(fake["brief_id"])
    expect(s1["decision"] == "DENY" and s1["reason_code"] == "seal_failed", f"s1 {s1}")
    expect(s1["receipt_class"] == "clearance", "s1 class")
    expect(any(f["reason"] == "ungrounded_citation" for f in s1["failures"]), f"s1 fail {s1}")
    f1 = ps.file_brief(fake["brief_id"], seal_id=s1.get("seal_id"))
    expect(f1["decision"] == "DENY", f"f1 {f1}")
    t1 = ps.transmit_efsp(fake["brief_id"], seal_id=s1.get("seal_id"))
    expect(t1["decision"] == "DENY", f"t1 {t1}")
    expect(t1["reason_code"] == "efsp_block_no_seal", f"t1 reason {t1}")
    expect(ps.get_receipt(s1["receipt_id"]) is not None, "s1 stranger receipt")

    # 2) real cite, fake quote → DENY
    bad_quote = ps.create_brief(
        [
            {
                "cite_key": "Fed. R. Civ. P. 11",
                "quoted_text": "Totally hallucinated quotation text",
            }
        ]
    )
    s2 = ps.seal_brief(bad_quote["brief_id"])
    expect(s2["decision"] == "DENY", f"s2 {s2}")
    expect(any(f["reason"] == "hallucinated_quote" for f in s2["failures"]), f"s2 {s2}")
    t2 = ps.transmit_efsp(bad_quote["brief_id"])
    expect(t2["reason_code"] == "efsp_block_no_seal", f"t2 {t2}")

    # 3) all grounded → seal ALLOW → file ALLOW + receipt
    good = ps.create_brief(
        [
            {
                "cite_key": "Fed. R. Civ. P. 11",
                "quoted_text": "By presenting to the court a pleading",
            },
            {
                "cite_key": "Mata v. Avianca, Inc., 678 F. Supp. 3d 443",
                "quoted_text": "The Court therefore imposes sanctions",
            },
        ]
    )
    s3 = ps.seal_brief(good["brief_id"])
    expect(s3["decision"] == "ALLOW" and s3["seal_id"], f"s3 {s3}")
    f3 = ps.file_brief(good["brief_id"], seal_id=s3["seal_id"])
    expect(f3["decision"] == "ALLOW" and f3["reason_code"] == "filed", f"f3 {f3}")
    expect(f3["result"]["seal_id"] == s3["seal_id"], "f3 seal link")
    expect(f3["their_production"] is False, "f3 production")
    expect(ps.get_receipt(f3["receipt_id"]) is not None, "f3 stranger receipt")

    # 3b) EFSP transmit ALLOW with LIVE seal (fixture — not real CM/ECF)
    t3 = ps.transmit_efsp(
        good["brief_id"],
        seal_id=s3["seal_id"],
        court_id="US-SDNY",
        case_number="1:26-cv-0099",
    )
    expect(t3["decision"] == "ALLOW" and t3["reason_code"] == "efsp_transmitted", f"t3 {t3}")
    expect(t3["result"]["real_cm_ecf"] is False, "t3 lab only")
    expect(t3["result"]["court_id"] == "US-SDNY", "t3 court")
    expect(t3["receipt_class"] == "clearance", "t3 class")

    # 4) file without seal → DENY
    bare = ps.create_brief(
        [
            {
                "cite_key": "28 U.S.C. § 1927",
                "quoted_text": "Any attorney or other person admitted",
            }
        ]
    )
    f4 = ps.file_brief(bare["brief_id"])
    expect(f4["decision"] == "DENY" and f4["reason_code"] == "no_seal", f"f4 {f4}")

    # 5) EFSP transmit without seal → block-transmit DENY
    t4 = ps.transmit_efsp(bare["brief_id"])
    expect(t4["decision"] == "DENY" and t4["reason_code"] == "efsp_block_no_seal", f"t4 {t4}")
    expect(t4["result"]["efsp_block"] is True, "t4 efsp_block flag")

    # ========== P0: stranger HTTP verify seal + file + transmit receipts ==========
    with stranger_verify() as srv:
        http_seal_deny = stranger_fetch(srv.base_url, s1["receipt_url"])
        expect(http_seal_deny["reason_code"] == "seal_failed", "http seal deny")
        expect(http_seal_deny["their_production"] is False, "http seal lab")

        http_file = stranger_fetch(srv.base_url, f3["receipt_url"])
        expect(http_file["decision"] == "ALLOW", "http file allow")
        expect(http_file["receipt_class"] == "clearance", "http file class")

        http_tx = stranger_fetch(srv.base_url, t3["receipt_url"])
        expect(http_tx["reason_code"] == "efsp_transmitted", "http tx")
        expect(http_tx["result"]["efsp"] == "lab_fixture", "http tx fixture")

        http_block = stranger_fetch(srv.base_url, t4["receipt_url"])
        expect(http_block["reason_code"] == "efsp_block_no_seal", "http block")

    assert_all_receipts_lab(ps)

    print("PERFORMATIVE_SEAL_PROVE_OK")
    print(
        {
            "denies": [
                s1["reason_code"],
                s2["reason_code"],
                f4["reason_code"],
                t1["reason_code"],
                t4["reason_code"],
            ],
            "filed_receipt": f3["receipt_id"],
            "efsp_transmit_receipt": t3["receipt_id"],
            "stranger_http_verify": True,
            "their_production": False,
        }
    )


if __name__ == "__main__":
    main()
