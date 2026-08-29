"""Mouth Ceiling enforcement — fail on new L2 invention modules until Gate 1.

Companion: MOUTH_CEILING.md · mouth_ceiling_freeze.json · ops_guards gate1 check.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

SPEC = "gate-mouth-ceiling-guard-v1"
FREEZE_PATH = Path(__file__).resolve().parent / "mouth_ceiling_freeze.json"

CORE_MODULES = frozenset(
    {
        "app.py",
        "db.py",
        "ops_guards.py",
        "mouth_ceiling_guard.py",
        "licensing_pack.py",
        "owner_guardrails.py",
        "bind_room.py",
        "listings.py",
        "register.py",
        "legal.py",
        "receipt.py",
        "epoch.py",
        "bound.py",
        "charge_authority.py",
        "cli.py",
        "deploy_render.py",
        "demo_limit.py",
        "evidence_log.py",
        "exclusion.py",
        "fields.py",
        "floor.py",
        "live.py",
        "mcp_server.py",
        "notify.py",
        "openapi_discovery.py",
        "operator_invoice.py",
        "particular.py",
        "positioning.py",
        "prefinality.py",
        "production_skin.py",
        "promo_clock.py",
        "public_url.py",
        "rtp_adapter.py",
        "runbook.py",
        "scorecard.py",
        "settlement.py",
        "spend_protocol.py",
        "ticket.py",
        "weld.py",
        "x402_audit.py",
        "x402_challenge.py",
        "action_os.py",
        "audiences.py",
        "canary.py",
        "command_radiation.py",
        "continuity_live.py",
        "counterfactual.py",
        "crucial_roles.py",
        "family_voices.py",
        "gate_anatomy.py",
        "foothill_max.py",
        "mandate_layer.py",
        "inhabitant.py",
        "intentions.py",
        "kappa.py",
        "license_fuse.py",
        "liturgy.py",
        "proof_suite.py",
        "restraint.py",
        "science_pri.py",
        "civ_maintenance.py",
        "exclusive.py",
        "counterpart.py",
    }
)


def _load_freeze() -> dict[str, Any]:
    return json.loads(FREEZE_PATH.read_text(encoding="utf-8"))


def is_invention_module(path: Path) -> bool:
    if path.name.startswith("test_") or path.suffix != ".py":
        return False
    if path.name in CORE_MODULES:
        return False
    if path.parent.name == "sdk":
        return False
    if path.name.endswith("_deep.py") or path.name.startswith("ip_asset_"):
        return True
    text = path.read_text(encoding="utf-8", errors="replace")
    if re.search(r'SPEC\s*=\s*"gate-', text) and (
        "invention" in text.lower() or "evaluate_slug" in text or "INVENTION" in text
    ):
        return True
    return False


def mouth_ceiling_check(
    gate_root: Path | None = None,
    *,
    gate1_met: bool | None = None,
) -> dict[str, Any]:
    """Return fail if any L2 invention module exists outside the freeze manifest."""
    gate_root = gate_root or Path(__file__).resolve().parent
    freeze = _load_freeze()
    allowed = frozenset(freeze.get("l2_invention_modules") or [])
    present = sorted(
        p.name for p in gate_root.glob("*.py") if is_invention_module(p)
    )
    unknown = sorted(set(present) - allowed)
    if gate1_met is None:
        try:
            from gate.ops_guards import gate1_status
        except ImportError:
            from ops_guards import gate1_status

        gate1_met = bool(gate1_status().get("gate1_met"))

    if unknown:
        return {
            "ok": False,
            "level": "fail",
            "code": "mouth_ceiling_new_l2_modules",
            "spec": SPEC,
            "frozen_at": freeze.get("frozen_at"),
            "gate1_met": gate1_met,
            "unknown_modules": unknown,
            "allowed_count": len(allowed),
            "present_count": len(present),
            "message": (
                f"Mouth Ceiling violated: {len(unknown)} new L2 module(s) — "
                + ", ".join(unknown)
                + ". Gate 1 required before adding invention modules."
            ),
        }
    if not gate1_met and freeze.get("gate1_required_to_add_l2_modules"):
        return {
            "ok": True,
            "level": "ok",
            "code": "mouth_ceiling_frozen",
            "spec": SPEC,
            "frozen_at": freeze.get("frozen_at"),
            "gate1_met": False,
            "allowed_count": len(allowed),
            "message": f"Mouth Ceiling enforced — {len(allowed)} L2 modules frozen until Gate 1",
        }
    return {
        "ok": True,
        "level": "ok",
        "code": "mouth_ceiling_ok",
        "spec": SPEC,
        "gate1_met": gate1_met,
        "allowed_count": len(allowed),
        "message": "Mouth Ceiling OK",
    }


def main() -> int:
    import json
    import sys

    result = mouth_ceiling_check()
    print(json.dumps(result, indent=2))
    return 2 if not result["ok"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
