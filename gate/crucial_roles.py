"""Crucial Roles — formal Can't Lose This Guy tier taxonomy (Gate / Nisaba).

Doctrine: can't lose = owns whether irreversible acts COUNT — before, during,
after — across principals, flags, and time.

See CRUCIAL_ROLES.md for the full formal specification.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class RoleTier(str, Enum):
    """Can't-lose tier. S = civilization; C = operational; NOT = replaceable fame."""

    S = "S"
    A = "A"
    B = "B"
    C = "C"
    NOT = "NOT"


@dataclass(frozen=True)
class CrucialRole:
    """One role in the can't-lose taxonomy."""

    id: str
    title: str
    tier: RoleTier
    scope: str
    loss_mode: str
    cant_lose_because: str
    formal_duties: tuple[str, ...] = ()
    load_bearing_for_cic: bool = False


# ── Tier S — civilization / intergalactic weather ────────────────────────────

TIER_S: tuple[CrucialRole, ...] = (
    CrucialRole(
        id="cic",
        title="Chief of Irreversibility Clearance (May Warden)",
        tier=RoleTier.S,
        scope="civilization / intergalactic weather",
        loss_mode="forgery, runaway, or blind commits at scale",
        cant_lose_because="bypass = amputation or forgery at scale",
        formal_duties=(
            "LIVE / DENY / CHOKE on sacred writes",
            "holds the verb every other S-tier role supports",
            "Bind Room = microscopic version of same job",
        ),
    ),
    CrucialRole(
        id="may_metrologist",
        title="May Metrologist (μ / undo-cost)",
        tier=RoleTier.S,
        scope="civilization / intergalactic weather",
        loss_mode="forgery, runaway, or blind commits at scale",
        cant_lose_because="bypass = amputation or forgery at scale",
        formal_duties=("ranks acts by true irreversibility (μ)",),
        load_bearing_for_cic=True,
    ),
    CrucialRole(
        id="cmcp",
        title="Central May Counterparty (CMCP)",
        tier=RoleTier.S,
        scope="civilization / intergalactic weather",
        loss_mode="forgery, runaway, or blind commits at scale",
        cant_lose_because="bypass = amputation or forgery at scale",
        formal_duties=("hard clears novate through one house",),
        load_bearing_for_cic=True,
    ),
    CrucialRole(
        id="unit_of_may",
        title="Unit-of-May Authority (ɱ)",
        tier=RoleTier.S,
        scope="civilization / intergalactic weather",
        loss_mode="forgery, runaway, or blind commits at scale",
        cant_lose_because="bypass = amputation or forgery at scale",
        formal_duties=("everyone prices permission in one unit",),
        load_bearing_for_cic=True,
    ),
    CrucialRole(
        id="stranger_prove_custodian",
        title="Stranger Prove Custodian",
        tier=RoleTier.S,
        scope="civilization / intergalactic weather",
        loss_mode="forgery, runaway, or blind commits at scale",
        cant_lose_because="bypass = amputation or forgery at scale",
        formal_duties=(
            "receipts outlive operators and flags",
            "twin inseparable with CIC — no prove = no chief, just a guy saying yes",
        ),
        load_bearing_for_cic=True,
    ),
    CrucialRole(
        id="principal_continuity",
        title="Principal Continuity Officer",
        tier=RoleTier.S,
        scope="civilization / intergalactic weather",
        loss_mode="forgery, runaway, or blind commits at scale",
        cant_lose_because="bypass = amputation or forgery at scale",
        formal_duties=("no ghost may across death / substrate / handoff",),
        load_bearing_for_cic=True,
    ),
    CrucialRole(
        id="light_delay_commander",
        title="Light-Delay Clearance Commander",
        tier=RoleTier.S,
        scope="civilization / intergalactic weather",
        loss_mode="forgery, runaway, or blind commits at scale",
        cant_lose_because="bypass = amputation or forgery at scale",
        formal_duties=("LIVE across light-cone latency",),
        load_bearing_for_cic=True,
    ),
    CrucialRole(
        id="replication_census",
        title="Replication Census Authority",
        tier=RoleTier.S,
        scope="civilization / intergalactic weather",
        loss_mode="forgery, runaway, or blind commits at scale",
        cant_lose_because="bypass = amputation or forgery at scale",
        formal_duties=("who may copy self-replicating systems",),
        load_bearing_for_cic=True,
    ),
    CrucialRole(
        id="consent_lattice",
        title="Consent Lattice Seat",
        tier=RoleTier.S,
        scope="civilization / intergalactic weather",
        loss_mode="forgery, runaway, or blind commits at scale",
        cant_lose_because="bypass = amputation or forgery at scale",
        formal_duties=("multi-sovereign LIVE on planetary writes",),
        load_bearing_for_cic=True,
    ),
    CrucialRole(
        id="bone_law_engineer",
        title="Bone Law Engineer",
        tier=RoleTier.S,
        scope="civilization / intergalactic weather",
        loss_mode="forgery, runaway, or blind commits at scale",
        cant_lose_because="bypass = amputation or forgery at scale",
        formal_duties=("mouth unextractable from the write surface",),
        load_bearing_for_cic=True,
    ),
)

