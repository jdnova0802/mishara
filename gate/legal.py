"""Ads-ready legal stubs — privacy + terms. Not counsel-signed opinions.

Honest floor so /operator can take paid traffic without claiming production
or hiding what we collect. Replace stubs with counsel copy before scale ads.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-legal-stubs-v1"
UPDATED = "2026-03-21"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


PRIVACY = {
    "title": "Privacy",
    "status": "stub",
    "not_counsel": True,
    "summary": (
        "Gate is a clearance mouth. We collect the minimum needed to run "
        "checkout, weld delivery, and fail-closed evidence — not a consumer dossier."
    ),
    "collects": [
        "Work email and checkout metadata when you pay a weld or management leg",
        "fuse_id / job_id / write-path identifiers you send on hops (no PII on the hop)",
        "Server logs (IP, user-agent, path, time) for abuse and uptime",
        "Optional ad/analytics pixels only when GATE_META_PIXEL_ID or GATE_GA_ID is set",
    ],
    "does_not": [
        "Sell personal data",
        "Require PII on the clearance hop",
        "Claim stranger-facing production weld status from marketing alone",
    ],
    "retention": "Checkout and weld records retained for billing, audit, and DENY evidence. Contact to request deletion of account-scoped PII where law requires.",
    "contact_path": "email",
}

TERMS = {
    "title": "Terms",
    "status": "stub",
    "not_counsel": True,
    "summary": (
        "Paying a weld buys a fail-closed mouth on one irreversible write plus the "
        "management leg. It does not buy Tier-S ownership, nuclear/C2 authority, "
        "or a claim that their_production is true before a real third-party weld."
    ),
    "rules": [
        "One married write per weld (withdraw/payout or bind-only unless contracted otherwise)",
        "Licensed operators only — unlicensed gambling voids the path",
        "Weld fee non-refundable once delivery window starts; management monthly until cancelled",
        "DENY under uncertainty is the product — soft-yes is breach of the mouth",
        "their_production stays false until a recorded third-party production weld (L4)",
        "Dogfood and first-party drills are not customer production",
        "Not legal advice; counsel reviews before enterprise embed",
    ],
}


def ads_floor(*, meta_pixel_id: str = "", ga_id: str = "") -> dict[str, Any]:
    """What must be true before paid ads land on /operator."""
    meta = (meta_pixel_id or "").strip()
    ga = (ga_id or "").strip()
    return {
        "land": "/operator",
        "required": [
            "privacy stub live",
            "terms stub live",
            "operator page states their_production false until L4",
            "no Tier-S ownership cosplay in creative",
        ],
        "pixels": {
            "meta_pixel_id_set": bool(meta),
            "ga_id_set": bool(ga),
            "default_off": True,
            "note": "Pixels stay off unless GATE_META_PIXEL_ID / GATE_GA_ID are set.",
        },
        "claims_forbidden": [
            "their_production true without third-party weld record",
            "own nuclear / C2 / grid monopoly",
            "payment rail / move the money",
        ],
    }


def manifest(
    public_url: str,
    contact_email: str,
    *,
    meta_pixel_id: str = "",
    ga_id: str = "",
) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "updated": UPDATED,
        "evaluated_at": _now(),
        "operator": "Nisaba LLC",
        "contact": contact_email,
        "not_legal_advice": True,
        "privacy": {**PRIVACY, "url": f"{base}/privacy"},
        "terms": {**TERMS, "url": f"{base}/terms"},
        "ads_floor": ads_floor(meta_pixel_id=meta_pixel_id, ga_id=ga_id),
        "links": {
            "privacy": f"{base}/privacy",
            "terms": f"{base}/terms",
            "operator": f"{base}/operator",
            "science": f"{base}/science",
            "json": f"{base}/.well-known/legal.json",
        },
        "gatekeep": "Stub floor for ads. Counsel before scale. Mouth only.",
    }
