"""Gate Anatomy — faceless body of may; protective Eyes/Hands only.

See GATE_ANATOMY.md. Not MGA outbound. Never Lockheed.
"""

from __future__ import annotations

from typing import Any

THESIS = (
    "Gate is a faceless body of may — Mouth decides; Eyes and Hands exist only "
    "to protect clearance integrity; never warlord can, never sight empire, "
    "never a face above the mouth."
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
        "job": "Protective sense — authenticity / presence / bypass detection",
        "may_inform": ["mouth", "ear", "immune", "tooth"],
        "never": [
            "battlefield fusion product",
            "mass surveillance SKU",
            "Eye output equals LIVE",
            "Eye authorizes offensive can",
        ],
        "formal": "Eye output never equals LIVE. Eye used to authorize offensive can ⇒ Filter.",
    },
    "hand": {
        "job": "Protective act — enforce DENY / amputate forged path",
        "requires": "Mouth DENY or CHOKE first",
        "never": [
            "missiles / guns / platforms / OEM muscle",
            "Lockheed path",
            "offensive force projection",
            "Hand moves without Mouth",
        ],
        "formal": "Hand never moves without Mouth. Hand as offensive L0 product ⇒ Filter.",
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
            "Hands/Eyes are protection-only under Mouth + Lattice + coordinators. "
            "Offensive can or sight-empire product = Filter."
        ),
        "spec": "gate/GATE_ANATOMY.md",
        "outbound_lock": (
            "Lead with AI governance + commit control. "
            "Do not lead with Hands, Eyes, anatomy, or Lockheed contrast."
        ),
        "well_known": f"{base}/.well-known/gate-anatomy.json" if base else None,
    }
