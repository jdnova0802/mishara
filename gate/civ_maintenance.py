"""Civilization Maintenance — market inventions above L2 foothills.

Thesis: Gate lives through civilizations only if DENY has teeth, prove has a
shared real, losers get deeds, may has telos, operators stay literate, exit
stays attested, joule hostage is honest, the unborn have a seat, domination is
faced, and the name can die.

See CIV_MAINTENANCE.md. Not MGA outbound.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MaintenanceInvention:
    """One civilization-maintenance market invention."""

    id: str
    title: str
    gap_killed: str
    one_line: str
    market_shape: str
    formal_rule: str
    sku_costume: tuple[str, ...]
    not_this: tuple[str, ...] = ()
    rank: int = 0  # 1 = most load-bearing for survival


INVENTIONS: tuple[MaintenanceInvention, ...] = (
    MaintenanceInvention(
        id="teeth_latch",
        title="Teeth Latch",
        gap_killed="DENY with no consequence is forged open",
        one_line=(
            "After DENY, something real must get more expensive — status, capital, "
            "access, or amputation of the write path."
        ),
        market_shape=(
            "Consequence bond tied to high-μ DENY — sanction schedule under "
            "coordinators; stranger-visible; funeral-capable."
        ),
        formal_rule="LIVE/DENY without Teeth Latch ⇒ theater.",
        sku_costume=(
            "commit-control enforcement policy",
            "fail-closed consequence profile",
        ),
        not_this=("private police", "CIC-as-warlord"),
        rank=1,
    ),
    MaintenanceInvention(
        id="reality_root",
        title="Reality Root",
        gap_killed="Epistemic war — rival feeds, deepfakes, split publics",
        one_line=(
            "Prove requires a shared real; without a root quorum, strangers cannot "
            "audit the no."
        ),
        market_shape=(
            "Multi-coordinator prove-root attestation — which ledger/world Gate "
            "receipts bind to; fork detection; rival-root DENY."
        ),
        formal_rule="No Reality Root ⇒ stranger prove collapses into another feed.",
        sku_costume=("receipt root attestation", "audit-world binding"),
        not_this=("one global truth ministry",),
        rank=2,
    ),
    MaintenanceInvention(
        id="loss_deed",
        title="Loss Deed",
        gap_killed="Legitimate losers — DENY creates enemies who call it theft",
        one_line=(
            "Publish who lost, what they lost, why it still counts as a first-class "
            "receipt — not a press release."
        ),
        market_shape=(
            "Examiner/court/public loss pack auto-issued on DENY for sacred classes; "
            "appeal path that cannot soft-LIVE."
        ),
        formal_rule="DENY without Loss Deed ⇒ riot narrative wins; Gate burns.",
        sku_costume=("adverse-action receipt", "denial audit pack"),
        not_this=("therapy", "PR"),
        rank=3,
    ),
    MaintenanceInvention(
        id="telos_charter",
        title="Telos Charter",
        gap_killed="Neutral may gets rented by the worst paying principal",
        one_line=(
            "What Gate is for — and what it will not clear — must be explicit, "
            "revisable under jubilee, never vibes."
        ),
        market_shape=(
            "Versioned charter: anti-runaway, anti-forgery, anti-throne, named "
            "exclusion classes; stranger-readable; coordinator-ratified."
        ),
        formal_rule="May without Telos Charter ⇒ captured weather.",
        sku_costume=("clearance policy charter", "commit-class exclusions"),
        not_this=("culture-war cosplay", "one man's morality"),
        rank=4,
    ),
    MaintenanceInvention(
        id="catechism_ordeal",
        title="Catechism Ordeal",
        gap_killed="Operator illiteracy — LIVE without understanding Bone Law",
        one_line=(
            "Seats that clear high-μ acts must periodically prove they still know "
            "what they clear."
        ),
        market_shape=(
            "Timed ordeal / scenario drill bound to Title Seat renewal; fail ⇒ "
            "seat funeral, not warning email."
        ),
        formal_rule="Illiterate LIVE ⇒ cargo-cult mouth ⇒ catastrophe.",
        sku_costume=("clearance operator certification", "commit-desk fitness"),
        not_this=("LMS theater", "badge collecting"),
        rank=5,
    ),
    MaintenanceInvention(
        id="attested_exit",
        title="Attested Exit",
        gap_killed="Totalizing Gate (Filter) vs underground forgery",
        one_line=(
            "Legitimate fork/exit that preserves prove lineage — leave without "
            "erasing the ledger."
        ),
        market_shape=(
            "Exit protocol: export receipts, tombstone old mouth, birth attested "
            "child root, no soft path around DENY history."
        ),
        formal_rule="No Attested Exit ⇒ underground may or Gate-as-regime.",
        sku_costume=("audit-preserving migration", "controlled clearance fork"),
        not_this=("crypto exit and forget", "dark bind"),
        rank=6,
    ),
    MaintenanceInvention(
        id="joule_hostage",
        title="Joule Hostage Map",
        gap_killed="Mouth captive to whoever owns energy, food, repair, pads",
        one_line=(
            "Every welded mouth publishes what can can kill it — power, plant, "
            "vendor, flag force."
        ),
        market_shape=(
            "Dependence disclosure + hostage score; high hostage ⇒ mandatory "
            "Continuity / dual-plant / coordinator escrow."
        ),
        formal_rule="May that hides its joule hostage ⇒ surprise capture.",
        sku_costume=(
            "operational dependency register",
            "commit-path resilience map",
        ),
        not_this=("Gate becomes an energy company",),
        rank=7,
    ),
    MaintenanceInvention(
        id="unborn_seat",
        title="Unborn Seat",
        gap_killed="Living desks discount the future on sacred long-horizon writes",
        one_line=(
            "High-μ classes require a future-principal constraint — debt to unborn "
            "made executable, not poetic."
        ),
        market_shape=(
            "Charter-bound future seat: delay, escrow, multi-decade inhibit, or "
            "civilizational quorum before LIVE; stranger-visible."
        ),
        formal_rule=(
            "Sacred future writes without Unborn Seat ⇒ present power with vocabulary."
        ),
        sku_costume=(
            "long-horizon commit review",
            "intergenerational clearance constraint",
        ),
        not_this=("mystic council", "one NGO veto forever"),
        rank=8,
    ),
    MaintenanceInvention(
        id="domination_facing",
        title="Domination Facing",
        gap_killed="Fake neutrality — Gate used as domination with receipts",
        one_line=(
            "Every meta-sheath / CMCP / registry deployment must face its domination "
            "stance — disclosed or funeral."
        ),
        market_shape=(
            "Mandatory facing statement in Mouth Registry / Meta-Sheath license; "
            "lying facing ⇒ funeral."
        ),
        formal_rule="Undisclosed domination ⇒ Filter with better HMAC.",
        sku_costume=(
            "governance posture disclosure",
            "control-plane ethics facing",
        ),
        not_this=("purity spiral", "we're just infrastructure cope"),
        rank=9,
    ),
    MaintenanceInvention(
        id="name_death",
        title="Name Death",
        gap_killed="Brand immortality fantasy — Gate/Nisaba as throne",
        one_line=(
            "Success = grammar that survives the company's funeral; brand escheat "
            "is a feature."
        ),
        market_shape=(
            "Pre-committed Name Death bit — open prove roots, de-licensable "
            "meta-sheath, coordinator inheritance of rails without founder key."
        ),
        formal_rule="If Gate cannot die as a name, it will die as a capture.",
        sku_costume=("vendor-exit continuity", "rails after insolvency"),
        not_this=("martyr branding", "open source and pray"),
        rank=10,
    ),
)

INVENTION_BY_ID: dict[str, MaintenanceInvention] = {i.id: i for i in INVENTIONS}

TOP_THREE_IDS: tuple[str, ...] = ("teeth_latch", "reality_root", "loss_deed")

THESIS = (
    "Gate lives through civilizations only if DENY has teeth, prove has a shared "
    "real, losers get deeds, may has telos, operators stay literate, exit stays "
    "attested, joule hostage is honest, the unborn have a seat, domination is "
    "faced, and the name can die."
)

SETTLEMENT_DEPENDENCY = {
    "id": "settlement_dependency",
    "title": "Settlement Dependency",
    "kind": "meta_kpi",
    "definition": (
        "Share of irreversible writes in a domain that cannot settle without a "
        "Gate-class receipt."
    ),
    "use": "Tells you whether you are civilization maintenance or a dashboard.",
    "target_shape": "Climb Settlement Dependency without climbing private Omega.",
}

ENTERABLE_LADDER: tuple[str, ...] = (
    "Bind Room / stranger verify",
    "weld + desk rent",
    "registry / rating / float",
    "Teeth + Loss Deed",
    "Reality Root + Telos",
    "Name Death + Attested Exit",
)


def _invention_to_dict(inv: MaintenanceInvention) -> dict[str, Any]:
    return {
        "id": inv.id,
        "title": inv.title,
        "gap_killed": inv.gap_killed,
        "one_line": inv.one_line,
        "market_shape": inv.market_shape,
        "formal_rule": inv.formal_rule,
        "sku_costume": list(inv.sku_costume),
        "not_this": list(inv.not_this),
        "rank": inv.rank,
    }


def civ_maintenance_manifest(public_url: str | None = None) -> dict[str, Any]:
    """Machine-readable civilization maintenance invention catalog."""
    base = (public_url or "").rstrip("/")
    return {
        "doctrine": "civ_maintenance",
        "version": "1.0.0",
        "layer": "L4_maintenance",
        "thesis": THESIS,
        "invention_count": len(INVENTIONS),
        "top_three": list(TOP_THREE_IDS),
        "inventions": [_invention_to_dict(i) for i in INVENTIONS],
        "settlement_dependency": SETTLEMENT_DEPENDENCY,
        "enterable_ladder": list(ENTERABLE_LADDER),
        "mouth_ceiling": "No new L2 throat spam until paid weld — these are upstairs.",
        "outbound_lock": (
            "Lead cold with AI governance + commit control. Do not lead with "
            "civilization maintenance invention names."
        ),
        "spec": "gate/CIV_MAINTENANCE.md",
        "related": [
            "gate/MAY_WARDEN.md",
            "gate/CRUCIAL_ROLES.md",
            "gate/INVISIBLE_SCALE.md",
            "gate/BONE_LAW.md",
        ],
        "well_known": f"{base}/.well-known/civ-maintenance.json" if base else None,
    }


def get_invention(invention_id: str) -> MaintenanceInvention | None:
    return INVENTION_BY_ID.get(invention_id)


def top_three() -> tuple[MaintenanceInvention, ...]:
    return tuple(INVENTION_BY_ID[i] for i in TOP_THREE_IDS)
