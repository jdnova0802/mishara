"""Owner guardrails — royalty path, distribution policy, IP non-assign (not legal advice).

Indexes formal MD stubs for stranger-grade diligence. Does not duplicate licensing_pack meters.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-owner-guardrails-v1"
OPERATOR = "Nisaba LLC"
FORMATION_STATE = "Wyoming"
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

OWNER_DISTRIBUTION_PCT = DISTRIBUTION_SPLIT["buckets"]["owner_distribution"]


def compute_personal_wire(
    *,
    company_gross_annual_usd: float = 0,
    opex_annual_usd: float = 0,
    salary_annual_usd: float = 0,
    reserve_funded: bool = False,
    owner_ownership_pct: float = 1.0,
) -> dict[str, Any]:
    """Company cash → personal take-home (pre-tax). Not tax or legal advice."""
    gross = max(0.0, float(company_gross_annual_usd))
    opex = max(0.0, float(opex_annual_usd)) + max(0.0, float(salary_annual_usd))
    own = min(1.0, max(0.0, float(owner_ownership_pct)))
    excess = max(0.0, gross - opex) if reserve_funded else 0.0
    owner_distribution = excess * OWNER_DISTRIBUTION_PCT * own
    salary = max(0.0, float(salary_annual_usd))
    personal_annual = owner_distribution + salary
    return {
        "spec": "gate-personal-wire-calculator-v1",
        "disclaimer": "Pre-tax illustrative wire math — not tax or legal advice.",
        "inputs": {
            "company_gross_annual_usd": gross,
            "opex_annual_usd": float(opex_annual_usd),
            "salary_annual_usd": salary,
            "reserve_funded": bool(reserve_funded),
            "owner_ownership_pct": own,
        },
        "company": {
            "gross_annual_usd": gross,
            "opex_including_salary_usd": opex,
            "excess_fcf_annual_usd": excess,
            "distribution_blocked_reason": None
            if reserve_funded
            else "reserve_not_funded_need_6mo_opex_before_owner_distribution",
        },
        "personal_pretax": {
            "owner_distribution_annual_usd": round(owner_distribution, 2),
            "salary_annual_usd": salary,
            "total_annual_usd": round(personal_annual, 2),
            "total_monthly_usd": round(personal_annual / 12, 2),
            "owner_distribution_formula": "max(0, gross - opex - salary) × 0.30 × ownership_pct",
        },
        "policy_ref": "gate/DISTRIBUTION_POLICY.md",
    }


WIRE_SCENARIO_PRESETS: tuple[dict[str, Any], ...] = (
    {
        "label": "gate_1_year",
        "company_gross_annual_usd": 75_000,
        "opex_annual_usd": 60_000,
        "salary_annual_usd": 0,
        "reserve_funded": False,
    },
    {
        "label": "early_business",
        "company_gross_annual_usd": 500_000,
        "opex_annual_usd": 150_000,
        "salary_annual_usd": 75_000,
        "reserve_funded": True,
    },
    {
        "label": "real_recurring",
        "company_gross_annual_usd": 2_000_000,
        "opex_annual_usd": 400_000,
        "salary_annual_usd": 120_000,
        "reserve_funded": True,
    },
    {
        "label": "ten_m_company",
        "company_gross_annual_usd": 10_000_000,
        "opex_annual_usd": 2_500_000,
        "salary_annual_usd": 250_000,
        "reserve_funded": True,
    },
)


def wire_calculator_manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    presets = [
        {"label": p["label"], **compute_personal_wire(**{k: v for k, v in p.items() if k != "label"})}
        for p in WIRE_SCENARIO_PRESETS
    ]
    return {
        "spec": "gate-personal-wire-calculator-v1",
        "disclaimer": "Pre-tax personal wire math — CPA for tax; counsel for distributions.",
        "formula": compute_personal_wire(reserve_funded=True, company_gross_annual_usd=1)["personal_pretax"][
            "owner_distribution_formula"
        ],
        "distribution_split": DISTRIBUTION_SPLIT,
        "demo": f"POST {base}/demo/pas/personal-wire-calculator",
        "example_presets": presets,
        "income_context": {
            "note": "Order-of-magnitude global context — not a Gate forecast.",
            "ten_m_plus_pretax_annual_global": "~40,000–80,000 people (not hundreds)",
            "one_m_plus_pretax_annual_global": "~500,000–1,500,000 people",
            "hundred_m_plus_pretax_spike_year_global": "~1,000–5,000 people",
            "hundred_m_plus_recurring_takehome_structured_global": "~50–800 people",
            "source_hint": "IRS SOI high-income returns; top-400 turnover; global extrapolation",
        },
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "operator": OPERATOR,
        "formation_state": FORMATION_STATE,
        "status": "formal_operating_stubs_counsel_review",
        "not_legal_advice": True,
        "royalty_waterfall": ROYALTY_WATERFALL,
        "distribution_policy": DISTRIBUTION_SPLIT,
        "documents": {
            "distribution_policy": "gate/DISTRIBUTION_POLICY.md",
            "entity_map": "gate/ENTITY_MAP.md",
            "personal_liquidity_stub": "gate/PERSONAL_LIQUIDITY_STUB.md",
            "ip_ownership_checklist": "gate/IP_OWNERSHIP_CHECKLIST.md",
            "pilot_contract_stub": "gate/PILOT_CONTRACT_STUB.md",
            "patent_counsel_brief": "gate/PATENT_COUNSEL_BRIEF.md",
            "licensed_field_value": "gate/LICENSED_FIELD_VALUE.md",
            "wealth_apparatus_freeze": "gate/WEALTH_APPARATUS_FREEZE.md",
            "mouth_ceiling": "gate/MOUTH_CEILING.md",
            "business_categories": "gate/BUSINESS_CATEGORIES.md",
            "licensing_pack": f"{base}/.well-known/licensing-pack.json",
            "wire_calculator": f"{base}/.well-known/personal-wire-calculator.json",
        },
        "gate1_work_order": {
            "licensed_field_value": "gate/LICENSED_FIELD_VALUE.md",
            "patent_counsel_brief": "gate/PATENT_COUNSEL_BRIEF.md",
            "wealth_frozen_until_gate1": "gate/WEALTH_APPARATUS_FREEZE.md",
            "mouth_ceiling_enforced": "gate/mouth_ceiling_guard.py",
            "only_work_until_gate1": "non_provisional_quote_then_stranger_paid_proved",
            "counsel_week": "gate/PATENT_COUNSEL_BRIEF.md",
            "counsel_do_not_attach": [
                "112_invention_modules",
                "exhibits_a_through_k",
                "ip_asset_ceiling_ladder",
                "licensing_revenue_models",
            ],
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
            "entity_map_holdco_opco_personal_layers",
            "patent_assigned_to_nisaba",
            "member_cap_table_documented",
            "ops_bank_separate_from_owner_personal",
            "distribution_policy_adopted",
            "personal_liquidity_triggers_when_distributions_start",
            "pilot_template_no_ip_assign",
        ],
        "well_known": {
            "guardrails": f"{base}/.well-known/owner-guardrails.json",
            "wire_calculator": f"{base}/.well-known/personal-wire-calculator.json",
            "licensing_pack": f"{base}/.well-known/licensing-pack.json",
            "legal": f"{base}/.well-known/legal.json",
        },
        "wire_calculator": f"{base}/.well-known/personal-wire-calculator.json",
    }
