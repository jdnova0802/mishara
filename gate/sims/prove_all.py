#!/usr/bin/env python3
"""Standard prove sequence — mouths + intelligences + S9 + lab invariant.

Required always: prove_mouth_watch, prove_lab_invariant.
New intelligences: preflight_diff (S10), epoch_decay (S16), deny_federation_stub (S13).
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
from gate.sims.prove_deny_federation_stub import main as prove_s13  # noqa: E402
from gate.sims.prove_edgar_disclose_seal import main as prove_s7  # noqa: E402
from gate.sims.prove_epoch_decay import main as prove_s16  # noqa: E402
from gate.sims.prove_lab_invariant import main as prove_lab  # noqa: E402
from gate.sims.prove_mouth_watch import main as prove_s9  # noqa: E402
from gate.sims.prove_performative_seal import main as prove_s3  # noqa: E402
from gate.sims.prove_preflight_diff import main as prove_s10  # noqa: E402
from gate.sims.prove_ron_attest_refuse import main as prove_s8  # noqa: E402
from gate.sims.prove_ron_s9_wire import main as prove_s8_s9  # noqa: E402


STANDARD_SEQUENCE = (
    ("prove_actus_fence", prove_s1),
    ("prove_performative_seal", prove_s3),
    ("prove_mouth_watch", prove_s9),
    ("prove_actus_s9_wire", prove_s1_s9),
    ("prove_preflight_diff", prove_s10),  # Scenario X: S9 clear + S10 DENY alone
    ("prove_epoch_decay", prove_s16),
    ("prove_deny_federation_stub", prove_s13),
    ("prove_edgar_disclose_seal", prove_s7),
    ("prove_deed_record_gate", prove_s6),
    ("prove_ron_attest_refuse", prove_s8),
    ("prove_ron_s9_wire", prove_s8_s9),
    ("prove_lab_invariant", prove_lab),
)


def main() -> None:
    ran: list[str] = []
    for name, fn in STANDARD_SEQUENCE:
        fn()
        ran.append(name)
    print("PROVE_ALL_OK")
    print(
        {
            "sequence": ran,
            "required_always": ["prove_mouth_watch", "prove_lab_invariant"],
            "s10_scenario_x": "S9 clear + preflight_delta_mismatch DENY (independent)",
            "p0_weld": {
                "s1": "bank_send + stranger HTTP clearance/threat",
                "s3": "transmit_efsp + efsp_block_no_seal + stranger HTTP",
                "logos": "shared mandate/grant/digest",
            },
            "tier2_weld": {
                "s8_s9": "prove_ron_s9_wire",
                "s7": "submit_edgar_gateway + edgar_block_no_seal",
                "s6": "record watch_session + stranger HTTP",
                "verify": "edgar/deed/ron routes on verify_http",
            },
        }
    )


if __name__ == "__main__":
    main()
