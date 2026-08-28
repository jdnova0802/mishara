"""Living Continuity inventions — machine manifest.

See CONTINUITY_LIVE.md. Grounded in real COG/NC3/key-loss/deepfake/agent gaps.
Not MGA outbound.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ContinuityInvention:
    id: str
    title: str
    real_gap: str
    one_line: str
    formal_rule: str
    priority: int
    sku_costume: tuple[str, ...]


INVENTIONS: tuple[ContinuityInvention, ...] = (
    ContinuityInvention(
        id="obey_bit",
        title="Obey Bit",
        real_gap="9/11 COG — successors refused or never reached protocol",
        one_line="Continuity seat refusal is a funeral event, not a private choice.",
        formal_rule="Named successor who can refuse without funeral ⇒ paper continuity.",
        priority=4,
        sku_costume=("continuity exercise attestation", "succession compliance bond"),
    ),
    ContinuityInvention(
        id="dual_state",
        title="Dual-State Continuity",
        real_gap="Perimeter/Dead Hand — retaliation without legitimate may",
        one_line="Dead Hand may only inhibit/hold/prove — never new sacred LIVE.",
        formal_rule="Dead Hand that can LIVE ⇒ forged civilization.",
        priority=6,
        sku_costume=("incapacity action envelope", "fail-closed succession mode"),
    ),
    ContinuityInvention(
        id="presence_proof",
        title="Presence Proof",
        real_gap="NC3 decapitation / silence treated as soft authority",
        one_line="Heartbeat that principal is alive and competent; silence ≠ LIVE.",
        formal_rule="No Presence Proof ⇒ ghost may or panic LIVE.",
        priority=5,
        sku_costume=("authority liveness attestation", "clearance heartbeat"),
    ),
    ContinuityInvention(
        id="voice_is_not_may",
        title="Voice is Not May",
        real_gap="Deepfake / voice-clone false orders on defense & exec paths",
        one_line="High-μ orders cannot clear on voice or face likeness alone.",
        formal_rule="If a clone can LIVE you, you never had may.",
        priority=1,
        sku_costume=("order authentication policy", "anti-impersonation commit path"),
    ),
    ContinuityInvention(
        id="access_tomb",
        title="Access Tomb",
        real_gap="Crypto/key estates — legal title without technical access",
        one_line="Dual-key legal succession + technical access; death cert alone never moves sacred writes.",
        formal_rule="Title without Access Tomb ⇒ authority that evaporates.",
        priority=2,
        sku_costume=("dual-control digital succession", "key-continuity vault"),
    ),
    ContinuityInvention(
        id="tacit_capture",
        title="Tacit Capture",
        real_gap="Government institutional memory walks out at retirement",
        one_line="Forced extraction of exception-path knowledge before seat funeral.",
        formal_rule="Funeral without Tacit Capture ⇒ zombie org with amnesia.",
        priority=7,
        sku_costume=("institutional memory escrow", "operator tacit pack"),
    ),
    ContinuityInvention(
        id="agent_succession_receipt",
        title="Agent Succession Receipt",
        real_gap="AI agents inherit tool authority; accountability dissolves",
        one_line="Portable prove that mandate moved; orphan agents get amputated.",
        formal_rule="Agent without Succession Receipt ⇒ ghost may at machine speed.",
        priority=3,
        sku_costume=("agent authority succession", "mandate chain attestation"),
    ),
    ContinuityInvention(
        id="continuity_clock",
        title="Continuity Condition Clock",
        real_gap="COG/COOP shelfware between crises",
        one_line="Unexercised continuity goes legally stale for sacred class.",
        formal_rule="Unexercised Continuity ⇒ forged Continuity.",
        priority=8,
        sku_costume=("continuity readiness rating", "succession drill compliance"),
    ),
    ContinuityInvention(
        id="rival_root",
        title="Rival-Root Continuity",
        real_gap="Split claimants after catastrophe / epistemic war",
        one_line="Pre-committed rule for two living claimants — no first-to-mic.",
        formal_rule="Two claimants + no Rival-Root ⇒ civil war of may.",
        priority=9,
        sku_costume=("competing succession protocol", "authority contest clearance"),
    ),
    ContinuityInvention(
        id="emergency_may_charter",
        title="Emergency May Charter",
        real_gap="Post-COVID emergency powers gutted; mid-crisis authority contests",
        one_line="Pre-scoped LIVE envelope with automatic Funeral/sunset — no boss soft-extend.",
        formal_rule="Emergency power without Emergency May Charter ⇒ improvised throne.",
        priority=10,
        sku_costume=("emergency commit charter", "time-boxed crisis clearance"),
    ),
    ContinuityInvention(
        id="seed_vault_live",
        title="Seed Vault LIVE + Funeral",
        real_gap="Genebanks die in war; Svalbard stores seed, not who-may-open",
        one_line="Sacred LIVE on open/move/destroy germplasm; Funeral when vault authority dies.",
        formal_rule="Seed move without Seed Vault LIVE ⇒ theft of the future dressed as rescue.",
        priority=11,
        sku_costume=("germplasm release clearance", "seed-vault commit control"),
    ),
    ContinuityInvention(
        id="bootstrap_may",
        title="Bootstrap May",
        real_gap="Recovery libraries teach how to rebuild — not who may restart irreversibles",
        one_line="Continuity-grade LIVE on industrial restart commits after collapse.",
        formal_rule="Bootstrap without Bootstrap May ⇒ can without may at civilizational scale.",
        priority=12,
        sku_costume=("industrial restart clearance", "rebuild commit control"),
    ),
    ContinuityInvention(
        id="deflection_may_bus",
        title="Deflection May Bus",
        real_gap="Planetary defense has detection + advice — no binding may",
        one_line="Fail-closed LIVE/DENY for divert/disrupt deflection under Consent Lattice.",
        formal_rule="Deflection without Deflection May Bus ⇒ unilateral planetary write.",
        priority=13,
        sku_costume=("planetary mitigation clearance", "deflection commit control"),
    ),
    ContinuityInvention(
        id="war_grade_order_auth",
        title="War-Grade Order Auth",
        real_gap="NC3 human-in-loop is policy; deepfakes hit command authenticity",
        one_line="Biscuit-class auth for sacred channels — likeness never sufficient.",
        formal_rule="Sacred LIVE on likeness ⇒ forged war.",
        priority=1,
        sku_costume=("high-assurance order authentication", "anti-impersonation command path"),
    ),
    ContinuityInvention(
        id="substrate_migration",
        title="Substrate Migration Continuity",
        real_gap="Org merge, region death, model swap, future substrate change",
        one_line="Substrate change clears the same bar as death — no soft vibes handoff.",
        formal_rule="Substrate change without Continuity rite ⇒ possession, not succession.",
        priority=14,
        sku_costume=("identity migration clearance", "principal substrate handoff"),
    ),
)

THESIS = (
    "Living Continuity = may that survives death, silence, deepfake, key-loss, "
    "agent swap, substrate change, emergency capture, seed rites, industrial restart, "
    "and planetary deflection — with strangers auditing the handoff and funeraling "
    "the seat that refused."
)

EVAC_STILL_ABOVE = (
    "ECLSS / life-support leads",
    "Power / reactor ops that keep the can alive",
    "Trauma / ICU / infection / pharmacy core",
    "Closed-loop food / water / waste leads",
    "Leak / EVA / damage-control that prevents hull loss",
)

EVAC_CEILING_NOTE = (
    "Full pack welded ⇒ ~#12–#25 on a serious first-wave core — highest mouth, never above oxygen."
)


def continuity_live_manifest(public_url: str | None = None) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    ordered = sorted(INVENTIONS, key=lambda i: i.priority)
    return {
        "doctrine": "continuity_live",
        "version": "1.0.0",
        "thesis": THESIS,
        "invention_count": len(INVENTIONS),
        "build_first": [i.id for i in ordered[:3]],
        "inventions": [
            {
                "id": i.id,
                "title": i.title,
                "real_gap": i.real_gap,
                "one_line": i.one_line,
                "formal_rule": i.formal_rule,
                "priority": i.priority,
                "sku_costume": list(i.sku_costume),
            }
            for i in ordered
        ],
        "spec": "gate/CONTINUITY_LIVE.md",
        "evac_still_above": list(EVAC_STILL_ABOVE),
        "evac_ceiling_note": EVAC_CEILING_NOTE,
        "outbound_lock": (
            "Lead with AI governance + commit control + operator continuity. "
            "Do not lead with Dead Hand / Obey Bit / Substrate Migration / "
            "Deflection May / Seed Vault LIVE."
        ),
        "well_known": f"{base}/.well-known/continuity-live.json" if base else None,
    }
