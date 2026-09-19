"""Fail closed if production diligence is still the DEPOSIT shakedown."""
from __future__ import annotations

import json
import urllib.request

OFFER = "https://gate.velaru.xyz/diligence/offer.json"
WANT_SPEC = "gate-ops-review-v2"


def main() -> int:
    with urllib.request.urlopen(OFFER, timeout=20) as r:
        data = json.load(r)
    spec = data.get("spec")
    ask = data.get("ask", "")
    print(f"spec={spec}")
    print(f"ask={ask}")
    if spec != WANT_SPEC:
        print("NO-GO: live offer is not gate-ops-review-v2. Do not send T1–T3.")
        return 1
    if "DEPOSIT" in ask.upper() and "REVIEW" not in ask.upper():
        print("NO-GO: live ask still DEPOSIT.")
        return 1
    print("GO: live page matches v2. T1–T3 may paste.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
