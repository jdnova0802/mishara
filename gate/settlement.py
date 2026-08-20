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
    # Only populated for the final "loss_allocation_to_surviving_members" step.
    # Keys are member_ids, values are allocated cents.
    allocations: dict[str, int] | None = None


@dataclass
class MemberProfile:
    """Member risk profile (DTCC-style: limits + suspension/default states)."""

    member_id: str
    state: str = MemberState.ACTIVE.value
    # Maximum allowed gross exposure for participation in a settlement window.
    risk_limit_cents: int = 0
    # Margin rate used to compute required collateral.
    # Keep this constant inline so module import order doesn't matter.
    margin_rate_bps: int = 500  # 5% default
    # Mutualized default-fund contribution weight (relative, not necessarily cents).
    default_fund_weight: int = 1


@dataclass
class CutoffSchedule:
    """Settlement cutoff scheduling semantics (T+0 intraday)."""

    window_duration_minutes: int = WINDOW_DURATION_MINUTES if "WINDOW_DURATION_MINUTES" in globals() else 60
    # Finality hash is stamped after state transitions to SETTLED/DEFAULTED.
    finality_hash_at: str = "settled_at"
    # Window ordering phases within a single cycle.
    phases: dict[str, str] = field(
        default_factory=lambda: {
            "OPEN": "accept obligations until cutoff_at",
            "NETTING": "collapse to net positions + compute margin snapshot",
            "SETTLED/DEFAULTED": "stamp finality hash and freeze exports",
        }
    )


def member_registry_manifest() -> dict:
    """Public architecture manifest for member/risk registry semantics."""
    return {
        "spec": "gate-member-registry-v1",
        "member_states": [s.value for s in MemberState],
        "risk_limit_basis": "max gross exposure (cents) allowed in a settlement window",
        "margin": {
            "rate_bps_default": DEFAULT_MARGIN_BPS,
            "trigger": "insufficient posted collateral => suspension => default waterfall",
        },
        "default_fund": {
            "contribution_model": "mutualized default fund via relative weights (implemented as constants in this MVP)",
            "gate_skin_in_game": GATE_CAPITAL_CENTS,
        },
        "their_production": False,
    }


def cutoff_schedule_manifest() -> dict:
    return {
        "spec": "gate-cutoff-schedule-v1",
        "window_duration_minutes": WINDOW_DURATION_MINUTES,
        "cutoff_semantics": {
            "cutoff_at": "opened_at + window_duration_minutes",
            "finality_hash": "SHA-256 over settled window state, stamped at settled_at",
        },
        "phases": {
            "OPEN": "accept obligations until cutoff_at",
            "NETTING": "compute net positions + margin snapshot",
            "SETTLED/DEFAULTED": "freeze and export compliance artifacts",
        },
        "their_production": False,
    }


def pro_rata_allocate(loss_cents: int, net_exposures_cents: dict[str, int]) -> dict[str, int]:
    """Pro-rata integer allocation of a loss across surviving members.

    - shares are floored deterministically
    - remainder cents are distributed to the highest exposures (then member_id tie-break)
    """
    total = sum(max(0, int(v)) for v in (net_exposures_cents or {}).values())
    if loss_cents <= 0 or total <= 0:
        return {}

    raw: dict[str, int] = {}
    allocated = 0
    for member_id, exposure in sorted(net_exposures_cents.items(), key=lambda kv: (-kv[1], kv[0])):
        if exposure <= 0:
            continue
        share = (loss_cents * exposure) // total
        raw[member_id] = share
        allocated += share

    remainder = loss_cents - allocated
    if remainder > 0:
        # Give remaining cents to highest-exposure members first.
        ordered = [m for m, _ in sorted(net_exposures_cents.items(), key=lambda kv: (-kv[1], kv[0])) if net_exposures_cents.get(m, 0) > 0]
        for i in range(remainder):
            if not ordered:
                break
            raw[ordered[i % len(ordered)]] = raw.get(ordered[i % len(ordered)], 0) + 1

    # Final normalization: ensure exact sum if possible.
    # (If exposures had all <=0, we'd have returned {} earlier.)
    return raw


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
        # Loss allocation is by surviving members' *net* exposure.
        surviving_exposures: dict[str, int] = {}
        for p in positions:
            if p.member_id in window.defaulted_members:
                continue
            surviving_exposures[p.member_id] = surviving_exposures.get(p.member_id, 0) + abs(int(p.net_cents))

        waterfall_steps = run_waterfall(
            loss_cents=total_loss,
            defaulter_margin_cents=sum(m.posted_collateral_cents for m in defaulted),
            surviving_net_exposures_cents=surviving_exposures,
        )
        window.waterfall = [asdict(s) for s in waterfall_steps]
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


def route_obligation_with_schism(
    *,
    obligation: Obligation,
    current_window: SettlementWindow,
    next_window: SettlementWindow,
) -> tuple[SettlementWindow, dict | None]:
    """Accept obligation into current window, or route to next with schism if late."""
    try:
        from gate import kappa as kappa_mod
    except ImportError:
        import kappa as kappa_mod

    payload = asdict(obligation)
    schism = kappa_mod.schism_at_cutoff(
        obligation_id=obligation.id,
        obligation_at=obligation.created_at,
        cutoff_at=current_window.cutoff_at or "",
        would_window_id=current_window.id,
        actual_window_id=next_window.id,
    )
    if schism:
        next_window.obligations.append(payload)
        return next_window, schism
    current_window.obligations.append(payload)
    return current_window, None


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
    surviving_net_exposures_cents: dict[str, int] | None = None,
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
        allocations = pro_rata_allocate(remaining, surviving_net_exposures_cents or {})
        allocated_sum = sum(allocations.values())
        # If there are no surviving exposures, Gate cannot allocate further.
        remaining_after = remaining - allocated_sum

        steps.append(
            WaterfallStep(
                layer=len(layers) + 1,
                source="loss_allocation_to_surviving_members",
                available_cents=allocated_sum,
                consumed_cents=allocated_sum,
                remaining_loss_cents=max(0, remaining_after),
                allocations=allocations or None,
            )
        )

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

    try:
        from gate import possibility as possibility_mod
    except ImportError:
        import possibility as possibility_mod
    try:
        from gate import constitution as constitution_mod
    except ImportError:
        import constitution as constitution_mod
    moments = possibility_mod.finality_moments(
        window_id=window.id,
        opened_at=window.opened_at,
        cutoff_at=window.cutoff_at,
        settled_at=window.settled_at,
        finality_hash=window.finality_hash,
        state=window.state,
    )
    clear = constitution_mod.extinguishment(
        window_id=window.id,
        state=window.state,
        finality_hash=window.finality_hash,
        net_positions=window.net_positions,
    )
    return {
        "spec": REPORTING_SPEC,
        "window_id": window.id,
        "state": window.state,
        "opened_at": window.opened_at,
        "settled_at": window.settled_at,
        "finality_hash": window.finality_hash,
        "finality_moments": moments,
        "extinguishment": clear,
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
            "member_registry": member_registry_manifest(),
            "cutoff_schedule": cutoff_schedule_manifest(),
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
                    "4. Pro-rata loss allocation to surviving members by net exposure (last resort)",
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
        "distribution": f"{public_url}/.well-known/distribution.json",
    }
