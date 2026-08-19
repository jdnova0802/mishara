"""Settlement engine — DTCC-shaped clearing for Gate.

Architectural components:
  1. Netting: collapse gross bind events into net positions per member per window.
  2. Settlement windows: T+0 intraday cycles with finality cutoffs.
  3. Default waterfall: cascading loss allocation when a licensed parent fails.
  4. Margin: collateral requirements per member based on gross exposure.
  5. Multi-asset streams: withdraw, bind-only, payout as separate settlement classes.
  6. Regulatory reporting: machine-readable compliance export per window.

Not SaaS. Not a dashboard. Load-bearing infrastructure that collapses risk.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any

SPEC = "gate-settlement-v1"
NETTING_SPEC = "gate-netting-v1"
WATERFALL_SPEC = "gate-default-waterfall-v1"
MARGIN_SPEC = "gate-margin-v1"
REPORTING_SPEC = "gate-regulatory-report-v1"


class AssetClass(str, Enum):
    WITHDRAW = "withdraw"
    BIND_ONLY = "bind_only"
    PAYOUT = "payout"


class SettlementState(str, Enum):
    OPEN = "OPEN"
    NETTING = "NETTING"
    SETTLED = "SETTLED"
    DEFAULTED = "DEFAULTED"


class MemberState(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DEFAULTED = "DEFAULTED"


@dataclass
class Obligation:
    """One gross obligation (a bind event that cleared)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    member_id: str = ""
    counterparty_id: str = ""
    asset_class: str = AssetClass.BIND_ONLY.value
    gross_cents: int = 0
    direction: str = "pay"  # "pay" or "receive"
    job_id: str | None = None
    event_id: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class NetPosition:
    """Result of netting: what a member actually owes or is owed."""
    member_id: str = ""
    asset_class: str = AssetClass.BIND_ONLY.value
    gross_pay_cents: int = 0
    gross_receive_cents: int = 0
    net_cents: int = 0  # positive = owes, negative = is owed
    obligation_count: int = 0
    settled: bool = False


@dataclass
class MarginRequirement:
    """Collateral a member must post based on gross exposure."""
    member_id: str = ""
    gross_exposure_cents: int = 0
    margin_rate_bps: int = 500  # 5% default
    required_collateral_cents: int = 0
    posted_collateral_cents: int = 0
    adequate: bool = True


@dataclass
class WaterfallStep:
    """One layer in the default waterfall."""
    layer: int = 0
    source: str = ""  # "defaulter_margin", "mutualized_fund", "gate_capital", "loss_allocation"
    available_cents: int = 0
    consumed_cents: int = 0
    remaining_loss_cents: int = 0


