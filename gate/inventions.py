"""Invention spine — physics multipliers, not SKUs.

Each invention is a fail-closed law at the mouth. Soft omit / soft resurrect /
museum cosplay are the overrides we kill.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-inventions-v1"


def catalog(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Gate inventions",
        "what": "Use-time physics at the irreversible mouth. Not a feature list.",
        "overrides_killed": [
            "soft license omit on welded mouths / GATE_LICENSE_REQUIRED=1",
            "canary bypass without auto-DEAD parent when license_id set",
            "redeem without use-time fuse LIVE recheck (TOCTOU)",
            "single CHARGE string opening both license and epoch gates",
            "DEAD→LIVE promotion at the Finality Sink under DEV panic",
            "exclusive door as museum label (harden when closed_world)",
            "screenshot Prefinality GO then spend without boundary reconstruction",
        ],
        "inventions": [
            {
                "spec": "gate-finality-sink-v1",
                "name": "Use-time Finality Sink",
                "manifest": f"{base}/.well-known/finality-sink.json",
                "law": "Fuse must still be LIVE at redeem. Hop ink is not spend grant.",
            },
            {
                "spec": "gate-license-fuse-v1",
                "name": "License Fuse",
                "manifest": f"{base}/.well-known/license-fuse.json",
                "law": "Children cannot outlive the parent. Welded mouths never soft-omit.",
            },
            {
                "spec": "gate-dual-charge-v1",
                "name": "Dual-gate CHARGE",
                "manifest": f"{base}/.well-known/dual-charge.json",
                "law": "DEAD→LIVE and HALT→ALLOW need two distinct charge authorities.",
            },
            {
                "spec": "gate-bypass-canary-v1",
                "name": "Bypass canary",
                "manifest": f"{base}/.well-known/canary.json",
                "law": "Suspected bypass + named parent → DEAD by default.",
            },
            {
                "spec": "gate-register-bill-v1",
                "name": "Register bill",
                "manifest": f"{base}/.well-known/register-bill.json",
                "law": "Management + bps + carry from cleared-flow ledger.",
            },
            {
                "spec": "gate-exclusive-timing-v1",
                "name": "Exclusive timing (hardened)",
                "manifest": f"{base}/.well-known/bound-answer.json",
                "law": "Closed-world door: bypass and CHARGE must cost more than the act.",
            },
            {
                "spec": "gate-settlement-v1",
                "name": "Settlement engine",
                "manifest": f"{base}/.well-known/settlement.json",
                "write": f"{base}/v1/settlement/window/open",
                "law": "DTCC-shaped netting + windows + waterfall. Fail closed.",
            },
            {
                "spec": "gate-exclusion-v1",
                "name": "Exclusion / proof of spend",
                "manifest": f"{base}/.well-known/exclusion.json",
                "law": "Spent leaf in Gate's map. Absence is bypass evidence, not metaphysical non-event.",
            },
            {
                "spec": "gate-prefinality-reconstruction-v1",
                "name": "Prefinality reconstruction-as-law",
                "manifest": f"{base}/.well-known/prefinality-reconstruction.json",
                "law": "Clear ⇔ Reconstruct = presented ∧ LIVE. Possession of GO is not finality.",
            },
        ],
        "their_production": False,
        "page": f"{base}/inventions",
    }
