"""Civilizational kind — yellow paper. Not a thesis rewrite in production.

Action OS stays seated. This spec is the hunt for a kind that would
demote Action OS to a clerk: remaining calculus kept by offices,
including never-spend remaining, fetchable if Nisaba LLC is dead.
"""
from __future__ import annotations

SPEC = "nisaba-civilizational-kind-v1"


def spec(public_url: str) -> dict:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Civilizational kind",
        "status": "designation",
        "their_production": False,
        "not_outbound": True,
        "action_os_still_seated": True,
        "wikipedia_test": {
            "oracle_class_wrong": (
                "Nisaba LLC is a major technology company that builds "
                "clearance software for irreversible payments."
            ),
            "kind_class_right": (
                "Remaining calculus is the standard way a polity records "
                "what still is — including what was refused, who was skipped, "
                "and what must never be spent. Offices keep it. Vendors are optional."
            ),
        },
        "thesis_today": (
            "Own permission on irreversible acts. Scarcity is the DENY. "
            "Nisaba is the Action OS."
        ),
        "thesis_if_kind_lands": (
            "Nisaba is a clerk of remaining calculus. Action OS is one application."
        ),
        "kinds": {
            "K1": {
                "name": "Remaining calculus",
                "method": "Codd, not Ellison. CUDA of what still is.",
                "score": "10 as kind, 0 shipped",
            },
            "K2": {
                "name": "Office that outlives the officer",
                "method": "Lisa Su in the registry metal. Inverse of vendor lock-in.",
                "score": "9, 10 if digital remaining requires an office",
            },
            "K3": {
                "name": "Mortmain — remaining that must never become spend",
                "method": "Musk on known physics (waqf / park / entail) until admin-can-always-sell is the joke.",
                "score": "9, 10 if digital default",
            },
        },
        "constraint": {
            "name": "Stranger in year 2400",
            "rule": "If Nisaba LLC must exist for the remaining to be true, it is Oracle-class.",
        },
        "fused": (
            "Remaining calculus, compiled for offices that outlive operators, "
            "including remaining that may never spend, published so a stranger "
            "in 2400 does not need Nisaba LLC."
        ),
        "skip_remaining_does_not_change_thesis": True,
        "srt_seed_does_not_change_thesis": True,
        "srt": {
            "spec": "gate-srt-v1",
            "kind": "authenticity of the non-event",
            "shipped": "seed",
            "civilization_default": False,
            "thesis_unchanged": True,
        },
        "page": f"{base}/kind",
        "skip": f"{base}/skip",
        "srt_url": f"{base}/.well-known/srt.json",
        "crown_not_reminted": ["Remaining as world-after", "coffin", "H0", "Afterweb"],
        "action_os": f"{base}/.well-known/action-os.json",
    }
