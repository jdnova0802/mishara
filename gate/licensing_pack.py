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
LICENSED_FIELD_SPEC = "gate-licensed-field-v1"

PATENT_ID = "64/124,027"
OPERATOR = "Nisaba LLC"
COMMIT_AUTH_SPEC = "gate-commit-auth-v1"

# Default Licensed Field (Exhibit B) — platform primitive; insurance is carve-in Field A.
DEFAULT_LICENSED_FIELD = "platform_delegated_write"
GTM_FOOTHILL = "insurance_bind_moment_pas_mga"

# Audience plates — vertical GTM surfaces; not separate patent grants by default.
AUDIENCE_PLATES: tuple[str, ...] = (
    "developers",
    "agents",
    "startups",
    "operators",
    "legal",
    "compliance",
    "carriers",
    "brokers",
    "enterprise",
    "boards",
    "defense",
    "hiring",
    "consumers",
    "investors",
    "partners",
)


def _base(public_url: str) -> str:
    return (public_url or "").rstrip("/")


def licensed_field_manifest(public_url: str) -> dict[str, Any]:
    """Exhibit B — Licensed Field definition. Option B (platform) is default; A is carve-in."""
    base = _base(public_url)
    return {
        "spec": LICENSED_FIELD_SPEC,
        "exhibit": "B",
        "patent": PATENT_ID,
        "operator": OPERATOR,
        "status": "formal_draft_counsel_review",
        "default": DEFAULT_LICENSED_FIELD,
        "gtm_foothill_note": (
            "PAS/MGA insurance bind is the current outbound foothill (STRONGEST_START vertical lock) — "
            "not the default Licensed Field. Patent lane is media-agnostic per COMMIT_AUTH.md."
        ),
        "fields": {
            "platform_delegated_write": {
                "option": "B",
                "default": True,
                "grant": (
                    "Irreversible delegated-write control planes — any vertical — where a third party "
                    "can verify epoch HALT + stranger-grade receipt without admin resurrect."
                ),
                "includes_examples": [
                    "agent_tool_commits_mcp_mesh",
                    "payout_withdraw_clearance",
                    "enterprise_org_root_spend",
                    "defense_irreversible_release",
                    "hiring_aedt_decision_stick",
                    "legal_gc_irreversible_write",
                ],
                "plates": list(AUDIENCE_PLATES),
                "plate_base": f"{base}/for/{{slug}}",
            },
            "insurance_pas_mga": {
                "option": "A",
                "default": False,
                "carve_in": True,
                "grant": (
                    "Policy administration bind-and-issue and renewal batch bind paths for P&C or MGA "
                    "carriers in named states/countries — subset of platform field."
                ),
                "gtm_foothill": GTM_FOOTHILL,
                "regulatory_latch_module": "naic_adoption_latch",
                "implementation_sibling": "exhibit_d_snare",
            },
            "field_limited_oem": {
                "option": "C",
                "default": False,
                "grant": "Licensee product line embedded in named customer segment only.",
                "fill": "[LICENSEE PRODUCT LINE] · [CUSTOMER SEGMENT]",
            },
        },
        "excluded_fields": [
            "tier_z_military_c2_nuclear_weapons",
            "may_authority_resale_charge_equivalent",
            "consumer_payments_card_networks_when_unrelated_to_delegated_write",
            "general_iam_unrelated_to_irreversible_commit",
        ],
        "non_compete": "field_limited_only — licensor may license non-overlapping fields",
        "term_sheet_section": "§3 — Exhibit B",
        "commit_auth": f"{base}/.well-known/commit-auth.json",
    }