# ── Tier A — national / program / escape-adjacent ────────────────────────────

TIER_A: tuple[CrucialRole, ...] = (
    CrucialRole(
        id="hard_commit_clearance",
        title="Hard-Commit Clearance Officer",
        tier=RoleTier.A,
        scope="national / program / escape-adjacent",
        loss_mode='wrong irreversible acts become "real"',
        cant_lose_because="they hold legitimacy under blame, not just speed",
        formal_duties=("LIVE / DENY on bind / pay / fire / release class",),
    ),
    CrucialRole(
        id="during_inhibit_commander",
        title="During-Inhibit Commander",
        tier=RoleTier.A,
        scope="national / program / escape-adjacent",
        loss_mode='wrong irreversible acts become "real"',
        cant_lose_because="they hold legitimacy under blame, not just speed",
        formal_duties=("stops mid-sequence cascade",),
    ),
    CrucialRole(
        id="ark_seed_warden",
        title="Ark / Seed Manifest Warden",
        tier=RoleTier.A,
        scope="national / program / escape-adjacent",
        loss_mode='wrong irreversible acts become "real"',
        cant_lose_because="they hold legitimacy under blame, not just speed",
        formal_duties=("what may leave / open / replicate",),
    ),
    CrucialRole(
        id="delta_v_conjunction",
        title="Δv / Conjunction Clearance",
        tier=RoleTier.A,
        scope="national / program / escape-adjacent",
        loss_mode='wrong irreversible acts become "real"',
        cant_lose_because="they hold legitimacy under blame, not just speed",
        formal_duties=("burns and maneuvers without clearance bus",),
    ),
    CrucialRole(
        id="ghost_may_hunter",
        title="Ghost-May Hunter",
        tier=RoleTier.A,
        scope="national / program / escape-adjacent",
        loss_mode='wrong irreversible acts become "real"',
        cant_lose_because="they hold legitimacy under blame, not just speed",
        formal_duties=("soft path / timeout / boss-yes can't stick",),
    ),
    CrucialRole(
        id="funeral_decommission",
        title="Funeral & Decommission Authority",
        tier=RoleTier.A,
        scope="national / program / escape-adjacent",
        loss_mode='wrong irreversible acts become "real"',
        cant_lose_because="they hold legitimacy under blame, not just speed",
        formal_duties=("proves authority is dead when scrapped",),
    ),
    CrucialRole(
        id="oath_roe_compiler",
        title="Oath / ROE Compiler-in-Chief",
        tier=RoleTier.A,
        scope="national / program / escape-adjacent",
        loss_mode='wrong irreversible acts become "real"',
        cant_lose_because="they hold legitimacy under blame, not just speed",
        formal_duties=("rules become executable inhibit graph",),
    ),
    CrucialRole(
        id="restraint_clearing_master",
        title="Restraint Clearing Master",
        tier=RoleTier.A,
        scope="national / program / escape-adjacent",
        loss_mode='wrong irreversible acts become "real"',
        cant_lose_because="they hold legitimacy under blame, not just speed",
        formal_duties=("non-fire settles as mass across desks",),
    ),
)

# ── Tier B — industry weather (hill money tier) ──────────────────────────────

