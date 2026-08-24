"""Gate-O / Gate-D skins — same mouth, different commit surfaces.

Invention (Action OS foothill): offensive and defensive *versions* of Gate are
not weapons. They are mass tables + dialect + default invention stacks on the
same throat / quorum / path-compiler grammar.

  Gate-C  Civil     — bind, payout, PAS (paying foothill / costume)
  Gate-D  Defensive — halt unjustified protective release
  Gate-O  Offensive — halt unjustified initiation / projection

LARP gap pack names where Lockheed / Anduril / Raytheon / Palantir stop and
Gate starts — under coordinators, never as a fifth prime.
"""
from __future__ import annotations

from typing import Any

try:
    from gate import stick_meter as stick_mod
except ImportError:
    import stick_meter as stick_mod

SPEC = "gate-od-skins-v1"
INVENTION = "Gate-O / Gate-D Skins"
FAMILY = "applicable_now"

SKIN_CIVIL = "gate_c"
SKIN_DEFENSIVE = "gate_d"
SKIN_OFFENSIVE = "gate_o"

CLASS_LIGHT = stick_mod.CLASS_LIGHT
CLASS_HEAVY = stick_mod.CLASS_HEAVY
CLASS_SACRED = stick_mod.CLASS_SACRED

# Commit surfaces — not effectors. Mouth questions only.
SURFACES_C = (
    {"id": "bind_issue", "question": "May this policy bind-and-issue stick?"},
    {"id": "payout_release", "question": "May this payout leave the vault?"},
    {"id": "agent_tool", "question": "May this agent tool write irreversibly?"},
    {"id": "plc_write", "question": "May this plant write cross the diode?"},
)

SURFACES_D = (
    {"id": "protective_release", "question": "May this defensive effector fire now under ROE?"},
    {"id": "intercept_commit", "question": "May intercept / C-UAS engage commit?"},
    {"id": "shed_to_protect", "question": "May protective shed / trip / lockdown run?"},
    {"id": "border_engage", "question": "May tower / sensor-triggered engage release?"},
    {"id": "continuity_override", "question": "May 'protect at all costs' override the sheath?"},
)

SURFACES_O = (
    {"id": "strike_release", "question": "May this offensive release initiate under ROE?"},
    {"id": "jam_commit", "question": "May spectrum / jam commit stick?"},
    {"id": "sanction_stick", "question": "May this sanction / freeze write stick?"},
    {"id": "agent_initiate", "question": "May this agent initiate an irreversible projection?"},
    {"id": "charisma_go", "question": "May 'boss said go' mint LIVE without quorum?"},
)

# Mass table: edge_id → default mass class (before Stick Meter modifiers)
MASS_C: dict[str, str] = {
    "bind_issue": CLASS_HEAVY,
    "payout_release": CLASS_HEAVY,
    "agent_tool": CLASS_HEAVY,
    "plc_write": CLASS_SACRED,
    "default": CLASS_HEAVY,
}

MASS_D: dict[str, str] = {
    "protective_release": CLASS_SACRED,
    "intercept_commit": CLASS_SACRED,
    "shed_to_protect": CLASS_HEAVY,
    "border_engage": CLASS_SACRED,
    "continuity_override": CLASS_SACRED,
    "default": CLASS_SACRED,
}

MASS_O: dict[str, str] = {
    "strike_release": CLASS_SACRED,
    "jam_commit": CLASS_SACRED,
    "sanction_stick": CLASS_HEAVY,
    "agent_initiate": CLASS_SACRED,
    "charisma_go": CLASS_SACRED,  # always sacred — anti-charisma
    "default": CLASS_SACRED,
}

# Default invention stack each skin leans on (already shipped seeds)
STACK_C = (
    "throat",
    "ghost_bind",
    "desk_quorum_fob",
    "charge_bride",
    "bind_path_compiler",
    "restraint_invoice",
)

STACK_D = (
    "throat",
    "panic_latch",
    "deadman_echo",
    "watchman_fuse",
    "desk_quorum_fob",
    "bind_path_compiler",
    "restraint_invoice",
    "witness_seat",
)