def qic_meter_manifest(public_url: str) -> dict[str, Any]:
    base = _base(public_url)
    return {
        "spec": QIC_METER_SPEC,
        "patent": PATENT_ID,
        "operator": OPERATOR,
        "licensed_field_default": DEFAULT_LICENSED_FIELD,
        "qic": {
            "name": "qualified_irreversible_commit",
            "definition": (
                "One server-side atomic redeem consume plus one irreversible write "
                "in the Licensed Field — vertical-agnostic (bind, payout, tool commit, release, etc.)."
            ),
            "counts_by_vertical_example": {
                "platform_agents": "tool_invocation_commit",
                "operators_payout": "withdraw_payout_stick",
                "enterprise": "delegated_org_write",
                "insurance_field_a": "new_business_bind",
                "insurance_field_a_renewal": "renewal_bind_when_commit_path_used",
                "defense": "irreversible_release_stick",
                "hiring": "aedt_decision_stick",
            },
            "excludes": [
                "quotes_rating_triage",
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
        "hybrid_bps_note": (
            "Cleared-flow or premium bps may apply instead of or stacked with per-QIC — "
            "see premium-bps-schedule.json."
        ),
        "term_sheet": "gate/PATENT_LICENSE_TERM_SHEET.md",
        "commit_auth": f"{base}/.well-known/commit-auth.json",
    }


def premium_bps_schedule_manifest(public_url: str) -> dict[str, Any]:
    """Exhibit I — basis-points on cleared flow / premium (multi-vertical)."""
    base = _base(public_url)
    return {
        "spec": PREMIUM_BPS_SPEC,
        "exhibit": "I",
        "patent": PATENT_ID,
        "operator": OPERATOR,
        "status": "formal_draft_counsel_review",
        "licensed_field_default": DEFAULT_LICENSED_FIELD,
        "meters": {
            "cleared_flow_bps": {
                "primary": True,
                "definition": "Basis points on dollar volume cleared through conformant irreversible-write path",
                "formula": "annual_royalty_usd = cleared_flow_usd × bps / 10_000",
                "verticals": [
                    "operators_payout_withdraw",
                    "enterprise_delegated_spend",
                    "agent_platform_gmv",
                    "insurance_field_a_npw",
                ],
            },
            "insurance_npw_bps": {
                "primary": False,
                "field_carve_in": "insurance_pas_mga",
                "definition": "Basis points on net premiums written through conformant bind path (Field A only)",
                "formula": "annual_royalty_usd = premium_volume_usd × bps / 10_000",
            },
        },
        "billable": "max(MAR, bps_royalty) when hybrid; counsel to define stack vs QIC-only deals",
        "illustrative_anchors": {
            "insurance_m1_full_us_npw": {
                "label": "Field A — 31 bps × ~$971B US P&C NPW (full penetration illustration)",
                "premium_volume_usd": 971_000_000_000,
                "bps": 31,
                "annual_usd": 300_910_000,
                "disclaimer": "Illustrative — not a forecast or offer.",
            },
            "operators_10bps_200b_cleared": {
                "label": "Platform — 10 bps × $200B cleared flow (operators plate analog)",
                "cleared_flow_usd": 200_000_000_000,
                "bps": 10,
                "annual_usd": 200_000_000,
                "disclaimer": "Illustrative — not a forecast or offer.",
            },
        },
        "licensee_tiers": [
            {
                "tier": "platform_field_b_default",
                "bps_range": [5, 25],
                "mar_usd_range": [250_000, 500_000],
                "meter": "cleared_flow_bps",
                "note": "Default license — agents, payout, enterprise, any irreversible delegated write",
            },
            {
                "tier": "operators_payout_igaming",
                "bps_range": [8, 15],
                "mar_usd_range": [100_000, 250_000],
                "meter": "cleared_flow_bps",
                "reference": "operators plate — 10 bps on cleared flow",
            },
            {
                "tier": "insurance_field_a_carve_in",
                "bps_range": [15, 62],
                "mar_usd_range": [50_000, 100_000],
                "meter": "insurance_npw_bps",
                "note": "Field A subset — MGA/PAS bind path only",
            },
            {
                "tier": "pas_oem_sublicense_field_a",
                "bps_range": [5, 25],
                "mar_usd_range": [250_000, 500_000],
                "meter": "insurance_npw_bps",
                "sublicense": "carrier NPW aggregated under Parent License ID",
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
        "licensed_field_default": DEFAULT_LICENSED_FIELD,
        "gtm_foothill": GTM_FOOTHILL,
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
            {"id": "distribution_policy", "path": "gate/DISTRIBUTION_POLICY.md", "role": "owner_liquid_policy"},
            {"id": "entity_map", "path": "gate/ENTITY_MAP.md", "role": "holdco_opco_personal_layers"},
            {"id": "personal_liquidity_stub", "path": "gate/PERSONAL_LIQUIDITY_STUB.md", "role": "post_distribution_personal_layer"},
            {"id": "ip_ownership_checklist", "path": "gate/IP_OWNERSHIP_CHECKLIST.md", "role": "pre_distribution_gate"},
            {"id": "pilot_contract_stub", "path": "gate/PILOT_CONTRACT_STUB.md", "role": "no_ip_assign_template"},
        ],
        "exhibits": {
            "A": "claim_chart_epoch_lock_commit_time",
            "B": f"{base}/.well-known/licensed-field.json",
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
            "licensed_field": f"{base}/.well-known/licensed-field.json",
            "premium_bps_schedule": f"{base}/.well-known/premium-bps-schedule.json",
            "gate_conformant_mark_spec": f"{base}/.well-known/gate-conformant-mark-spec.json",
            "qic_meter": f"{base}/.well-known/qic-meter.json",
            "epoch_lock_patent_asset": f"{base}/.well-known/epoch-lock-patent-asset.json",
            "ceiling_ladder": f"{base}/.well-known/ip-asset-ceiling-ladder.json",
            "commit_auth": f"{base}/.well-known/commit-auth.json",
            "owner_guardrails": f"{base}/.well-known/owner-guardrails.json",
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
            "agent_runtime_field_license": {
                "family": "ip-asset-ceiling",
                "well_known": f"{base}/.well-known/agent-runtime-field-license.json",
                "role": "platform_field_b_module",
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
