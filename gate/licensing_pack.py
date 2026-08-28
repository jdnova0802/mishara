"""Formal patent licensing pack — canonical well-known index for 64/124,027.

Not an invention batch. Indexes term sheet, exhibits, meter specs, and the three
formal IP modules in ip_asset_ceiling without duplicating evaluate_slug registries.

Cross-refs (do not duplicate logic):
- exhibit_d_snare.py — NAIC AIS implementation snare
- ip_asset_ceiling.naic_adoption_latch — IP volume-latch formal module
- ip_asset_deep.epoch_lock_patent_asset — patent asset evaluator
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-licensing-pack-v1"
PREMIUM_BPS_SPEC = "gate-premium-bps-schedule-v1"
CONFORMANT_MARK_SPEC = "gate-conformant-mark-spec-v1"
QIC_METER_SPEC = "gate-qic-meter-v1"

PATENT_ID = "64/124,027"
OPERATOR = "Nisaba LLC"
COMMIT_AUTH_SPEC = "gate-commit-auth-v1"


def _base(public_url: str) -> str:
    return (public_url or "").rstrip("/")


def qic_meter_manifest(public_url: str) -> dict[str, Any]:
    base = _base(public_url)
    return {
        "spec": QIC_METER_SPEC,
        "patent": PATENT_ID,
        "operator": OPERATOR,
        "qic": {
            "name": "qualified_irreversible_commit",
            "definition": (
                "One server-side atomic redeem consume plus one irreversible bind write "
                "in the Licensed Field."
            ),
            "counts": [
                "new_business_bind",
                "renewal_bind_when_commit_path_used",
            ],
            "excludes": [
                "quotes_and_rating",
                "failed_redeem_attempts",
                "read_only_hops",
                "dashboard_green_without_irreversible_write",
            ],
        },
        "caq": {
            "name": "contracted_annual_qic",
            "definition": "Volume commitment in license agreement (tier / overage).",
        },
        "laq": {
            "name": "licensed_actual_annual_qic",
            "definition": "Metered actual events reported quarterly under §8.",
        },
        "billable_formula": "max(MAR, LAQ × per_QIC_rate)",
        "hybrid_bps_note": "Premium bps schedule may apply instead of or stacked with per-QIC — see premium-bps-schedule.json.",
        "term_sheet": "gate/PATENT_LICENSE_TERM_SHEET.md",
        "commit_auth": f"{base}/.well-known/commit-auth.json",
    }


def premium_bps_schedule_manifest(public_url: str) -> dict[str, Any]:
    """Exhibit I — formal premium basis-points schedule (Qualcomm-on-NPW analog)."""
    base = _base(public_url)
    return {
        "spec": PREMIUM_BPS_SPEC,
        "exhibit": "I",
        "patent": PATENT_ID,
        "operator": OPERATOR,
        "status": "formal_draft_counsel_review",
        "meter": "premium_net_premiums_written_through_conformant_bind_path",
        "formula": "annual_royalty_usd = premium_volume_usd × bps / 10_000",
        "billable": "max(MAR, premium_bps_royalty) when hybrid; counsel to define stack vs QIC-only deals",
        "illustrative_m1_anchor": {
            "label": "M1 — $300M start (full US penetration illustration only)",
            "premium_volume_usd": 971_000_000_000,
            "bps": 31,
            "annual_usd": 300_910_000,
            "disclaimer": "Illustrative — not a forecast or offer.",
        },
        "licensee_tiers": [
            {
                "tier": "mga_field_a",
                "bps_range": [15, 62],
                "mar_usd_range": [50_000, 100_000],
                "typical_npW_share": "single_program",
            },
            {
                "tier": "pas_oem_field_b",
                "bps_range": [5, 25],
                "mar_usd_range": [250_000, 500_000],
                "sublicense": "carrier NPW aggregated under Parent License ID",
            },
            {
                "tier": "scale_partial_us",
                "bps_range": [10, 20],
                "note": "20% US NPW × 20 bps ≈ $388M/yr illustrative stack component",
            },
        ],
        "formal_module": f"{base}/.well-known/premium-bps-meter.json",
        "demo": f"POST {base}/demo/pas/premium-bps-meter",
        "term_sheet_section": "§7.2 — Exhibit I",
    }


def gate_conformant_mark_spec_manifest(public_url: str) -> dict[str, Any]:
    """Exhibit J — Gate Conformant™ franchise spec (PCI/UL-class, trademark separate)."""
    base = _base(public_url)
    return {
        "spec": CONFORMANT_MARK_SPEC,
        "exhibit": "J",
        "patent": PATENT_ID,
        "operator": OPERATOR,
        "status": "formal_draft_counsel_review",
        "mark": "Gate Conformant",
        "mark_note": "Trademark license separate from patent license — not granted in default patent template.",
        "requirements": [
            "epoch_lock_persisted_until_charge_class_event",
            "single_use_server_redeem",
            "fail_closed_redeem",
            "override_impossibility_no_forged_resurrection",
            "stranger_verify_receipt_without_operator_narration",
            "license_fuse_cascade_when_sublicensing",
            "annual_attestation_signed_by_officer",
        ],
        "conformance_refs": {
            "commit_auth": f"{base}/.well-known/commit-auth.json",
            "spend_protocol": f"{base}/.well-known/spend-protocol.json",
            "override_impossibility": f"{base}/.well-known/override-impossibility.json",
        },
        "fee_model": {
            "type": "certification_franchise",
            "formula": "annual_usd = certified_implementers × cert_fee_annual",
            "illustrative_m1_anchor": {
                "implementers": 10_000,
                "cert_fee_annual_usd": 30_000,
                "annual_usd": 300_000_000,
                "disclaimer": "Illustrative — not a forecast or offer.",
            },
        },
        "ghost_conformant": "DENY — attestation without test pass is ghost certification",
        "formal_module": f"{base}/.well-known/gate-conformant-mark.json",
        "demo": f"POST {base}/demo/pas/gate-conformant-mark",
        "term_sheet_section": "§11 + Exhibit J",
    }


def pack_manifest(public_url: str) -> dict[str, Any]:
    """Canonical licensing pack index — single stranger-grade entry point."""
    base = _base(public_url)
    return {
        "spec": SPEC,
        "status": "formal_draft_counsel_review",
        "patent": PATENT_ID,
        "operator": OPERATOR,
        "commit_auth_spec": COMMIT_AUTH_SPEC,
        "claims_licensed_default": ["epoch_lock", "commit_time_single_use_bind"],
        "not_in_default_patent_grant": [
            "velaru_charge_may_authority",
            "trademark",
            "copyright_except_exhibit_i_j_as_negotiated",
            "112_invention_module_names_as_brand_positioning",
        ],
        "documents": [
            {"id": "term_sheet", "path": "gate/PATENT_LICENSE_TERM_SHEET.md", "role": "skeleton"},
            {"id": "exhibit_redacted", "path": "gate/PATENT_LICENSE_EXHIBIT_REDACTED.md", "role": "sendable_one_pagers"},
            {"id": "event_potential", "path": "gate/PATENT_LICENSE_EVENT_POTENTIAL.md", "role": "qic_model"},
            {"id": "ceiling_ladder", "path": "gate/IP_ASSET_CEILING.md", "role": "upside_ladder_doc"},
        ],
        "exhibits": {
            "A": "claim_chart_epoch_lock_commit_time",
            "B": "licensed_field_and_exclusions",
            "C": "conformance_spec_commit_auth",
            "D": "source_sdk_tier_2",
            "E": "trademark_guidelines",
            "F": "sublicense_license_fuse_cascade",
            "G": "fee_schedule_upfront_mar_qic",
            "H": "frand_letter_optional",
            "I": f"{base}/.well-known/premium-bps-schedule.json",
            "J": f"{base}/.well-known/gate-conformant-mark-spec.json",
            "K": f"{base}/.well-known/qic-meter.json",
        },
        "well_known": {
            "pack": f"{base}/.well-known/licensing-pack.json",
            "premium_bps_schedule": f"{base}/.well-known/premium-bps-schedule.json",
            "gate_conformant_mark_spec": f"{base}/.well-known/gate-conformant-mark-spec.json",
            "qic_meter": f"{base}/.well-known/qic-meter.json",
            "epoch_lock_patent_asset": f"{base}/.well-known/epoch-lock-patent-asset.json",
            "ceiling_ladder": f"{base}/.well-known/ip-asset-ceiling-ladder.json",
            "commit_auth": f"{base}/.well-known/commit-auth.json",
        },
        "formal_modules": {
            "epoch_lock_patent_asset": {
                "family": "ip-asset-deep",
                "well_known": f"{base}/.well-known/epoch-lock-patent-asset.json",
            },
            "premium_bps_meter": {
                "family": "ip-asset-ceiling",
                "well_known": f"{base}/.well-known/premium-bps-meter.json",
                "exhibit": "I",
            },
            "gate_conformant_mark": {
                "family": "ip-asset-ceiling",
                "well_known": f"{base}/.well-known/gate-conformant-mark.json",
                "exhibit": "J",
            },
            "naic_adoption_latch": {
                "family": "ip-asset-ceiling",
                "well_known": f"{base}/.well-known/naic-adoption-latch.json",
                "role": "regulatory_volume_driver",
                "implementation_sibling": "exhibit_d_snare",
                "note": "Latch multiplies LAQ; does not replace exhibit_d_snare evaluator.",
            },
        },
        "meter": qic_meter_manifest(public_url)["billable_formula"],
        "first_deal_target": "one_field_limited_paid_license_with_auditable_LAQ",
        "counsel": "Review before execution — not legal advice.",
    }