STACK_O = (
    "throat",
    "charge_bride",
    "desk_quorum_fob",
    "soft_yes_snare",
    "indulgence_trap",
    "pardon_sunset",
    "bind_path_compiler",
    "restraint_invoice",
)

FAILURE_C = "soft PAS / timeout treated as LIVE"
FAILURE_D = "panic soft-yes — protect at all costs"
FAILURE_O = "charisma soft-yes — boss said go"

POSTURE = (
    "Under coordinators. Never sovereign. Skins are dialects of one mouth — "
    "not weapons, platforms, or C2."
)

LARP_GAPS = (
    {
        "letter": "L",
        "firm": "Lockheed",
        "they_ship": "Platforms that carry",
        "gate_gap": "May welded into the platform / sheath cell at factory — not PDF ROE",
        "skin_hint": f"{SKIN_DEFENSIVE}+{SKIN_OFFENSIVE}",
    },
    {
        "letter": "A",
        "firm": "Anduril",
        "they_ship": "Autonomy at the edge",
        "gate_gap": "Edge throat — agent/drone cannot commit without LIVE; loss of link ⇒ DENY",
        "skin_hint": SKIN_DEFENSIVE,
    },
    {
        "letter": "R",
        "firm": "Raytheon",
        "they_ship": "Effectors that hit",
        "gate_gap": "Release mouth on the fire edge — prove before / during inhibit / stranger after",
        "skin_hint": f"{SKIN_OFFENSIVE}+{SKIN_DEFENSIVE}",
    },
    {
        "letter": "P",
        "firm": "Palantir",
        "they_ship": "See everything",
        "gate_gap": "Sight ≠ LIVE — mouth on the irreversible act after the pane recommends",
        "skin_hint": f"{SKIN_CIVIL}+{SKIN_OFFENSIVE}",
    },
)

UNIFIED_GAPS = (
    "May as manufactured property — not policy theater",
    "During-inhibit — halt mid-sequence, not only before",
    "Counterfactual prove — receipts for what did not fire",
    "Forge-time DENY proof — unit cannot ship until sheath HIL passes",
    "Anti-Perimeter — contact lost ⇒ DENY, never auto-LIVE",
    "Unified grammar across bind / payout / agent / plant / force",
)


def _norm_skin(skin: str | None) -> str:
    s = (skin or "").strip().lower().replace("-", "_")
    aliases = {
        "c": SKIN_CIVIL,
        "civil": SKIN_CIVIL,
        "gate_c": SKIN_CIVIL,
        "gatec": SKIN_CIVIL,
        "d": SKIN_DEFENSIVE,
        "defensive": SKIN_DEFENSIVE,
        "defense": SKIN_DEFENSIVE,
        "gate_d": SKIN_DEFENSIVE,
        "gated": SKIN_DEFENSIVE,
        "o": SKIN_OFFENSIVE,
        "offensive": SKIN_OFFENSIVE,
        "offense": SKIN_OFFENSIVE,
        "gate_o": SKIN_OFFENSIVE,
        "gateo": SKIN_OFFENSIVE,
    }
    return aliases.get(s, SKIN_CIVIL if not s else s if s in (SKIN_CIVIL, SKIN_DEFENSIVE, SKIN_OFFENSIVE) else SKIN_CIVIL)


