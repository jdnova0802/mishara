"""IOMMU Door — devices cannot DMA around the mouth into LIVE.

IOMMU: peripherals cannot write arbitrary physical memory. Gate: PAS,
agents, and 'integrations' cannot DMA a bind into LIVE. Every irreversible
write is mapped through the exclusive door. Side-channel APIs are unmapped
bus masters — faults, not features.

Gatekeep only to ourselves: IOMMU → no DMA skip-clear.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-iommu-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def map_write(
    *,
    via_exclusive_door: bool | None = None,
    device: str | None = None,
    claimed_live: bool | None = None,
) -> dict[str, Any]:
    door = bool(via_exclusive_door)
    dev = (device or "").strip().lower()
    claimed = bool(claimed_live)
    dma = dev in ("side_api", "legacy_bind", "admin_panel", "partner_webhook") or dev.startswith("dma_")
    if claimed and not door:
        posture = "iommu_fault"
        claim = "unmapped_bus_master_cannot_write_live"
    elif dma and not door:
        posture = "unmapped_device"
        claim = "device_has_no_iova_to_live"
    elif door:
        posture = "mapped"
        claim = "write_translated_through_exclusive_door"
    else:
        posture = "idle"
        claim = "no_write"
    return {
        "spec": SPEC,
        "name": "IOMMU Door",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "IOMMU / VT-d / SMMU — devices cannot DMA untranslated",
            "Gate exclusive door — the only IOVA to irreversible spend",
        ],
        "via_exclusive_door": door,
        "device": dev or None,
        "claimed_live": claimed,
        "posture": posture,
        "claim": claim,
        "thesis": "Integrations are devices. They do not get a DMA hole to LIVE.",
        "gatekeep": "Proprietary IOMMU-door doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "IOMMU Door",
        "inventor": INVENTOR,
        "example_mapped": map_write(via_exclusive_door=True, device="pas_hop"),
        "example_fault": map_write(via_exclusive_door=False, claimed_live=True, device="side_api"),
        "live": f"{base}/.well-known/iommu.json",
        "nonorientable": f"{base}/.well-known/nonorientable.json",
        "their_production": False,
    }
