"""Adversarial Weld — Gate as a minimax default against the worst licensed actor.

Not "trust the operator." Not "trust the integrator." The mouth is sized
for the adversary who has a license, a production key, and an incentive
to skip clear-before-wire. Every fail-closed path is a move against that
player. Copycats who ship happy-path demos lose the game before kickoff.

Gatekeep only to ourselves: adversarial robustness → minimax mouth.
"""

from __future__ import annotations

from typing import Any

SPEC = "gate-adversarial-v1"
INVENTOR = "Nisaba LLC / Gate"


def public_document() -> dict[str, Any]:
    return {
        "spec": SPEC,
        "inventor": INVENTOR,
        "gatekeep": True,
        "title": "Adversarial Weld",
        "thesis": (
            "The mouth is sized for the worst licensed actor who wants to "
            "skip clear-before-wire — not for the happy-path demo partner."
        ),
        "adversary_model": {
            "has": ["license", "production credentials", "incentive to skip clear"],
            "cannot": [
                "forge CHARGE without costliness",
                "skip DEAD→LIVE without signed CHARGE",
                "move PII onto PAS",
            ],
        },
        "minimax": [
            "Assume skip-clear intent on every irreversible path",
            "Prefer HALT over silent success when evidence is thin",
            "Never ship a demo path that becomes production by default",
        ],
        "not": [
            "Red-team theater for marketing",
            "Permission to attack third-party systems",
        ],
        "relation": {
            "costliness": "Unforgeable cost of CHARGE raises adversary expense",
            "skin": "Skin in the weld aligns licensed operator with restraint",
            "moat": "Adversarial sizing is part of the uncopyable fingerprint",
        },
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    body = public_document()
    body["name"] = body.get("title") or "Adversarial Weld"
    body["live"] = f"{base}/.well-known/adversarial.json"
    body["their_production"] = False
    return body
