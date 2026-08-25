"""Gate Anatomy — faceless body of may; protective Eyes/Hands only.

See GATE_ANATOMY.md. Not MGA outbound. Never Lockheed.
"""

from __future__ import annotations

from typing import Any

THESIS = (
    "Gate is a faceless body of may — Mouth decides; Eyes and Hands are real "
    "classical/advanced/cosmic protection hardware for the rail; never warlord "
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

PROTECTION_DEAL = {
    "eye": {
        "job": "Real protective sense — see threats to Gate organs + sacred channels",
        "tiers": {
            "classical": "tamper / CCTV / door / RF / seals on mouth facilities",
            "advanced": "deepfake / liveness / intrusion / Bone peel alarms",
            "cosmic": "lattice integrity / ark vault / planetary-bus authenticity Eyes",
        },
        "may_inform": ["mouth", "ear", "immune", "hand"],
        "never": [
            "battlefield ISR product",
            "civilian panopticon SKU",
            "Eye output equals LIVE",
            "Eye soft-authorizes offensive can",
        ],
        "formal": (
            "Eye output never equals LIVE. Classical/advanced/cosmic Eye hardware "
            "allowed for Gate protection. Eye used to authorize offensive can ⇒ Filter."
        ),
    },
    "hand": {
        "job": "Real protective act — stop ruin of Gate + enforce DENY",
        "tiers": {
            "classical": "locks / kill-power / seals / door hard-DENY / cut forged paths",
            "advanced": "sheath tripwires / key tomb / agent amputation / quarantine",
            "cosmic": "lattice amputation / ark deadman / planetary-bus inhibit Hands",
        },
        "requires": "Mouth DENY/CHOKE or pre-scoped Emergency May Charter",
        "never": [
            "offensive weapons product line / Lockheed path",
            "conquest / force projection unrelated to protecting may",
            "Hand moves without Mouth",
        ],
        "formal": (
            "Hand never moves without Mouth. Classical/advanced/cosmic Hand hardware "
            "allowed to defend Gate and enforce DENY. Offensive L0 product line ⇒ Filter."
        ),
    },
}

PROTECTION_FLOW = (
    "threat to may integrity",
    "Eye senses",
    "Ear challenges",
    "Mouth LIVE/DENY/CHOKE",
    "if DENY/CHOKE: Hand enforces",
    "Stone proves",
    "Immune/Liver clean capture",
)

FORBIDDEN_FLOW = ("Eye sees enemy", "Hand shoots")


def gate_anatomy_manifest(public_url: str | None = None) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "doctrine": "gate_anatomy",
        "version": "1.0.0",
        "thesis": THESIS,
        "no_face": True,
        "organs_core": list(ORGANS_CORE),
        "organs_protection": list(ORGANS_PROTECTION),
        "organs_forbidden": list(ORGANS_FORBIDDEN),
        "protection_deal": PROTECTION_DEAL,
        "protection_flow": list(PROTECTION_FLOW),
        "forbidden_flow": list(FORBIDDEN_FLOW),
        "lockheed_rule": (
            "Classical/advanced/cosmic Eyes+Hands ARE allowed to protect Gate organs "
            "and enforce DENY. Offensive weapons product line / conquest can = Filter. "
            "Protection ≠ disabled feature."
        ),
        "spec": "gate/GATE_ANATOMY.md",
        "outbound_lock": (
            "Lead with AI governance + commit control. "
            "Do not lead with Hands, Eyes, anatomy, or Lockheed contrast."
        ),
        "well_known": f"{base}/.well-known/gate-anatomy.json" if base else None,
    }
