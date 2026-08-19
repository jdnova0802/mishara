"""The register — external face of the mouth. Not SaaS.

Infrastructure on irreversible spend: permission mortality, one married write,
10 bps of what clears. The floor is a quiet-door minimum. The asset is default.
"""
from __future__ import annotations

try:
    from gate import operator_invoice as operator_mod
except ImportError:
    import operator_invoice as operator_mod

SPEC = "gate-register-v1"


def manifest(public_url: str, contact_email: str) -> dict:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "The register",
        "operator": "Nisaba LLC",
        "contact": contact_email,
        "what": "The mouth civilization uses so irreversible spend cannot bypass permission.",
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
        "equations": {
            "asset": "default x permission x welded mouths",
            "cash_register": "max(floor, bps of cleared, per-hop)",
            "bps": operator_mod.BPS,
            "quiet_minimum": operator_mod.FLOOR_PRICE_LABEL,
            "not_the_prize": operator_mod.FLOOR_PRICE_LABEL,
        },
        "scale": {
            "note": "10 bps of what clears through welded doors. Not a forecast.",
            "year": operator_mod.year_scale(),
        },
        "sit_down": {
            "weld": operator_mod.WELD_PRICE_LABEL,
            "deliverable": "one production write fail-closed in 48hr",
            "checkout": f"{base}/operator",
        },
        "licensed_only": True,
        "one_write_per_weld": True,
        "their_production": False,
        "page": f"{base}/register",
        "operator_contract": f"{base}/.well-known/operator.json",
        "engine": "https://velaru.xyz",
    }
