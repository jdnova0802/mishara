#!/usr/bin/env python3
"""Meta-prove: their_production is a hard invariant across all lab mouths.

Not aspirational. Mutating THEIR_PRODUCTION to True must fail at stamp time.
Every mouth prove must leave only lab receipts.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gate.sims import (  # noqa: E402
    actus_fence,
    cls_settle,
    college_arms,
    deed_record_gate,
    deny_federation,
    edgar_disclose_seal,
    epoch_decay,
    freeport_ingress,
    iana_root_change,
    isda_dc_publish,
    isa_exploit,
    itu_biu_mifr,
    kp_export,
    lab_invariant as lab,
    lloyds_bind_stamp,
    mouth_watch,
    peerage_roll,
    performative_seal,
    preflight_diff,
    ron_attest_refuse,
)
from gate.sims.prove_actus_fence import main as prove_s1  # noqa: E402
from gate.sims.prove_cls_settle import main as prove_z2  # noqa: E402
from gate.sims.prove_college_arms import main as prove_z10  # noqa: E402
from gate.sims.prove_deed_record_gate import main as prove_s6  # noqa: E402
from gate.sims.prove_deny_federation_stub import main as prove_s13  # noqa: E402
from gate.sims.prove_edgar_disclose_seal import main as prove_s7  # noqa: E402
from gate.sims.prove_epoch_decay import main as prove_s16  # noqa: E402
from gate.sims.prove_freeport_ingress import main as prove_z8  # noqa: E402
from gate.sims.prove_iana_root_change import main as prove_z3  # noqa: E402
from gate.sims.prove_isda_dc_publish import main as prove_z1  # noqa: E402
from gate.sims.prove_isa_exploit import main as prove_z6  # noqa: E402
from gate.sims.prove_itu_biu_mifr import main as prove_z5  # noqa: E402
from gate.sims.prove_kp_export import main as prove_z7  # noqa: E402
from gate.sims.prove_lloyds_bind_stamp import main as prove_z4  # noqa: E402
from gate.sims.prove_mouth_watch import main as prove_s9  # noqa: E402
from gate.sims.prove_peerage_roll import main as prove_z9  # noqa: E402
from gate.sims.prove_performative_seal import main as prove_s3  # noqa: E402
from gate.sims.prove_preflight_diff import main as prove_s10  # noqa: E402
from gate.sims.prove_ron_attest_refuse import main as prove_s8  # noqa: E402


MOUTHS = (
    actus_fence,
    performative_seal,
    edgar_disclose_seal,
    deed_record_gate,
    ron_attest_refuse,
    mouth_watch,
    preflight_diff,
    epoch_decay,
    deny_federation,
    isda_dc_publish,
    cls_settle,
    iana_root_change,
    lloyds_bind_stamp,
    itu_biu_mifr,
    isa_exploit,
    kp_export,
    freeport_ingress,
    peerage_roll,
    college_arms,
)


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> None:
    for m in MOUTHS:
        lab.assert_module_lab(m)

    victim = actus_fence
    original = victim.THEIR_PRODUCTION
    try:
        victim.THEIR_PRODUCTION = True  # type: ignore[misc]
        raised = False
        try:
            lab.stamp_lab_flag(victim.THEIR_PRODUCTION, module="actus_fence")
        except lab.LabInvariantError:
            raised = True
        expect(raised, "mutated THEIR_PRODUCTION=True must raise at stamp")
    finally:
        victim.THEIR_PRODUCTION = original  # type: ignore[misc]

    expect(victim.THEIR_PRODUCTION is False, "restored lab flag")

    prove_s1()
    prove_s3()
    prove_s7()
    prove_s6()
    prove_s8()
    prove_s9()
    prove_s10()
    prove_s16()
    prove_s13()
    prove_z1()
    prove_z2()
    prove_z3()
    prove_z4()
    prove_z5()
    prove_z6()
    prove_z7()
    prove_z8()
    prove_z9()
    prove_z10()

    for m in MOUTHS:
        lab.assert_all_receipts_lab(m)

    print("LAB_INVARIANT_PROVE_OK")
    print(
        {
            "mouths": [m.__name__ for m in MOUTHS],
            "their_production": False,
            "mutation_caught": True,
        }
    )


if __name__ == "__main__":
    main()
