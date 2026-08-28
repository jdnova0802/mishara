"""IP Asset Ceiling — 24 experimental IP-X inventions for nine-figure → twelve-figure upside.

Registry pattern matches ip_asset_deep; tier IP-X = experimental scale path (not shipped product claims).
Fills gaps: conformance franchise, premium bps, agent field, pool operator, registry SaaS, interchange analogs.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

FAMILY = "ip-asset-ceiling"
TIER = "IP-X"

SLUGS: tuple[str, ...] = (
    "gate_conformant_mark",
    "premium_bps_meter",
    "agent_runtime_field_license",
    "patent_pool_operator_toll",
    "ietf_profile_spec_asset",
    "fuse_registry_meter_saas",
    "naic_adoption_latch",
    "visa_interchange_commit_analog",
    "swift_iso20022_message_toll",
    "stripe_connect_platform_cut",
    "eu_ai_act_essential_pack",
    "fedwire_oc6_finality_fee",
    "bis_agora_atomic_toll",
    "mcp_mesh_commit_meter",
    "agent_fleet_rcc_bundle",
    "edge_worker_bind_surcharge",
    "securitized_royalty_spv_live",
    "forward_royalty_catalog_sale",
    "ip_receipt_index_fund",
    "stranger_grade_benchmark_feed",
    "rfc3161_timestamp_toll",
    "cross_border_pct_cascade",
    "trillion_qic_step_ladder",
    "planetary_quorum_license",
)

assert len(SLUGS) == 24, f"expected 24 slugs, got {len(SLUGS)}"
assert len(set(SLUGS)) == 24, "SLUGS must be unique"


def slug_to_kebab(slug: str) -> str:
    return (slug or "").strip().lower().replace("_", "-")


def _spec(slug: str) -> str:
    return f"gate-{slug_to_kebab(slug)}-v1"


def _out(slug: str, invention: str, real: dict[str, Any], verdict: str, **extra: Any) -> dict[str, Any]:
    return {
        "spec": _spec(slug),
        "invention": invention,
        "tier": TIER,
        "verdict": verdict,
        "real_institution": real,
        **extra,
    }


def _illustrative_ceiling(
    laq: float = 0,
    rate: float = 0,
    premium_volume_usd: float = 0,
    bps: float = 0,
    cert_holders: float = 0,
    cert_fee_annual: float = 0,
    override_usd: float | None = None,
) -> float | None:
    """Optional upside hint from scenario inputs (USD/yr, not a forecast)."""
    if override_usd is not None:
        return float(override_usd)
    if premium_volume_usd and bps:
        return premium_volume_usd * bps / 10_000
    if laq and rate:
        return laq * rate
    if cert_holders and cert_fee_annual:
        return cert_holders * cert_fee_annual
    return None


# ---------------------------------------------------------------------------
# Real institutions (web-verifiable anchors where possible)
# ---------------------------------------------------------------------------

_REAL_CONFORMANT = {
    "institution": "PCI SSC + UL Mark — conformance certification franchises",
    "analog": "Annual assessor/recert fees × implementer count, not per-transaction alone",
    "url": "https://www.pcisecuritystandards.org/",
    "note": "Gate Conformant™ path: trademark + test suite copyright + annual attestation.",
}

_REAL_PREMIUM_BPS = {
    "institution": "Qualcomm ASP royalty — adapted to premium bound (NPW meter)",
    "analog": "Basis points on premium flowing through conformant bind path",
    "url": "https://www.qualcomm.com/licensing",
    "note": "31 bps × ~$971B US P&C NPW ≈ $300M/yr at full US penetration.",
}

_REAL_AGENT_FIELD = {
    "institution": "Cloud agent runtimes — delegated irreversible write control planes",
    "analog": "Licensed Field B: enterprise + MCP mesh commit primitives",
    "url": "https://arxiv.org/abs/2603.09875",
    "note": "Parakhin RCC: billions of agent-speed commits >> insurance bind ceiling.",
}

_REAL_POOL_OP = {
    "institution": "MPEG LA / Via Licensing — patent pool operator admin toll",
    "analog": "Admin fee on every pool sublicense + essentiality review",
    "url": "https://www.mpegla.com/",
    "note": "Pool operator cut is recurring infrastructure, not single patent license.",
}

_REAL_IETF_SPEC = {
    "institution": "IETF Trust — RFC/copyright + implementer guidelines",
    "analog": "Dual bundle: spec copyright + patent claim chart on profile",
    "url": "https://trustee.ietf.org/",
    "note": "draft-velaru-gate-bind-commit-profile as licensable conformance spec.",
}

_REAL_FUSE_REGISTRY = {
    "institution": "Gate license_fuse parent registry — stranger-verify Parent License ID",
    "analog": "Metered SaaS: registry lookup + LAQ attestation band",
    "url": "https://gate.velaru.xyz/.well-known/license-fuse.json",
    "note": "Tier-2 hosted redeem pairs with registry meter.",
}

_REAL_NAIC_LATCH = {
    "institution": "NAIC AIS Evaluation Tool — Exhibit D adoption path (12-state pilot 2026)",
    "analog": "Regulatory latch forces conformant bind on audited models",
    "url": "https://content.naic.org/",
    "note": "Regulatory latch multiplies LAQ; implementation sibling exhibit_d_snare.py — do not duplicate evaluator.",
}

_REAL_VISA = {
    "institution": "Visa interchange — network fee on settled payment volume",
    "analog": "Micro-toll per irreversible commit at planetary transaction scale",
    "url": "https://usa.visa.com/support/small-business/regulations-fees.html",
    "note": "~$15T+ global purchase volume; 1 bp = $1.5B/yr class.",
}

_REAL_SWIFT = {
    "institution": "SWIFT ISO 20022 — financial messaging per-message economics",
    "analog": "Per-message toll on commit receipts crossing settlement boundary",
    "url": "https://www.swift.com/standards/iso-20022",
    "note": "Finality messages as QIC analog in payment rail Licensed Field.",
}

_REAL_STRIPE = {
    "institution": "Stripe Connect — application_fee on platform volume",
    "analog": "Platform cut on partner processed commit volume",
    "url": "https://stripe.com/connect",
    "note": "SI/distributor pass-through from term sheet §8 sublicense.",
}

_REAL_EU_AI = {
    "institution": "EU AI Act Arts 12–14 — logging + human oversight for high-risk AI",
    "analog": "Essential conformance pack for AI bind paths in EU",
    "url": "https://artificialintelligenceact.eu/",
    "note": "Regulatory essential pack → FRAND-capable SEP story.",
}

_REAL_FEDWIRE = {
    "institution": "Fedwire OC6 Critical Payment Order (Jan 2026 protracted outage regime)",
    "analog": "Finality fee on commits that must survive protracted outage order",
    "url": "https://www.frbservices.org/",
    "note": "Pairs with protracted_outage_order civilizational module.",
}

_REAL_AGORA = {
    "institution": "BIS Project Agorá — atomic settlement / wholesale CBDC experiments",
    "analog": "Atomic toll when premium mass + settlement must fire together",
    "url": "https://www.bis.org/about/bisih/topics/fmis/agora.htm",
    "note": "Licensed Field expansion into wholesale settlement.",
}

_REAL_MCP = {
    "institution": "Model Context Protocol — tool invocation mesh at agent speed",
    "analog": "Per-tool-commit meter on high-velocity delegated writes",
    "url": "https://modelcontextprotocol.io/",
    "note": "v·TTL exposure class — needs RCC bundle for honest licensing.",
}

_REAL_RCC = {
    "institution": "Parakhin execution-count budgets (RCC) — arXiv:2603.09875",
    "analog": "Agent fleet license: D≤n commits per credential independent of velocity",
    "url": "https://arxiv.org/abs/2603.09875",
    "note": "Mouth Ceiling today for multi-spend; license field ready when shipped.",
}

_REAL_EDGE = {
    "institution": "Cloudflare Workers — edge redeem / bind worker surcharge",
    "analog": "Per-invocation surcharge on hosted redeem at edge",
    "url": "https://developers.cloudflare.com/workers/",
    "note": "Tier-2 hosted redeem economics.",
}

_REAL_SPV = {
    "institution": "Bowie bonds 1997 — $55M securitization on royalty catalog",
    "analog": "SPV executes on contracted LAQ stream — upfront + residual",
    "url": "https://www.sec.gov/Archives/edgar/data/",
    "note": "Monetizes royalty stream; does not create volume.",
}

_REAL_FORWARD = {
    "institution": "Hipgnosis / catalog annuity sales — forward royalty trades",
    "analog": "Sell N years of LAQ at DCF; retain admin toll",
    "url": "https://www.hipgnosissongs.com/",
    "note": "Balance-sheet upside from proven meter.",
}

_REAL_INDEX = {
    "institution": "IP receipt index / royalty ETF analog",
    "analog": "Index fund on aggregate stranger-grade QIC + HALT depth bands",
    "url": "https://www.sec.gov/",
    "note": "Requires published aggregate meter (no PII).",
}

_REAL_BENCHMARK = {
    "institution": "Guidewire Compare — peer benchmark data product",
    "analog": "Sell anonymized commit/HALT benchmark feed to carriers",
    "url": "https://docs.guidewire.com/cloud/compare/latest/",
    "note": "Data asset orthogonal to per-QIC patent.",
}

_REAL_RFC3161 = {
    "institution": "RFC 3161 timestamp authority — per-seal toll",
    "analog": "TSA toll on stranger-grade receipt anchors",
    "url": "https://www.rfc-editor.org/rfc/rfc3161",
    "note": "Pairs with Authproof/CertNode attestation lane.",
}

_REAL_PCT = {
    "institution": "WIPO PCT — national-phase cascade on global Licensed Field",
    "analog": "Multi-jurisdiction patent ladder unlocks ex-US premium bps",
    "url": "https://www.wipo.int/pct/en/",
    "note": "Extends 64/124,027 family; wipo_pct_epoch in batch 5.",
}

_REAL_STEP = {
    "institution": "ARM royalty step-down tiers — volume-triggered rate ladder",
    "analog": "Trillion-QIC step ladder: rate falls, revenue rises to plateau",
    "url": "https://www.arm.com/company/partnerships/licensing",
    "note": "Illustrative ceiling band: 1T QIC × $0.003 = $3B/yr.",
}

_REAL_SMPAG = {
    "institution": "ESA SMPAG — planetary defense may-quorum",
    "analog": "No single desk licenses planet-scale commit without quorum attestation",
    "url": "https://www.cosmos.esa.int/web/smpag",
    "note": "Civilizational ceiling guard — pairs smpag_may_quorum batch 3.",
}


# ---------------------------------------------------------------------------
# Evaluators (compact)
# ---------------------------------------------------------------------------


def _eval_gate_conformant_mark(**kwargs: Any) -> dict[str, Any]:
    certified = bool(kwargs.get("conformant_certified") or kwargs.get("annual_attestation"))
    ghost = bool(kwargs.get("ghost_conformant") or kwargs.get("ghost_licensing"))
    holders = int(kwargs.get("cert_holders") or kwargs.get("implementers") or 0)
    fee = float(kwargs.get("cert_fee_annual") or 30_000)
    ceiling = _illustrative_ceiling(cert_holders=holders or 10_000, cert_fee_annual=fee)
    if ghost:
        return _out(
            "gate_conformant_mark", "Gate Conformant Mark", _REAL_CONFORMANT,
            "GHOST_CONFORMANT_DENY", recurring_income_analog="certification_franchise_fee",
            rule="Gate Conformant™ without annual attestation is ghost certification — DENY.",
            ceiling_band_usd="100M-1B+",
        )
    if not certified:
        return _out(
            "gate_conformant_mark", "Gate Conformant Mark", _REAL_CONFORMANT,
            "CONFORMANT_REQUIRED", recurring_income_analog="certification_franchise_fee",
            rule="UL/PCI-class mark — trademark + test suite + annual recert before bind stick.",
            ceiling_band_usd="100M-1B+",
            illustrative_ceiling_usd=ceiling,
        )
    return _out(
        "gate_conformant_mark", "Gate Conformant Mark", _REAL_CONFORMANT,
        "CONFORMANT_MARK_OK", recurring_income_analog="certification_franchise_fee",
        rule="Certified implementer — franchise fee scales with deploy count, not QIC alone.",
        ceiling_band_usd="100M-1B+",
        illustrative_ceiling_usd=ceiling,
        cert_holders=holders,
    )


def _eval_premium_bps_meter(**kwargs: Any) -> dict[str, Any]:
    npw = float(kwargs.get("premium_volume_usd") or kwargs.get("npw_usd") or 0)
    bps = float(kwargs.get("bps") or kwargs.get("premium_bps") or 0)
    licensed = bool(kwargs.get("premium_meter_licensed") or kwargs.get("patent_licensed"))
    ceiling = _illustrative_ceiling(
        premium_volume_usd=npw or 97_100_000_000,
        bps=bps or 31,
    )
    if npw and bps and not licensed:
        return _out(
            "premium_bps_meter", "Premium BPS Meter", _REAL_PREMIUM_BPS,
            "METER_UNLICENSED", recurring_income_analog="premium_basis_points_royalty",
            rule="Premium bps without field license — meter read only, no stick.",
            ceiling_band_usd="300M-10B+",
            illustrative_ceiling_usd=ceiling,
            npw_usd=npw, bps=bps,
        )
    return _out(
        "premium_bps_meter", "Premium BPS Meter", _REAL_PREMIUM_BPS,
        "PREMIUM_BPS_OK" if licensed and bps else "PREMIUM_BPS_READY",
        recurring_income_analog="premium_basis_points_royalty",
        rule="Qualcomm-on-premium: royalty linear in bound NPW, not chip ASP.",
        ceiling_band_usd="300M-10B+",
        illustrative_ceiling_usd=ceiling,
        npw_usd=npw or None, bps=bps or None,
    )


def _eval_agent_runtime_field_license(**kwargs: Any) -> dict[str, Any]:
    field_b = bool(kwargs.get("licensed_field_b") or kwargs.get("agent_runtime"))
    multi_spend = bool(kwargs.get("multi_spend_tickets"))
    rcc = bool(kwargs.get("rcc_budget") or kwargs.get("execution_count_cap"))
    laq = float(kwargs.get("laq") or kwargs.get("qic_volume") or 10_000_000_000)
    rate = float(kwargs.get("per_qic_rate") or 0.03)
    if field_b and multi_spend and not rcc:
        return _out(
            "agent_runtime_field_license", "Agent Runtime Field License", _REAL_AGENT_FIELD,
            "RCC_REQUIRED_DENY", recurring_income_analog="agent_field_per_commit_royalty",
            rule="Multi-spend agent field without RCC budget — Parakhin gap; DENY until Mouth ships.",
            ceiling_band_usd="1B-100B+",
        )
    ceiling = _illustrative_ceiling(laq=laq, rate=rate)
    return _out(
        "agent_runtime_field_license", "Agent Runtime Field License", _REAL_AGENT_FIELD,
        "AGENT_FIELD_OK" if field_b else "AGENT_FIELD_LATENT",
        recurring_income_analog="agent_field_per_commit_royalty",
        rule="Licensed Field B — billions of QIC/yr at cents = nine-figure+ royalty.",
        ceiling_band_usd="1B-100B+",
        illustrative_ceiling_usd=ceiling,
        laq=laq, per_qic_rate=rate,
    )


def _eval_patent_pool_operator_toll(**kwargs: Any) -> dict[str, Any]:
    pool_live = bool(kwargs.get("pool_operator") or kwargs.get("pool_live"))
    essential = bool(kwargs.get("standard_essential") or kwargs.get("sep_declared"))
    admin_bps = float(kwargs.get("pool_admin_bps") or 2)
    volume = float(kwargs.get("pool_volume_usd") or kwargs.get("premium_volume_usd") or 0)
    ceiling = volume * admin_bps / 10_000 if volume else None
    if essential and not pool_live:
        return _out(
            "patent_pool_operator_toll", "Patent Pool Operator Toll", _REAL_POOL_OP,
            "POOL_OPERATOR_REQUIRED", recurring_income_analog="pool_administration_toll",
            rule="SEP declared but no pool operator — MPEG-class admin toll missing.",
            ceiling_band_usd="500M-50B+",
        )
    return _out(
        "patent_pool_operator_toll", "Patent Pool Operator Toll", _REAL_POOL_OP,
        "POOL_TOLL_OK" if pool_live else "POOL_TOLL_LATENT",
        recurring_income_analog="pool_administration_toll",
        rule="Operator cut on every essential implementer — recurring regardless of single patent.",
        ceiling_band_usd="500M-50B+",
        illustrative_ceiling_usd=ceiling,
    )


def _eval_ietf_profile_spec_asset(**kwargs: Any) -> dict[str, Any]:
    draft_filed = bool(kwargs.get("ietf_draft_live") or kwargs.get("profile_published"))
    copyright_bundle = bool(kwargs.get("spec_copyright_licensed"))
    if draft_filed and not copyright_bundle:
        return _out(
            "ietf_profile_spec_asset", "IETF Profile Spec Asset", _REAL_IETF_SPEC,
            "SPEC_LICENSE_GAP", recurring_income_analog="spec_copyright_plus_patent_bundle",
            rule="Profile live without spec copyright license — implementers read free, you miss spec SKU.",
            ceiling_band_usd="100M-5B+",
        )
    return _out(
        "ietf_profile_spec_asset", "IETF Profile Spec Asset", _REAL_IETF_SPEC,
        "SPEC_ASSET_OK" if copyright_bundle else "SPEC_ASSET_LATENT",
        recurring_income_analog="spec_copyright_plus_patent_bundle",
        rule="Dual IP: RFC/profile copyright + epoch-lock claim chart as single conformance SKU.",
        ceiling_band_usd="100M-5B+",
    )


def _eval_fuse_registry_meter_saas(**kwargs: Any) -> dict[str, Any]:
    registry = bool(kwargs.get("parent_registry_live") or kwargs.get("registry_published"))
    hosted = bool(kwargs.get("hosted_redeem") or kwargs.get("tier_2_saas"))
    subs = int(kwargs.get("active_sublicenses") or 0)
    fee = float(kwargs.get("registry_saas_annual") or 25_000)
    ceiling = subs * fee if subs else None
    return _out(
        "fuse_registry_meter_saas", "Fuse Registry Meter SaaS", _REAL_FUSE_REGISTRY,
        "REGISTRY_METER_OK" if registry and hosted else "REGISTRY_METER_LATENT",
        recurring_income_analog="registry_meter_saas",
        rule="Stranger-verify Parent License ID + LAQ band — SaaS meter on sublicense tree.",
        ceiling_band_usd="50M-1B+",
        illustrative_ceiling_usd=ceiling,
        active_sublicenses=subs,
    )


def _eval_naic_adoption_latch(**kwargs: Any) -> dict[str, Any]:
    exhibit_d = bool(kwargs.get("exhibit_d_required") or kwargs.get("naic_audit"))
    conformant = bool(kwargs.get("conformant_certified"))
    if exhibit_d and not conformant:
        return _out(
            "naic_adoption_latch", "NAIC Adoption Latch", _REAL_NAIC_LATCH,
            "ADOPTION_LATCH_CHOKE", recurring_income_analog="regulatory_volume_driver",
            rule="Exhibit D audit path requires conformant bind — volume latch, not fee by itself.",
            ceiling_band_usd="300M+ (enables bps/QIC)",
            adoption_multiplier="5-50× LAQ when mandatory",
        )
    return _out(
        "naic_adoption_latch", "NAIC Adoption Latch", _REAL_NAIC_LATCH,
        "ADOPTION_LATCH_OK" if exhibit_d else "ADOPTION_LATCH_LATENT",
        recurring_income_analog="regulatory_volume_driver",
        rule="Regulatory latch multiplies LAQ — pairs premium_bps_meter + gate_conformant_mark.",
        ceiling_band_usd="300M+ (enables bps/QIC)",
    )


def _eval_visa_interchange_commit_analog(**kwargs: Any) -> dict[str, Any]:
    volume = float(kwargs.get("commit_volume_usd") or kwargs.get("settlement_volume_usd") or 0)
    bp = float(kwargs.get("interchange_bp") or 1)
    ceiling = volume * bp / 10_000 if volume else None
    return _out(
        "visa_interchange_commit_analog", "Visa Interchange Commit Analog", _REAL_VISA,
        "INTERCHANGE_ANALOG_OK" if volume else "INTERCHANGE_ANALOG_LATENT",
        recurring_income_analog="network_interchange_on_commits",
        rule="Planetary commit volume × basis points — Visa-class, not MGA-class unit economics.",
        ceiling_band_usd="10B-300B+",
        illustrative_ceiling_usd=ceiling or 150_000_000_000 * bp / 10_000,
        commit_volume_usd=volume or None,
    )


def _eval_swift_iso20022_message_toll(**kwargs: Any) -> dict[str, Any]:
    msgs = float(kwargs.get("messages_per_year") or kwargs.get("laq") or 0)
    toll = float(kwargs.get("message_toll") or 0.05)
    ceiling = msgs * toll if msgs else None
    return _out(
        "swift_iso20022_message_toll", "SWIFT ISO 20022 Message Toll", _REAL_SWIFT,
        "MESSAGE_TOLL_OK" if msgs else "MESSAGE_TOLL_LATENT",
        recurring_income_analog="per_finality_message_toll",
        rule="Settlement-bound commit receipts as ISO 20022 messages — per-message royalty.",
        ceiling_band_usd="1B-30B+",
        illustrative_ceiling_usd=ceiling,
    )


def _eval_stripe_connect_platform_cut(**kwargs: Any) -> dict[str, Any]:
    gmv = float(kwargs.get("platform_gmv_usd") or 0)
    cut_bps = float(kwargs.get("platform_cut_bps") or 25)
    ceiling = gmv * cut_bps / 10_000 if gmv else None
    return _out(
        "stripe_connect_platform_cut", "Stripe Connect Platform Cut", _REAL_STRIPE,
        "PLATFORM_CUT_OK" if gmv else "PLATFORM_CUT_LATENT",
        recurring_income_analog="sublicense_platform_application_fee",
        rule="SI/distributor pass-through — % of sublicensee processed commit volume.",
        ceiling_band_usd="100M-10B+",
        illustrative_ceiling_usd=ceiling,
    )


def _eval_eu_ai_act_essential_pack(**kwargs: Any) -> dict[str, Any]:
    eu_bind = bool(kwargs.get("eu_high_risk_ai_bind"))
    pack = bool(kwargs.get("essential_pack_shipped"))
    if eu_bind and not pack:
        return _out(
            "eu_ai_act_essential_pack", "EU AI Act Essential Pack", _REAL_EU_AI,
            "ESSENTIAL_PACK_REQUIRED", recurring_income_analog="regulatory_essential_pack_fee",
            rule="High-risk AI bind in EU without Arts 12–14 pack — choke before stick.",
            ceiling_band_usd="500M-20B+",
        )
    return _out(
        "eu_ai_act_essential_pack", "EU AI Act Essential Pack", _REAL_EU_AI,
        "ESSENTIAL_PACK_OK" if pack else "ESSENTIAL_PACK_LATENT",
        recurring_income_analog="regulatory_essential_pack_fee",
        rule="EU essential pack → FRAND-capable SEP + annual conformance SKU.",
        ceiling_band_usd="500M-20B+",
    )


def _eval_fedwire_oc6_finality_fee(**kwargs: Any) -> dict[str, Any]:
    critical = bool(kwargs.get("critical_payment_order") or kwargs.get("oc6_regime"))
    finality = bool(kwargs.get("finality_attested"))
    if critical and not finality:
        return _out(
            "fedwire_oc6_finality_fee", "Fedwire OC6 Finality Fee", _REAL_FEDWIRE,
            "FINALITY_FEE_DENY", recurring_income_analog="finality_survival_premium",
            rule="OC6 protracted outage — commit without finality attestation is DENY.",
            ceiling_band_usd="100M-5B+",
        )
    return _out(
        "fedwire_oc6_finality_fee", "Fedwire OC6 Finality Fee", _REAL_FEDWIRE,
        "FINALITY_FEE_OK" if critical else "FINALITY_FEE_LATENT",
        recurring_income_analog="finality_survival_premium",
        rule="Premium for commits that survive protracted outage order — pairs nss_finality_stamp.",
        ceiling_band_usd="100M-5B+",
    )


def _eval_bis_agora_atomic_toll(**kwargs: Any) -> dict[str, Any]:
    atomic = bool(kwargs.get("atomic_settlement") or kwargs.get("agora_path"))
    partial = bool(kwargs.get("partial_ghost_bind"))
    if partial:
        return _out(
            "bis_agora_atomic_toll", "BIS Agorá Atomic Toll", _REAL_AGORA,
            "ATOMIC_TOLL_DENY", recurring_income_analog="wholesale_atomic_settlement_toll",
            rule="Partial ghost bind on atomic settlement path — none fire or all fire.",
            ceiling_band_usd="1B-50B+",
        )
    return _out(
        "bis_agora_atomic_toll", "BIS Agorá Atomic Toll", _REAL_AGORA,
        "ATOMIC_TOLL_OK" if atomic else "ATOMIC_TOLL_LATENT",
        recurring_income_analog="wholesale_atomic_settlement_toll",
        rule="Wholesale CBDC/settlement Licensed Field — atomic toll on stick.",
        ceiling_band_usd="1B-50B+",
    )


def _eval_mcp_mesh_commit_meter(**kwargs: Any) -> dict[str, Any]:
    mesh = bool(kwargs.get("mcp_mesh") or kwargs.get("tool_invocations"))
    invocations = float(kwargs.get("tool_invocations_per_year") or kwargs.get("laq") or 0)
    rate = float(kwargs.get("per_invocation_rate") or 0.001)
    ceiling = invocations * rate if invocations else None
    return _out(
        "mcp_mesh_commit_meter", "MCP Mesh Commit Meter", _REAL_MCP,
        "MCP_METER_OK" if mesh else "MCP_METER_LATENT",
        recurring_income_analog="tool_mesh_per_invocation_royalty",
        rule="Agent-speed tool commits — meter at invocation, not insurance bind cadence.",
        ceiling_band_usd="1B-100B+",
        illustrative_ceiling_usd=ceiling or 100_000_000_000 * rate,
    )


def _eval_agent_fleet_rcc_bundle(**kwargs: Any) -> dict[str, Any]:
    fleet = bool(kwargs.get("agent_fleet") or kwargs.get("multi_spend_tickets"))
    rcc = bool(kwargs.get("rcc_budget") or kwargs.get("execution_count_cap"))
    cap = int(kwargs.get("execution_count_cap") or kwargs.get("rcc_d") or 0)
    if fleet and not rcc:
        return _out(
            "agent_fleet_rcc_bundle", "Agent Fleet RCC Bundle", _REAL_RCC,
            "RCC_BUNDLE_REQUIRED", recurring_income_analog="execution_count_license_bundle",
            rule="Fleet license bundles D≤n execution-count budgets — sell RCC packs.",
            ceiling_band_usd="500M-50B+",
        )
    return _out(
        "agent_fleet_rcc_bundle", "Agent Fleet RCC Bundle", _REAL_RCC,
        "RCC_BUNDLE_OK" if rcc else "RCC_BUNDLE_LATENT",
        recurring_income_analog="execution_count_license_bundle",
        rule="Parakhin-honest fleet licensing — per-agent RCC packs at scale.",
        ceiling_band_usd="500M-50B+",
        execution_count_cap=cap or None,
    )


def _eval_edge_worker_bind_surcharge(**kwargs: Any) -> dict[str, Any]:
    edge = bool(kwargs.get("edge_redeem") or kwargs.get("cloudflare_worker"))
    invocations = float(kwargs.get("worker_invocations_per_year") or 0)
    surcharge = float(kwargs.get("surcharge_per_invoke") or 0.0001)
    ceiling = invocations * surcharge if invocations else None
    return _out(
        "edge_worker_bind_surcharge", "Edge Worker Bind Surcharge", _REAL_EDGE,
        "EDGE_SURCHARGE_OK" if edge else "EDGE_SURCHARGE_LATENT",
        recurring_income_analog="hosted_redeem_edge_surcharge",
        rule="Tier-2 hosted redeem — micro-surcharge per edge invocation.",
        ceiling_band_usd="50M-5B+",
        illustrative_ceiling_usd=ceiling,
    )


def _eval_securitized_royalty_spv_live(**kwargs: Any) -> dict[str, Any]:
    laq = float(kwargs.get("contracted_laq") or kwargs.get("laq") or 0)
    rate = float(kwargs.get("per_qic_rate") or 0)
    stream = laq * rate
    spv = bool(kwargs.get("spv_executed") or kwargs.get("securitization_closed"))
    upfront_pct = float(kwargs.get("spv_upfront_pct") or 0.7)
    return _out(
        "securitized_royalty_spv_live", "Securitized Royalty SPV Live", _REAL_SPV,
        "SPV_LIVE" if spv else "SPV_LATENT",
        recurring_income_analog="securitized_royalty_upfront_plus_residual",
        rule="Bowie-class: sell % of contracted LAQ stream; retain admin + new volume.",
        ceiling_band_usd="balance-sheet (not ARR)",
        illustrative_stream_usd=stream or None,
        illustrative_upfront_usd=stream * upfront_pct if stream else None,
    )


def _eval_forward_royalty_catalog_sale(**kwargs: Any) -> dict[str, Any]:
    years = int(kwargs.get("forward_years") or 10)
    arr = float(kwargs.get("proven_arr") or 0)
    multiple = float(kwargs.get("sale_multiple") or 8)
    return _out(
        "forward_royalty_catalog_sale", "Forward Royalty Catalog Sale", _REAL_FORWARD,
        "FORWARD_SALE_READY" if arr else "FORWARD_SALE_LATENT",
        recurring_income_analog="catalog_forward_sale_dcf",
        rule="Hipgnosis-class: forward sale of N-year royalty catalog at multiple of proven ARR.",
        ceiling_band_usd="balance-sheet (not ARR)",
        illustrative_sale_usd=arr * multiple if arr else None,
        forward_years=years,
    )


def _eval_ip_receipt_index_fund(**kwargs: Any) -> dict[str, Any]:
    published = bool(kwargs.get("aggregate_meter_public") or kwargs.get("stranger_grade_public"))
    aum = float(kwargs.get("index_aum_usd") or 0)
    mgmt_bps = float(kwargs.get("mgmt_fee_bps") or 50)
    ceiling = aum * mgmt_bps / 10_000 if aum else None
    if not published:
        return _out(
            "ip_receipt_index_fund", "IP Receipt Index Fund", _REAL_INDEX,
            "INDEX_METER_PRIVATE", recurring_income_analog="index_mgmt_fee_on_aum",
            rule="Index requires public aggregate QIC/HALT band — no PII.",
            ceiling_band_usd="100M-10B+ AUM fee",
        )
    return _out(
        "ip_receipt_index_fund", "IP Receipt Index Fund", _REAL_INDEX,
        "INDEX_FUND_OK",
        recurring_income_analog="index_mgmt_fee_on_aum",
        rule="Royalty ETF/index on published stranger-grade commit receipts.",
        ceiling_band_usd="100M-10B+ AUM fee",
        illustrative_ceiling_usd=ceiling,
    )


def _eval_stranger_grade_benchmark_feed(**kwargs: Any) -> dict[str, Any]:
    subscribers = int(kwargs.get("benchmark_subscribers") or 0)
    fee = float(kwargs.get("benchmark_annual") or 100_000)
    ceiling = subscribers * fee if subscribers else None
    return _out(
        "stranger_grade_benchmark_feed", "Stranger Grade Benchmark Feed", _REAL_BENCHMARK,
        "BENCHMARK_OK" if subscribers else "BENCHMARK_LATENT",
        recurring_income_analog="anonymized_benchmark_data_feed",
        rule="Guidewire Compare-class: sell HALT depth + QIC bands to carriers.",
        ceiling_band_usd="50M-2B+",
        illustrative_ceiling_usd=ceiling,
    )


def _eval_rfc3161_timestamp_toll(**kwargs: Any) -> dict[str, Any]:
    seals = float(kwargs.get("timestamp_seals_per_year") or kwargs.get("laq") or 0)
    toll = float(kwargs.get("tsa_toll") or 0.02)
    ceiling = seals * toll if seals else None
    return _out(
        "rfc3161_timestamp_toll", "RFC 3161 Timestamp Toll", _REAL_RFC3161,
        "TSA_TOLL_OK" if seals else "TSA_TOLL_LATENT",
        recurring_income_analog="timestamp_authority_per_seal",
        rule="Per-seal TSA toll on stranger-grade receipt anchors.",
        ceiling_band_usd="100M-5B+",
        illustrative_ceiling_usd=ceiling,
    )


def _eval_cross_border_pct_cascade(**kwargs: Any) -> dict[str, Any]:
    national = int(kwargs.get("national_phases_entered") or 0)
    global_npw = float(kwargs.get("global_npw_usd") or 0)
    bps = float(kwargs.get("bps") or 10)
    ceiling = global_npw * bps / 10_000 if global_npw else None
    return _out(
        "cross_border_pct_cascade", "Cross Border PCT Cascade", _REAL_PCT,
        "PCT_CASCADE_OK" if national >= 3 else "PCT_CASCADE_LATENT",
        recurring_income_analog="multi_jurisdiction_premium_bps",
        rule="WIPO national-phase ladder — ex-US premium bps on global Licensed Field.",
        ceiling_band_usd="1B-30B+",
        illustrative_ceiling_usd=ceiling,
        national_phases_entered=national,
    )


def _eval_trillion_qic_step_ladder(**kwargs: Any) -> dict[str, Any]:
    laq = float(kwargs.get("laq") or kwargs.get("qic_volume") or 0)
    tiers = kwargs.get("step_tiers") or [
        (1_000_000_000, 0.05),
        (10_000_000_000, 0.02),
        (1_000_000_000_000, 0.003),
    ]
    revenue = 0.0
    remaining = laq
    prev_cap = 0.0
    for cap, rate in tiers:
        band = min(remaining, cap - prev_cap) if cap > prev_cap else remaining
        if band <= 0:
            break
        revenue += band * rate
        remaining -= band
        prev_cap = cap
        if remaining <= 0:
            break
    if remaining > 0 and tiers:
        revenue += remaining * tiers[-1][1]
    return _out(
        "trillion_qic_step_ladder", "Trillion QIC Step Ladder", _REAL_STEP,
        "STEP_LADDER_OK" if laq else "STEP_LADDER_LATENT",
        recurring_income_analog="volume_step_down_royalty_ladder",
        rule="ARM-class: rate falls with volume; revenue rises to plateau then dominates.",
        ceiling_band_usd="1B-300B+",
        illustrative_ceiling_usd=revenue if laq else 3_000_000_000,
        laq=laq or None,
        step_tiers=tiers,
    )


def _eval_planetary_quorum_license(**kwargs: Any) -> dict[str, Any]:
    quorum = bool(kwargs.get("may_quorum") or kwargs.get("smpag_quorum"))
    solo = bool(kwargs.get("solo_planetary_license"))
    if solo:
        return _out(
            "planetary_quorum_license", "Planetary Quorum License", _REAL_SMPAG,
            "SOLO_PLANETARY_DENY", recurring_income_analog="quorum_gated_planetary_license",
            rule="No single desk licenses planet-scale commit — SMPAG-class quorum required.",
            ceiling_band_usd="symbolic / civilizational",
        )
    return _out(
        "planetary_quorum_license", "Planetary Quorum License", _REAL_SMPAG,
        "QUORUM_LICENSE_OK" if quorum else "QUORUM_LICENSE_LATENT",
        recurring_income_analog="quorum_gated_planetary_license",
        rule="Civilizational ceiling guard — pairs smpag_may_quorum; experimental upside cap.",
        ceiling_band_usd="symbolic / civilizational",
    )


@dataclass
class _Invention:
    slug: str
    invention: str
    one_liner: str
    real: dict[str, Any]
    evaluate: Callable[..., dict[str, Any]]


REGISTRY: dict[str, _Invention] = {
    "gate_conformant_mark": _Invention(
        "gate_conformant_mark", "Gate Conformant Mark",
        "PCI/UL-class certification franchise — trademark + test suite + annual recert.",
        _REAL_CONFORMANT, _eval_gate_conformant_mark,
    ),
    "premium_bps_meter": _Invention(
        "premium_bps_meter", "Premium BPS Meter",
        "Qualcomm-on-premium: basis points on NPW through conformant bind.",
        _REAL_PREMIUM_BPS, _eval_premium_bps_meter,
    ),
    "agent_runtime_field_license": _Invention(
        "agent_runtime_field_license", "Agent Runtime Field License",
        "Licensed Field B — billions of agent commits at cents per QIC.",
        _REAL_AGENT_FIELD, _eval_agent_runtime_field_license,
    ),
    "patent_pool_operator_toll": _Invention(
        "patent_pool_operator_toll", "Patent Pool Operator Toll",
        "MPEG LA admin toll on every essential pool sublicense.",
        _REAL_POOL_OP, _eval_patent_pool_operator_toll,
    ),
    "ietf_profile_spec_asset": _Invention(
        "ietf_profile_spec_asset", "IETF Profile Spec Asset",
        "Spec copyright + patent bundle on gate-bind-commit-profile.",
        _REAL_IETF_SPEC, _eval_ietf_profile_spec_asset,
    ),
    "fuse_registry_meter_saas": _Invention(
        "fuse_registry_meter_saas", "Fuse Registry Meter SaaS",
        "Parent License registry + LAQ attestation as metered SaaS.",
        _REAL_FUSE_REGISTRY, _eval_fuse_registry_meter_saas,
    ),
    "naic_adoption_latch": _Invention(
        "naic_adoption_latch", "NAIC Adoption Latch",
        "Exhibit D regulatory latch — multiplies conformant bind volume.",
        _REAL_NAIC_LATCH, _eval_naic_adoption_latch,
    ),
    "visa_interchange_commit_analog": _Invention(
        "visa_interchange_commit_analog", "Visa Interchange Commit Analog",
        "Network interchange basis points on planetary commit volume.",
        _REAL_VISA, _eval_visa_interchange_commit_analog,
    ),
    "swift_iso20022_message_toll": _Invention(
        "swift_iso20022_message_toll", "SWIFT ISO 20022 Message Toll",
        "Per-message toll on finality-bound commit receipts.",
        _REAL_SWIFT, _eval_swift_iso20022_message_toll,
    ),
    "stripe_connect_platform_cut": _Invention(
        "stripe_connect_platform_cut", "Stripe Connect Platform Cut",
        "Platform application fee on sublicense processed volume.",
        _REAL_STRIPE, _eval_stripe_connect_platform_cut,
    ),
    "eu_ai_act_essential_pack": _Invention(
        "eu_ai_act_essential_pack", "EU AI Act Essential Pack",
        "High-risk AI bind conformance pack for EU Arts 12–14.",
        _REAL_EU_AI, _eval_eu_ai_act_essential_pack,
    ),
    "fedwire_oc6_finality_fee": _Invention(
        "fedwire_oc6_finality_fee", "Fedwire OC6 Finality Fee",
        "Finality survival premium under protracted outage order.",
        _REAL_FEDWIRE, _eval_fedwire_oc6_finality_fee,
    ),
    "bis_agora_atomic_toll": _Invention(
        "bis_agora_atomic_toll", "BIS Agorá Atomic Toll",
        "Wholesale atomic settlement toll — all fire or none.",
        _REAL_AGORA, _eval_bis_agora_atomic_toll,
    ),
    "mcp_mesh_commit_meter": _Invention(
        "mcp_mesh_commit_meter", "MCP Mesh Commit Meter",
        "Per tool-invocation royalty on agent-speed MCP mesh.",
        _REAL_MCP, _eval_mcp_mesh_commit_meter,
    ),
    "agent_fleet_rcc_bundle": _Invention(
        "agent_fleet_rcc_bundle", "Agent Fleet RCC Bundle",
        "Execution-count budget packs for multi-spend agent fleets.",
        _REAL_RCC, _eval_agent_fleet_rcc_bundle,
    ),
    "edge_worker_bind_surcharge": _Invention(
        "edge_worker_bind_surcharge", "Edge Worker Bind Surcharge",
        "Micro-surcharge per hosted redeem at Cloudflare edge.",
        _REAL_EDGE, _eval_edge_worker_bind_surcharge,
    ),
    "securitized_royalty_spv_live": _Invention(
        "securitized_royalty_spv_live", "Securitized Royalty SPV Live",
        "Bowie-class SPV on contracted LAQ stream — upfront + residual.",
        _REAL_SPV, _eval_securitized_royalty_spv_live,
    ),
    "forward_royalty_catalog_sale": _Invention(
        "forward_royalty_catalog_sale", "Forward Royalty Catalog Sale",
        "Hipgnosis-class forward sale of proven royalty catalog.",
        _REAL_FORWARD, _eval_forward_royalty_catalog_sale,
    ),
    "ip_receipt_index_fund": _Invention(
        "ip_receipt_index_fund", "IP Receipt Index Fund",
        "Index/ETF mgmt fee on public aggregate commit receipt meter.",
        _REAL_INDEX, _eval_ip_receipt_index_fund,
    ),
    "stranger_grade_benchmark_feed": _Invention(
        "stranger_grade_benchmark_feed", "Stranger Grade Benchmark Feed",
        "Anonymized HALT/QIC benchmark data feed — Compare analog.",
        _REAL_BENCHMARK, _eval_stranger_grade_benchmark_feed,
    ),
    "rfc3161_timestamp_toll": _Invention(
        "rfc3161_timestamp_toll", "RFC 3161 Timestamp Toll",
        "TSA per-seal toll on stranger-grade receipt anchors.",
        _REAL_RFC3161, _eval_rfc3161_timestamp_toll,
    ),
    "cross_border_pct_cascade": _Invention(
        "cross_border_pct_cascade", "Cross Border PCT Cascade",
        "Multi-jurisdiction premium bps after PCT national phase.",
        _REAL_PCT, _eval_cross_border_pct_cascade,
    ),
    "trillion_qic_step_ladder": _Invention(
        "trillion_qic_step_ladder", "Trillion QIC Step Ladder",
        "ARM volume step-down — 1T QIC × $0.003 = $3B/yr illustrative.",
        _REAL_STEP, _eval_trillion_qic_step_ladder,
    ),
    "planetary_quorum_license": _Invention(
        "planetary_quorum_license", "Planetary Quorum License",
        "SMPAG-class quorum gate on planet-scale commit licensing.",
        _REAL_SMPAG, _eval_planetary_quorum_license,
    ),
}

assert set(REGISTRY.keys()) == set(SLUGS)


def evaluate_slug(slug: str, **kwargs: Any) -> dict[str, Any]:
    key = (slug or "").strip().lower()
    inv = REGISTRY.get(key)
    if not inv:
        return {"error": "unknown_slug", "slug": slug, "known": list(SLUGS)}
    return inv.evaluate(**kwargs)


_BLOCKER_VERDICTS = frozenset({
    "GHOST_CONFORMANT_DENY",
    "RCC_REQUIRED_DENY",
    "ADOPTION_LATCH_CHOKE",
    "ESSENTIAL_PACK_REQUIRED",
    "FINALITY_FEE_DENY",
    "ATOMIC_TOLL_DENY",
    "RCC_BUNDLE_REQUIRED",
    "SOLO_PLANETARY_DENY",
    "POOL_OPERATOR_REQUIRED",
    "SPEC_LICENSE_GAP",
    "INDEX_METER_PRIVATE",
})


def attach(plan: dict) -> dict:
    layer: dict[str, dict[str, Any]] = {}
    ceilings: list[float] = []
    for slug in SLUGS:
        ev = evaluate_slug(slug, **(plan if isinstance(plan, dict) else {}))
        layer[slug] = {
            "verdict": ev.get("verdict"),
            "spec": ev.get("spec"),
            "invention": ev.get("invention"),
            "tier": ev.get("tier"),
        }
        if "recurring_income_analog" in ev:
            layer[slug]["recurring_income_analog"] = ev["recurring_income_analog"]
        if "ceiling_band_usd" in ev:
            layer[slug]["ceiling_band_usd"] = ev["ceiling_band_usd"]
        ill = ev.get("illustrative_ceiling_usd")
        if isinstance(ill, (int, float)) and ill > 0:
            layer[slug]["illustrative_ceiling_usd"] = ill
            ceilings.append(float(ill))
        verdict = ev.get("verdict") or ""
        if verdict in _BLOCKER_VERDICTS or verdict.endswith("_DENY"):
            layer[slug]["block"] = True
    plan["ip_asset_ceiling"] = layer
    if ceilings:
        plan["ip_asset_ceiling_illustrative_stack_usd"] = sum(ceilings)
        plan["ip_asset_ceiling_illustrative_max_usd"] = max(ceilings)
    blockers = [s for s, v in layer.items() if v.get("block")]
    if blockers:
        plan["ip_asset_ceiling_blockers"] = blockers
    return plan


def manifest(public_url: str, slug: str) -> dict[str, Any]:
    key = (slug or "").strip().lower()
    inv = REGISTRY.get(key)
    if not inv:
        return {"error": "unknown_slug", "slug": slug, "known": list(SLUGS)}
    base = (public_url or "").rstrip("/")
    kebab = slug_to_kebab(key)
    return {
        "spec": _spec(key),
        "invention": inv.invention,
        "family": FAMILY,
        "tier": TIER,
        "slug": key,
        "one_liner": inv.one_liner,
        "real_institution": inv.real,
        "demo": f"POST {base}/demo/pas/{kebab}",
        "well_known": f"{base}/.well-known/{kebab}.json",
    }


def catalog_manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    entries = [manifest(public_url, slug) for slug in SLUGS]
    return {
        "spec": "gate-ip-asset-ceiling-catalog-v1",
        "invention": "IP Asset Ceiling Catalog",
        "family": FAMILY,
        "tier": TIER,
        "count": len(SLUGS),
        "slugs": list(SLUGS),
        "inventions": entries,
        "upside_ladder": f"{base}/.well-known/ip-asset-ceiling-ladder.json",
        "well_known": f"{base}/.well-known/ip-asset-ceiling.json",
        "doc": "gate/IP_ASSET_CEILING.md",
    }


def upside_ladder_manifest(public_url: str) -> dict[str, Any]:
    """Experimental ceiling tiers — illustrative, not forecast."""
    base = (public_url or "").rstrip("/")
    return {
        "spec": "gate-ip-asset-ceiling-ladder-v1",
        "tier": TIER,
        "disclaimer": "Illustrative mechanism stack — not financial advice or forecast.",
        "rungs": [
            {
                "rung": "M0",
                "label": "Gate 1 proof",
                "annual_usd": "50k-250k",
                "mechanism": "First field-limited patent license + MAR",
                "modules": ["epoch_lock_patent_asset"],
            },
            {
                "rung": "M1",
                "label": "$300M start",
                "annual_usd": "300M",
                "mechanism": "Premium bps (31 bps × ~$971B US NPW) OR 300M QIC × $1",
                "modules": ["premium_bps_meter", "naic_adoption_latch", "gate_conformant_mark"],
            },
            {
                "rung": "M2",
                "label": "$1B class",
                "annual_usd": "1B",
                "mechanism": "10B agent QIC × $0.10 OR cert franchise + partial bps stack",
                "modules": ["agent_runtime_field_license", "gate_conformant_mark", "fuse_registry_meter_saas"],
            },
            {
                "rung": "M3",
                "label": "$10B class",
                "annual_usd": "10B",
                "mechanism": "100B QIC × $0.10 OR 1 bp × $1T commit volume",
                "modules": ["mcp_mesh_commit_meter", "visa_interchange_commit_analog", "trillion_qic_step_ladder"],
            },
            {
                "rung": "M4",
                "label": "$100B class",
                "annual_usd": "100B",
                "mechanism": "Standard-essential pool + global premium bps + interchange stack",
                "modules": ["patent_pool_operator_toll", "cross_border_pct_cascade", "eu_ai_act_essential_pack"],
            },
            {
                "rung": "M5",
                "label": "$300B+ cartoon",
                "annual_usd": "300B+",
                "mechanism": "Mandatory planetary commit primitive — Visa × ARM × Disney trust mark",
                "modules": ["visa_interchange_commit_analog", "trillion_qic_step_ladder", "planetary_quorum_license"],
                "honest_blocker": "Requires civilization-scale mandatory adoption — not insurance GTM alone.",
            },
        ],
        "stack_demo": f"POST {base}/demo/pas/trillion-qic-step-ladder",
        "catalog": f"{base}/.well-known/ip-asset-ceiling.json",
    }
