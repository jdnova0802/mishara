"""Item 167 — live media is untrusted by doctrine, not classified.

Real-time telephony/video deepfake detection at $129M stakes is still
open industry-wide. This module does not ship a detector, does not cite
ISO/IEC 30107 (wrong scope), and refuses any instruction that treats the
call itself as proof the speaker was real. 161's out-of-band challenge
is the allowed evidence class.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-media-untrusted-v1"


def stance() -> dict[str, Any]:
    return {
        "spec": SPEC,
        "detector_built": False,
        "iso_30107": False,
        "call_status": "untrusted_by_doctrine",
        "allowed_evidence": ["out_of_band_challenge"],
        "plain": "The call is not evidence. Callback-on-file is. A detector is not hiding behind this sentence.",
    }


def refuse_media_claim(*, media_evidence_claimed: Any) -> dict[str, Any] | None:
    claimed = media_evidence_claimed in (True, 1, "1", "true", "yes", "TRUE")
    if not claimed:
        return None
    return {
        "spec": SPEC,
        "ok": False,
        "error": "media_is_not_evidence",
        "detector_built": False,
        "plain": "Live voice/video cannot prove the speaker. That problem is unsolved. Use the 161 callback.",
    }
