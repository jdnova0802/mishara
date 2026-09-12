"""Nisaba brand map — honest hosts, not marketing cosplay.

Surface-audit truth for domains vs product rails. Internal / discovery.
Do not invent mid-ladder SKUs. Do not claim parked or third-party domains.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "nisaba-brand-map-v1"
INVENTOR = "Nisaba LLC"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# Host inventory as of the last Gate-side surface pass.
# Update when DNS / Render / product URLs change — keep money out of this file.
BRANDS: list[dict[str, Any]] = [
    {
        "id": "gate",
        "name": "Gate",
        "role": "Action OS mouth",
        "product_urls": [
            "https://gate.velaru.xyz",
            "https://gate-api-vsq8.onrender.com",
        ],
        "canonical": "https://gate.velaru.xyz",
        "status": "live",
        "notes": [
            "Money door: Bind Room $1,750 → operator weld $25k + $5k/mo + 10 bps.",
            "x402 USDC prices stay offline until GATE_X402_PAYTO is set.",
        ],
    },
    {
        "id": "velaru",
        "name": "Velaru",
        "role": "proof rail",
        "product_urls": [
            "https://velaru.xyz",
            "https://velaru.onrender.com",
        ],
        "canonical": "https://velaru.xyz",
        "status": "live",
        "notes": [
            "Pricing page lists HOLD $149 / Monitor $249/mo / volume.",
            "Instant lane still sells $25 / $49 on /instant + llms.txt — align with /pricing in Velaru repo.",
        ],
        "open_forks": [
            {
                "severity": "money",
                "detail": "/instant and llms.txt advertise $25 GAM + $49 receipt; /pricing omits them",
                "fix": "velaru_repo",
            }
        ],
    },
    {
        "id": "erra",
        "name": "Erra",
        "role": "signal rail",
        "product_urls": [
            "https://velaru.xyz/erra",
            "https://erra-jf6a.onrender.com",
            "https://velaru-erra.onrender.com",
        ],
        "canonical": "https://velaru.xyz/erra",
        "status": "live",
        "notes": [
            "Canonical buyer surface is the Velaru twin path /erra — not erra.xyz.",
            "Dedicated Render host erra-jf6a is live; probe /healthz (not /health).",
            "GET /health still 500s on diligence profile — fix in Velaru repo; do not flip probe back.",
            "erra.onrender.com is not a live host — do not advertise it.",
        ],
        "domains": {
            "erra.xyz": {
                "owned_by_nisaba": False,
                "status": "for_sale_spaceship",
                "detail": "Parked for-sale lander — not the product.",
            }
        },
        "open_forks": [
            {
                "severity": "ops",
                "detail": "GET /health (and /erra/health) 500s via build_diligence_profile('nisaba-llc')",
                "fix": "velaru_repo",
            },
            {
                "severity": "discovery",
                "detail": "No /erra/pricing or /erra/llms.txt — SKUs live on sprint/mandate pages only",
                "fix": "velaru_repo",
            },
            {
                "severity": "dns",
                "detail": "erra.xyz for sale on Spaceship — buy/point or stop treating as brand domain",
                "fix": "founder_dns",
            },
        ],
    },
    {
        "id": "verra",
        "name": "Verra",
        "role": "action session (both rails before bind)",
        "product_urls": [
            "https://gate.velaru.xyz/bind-room",
            "https://velaru.xyz/verra",
            "https://gate.velaru.xyz/family/verra",
        ],
        "canonical": "https://gate.velaru.xyz/bind-room",
        "status": "live_as_bind_room",
        "notes": [
            "Verra is the room, not a fourth deploy — velaru.xyz/verra aliases Bind Room.",
            "Gate /family/verra is the voice pack; paste into chrome when Bind Room TOC is replaced.",
            "verra.xyz is NOT Nisaba — third-party games portfolio (GreatVerrazano).",
        ],
        "domains": {
            "verra.xyz": {
                "owned_by_nisaba": False,
                "status": "third_party_unrelated",
                "detail": "Unrelated site — do not link as product.",
            }
        },
        "open_forks": [
            {
                "severity": "voice",
                "detail": "Live /verra still reads as Bind Room officer pack, not Verra hero voice",
                "fix": "velaru_repo_or_gate_chrome",
            },
            {
                "severity": "dns",
                "detail": "verra.xyz is unrelated third-party — do not acquire confusion; never advertise",
                "fix": "founder_dns",
            },
        ],
    },
    {
        "id": "mishara",
        "name": "Mishara",
        "role": "consumer harm path",
        "product_urls": [
            "https://mishara.onrender.com",
        ],
        "canonical": "https://mishara.onrender.com",
        "status": "live",
        "notes": [
            "Ladder Free / $99 / $499. Not Gate. Not Erra.",
        ],
    },
    {
        "id": "nisaba",
        "name": "Nisaba LLC",
        "role": "inventor / law holder",
        "product_urls": [
            "https://gate.velaru.xyz/family",
            "https://gate.velaru.xyz/nisaba",
        ],
        "canonical": "https://gate.velaru.xyz/nisaba",
        "status": "hub_on_gate",
        "notes": [
            "nisaba.xyz is Afternic-parked — not a product hub until DNS is recovered.",
        ],
        "domains": {
            "nisaba.xyz": {
                "owned_by_nisaba": "unknown_or_parked",
                "status": "afternic_parked",
                "detail": "Registrar/DNS — not a code fix.",
            }
        },
        "open_forks": [
            {
                "severity": "dns",
                "detail": "nisaba.xyz parked lander — point at this hub or leave dark",
                "fix": "founder_dns",
            }
        ],
    },
]


def manifest(public_url: str = "") -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    brands = [dict(b) for b in BRANDS]
    open_forks: list[dict[str, Any]] = []
    for b in brands:
        for fork in b.get("open_forks") or []:
            open_forks.append({"brand": b["id"], **fork})
    return {
        "spec": SPEC,
        "name": "Nisaba brand map",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "thesis": (
            "Product URLs beat vanity domains. Parked and third-party hosts are not live. "
            "Verra is the Bind Room session — not verra.xyz."
        ),
        "brands": brands,
        "open_forks": open_forks,
        "do_not_advertise": [
            "https://erra.xyz",
            "https://erra.onrender.com",
            "https://verra.xyz",
            "https://nisaba.xyz",
        ],
        "links": {
            "family": f"{base}/.well-known/family.json" if base else None,
            "scorecard": f"{base}/.well-known/scorecard.json" if base else None,
            "page": f"{base}/nisaba" if base else None,
            "json": f"{base}/.well-known/nisaba.json" if base else None,
        },
        "page": f"{base}/nisaba" if base else None,
        "their_production": False,
        "gatekeep": "Host honesty. Ours.",
    }
