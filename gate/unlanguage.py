"""Unlanguage Receipt — valid without English. Hash + fetch is the speech.

The chassis does not speak KPI, legal, or governance. Its native utterance
is fetchable structure: receipt hash, verify antenna, restraint leaf.
English theses on this document are a translation for a species that
reads. Validity does not require the translation. If it only exists as
a paragraph, it has not spoken.

Not Earth-side: not documentation. Speech that is not words.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

SPEC = "gate-unlanguage-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def utter(
    *,
    receipt_hash: str | None = None,
    verify_url: str | None = None,
    english_only: bool | None = None,
) -> dict[str, Any]:
    rh = bool((receipt_hash or "").strip())
    url = bool((verify_url or "").strip())
    eng = bool(english_only)
    if eng and not (rh and url):
        posture = "translation_without_speech"
        claim = "paragraphs_are_not_utterance"
    elif rh and url:
        posture = "spoken"
        claim = "hash_and_antenna_are_native"
    else:
        posture = "mute"
        claim = "no_fetchable_utterance"
    return {
        "spec": SPEC,
        "name": "Unlanguage Receipt",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "receipt_hash_present": rh,
        "verify_present": url,
        "english_only": eng,
        "posture": posture,
        "claim": claim,
        "thesis": "The mouth speaks in fetch. English is a visitor's pamphlet.",
        "gatekeep": "Proprietary unlanguage. Ours.",
        "earth_side": False,
        "their_production": False,
    }


def attach_to_receipt_payload(payload: Mapping[str, Any], row: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(payload)
    out["unlanguage"] = utter(
        receipt_hash=row.get("receipt_hash"),
        verify_url=row.get("verify_url"),
        english_only=False,
    )
    return out


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Unlanguage Receipt",
        "inventor": INVENTOR,
        "example_spoken": utter(receipt_hash="abc", verify_url="https://velaru.xyz/verify"),
        "example_mute": utter(english_only=True),
        "live": f"{base}/.well-known/unlanguage.json",
        "holographic": f"{base}/.well-known/holographic.json",
        "their_production": False,
    }
