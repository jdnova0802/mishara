"""Owner guardrails — royalty path, distribution policy, IP non-assign (not legal advice).

Indexes formal MD stubs for stranger-grade diligence. Does not duplicate licensing_pack meters.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-owner-guardrails-v1"
OPERATOR = "Nisaba LLC"
PATENT_ID = "64/124,027"

IP_NON_ASSIGN_ONE_LINER = (
    "No IP assignment. Nisaba LLC retains all patents, specs, and marks. Pilot is use-only under defined scope."
)

IP_NON_ASSIGN_BLOCK = (
    "Customer receives no ownership, assignment, or exclusive license to Licensor's patents "
    f"(including US Provisional {PATENT_ID} and continuations), copyrights, trade secrets, "
    "Gate commit-auth specifications, or Velaru / Gate marks."
)

DISTRIBUTION_SPLIT = {
    "trigger": "company_holds_gte_6_months_opex_reserve",
    "buckets": {
        "runway_lattice_reserve": 0.30,
        "team_partner_pool": 0.20,
        "owner_distribution": 0.30,
        "growth_welds": 0.20,
    },
    "owner_equity_target_pct": "70-80 through age 30 unless non-may deal raises liquid",
}

ROYALTY_WATERFALL = [
    "licensee_pays_nisaba_llc_licensor",
    "company_bank_mar_qic_bps_cert",
    "distribution_policy_on_excess_fcf",
    "owner_distribution_30pct_of_excess",
]


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "operator": OPERATOR,
        "patent": PATENT_ID,
        "status": "formal_operating_stubs_counsel_review",
        "not_legal_advice": True,
        "royalty_waterfall": ROYALTY_WATERFALL,
        "distribution_policy": DISTRIBUTION_SPLIT,
        "documents": {
            "distribution_policy": "gate/DISTRIBUTION_POLICY.md",
            "ip_ownership_checklist": "gate/IP_OWNERSHIP_CHECKLIST.md",
            "pilot_contract_stub": "gate/PILOT_CONTRACT_STUB.md",
            "licensing_pack": f"{base}/.well-known/licensing-pack.json",
        },
        "pilot_guardrails": {
            "ip_non_assign_one_liner": IP_NON_ASSIGN_ONE_LINER,
            "ip_non_assign_block": IP_NON_ASSIGN_BLOCK,
            "no_personal_guarantee": True,
            "no_override_key": True,
            "no_may_in_patent_license": True,
            "name_death": True,
            "floor_and_bps_path": True,
        },
        "ownership_checklist_summary": [
            "nisaba_llc_licensor_of_record",
            "patent_assigned_to_nisaba",
            "member_cap_table_documented",
            "ops_bank_separate_from_owner_personal",
            "distribution_policy_adopted",
            "pilot_template_no_ip_assign",
        ],
        "well_known": {
            "guardrails": f"{base}/.well-known/owner-guardrails.json",
            "licensing_pack": f"{base}/.well-known/licensing-pack.json",
            "legal": f"{base}/.well-known/legal.json",
        },
    }
