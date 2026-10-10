"""Register bill — auto invoice from cleared-flow ledger + management.

Ops posts cleared flow; this builds the GP-style invoice (mgmt + 10 bps + carry)
ready for Stripe / operator settlement. Does not flip their_production.
"""
from __future__ import annotations

from typing import Any

try:
    from gate import db
except ImportError:
    import db

try:
    from gate import operator_invoice as operator_mod
except ImportError:
    import operator_invoice as operator_mod

SPEC = "gate-register-bill-v1"


def from_ledger(
    *,
    welded_writes: int = 1,
    live_parents: int | None = None,
    hop_count: int | None = None,
) -> dict[str, Any]:
    totals = db.cleared_flow_totals()
    cleared = int(totals.get("cleared_cents") or 0)
    hops = int(hop_count if hop_count is not None else (totals.get("hop_count") or 0))
    parents = int(live_parents) if live_parents is not None else db.count_live_license_parents()
    invoice = operator_mod.register_invoice(
        cleared_cents=cleared,
        hop_count=hops,
        welded_writes=max(0, int(welded_writes)),
        live_parents=max(0, parents),
    )
    return {
        "spec": SPEC,
        "ok": True,
        "ledger_totals": totals,
        "invoice": invoice,
        "carry_active": cleared > operator_mod.HURDLE_CLEARED_CENTS,
        "bps": operator_mod.BPS,
        "bps_carry": operator_mod.BPS_CARRY,
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Register bill",
        "what": "Build management + bps + carry invoice from the cleared-flow ledger.",
        "post": f"{base}/v1/register/bill",
        "cleared": f"{base}/v1/register/cleared",
        "cleared_manifest": f"{base}/.well-known/cleared-flow.json",
        "operator": f"{base}/.well-known/operator.json",
        "their_production": False,
    }
