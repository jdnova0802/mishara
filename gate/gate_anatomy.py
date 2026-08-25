"""Gate Anatomy — faceless body of may; P1/P2/P3 protection Eyes/Hands.

See GATE_ANATOMY.md. Ideation ≠ canon. Not MGA outbound. Never Lockheed.
"""

from __future__ import annotations

from typing import Any

THESIS = (
    "Gate is a faceless body of may — Mouth decides; P1 Facility / P2 Channel / "
    "P3 Lattice Eyes and Hands are real protection for the rail; never warlord "
    "offense OEM; never a face above the mouth."
)

ORGANS_CORE: tuple[str, ...] = (
    "mouth",
    "sheath",
    "bone",
    "tooth",
    "stone",
    "blood",
    "gut",
    "heart",
    "cord",
    "ear",
    "marrow",
    "immune",
    "liver",
    "womb",
    "lattice",
    "breath",
)

ORGANS_PROTECTION: tuple[str, ...] = ("eye", "hand")
ORGANS_FORBIDDEN: tuple[str, ...] = ("face",)

PROTECTION_LAYERS = {
    "P1": {
        "name": "Facility Protect",
        "enter": "now",
        "eye": "tamper / CCTV / door / RF / seals on mouth facilities",
        "hand": "locks / kill-power / seals / door hard-DENY / cut forged paths",
    },
    "P2": {
        "name": "Channel Protect",
        "enter": "with paid weld",
        "eye": "deepfake / liveness / sheath IDS / Bone peel alarms",
        "hand": "sheath tripwires / Access Tomb / agent amputation / quarantine",
    },
    "P3": {
        "name": "Lattice Protect",
        "enter": "mountain — after Settlement Dependency",
        "eye": "lattice integrity / ark vault / planetary-bus authenticity Eyes",
        "hand": "lattice amputation / ark deadman / planetary-bus inhibit Hands",
    },
}

PROTECTION_DEAL = {
    "eye": {
        "job": "See threats to Gate organs + sacred channels",
        "layers": PROTECTION_LAYERS,
        "may_inform": ["mouth", "ear", "immune", "hand"],
        "formal": (
            "Eye output never equals LIVE. P1/P2/P3 Eye hardware allowed for "
            "Gate protection. Eye used to authorize offensive can ⇒ Filter."
        ),
    },
    "hand": {
        "job": "Stop ruin of Gate + enforce DENY",
        "layers": PROTECTION_LAYERS,
        "requires": "Mouth DENY/CHOKE or pre-scoped Emergency May Charter",
        "formal": (
            "Hand never moves without Mouth. P1/P2/P3 Hand hardware allowed to "
            "defend Gate and enforce DENY. Offensive L0 product line ⇒ Filter."
        ),
    },
}

PROTECTION_FLOW = (
    "attack / forge / peel Gate",
    "Eye (P1→P3 as scoped)",
    "Ear challenge if channel spoof",
    "Mouth LIVE/DENY/CHOKE",
    "Hand enforces (P1→P3 as scoped)",
    "Stone proves",
    "Immune/Liver clean capture",
)

FORBIDDEN_FLOW = ("Eye sees geopolitical foe", "Hand launches offensive can")


def gate_anatomy_manifest(public_url: str | None = None) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "doctrine": "gate_anatomy",
        "version": "1.1.0",
        "thesis": THESIS,
        "ideation_rule": (
            "Raw riffs are brainstorm fuel; canon uses formal P1/P2/P3 names."
        ),
        "no_face": True,
        "organs_core": list(ORGANS_CORE),
        "organs_protection": list(ORGANS_PROTECTION),
        "organs_forbidden": list(ORGANS_FORBIDDEN),
        "protection_layers": PROTECTION_LAYERS,
        "protection_deal": PROTECTION_DEAL,
        "protection_flow": list(PROTECTION_FLOW),
        "forbidden_flow": list(FORBIDDEN_FLOW),
        "lockheed_rule": (
            "P1/P2/P3 Eyes+Hands ARE allowed to protect Gate and enforce DENY. "
            "Offensive weapons product line / conquest can = Filter. "
            "Protection ≠ disabled feature."
        ),
        "spec": "gate/GATE_ANATOMY.md",
        "outbound_lock": (
            "Lead with AI governance + commit control. "
            "Do not lead with Hands, Eyes, anatomy, or Lockheed contrast."
        ),
        "well_known": f"{base}/.well-known/gate-anatomy.json" if base else None,
    }
