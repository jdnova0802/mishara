"""Command radiation — the uplink.

ASML prints the chip. The scanner prints bind-only. This is the mouth:

  May this CLTU still be radiated, for this vehicle, in this now?

DSN Command Service aborts radiation if monitors fail. There is no second
copy of the bits. A spacecraft Command Loss Timer is not reset by silence.
UTC is the only recommended international now (CGPM 2018). A command that
is not in that now is not a command.

Gate mapping (not a museum):
  vehicle            = job_id
  CLTU               = bind ticket + spend fingerprint
  radiate            = redeem, then forward bind-only
  radiation_abort    = monitors failed (skew, missing now, wrong write, stale)
  command_loss_timer = ticket not_after; silence is DEAD

Not Starship. The only mouth that can still talk to something that already left.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone

SPEC = "gate-command-radiation-v1"
REASON_NOW_REQUIRED = "command_now_required"
REASON_NOW_INVALID = "command_now_invalid"
DEFAULT_SKEW = 15


def max_skew_seconds() -> int:
    try:
        n = int(os.getenv("GATE_COMMAND_SKEW", str(DEFAULT_SKEW)))
    except ValueError:
        n = DEFAULT_SKEW
    return max(1, min(n, 300))


def parse_utc(value: str | None) -> datetime | None:
    s = (value or "").strip()
    if not s:
        return None
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def check_now(presented: str | None, *, server: datetime | None = None) -> dict:
    """Fail closed if the command is not in the shared now.

    Missing now is not the same as a broken monitor. Empty → required.
    Unparseable or skewed → invalid. Neither consumes the ticket.
    """
    server = server or datetime.now(timezone.utc)
    skew = max_skew_seconds()
    raw = (presented or "").strip()
    if not raw:
        return {
            "ok": False,
            "radiation_abort": True,
            "reason": REASON_NOW_REQUIRED,
            "server_now": server.isoformat(),
            "max_skew_seconds": skew,
        }
    parsed = parse_utc(raw)
    if parsed is None:
        return {
            "ok": False,
            "radiation_abort": True,
            "reason": REASON_NOW_INVALID,
            "server_now": server.isoformat(),
            "presented_now": raw,
            "max_skew_seconds": skew,
        }
    delta = abs((parsed - server).total_seconds())
    if delta > skew:
        return {
            "ok": False,
            "radiation_abort": True,
            "reason": REASON_NOW_INVALID,
            "server_now": server.isoformat(),
            "presented_now": parsed.isoformat(),
            "skew_seconds": delta,
            "max_skew_seconds": skew,
        }
    return {
        "ok": True,
        "radiation_abort": False,
        "server_now": server.isoformat(),
        "presented_now": parsed.isoformat(),
        "skew_seconds": delta,
        "max_skew_seconds": skew,
    }


def spec(public_url: str) -> dict:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Command radiation",
        "what": "May this CLTU still be radiated, for this vehicle, in this now?",
        "not": [
            "a hop receipt",
            "Starship",
            "a second speaker for a vehicle you did not book",
        ],
        "lineage": {
            "dsn_command_service": "Radiation aborts if monitors fail. No independent copy of the bits.",
            "command_loss_timer": "Valid uplink resets the timer. Silence is DEAD.",
            "utc": "CGPM 2018: UTC is the only recommended international time scale.",
        },
        "mapping": {
            "vehicle": "job_id",
            "cltu": "bind ticket + spend_fingerprint",
            "radiate": f"POST {base}/v1/pas/bind-ticket/redeem then forward bind-only",
            "now": "UTC. Redeem must present now. Skew beyond max_skew_seconds aborts.",
        },
        "now": {
            "required": True,
            "scale": "UTC",
            "max_skew_seconds": max_skew_seconds(),
            "missing": REASON_NOW_REQUIRED,
            "invalid": REASON_NOW_INVALID,
        },
        "radiation_abort": True,
        "abort_does_not_consume": True,
        "fail_closed": True,
        "spend_protocol": f"{base}/.well-known/spend-protocol.json",
        "redeem": f"{base}/v1/pas/bind-ticket/redeem",
        "implementor": f"{base}/listings/cloudflare-worker-bind.js",
        "their_production": False,
        "page": f"{base}/uplink",
    }
