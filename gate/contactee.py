"""Contactee Ban — you do not talk to the chassis. You present at ports.

Earth wants a conversation with the alien: chat UIs, copilots, 'ask Gate
if we can bind'. This hardware has no dialogical interior. You present a
hop at the exclusive door. It emits ALLOW|HALT|BLOCK and maybe a CHARGE
requirement. Anthropomorphizing it into a colleague is how skip-clear
gets a nickname and a Slack channel.

Not Earth-side: not 'AI assistant for compliance'.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-contactee-ban-v1"
INVENTOR = "Nisaba LLC / Gate"

ILLEGAL_CHANNELS = (
    "chat_ask_gate",
    "copilot_please_approve",
    "slack_thread_with_the_mouth",
    "voice_of_the_machine",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def present(*, channel: str | None = None, at_exclusive_door: bool | None = None) -> dict[str, Any]:
    ch = (channel or "").strip().lower()
    door = bool(at_exclusive_door)
    if ch in ILLEGAL_CHANNELS or ch.startswith("chat_") or ch.startswith("ask_"):
        posture = "contactee_illegal"
        claim = "no_dialogical_interior"
    elif door:
        posture = "port_presentation"
        claim = "hop_at_door_is_the_only_legal_contact"
    else:
        posture = "no_contact"
        claim = "nothing_presented"
    return {
        "spec": SPEC,
        "name": "Contactee Ban",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "illegal_channels": list(ILLEGAL_CHANNELS),
        "channel": ch or None,
        "at_exclusive_door": door,
        "posture": posture,
        "claim": claim,
        "thesis": "Do not befriend the apparatus. Present at the port.",
        "gatekeep": "Proprietary contactee ban. Ours.",
        "earth_side": False,
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Contactee Ban",
        "inventor": INVENTOR,
        "example_port": present(at_exclusive_door=True, channel="exclusive_door"),
        "example_ban": present(channel="chat_ask_gate"),
        "live": f"{base}/.well-known/contactee-ban.json",
        "contact_protocol": f"{base}/.well-known/contact-protocol.json",
        "their_production": False,
    }
