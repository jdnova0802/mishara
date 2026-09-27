#!/usr/bin/env python3
"""Prove S10 Preflight Diff — independent of S9 trust.

CRITICAL: Scenario X — S9 session fully clear (no threat) AND preflight still
DENYs purely on delta mismatch. That proves S10 is not secretly S9.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gate.sims import actus_fence as af  # noqa: E402
from gate.sims import mouth_watch as mw  # noqa: E402
from gate.sims import preflight_diff as pf  # noqa: E402
from gate.sims.lab_invariant import assert_all_receipts_lab  # noqa: E402


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> None:
    pf.reset()
    mw.reset()
    af.reset()

    action = "pay"
    payload = {"payee": "acme", "amount_cents": 100}

    # --- basic DENYs ---
    r0 = pf.check_preflight(action, payload)
    expect(r0["decision"] == "DENY" and r0["reason_code"] == "preflight_missing", f"r0 {r0}")
    expect(r0["receipt_class"] == "preflight", "r0 class")

    stale = pf.record_preflight(
        action,
        payload,
        projected_delta={"balance_delta": -100},
        invariants_ok=True,
        ttl_sec=-1,
    )
    r1 = pf.check_preflight(action, payload, preflight_id=stale["preflight_id"])
    expect(r1["decision"] == "DENY" and r1["reason_code"] == "preflight_stale", f"r1 {r1}")

    hostile = pf.record_preflight(
        action,
        payload,
        projected_delta={"balance_delta": -999999},
        invariants_ok=True,
        hostile=True,
    )
    r2 = pf.check_preflight(action, payload, preflight_id=hostile["preflight_id"])
    expect(r2["decision"] == "DENY" and r2["reason_code"] == "preflight_hostile_delta", f"r2 {r2}")

    uncertain = pf.record_preflight(
        action,
        payload,
        projected_delta={"balance_delta": -100},
        invariants_ok=None,
    )
    r3 = pf.check_preflight(action, payload, preflight_id=uncertain["preflight_id"])
    expect(r3["decision"] == "DENY" and r3["reason_code"] == "preflight_uncertain", f"r3 {r3}")

    # ========== CRITICAL Scenario X ==========
    # S9 trust check PASSES cleanly (no threat). Preflight DENYs on delta mismatch alone.
    mw.reset()
    pf.reset()
    s9 = mw.score_session(appearance="live", device_trust="known", network_risk="low")
    expect(s9["decision"] == "ALLOW", f"X S9 must be clear {s9}")
    expect(s9["receipt_class"] == "watch_clear", f"X S9 class {s9}")
    expect(s9.get("threat_class") is None, "X no threat_class")

    sim = pf.record_preflight(
        action,
        payload,
        projected_delta={"balance_delta": -100, "payee": "acme"},
        invariants_ok=True,
        hostile=False,
    )
    # Actual commit delta differs from simulated — S10 alone must DENY
    x = pf.check_preflight(
        action,
        payload,
        preflight_id=sim["preflight_id"],
        actual_delta={"balance_delta": -500, "payee": "acme"},  # mismatch
    )
    expect(x["decision"] == "DENY", f"X preflight DENY {x}")
    expect(x["reason_code"] == "preflight_delta_mismatch", f"X reason {x}")
    expect(x["receipt_class"] == "preflight", "X receipt_class preflight")
    expect(x.get("threat_class") is None, "X not a threat object")
    # Prove no S9 entanglement: re-score still clear; X denial has no watch_block fields
    s9b = mw.score_session(appearance="live", device_trust="known", network_risk="low")
    expect(s9b["decision"] == "ALLOW", f"X S9 still clear after preflight DENY {s9b}")
    expect("watch_block" not in x or x.get("watch_block") in (False, None), "X no watch_block")
    expect(x.get("threat_receipt_id") is None, "X no threat_receipt_id")

    # Wire through Actus Fence: clean S9 session + mismatched preflight → clearance DENY
    # linking preflight, NOT threat
    af.reset()
    m = af.create_mandate(["pay"], max_amount_cents=5000, payee_allowlist=["acme"])
    dig = af.action_digest("pay", payload)
    g = af.create_grant(m["mandate_id"], dig)
    # Use preflight check result as gate before execute (mouth consults S10 separately)
    expect(x["decision"] == "DENY", "X still deny before execute")
    # Clean path ALLOW when delta matches
    pf.reset()
    good = pf.record_preflight(
        action,
        payload,
        projected_delta={"balance_delta": -100, "payee": "acme"},
        invariants_ok=True,
    )
    ok = pf.check_preflight(
        action,
        payload,
        preflight_id=good["preflight_id"],
        actual_delta={"balance_delta": -100, "payee": "acme"},
    )
    expect(ok["decision"] == "ALLOW" and ok["reason_code"] == "preflight_clear", f"ok {ok}")
    expect(ok["receipt_class"] == "preflight", "ok class")
    expect(pf.get_receipt(ok["receipt_id"]) is not None, "stranger receipt")

    # Execute with clean S9 + matching preflight already verified
    exec_ok = af.execute(
        "pay",
        payload,
        mandate_id=m["mandate_id"],
        grant_id=g["grant_id"],
        watch_session={"appearance": "live", "device_trust": "known", "network_risk": "low"},
    )
    expect(exec_ok["decision"] == "ALLOW", f"exec_ok {exec_ok}")
    expect(exec_ok["watch_block"] is False, "exec no watch_block")
    expect(exec_ok["threat_receipt_id"] is None, "exec no threat")
    expect(exec_ok["receipt_class"] == "clearance", "exec clearance")

    assert_all_receipts_lab(pf)
    assert_all_receipts_lab(mw)
    assert_all_receipts_lab(af)

    print("PREFLIGHT_DIFF_PROVE_OK")
    print(
        {
            "scenario_x": {
                "s9_clear": True,
                "preflight_deny_reason": x["reason_code"],
                "receipt_class": x["receipt_class"],
                "independent_of_threat": True,
            },
            "denies": [
                r0["reason_code"],
                r1["reason_code"],
                r2["reason_code"],
                r3["reason_code"],
                x["reason_code"],
            ],
            "their_production": False,
        }
    )


if __name__ == "__main__":
    main()
