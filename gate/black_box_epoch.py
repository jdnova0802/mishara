"""Black Box Epoch — Svalbard black-box regime for HALT deposits.

Real institution: Svalbard Global Seed Vault (Norway / NordGen / Crop Trust).
Black-box regime: depositor retains ownership; only depositor may withdraw;
Norway holds the mountain, not the keys.

Twist: epoch HALT receipts deposited black-box — only carrier depositor + Velaru
CHARGE may withdraw/resurrect. Gate/Norway analog holds permanence, not may.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-black-box-epoch-v1"
INVENTION = "Black Box Epoch"
FAMILY = "institutional-twist"

REAL = {
    "institution": "Svalbard Global Seed Vault",
    "operators": ["Norwegian Ministry of Agriculture and Food", "NordGen", "Crop Trust"],
    "regime": "black_box — depositor-only withdrawal, ownership never transfers",
    "url": "https://www.seedvault.no/",
    "deposit_agreement": "seedvault.nordgen.org SGSV Deposit Agreement Art 3.3",
}


def deposit(
    *,
    depositor_id: str | None,
    job_id: str | None,
    halt_receipt: dict | None = None,
) -> dict[str, Any]:
    dep = (depositor_id or "").strip() or "DEPOSITOR_UNNAMED"
    jid = (job_id or "").strip() or None
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "real_institution": REAL,
        "black_box": True,
        "depositor_id": dep,
        "job_id": jid,
        "ownership_transfers": False,
        "vault_holds": "permanence_not_may",
        "withdrawal_allowed_for": [dep],
        "resurrect_requires": "velaru_charge_written_notice",
        "halt_receipt": halt_receipt or {},
        "rule": "Only the depositor withdraws its HALT — Norway holds the mountain.",
    }


def withdrawal_request(
    *,
    depositor_id: str | None,
    charge_id: str | None,
    impostor_admin: bool | None = None,
) -> dict[str, Any]:
    if impostor_admin and not charge_id:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "verdict": "DENIED",
            "reason": "black_box_depositor_only",
            "forged": True,
        }
    if charge_id:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "verdict": "WITHDRAWAL_ACCEPTED",
            "charge_id": charge_id,
            "regime_change": "written_notice_equivalent",
        }
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "verdict": "DENIED",
        "reason": "charge_notice_required",
    }


def attach(plan: dict) -> dict:
    if plan.get("halt") or (plan.get("decision") or "").upper() in ("HALT", "BLOCK"):
        plan["black_box_epoch"] = deposit(
            depositor_id=str(plan.get("account_id") or plan.get("fuse_id") or "carrier"),
            job_id=str(plan.get("job_id") or ""),
            halt_receipt={
                "event_id": plan.get("event_id"),
                "verify_url": plan.get("verify_url"),
                "epoch": plan.get("epoch"),
            },
        )
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Svalbard black-box for epoch HALT — depositor-only resurrection.",
        "real_institution": REAL,
        "demo_deposit": f"POST {base}/demo/pas/black-box-epoch/deposit",
        "demo_withdraw": f"POST {base}/demo/pas/black-box-epoch/withdraw",
        "well_known": f"{base}/.well-known/black-box-epoch.json",
        "pairs_with": "HALT Cemetery · Epoch lock",
    }
