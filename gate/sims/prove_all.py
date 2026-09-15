#!/usr/bin/env python3
"""Standard prove sequence for every mouth — includes S9 + lab invariant by default.

Template for future mouths (S6/S7/S8 and beyond):
  1. prove_<mouth>
  2. prove_mouth_watch          # always
  3. prove_lab_invariant        # always (runs all mouths + mutation catch)
  4. any wire proves (e.g. prove_actus_s9_wire)

Do not ship a mouth prove without 2+3 in the sequence.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gate.sims.prove_actus_fence import main as prove_s1  # noqa: E402
from gate.sims.prove_actus_s9_wire import main as prove_s1_s9  # noqa: E402
from gate.sims.prove_deed_record_gate import main as prove_s6  # noqa: E402
from gate.sims.prove_edgar_disclose_seal import main as prove_s7  # noqa: E402
from gate.sims.prove_lab_invariant import main as prove_lab  # noqa: E402
from gate.sims.prove_mouth_watch import main as prove_s9  # noqa: E402
from gate.sims.prove_performative_seal import main as prove_s3  # noqa: E402
from gate.sims.prove_ron_attest_refuse import main as prove_s8  # noqa: E402


# Canonical order — copy this when adding a new mouth prove.
STANDARD_SEQUENCE = (
    ("prove_actus_fence", prove_s1),
    ("prove_performative_seal", prove_s3),
    ("prove_mouth_watch", prove_s9),  # required for every future mouth ship
    ("prove_actus_s9_wire", prove_s1_s9),  # separate canary vs hostile session
    ("prove_edgar_disclose_seal", prove_s7),
    ("prove_deed_record_gate", prove_s6),
    ("prove_ron_attest_refuse", prove_s8),
    ("prove_lab_invariant", prove_lab),  # required — last
)


def main() -> None:
    ran: list[str] = []
    for name, fn in STANDARD_SEQUENCE:
        fn()
        ran.append(name)
    print("PROVE_ALL_OK")
    print({"sequence": ran, "required_always": ["prove_mouth_watch", "prove_lab_invariant"]})


if __name__ == "__main__":
    main()
