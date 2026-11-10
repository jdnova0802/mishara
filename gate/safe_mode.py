"""Item 20 — defined fallback after HOLD/HALT. The agent does not improvise."""
from __future__ import annotations

SPEC = "gate-safe-mode-v1"
ALLOWED = ("read", "verify", "escalate")
FORBIDDEN = ("bind", "payout", "withdraw", "issue", "charge")


def snapshot(*, reason: str) -> dict:
    return {
        "spec": SPEC,
        "state": "SAFE_MODE",
        "reason": reason,
        "allowed": list(ALLOWED),
        "forbidden": list(FORBIDDEN),
        "plain": "Stop writes. You may read, verify, or escalate. You may not bind, pay, or issue.",
    }
