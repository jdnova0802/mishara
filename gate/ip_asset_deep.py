"""IP Asset Deep — 32 IP-S+ bind-path inventions from real intellectual-property precedent.

Registry pattern: each slug carries spec, one_liner, real institution, and compact evaluate().
Not duplicating civilizational_deep slugs or shipped fuse modules (license_fuse owns parent-child
live/dead cascade — epoch_lock_patent_asset formalizes the patent as licensable IP asset only).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

FAMILY = "ip-asset-deep"
TIER = "IP-S+"

SLUGS: tuple[str, ...] = (
    "steamboat_willie_split",
    "arm_dual_stream",
    "mickey_trademark_moat",
    "sonny_bono_extension",
    "bowie_bond_securitization",
    "hipgnosis_catalog_annuity",
    "taylor_masters_rerecord",
    "frand_sep_choke",
    "mpeg_patent_pool_toll",
    "qualcomm_asp_royalty",
    "jordan_brand_unit_royalty",
    "disney_vault_window",
    "marvel_cross_license_lattice",
    "wipo_pct_epoch",
    "uspto_provisional_ladder",
    "epoch_lock_patent_asset",
    "trade_secret_dtsa_vault",
    "lanham_dilution_snare",
    "right_of_publicity_likeness",
    "work_for_hire_ownership",
    "sync_license_moment",
    "mechanical_royalty_stream",
    "sag_residual_choke",
    "merchandising_mg_overage",
    "open_invention_network_shield",
    "copyleft_contamination_snare",
    "creative_commons_tier_ladder",
    "ip_escrow_mna_latch",
    "royalty_audit_clawback",
    "cross_collateral_ip_basket",
    "character_sequel_option",
    "public_domain_recombine",
)

assert len(SLUGS) == 32, f"expected 32 slugs, got {len(SLUGS)}"
assert len(set(SLUGS)) == 32, "SLUGS must be unique"


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


# ---------------------------------------------------------------------------
# Evaluate implementations (compact, meaningful)
# ---------------------------------------------------------------------------

_REAL_STEAMBOAT = {
    "institution": "Steamboat Willie (1928) — US public domain Jan 1 2024",
    "copyright_pd": "2024-01-01 — Mickey Mouse film entered US public domain",
    "trademark_moat": "Disney retains active Mickey Mouse trademark registrations",
    "url": "https://www.copyright.gov/publicdomain/2024/",
}


def _eval_steamboat_willie_split(**kwargs: Any) -> dict[str, Any]:
    pd_clear = bool(kwargs.get("public_domain") or kwargs.get("copyright_expired"))
    tm_respected = bool(kwargs.get("trademark_respected", True))
    ghost = bool(kwargs.get("ghost_licensing") or kwargs.get("ghost_bind_haunted"))
    if ghost:
        return _out(
            "steamboat_willie_split",
            "Steamboat Willie Split",
            _REAL_STEAMBOAT,
            "GHOST_LICENSING_DENY",
            public_domain=pd_clear,
            trademark_respected=tm_respected,
            recurring_income_analog="trademark_moat_annuity",
            rule="PD film ≠ free Mickey — ghost licensing on expired copyright is DENY.",
        )
    if pd_clear and not tm_respected:
        return _out(
            "steamboat_willie_split",
            "Steamboat Willie Split",
            _REAL_STEAMBOAT,
            "TRADEMARK_MOAT_DENY",
            public_domain=True,
            trademark_respected=False,
            recurring_income_analog="trademark_moat_annuity",
            rule="Copyright PD Jan 1 2024 — trademark moat still blocks confusing bind marks.",
        )
    return _out(
        "steamboat_willie_split",
        "Steamboat Willie Split",
        _REAL_STEAMBOAT,
        "SPLIT_OK",
        public_domain=pd_clear,
        trademark_respected=tm_respected,
        recurring_income_analog="trademark_moat_annuity",
        rule="Separate copyright expiry from trademark moat — PD reuse without TM confusion OK.",
    )


_REAL_ARM = {
    "institution": "Arm Holdings — dual-stream semiconductor IP licensing",
    "model": "Upfront license fee + per-unit royalty on shipped silicon",
    "url": "https://www.arm.com/company/partnerships/licensing",
}


def _eval_arm_dual_stream(**kwargs: Any) -> dict[str, Any]:
    fee_paid = bool(kwargs.get("license_fee_paid") or kwargs.get("upfront_fee"))
    per_unit = float(kwargs.get("per_unit_royalty") or kwargs.get("royalty_per_unit") or 0.0)
    units = max(0, int(kwargs.get("units_shipped") or kwargs.get("bind_units") or 0))
    if not fee_paid:
        return _out(
            "arm_dual_stream",
            "Arm Dual Stream",
            _REAL_ARM,
            "UPFRONT_FEE_DENY",
            license_fee_paid=False,
            recurring_income_analog="per_unit_royalty_stream",
            rule="Arm-class bind requires upfront license fee before per-unit royalty accrual.",
        )
    stream = round(per_unit * units, 4)
    return _out(
        "arm_dual_stream",
        "Arm Dual Stream",
        _REAL_ARM,
        "DUAL_STREAM_OK",
        license_fee_paid=True,
        per_unit_royalty=per_unit,
        units_shipped=units,
        accrued_royalty=stream,
        recurring_income_analog="per_unit_royalty_stream",
        rule="License fee + per-unit royalty — dual income stream on every bind shipment.",
    )


_REAL_MICKEY_TM = {
    "institution": "USPTO Trademark — Steamboat Willie title card mark",
    "registration": "US Reg. 6846660 — Mickey Mouse film title card",
    "url": "https://tsdr.uspto.gov/#caseNumber=6846660&caseSearchType=US_APPLICATION",
}


def _eval_mickey_trademark_moat(**kwargs: Any) -> dict[str, Any]:
    mark_clear = bool(kwargs.get("mark_clearance") or kwargs.get("trademark_cleared"))
    confusing = bool(kwargs.get("confusingly_similar") or kwargs.get("dilution_risk"))
    if confusing or not mark_clear:
        return _out(
            "mickey_trademark_moat",
            "Mickey Trademark Moat",
            _REAL_MICKEY_TM,
            "TM_MOAT_DENY",
            mark_clearance=mark_clear,
            confusingly_similar=confusing,
            recurring_income_analog="trademark_renewal_annuity",
            rule="US Reg 6846660 title-card moat — confusing bind marks are absolute DENY.",
        )
    return _out(
        "mickey_trademark_moat",
        "Mickey Trademark Moat",
        _REAL_MICKEY_TM,
        "TM_MOAT_OK",
        mark_clearance=True,
        recurring_income_analog="trademark_renewal_annuity",
        rule="Steamboat title-card trademark survives copyright PD — clearance required.",
    )


_REAL_SONNY_BONO = {
    "institution": "Copyright Term Extension Act (1998) — Sonny Bono Act",
    "term": "Life + 70 years (individual) · 95 years (corporate works from 1928)",
    "statute": "17 U.S.C. § 302",
    "url": "https://www.copyright.gov/title17/92chap3.html",
}


def _eval_sonny_bono_extension(**kwargs: Any) -> dict[str, Any]:
    work_year = int(kwargs.get("work_year") or kwargs.get("publication_year") or 1928)
    bind_year = int(kwargs.get("bind_year") or kwargs.get("current_year") or 2026)
    corporate = bool(kwargs.get("corporate_work", work_year <= 1978))
    expiry = work_year + 95 if corporate else work_year + 70
    expired = bind_year >= expiry
    return _out(
        "sonny_bono_extension",
        "Sonny Bono Extension",
        _REAL_SONNY_BONO,
        "TERM_ACTIVE" if not expired else "TERM_EXPIRED_PD",
        work_year=work_year,
        expiry_year=expiry,
        corporate_work=corporate,
        recurring_income_analog="copyright_term_rent",
        rule="95-year corporate term — bind must respect Sonny Bono clock before PD reuse.",
    )


_REAL_BOWIE = {
    "institution": "Bowie Bonds (1997) — securitized music royalty stream",
    "deal": "$55M issue · 7.9% coupon · 29 albums / 287 songs collateral",
    "underwriter": "Prudential Insurance · pulled from market 2007",
    "url": "https://www.sec.gov/Archives/edgar/data/1045520/000104552098000001/0001045520-98-000001.txt",
}


def _eval_bowie_bond_securitization(**kwargs: Any) -> dict[str, Any]:
    catalog_value = float(kwargs.get("catalog_value") or kwargs.get("collateral_value") or 0.0)
    royalty_yield = float(kwargs.get("royalty_yield_pct") or kwargs.get("coupon_pct") or 0.0)
    securitized = bool(kwargs.get("securitized") or catalog_value >= 1_000_000)
    if securitized and royalty_yield < 5.0:
        return _out(
            "bowie_bond_securitization",
            "Bowie Bond Securitization",
            _REAL_BOWIE,
            "YIELD_TOO_THIN",
            catalog_value=catalog_value,
            royalty_yield_pct=royalty_yield,
            recurring_income_analog="securitized_royalty_coupon",
            rule="Bowie Bonds proved catalog cashflows securitize — sub-5% yield flags thin collateral.",
        )
    return _out(
        "bowie_bond_securitization",
        "Bowie Bond Securitization",
        _REAL_BOWIE,
        "SECURITIZATION_OK" if securitized else "CATALOG_UNSECURITIZED",
        catalog_value=catalog_value,
        royalty_yield_pct=royalty_yield or 7.9,
        recurring_income_analog="securitized_royalty_coupon",
        rule="$55M / 7.9% Bowie Bonds — IP royalty streams are bond-grade recurring income.",
    )


_REAL_HIPGNOSIS = {
    "institution": "Hipgnosis Songs Fund — music catalog acquisition annuity model",
    "acquirer": "Blackstone acquired Hipgnosis Songs Capital (2024)",
    "model": "Perpetual catalog acquisition targeting 5%+ net asset yield",
    "url": "https://www.hipgnosissongs.com/",
}


def _eval_hipgnosis_catalog_annuity(**kwargs: Any) -> dict[str, Any]:
    catalog_yield = float(kwargs.get("catalog_yield_pct") or kwargs.get("net_yield") or 0.0)
    songs = max(0, int(kwargs.get("song_count") or kwargs.get("catalog_size") or 0))
    recurring = catalog_yield >= 4.0 or songs >= 50
    return _out(
        "hipgnosis_catalog_annuity",
        "Hipgnosis Catalog Annuity",
        _REAL_HIPGNOSIS,
        "CATALOG_ANNUITY_OK" if recurring else "CATALOG_YIELD_THIN",
        catalog_yield_pct=catalog_yield,
        song_count=songs,
        recurring_income_analog="catalog_streaming_annuity",
        rule="Hipgnosis/Blackstone model — music catalog bind is perpetual streaming annuity.",
    )


_REAL_TAYLOR = {
    "institution": "Taylor Swift — masters re-recording ('Taylor's Version') strategy",
    "event": "Re-recorded albums after Big Machine masters sale (2019–2023)",
    "mechanism": "Copyright in new sound recordings reclaims performance income",
    "url": "https://www.copyright.gov/help/faq/faq-soundrecordings.html",
}


def _eval_taylor_masters_rerecord(**kwargs: Any) -> dict[str, Any]:
    owns_masters = bool(kwargs.get("owns_masters"))
    rerecord_rights = bool(kwargs.get("rerecord_rights") or kwargs.get("can_rerecord"))
    contract_block = bool(kwargs.get("contract_block") or kwargs.get("exclusive_lock"))
    if contract_block and not rerecord_rights:
        return _out(
            "taylor_masters_rerecord",
            "Taylor Masters Re-record",
            _REAL_TAYLOR,
            "RERECORD_BLOCKED",
            owns_masters=owns_masters,
            rerecord_rights=False,
            recurring_income_analog="master_recording_stream",
            rule="Lost masters without re-record rights — bind income flows to prior owner.",
        )
    return _out(
        "taylor_masters_rerecord",
        "Taylor Masters Re-record",
        _REAL_TAYLOR,
        "RERECORD_RECLAIM_OK" if rerecord_rights or owns_masters else "MASTERS_AT_RISK",
        owns_masters=owns_masters,
        rerecord_rights=rerecord_rights,
        recurring_income_analog="master_recording_stream",
        rule="Taylor's Version proves re-recording reclaims IP when masters are encumbered.",
    )


_REAL_FRAND = {
    "institution": "FRAND — Fair, Reasonable, And Non-Discriminatory SEP licensing",
    "bodies": "ETSI · IEEE · ITU standard-essential patent commitments",
    "url": "https://www.etsi.org/intellectual-property-rights",
}


def _eval_frand_sep_choke(**kwargs: Any) -> dict[str, Any]:
    sep = bool(kwargs.get("standard_essential") or kwargs.get("sep"))
    frand_offered = bool(kwargs.get("frand_offered") or kwargs.get("frand_terms"))
    holdout = bool(kwargs.get("holdout") or kwargs.get("injunction_sought"))
    if sep and (holdout or not frand_offered):
        return _out(
            "frand_sep_choke",
            "FRAND SEP Choke",
            _REAL_FRAND,
            "FRAND_CHOKE_DENY",
            standard_essential=sep,
            frand_offered=frand_offered,
            recurring_income_analog="sep_royalty_pool",
            rule="SEP without FRAND offer — injunction choke blocks bind until terms published.",
        )
    return _out(
        "frand_sep_choke",
        "FRAND SEP Choke",
        _REAL_FRAND,
        "FRAND_OK",
        standard_essential=sep,
        frand_offered=frand_offered or not sep,
        recurring_income_analog="sep_royalty_pool",
        rule="Standard-essential bind must offer FRAND — pool toll before stick.",
    )


_REAL_MPEG = {
    "institution": "MPEG / AAC patent pool — Via Licensing / MPEG LA",
    "codecs": "H.264 · H.265/HEVC · AAC — collective patent toll",
    "url": "https://www.vialicensing.com/",
}


def _eval_mpeg_patent_pool_toll(**kwargs: Any) -> dict[str, Any]:
    codec = (kwargs.get("codec") or kwargs.get("format") or "h264").lower()
    pool_paid = bool(kwargs.get("pool_license_paid") or kwargs.get("patent_pool_cleared"))
    units = max(0, int(kwargs.get("units") or kwargs.get("bind_units") or 0))
    if codec in ("h264", "hevc", "h265", "aac") and not pool_paid:
        return _out(
            "mpeg_patent_pool_toll",
            "MPEG Patent Pool Toll",
            _REAL_MPEG,
            "POOL_TOLL_DENY",
            codec=codec,
            pool_license_paid=False,
            recurring_income_analog="codec_pool_per_unit_toll",
            rule="MPEG/AAC pool toll unpaid — codec bind is DENY until collective license.",
        )
    return _out(
        "mpeg_patent_pool_toll",
        "MPEG Patent Pool Toll",
        _REAL_MPEG,
        "POOL_TOLL_OK",
        codec=codec,
        pool_license_paid=pool_paid or codec not in ("h264", "hevc", "h265", "aac"),
        units=units,
        recurring_income_analog="codec_pool_per_unit_toll",
        rule="Patent pool per-unit toll — MPEG-class recurring income on every codec shipment.",
    )


_REAL_QUALCOMM = {
    "institution": "Qualcomm — ASP percentage royalty model (CDMA/LTE SEP)",
    "model": "Royalty as percentage of entire device average selling price",
    "ftc": "FTC v. Qualcomm (2019) — FRAND and ASP royalty scrutiny",
    "url": "https://www.ftc.gov/legal-library/browse/cases-proceedings/141-0199-qualcomm-inc",
}


def _eval_qualcomm_asp_royalty(**kwargs: Any) -> dict[str, Any]:
    asp = float(kwargs.get("asp") or kwargs.get("average_selling_price") or 0.0)
    pct = float(kwargs.get("royalty_pct") or kwargs.get("asp_pct") or 0.0)
    cap = float(kwargs.get("royalty_cap_pct") or 5.0)
    effective = min(pct, cap)
    royalty = round(asp * effective / 100.0, 4) if asp else 0.0
    excessive = pct > cap
    return _out(
        "qualcomm_asp_royalty",
        "Qualcomm ASP Royalty",
        _REAL_QUALCOMM,
        "ASP_ROYALTY_CAP" if excessive else "ASP_ROYALTY_OK",
        asp=asp,
        royalty_pct=pct,
        royalty_cap_pct=cap,
        per_unit_royalty=royalty,
        recurring_income_analog="asp_percentage_royalty",
        rule="Qualcomm ASP % royalty — recurring income scales with device price, capped at FRAND.",
    )


_REAL_JORDAN = {
    "institution": "Air Jordan — Nike royalty per unit sold (Jordan Brand)",
    "model": "Michael Jordan receives royalty on each Jordan Brand unit sold",
    "revenue": "Jordan Brand >$5B annual revenue (Nike FY reports)",
    "url": "https://investors.nike.com/investors/news-events-and-reports/default.aspx",
}


def _eval_jordan_brand_unit_royalty(**kwargs: Any) -> dict[str, Any]:
    per_unit = float(kwargs.get("per_unit_royalty") or kwargs.get("royalty_per_unit") or 0.0)
    units = max(0, int(kwargs.get("units_sold") or kwargs.get("bind_units") or 0))
    mg_met = bool(kwargs.get("minimum_guarantee_met", True))
    if not mg_met:
        return _out(
            "jordan_brand_unit_royalty",
            "Jordan Brand Unit Royalty",
            _REAL_JORDAN,
            "MG_SHORTFALL",
            per_unit_royalty=per_unit,
            units_sold=units,
            recurring_income_analog="unit_royalty_plus_mg",
            rule="Jordan-class unit royalty requires minimum guarantee before overage accrual.",
        )
    total = round(per_unit * units, 4)
    return _out(
        "jordan_brand_unit_royalty",
        "Jordan Brand Unit Royalty",
        _REAL_JORDAN,
        "UNIT_ROYALTY_OK",
        per_unit_royalty=per_unit,
        units_sold=units,
        accrued_royalty=total,
        recurring_income_analog="unit_royalty_plus_mg",
        rule="Per-unit royalty on every Jordan-class bind shipment — likeness income stream.",
    )


_REAL_DISNEY_VAULT = {
    "institution": "Disney Vault — controlled re-release windowing strategy",
    "practice": "Classic titles withdrawn from sale to create scarcity windows",
    "url": "https://www.disney.com/",
}


def _eval_disney_vault_window(**kwargs: Any) -> dict[str, Any]:
    in_vault = bool(kwargs.get("in_vault") or kwargs.get("vault_withdrawn"))
    window_open = bool(kwargs.get("release_window_open") or kwargs.get("window_active"))
    if in_vault and not window_open:
        return _out(
            "disney_vault_window",
            "Disney Vault Window",
            _REAL_DISNEY_VAULT,
            "VAULT_CLOSED_DENY",
            in_vault=True,
            release_window_open=False,
            recurring_income_analog="scarcity_window_spike",
            rule="Vault-closed bind is DENY — IP asset earns on timed re-release windows only.",
        )
    return _out(
        "disney_vault_window",
        "Disney Vault Window",
        _REAL_DISNEY_VAULT,
        "VAULT_WINDOW_OK",
        in_vault=in_vault,
        release_window_open=window_open or not in_vault,
        recurring_income_analog="scarcity_window_spike",
        rule="Vault windowing — recurring income spikes when scarcity window opens.",
    )


_REAL_MARVEL = {
    "institution": "Marvel Cinematic Universe — cross-license character lattice",
    "structure": "Disney/Marvel cross-licensed character rights across film, TV, merchandise",
    "url": "https://www.marvel.com/",
}


def _eval_marvel_cross_license_lattice(**kwargs: Any) -> dict[str, Any]:
    licenses = kwargs.get("cross_licenses") if isinstance(kwargs.get("cross_licenses"), list) else []
    count = len(licenses) if licenses else max(0, int(kwargs.get("license_count") or 0))
    lattice_complete = count >= 2 or bool(kwargs.get("lattice_complete"))
    gap = bool(kwargs.get("license_gap") or kwargs.get("missing_character_rights"))
    if gap or not lattice_complete:
        return _out(
            "marvel_cross_license_lattice",
            "Marvel Cross-License Lattice",
            _REAL_MARVEL,
            "LATTICE_GAP_DENY",
            license_count=count,
            lattice_complete=lattice_complete,
            recurring_income_analog="cross_license_mesh_royalty",
            rule="MCU-class bind requires complete cross-license lattice — no orphan character rights.",
        )
    return _out(
        "marvel_cross_license_lattice",
        "Marvel Cross-License Lattice",
        _REAL_MARVEL,
        "LATTICE_OK",
        license_count=count,
        recurring_income_analog="cross_license_mesh_royalty",
        rule="Cross-license mesh — each character node pays into lattice royalty stream.",
    )


_REAL_WIPO_PCT = {
    "institution": "WIPO PCT — Patent Cooperation Treaty international filing epoch",
    "deadline": "30/31-month national phase entry from priority date",
    "url": "https://www.wipo.int/pct/en/",
}


def _eval_wipo_pct_epoch(**kwargs: Any) -> dict[str, Any]:
    months = max(0, int(kwargs.get("months_since_priority") or kwargs.get("pct_months") or 0))
    national_phase = bool(kwargs.get("national_phase_entered"))
    deadline = 31
    lapsed = months > deadline and not national_phase
    return _out(
        "wipo_pct_epoch",
        "WIPO PCT Epoch",
        _REAL_WIPO_PCT,
        "PCT_LAPSED" if lapsed else "PCT_EPOCH_OK",
        months_since_priority=months,
        national_phase_entered=national_phase,
        deadline_months=deadline,
        recurring_income_analog="international_filing_renewal",
        rule="PCT 30/31-month epoch — missed national phase forfeits international bind asset.",
    )


_REAL_USPTO_PROV = {
    "institution": "USPTO — provisional → non-provisional utility patent ladder",
    "deadline": "12 months from provisional filing to utility conversion",
    "url": "https://www.uspto.gov/patents/basics/types-patent-applications/provisional-application",
}


def _eval_uspto_provisional_ladder(**kwargs: Any) -> dict[str, Any]:
    months = max(0, int(kwargs.get("months_since_provisional") or 0))
    converted = bool(kwargs.get("utility_filed") or kwargs.get("non_provisional_filed"))
    deadline = 12
    lapsed = months > deadline and not converted
    return _out(
        "uspto_provisional_ladder",
        "USPTO Provisional Ladder",
        _REAL_USPTO_PROV,
        "PROVISIONAL_LAPSED" if lapsed else "PROVISIONAL_LADDER_OK",
        months_since_provisional=months,
        utility_filed=converted,
        deadline_months=deadline,
        recurring_income_analog="patent_maintenance_fee_ladder",
        rule="12-month provisional ladder — unconverted provisional cannot stick as licensable asset.",
    )


_REAL_EPOCH_PATENT = {
    "institution": "Gate patent asset — US Provisional 64/124,027",
    "title": "Non-resurrecting halt / epoch lock bind system",
    "operator": "Nisaba LLC",
    "url": "https://www.uspto.gov/patents/search",
    "note": "Formalized as licensable IP asset; parent-child cascade owned by license_fuse module.",
}


def _eval_epoch_lock_patent_asset(**kwargs: Any) -> dict[str, Any]:
    patent_id = (kwargs.get("patent_id") or kwargs.get("license_id") or "64/124,027").strip()
    licensed = bool(kwargs.get("patent_licensed") or kwargs.get("license_fee_paid"))
    parent_live = bool(kwargs.get("license_parent_live", kwargs.get("parent_live")))
    ghost = bool(kwargs.get("ghost_licensing") or kwargs.get("ghost_bind_haunted"))
    if ghost:
        return _out(
            "epoch_lock_patent_asset",
            "Epoch Lock Patent Asset",
            _REAL_EPOCH_PATENT,
            "GHOST_LICENSING_DENY",
            patent_id=patent_id,
            recurring_income_analog="patent_license_royalty_cascade",
            rule="Ghost licensing of 64/124,027 is DENY — sublicense without parent fuse is void.",
            fuse_module="license_fuse",
        )
    if licensed and not parent_live:
        return _out(
            "epoch_lock_patent_asset",
            "Epoch Lock Patent Asset",
            _REAL_EPOCH_PATENT,
            "PARENT_NOT_LIVE",
            patent_id=patent_id,
            recurring_income_analog="patent_license_royalty_cascade",
            rule="Patent sublicense requires LIVE parent — license_fuse owns cascade, not this evaluator.",
            fuse_module="license_fuse",
        )
    return _out(
        "epoch_lock_patent_asset",
        "Epoch Lock Patent Asset",
        _REAL_EPOCH_PATENT,
        "PATENT_ASSET_OK" if licensed else "PATENT_UNLICENSED",
        patent_id=patent_id,
        patent_licensed=licensed,
        parent_live=parent_live,
        recurring_income_analog="patent_license_royalty_cascade",
        rule="64/124,027 as licensable epoch-lock asset — royalty cascades through license_fuse parent.",
        fuse_module="license_fuse",
    )


_REAL_DTSA = {
    "institution": "Defend Trade Secrets Act (2016) — 18 U.S.C. § 1836",
    "remedy": "Federal civil seizure and injunctive relief for trade secret misappropriation",
    "url": "https://www.congress.gov/bill/114th-congress/senate-bill/1890",
}


def _eval_trade_secret_dtsa_vault(**kwargs: Any) -> dict[str, Any]:
    vaulted = bool(kwargs.get("trade_secret_vaulted") or kwargs.get("dtsa_vault"))
    exposed = bool(kwargs.get("secret_exposed") or kwargs.get("misappropriated"))
    reasonable_measures = bool(kwargs.get("reasonable_measures", vaulted))
    if exposed or not reasonable_measures:
        return _out(
            "trade_secret_dtsa_vault",
            "Trade Secret DTSA Vault",
            _REAL_DTSA,
            "DTSA_VAULT_BREACH",
            trade_secret_vaulted=vaulted,
            secret_exposed=exposed,
            rule="DTSA vault breach — exposed trade secret bind is DENY with federal seizure risk.",
        )
    return _out(
        "trade_secret_dtsa_vault",
        "Trade Secret DTSA Vault",
        _REAL_DTSA,
        "DTSA_VAULT_OK",
        trade_secret_vaulted=vaulted,
        reasonable_measures=reasonable_measures,
        recurring_income_analog="trade_secret_licensing_fee",
        rule="DTSA-class vault — trade secrets earn licensing fees while reasonable measures hold.",
    )


_REAL_LANHAM = {
    "institution": "Lanham Act § 43(c) — 15 U.S.C. § 1125(c) trademark dilution",
    "tiers": "Blurring and tarnishment of famous marks",
    "url": "https://www.law.cornell.edu/uscode/text/15/1125",
}


def _eval_lanham_dilution_snare(**kwargs: Any) -> dict[str, Any]:
    famous = bool(kwargs.get("famous_mark") or kwargs.get("target_famous"))
    dilution = bool(kwargs.get("dilution_risk") or kwargs.get("blurring") or kwargs.get("tarnishment"))
    cleared = bool(kwargs.get("dilution_cleared"))
    if famous and dilution and not cleared:
        return _out(
            "lanham_dilution_snare",
            "Lanham Dilution Snare",
            _REAL_LANHAM,
            "DILUTION_SNARE_DENY",
            famous_mark=famous,
            dilution_risk=True,
            recurring_income_analog="famous_mark_dilution_damages",
            rule="Lanham dilution snare — blurring/tarnishment of famous mark blocks bind.",
        )
    return _out(
        "lanham_dilution_snare",
        "Lanham Dilution Snare",
        _REAL_LANHAM,
        "DILUTION_CLEAR",
        famous_mark=famous,
        dilution_risk=dilution,
        dilution_cleared=cleared or not dilution,
        recurring_income_analog="famous_mark_licensing_premium",
        rule="Famous mark licensing premium — dilution clearance required before stick.",
    )


_REAL_PUBLICITY = {
    "institution": "Right of publicity — likeness licensing (state statutory/common law)",
    "examples": "California Civil Code § 3344 · New York Civil Rights Law §§ 50–51",
    "url": "https://www.copyright.gov/docs/microsites/morphing/reports/right-publicity.html",
}


def _eval_right_of_publicity_likeness(**kwargs: Any) -> dict[str, Any]:
    likeness_used = bool(kwargs.get("likeness_used") or kwargs.get("uses_likeness"))
    licensed = bool(kwargs.get("publicity_licensed") or kwargs.get("likeness_cleared"))
    ghost = bool(kwargs.get("ghost_licensing"))
    if likeness_used and (ghost or not licensed):
        return _out(
            "right_of_publicity_likeness",
            "Right of Publicity Likeness",
            _REAL_PUBLICITY,
            "GHOST_LICENSING_DENY" if ghost else "PUBLICITY_DENY",
            likeness_used=True,
            publicity_licensed=licensed,
            recurring_income_analog="likeness_royalty_per_use",
            rule="Likeness bind requires publicity license — ghost likeness licensing is DENY.",
        )
    return _out(
        "right_of_publicity_likeness",
        "Right of Publicity Likeness",
        _REAL_PUBLICITY,
        "PUBLICITY_OK",
        likeness_used=likeness_used,
        publicity_licensed=licensed or not likeness_used,
        recurring_income_analog="likeness_royalty_per_use",
        rule="Right of publicity — recurring likeness royalty on every authorized bind use.",
    )


_REAL_WFH = {
    "institution": "Work made for hire — 17 U.S.C. § 101",
    "effect": "Employer/commissioning party owns copyright when WFH criteria met",
    "url": "https://www.copyright.gov/circs/circ09.pdf",
}


def _eval_work_for_hire_ownership(**kwargs: Any) -> dict[str, Any]:
    wfh = bool(kwargs.get("work_for_hire") or kwargs.get("wfh"))
    written_agreement = bool(kwargs.get("written_agreement", wfh))
    at_stick = bool(kwargs.get("at_stick") or kwargs.get("bind_stick"))
    if at_stick and wfh and not written_agreement:
        return _out(
            "work_for_hire_ownership",
            "Work For Hire Ownership",
            _REAL_WFH,
            "WFH_AGREEMENT_DENY",
            work_for_hire=True,
            written_agreement=False,
            rule="Work-for-hire at bind stick requires written agreement — ownership must transfer at stick.",
        )
    return _out(
        "work_for_hire_ownership",
        "Work For Hire Ownership",
        _REAL_WFH,
        "WFH_OWNERSHIP_OK",
        work_for_hire=wfh,
        written_agreement=written_agreement,
        at_stick=at_stick,
        recurring_income_analog="commissioned_work_fee",
        rule="WFH ownership vests at stick — bind operator owns IP, not ghost contractor claim.",
    )


_REAL_SYNC = {
    "institution": "Synchronization license — music sync rights at point of use",
    "moment": "Irreversible audiovisual fixation requires sync clearance before distribution",
    "url": "https://www.copyright.gov/circs/circ01.pdf",
}


def _eval_sync_license_moment(**kwargs: Any) -> dict[str, Any]:
    audiovisual = bool(kwargs.get("audiovisual") or kwargs.get("sync_needed"))
    cleared = bool(kwargs.get("sync_cleared") or kwargs.get("sync_licensed"))
    irreversible = bool(kwargs.get("irreversible_moment") or kwargs.get("at_stick"))
    if audiovisual and irreversible and not cleared:
        return _out(
            "sync_license_moment",
            "Sync License Moment",
            _REAL_SYNC,
            "SYNC_MOMENT_DENY",
            audiovisual=True,
            sync_cleared=False,
            recurring_income_analog="sync_license_fee",
            rule="Sync rights must clear at irreversible moment — no retroactive sync after stick.",
        )
    return _out(
        "sync_license_moment",
        "Sync License Moment",
        _REAL_SYNC,
        "SYNC_MOMENT_OK",
        audiovisual=audiovisual,
        sync_cleared=cleared or not audiovisual,
        recurring_income_analog="sync_license_fee",
        rule="Sync license fee at irreversible audiovisual fixation — one-time + reuse tiers.",
    )


_REAL_MECHANICAL = {
    "institution": "Mechanical royalty — Copyright Royalty Board statutory rate",
    "stream": "PRO/collective mechanical royalty on reproduction/distribution",
    "url": "https://www.copyright.gov/licensing/",
}


def _eval_mechanical_royalty_stream(**kwargs: Any) -> dict[str, Any]:
    streams = max(0, int(kwargs.get("streams") or kwargs.get("reproductions") or 0))
    rate = float(kwargs.get("mechanical_rate") or kwargs.get("statutory_rate") or 0.124)
    pro_registered = bool(kwargs.get("pro_registered", True))
    accrued = round(streams * rate, 4)
    if streams > 0 and not pro_registered:
        return _out(
            "mechanical_royalty_stream",
            "Mechanical Royalty Stream",
            _REAL_MECHANICAL,
            "PRO_UNREGISTERED",
            streams=streams,
            pro_registered=False,
            recurring_income_analog="mechanical_royalty_stream",
            rule="Mechanical stream accrues but PRO registration required for collection.",
        )
    return _out(
        "mechanical_royalty_stream",
        "Mechanical Royalty Stream",
        _REAL_MECHANICAL,
        "MECHANICAL_STREAM_OK",
        streams=streams,
        mechanical_rate=rate,
        accrued_royalty=accrued,
        recurring_income_analog="mechanical_royalty_stream",
        rule="CRB mechanical rate × reproductions — perpetual PRO collection stream.",
    )


_REAL_SAG = {
    "institution": "SAG-AFTRA — residual payments on reuse of recorded performances",
    "trigger": "Reuse in new media, syndication, streaming triggers residual choke",
    "url": "https://www.sagaftra.org/",
}


def _eval_sag_residual_choke(**kwargs: Any) -> dict[str, Any]:
    union = bool(kwargs.get("sag_aftra") or kwargs.get("union_performance"))
    residuals_paid = bool(kwargs.get("residuals_paid") or kwargs.get("residuals_current"))
    reuse = bool(kwargs.get("reuse") or kwargs.get("new_media_reuse"))
    if union and reuse and not residuals_paid:
        return _out(
            "sag_residual_choke",
            "SAG Residual Choke",
            _REAL_SAG,
            "RESIDUAL_CHOKE_DENY",
            sag_aftra=True,
            reuse=True,
            residuals_paid=False,
            recurring_income_analog="residual_payment_stream",
            rule="SAG-AFTRA residual choke — unpaid reuse blocks bind distribution.",
        )
    return _out(
        "sag_residual_choke",
        "SAG Residual Choke",
        _REAL_SAG,
        "RESIDUAL_OK",
        sag_aftra=union,
        reuse=reuse,
        residuals_paid=residuals_paid or not reuse,
        recurring_income_analog="residual_payment_stream",
        rule="Union performance residuals — recurring choke payment on every reuse window.",
    )


_REAL_MERCH_MG = {
    "institution": "Merchandising license — minimum guarantee (MG) + overage royalty",
    "structure": "Advance MG recouped against percentage royalty on net sales",
    "url": "https://www.copyright.gov/circs/circ01.pdf",
}


def _eval_merchandising_mg_overage(**kwargs: Any) -> dict[str, Any]:
    mg = float(kwargs.get("minimum_guarantee") or kwargs.get("mg") or 0.0)
    sales = float(kwargs.get("net_sales") or kwargs.get("merchandise_sales") or 0.0)
    pct = float(kwargs.get("royalty_pct") or kwargs.get("merchandise_pct") or 10.0)
    overage = max(0.0, sales * pct / 100.0 - mg) if mg else sales * pct / 100.0
    mg_recouped = sales * pct / 100.0 >= mg if mg else True
    return _out(
        "merchandising_mg_overage",
        "Merchandising MG Overage",
        _REAL_MERCH_MG,
        "MG_RECOUPED" if mg_recouped else "MG_UNRECOUPED",
        minimum_guarantee=mg,
        net_sales=sales,
        royalty_pct=pct,
        overage_royalty=round(overage, 4),
        recurring_income_analog="mg_plus_overage_royalty",
        rule="MG recouped first — overage royalty accrues on merchandise bind sales above guarantee.",
    )


_REAL_OIN = {
    "institution": "Open Invention Network — defensive patent pool shield",
    "members": "Google, IBM, Red Hat, Toyota — cross-license Linux ecosystem",
    "url": "https://openinventionnetwork.com/",
}


def _eval_open_invention_network_shield(**kwargs: Any) -> dict[str, Any]:
    oin_member = bool(kwargs.get("oin_member") or kwargs.get("defensive_pool"))
    aggression = bool(kwargs.get("patent_aggression") or kwargs.get("asserting_patents"))
    linux_zone = bool(kwargs.get("linux_ecosystem") or kwargs.get("defensive_zone"))
    if aggression and linux_zone and not oin_member:
        return _out(
            "open_invention_network_shield",
            "Open Invention Network Shield",
            _REAL_OIN,
            "OIN_SHIELD_EXPOSED",
            oin_member=False,
            patent_aggression=True,
            rule="Patent aggression in OIN zone without membership — defensive shield absent.",
        )
    return _out(
        "open_invention_network_shield",
        "Open Invention Network Shield",
        _REAL_OIN,
        "OIN_SHIELD_OK",
        oin_member=oin_member or not aggression,
        defensive_pool=oin_member,
        recurring_income_analog="defensive_pool_dues",
        rule="OIN defensive pool — membership shields bind stack from Linux-ecosystem patent aggression.",
    )


_REAL_COPYLEFT = {
    "institution": "GPL copyleft — viral license contamination on derivative works",
    "trigger": "Distribution of GPL-linked derivative requires source release",
    "url": "https://www.gnu.org/licenses/gpl-3.0.html",
}


def _eval_copyleft_contamination_snare(**kwargs: Any) -> dict[str, Any]:
    gpl_linked = bool(kwargs.get("gpl_linked") or kwargs.get("copyleft_exposure"))
    proprietary = bool(kwargs.get("proprietary_bind") or kwargs.get("closed_source"))
    source_offered = bool(kwargs.get("source_offered") or kwargs.get("gpl_compliant"))
    if gpl_linked and proprietary and not source_offered:
        return _out(
            "copyleft_contamination_snare",
            "Copyleft Contamination Snare",
            _REAL_COPYLEFT,
            "COPYLEFT_CONTAMINATION_DENY",
            gpl_linked=True,
            proprietary_bind=True,
            source_offered=False,
            rule="GPL viral contamination — proprietary bind linked to GPL without source is DENY.",
        )
    return _out(
        "copyleft_contamination_snare",
        "Copyleft Contamination Snare",
        _REAL_COPYLEFT,
        "COPYLEFT_CLEAR",
        gpl_linked=gpl_linked,
        proprietary_bind=proprietary,
        source_offered=source_offered or not gpl_linked,
        rule="Copyleft snare — scan bind path for GPL contamination before proprietary stick.",
    )


_REAL_CC = {
    "institution": "Creative Commons license tier ladder",
    "tiers": "CC BY · CC BY-SA · CC BY-NC · CC BY-NC-SA — ascending restriction",
    "url": "https://creativecommons.org/share-your-work/cclicenses/",
}


def _eval_creative_commons_tier_ladder(**kwargs: Any) -> dict[str, Any]:
    tier = (kwargs.get("cc_tier") or kwargs.get("creative_commons") or "BY").upper().replace("-", "_")
    commercial = bool(kwargs.get("commercial_use", True))
    derivatives = bool(kwargs.get("derivatives_allowed", True))
    nc = "NC" in tier
    sa = "SA" in tier
    if commercial and nc:
        return _out(
            "creative_commons_tier_ladder",
            "Creative Commons Tier Ladder",
            _REAL_CC,
            "CC_NC_VIOLATION",
            cc_tier=tier,
            commercial_use=True,
            recurring_income_analog="nc_license_upgrade_fee",
            rule="NC tier blocks commercial bind — upgrade license or downgrade use.",
        )
    if not derivatives and sa:
        return _out(
            "creative_commons_tier_ladder",
            "Creative Commons Tier Ladder",
            _REAL_CC,
            "CC_SA_VIOLATION",
            cc_tier=tier,
            derivatives_allowed=False,
            rule="SA tier requires share-alike — no proprietary derivative without compatible license.",
        )
    return _out(
        "creative_commons_tier_ladder",
        "Creative Commons Tier Ladder",
        _REAL_CC,
        "CC_TIER_OK",
        cc_tier=tier,
        commercial_use=commercial,
        derivatives_allowed=derivatives,
        recurring_income_analog="attribution_license_stream",
        rule="CC tier ladder — each restriction level gates bind commercialization path.",
    )


_REAL_ESCROW = {
    "institution": "IP escrow — M&A closing condition on intellectual property transfer",
    "function": "Escrow agent holds IP assignments until closing conditions satisfied",
    "url": "https://www.ipo.org/wp-content/uploads/2013/09/IP-Escrow-Guide.pdf",
}


def _eval_ip_escrow_mna_latch(**kwargs: Any) -> dict[str, Any]:
    escrow = bool(kwargs.get("ip_escrow") or kwargs.get("escrow_active"))
    conditions_met = bool(kwargs.get("closing_conditions_met") or kwargs.get("mna_closed"))
    if escrow and not conditions_met:
        return _out(
            "ip_escrow_mna_latch",
            "IP Escrow M&A Latch",
            _REAL_ESCROW,
            "ESCROW_LATCH_HOLD",
            ip_escrow=True,
            closing_conditions_met=False,
            recurring_income_analog="escrow_release_milestone",
            rule="M&A IP escrow latch — bind cannot transfer until closing conditions release.",
        )
    return _out(
        "ip_escrow_mna_latch",
        "IP Escrow M&A Latch",
        _REAL_ESCROW,
        "ESCROW_RELEASED",
        ip_escrow=escrow,
        closing_conditions_met=conditions_met or not escrow,
        recurring_income_analog="escrow_release_milestone",
        rule="IP escrow releases at M&A close — licensable asset transfers with latch receipt.",
    )


_REAL_AUDIT = {
    "institution": "Royalty audit clawback — contract audit rights and recovery",
    "practice": "Licensee audit discovers underpayment → clawback + interest + costs",
    "url": "https://www.copyright.gov/licensing/",
}


def _eval_royalty_audit_clawback(**kwargs: Any) -> dict[str, Any]:
    reported = float(kwargs.get("reported_royalty") or 0.0)
    audited = float(kwargs.get("audited_royalty") or reported)
    audit_rights = bool(kwargs.get("audit_rights", True))
    clawback = max(0.0, audited - reported)
    if audit_rights and clawback > 0:
        return _out(
            "royalty_audit_clawback",
            "Royalty Audit Clawback",
            _REAL_AUDIT,
            "CLAWBACK_DUE",
            reported_royalty=reported,
            audited_royalty=audited,
            clawback_amount=round(clawback, 4),
            recurring_income_analog="audit_recovery_lump_sum",
            rule="Under-reported royalty triggers clawback — audit rights are bind-path enforcement.",
        )
    return _out(
        "royalty_audit_clawback",
        "Royalty Audit Clawback",
        _REAL_AUDIT,
        "AUDIT_CLEAR",
        reported_royalty=reported,
        audited_royalty=audited,
        audit_rights=audit_rights,
        recurring_income_analog="audit_recovery_lump_sum",
        rule="Royalty audit clause — recurring income protected by periodic clawback enforcement.",
    )


_REAL_CROSS_COLLATERAL = {
    "institution": "IP cross-collateral — portfolio basket secures credit facility",
    "structure": "Multiple IP assets pledged as cross-collateral for single loan",
    "url": "https://www.uspto.gov/patents/basics/assignments",
}


def _eval_cross_collateral_ip_basket(**kwargs: Any) -> dict[str, Any]:
    assets = max(0, int(kwargs.get("ip_asset_count") or kwargs.get("portfolio_size") or 0))
    encumbered = bool(kwargs.get("encumbered") or kwargs.get("cross_collateralized"))
    release = bool(kwargs.get("release_obtained") or kwargs.get("lien_released"))
    if encumbered and not release:
        return _out(
            "cross_collateral_ip_basket",
            "Cross Collateral IP Basket",
            _REAL_CROSS_COLLATERAL,
            "BASKET_ENCUMBERED",
            ip_asset_count=assets,
            encumbered=True,
            release_obtained=False,
            recurring_income_analog="collateralized_royalty_stream",
            rule="Cross-collateral basket encumbered — bind transfer blocked until lien release.",
        )
    return _out(
        "cross_collateral_ip_basket",
        "Cross Collateral IP Basket",
        _REAL_CROSS_COLLATERAL,
        "BASKET_CLEAR",
        ip_asset_count=assets,
        encumbered=encumbered,
        release_obtained=release or not encumbered,
        recurring_income_analog="collateralized_royalty_stream",
        rule="IP portfolio basket — recurring royalty stream secures cross-collateral facility.",
    )


_REAL_SEQUEL = {
    "institution": "Character rights sequel option — grant of future work option",
    "structure": "Option fee + exercise price for sequel/derivative character exploitation",
    "url": "https://www.copyright.gov/circs/circ01.pdf",
}


def _eval_character_sequel_option(**kwargs: Any) -> dict[str, Any]:
    option_held = bool(kwargs.get("sequel_option") or kwargs.get("option_held"))
    exercised = bool(kwargs.get("option_exercised"))
    expired = bool(kwargs.get("option_expired"))
    if option_held and expired and not exercised:
        return _out(
            "character_sequel_option",
            "Character Sequel Option",
            _REAL_SEQUEL,
            "OPTION_EXPIRED",
            sequel_option=True,
            option_exercised=False,
            option_expired=True,
            recurring_income_analog="option_fee_plus_sequel_royalty",
            rule="Expired sequel option — character bind reverts; exercise before epoch deadline.",
        )
    return _out(
        "character_sequel_option",
        "Character Sequel Option",
        _REAL_SEQUEL,
        "OPTION_OK" if option_held else "NO_OPTION",
        sequel_option=option_held,
        option_exercised=exercised,
        recurring_income_analog="option_fee_plus_sequel_royalty",
        rule="Character sequel option — option fee now, sequel royalty stream on exercise.",
    )


_REAL_PD_RECOMBINE = {
    "institution": "Public domain recombination — PD use without trademark confusion",
    "doctrine": "PD works reusable; trademark law still bars confusingly similar marks",
    "url": "https://www.copyright.gov/publicdomain/",
}


def _eval_public_domain_recombine(**kwargs: Any) -> dict[str, Any]:
    pd_source = bool(kwargs.get("public_domain_source") or kwargs.get("pd_work"))
    tm_clear = bool(kwargs.get("trademark_clear") or kwargs.get("no_tm_confusion", True))
    ghost = bool(kwargs.get("ghost_licensing"))
    if pd_source and not tm_clear:
        return _out(
            "public_domain_recombine",
            "Public Domain Recombine",
            _REAL_PD_RECOMBINE,
            "TM_CONFUSION_DENY",
            public_domain_source=True,
            trademark_clear=False,
            recurring_income_analog="pd_derivative_revenue",
            rule="PD recombination OK on copyright axis — trademark confusion still DENY.",
        )
    if ghost:
        return _out(
            "public_domain_recombine",
            "Public Domain Recombine",
            _REAL_PD_RECOMBINE,
            "GHOST_LICENSING_DENY",
            public_domain_source=pd_source,
            ghost_licensing=True,
            recurring_income_analog="pd_derivative_revenue",
            rule="Ghost licensing of PD recombination — fake clearance on free work is DENY.",
        )
    return _out(
        "public_domain_recombine",
        "Public Domain Recombine",
        _REAL_PD_RECOMBINE,
        "PD_RECOMBINE_OK",
        public_domain_source=pd_source,
        trademark_clear=tm_clear,
        recurring_income_analog="pd_derivative_revenue",
        rule="PD reuse + TM clearance — recombine freely without confusion or ghost license.",
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class _Invention:
    slug: str
    invention: str
    one_liner: str
    real: dict[str, Any]
    evaluate: Callable[..., dict[str, Any]]


REGISTRY: dict[str, _Invention] = {
    "steamboat_willie_split": _Invention(
        "steamboat_willie_split",
        "Steamboat Willie Split",
        "Copyright PD Jan 1 2024 vs Disney trademark moat on Mickey.",
        _REAL_STEAMBOAT,
        _eval_steamboat_willie_split,
    ),
    "arm_dual_stream": _Invention(
        "arm_dual_stream",
        "Arm Dual Stream",
        "Upfront license fee + per-unit royalty — Arm Holdings semiconductor model.",
        _REAL_ARM,
        _eval_arm_dual_stream,
    ),
    "mickey_trademark_moat": _Invention(
        "mickey_trademark_moat",
        "Mickey Trademark Moat",
        "US Reg 6846660 Steamboat title card trademark survives copyright expiry.",
        _REAL_MICKEY_TM,
        _eval_mickey_trademark_moat,
    ),
    "sonny_bono_extension": _Invention(
        "sonny_bono_extension",
        "Sonny Bono Extension",
        "Copyright Term Extension Act — 95-year corporate term clock.",
        _REAL_SONNY_BONO,
        _eval_sonny_bono_extension,
    ),
    "bowie_bond_securitization": _Invention(
        "bowie_bond_securitization",
        "Bowie Bond Securitization",
        "1997 $55M Bowie Bonds at 7.9% — securitized royalty catalog.",
        _REAL_BOWIE,
        _eval_bowie_bond_securitization,
    ),
    "hipgnosis_catalog_annuity": _Invention(
        "hipgnosis_catalog_annuity",
        "Hipgnosis Catalog Annuity",
        "Music catalog acquisition annuity — Hipgnosis/Blackstone streaming yield.",
        _REAL_HIPGNOSIS,
        _eval_hipgnosis_catalog_annuity,
    ),
    "taylor_masters_rerecord": _Invention(
        "taylor_masters_rerecord",
        "Taylor Masters Re-record",
        "Taylor's Version re-recording reclaims masters when encumbered.",
        _REAL_TAYLOR,
        _eval_taylor_masters_rerecord,
    ),
    "frand_sep_choke": _Invention(
        "frand_sep_choke",
        "FRAND SEP Choke",
        "Standard-essential patent FRAND choke before bind stick.",
        _REAL_FRAND,
        _eval_frand_sep_choke,
    ),
    "mpeg_patent_pool_toll": _Invention(
        "mpeg_patent_pool_toll",
        "MPEG Patent Pool Toll",
        "MPEG/LAAC collective patent pool per-unit toll.",
        _REAL_MPEG,
        _eval_mpeg_patent_pool_toll,
    ),
    "qualcomm_asp_royalty": _Invention(
        "qualcomm_asp_royalty",
        "Qualcomm ASP Royalty",
        "Royalty percentage of average selling price — Qualcomm SEP model.",
        _REAL_QUALCOMM,
        _eval_qualcomm_asp_royalty,
    ),
    "jordan_brand_unit_royalty": _Invention(
        "jordan_brand_unit_royalty",
        "Jordan Brand Unit Royalty",
        "Nike Jordan per-unit royalty on every brand unit sold.",
        _REAL_JORDAN,
        _eval_jordan_brand_unit_royalty,
    ),
    "disney_vault_window": _Invention(
        "disney_vault_window",
        "Disney Vault Window",
        "Vault re-release windowing — scarcity-driven IP income spikes.",
        _REAL_DISNEY_VAULT,
        _eval_disney_vault_window,
    ),
    "marvel_cross_license_lattice": _Invention(
        "marvel_cross_license_lattice",
        "Marvel Cross-License Lattice",
        "MCU cross-license mesh — no orphan character rights.",
        _REAL_MARVEL,
        _eval_marvel_cross_license_lattice,
    ),
    "wipo_pct_epoch": _Invention(
        "wipo_pct_epoch",
        "WIPO PCT Epoch",
        "PCT 30/31-month national phase filing epoch deadline.",
        _REAL_WIPO_PCT,
        _eval_wipo_pct_epoch,
    ),
    "uspto_provisional_ladder": _Invention(
        "uspto_provisional_ladder",
        "USPTO Provisional Ladder",
        "Provisional → non-provisional utility 12-month conversion ladder.",
        _REAL_USPTO_PROV,
        _eval_uspto_provisional_ladder,
    ),
    "epoch_lock_patent_asset": _Invention(
        "epoch_lock_patent_asset",
        "Epoch Lock Patent Asset",
        "Gate patent 64/124,027 as licensable asset — cascade via license_fuse.",
        _REAL_EPOCH_PATENT,
        _eval_epoch_lock_patent_asset,
    ),
    "trade_secret_dtsa_vault": _Invention(
        "trade_secret_dtsa_vault",
        "Trade Secret DTSA Vault",
        "Defend Trade Secrets Act vault — federal misappropriation remedy.",
        _REAL_DTSA,
        _eval_trade_secret_dtsa_vault,
    ),
    "lanham_dilution_snare": _Invention(
        "lanham_dilution_snare",
        "Lanham Dilution Snare",
        "Lanham Act § 1125(c) famous mark dilution blurring/tarnishment.",
        _REAL_LANHAM,
        _eval_lanham_dilution_snare,
    ),
    "right_of_publicity_likeness": _Invention(
        "right_of_publicity_likeness",
        "Right of Publicity Likeness",
        "Likeness licensing — state right of publicity at bind stick.",
        _REAL_PUBLICITY,
        _eval_right_of_publicity_likeness,
    ),
    "work_for_hire_ownership": _Invention(
        "work_for_hire_ownership",
        "Work For Hire Ownership",
        "17 USC § 101 work-for-hire ownership transfer at bind stick.",
        _REAL_WFH,
        _eval_work_for_hire_ownership,
    ),
    "sync_license_moment": _Invention(
        "sync_license_moment",
        "Sync License Moment",
        "Synchronization rights clear at irreversible audiovisual moment.",
        _REAL_SYNC,
        _eval_sync_license_moment,
    ),
    "mechanical_royalty_stream": _Invention(
        "mechanical_royalty_stream",
        "Mechanical Royalty Stream",
        "CRB statutory mechanical royalty PRO collection stream.",
        _REAL_MECHANICAL,
        _eval_mechanical_royalty_stream,
    ),
    "sag_residual_choke": _Invention(
        "sag_residual_choke",
        "SAG Residual Choke",
        "SAG-AFTRA residual payments choke on performance reuse.",
        _REAL_SAG,
        _eval_sag_residual_choke,
    ),
    "merchandising_mg_overage": _Invention(
        "merchandising_mg_overage",
        "Merchandising MG Overage",
        "Minimum guarantee recoup then overage royalty on merchandise.",
        _REAL_MERCH_MG,
        _eval_merchandising_mg_overage,
    ),
    "open_invention_network_shield": _Invention(
        "open_invention_network_shield",
        "Open Invention Network Shield",
        "OIN defensive patent pool shields Linux-ecosystem bind stack.",
        _REAL_OIN,
        _eval_open_invention_network_shield,
    ),
    "copyleft_contamination_snare": _Invention(
        "copyleft_contamination_snare",
        "Copyleft Contamination Snare",
        "GPL viral license contamination snare on proprietary bind.",
        _REAL_COPYLEFT,
        _eval_copyleft_contamination_snare,
    ),
    "creative_commons_tier_ladder": _Invention(
        "creative_commons_tier_ladder",
        "Creative Commons Tier Ladder",
        "CC BY-NC-SA tier ladder gates commercial bind path.",
        _REAL_CC,
        _eval_creative_commons_tier_ladder,
    ),
    "ip_escrow_mna_latch": _Invention(
        "ip_escrow_mna_latch",
        "IP Escrow M&A Latch",
        "IP escrow latch holds assignment until M&A closing conditions.",
        _REAL_ESCROW,
        _eval_ip_escrow_mna_latch,
    ),
    "royalty_audit_clawback": _Invention(
        "royalty_audit_clawback",
        "Royalty Audit Clawback",
        "Royalty audit underpayment clawback + interest enforcement.",
        _REAL_AUDIT,
        _eval_royalty_audit_clawback,
    ),
    "cross_collateral_ip_basket": _Invention(
        "cross_collateral_ip_basket",
        "Cross Collateral IP Basket",
        "IP portfolio cross-collateral basket secures credit facility.",
        _REAL_CROSS_COLLATERAL,
        _eval_cross_collateral_ip_basket,
    ),
    "character_sequel_option": _Invention(
        "character_sequel_option",
        "Character Sequel Option",
        "Character rights sequel option fee + exercise royalty stream.",
        _REAL_SEQUEL,
        _eval_character_sequel_option,
    ),
    "public_domain_recombine": _Invention(
        "public_domain_recombine",
        "Public Domain Recombine",
        "PD recombination without trademark confusion or ghost licensing.",
        _REAL_PD_RECOMBINE,
        _eval_public_domain_recombine,
    ),
}

assert set(REGISTRY.keys()) == set(SLUGS), "REGISTRY keys must match SLUGS exactly"


def evaluate_slug(slug: str, **kwargs: Any) -> dict[str, Any]:
    key = (slug or "").strip().lower()
    inv = REGISTRY.get(key)
    if not inv:
        return {
            "error": "unknown_slug",
            "slug": slug,
            "known": list(SLUGS),
        }
    return inv.evaluate(**kwargs)


_BLOCKER_VERDICTS = frozenset({
    "GHOST_LICENSING_DENY",
    "DILUTION_SNARE_DENY",
    "COPYLEFT_CONTAMINATION_DENY",
    "TRADEMARK_MOAT_DENY",
    "TM_MOAT_DENY",
    "TM_CONFUSION_DENY",
    "FRAND_CHOKE_DENY",
    "POOL_TOLL_DENY",
    "VAULT_CLOSED_DENY",
    "LATTICE_GAP_DENY",
    "PCT_LAPSED",
    "PROVISIONAL_LAPSED",
    "PARENT_NOT_LIVE",
    "DTSA_VAULT_BREACH",
    "PUBLICITY_DENY",
    "WFH_AGREEMENT_DENY",
    "SYNC_MOMENT_DENY",
    "RESIDUAL_CHOKE_DENY",
    "UPFRONT_FEE_DENY",
    "CC_NC_VIOLATION",
    "CC_SA_VIOLATION",
    "ESCROW_LATCH_HOLD",
    "BASKET_ENCUMBERED",
})


def _plan_context(plan: dict[str, Any]) -> dict[str, Any]:
    """Extract bind-path IP fields from a spend plan for ip_asset evaluate calls."""
    epoch = plan.get("epoch") if isinstance(plan.get("epoch"), dict) else {}
    ghost = plan.get("ghost_bind") if isinstance(plan.get("ghost_bind"), dict) else {}
    ip = plan.get("ip") if isinstance(plan.get("ip"), dict) else {}
    license_meta = plan.get("license") if isinstance(plan.get("license"), dict) else {}
    return {
        "ghost_bind_haunted": bool(ghost.get("haunted")),
        "ghost_licensing": bool(
            ghost.get("haunted")
            or plan.get("ghost_licensing")
            or ip.get("ghost_licensing")
        ),
        "public_domain": bool(ip.get("public_domain") or plan.get("public_domain")),
        "trademark_respected": bool(ip.get("trademark_respected", True)),
        "trademark_cleared": bool(ip.get("trademark_cleared") or ip.get("mark_clearance")),
        "dilution_risk": bool(ip.get("dilution_risk") or plan.get("dilution_risk")),
        "dilution_cleared": bool(ip.get("dilution_cleared")),
        "confusingly_similar": bool(ip.get("confusingly_similar")),
        "famous_mark": bool(ip.get("famous_mark")),
        "license_fee_paid": bool(ip.get("license_fee_paid") or license_meta.get("fee_paid")),
        "license_id": plan.get("license_id") or license_meta.get("license_id"),
        "license_parent_live": bool(
            license_meta.get("parent_live")
            or (license_meta.get("state") == "LIVE")
        ),
        "patent_id": ip.get("patent_id") or plan.get("patent_id") or "64/124,027",
        "patent_licensed": bool(ip.get("patent_licensed") or license_meta.get("licensed")),
        "gpl_linked": bool(ip.get("gpl_linked") or plan.get("copyleft_exposure")),
        "copyleft_exposure": bool(ip.get("copyleft_exposure") or plan.get("copyleft_exposure")),
        "proprietary_bind": bool(ip.get("proprietary_bind", True)),
        "source_offered": bool(ip.get("source_offered") or ip.get("gpl_compliant")),
        "cc_tier": ip.get("cc_tier") or plan.get("creative_commons"),
        "commercial_use": ip.get("commercial_use", plan.get("commercial_use", True)),
        "standard_essential": bool(ip.get("standard_essential") or ip.get("sep")),
        "frand_offered": bool(ip.get("frand_offered")),
        "pool_license_paid": bool(ip.get("pool_license_paid")),
        "codec": ip.get("codec"),
        "per_unit_royalty": ip.get("per_unit_royalty"),
        "bind_units": plan.get("bind_units") or ip.get("units"),
        "likeness_used": bool(ip.get("likeness_used")),
        "publicity_licensed": bool(ip.get("publicity_licensed")),
        "work_for_hire": bool(ip.get("work_for_hire")),
        "written_agreement": bool(ip.get("written_agreement")),
        "at_stick": bool(plan.get("at_stick") or plan.get("allow_bind")),
        "sync_needed": bool(ip.get("sync_needed") or ip.get("audiovisual")),
        "sync_cleared": bool(ip.get("sync_cleared")),
        "irreversible_moment": bool(plan.get("allow_bind") or plan.get("at_stick")),
        "sag_aftra": bool(ip.get("sag_aftra")),
        "residuals_paid": bool(ip.get("residuals_paid")),
        "reuse": bool(ip.get("reuse")),
        "oin_member": bool(ip.get("oin_member")),
        "patent_aggression": bool(ip.get("patent_aggression")),
        "ip_escrow": bool(ip.get("ip_escrow") or plan.get("mna_escrow")),
        "closing_conditions_met": bool(ip.get("closing_conditions_met")),
        "encumbered": bool(ip.get("encumbered")),
        "release_obtained": bool(ip.get("release_obtained")),
        "months_since_provisional": ip.get("months_since_provisional"),
        "utility_filed": bool(ip.get("utility_filed")),
        "months_since_priority": ip.get("months_since_priority"),
        "national_phase_entered": bool(ip.get("national_phase_entered")),
        "trade_secret_vaulted": bool(ip.get("trade_secret_vaulted")),
        "secret_exposed": bool(ip.get("secret_exposed")),
        "in_vault": bool(ip.get("in_vault")),
        "release_window_open": bool(ip.get("release_window_open")),
        "public_domain_source": bool(ip.get("public_domain_source")),
        "trademark_clear": bool(ip.get("trademark_clear", True)),
        "epoch_locked": bool(epoch.get("locked") or plan.get("epoch_locked")),
    }


def attach(plan: dict) -> dict:
    ctx = _plan_context(plan)
    layer: dict[str, dict[str, Any]] = {}
    for slug in SLUGS:
        ev = evaluate_slug(slug, **ctx)
        layer[slug] = {
            "verdict": ev.get("verdict"),
            "spec": ev.get("spec"),
            "invention": ev.get("invention"),
            "tier": ev.get("tier"),
        }
        if "recurring_income_analog" in ev:
            layer[slug]["recurring_income_analog"] = ev["recurring_income_analog"]
        if "may_bind" in ev:
            layer[slug]["may_bind"] = ev["may_bind"]
        if "may_stick" in ev:
            layer[slug]["may_stick"] = ev["may_stick"]
        verdict = ev.get("verdict") or ""
        if verdict in _BLOCKER_VERDICTS or verdict.endswith("_DENY"):
            layer[slug]["block"] = True
        if verdict in (
            "GHOST_LICENSING_DENY",
        ):
            layer[slug]["ghost_licensing_block"] = True
        if verdict == "DILUTION_SNARE_DENY":
            layer[slug]["dilution_block"] = True
        if verdict == "COPYLEFT_CONTAMINATION_DENY":
            layer[slug]["copyleft_block"] = True
    plan["ip_asset_deep"] = layer
    blockers = [s for s, v in layer.items() if v.get("block")]
    if blockers:
        plan["ip_asset_deep_blockers"] = blockers
    ghost_blockers = [s for s, v in layer.items() if v.get("ghost_licensing_block")]
    if ghost_blockers:
        plan["ip_asset_deep_ghost_licensing_blockers"] = ghost_blockers
    dilution_blockers = [s for s, v in layer.items() if v.get("dilution_block")]
    if dilution_blockers:
        plan["ip_asset_deep_dilution_blockers"] = dilution_blockers
    copyleft_blockers = [s for s, v in layer.items() if v.get("copyleft_block")]
    if copyleft_blockers:
        plan["ip_asset_deep_copyleft_blockers"] = copyleft_blockers
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
        "spec": "gate-ip-asset-deep-catalog-v1",
        "invention": "IP Asset Deep Catalog",
        "family": FAMILY,
        "tier": TIER,
        "count": len(SLUGS),
        "slugs": list(SLUGS),
        "inventions": entries,
        "well_known": f"{base}/.well-known/ip-asset-deep.json",
        "catalog": f"{base}/.well-known/ip-asset-deep-catalog.json",
    }
