"""Contact Protocol — first contact with irreversible spend is not a chat UI.

Alien contact fiction: you do not improvise handshake. Gate publishes the
protocol: hop, exclusive door, mouth alphabet, CHARGE or HALT, receipt
antenna. A Slack 'lgtm' is not first contact. Copycats invent vibes.
Gate invents a handshake the stranger can verify.

Gatekeep only to ourselves: SETI/contact protocol → irreversible first contact.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-contact-protocol-v1"
INVENTOR = "Nisaba LLC / Gate"

STEPS = (
    "present_hop_on_exclusive_door",
    "mouth_decodes_allow_halt_block",
    "charge_or_remain_dead",
    "receipt_broadcast_on_verify_antenna",
)

NOT_CONTACT = (
    "slack_lgtm",
    "email_approve",
    "dashboard_click",
    "ai_chat_yes",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def handshake(*, channel: str | None = None, steps_honored: int | None = None) -> dict[str, Any]:
    ch = (channel or "").strip().lower()
    n = int(steps_honored) if steps_honored is not None else 0
    if ch in NOT_CONTACT:
        posture = "not_contact"
        claim = "improvised_channel_is_not_the_protocol"
    elif n >= 4:
        posture = "contact_complete"
        claim = "handshake_closed_with_antenna"
    elif n >= 1:
        posture = "contact_in_progress"
        claim = "protocol_steps_partial"
    else:
        posture = "no_handshake"
        claim = "no_door_no_contact"
    return {
        "spec": SPEC,
        "name": "Contact Protocol",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "First-contact / SETI handshake discipline",
            "Gate spend protocol + stranger verify",
        ],
        "steps": list(STEPS),
        "not_contact": list(NOT_CONTACT),
        "channel": ch or None,
        "steps_honored": n,
        "posture": posture,
        "claim": claim,
        "thesis": "Irreversible spend is first contact. You do not freestyle it.",
        "gatekeep": "Proprietary contact-protocol doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Contact Protocol",
        "inventor": INVENTOR,
        "example_ok": handshake(channel="exclusive_door", steps_honored=4),
        "example_not": handshake(channel="slack_lgtm"),
        "live": f"{base}/.well-known/contact-protocol.json",
        "spend_protocol": f"{base}/.well-known/spend-protocol.json",
        "their_production": False,
    }