TIER_B: tuple[CrucialRole, ...] = (
    CrucialRole(
        id="clearinghouse_finality",
        title="Clearinghouse / Finality Operator",
        tier=RoleTier.B,
        scope="industry weather (hill money tier)",
        loss_mode="hurts; someone could rebuild over years",
        cant_lose_because="painful to replace for incumbents, not physics",
        formal_duties=("when an act is done-done",),
    ),
    CrucialRole(
        id="interchange_toll",
        title="Interchange / Toll Architect",
        tier=RoleTier.B,
        scope="industry weather (hill money tier)",
        loss_mode="hurts; someone could rebuild over years",
        cant_lose_because="painful to replace for incumbents, not physics",
        formal_duties=("tax on cross-rail commits",),
    ),
    CrucialRole(
        id="mouth_registry_keeper",
        title="Mouth Registry Keeper",
        tier=RoleTier.B,
        scope="industry weather (hill money tier)",
        loss_mode="hurts; someone could rebuild over years",
        cant_lose_because="painful to replace for incumbents, not physics",
        formal_duties=("which throats are attested / live / dead",),
    ),
    CrucialRole(
        id="meta_sheath_licensor",
        title="Meta-Sheath Licensor",
        tier=RoleTier.B,
        scope="industry weather (hill money tier)",
        loss_mode="hurts; someone could rebuild over years",
        cant_lose_because="painful to replace for incumbents, not physics",
        formal_duties=("who may mint mouths (under flag)",),
    ),
    CrucialRole(
        id="mouth_rating_oracle",
        title="Rating Oracle for Mouths",
        tier=RoleTier.B,
        scope="industry weather (hill money tier)",
        loss_mode="hurts; someone could rebuild over years",
        cant_lose_because="painful to replace for incumbents, not physics",
        formal_duties=("stranger grade desks price against",),
    ),
    CrucialRole(
        id="reserve_prove_float",
        title="Reserve Prove Float Manager",
        tier=RoleTier.B,
        scope="industry weather (hill money tier)",
        loss_mode="hurts; someone could rebuild over years",
        cant_lose_because="painful to replace for incumbents, not physics",
        formal_duties=("collateral for stranger-verify capacity",),
    ),
)

# ── Tier C — operational critical ────────────────────────────────────────────

TIER_C: tuple[CrucialRole, ...] = (
    CrucialRole(
        id="pas_bind_path_owner",
        title="PAS Bind Path Owner",
        tier=RoleTier.C,
        scope="operational critical (respect, not immortality)",
        loss_mode="important; replaceable with time + pain",
        cant_lose_because="respect, not immortality",
        formal_duties=("BlocksBind vs quote release",),
    ),
    CrucialRole(
        id="program_gc",
        title="Program GC on Hard Writes",
        tier=RoleTier.C,
        scope="operational critical (respect, not immortality)",
        loss_mode="important; replaceable with time + pain",
        cant_lose_because="respect, not immortality",
        formal_duties=("liability framing",),
    ),
    CrucialRole(
        id="examiner_pack_author",
        title="Examiner-Facing Pack Author",
        tier=RoleTier.C,
        scope="operational critical (respect, not immortality)",
        loss_mode="important; replaceable with time + pain",
        cant_lose_because="respect, not immortality",
        formal_duties=("officer pack / appendix",),
    ),
    CrucialRole(
        id="weld_integrator",
        title="Weld Integrator",
        tier=RoleTier.C,
        scope="operational critical (respect, not immortality)",
        loss_mode="important; replaceable with time + pain",
        cant_lose_because="respect, not immortality",
        formal_duties=("mouth on one production path",),
    ),
    CrucialRole(
        id="incident_receipt_commander",
        title="Incident Receipt Commander",
        tier=RoleTier.C,
        scope="operational critical (respect, not immortality)",
        loss_mode="important; replaceable with time + pain",
        cant_lose_because="respect, not immortality",
        formal_duties=("after-action stranger proof",),
    ),
)

# ── NOT can't-lose tier ────────────────────────────────────────────────────────

TIER_NOT: tuple[CrucialRole, ...] = (
    CrucialRole(
        id="propulsion_hero",
        title="Propulsion / Platform Hero",
        tier=RoleTier.NOT,
        scope="famous but replaceable",
        loss_mode="L0 can; engines exist, may doesn't",
        cant_lose_because="narrative, not finality",
    ),
    CrucialRole(
        id="fusion_ontology_priest",
        title="Fusion / Ontology Priest",
        tier=RoleTier.NOT,
        scope="famous but replaceable",
        loss_mode="L1 sight; advises, doesn't constitute",
        cant_lose_because="narrative, not finality",
    ),
    CrucialRole(
        id="charismatic_ceo",
        title="Charismatic CEO",
        tier=RoleTier.NOT,
        scope="famous but replaceable",
        loss_mode="narrative, not finality",
        cant_lose_because="narrative, not finality",
    ),
    CrucialRole(
        id="ai_model_vendor",
        title="AI Model Vendor",
        tier=RoleTier.NOT,
        scope="famous but replaceable",
        loss_mode="commodity over horizon",
        cant_lose_because="narrative, not finality",
    ),
    CrucialRole(
        id="dashboard_governance",
        title="Dashboard Governance",
        tier=RoleTier.NOT,
        scope="famous but replaceable",
        loss_mode="skippable hall monitor",
        cant_lose_because="narrative, not finality",
    ),
    CrucialRole(
        id="private_omega",
        title="Private Omega / Throne Guy",
        tier=RoleTier.NOT,
        scope="famous but replaceable",
        loss_mode="they remove you, not keep you",
        cant_lose_because="narrative, not finality",
    ),
)