def skin_profile(skin: str | None = None) -> dict[str, Any]:
    sid = _norm_skin(skin)
    if sid == SKIN_DEFENSIVE:
        return {
            "skin": SKIN_DEFENSIVE,
            "name": "Gate-D",
            "label": "Defensive",
            "job": "Sheath unjustified protective release when you claim we are protecting",
            "mouth_question": "May this defensive effector fire now, under this ROE?",
            "surfaces": [dict(x) for x in SURFACES_D],
            "mass_table": dict(MASS_D),
            "default_mass": MASS_D["default"],
            "invention_stack": list(STACK_D),
            "failure_mode": FAILURE_D,
            "costume": "Safety / continuity / control — not a shield product",
            "prove_after": "Prove what you held back (restraint) and what you intercepted",
        }
    if sid == SKIN_OFFENSIVE:
        return {
            "skin": SKIN_OFFENSIVE,
            "name": "Gate-O",
            "label": "Offensive",
            "job": "Sheath unjustified initiation when you claim we are projecting",
            "mouth_question": "May this offensive write / release now, under this ROE?",
            "surfaces": [dict(x) for x in SURFACES_O],
            "mass_table": dict(MASS_O),
            "default_mass": MASS_O["default"],
            "invention_stack": list(STACK_O),
            "failure_mode": FAILURE_O,
            "costume": "ROE / pre-fire clearance / audit — not a weapon",
            "prove_after": "Prove clearance chain + what did not fire (counterfactual)",
        }
    return {
        "skin": SKIN_CIVIL,
        "name": "Gate-C",
        "label": "Civil",
        "job": "Sheath unjustified commercial / plant / agent commits",
        "mouth_question": "May this bind / payout / tool / PLC write stick?",
        "surfaces": [dict(x) for x in SURFACES_C],
        "mass_table": dict(MASS_C),
        "default_mass": MASS_C["default"],
        "invention_stack": list(STACK_C),
        "failure_mode": FAILURE_C,
        "costume": "AI governance / control-not-model — paying foothill",
        "prove_after": "Stranger verify_url + restraint invoice on HALT",
    }


def mass_for_edge(*, skin: str | None = None, edge_id: str | None = None) -> str:
    profile = skin_profile(skin)
    table: dict[str, str] = profile["mass_table"]
    eid = (edge_id or "").strip().lower()
    if eid in table:
        return table[eid]
    return table.get("default", CLASS_HEAVY)


def classify(
    *,
    skin: str | None = None,
    edge_id: str | None = None,
    stick_score: int | None = None,
    stick_mass_class: str | None = None,
    panic: bool | None = None,
    boss_said_go: bool | None = None,
    loss_of_link: bool | None = None,
) -> dict[str, Any]:
    """Classify a commit under a skin — mass + default stack + haunt flags."""
    profile = skin_profile(skin)
    sid = profile["skin"]
    edge = (edge_id or "").strip().lower() or None
    mass = mass_for_edge(skin=sid, edge_id=edge)

    # Stick Meter can only raise mass, never lower skin floor for D/O
    if stick_mass_class == CLASS_SACRED:
        mass = CLASS_SACRED
    elif stick_mass_class == CLASS_HEAVY and mass == CLASS_LIGHT:
        mass = CLASS_HEAVY
    if stick_score is not None:
        if stick_score >= 75:
            mass = CLASS_SACRED
        elif stick_score >= 40 and mass == CLASS_LIGHT:
            mass = CLASS_HEAVY

    haunts: list[str] = []
    if sid == SKIN_DEFENSIVE and panic:
        haunts.append("panic_soft_yes")
    if sid == SKIN_OFFENSIVE and boss_said_go:
        haunts.append("charisma_soft_yes")
    if loss_of_link:
        haunts.append("anti_perimeter_deny")  # contact lost ⇒ DENY

    quorum_required = mass in (CLASS_HEAVY, CLASS_SACRED)
    charge_required = mass == CLASS_SACRED or sid in (SKIN_DEFENSIVE, SKIN_OFFENSIVE)

    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "skin": sid,
        "name": profile["name"],
        "edge_id": edge,
        "mass_class": mass,
        "quorum_required": quorum_required,
        "charge_required": charge_required,
        "invention_stack": profile["invention_stack"],
        "mouth_question": profile["mouth_question"],
        "failure_mode": profile["failure_mode"],
        "haunts": haunts,
        "may_mint_weapon": False,
        "rule": (
            "Skin selects mass floor + dialect + invention lean. "
            "Throat still CHOKE on ambiguity. Path compiler still returns procedure. "
            "No soft-allow. No private Omega."
        ),
        "posture": POSTURE,
    }


