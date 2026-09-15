#!/usr/bin/env python3
"""Prove S3 Performative Seal DENY paths. Lab only."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gate.sims import performative_seal as ps  # noqa: E402


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> None:
    ps.reset()

    # 1) planted fake case → seal DENY
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
    expect(any(f["reason"] == "ungrounded_citation" for f in s1["failures"]), f"s1 fail {s1}")
    f1 = ps.file_brief(fake["brief_id"], seal_id=s1.get("seal_id"))
    expect(f1["decision"] == "DENY", f"f1 {f1}")
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

    print("PERFORMATIVE_SEAL_PROVE_OK")
    print(
        {
            "denies": [s1["reason_code"], s2["reason_code"], f4["reason_code"]],
            "filed_receipt": f3["receipt_id"],
            "their_production": False,
        }
    )


if __name__ == "__main__":
    main()