ALL_ROLES: tuple[CrucialRole, ...] = TIER_S + TIER_A + TIER_B + TIER_C + TIER_NOT

ROLE_BY_ID: dict[str, CrucialRole] = {r.id: r for r in ALL_ROLES}

DREAM_SEAT_ID = "cic"
MOST_VITAL_S_TIER_ID = "cic"
INSEPARABLE_TWIN_ID = "stranger_prove_custodian"

ENTERABLE_PATH: tuple[str, ...] = (
    "bind halt + stranger verify",
    "weld",
    "registry / rent",
    "clearance weather",
)

ONE_LINE_CANT_LOSE = (
    "Can't lose = owns whether irreversible acts COUNT — before, during, after — "
    "across principals, flags, and time."
)

ONE_LINE_MOST_VITAL = (
    "Most vital S-tier = whoever holds LIVE on irreversible acts so strangers can "
    "still audit the no."
)


def _role_to_dict(role: CrucialRole) -> dict[str, Any]:
    return {
        "id": role.id,
        "title": role.title,
        "tier": role.tier.value,
        "scope": role.scope,
        "loss_mode": role.loss_mode,
        "cant_lose_because": role.cant_lose_because,
        "formal_duties": list(role.formal_duties),
        "load_bearing_for_cic": role.load_bearing_for_cic,
    }


def crucial_roles_manifest() -> dict[str, Any]:
    """Machine-readable Can't Lose This Guy manifest."""
    by_tier = {
        "S": [_role_to_dict(r) for r in TIER_S],
        "A": [_role_to_dict(r) for r in TIER_A],
        "B": [_role_to_dict(r) for r in TIER_B],
        "C": [_role_to_dict(r) for r in TIER_C],
        "NOT": [_role_to_dict(r) for r in TIER_NOT],
    }
    cic = ROLE_BY_ID[DREAM_SEAT_ID]
    twin = ROLE_BY_ID[INSEPARABLE_TWIN_ID]
    load_bearing = [r.id for r in TIER_S if r.load_bearing_for_cic]

    return {
        "doctrine": "crucial_roles",
        "version": "1.0.0",
        "one_line_cant_lose": ONE_LINE_CANT_LOSE,
        "one_line_most_vital_s_tier": ONE_LINE_MOST_VITAL,
        "dream_seat": {
            "id": cic.id,
            "title": cic.title,
            "tier": cic.tier.value,
        },
        "most_vital_s_tier": {
            "id": MOST_VITAL_S_TIER_ID,
            "title": cic.title,
            "why_beats_other_s_tier": [
                "It IS the verb — LIVE / DENY / CHOKE on sacred writes",
                "Without it, every other S-tier role is metadata about a mouth that doesn't exist",
                "Escape, Δv, replication, ark manifest, handoff — all collapse to: may this irreversible act proceed?",
                "Every other S-tier role exists to make THIS role legitimate, unforgeable, and durable",
            ],
        },
        "inseparable_twin": {
            "clearance_id": cic.id,
            "prove_id": twin.id,
            "rule": "no prove = no chief, just a guy saying yes",
        },
        "load_bearing_for_cic": load_bearing,
        "enterable_path": {
            "tiers": ["C", "B", "A", "S"],
            "steps": list(ENTERABLE_PATH),
            "note": "Same role family. Different μ (undo-cost).",
            "microscopic_version_now": "Bind Room",
        },
        "tiers": {
            tier: {
                "count": len(roles),
                "loss_mode_summary": roles[0].loss_mode if roles else "",
                "roles": by_tier[tier],
            }
            for tier, roles in [
                ("S", TIER_S),
                ("A", TIER_A),
                ("B", TIER_B),
                ("C", TIER_C),
                ("NOT", TIER_NOT),
            ]
        },
        "total_roles": len(ALL_ROLES),
        "spec": "gate/CRUCIAL_ROLES.md",
        "related": ["gate/MAY_WARDEN.md", "gate/BONE_LAW.md"],
    }


def get_role(role_id: str) -> CrucialRole | None:
    return ROLE_BY_ID.get(role_id)


def roles_by_tier(tier: RoleTier) -> tuple[CrucialRole, ...]:
    mapping = {
        RoleTier.S: TIER_S,
        RoleTier.A: TIER_A,
        RoleTier.B: TIER_B,
        RoleTier.C: TIER_C,
        RoleTier.NOT: TIER_NOT,
    }
    return mapping[tier]
