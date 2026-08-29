"""Public inventor lock — the Satoshi inverse.

Satoshi's social invention was absence: no one to subpoena, no one to
recant, no one to sell the throat. That made bearer cash feel ownerless.

Irreversible permission cannot be ownerless. A mouth without a name is
how soft-yes gets laundered. Identity is load-bearing. The inventor
stands. A stranger can find the name.

Not an email dump. Legal name + entity + patent. No pseudonym.
"""
from __future__ import annotations

from typing import Any

SPEC = "nisaba-inventor-v1"

# Public on purpose. Hiding this is the Satoshi move. We refuse it.
INVENTOR: dict[str, Any] = {
    "name": "Demond Davis",
    "entity": "Nisaba LLC",
    "patent": "64/124,027",
    "anonymous": False,
    "pseudonym": None,
    "satoshi_inverse": True,
    "rule": (
        "Identity is load-bearing. The throat has a name a stranger can find. "
        "We do not hide the inventor so the mouth can be sold later."
    ),
    "never_sell": ("may", "the throat", "critical planetary capacity"),
}


def stamp() -> dict[str, Any]:
    return {
        "spec": SPEC,
        **INVENTOR,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        **stamp(),
        "page": f"{base}/inventions",
        "inventions": f"{base}/.well-known/inventions.json",
        "named_may": f"{base}/.well-known/named-may.json",
        "conformant": f"{base}/.well-known/conformant.json",
        "qic": f"{base}/.well-known/qic.json",
        "their_production": False,
    }
