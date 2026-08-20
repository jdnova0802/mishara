"""Cultural positioning — borrowed lenses, operational meaning.

Not museum text. Each reference maps to something Gate actually ships:
feedback loops, maintenance registers, intergenerational obligation,
post-automation possibility, non-SaaS form, public confidence without naivety.
"""
from __future__ import annotations

SPEC = "gate-positioning-v1"

# ---------------------------------------------------------------------------
# GTM / focus (plain operational translation)
# ---------------------------------------------------------------------------
FOCUS_PLAIN = (
    "Three faces on the hull: exclusive door, CHARGE port, distribution stack. "
    "Fail-closed on irreversible spend. DEAD→LIVE only via unforgeable CHARGE. "
    "Post-trade propagation matches the register — doctrine at apex, bps at operator. "
    "Everything else is moat."
)

FOCUS_FOR = [
    "Operators (weld the production door and start management)",
    "Carriers & implementors (wire one scanner + one protocol face)",
    "Auditors & risk (verify LIVE/DEAD decisions + evidence proofs)",
    "Engineers (see shipped invariants: spend protocol, receipts, settlement windows)",
]

NEXT_STEPS = [
    {"label": "Weld + management", "endpoint": "operator_page", "style": "btn-primary"},
    {"label": "Read the register fees", "endpoint": "register_page", "style": "btn-ghost"},
    {"label": "Implement the scanner", "endpoint": "scanner_page", "style": "btn-ghost"},
    {"label": "Machine-readable positioning.json", "endpoint": "well_known_positioning", "style": "btn-ghost"},
]

# ---------------------------------------------------------------------------
# Ops / design philosophy (how we run and build)
# ---------------------------------------------------------------------------

CYBERNETICS = {
    "borrowed_from": "Project Cybersyn (Chile, 1971) — Stafford Beer cybernetic management",
    "gate_meaning": "Ops room at scale: manifests publish state; humans stay in the loop on irreversible spend.",
    "shipped_as": [
        "Public feedback surfaces — kappa, settlement windows, restraint inventory, evidence-head",
        "CHARGE-only resurrection — permission collapse is never fully automated",
        "Operator weld checkout — human commits before production mouth goes LIVE",
        "κ (restraint) and τ (tension) — measurable loops, not dashboard theater",
    ],
    "not": "Retro futurism cosplay. No fake ops room UI. The manifests ARE the room.",
}

MAINTENANCE_FUTURISM = {
    "borrowed_from": "Maintenance futurism — credibility over launch-day theater",
    "gate_meaning": "Future worth inheriting is maintained, not announced.",
    "shipped_as": [
        "their_production: false until a real weld — honest scope flags",
        "Stranger verify + Merkle evidence — proof that survives the launch party",
        "Idempotent checkout — ops immovability, not demo churn",
        "Settlement finality hashes — boring tamper-evident closure",
    ],
    "not": "Hype cycles, vapor manifests, or features that exist only in slide decks.",
}

COSMISM_COMMON_TASK = {
    "borrowed_from": "Russian cosmism — Fedorov's Common Task; intergenerational obligation",
    "gate_meaning": "Design for mouths the next generation cannot bypass or outlive casually.",
    "shipped_as": [
        "License parent — children cannot outlive parent DEAD",
        "Inhabitant + afterward receipts — including later, not just the hop",
        "Counterfactual spend proofs — what did not happen is also inherited evidence",
        "Civilization default register — asset is the mouth, not a quarterly seat count",
    ],
    "not": "Transhumanism pitch. Obligation as engineering constraint: fail-closed, one write, licensed only.",
}

# ---------------------------------------------------------------------------
# Narrative / brand / cultural positioning
# ---------------------------------------------------------------------------

SITUATIONIST_NEW_BABYLON = {
    "borrowed_from": "Constant Nieuwenhuys — New Babylon; life after necessary labor is handled",
    "gate_meaning": "When irreversible spend is gated reliably, builders stop guarding the bind path.",
    "shipped_as": [
        "One door on the write — anxiety moves from every engineer to one mouth",
        "Permission mortality fuse — agents and carriers inherit clear LIVE/DEAD/ARMED",
        "What becomes possible: less bind-path paranoia, more actual product on licensed rails",
    ],
    "not": "Utopia marketing. The mouth is strict. Possibility is conditional on restraint holding.",
}

ANTHROPOPHAGY = {
    "borrowed_from": "Oswald de Andrade — anthropophagy; digest foreign forms, excrete something native",
    "gate_meaning": "Eat DTCC, SWIFT, Visa, CLS — do not photocopy US SaaS.",
    "shipped_as": [
        "GP register (2-and-20 shape) on infrastructure, not seat tiers",
        "Netting + settlement windows + default waterfall — digested, not cloned Stripe Billing",
        "Public .well-known manifests — protocol face, not product-led growth chrome",
        "Nisaba voice — refusal SKU, stranger mass, inhabitant — not another purple gradient dashboard",
    ],
    "not": "Nationalist branding. Hybrid appetite: global rails, non-clone form.",
}

ATOM_AGE_CIVIC_OPTIMISM = {
    "borrowed_from": "Atom-age civic optimism — visible public confidence without naivety",
    "gate_meaning": "Point at the infrastructure like a dam. Verify it like a receipt.",
    "shipped_as": [
        "Stranger verify URLs — anyone can confirm DEAD/LIVE without login",
        "Published nos inventory — public restraint, not hidden deny lists",
        "Evidence packets + inclusion proofs — confidence you can audit",
        "Licensed-only, fail-closed — optimism with teeth",
    ],
    "not": "Blind trust or 'move fast break things.' Public confidence earned by proof.",
}


def manifest(public_url: str) -> dict:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Gate positioning",
        "headline": "Infrastructure mouth — borrowed lenses, operational meaning.",
        "focus_plain": FOCUS_PLAIN,
        "focus_for": FOCUS_FOR,
        "next_steps": NEXT_STEPS,
        "deploy_note": "Manifests are live surfaces. Positioning is how we explain why they exist.",
        "ops_philosophy": {
            "cybernetics_cybersyn": CYBERNETICS,
            "maintenance_futurism": MAINTENANCE_FUTURISM,
            "cosmism_common_task": COSMISM_COMMON_TASK,
        },
        "narrative_brand": {
            "situationist_new_babylon": SITUATIONIST_NEW_BABYLON,
            "anthropophagy": ANTHROPOPHAGY,
            "atom_age_civic_optimism": ATOM_AGE_CIVIC_OPTIMISM,
        },
        "one_line": (
            "Cybernetic ops room without the theater; maintenance over hype; "
            "intergenerational mouth; possibility after the bind is gated; "
            "digest incumbents don't clone SaaS; public verify without naivety."
        ),
        "public_face": {
            "manifest": f"{base}/.well-known/public-face.json",
            "door": f"{base}/.well-known/monolith.json",
            "charge": f"{base}/.well-known/costliness.json",
            "distribution": f"{base}/.well-known/distribution.json",
        },
        "catalog": {
            "inventions": f"{base}/.well-known/inventions.json",
            "moat": f"{base}/.well-known/moat.json",
        },
        "links": {
            "register": f"{base}/.well-known/register.json",
            "verify_engine": "https://velaru.xyz/verify",
        },
        "page": f"{base}/positioning",
        "their_production": False,
    }


def page_cards() -> list[dict]:
    """Three pillars — door, CHARGE, distribution. Depth lives in catalog + moat."""
    try:
        from gate import public_face as public_face_mod
    except ImportError:
        import public_face as public_face_mod  # type: ignore[no-redef]
    return public_face_mod.page_cards()
