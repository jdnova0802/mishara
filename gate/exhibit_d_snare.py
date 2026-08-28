"""Exhibit D Snare — NAIC AIS Evaluation Tool ghost detector.

Real institution: NAIC AI Systems Evaluation Tool (12-state pilot Mar–Sep 2026;
Fall National Meeting adoption target Nov 2026). Exhibits A–D — Exhibit D is
data integrity / input lineage examiners hammer.

Ghost: written AIS Program that cannot produce bind-path artifacts Gate already stamps.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-exhibit-d-snare-v1"
INVENTION = "Exhibit D Snare"
FAMILY = "institutional-twist"

REAL = {
    "institution": "NAIC Big Data and Artificial Intelligence (H) Working Group",
    "instrument": "AI Risk Evaluation Supplement (formerly AI Systems Evaluation Tool)",
    "pilot": "March–September 2026, 12 states",
    "adoption_target": "November 2026 Fall National Meeting (v7.0)",
    "exhibits": ["A_inventory", "B_governance", "C_high_risk", "D_model_data"],
    "url": "https://content.naic.org/industry/artificial-intelligence",
}


def scan(scenario: dict | None = None) -> dict[str, Any]:
    s = scenario if isinstance(scenario, dict) else {}
    ghosts: list[dict[str, str]] = []

    def g(code: str, detail: str) -> None:
        ghosts.append({"ghost": code, "detail": detail, "exhibit": "D"})

    if s.get("ais_program_claimed") and not s.get("bind_artifact_trail"):
        g("exhibit_d_no_trail", "AIS Program claimed but no bind-path artifact trail for Exhibit D.")
    if s.get("vendor_ai_bind") and not s.get("audit_rights_exercised"):
        g("vendor_black_box", "Third-party bind AI with no exercised audit rights — Exhibit B ghost.")
    if s.get("high_risk_bind") and not s.get("epoch_lock_documented"):
        g("exhibit_c_no_epoch", "High-risk bind automation with no epoch-lock documentation.")
    if s.get("drift_detected") and not s.get("stop_procedure_tested"):
        g("no_tested_shutdown", "Model drift noted; no tested shutdown per AM Best / NAIC posture.")
    if s.get("human_review") and s.get("every_review_approved"):
        g("procedural_click", "Human review always approves — procedural click, not HITL.")

    haunted = bool(ghosts)
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "real_institution": REAL,
        "haunted": haunted,
        "ghosts": ghosts,
        "verdict": "EXAMINER_HAUNTED" if haunted else "EXHIBIT_READY",
        "gate_fills": [
            "halt_cemetery",
            "refuse_ledger",
            "override_impossibility",
            "commit_auth",
        ],
        "rule": "NAIC Exhibit D wants data integrity — produce bind artifacts or haunt.",
    }


def compile_exhibits(*, plan: dict | None = None) -> dict[str, Any]:
    p = plan if isinstance(plan, dict) else {}
    return {
        "spec": SPEC,
        "exhibits": {
            "A_inventory": {
                "bind_path": "PAS PolicyCenter pre-bind + bind-only spend protocol",
                "gate_modules": ["throat", "bind_ticket", "epoch", "spend_protocol"],
            },
            "B_governance": {
                "epoch_lock": (p.get("epoch") or {}).get("rule"),
                "charge_only_resurrect": True,
                "fail_closed": True,
            },
            "C_high_risk": {
                "job_id": p.get("job_id"),
                "mass_class": (p.get("stick_meter") or {}).get("mass_class"),
                "allow_bind": p.get("allow_bind"),
            },
            "D_data_integrity": {
                "event_id": p.get("event_id"),
                "verify_url": p.get("verify_url"),
                "receipt_hash": p.get("receipt_hash"),
                "halt_cemetery": (p.get("halt_cemetery") or {}).get("stone_id"),
                "refuse_ledger": (p.get("refuse_ledger") or {}).get("line_id"),
            },
        },
        "naic_pilot_ready": bool(p.get("verify_url")),
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "NAIC AIS Exhibit D snare — bind artifact trail or examiner haunt.",
        "real_institution": REAL,
        "demo": f"POST {base}/demo/pas/exhibit-d-snare",
        "compile": f"POST {base}/demo/pas/exhibit-d-compile",
        "well_known": f"{base}/.well-known/exhibit-d-snare.json",
    }
