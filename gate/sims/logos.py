"""Shared logos grammar — mandate → grant → digest → actus.

Every consequential mouth consults the same object shape so new welds
multiply without reinventing trust objects per vertical.

Lab only. their_production stamped by calling mouths, not here.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any


# Pay-shaped + bank-push-shaped actus that need amount/creditor checks.
BANK_SEND_ACTIONS = frozenset({"bank_send", "fednow_push", "rtp_push"})
AMOUNT_BOUND_ACTIONS = frozenset({"pay"}) | BANK_SEND_ACTIONS
ALLOWED_RAILS = frozenset({"fednow", "rtp"})


def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def action_digest(action_type: str, payload: dict[str, Any]) -> str:
    body = {"action_type": action_type, "payload": payload}
    return hashlib.sha256(canonical(body).encode("utf-8")).hexdigest()


@dataclass
class Mandate:
    """LIVE logos binding scope (and optional money/rail constraints)."""

    mandate_id: str
    scope: list[str]
    max_amount_cents: int | None
    payee_allowlist: list[str]
    allowed_rails: list[str]
    expires_at: float
    revoked: bool = False

    def is_live(self, now: float | None = None) -> bool:
        t = time.time() if now is None else now
        return (not self.revoked) and self.expires_at >= t


@dataclass
class Grant:
    """Short-lived token bound to an exact action digest."""

    grant_id: str
    mandate_id: str
    digest: str
    expires_at: float

    def is_live(self, now: float | None = None) -> bool:
        t = time.time() if now is None else now
        return self.expires_at >= t


def creditor_from_payload(payload: dict[str, Any]) -> str:
    """Bank-send fixtures use creditor; pay uses payee — same allowlist."""
    return str(payload.get("creditor") or payload.get("payee") or "")


def rail_from_payload(action_type: str, payload: dict[str, Any]) -> str | None:
    """Infer rail for bank-send-shaped actus. None for non-rail actions."""
    if action_type == "fednow_push":
        return "fednow"
    if action_type == "rtp_push":
        return "rtp"
    if action_type == "bank_send":
        rail = str(payload.get("rail") or "").lower()
        return rail or None
    return None
