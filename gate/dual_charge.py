"""Dual-gate CHARGE — resurrection requires two authorities.

DEAD→LIVE (license parent) and HALT→ALLOW (epoch on a job) are separate
charges. Dual-gate means both must clear when both gates are locked:

  license_charge_id  → purpose=license, subject=license_id
  epoch_charge_id    → purpose=epoch,   subject=job_id

One string cannot open both doors. Soft single-CHARGE is the override we kill.
"""
from __future__ import annotations

from typing import Any

try:
    from gate import charge_authority as charge_mod
except ImportError:
    import charge_authority as charge_mod

try:
    from gate import license_fuse as license_fuse_mod
except ImportError:
    import license_fuse as license_fuse_mod

try:
    from gate import epoch as epoch_mod
except ImportError:
    import epoch as epoch_mod

SPEC = "gate-dual-charge-v1"
REASON_LICENSE_CHARGE = "license_charge_id_required"
REASON_EPOCH_CHARGE = "epoch_charge_id_required"
REASON_BOTH = "dual_gate_charge_required"


def unlock(
    *,
    license_id: str | None,
    job_id: str | None,
    license_charge_id: str | None,
    epoch_charge_id: str | None,
    require_epoch: bool = True,
    require_license: bool = True,
) -> dict[str, Any]:
    """Apply both CHARGE gates. Fail closed if either required leg is missing/invalid."""
    out: dict[str, Any] = {
        "spec": SPEC,
        "ok": False,
        "halt": True,
        "dual_gate": True,
        "license": None,
        "epoch": None,
    }
    need_lic = bool(require_license and license_id)
    need_ep = bool(require_epoch and job_id)

    if need_lic and not charge_mod.normalize(license_charge_id):
        out["reason"] = REASON_LICENSE_CHARGE
        return out
    if need_ep and not charge_mod.normalize(epoch_charge_id):
        out["reason"] = REASON_EPOCH_CHARGE
        return out
    if need_lic and need_ep:
        lic_cid = charge_mod.normalize(license_charge_id)
        ep_cid = charge_mod.normalize(epoch_charge_id)
        if lic_cid and ep_cid and lic_cid == ep_cid:
            out["reason"] = REASON_BOTH
            out["hint"] = "license_charge_id and epoch_charge_id must be distinct authorities"
            return out

    license_result = None
    if need_lic:
        license_result = license_fuse_mod.charge(
            license_id=license_id,
            charge_id=license_charge_id,
        )
        out["license"] = license_result
        if not license_result.get("ok"):
            out["reason"] = license_result.get("reason") or REASON_LICENSE_CHARGE
            return out

    epoch_meta = None
    if need_ep:
        # Probe lock then accept distinct epoch charge via a synthetic ALLOW hop.
        hop = {"halt": False, "verdict": True, "state": "LIVE"}
        hop_d, epoch_meta = epoch_mod.apply(
            job_id=job_id,
            hop=hop,
            charge_id=epoch_charge_id,
        )
        out["epoch"] = epoch_meta
        if epoch_meta.get("locked"):
            out["reason"] = epoch_meta.get("reason") or REASON_EPOCH_CHARGE
            out["hop"] = hop_d
            return out

    out.update({"ok": True, "halt": False, "reason": None})
    return out


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Dual-gate CHARGE",
        "what": "DEAD→LIVE and HALT→ALLOW need two distinct charge authorities.",
        "not": [
            "one admin string opens everything",
            "Velaru admin CHARGE cosplay",
            "soft resurrect for nice buyers",
        ],
        "post": f"{base}/v1/pas/dual-charge",
        "demo": f"{base}/demo/pas/dual-charge",
        "legs": ["license_charge_id", "epoch_charge_id"],
        "their_production": False,
    }
