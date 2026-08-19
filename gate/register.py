"""The register — external face of the mouth. Not SaaS.

Infrastructure on irreversible spend: permission mortality, fund-style fees,
10 bps + carry on cleared flow. Civilization default is the asset; GP keeps the mouth.
"""
from __future__ import annotations

try:
    from gate import operator_invoice as operator_mod
except ImportError:
    import operator_invoice as operator_mod

SPEC = "gate-register-v1"


def manifest(public_url: str, contact_email: str) -> dict:
    base = (public_url or "").rstrip("/")
    fees = operator_mod.manifest(base, contact_email)["register_fees"]
    return {
        "spec": SPEC,
        "name": "The register",
        "operator": "Nisaba LLC",
        "contact": contact_email,
        "what": "The mouth civilization uses so irreversible spend cannot bypass permission.",
        "civilization": {
            "asset": "default on irreversible spend — globally, across licensed rails",
            "not": "a money hoard without a mouth; not SaaS; not a calculator",
            "reward": "GP register: management on mouths + bps + carry on cleared flow",
            "keep": "Nisaba retains the mouth — do not dilute the GP early",
        },
        "not": [
            "SaaS",
            "a calculator",
            "a dashboard product",
            "a museum hop nobody required",
            "unlicensed / offshore gambling",
            "a second married bind-only write",
        ],
        "mouth": {
            "one_door": "POST /job/v1/jobs/{job_id}/bind-only (or one welded payout path)",
            "parent": f"{base}/.well-known/license-fuse.json",
            "children_cannot_outlive_parent": True,
            "ticket": f"{base}/.well-known/commit-auth.json",
            "scanner": f"{base}/.well-known/spend-protocol.json",
            "nos": f"{base}/.well-known/restraint.json",
            "fail_closed": True,
        },
        "register_fees": fees,
        "equations": {
            "asset": "default x permission x welded mouths",
            "management": fees["fund_analog"]["management"],
            "flow": fees["fund_analog"]["flow"],
            "not_the_prize": "one lonely quiet minimum on one door",
        },
        "scale": {
            "note": "Annual flow bands at 10 bps + carry. Not a forecast.",
            "year": operator_mod.year_scale(),
            "potential": fees["potential"],
        },
        "sit_down": {
            "weld": operator_mod.WELD_PRICE_LABEL,
            "requires_management": True,
            "deliverable": "one production write fail-closed in 48hr + per-mouth rent",
            "checkout": f"{base}/operator",
        },
        "licensed_only": True,
        "one_write_per_weld": True,
        "their_production": False,
        "page": f"{base}/register",
        "operator_contract": f"{base}/.well-known/operator.json",
        "positioning": f"{base}/.well-known/positioning.json",
        "engine": "https://velaru.xyz",
    }
