"""Clock Domain Crossing — PAS time is not weld time; CHARGE is the synchronizer.

CDC: two clocks cannot share a bit without a synchronizer or you get
metastable garbage. Gate: PolicyCenter 'now', agent 'now', and weld
epoch are different domains. Treating a PAS 200 as LIVE is an unsynced
bit. CHARGE is the two-flop synchronizer. Command radiation already
demands UTC now — this names why.

Gatekeep only to ourselves: CDC hardware → CHARGE as domain synchronizer.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-cdc-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sync(
    *,
    pas_ok: bool | None = None,
    weld_epoch_ok: bool | None = None,
    charge_id: str | None = None,
) -> dict[str, Any]:
    pas = bool(pas_ok)
    epoch = bool(weld_epoch_ok)
    charge = bool((charge_id or "").strip())
    if pas and not epoch and not charge:
        posture = "metastable_cdc"
        claim = "unsynchronized_pas_bit_is_not_live"
    elif charge and epoch:
        posture = "synchronized"
        claim = "charge_flops_the_bit_into_weld_domain"
    elif pas and epoch:
        posture = "same_domain_or_waiting"
        claim = "epoch_present_charge_still_required_for_live"
    else:
        posture = "idle_domains"
        claim = "no_crossing"
    return {
        "spec": SPEC,
        "name": "Clock Domain Crossing",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Digital CDC / dual-flop synchronizers — unsynced bits are poison",
            "Gate command radiation + epoch lock + CHARGE",
        ],
        "pas_ok": pas,
        "weld_epoch_ok": epoch,
        "charge_present": charge,
        "posture": posture,
        "claim": claim,
        "thesis": "PAS now and weld now are different clocks. CHARGE synchronizes. 200 does not.",
        "gatekeep": "Proprietary CDC doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Clock Domain Crossing",
        "inventor": INVENTOR,
        "example_meta": sync(pas_ok=True, weld_epoch_ok=False),
        "example_sync": sync(pas_ok=True, weld_epoch_ok=True, charge_id="chg_1"),
        "live": f"{base}/.well-known/cdc.json",
        "temporal_weld": f"{base}/.well-known/temporal-weld.json",
        "their_production": False,
    }
