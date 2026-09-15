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
    deed_record_gate,
    edgar_disclose_seal,
    lab_invariant as lab,
    mouth_watch,
    performative_seal,
    ron_attest_refuse,
)
from gate.sims.prove_actus_fence import main as prove_s1  # noqa: E402
from gate.sims.prove_deed_record_gate import main as prove_s6  # noqa: E402
from gate.sims.prove_edgar_disclose_seal import main as prove_s7  # noqa: E402
from gate.sims.prove_mouth_watch import main as prove_s9  # noqa: E402
from gate.sims.prove_performative_seal import main as prove_s3  # noqa: E402
from gate.sims.prove_ron_attest_refuse import main as prove_s8  # noqa: E402


MOUTHS = (
    actus_fence,
    performative_seal,
    edgar_disclose_seal,
    deed_record_gate,
    ron_attest_refuse,
    mouth_watch,
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
