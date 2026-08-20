"""Public face — three pillars. Everything else is moat.

Door + CHARGE + distribution stack. The hull is monolith-shaped;
the catalog (105 specs) lives behind inventions.json + moat fingerprint.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-public-face-v1"
INVENTOR = "Nisaba LLC / Gate"

PILLARS = (
    {
        "id": "door",
        "name": "Exclusive door",
        "tagline": "One irreversible write per weld. Fail closed on DEAD.",
        "manifest": "monolith.json",
        "routes": ("operator", "register", "only"),
        "not": "Dashboard fauna. bind-and-issue. Soft-yes inbox.",
    },
    {
        "id": "charge",
        "name": "CHARGE port",
        "tagline": "DEAD→LIVE only via unforgeable CHARGE — never admin toggle.",
        "manifest": "costliness.json",
        "routes": ("ocsp", "license_fuse"),
        "not": "UW approve without CHARGE. Dashboard LIVE flip.",
    },
    {
        "id": "distribution",
        "name": "Distribution stack",
        "tagline": "Clear the instruction before it becomes their exception queue.",
        "manifest": "distribution.json",
        "routes": ("settlement", "post_trade_distribution"),
        "not": "Replace DTCC. Per-seat SaaS. CCP cosplay.",
    },
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _link(base: str, path: str) -> str:
    return f"{base.rstrip('/')}/.well-known/{path}"


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    pillars = []
    for p in PILLARS:
        pillars.append(
            {
                **p,
                "href": _link(base, p["manifest"]) if base else None,
            }
        )
    return {
        "spec": SPEC,
        "name": "Gate public face",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "thesis": (
            "Two ports on the monolith — exclusive door + CHARGE — plus the "
            "post-trade stack that propagates register tiers down from FMI apex. "
            "The other 102 inventions are moat, not homepage."
        ),
        "pillars": pillars,
        "catalog": {
            "inventions": _link(base, "inventions.json") if base else None,
            "moat": _link(base, "moat.json") if base else None,
            "production_skin": _link(base, "production-skin.json") if base else None,
            "scorecard": _link(base, "scorecard.json") if base else None,
            "claim": "Partial clones fail fingerprint. Full clone still lacks weld skin.",
        },
        "depth": {
            "positioning": _link(base, "positioning.json") if base else None,
            "mouth_constitution": _link(base, "mouth-constitution.json") if base else None,
        },
        "their_production": _their_production(),
    }


def _their_production() -> bool:
    try:
        from gate import production_skin as skin_mod
    except ImportError:
        import production_skin as skin_mod  # type: ignore[no-redef]
    return skin_mod.their_production()


def catalog_discovery(public_url: str) -> dict[str, str]:
    """Full invention index URLs — nested under catalog.discovery, not top-level gate.json."""
    try:
        from gate import inventions as inventions_mod
    except ImportError:
        import inventions as inventions_mod  # type: ignore[no-redef]

    base = (public_url or "").rstrip("/")
    out: dict[str, str] = {}
    for entry in inventions_mod.CATALOG:
        inv_id, _name, _spec, _liner, filename = entry
        out[inv_id] = f"{base}/.well-known/{filename}"
    return out


def gate_catalog_block(public_url: str) -> dict[str, Any]:
    """Catalog section for gate.json — moat behind fingerprint."""
    try:
        from gate import inventions as inventions_mod
        from gate import moat as moat_mod
    except ImportError:
        import inventions as inventions_mod  # type: ignore[no-redef]
        import moat as moat_mod  # type: ignore[no-redef]

    base = (public_url or "").rstrip("/")
    fp = moat_mod.fingerprint(base)
    inv = inventions_mod.manifest(base)
    return {
        "inventions": inv["live"],
        "moat": f"{base}/.well-known/moat.json",
        "count": inv["count"],
        "fingerprint_short": fp["fingerprint_short"],
        "discovery": catalog_discovery(base),
        "note": "105 specs welded. Public face is door + CHARGE + distribution only.",
        "production_skin": f"{base}/.well-known/production-skin.json",
        "scorecard": f"{base}/.well-known/scorecard.json",
        "runbook": f"{base}/.well-known/runbook.json",
        "proof_suite": f"{base}/.well-known/proof-suite.json",
    }


def gate_public_face_block(public_url: str) -> dict[str, Any]:
    """Top-of-gate.json public face — three pillars."""
    base = (public_url or "").rstrip("/")
    m = manifest(base)
    return {
        "manifest": f"{base}/.well-known/public-face.json",
        "door": m["pillars"][0]["href"],
        "charge": m["pillars"][1]["href"],
        "distribution": m["pillars"][2]["href"],
        "thesis": m["thesis"],
    }


def page_cards() -> list[dict]:
    """Three cards — the only invention-facing surface on HTML."""
    return [
        {
            "tag": "Face",
            "title": "Exclusive door",
            "body": (
                "One welded write. bind-only or payout — not a settings panel. "
                "Parent DEAD, children cannot spend. Stranger verify without login."
            ),
            "ref": "Monolith · door",
            "href_key": "door",
        },
        {
            "tag": "Face",
            "title": "CHARGE port",
            "body": (
                "Regime change only via costly CHARGE. UW soft-yes does not resurrect. "
                "Unforgeable costliness — the only DEAD→LIVE path on the engine."
            ),
            "ref": "Costliness · CHARGE",
            "href_key": "charge",
        },
        {
            "tag": "Face",
            "title": "Distribution stack",
            "body": (
                "DTCC peers cite PFMI manifests. We filter gross before the net. "
                "Register tiers down the stack — doctrine at apex, bps at operator."
            ),
            "ref": "Post-trade · register tiers",
            "href_key": "distribution",
        },
    ]
