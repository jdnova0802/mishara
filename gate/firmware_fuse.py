"""Firmware Fuse — LIVE is a write-once firmware flash, not a runtime flag.

Alien devices often ship with fused bits you cannot unset from software.
Gate: DEAD→LIVE is firmware CHARGE. Runtime 'set live=true' is a jailbreak
fantasy. Epoch lock is the write-protect. Copycats treat LIVE as RAM.

Gatekeep only to ourselves: OTP fuse / firmware write-protect → CHARGE flash.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-firmware-fuse-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def flash(
    *,
    runtime_flag: bool | None = None,
    charge_id: str | None = None,
    epoch_locked: bool | None = None,
) -> dict[str, Any]:
    runtime = bool(runtime_flag)
    charge = bool((charge_id or "").strip())
    locked = bool(epoch_locked)
    if runtime and not charge:
        posture = "jailbreak_attempt"
        claim = "runtime_live_flag_is_not_firmware"
    elif charge and not runtime:
        posture = "fused"
        claim = "charge_flashed_write_once_live"
    elif locked and runtime:
        posture = "write_protect_held"
        claim = "epoch_lock_refuses_ram_live"
    else:
        posture = "unflashed"
        claim = "dead_firmware_image"
    return {
        "spec": SPEC,
        "name": "Firmware Fuse",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "OTP / eFuse / write-once firmware bits",
            "Gate epoch + CHARGE-only resurrection",
        ],
        "runtime_flag": runtime,
        "charge_present": charge,
        "epoch_locked": locked,
        "posture": posture,
        "claim": claim,
        "thesis": "LIVE is fused. Flags are RAM. Jailbreaks are not a product.",
        "gatekeep": "Proprietary firmware-fuse doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Firmware Fuse",
        "inventor": INVENTOR,
        "example_fused": flash(charge_id="chg_1", runtime_flag=False),
        "example_jailbreak": flash(runtime_flag=True, charge_id=None),
        "live": f"{base}/.well-known/firmware-fuse.json",
        "license_fuse": f"{base}/.well-known/license-fuse.json",
        "their_production": False,
    }