@dataclass
class SettlementWindow:
    """One settlement cycle (T+0 intraday)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    state: str = SettlementState.OPEN.value
    opened_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    cutoff_at: str | None = None
    settled_at: str | None = None
    obligations: list = field(default_factory=list)
    net_positions: list = field(default_factory=list)
    waterfall: list = field(default_factory=list)
    margin_snapshot: list = field(default_factory=list)
    defaulted_members: list = field(default_factory=list)
    finality_hash: str | None = None


# ---------------------------------------------------------------------------
# Netting Engine
# ---------------------------------------------------------------------------

def compute_net_positions(obligations: list[Obligation]) -> list[NetPosition]:
    """Collapse gross obligations into net positions per member per asset class.

    This is the core DTCC-shaped netting algorithm: many bilateral obligations
    become fewer net settlement amounts.
    """
    positions: dict[tuple[str, str], NetPosition] = {}

    for ob in obligations:
        key = (ob.member_id, ob.asset_class)
        if key not in positions:
            positions[key] = NetPosition(member_id=ob.member_id, asset_class=ob.asset_class)
        pos = positions[key]
        pos.obligation_count += 1
        if ob.direction == "pay":
            pos.gross_pay_cents += ob.gross_cents
        else:
            pos.gross_receive_cents += ob.gross_cents

    for pos in positions.values():
        pos.net_cents = pos.gross_pay_cents - pos.gross_receive_cents

    return list(positions.values())


def netting_ratio(positions: list[NetPosition]) -> dict:
    """How much netting reduced the gross to net (DTCC typically achieves 98%+)."""
    gross = sum(p.gross_pay_cents + p.gross_receive_cents for p in positions)
    net = sum(abs(p.net_cents) for p in positions)
    ratio = 1.0 - (net / gross) if gross > 0 else 0.0
    return {
        "spec": NETTING_SPEC,
        "gross_cents": gross,
        "net_cents": net,
        "reduction_ratio": round(ratio, 4),
        "positions": len(positions),
    }


# ---------------------------------------------------------------------------
# Settlement Windows (T+0 intraday)
# ---------------------------------------------------------------------------

WINDOW_DURATION_MINUTES = 60  # 1-hour settlement cycles


def open_window() -> SettlementWindow:
    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(minutes=WINDOW_DURATION_MINUTES)
    return SettlementWindow(
        state=SettlementState.OPEN.value,
        opened_at=now.isoformat(),
        cutoff_at=cutoff.isoformat(),
    )


def close_window(window: SettlementWindow) -> SettlementWindow:
    """Move window to NETTING, compute net positions, then SETTLED."""
    window.state = SettlementState.NETTING.value
    obligations = [Obligation(**o) if isinstance(o, dict) else o for o in window.obligations]
    positions = compute_net_positions(obligations)
    window.net_positions = [asdict(p) for p in positions]

    margin_snap = [compute_margin(ob_list=obligations, member_id=p.member_id) for p in positions]
    window.margin_snapshot = [asdict(m) for m in margin_snap]

    defaulted = [m for m in margin_snap if not m.adequate]
    window.defaulted_members = [m.member_id for m in defaulted]

    if defaulted:
        window.state = SettlementState.DEFAULTED.value
        total_loss = sum(m.required_collateral_cents - m.posted_collateral_cents for m in defaulted)
        window.waterfall = [asdict(s) for s in run_waterfall(
            loss_cents=total_loss,
            defaulter_margin_cents=sum(m.posted_collateral_cents for m in defaulted),
        )]
    else:
        for p_dict in window.net_positions:
            p_dict["settled"] = True
        window.state = SettlementState.SETTLED.value

    window.settled_at = datetime.now(timezone.utc).isoformat()
    window.finality_hash = _finality_hash(window)
    return window


def _finality_hash(window: SettlementWindow) -> str:
    """Tamper-evident hash over the settled window state."""
    canonical = json.dumps(
        {"id": window.id, "net_positions": window.net_positions, "settled_at": window.settled_at},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Margin / Collateral
# ---------------------------------------------------------------------------

DEFAULT_MARGIN_BPS = 500  # 5% of gross exposure


def compute_margin(
    *,
    ob_list: list[Obligation],
    member_id: str,
    margin_bps: int = DEFAULT_MARGIN_BPS,
    posted_cents: int = 0,
) -> MarginRequirement:
    """Compute margin requirement for a member based on their gross exposure."""
    gross = sum(o.gross_cents for o in ob_list if o.member_id == member_id)
    required = (gross * margin_bps) // 10_000
    return MarginRequirement(
        member_id=member_id,
        gross_exposure_cents=gross,
        margin_rate_bps=margin_bps,
        required_collateral_cents=required,
        posted_collateral_cents=posted_cents,
        adequate=posted_cents >= required,
    )


# ---------------------------------------------------------------------------
# Default Waterfall
# ---------------------------------------------------------------------------

MUTUALIZED_FUND_CENTS = 10_000_000_00  # $10M mutualized default fund
GATE_CAPITAL_CENTS = 5_000_000_00  # $5M Gate (Nisaba) skin-in-the-game layer


def run_waterfall(
    *,
    loss_cents: int,
    defaulter_margin_cents: int = 0,
    mutualized_fund_cents: int = MUTUALIZED_FUND_CENTS,
    gate_capital_cents: int = GATE_CAPITAL_CENTS,
) -> list[WaterfallStep]:
    """DTCC-shaped default waterfall: defaulter margin → mutualized fund → Gate capital → loss allocation.

    Each layer absorbs loss in order. Remaining loss after all layers = allocated to surviving members.
    """
    remaining = max(0, loss_cents)
    steps: list[WaterfallStep] = []

    layers = [
        ("defaulter_margin", defaulter_margin_cents),
        ("mutualized_fund", mutualized_fund_cents),
        ("gate_capital", gate_capital_cents),
    ]

    for i, (source, available) in enumerate(layers):
        consumed = min(remaining, available)
        remaining -= consumed
        steps.append(WaterfallStep(
            layer=i + 1,
            source=source,
            available_cents=available,
            consumed_cents=consumed,
            remaining_loss_cents=remaining,
        ))

    if remaining > 0:
        steps.append(WaterfallStep(
            layer=len(layers) + 1,
            source="loss_allocation_to_surviving_members",
            available_cents=0,
            consumed_cents=0,
            remaining_loss_cents=remaining,
        ))

    return steps


# ---------------------------------------------------------------------------
# Regulatory Reporting
# ---------------------------------------------------------------------------

def regulatory_report(window: SettlementWindow) -> dict:
    """Machine-readable compliance export for one settlement window."""
    obligations = [Obligation(**o) if isinstance(o, dict) else o for o in window.obligations]
    by_class: dict[str, int] = {}
    for ob in obligations:
        by_class[ob.asset_class] = by_class.get(ob.asset_class, 0) + ob.gross_cents

    return {
        "spec": REPORTING_SPEC,
        "window_id": window.id,
        "state": window.state,
        "opened_at": window.opened_at,
        "settled_at": window.settled_at,
        "finality_hash": window.finality_hash,
        "obligation_count": len(obligations),
        "gross_by_asset_class_cents": by_class,
        "net_positions": window.net_positions,
        "netting": netting_ratio(compute_net_positions(obligations)),
        "margin_snapshot": window.margin_snapshot,
        "defaulted_members": window.defaulted_members,
        "waterfall": window.waterfall,
        "their_production": False,
    }


# ---------------------------------------------------------------------------
# Public manifest
# ---------------------------------------------------------------------------

def spec(public_url: str) -> dict:
    return {
        "spec": SPEC,
        "name": "Gate Settlement Engine",
        "architecture": "DTCC-shaped: netting + settlement windows + default waterfall + margin + multi-asset",
        "components": {
            "netting": {
                "spec": NETTING_SPEC,
                "what": "Collapse gross obligations into net positions per member per asset class",
                "goal": "98%+ reduction ratio at scale (same target as DTCC/NSCC)",
            },
            "settlement_windows": {
                "cycle": f"{WINDOW_DURATION_MINUTES} minutes (T+0 intraday)",
                "finality": "SHA-256 hash over settled positions — tamper-evident",
                "states": [s.value for s in SettlementState],
            },
            "default_waterfall": {
                "spec": WATERFALL_SPEC,
                "layers": [
                    "1. Defaulter's posted margin",
                    "2. Mutualized default fund (all members contribute)",
                    "3. Gate (Nisaba) skin-in-the-game capital",
                    "4. Loss allocation to surviving members (last resort)",
                ],
                "mutualized_fund_cents": MUTUALIZED_FUND_CENTS,
                "gate_capital_cents": GATE_CAPITAL_CENTS,
            },
            "margin": {
                "spec": MARGIN_SPEC,
                "rate_bps": DEFAULT_MARGIN_BPS,
                "basis": "gross exposure per member",
                "inadequate_triggers": "suspension → default waterfall",
            },
            "asset_classes": [ac.value for ac in AssetClass],
            "regulatory_reporting": {
                "spec": REPORTING_SPEC,
                "format": "JSON per window",
                "includes": ["gross by asset class", "net positions", "netting ratio", "margin", "waterfall", "finality hash"],
            },
        },
        "fail_closed": True,
        "their_production": False,
        "url": f"{public_url}/.well-known/settlement.json",
    }
