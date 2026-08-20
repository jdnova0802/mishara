"""Secure Boot Regime — only CHARGE-signed images of LIVE may boot.

Secure boot: the CPU refuses unsigned kernels. Gate: DEAD will not boot
LIVE unless the image is CHARGE-signed (named witness, epoch, fuse).
Admin toggles are unsigned kernels. Copycats allow 'dev mode' in
production. That is insecure boot.

Gatekeep only to ourselves: UEFI secure boot → CHARGE as the only LIVE signer.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-secure-boot-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def boot(
    *,
    charge_id: str | None = None,
    unsigned_live: bool | None = None,
    prod: bool | None = None,
) -> dict[str, Any]:
    charge = bool((charge_id or "").strip())
    unsigned = bool(unsigned_live)
    production = bool(prod)
    if unsigned and production:
        posture = "insecure_boot"
        claim = "unsigned_live_in_production"
    elif charge:
        posture = "secure_boot"
        claim = "charge_signed_live_image"
    elif unsigned:
        posture = "unsigned_refused"
        claim = "dead_holds_without_signer"
    else:
        posture = "unbooted"
        claim = "no_live_image"
    return {
        "spec": SPEC,
        "name": "Secure Boot Regime",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "UEFI/verified boot — unsigned kernels do not run",
            "Gate firmware fuse + CHARGE-only DEAD→LIVE",
        ],
        "charge_present": charge,
        "unsigned_live": unsigned,
        "production_claimed": production,
        "posture": posture,
        "claim": claim,
        "thesis": "LIVE is a signed boot. Dev-mode production is a bricked cosmos.",
        "gatekeep": "Proprietary secure-boot regime doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Secure Boot Regime",
        "inventor": INVENTOR,
        "example_ok": boot(charge_id="chg_1"),
        "example_bad": boot(unsigned_live=True, prod=True),
        "live": f"{base}/.well-known/secure-boot.json",
        "firmware_fuse": f"{base}/.well-known/firmware-fuse.json",
        "their_production": False,
    }