def larp_gap_pack(public_url: str = "") -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": "gate-larp-gap-pack-v1",
        "invention": "LARP Gap Pack",
        "family": FAMILY,
        "one_liner": "Where L/A/R/P stop; where Gate starts — may / sheath / prove under their can / sight.",
        "acronym_joke": "LARP is a meme. The firms are real. The gap is may.",
        "gaps": [dict(g) for g in LARP_GAPS],
        "unified_gaps": list(UNIFIED_GAPS),
        "skins": {
            SKIN_CIVIL: "Civil foothill — bind / payout (costume for outbound)",
            SKIN_DEFENSIVE: "Defensive mouth — protective release edges",
            SKIN_OFFENSIVE: "Offensive mouth — initiation / projection edges",
        },
        "not": [
            "Not a fifth prime",
            "Not platforms, effectors, or C2",
            "Not MGA email copy — keep force skins out of CUO outbound",
        ],
        "well_known_skins": f"{base}/.well-known/gate-od-skins.json" if base else None,
        "posture": POSTURE,
    }


def attach(plan: dict, *, public_url: str = "") -> dict:
    skin = plan.get("gate_skin") or plan.get("skin") or SKIN_CIVIL
    edge = plan.get("edge_id") or plan.get("commit_surface")
    sm = plan.get("stick_meter") if isinstance(plan.get("stick_meter"), dict) else {}
    mt = plan.get("mass_tag") if isinstance(plan.get("mass_tag"), dict) else {}
    result = classify(
        skin=skin if isinstance(skin, str) else SKIN_CIVIL,
        edge_id=edge if isinstance(edge, str) else None,
        stick_score=sm.get("score"),
        stick_mass_class=mt.get("mass_class") or mt.get("tag") or sm.get("mass_class"),
        panic=bool(plan.get("panic") or plan.get("panic_mode")),
        boss_said_go=bool(plan.get("boss_said_go") or plan.get("boss_said_yes")),
        loss_of_link=bool(plan.get("loss_of_link") or plan.get("link_lost")),
    )
    plan["gate_od_skins"] = result
    # Raise mass tag floor when skin demands sacred/heavy
    if isinstance(mt, dict) and mt:
        floor = result["mass_class"]
        current = mt.get("mass_class") or mt.get("tag") or CLASS_LIGHT
        order = {CLASS_LIGHT: 0, CLASS_HEAVY: 1, CLASS_SACRED: 2}
        if order.get(floor, 0) > order.get(current, 0):
            mt = dict(mt)
            mt["mass_class"] = floor
            mt["tag"] = floor
            mt["skin_floor"] = result["skin"]
            plan["mass_tag"] = mt
    if public_url:
        plan["gate_od_skins"]["larp_gap_pack"] = f"{public_url.rstrip('/')}/.well-known/larp-gap-pack.json"
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Gate-C / Gate-D / Gate-O — same mouth, civil · defensive · offensive commit surfaces.",
        "skins": {
            SKIN_CIVIL: skin_profile(SKIN_CIVIL),
            SKIN_DEFENSIVE: skin_profile(SKIN_DEFENSIVE),
            SKIN_OFFENSIVE: skin_profile(SKIN_OFFENSIVE),
        },
        "demo": f"POST {base}/demo/pas/gate-od-skins",
        "well_known": f"{base}/.well-known/gate-od-skins.json",
        "larp_gap_pack": f"{base}/.well-known/larp-gap-pack.json",
        "bind_room": f"{base}/bind-room",
        "manufactures": [
            "skin_dialect",
            "mass_table",
            "invention_stack_lean",
            "larp_gap_map",
        ],
        "pairs_with": "Throat · Desk Quorum Fob · Bind Path Compiler · Restraint Invoice · Panic Latch · Charge Bride",
        "north_star": "gate/NORTH_STAR.md#inventions-forge-catalog",
        "posture": POSTURE,
    }
