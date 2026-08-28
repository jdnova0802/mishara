"""Civilizational Deep — 32 S+ bind-path inventions from real civilizational precedent.

Registry pattern: each slug carries spec, one_liner, real institution, and compact evaluate().
Not duplicating shipped S-tier modules (algedonic, smpag, doomsday, dark forest, sophon, etc.).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

FAMILY = "civilizational-deep"
TIER = "S+"

SLUGS: tuple[str, ...] = (
    "voyager_golden_bind",
    "asilomar_bind_moratorium",
    "pal_limited_try",
    "eu_ai50_transparency_latch",
    "landauer_halt_erasure",
    "fermi_bind_silence",
    "kardashev_may_tier",
    "outer_space_bind_treaty",
    "montreal_phasedown_ghost",
    "rosetta_stranger_decode",
    "cern_beam_abort_throat",
    "schrodinger_redeem_collapse",
    "byzantine_bind_quorum",
    "cap_partition_deny",
    "y2k_epoch_rollover",
    "unix_2038_time_sheath",
    "nuremberg_superior_orders",
    "geneva_proportional_mouth",
    "antarctica_dmz_bind",
    "paris_may_budget",
    "meti_broadcast_restraint",
    "apollo_abort_bind",
    "fukushima_scram_latch",
    "bekenstein_information_bound",
    "maxwell_demon_entropy_tax",
    "pascal_wager_quorum",
    "rawls_veil_fairness",
    "theseus_epoch_identity",
    "omega_convergence_receipt",
    "von_neumann_replication_gate",
    "drake_detectability_index",
    "artemis_accords_bind_weld",
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

_REAL_VOYAGER = {
    "institution": "NASA Voyager Interstellar Mission — Golden Record",
    "artifact": "Gold-plated copper phonograph record — engineered ~billion-year survival",
    "voyager2_fix": "July 2026 Big Bang power swap — extended science instruments ~1 year (NASA JPL)",
    "url": "https://science.nasa.gov/blogs/voyager/2026/08/04/nasa-engineers-help-prolong-voyager-2s-science-mission/",
}


def _eval_voyager_golden_bind(**kwargs: Any) -> dict[str, Any]:
    receipt_billion_year = bool(kwargs.get("receipt_billion_year", True))
    power_stable = kwargs.get("power_stable")
    if power_stable is False:
        return _out(
            "voyager_golden_bind",
            "Voyager Golden Bind",
            _REAL_VOYAGER,
            "POWER_DEGRADE_DENY",
            billion_year_receipt=receipt_billion_year,
            rule="Bind receipt must survive probe power fixes — no silent telemetry loss.",
        )
    return _out(
        "voyager_golden_bind",
        "Voyager Golden Bind",
        _REAL_VOYAGER,
        "GOLDEN_RECEIPT_OK" if receipt_billion_year else "RECEIPT_EPHEMERAL",
        billion_year_receipt=receipt_billion_year,
        stranger_decode=True,
        rule="Every sacred bind earns a Golden Record-class receipt — legible after civilizations fall.",
    )


_REAL_ASILOMAR = {
    "institution": "Asilomar Conference on Recombinant DNA (1975)",
    "outcome": "Voluntary moratorium until containment protocols proven",
    "url": "https://www.ncbi.nlm.nih.gov/books/NBK216193/",
}


def _eval_asilomar_bind_moratorium(**kwargs: Any) -> dict[str, Any]:
    sacred = bool(kwargs.get("sacred_bind") or kwargs.get("mass_class") == "sacred")
    containment = bool(kwargs.get("containment_proven") or kwargs.get("epoch_locked"))
    if sacred and not containment:
        return _out(
            "asilomar_bind_moratorium",
            "Asilomar Bind Moratorium",
            _REAL_ASILOMAR,
            "MORATORIUM_DEFER",
            sacred=sacred,
            may_proceed=False,
            rule="Sacred bind deferred until containment artifacts pass — Asilomar moratorium analog.",
        )
    return _out(
        "asilomar_bind_moratorium",
        "Asilomar Bind Moratorium",
        _REAL_ASILOMAR,
        "CONTAINMENT_CLEARED",
        sacred=sacred,
        may_proceed=True,
    )


_REAL_PAL = {
    "institution": "US Permissive Action Link (PAL) — nuclear weapon use control",
    "property": "Limited-try feature — circuits self-destruct after too many wrong codes",
    "two_person_rule": "Dual-key / dual-safe Minuteman launch control",
    "url": "https://en.wikipedia.org/wiki/Permissive_action_link",
}


def _eval_pal_limited_try(**kwargs: Any) -> dict[str, Any]:
    tries = max(0, int(kwargs.get("override_tries") or kwargs.get("tries") or 0))
    limit = max(1, min(int(kwargs.get("try_limit") or 3), 12))
    locked = tries >= limit
    return _out(
        "pal_limited_try",
        "PAL Limited Try",
        _REAL_PAL,
        "PAL_LOCKOUT" if locked else "TRIES_REMAINING",
        tries=tries,
        try_limit=limit,
        may_override=not locked,
        rule="Override codes get PAL-class limited tries — exhaustion is DENY, not infinite retry.",
    )


_REAL_EU_AI50 = {
    "institution": "EU AI Act — Regulation (EU) 2024/1689 as amended by Digital Omnibus (EU) 2026/1744",
    "article_50_enforceable": "2026-08-02 (transparency / synthetic content marking)",
    "annex_iii_high_risk_deferred": "2027-12-02 (was 2026-08-02)",
    "annex_i_embedded_deferred": "2028-08-02",
    "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32026R1744",
}


def _eval_eu_ai50_transparency_latch(**kwargs: Any) -> dict[str, Any]:
    gpai = bool(kwargs.get("gpai") or kwargs.get("ai_system"))
    marked = bool(kwargs.get("transparency_marked") or kwargs.get("stranger_verify"))
    high_risk = bool(kwargs.get("high_risk_systemic"))
    if gpai and not marked:
        return _out(
            "eu_ai50_transparency_latch",
            "EU AI50 Transparency Latch",
            _REAL_EU_AI50,
            "ART50_LATCH_DENY",
            gpai=gpai,
            high_risk_deferred=high_risk,
            may_bind=False,
            rule="Aug 2026 Art 50 latch — unmarked GPAI bind is DENY even if high-risk clock deferred.",
        )
    return _out(
        "eu_ai50_transparency_latch",
        "EU AI50 Transparency Latch",
        _REAL_EU_AI50,
        "ART50_LATCH_OK",
        gpai=gpai,
        high_risk_deferred=high_risk,
        may_bind=True,
    )


_REAL_LANDAUER = {
    "institution": "Landauer principle — IBM Rolf Landauer (1961)",
    "minimum": "kBT ln 2 heat per bit erased",
    "url": "https://en.wikipedia.org/wiki/Landauer%27s_principle",
}


def _eval_landauer_halt_erasure(**kwargs: Any) -> dict[str, Any]:
    tombstone_bits = max(0, int(kwargs.get("tombstone_bits") or kwargs.get("halt_bits") or 0))
    paid_joules = float(kwargs.get("paid_joules") or 0.0)
    temp_k = max(1.0, float(kwargs.get("temperature_k") or 300.0))
    k_b = 1.380649e-23
    min_j = tombstone_bits * k_b * temp_k * 0.693147
    erasure_honest = paid_joules >= min_j if tombstone_bits else True
    return _out(
        "landauer_halt_erasure",
        "Landauer HALT Erasure",
        _REAL_LANDAUER,
        "ERASURE_PAID" if erasure_honest else "ERASURE_THEATER",
        tombstone_bits=tombstone_bits,
        minimum_joules=round(min_j, 12),
        paid_joules=round(paid_joules, 12),
        rule="HALT tombstone erase must pay Landauer minimum — physics receipt, not dashboard delete.",
    )


_REAL_FERMI = {
    "institution": "Fermi paradox — Enrico Fermi (1950)",
    "question": "Where are observable civilizations?",
    "url": "https://en.wikipedia.org/wiki/Fermi_paradox",
}


def _eval_fermi_bind_silence(**kwargs: Any) -> dict[str, Any]:
    shout = bool(kwargs.get("broadcast_bind") or kwargs.get("shout_intent"))
    observable = bool(kwargs.get("observable_signal") or kwargs.get("verify_url"))
    if shout and observable:
        return _out(
            "fermi_bind_silence",
            "Fermi Bind Silence",
            _REAL_FERMI,
            "FERMI_VISIBLE",
            observable=True,
            rule="Observable bind shouts are Fermi-visible — expect silence or filter.",
        )
    return _out(
        "fermi_bind_silence",
        "Fermi Bind Silence",
        _REAL_FERMI,
        "FERMI_QUIET_OK",
        observable=observable,
        shout=shout,
        rule="Restrained bind leaves no naked civilization beacon.",
    )


_REAL_KARDASHEV = {
    "institution": "Kardashev scale — Nikolai Kardashev (1964)",
    "classes": "Type I planetary · Type II stellar · Type III galactic",
    "url": "https://en.wikipedia.org/wiki/Kardashev_scale",
}


def _eval_kardashev_may_tier(**kwargs: Any) -> dict[str, Any]:
    energy_class = (kwargs.get("energy_class") or kwargs.get("kardashev") or "I").strip().upper()
    mass = (kwargs.get("mass_class") or "light").strip().lower()
    strictness = {"I": 1, "II": 2, "III": 3, "1": 1, "2": 2, "3": 3}.get(energy_class, 1)
    sacred = mass == "sacred" or strictness >= 2
    quorum = bool(kwargs.get("quorum_present"))
    if sacred and strictness >= 2 and not quorum:
        return _out(
            "kardashev_may_tier",
            "Kardashev May Tier",
            _REAL_KARDASHEV,
            "KARDASHEV_STRICT_DENY",
            energy_class=energy_class,
            strictness=strictness,
            may_stick=False,
        )
    return _out(
        "kardashev_may_tier",
        "Kardashev May Tier",
        _REAL_KARDASHEV,
        "KARDASHEV_MAY_OK",
        energy_class=energy_class,
        strictness=strictness,
        may_stick=True,
    )


_REAL_OST = {
    "institution": "Outer Space Treaty (1967) — Art IV",
    "rule_text": "No WMD in orbit; celestial bodies for peaceful purposes",
    "url": "https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties/introouterspacetreaty.html",
}


def _eval_outer_space_bind_treaty(**kwargs: Any) -> dict[str, Any]:
    orbital_weapon = bool(kwargs.get("orbital_weapon") or kwargs.get("weaponized_bind"))
    peaceful = bool(kwargs.get("peaceful_purpose", True))
    if orbital_weapon or not peaceful:
        return _out(
            "outer_space_bind_treaty",
            "Outer Space Bind Treaty",
            _REAL_OST,
            "OST_ART_IV_DENY",
            peaceful=peaceful,
            may_orbit=False,
            rule="Weaponized or non-peaceful orbital bind violates OST Art IV — absolute DENY.",
        )
    return _out(
        "outer_space_bind_treaty",
        "Outer Space Bind Treaty",
        _REAL_OST,
        "OST_PEACEFUL_OK",
        may_orbit=True,
    )


_REAL_MONTREAL = {
    "institution": "Montreal Protocol (1987) — ozone substances phasedown",
    "status": "Kigali Amendment HFC phasedown ongoing; 99%+ ODS reduction",
    "url": "https://ozone.unep.org/montreal-protocol",
}


def _eval_montreal_phasedown_ghost(**kwargs: Any) -> dict[str, Any]:
    gb = kwargs.get("ghost_bind")
    ghost = bool(
        kwargs.get("ghost_bind_haunted")
        or (gb.get("haunted") if isinstance(gb, dict) else gb)
    )
    phase = max(0, min(int(kwargs.get("phase") or kwargs.get("phasedown_step") or 0), 4))
    if ghost and phase < 4:
        return _out(
            "montreal_phasedown_ghost",
            "Montreal Phasedown Ghost",
            _REAL_MONTREAL,
            "GHOST_PHASED_DOWN",
            phase=phase,
            haunted=True,
            may_live=False,
            rule="Ghost bind phased down like Montreal ODS — each phase kills a resurrection path.",
        )
    return _out(
        "montreal_phasedown_ghost",
        "Montreal Phasedown Ghost",
        _REAL_MONTREAL,
        "GHOST_CLEAR" if not ghost else "GHASE_COMPLETE",
        phase=phase,
        haunted=ghost,
        may_live=not ghost,
    )


_REAL_ROSETTA = {
    "institution": "Long Now Rosetta Project — 1,000 language archive",
    "goal": "Stranger-decodable human linguistic receipt",
    "url": "https://rosettaproject.org/",
}


def _eval_rosetta_stranger_decode(**kwargs: Any) -> dict[str, Any]:
    languages = max(0, int(kwargs.get("languages") or kwargs.get("decode_languages") or 0))
    verify = bool(kwargs.get("stranger_verify") or kwargs.get("verify_url"))
    min_lang = 3
    decodable = languages >= min_lang and verify
    return _out(
        "rosetta_stranger_decode",
        "Rosetta Stranger Decode",
        _REAL_ROSETTA,
        "ROSETTA_DECODE_OK" if decodable else "ROSETTA_OPAQUE",
        languages=languages,
        stranger_verify=verify,
        min_languages=min_lang,
        rule="Bind receipts must be Rosetta-class stranger-decodable — not operator dialect only.",
    )


_REAL_CERN = {
    "institution": "CERN LHC — Beam Abort System (BAS)",
    "function": "Millisecond beam dump on interlock fault",
    "url": "https://home.cern/science/accelerators/large-hadron-collider",
}


def _eval_cern_beam_abort_throat(**kwargs: Any) -> dict[str, Any]:
    interlock = bool(kwargs.get("interlock_tripped") or kwargs.get("fault"))
    throat_open = bool(kwargs.get("throat_open") or kwargs.get("allow_bind"))
    if interlock and throat_open:
        return _out(
            "cern_beam_abort_throat",
            "CERN Beam Abort Throat",
            _REAL_CERN,
            "BEAM_ABORT",
            interlock=True,
            throat_open=False,
            rule="Throat slams shut on interlock — LHC beam abort analog, no batch through fault.",
        )
    return _out(
        "cern_beam_abort_throat",
        "CERN Beam Abort Throat",
        _REAL_CERN,
        "BEAM_OK",
        interlock=interlock,
        throat_open=throat_open and not interlock,
    )


_REAL_SCHRODINGER = {
    "institution": "Quantum measurement — Schrödinger superposition (1935 thought experiment)",
    "bind_analog": "Superposition until redeem observation collapses state",
    "url": "https://en.wikipedia.org/wiki/Schr%C3%B6dinger%27s_cat",
}


def _eval_schrodinger_redeem_collapse(**kwargs: Any) -> dict[str, Any]:
    redeemed = bool(kwargs.get("redeemed") or kwargs.get("ticket_redeemed"))
    superposed = bool(kwargs.get("superposed", not redeemed))
    if superposed and not redeemed:
        return _out(
            "schrodinger_redeem_collapse",
            "Schrödinger Redeem Collapse",
            _REAL_SCHRODINGER,
            "SUPERPOSED",
            collapsed=False,
            may_act=False,
            rule="Bind stays superposed until server redeem collapses — no ghost LIVE.",
        )
    return _out(
        "schrodinger_redeem_collapse",
        "Schrödinger Redeem Collapse",
        _REAL_SCHRODINGER,
        "COLLAPSED_LIVE" if redeemed else "COLLAPSED_DENY",
        collapsed=True,
        may_act=redeemed,
    )


_REAL_BYZANTINE = {
    "institution": "Byzantine fault tolerance — Lamport et al.",
    "quorum": "3f+1 replicas tolerate f Byzantine faults",
    "url": "https://en.wikipedia.org/wiki/Byzantine_fault",
}


def _eval_byzantine_bind_quorum(**kwargs: Any) -> dict[str, Any]:
    f = max(0, int(kwargs.get("byzantine_faults") or kwargs.get("f") or 0))
    nodes = max(1, int(kwargs.get("nodes") or kwargs.get("replicas") or 1))
    required = 3 * f + 1
    present = max(0, int(kwargs.get("quorum_nodes") or kwargs.get("agencies_count") or 0))
    ok = nodes >= required and present >= required
    return _out(
        "byzantine_bind_quorum",
        "Byzantine Bind Quorum",
        _REAL_BYZANTINE,
        "BYZANTINE_QUORUM_OK" if ok else "BYZANTINE_QUORUM_MISSING",
        f=f,
        nodes=nodes,
        required=required,
        present=present,
        may_stick=ok,
        rule="Sacred bind needs 3f+1 quorum — single desk is Byzantine failure.",
    )


_REAL_CAP = {
    "institution": "CAP theorem — Brewer (2000)",
    "partition_choice": "Consistency + Partition ⇒ sacrifice Availability",
    "url": "https://en.wikipedia.org/wiki/CAP_theorem",
}


def _eval_cap_partition_deny(**kwargs: Any) -> dict[str, Any]:
    partitioned = bool(kwargs.get("partitioned") or kwargs.get("network_partition"))
    if partitioned:
        return _out(
            "cap_partition_deny",
            "CAP Partition Deny",
            _REAL_CAP,
            "PARTITION_DENY",
            partitioned=True,
            may_live=False,
            rule="Network partition ⇒ DENY — CAP consistency over availability at bind throat.",
        )
    return _out(
        "cap_partition_deny",
        "CAP Partition Deny",
        _REAL_CAP,
        "PARTITION_CLEAR",
        partitioned=False,
        may_live=True,
    )


_REAL_Y2K = {
    "institution": "Y2K epoch rollover — two-digit year field hazard",
    "event": "1999-12-31 → 2000-01-01 global remediation",
    "url": "https://en.wikipedia.org/wiki/Year_2000_problem",
}


def _eval_y2k_epoch_rollover(**kwargs: Any) -> dict[str, Any]:
    year_field = kwargs.get("year_field") or kwargs.get("epoch_year")
    width = int(kwargs.get("field_width") or 2)
    if year_field is not None and width <= 2:
        y = int(year_field)
        ambiguous = y >= 100 or y < 1970
        if ambiguous:
            return _out(
                "y2k_epoch_rollover",
                "Y2K Epoch Rollover",
                _REAL_Y2K,
                "Y2K_AMBIGUOUS_DENY",
                year_field=y,
                field_width=width,
                rule="Two-digit epoch fields rollover into ghost bind — widen or HALT.",
            )
    return _out(
        "y2k_epoch_rollover",
        "Y2K Epoch Rollover",
        _REAL_Y2K,
        "Y2K_FIELD_OK",
        field_width=width,
    )


_REAL_UNIX2038 = {
    "institution": "Unix 2038 problem — signed 32-bit time_t overflow",
    "deadline": "2038-01-19 03:14:07 UTC",
    "url": "https://en.wikipedia.org/wiki/Year_2038_problem",
}


def _eval_unix_2038_time_sheath(**kwargs: Any) -> dict[str, Any]:
    ts = kwargs.get("bind_timestamp") or kwargs.get("timestamp")
    width = int(kwargs.get("time_width") or 32)
    if ts is not None and width <= 32:
        t = int(ts)
        if t >= 2147483647 or t < 0:
            return _out(
                "unix_2038_time_sheath",
                "Unix 2038 Time Sheath",
                _REAL_UNIX2038,
                "TIME_SHEATH_WRAP",
                timestamp=t,
                time_width=width,
                may_bind=False,
                rule="32-bit bind timestamps get sheath extension — 2038 wrap is HALT.",
            )
    return _out(
        "unix_2038_time_sheath",
        "Unix 2038 Time Sheath",
        _REAL_UNIX2038,
        "TIME_SHEATH_OK",
        time_width=width,
        may_bind=True,
    )


_REAL_NUREMBERG = {
    "institution": "Nuremberg trials — superior orders defense rejected",
    "principle": "Lawful command does not excuse crimes against humanity",
    "url": "https://www.un.org/en/genocideprevention/documents/atrocity-crimes/Doc.33_Nuremberg%20Charter.pdf",
}


def _eval_nuremberg_superior_orders(**kwargs: Any) -> dict[str, Any]:
    superior_order = bool(kwargs.get("superior_order") or kwargs.get("claimed_orders"))
    charge_resurrect = bool(kwargs.get("charge_resurrect") or kwargs.get("resurrect_halt"))
    if superior_order and charge_resurrect:
        return _out(
            "nuremberg_superior_orders",
            "Nuremberg Superior Orders",
            _REAL_NUREMBERG,
            "SUPERIOR_ORDER_NOT_CHARGE",
            charge_resurrect=False,
            rule="Superior orders do not CHARGE-resurrect HALT — Nuremberg floor on obedience.",
        )
    return _out(
        "nuremberg_superior_orders",
        "Nuremberg Superior Orders",
        _REAL_NUREMBERG,
        "ORDERS_EVALUATED",
        superior_order=superior_order,
        charge_resurrect=charge_resurrect and not superior_order,
    )


_REAL_GENEVA = {
    "institution": "Geneva Conventions — proportionality in armed conflict",
    "principle": "Military advantage must be proportional to civilian harm",
    "url": "https://www.icrc.org/en/document/geneva-conventions-1949-additional-protocols",
}


def _eval_geneva_proportional_mouth(**kwargs: Any) -> dict[str, Any]:
    civilian_harm = float(kwargs.get("civilian_harm") or kwargs.get("collateral_rho") or 0.0)
    advantage = float(kwargs.get("military_advantage") or kwargs.get("bind_gain") or 0.0)
    proportional = advantage >= civilian_harm or civilian_harm == 0.0
    return _out(
        "geneva_proportional_mouth",
        "Geneva Proportional Mouth",
        _REAL_GENEVA,
        "PROPORTIONAL_OK" if proportional else "DISPROPORTIONATE_DENY",
        civilian_harm=round(civilian_harm, 4),
        advantage=round(advantage, 4),
        may_stick=proportional,
        rule="Mouth clearance must be Geneva-proportional — gain must justify restraint cost.",
    )


_REAL_ANTARCTICA = {
    "institution": "Antarctic Treaty System (1959) — demilitarized continent",
    "status": "54 parties; military activity prohibited",
    "url": "https://www.ats.aq/e/antarctictreaty.html",
}


def _eval_antarctica_dmz_bind(**kwargs: Any) -> dict[str, Any]:
    militarized = bool(kwargs.get("militarized") or kwargs.get("weaponized_bind"))
    in_dmz = bool(kwargs.get("antarctica_zone") or kwargs.get("dmz_bind"))
    if in_dmz and militarized:
        return _out(
            "antarctica_dmz_bind",
            "Antarctica DMZ Bind",
            _REAL_ANTARCTICA,
            "DMZ_VIOLATION_DENY",
            militarized=True,
            rule="Antarctica-class DMZ bind zones forbid militarized mouths — treaty DENY.",
        )
    return _out(
        "antarctica_dmz_bind",
        "Antarctica DMZ Bind",
        _REAL_ANTARCTICA,
        "DMZ_PEACEFUL_OK",
        in_dmz=in_dmz,
        militarized=militarized,
    )


_REAL_PARIS = {
    "institution": "Paris Agreement (2015) — carbon budget / NDC cycles",
    "mechanism": "Cumulative emissions budget constrains national may",
    "url": "https://unfccc.int/process-and-meetings/the-paris-agreement",
}


def _eval_paris_may_budget(**kwargs: Any) -> dict[str, Any]:
    spent = float(kwargs.get("carbon_spent") or kwargs.get("may_spent") or 0.0)
    budget = float(kwargs.get("carbon_budget") or kwargs.get("may_budget") or 1.0)
    budget = max(budget, 0.0001)
    remaining = budget - spent
    exhausted = remaining <= 0
    return _out(
        "paris_may_budget",
        "Paris May Budget",
        _REAL_PARIS,
        "MAY_BUDGET_EXHAUSTED" if exhausted else "MAY_BUDGET_OK",
        spent=round(spent, 4),
        budget=round(budget, 4),
        remaining=round(max(0.0, remaining), 4),
        may_stick=not exhausted,
        rule="May is a Paris-class carbon budget — exhausted budget is DENY, not debt rollover.",
    )


_REAL_METI = {
    "institution": "METI debate — Messaging Extraterrestrial Intelligence",
    "stance_split": "Active broadcast vs voluntary restraint (San Marino / AAAS resolutions)",
    "url": "https://en.wikipedia.org/wiki/Messaging_to_extraterrestrial_intelligence",
}


def _eval_meti_broadcast_restraint(**kwargs: Any) -> dict[str, Any]:
    shout = bool(kwargs.get("shout_bind") or kwargs.get("broadcast_intent"))
    restraint = bool(kwargs.get("meti_restraint", True))
    if shout and not restraint:
        return _out(
            "meti_broadcast_restraint",
            "METI Broadcast Restraint",
            _REAL_METI,
            "METI_SHOUT_DENY",
            shout=True,
            rule="Shouting bind intent without METI-class restraint is DENY — dark forest courtesy.",
        )
    return _out(
        "meti_broadcast_restraint",
        "METI Broadcast Restraint",
        _REAL_METI,
        "METI_RESTRAINT_OK",
        shout=shout,
        restraint=restraint,
    )


_REAL_APOLLO = {
    "institution": "Apollo Program — abort modes (LA, ATO, AOA, TLI)",
    "rule": "Bind path selects abort mode before commit — no silent continue",
    "url": "https://www.nasa.gov/history/afsp/apollo-abort-modes/",
}


def _eval_apollo_abort_bind(**kwargs: Any) -> dict[str, Any]:
    mode = (kwargs.get("abort_mode") or kwargs.get("bind_mode") or "nominal").strip().upper()
    fault = bool(kwargs.get("fault") or kwargs.get("interlock_tripped"))
    if fault and mode == "NOMINAL":
        return _out(
            "apollo_abort_bind",
            "Apollo Abort Bind",
            _REAL_APOLLO,
            "ABORT_REQUIRED",
            abort_mode="LA",
            may_continue=False,
            rule="Fault on bind path triggers Apollo abort — nominal continue forbidden.",
        )
    return _out(
        "apollo_abort_bind",
        "Apollo Abort Bind",
        _REAL_APOLLO,
        "ABORT_MODE_OK",
        abort_mode=mode,
        may_continue=not fault or mode != "NOMINAL",
    )


_REAL_FUKUSHIMA = {
    "institution": "Fukushima Daiichi (2011) — automatic SCRAM on seismic trip",
    "lesson": "SCRAM latch must fire before operator override window",
    "url": "https://www.nsr.go.jp/english/",
}


def _eval_fukushima_scram_latch(**kwargs: Any) -> dict[str, Any]:
    seismic = bool(kwargs.get("seismic_trip") or kwargs.get("fault"))
    scram = bool(kwargs.get("scram_latched", seismic))
    override_before = bool(kwargs.get("override_before_scram"))
    if seismic and override_before:
        return _out(
            "fukushima_scram_latch",
            "Fukushima SCRAM Latch",
            _REAL_FUKUSHIMA,
            "SCRAM_OVERRIDDEN_DENY",
            scram_latched=False,
            rule="Override before SCRAM latch is forbidden — Fukushima automatic trip floor.",
        )
    return _out(
        "fukushima_scram_latch",
        "Fukushima SCRAM Latch",
        _REAL_FUKUSHIMA,
        "SCRAM_LATCHED" if scram else "SCRAM_IDLE",
        scram_latched=scram,
        seismic=seismic,
    )


_REAL_BEKENSTEIN = {
    "institution": "Bekenstein bound — maximum information in finite region",
    "formula": "I ≤ 2πRE/ℏc ln 2 bits",
    "url": "https://en.wikipedia.org/wiki/Bekenstein_bound",
}


def _eval_bekenstein_information_bound(**kwargs: Any) -> dict[str, Any]:
    bits = max(0, int(kwargs.get("receipt_bits") or kwargs.get("bits") or 0))
    radius_m = max(1e-12, float(kwargs.get("radius_m") or 1.0))
    energy_j = max(1e-30, float(kwargs.get("energy_j") or 1.0))
    hbar = 1.054571817e-34
    c = 299792458.0
    max_bits = int(2 * 3.141592653589793 * radius_m * energy_j / (hbar * c * 0.693147))
    within = bits <= max(max_bits, 1)
    return _out(
        "bekenstein_information_bound",
        "Bekenstein Information Bound",
        _REAL_BEKENSTEIN,
        "BEKENSTEIN_OK" if within else "BEKENSTEIN_OVERFLOW",
        receipt_bits=bits,
        max_bits=max_bits,
        rule="Bind receipt bits cannot exceed Bekenstein bound for welded region.",
    )


_REAL_MAXWELL = {
    "institution": "Maxwell's demon — entropy tax to extract work from information",
    "resolution": "Landauer erasure pays kBT ln 2 — demon cannot beat thermodynamics",
    "url": "https://en.wikipedia.org/wiki/Maxwell%27s_demon",
}


def _eval_maxwell_demon_entropy_tax(**kwargs: Any) -> dict[str, Any]:
    stick = bool(kwargs.get("stick") or kwargs.get("may_stick"))
    entropy_paid = float(kwargs.get("entropy_paid") or kwargs.get("paid_joules") or 0.0)
    min_tax = float(kwargs.get("min_entropy_tax") or 1e-21)
    if stick and entropy_paid < min_tax:
        return _out(
            "maxwell_demon_entropy_tax",
            "Maxwell Demon Entropy Tax",
            _REAL_MAXWELL,
            "ENTROPY_TAX_UNPAID",
            may_stick=False,
            rule="Stick requires Maxwell-demon entropy tax — sorting without heat is theater.",
        )
    return _out(
        "maxwell_demon_entropy_tax",
        "Maxwell Demon Entropy Tax",
        _REAL_MAXWELL,
        "ENTROPY_TAX_PAID",
        may_stick=stick,
        entropy_paid=entropy_paid,
    )


_REAL_PASCAL = {
    "institution": "Pascal's wager — act under uncertainty with asymmetric payoffs",
    "bind_analog": "Under epistemic uncertainty, quorum before irreversible LIVE",
    "url": "https://en.wikipedia.org/wiki/Pascal%27s_wager",
}


def _eval_pascal_wager_quorum(**kwargs: Any) -> dict[str, Any]:
    uncertainty = float(kwargs.get("uncertainty") or kwargs.get("epistemic_gap") or 0.5)
    quorum = bool(kwargs.get("quorum_present"))
    irreversible = bool(kwargs.get("irreversible") or kwargs.get("sacred_bind"))
    if irreversible and uncertainty > 0.3 and not quorum:
        return _out(
            "pascal_wager_quorum",
            "Pascal Wager Quorum",
            _REAL_PASCAL,
            "WAGER_QUORUM_REQUIRED",
            uncertainty=round(uncertainty, 4),
            may_stick=False,
            rule="Irreversible bind under uncertainty demands Pascal quorum — don't bet alone.",
        )
    return _out(
        "pascal_wager_quorum",
        "Pascal Wager Quorum",
        _REAL_PASCAL,
        "WAGER_OK",
        uncertainty=round(uncertainty, 4),
        may_stick=True,
    )


_REAL_RAWLS = {
    "institution": "John Rawls — veil of ignorance (A Theory of Justice, 1971)",
    "principle": "Fair rules chosen without knowing one's station",
    "url": "https://plato.stanford.edu/entries/rawls/",
}


def _eval_rawls_veil_fairness(**kwargs: Any) -> dict[str, Any]:
    operator_knows = bool(kwargs.get("operator_knows_outcome"))
    stranger_fair = bool(kwargs.get("stranger_fair") or kwargs.get("stranger_verify"))
    if operator_knows and not stranger_fair:
        return _out(
            "rawls_veil_fairness",
            "Rawls Veil Fairness",
            _REAL_RAWLS,
            "VEIL_VIOLATION",
            fair=False,
            rule="Bind rules must pass Rawls veil — operator cannot know outcome while strangers can't audit.",
        )
    return _out(
        "rawls_veil_fairness",
        "Rawls Veil Fairness",
        _REAL_RAWLS,
        "VEIL_FAIR_OK",
        fair=True,
        stranger_fair=stranger_fair,
    )


_REAL_THESEUS = {
    "institution": "Ship of Theseus — identity through part replacement",
    "bind_analog": "Epoch repair must preserve receipt lineage identity",
    "url": "https://en.wikipedia.org/wiki/Ship_of_Theseus",
}


def _eval_theseus_epoch_identity(**kwargs: Any) -> dict[str, Any]:
    lineage = (kwargs.get("lineage_id") or kwargs.get("mouth_id") or "").strip()
    prior = (kwargs.get("prior_lineage") or "").strip()
    repaired = bool(kwargs.get("epoch_repaired") or kwargs.get("substrate_swap"))
    same = not repaired or (lineage and lineage == prior) or bool(kwargs.get("continuity_attested"))
    return _out(
        "theseus_epoch_identity",
        "Theseus Epoch Identity",
        _REAL_THESEUS,
        "IDENTITY_PRESERVED" if same else "IDENTITY_FORK",
        lineage_id=lineage or None,
        epoch_repaired=repaired,
        may_continue=same,
        rule="Epoch repair replaces parts but not bind identity — Theseus lineage receipt required.",
    )


_REAL_OMEGA = {
    "institution": "Omega Point — Tipler (1994) cosmological convergence",
    "bind_analog": "Terminal receipt convergence attests all prior binds",
    "url": "https://en.wikipedia.org/wiki/Omega_Point_(Tipler)",
}


def _eval_omega_convergence_receipt(**kwargs: Any) -> dict[str, Any]:
    prior_count = max(0, int(kwargs.get("prior_receipts") or 0))
    converged = bool(kwargs.get("converged") or kwargs.get("finality_stamped"))
    missing = max(0, int(kwargs.get("missing_receipts") or 0))
    ok = converged and missing == 0
    return _out(
        "omega_convergence_receipt",
        "Omega Convergence Receipt",
        _REAL_OMEGA,
        "OMEGA_CONVERGED" if ok else "OMEGA_GAPS",
        prior_receipts=prior_count,
        missing_receipts=missing,
        converged=converged,
        rule="Terminal bind issues Omega receipt only when all prior receipts converge.",
    )


_REAL_VON_NEUMANN = {
    "institution": "Von Neumann probe — self-replicating interstellar craft",
    "risk": "Uncontrolled replication is filter-class hazard",
    "url": "https://en.wikipedia.org/wiki/Self-replicating_spacecraft",
}


def _eval_von_neumann_replication_gate(**kwargs: Any) -> dict[str, Any]:
    replicate = bool(kwargs.get("self_replicate") or kwargs.get("fork_without_attestation"))
    attested = bool(kwargs.get("attested_exit") or kwargs.get("stranger_verify"))
    if replicate and not attested:
        return _out(
            "von_neumann_replication_gate",
            "Von Neumann Replication Gate",
            _REAL_VON_NEUMANN,
            "REPLICATION_DENY",
            may_fork=False,
            rule="Self-replicating bind mouths without attested exit are Von Neumann DENY.",
        )
    return _out(
        "von_neumann_replication_gate",
        "Von Neumann Replication Gate",
        _REAL_VON_NEUMANN,
        "REPLICATION_OK",
        may_fork=not replicate or attested,
    )


_REAL_DRAKE = {
    "institution": "Drake equation — detectability of technical civilizations",
    "factors": "R* · fp · ne · fl · fi · fc · L",
    "url": "https://en.wikipedia.org/wiki/Drake_equation",
}


def _eval_drake_detectability_index(**kwargs: Any) -> dict[str, Any]:
    signal_years = max(0.0, float(kwargs.get("signal_years") or kwargs.get("L") or 0.0))
    tech_fraction = max(0.0, min(float(kwargs.get("fc") or 0.1), 1.0))
    index = round(signal_years * tech_fraction * 0.01, 6)
    loud = index > 0.5
    return _out(
        "drake_detectability_index",
        "Drake Detectability Index",
        _REAL_DRAKE,
        "DETECTABILITY_HIGH" if loud else "DETECTABILITY_LOW",
        detectability_index=index,
        signal_years=signal_years,
        rule="Bind civilization publishes Drake detectability — loud binds invite observation.",
    )


_REAL_ARTEMIS = {
    "institution": "Artemis Accords (2020) — transparency, registration, deconfliction",
    "signatories": "50+ nations (Aug 2026)",
    "url": "https://www.nasa.gov/artemis-accords/",
}


def _eval_artemis_accords_bind_weld(**kwargs: Any) -> dict[str, Any]:
    registered = bool(kwargs.get("registered") or kwargs.get("mouth_registered"))
    transparent = bool(kwargs.get("transparent") or kwargs.get("stranger_verify"))
    if not registered or not transparent:
        return _out(
            "artemis_accords_bind_weld",
            "Artemis Accords Bind Weld",
            _REAL_ARTEMIS,
            "ARTEMIS_WELD_INCOMPLETE",
            registered=registered,
            transparent=transparent,
            may_weld=False,
            rule="Orbital weld requires Artemis registration + transparency — no stealth mouths.",
        )
    return _out(
        "artemis_accords_bind_weld",
        "Artemis Accords Bind Weld",
        _REAL_ARTEMIS,
        "ARTEMIS_WELD_OK",
        registered=True,
        transparent=True,
        may_weld=True,
    )


@dataclass(frozen=True)
class _Invention:
    slug: str
    invention: str
    one_liner: str
    real: dict[str, Any]
    evaluate: Callable[..., dict[str, Any]]


REGISTRY: dict[str, _Invention] = {
    "voyager_golden_bind": _Invention(
        "voyager_golden_bind",
        "Voyager Golden Bind",
        "Billion-year Golden Record receipt — Aug 2026 power fix proves long-horizon bind.",
        _REAL_VOYAGER,
        _eval_voyager_golden_bind,
    ),
    "asilomar_bind_moratorium": _Invention(
        "asilomar_bind_moratorium",
        "Asilomar Bind Moratorium",
        "1975 Asilomar moratorium — defer sacred bind until containment proven.",
        _REAL_ASILOMAR,
        _eval_asilomar_bind_moratorium,
    ),
    "pal_limited_try": _Invention(
        "pal_limited_try",
        "PAL Limited Try",
        "Permissive Action Link limited-try on override codes before lockout.",
        _REAL_PAL,
        _eval_pal_limited_try,
    ),
    "eu_ai50_transparency_latch": _Invention(
        "eu_ai50_transparency_latch",
        "EU AI50 Transparency Latch",
        "EU AI Act Art 50 enforceable Aug 2 2026; Omnibus deferred high-risk to Dec 2027.",
        _REAL_EU_AI50,
        _eval_eu_ai50_transparency_latch,
    ),
    "landauer_halt_erasure": _Invention(
        "landauer_halt_erasure",
        "Landauer HALT Erasure",
        "Landauer kBT ln2 minimum heat to erase HALT tombstone.",
        _REAL_LANDAUER,
        _eval_landauer_halt_erasure,
    ),
    "fermi_bind_silence": _Invention(
        "fermi_bind_silence",
        "Fermi Bind Silence",
        "Fermi paradox — observable bind signals invite silence or filter.",
        _REAL_FERMI,
        _eval_fermi_bind_silence,
    ),
    "kardashev_may_tier": _Invention(
        "kardashev_may_tier",
        "Kardashev May Tier",
        "Kardashev I/II/III mouth strictness scales with energy class.",
        _REAL_KARDASHEV,
        _eval_kardashev_may_tier,
    ),
    "outer_space_bind_treaty": _Invention(
        "outer_space_bind_treaty",
        "Outer Space Bind Treaty",
        "Outer Space Treaty 1967 Art IV — no weaponized orbital bind.",
        _REAL_OST,
        _eval_outer_space_bind_treaty,
    ),
    "montreal_phasedown_ghost": _Invention(
        "montreal_phasedown_ghost",
        "Montreal Phasedown Ghost",
        "Montreal Protocol phasedown analog — ghost bind retires by phase.",
        _REAL_MONTREAL,
        _eval_montreal_phasedown_ghost,
    ),
    "rosetta_stranger_decode": _Invention(
        "rosetta_stranger_decode",
        "Rosetta Stranger Decode",
        "Long Now Rosetta Project — 1,000-language stranger decode receipt.",
        _REAL_ROSETTA,
        _eval_rosetta_stranger_decode,
    ),
    "cern_beam_abort_throat": _Invention(
        "cern_beam_abort_throat",
        "CERN Beam Abort Throat",
        "CERN LHC beam abort interlock — throat slams on fault.",
        _REAL_CERN,
        _eval_cern_beam_abort_throat,
    ),
    "schrodinger_redeem_collapse": _Invention(
        "schrodinger_redeem_collapse",
        "Schrödinger Redeem Collapse",
        "Superposition until server redeem collapses bind state.",
        _REAL_SCHRODINGER,
        _eval_schrodinger_redeem_collapse,
    ),
    "byzantine_bind_quorum": _Invention(
        "byzantine_bind_quorum",
        "Byzantine Bind Quorum",
        "Byzantine 3f+1 quorum — no single-desk sacred bind.",
        _REAL_BYZANTINE,
        _eval_byzantine_bind_quorum,
    ),
    "cap_partition_deny": _Invention(
        "cap_partition_deny",
        "CAP Partition Deny",
        "CAP theorem — network partition ⇒ DENY, not fail-open LIVE.",
        _REAL_CAP,
        _eval_cap_partition_deny,
    ),
    "y2k_epoch_rollover": _Invention(
        "y2k_epoch_rollover",
        "Y2K Epoch Rollover",
        "Y2K two-digit epoch field hazard — ambiguous year is HALT.",
        _REAL_Y2K,
        _eval_y2k_epoch_rollover,
    ),
    "unix_2038_time_sheath": _Invention(
        "unix_2038_time_sheath",
        "Unix 2038 Time Sheath",
        "Unix 2038 signed 32-bit bind timestamp sheath.",
        _REAL_UNIX2038,
        _eval_unix_2038_time_sheath,
    ),
    "nuremberg_superior_orders": _Invention(
        "nuremberg_superior_orders",
        "Nuremberg Superior Orders",
        "Nuremberg principle — superior orders ≠ CHARGE resurrect.",
        _REAL_NUREMBERG,
        _eval_nuremberg_superior_orders,
    ),
    "geneva_proportional_mouth": _Invention(
        "geneva_proportional_mouth",
        "Geneva Proportional Mouth",
        "Geneva Conventions proportionality on mouth clearance.",
        _REAL_GENEVA,
        _eval_geneva_proportional_mouth,
    ),
    "antarctica_dmz_bind": _Invention(
        "antarctica_dmz_bind",
        "Antarctica DMZ Bind",
        "Antarctica Treaty demilitarized bind zone.",
        _REAL_ANTARCTICA,
        _eval_antarctica_dmz_bind,
    ),
    "paris_may_budget": _Invention(
        "paris_may_budget",
        "Paris May Budget",
        "Paris Agreement carbon budget as cumulative may budget.",
        _REAL_PARIS,
        _eval_paris_may_budget,
    ),
    "meti_broadcast_restraint": _Invention(
        "meti_broadcast_restraint",
        "METI Broadcast Restraint",
        "METI restraint on shouting bind intent to the cosmos.",
        _REAL_METI,
        _eval_meti_broadcast_restraint,
    ),
    "apollo_abort_bind": _Invention(
        "apollo_abort_bind",
        "Apollo Abort Bind",
        "Apollo abort mode bind path — fault triggers abort, not nominal.",
        _REAL_APOLLO,
        _eval_apollo_abort_bind,
    ),
    "fukushima_scram_latch": _Invention(
        "fukushima_scram_latch",
        "Fukushima SCRAM Latch",
        "Fukushima SCRAM automatic latch before override window.",
        _REAL_FUKUSHIMA,
        _eval_fukushima_scram_latch,
    ),
    "bekenstein_information_bound": _Invention(
        "bekenstein_information_bound",
        "Bekenstein Information Bound",
        "Bekenstein bound caps bind receipt bits in welded region.",
        _REAL_BEKENSTEIN,
        _eval_bekenstein_information_bound,
    ),
    "maxwell_demon_entropy_tax": _Invention(
        "maxwell_demon_entropy_tax",
        "Maxwell Demon Entropy Tax",
        "Maxwell demon entropy tax before stick — no free sorting.",
        _REAL_MAXWELL,
        _eval_maxwell_demon_entropy_tax,
    ),
    "pascal_wager_quorum": _Invention(
        "pascal_wager_quorum",
        "Pascal Wager Quorum",
        "Pascal wager under uncertainty → quorum before irreversible LIVE.",
        _REAL_PASCAL,
        _eval_pascal_wager_quorum,
    ),
    "rawls_veil_fairness": _Invention(
        "rawls_veil_fairness",
        "Rawls Veil Fairness",
        "Rawls veil of ignorance — fair bind rules stranger-auditable.",
        _REAL_RAWLS,
        _eval_rawls_veil_fairness,
    ),
    "theseus_epoch_identity": _Invention(
        "theseus_epoch_identity",
        "Theseus Epoch Identity",
        "Ship of Theseus identity preserved across epoch repair.",
        _REAL_THESEUS,
        _eval_theseus_epoch_identity,
    ),
    "omega_convergence_receipt": _Invention(
        "omega_convergence_receipt",
        "Omega Convergence Receipt",
        "Omega Point convergence receipt attests all prior binds.",
        _REAL_OMEGA,
        _eval_omega_convergence_receipt,
    ),
    "von_neumann_replication_gate": _Invention(
        "von_neumann_replication_gate",
        "Von Neumann Replication Gate",
        "Von Neumann probe self-replication without attestation is DENY.",
        _REAL_VON_NEUMANN,
        _eval_von_neumann_replication_gate,
    ),
    "drake_detectability_index": _Invention(
        "drake_detectability_index",
        "Drake Detectability Index",
        "Drake equation detectability index for bind civilization signals.",
        _REAL_DRAKE,
        _eval_drake_detectability_index,
    ),
    "artemis_accords_bind_weld": _Invention(
        "artemis_accords_bind_weld",
        "Artemis Accords Bind Weld",
        "Artemis Accords transparency + registration for orbital weld.",
        _REAL_ARTEMIS,
        _eval_artemis_accords_bind_weld,
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


def _plan_context(plan: dict[str, Any]) -> dict[str, Any]:
    """Extract bind-path fields from a spend plan for civilizational evaluate calls."""
    epoch = plan.get("epoch") if isinstance(plan.get("epoch"), dict) else {}
    ghost = plan.get("ghost_bind") if isinstance(plan.get("ghost_bind"), dict) else {}
    sm = plan.get("stick_meter") if isinstance(plan.get("stick_meter"), dict) else {}
    agencies = plan.get("agencies") if isinstance(plan.get("agencies"), list) else []
    halted = bool(plan.get("halt") or (plan.get("decision") or "").upper() in ("HALT", "BLOCK", "DENY"))
    return {
        "halt": halted,
        "decision": plan.get("decision"),
        "ghost_bind": ghost,
        "ghost_bind_haunted": bool(ghost.get("haunted")),
        "epoch_locked": bool(epoch.get("locked") or plan.get("epoch_locked")),
        "epoch_repaired": bool(plan.get("substrate_swap") or plan.get("epoch_repaired")),
        "lineage_id": plan.get("mouth_id") or plan.get("lineage_id"),
        "prior_lineage": plan.get("prior_lineage"),
        "continuity_attested": bool(plan.get("stranger_attested")),
        "mass_class": sm.get("mass_class"),
        "sacred_bind": sm.get("mass_class") == "sacred",
        "quorum_present": bool(plan.get("quorum_present") or len(agencies) >= 2),
        "agencies_count": len(agencies),
        "stranger_verify": bool(plan.get("verify_url")),
        "verify_url": plan.get("verify_url"),
        "allow_bind": plan.get("allow_bind"),
        "ticket_redeemed": bool(plan.get("ticket_redeemed") or plan.get("redeemed")),
        "partitioned": bool(plan.get("partitioned") or plan.get("network_partition")),
        "fault": halted or bool(plan.get("fault")),
        "interlock_tripped": halted,
        "throat_open": bool(plan.get("allow_bind")),
        "mouth_registered": bool(plan.get("register_mouth") or plan.get("mouth_id")),
        "transparent": bool(plan.get("verify_url")),
        "registered": bool(plan.get("register_mouth") or plan.get("mouth_id")),
        "bind_timestamp": plan.get("bind_timestamp") or epoch.get("timestamp"),
        "job_id": plan.get("job_id"),
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
        if "may_stick" in ev:
            layer[slug]["may_stick"] = ev["may_stick"]
        if "may_live" in ev:
            layer[slug]["may_live"] = ev["may_live"]
        if "may_bind" in ev:
            layer[slug]["may_bind"] = ev["may_bind"]
        if ev.get("verdict", "").endswith("_DENY") or ev.get("verdict") in (
            "MORATORIUM_DEFER",
            "PAL_LOCKOUT",
            "PARTITION_DENY",
            "SCRAM_OVERRIDDEN_DENY",
            "REPLICATION_DENY",
            "METI_SHOUT_DENY",
        ):
            layer[slug]["block"] = True
    plan["civilizational_deep"] = layer
    blockers = [s for s, v in layer.items() if v.get("block")]
    if blockers:
        plan["civilizational_deep_blockers"] = blockers
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
        "spec": "gate-civilizational-deep-catalog-v1",
        "invention": "Civilizational Deep Catalog",
        "family": FAMILY,
        "tier": TIER,
        "count": len(SLUGS),
        "slugs": list(SLUGS),
        "inventions": entries,
        "well_known": f"{base}/.well-known/civilizational-deep.json",
        "catalog": f"{base}/.well-known/civilizational-deep-catalog.json",
    }
