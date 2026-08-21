"""Operator invoice — fund-style register on infrastructure.

Not SaaS. Two legs like a GP:
  1. Management — rent per welded write + per LIVE license parent (2%-analog).
  2. Flow register — 10 bps on cleared + carry above hurdle (20%-analog).

One married write per weld. Licensed payout / bind only. Not a second engine.
"""
from __future__ import annotations

SPEC = "gate-operator-invoice-v1"
REGISTER_FEES_SPEC = "gate-register-fees-v1"

WELD_PRICE_LABEL = "$25,000"
WELD_PRICE_CENTS = 2_500_000
FLOOR_PRICE_LABEL = "$5,000/mo"
FLOOR_PRICE_CENTS = 500_000
BPS = 10
BPS_CARRY = 5  # additional bps on cleared above hurdle (15 total on marginal)
HURDLE_CLEARED_CENTS = 50_000_000_000  # $500M/mo — carry analog kicks in above this
HOP_CENTS = 10
EXTRA_WRITE_CENTS = WELD_PRICE_CENTS

YEAR_SCALE = (
    {"cleared_cents": 10_000_000_000, "through": "$100M"},
    {"cleared_cents": 100_000_000_000, "through": "$1B"},
    {"cleared_cents": 1_000_000_000_000, "through": "$10B"},
    {"cleared_cents": 10_000_000_000_000, "through": "$100B"},
    {"cleared_cents": 100_000_000_000_000, "through": "$1T"},
)

COMMITTED_FLOW_TIERS = (
    {"band": "quiet", "through_month": "$100M", "cleared_cents": 10_000_000_000, "bps": BPS},
    {"band": "desk", "through_month": "$500M", "cleared_cents": 50_000_000_000, "bps": BPS},
    {"band": "operator", "through_month": "$1B", "cleared_cents": 100_000_000_000, "bps": BPS},
    {"band": "rail", "through_month": "$10B", "cleared_cents": 1_000_000_000_000, "bps": BPS},
    {
        "band": "carry",
        "through_month": f"above ${HURDLE_CLEARED_CENTS // 100_000_000}/mo",
        "cleared_cents": HURDLE_CLEARED_CENTS,
        "bps_base": BPS,
        "bps_carry": BPS_CARRY,
        "bps_total_on_excess": BPS + BPS_CARRY,
    },
)

WRITES = {
    "withdraw": {
        "id": "withdraw",
        "label": "Withdraw / payout",
        "meaning": "Clear-before-wire. Their withdraw does not fire unless Gate says yes.",
        "example_path": "POST /v1/payouts/{id}/release",
    },
    "bind_only": {
        "id": "bind_only",
        "label": "Bind-only",
        "meaning": "Policy becomes Bound. Ticket married to one write.",
        "example_path": "POST /job/v1/jobs/{job_id}/bind-only",
    },
}


def bps_cents(cleared_cents: int, bps: int = BPS) -> int:
    return (max(0, int(cleared_cents)) * int(bps)) // 10_000


def management_register(
    *,
    welded_writes: int = 1,
    live_parents: int = 0,
    floor_cents: int = FLOOR_PRICE_CENTS,
) -> dict:
    """Mgmt leg: per welded write + per LIVE license parent. Fund 2%-analog."""
    writes = max(0, int(welded_writes))
    parents = max(0, int(live_parents))
    per = max(0, int(floor_cents))
    total = (writes + parents) * per
    return {
        "spec": REGISTER_FEES_SPEC,
        "leg": "management",
        "fund_analog": "2% on AUM — here: rent per mouth + per LIVE parent",
        "welded_writes": writes,
        "live_parents": parents,
        "per_mouth_cents": per,
        "per_mouth": FLOOR_PRICE_LABEL,
        "total_cents": total,
        "total": f"${total / 100:,.2f}",
    }


def flow_register(
    *,
    cleared_cents: int = 0,
    hop_count: int = 0,
    bps: int = BPS,
    carry_bps: int = BPS_CARRY,
    hurdle_cents: int = HURDLE_CLEARED_CENTS,
    hop_cents: int = HOP_CENTS,
    quiet_floor_cents: int = FLOOR_PRICE_CENTS,
) -> dict:
    """Flow leg: 10 bps + carry above hurdle, vs per-hop. Fund 20%-analog on marginal flow."""
    cleared = max(0, int(cleared_cents))
    hops = max(0, int(hop_count))
    hurdle = max(0, int(hurdle_cents))
    base = bps_cents(cleared, bps=bps)
    excess = max(0, cleared - hurdle)
    carry = bps_cents(excess, bps=carry_bps)
    flow = base + carry
    hop_amt = hops * int(hop_cents)
    billed = max(quiet_floor_cents if cleared == 0 and hops == 0 else 0, flow, hop_amt)
    if cleared == 0 and hops == 0:
        billed = 0
    else:
        billed = max(flow, hop_amt)
    return {
        "spec": REGISTER_FEES_SPEC,
        "leg": "flow",
        "fund_analog": "20% carry — here: +5 bps on cleared above hurdle",
        "cleared_cents": cleared,
        "hop_count": hops,
        "bps": int(bps),
        "bps_base_cents": base,
        "hurdle_cents": hurdle,
        "excess_cents": excess,
        "carry_bps": int(carry_bps),
        "carry_cents": carry,
        "flow_cents": flow,
        "per_hop_cents": hop_amt,
        "billed_cents": billed,
        "billed": f"${billed / 100:,.2f}",
        "winner": "flow"
        if flow >= hop_amt
        else ("per_hop" if hop_amt else "none"),
    }


def register_invoice(
    *,
    cleared_cents: int = 0,
    hop_count: int = 0,
    welded_writes: int = 1,
    live_parents: int = 0,
) -> dict:
    """Full month: management + flow. This is the fund-style register."""
    mgmt = management_register(welded_writes=welded_writes, live_parents=live_parents)
    flow = flow_register(cleared_cents=cleared_cents, hop_count=hop_count)
    total = mgmt["total_cents"] + flow["billed_cents"]
    return {
        "spec": REGISTER_FEES_SPEC,
        "formula": "management (per write + per LIVE parent) + flow (bps + carry above hurdle)",
        "not_saas": True,
        "management": mgmt,
        "flow": flow,
        "total_cents": total,
        "total": f"${total / 100:,.2f}",
        "committed_flow_tiers": list(COMMITTED_FLOW_TIERS),
    }


def invoice(
    *,
    cleared_cents: int = 0,
    hop_count: int = 0,
    floor_cents: int = FLOOR_PRICE_CENTS,
    bps: int = BPS,
    hop_cents: int = HOP_CENTS,
    welded_writes: int = 1,
    live_parents: int = 0,
) -> dict:
    """Backward-compatible single-door view; delegates to register_invoice when scaled."""
    if welded_writes != 1 or live_parents != 0:
        reg = register_invoice(
            cleared_cents=cleared_cents,
            hop_count=hop_count,
            welded_writes=welded_writes,
            live_parents=live_parents,
        )
        reg["formula"] = "management + flow (fund-style register)"
        return reg
    cleared = max(0, int(cleared_cents))
    hops = max(0, int(hop_count))
    floor_amt = max(0, int(floor_cents))
    flow = flow_register(
        cleared_cents=cleared,
        hop_count=hops,
        bps=bps,
        hop_cents=hop_cents,
        quiet_floor_cents=0,
    )
    billed = max(floor_amt, flow["billed_cents"])
    legs = {
        "floor": floor_amt,
        "bps": flow["bps_base_cents"] + flow["carry_cents"],
        "per_hop": flow["per_hop_cents"],
    }
    winners = [name for name, amt in legs.items() if amt == billed]
    return {
        "cleared_cents": cleared,
        "hop_count": hops,
        "bps": int(bps),
        "hop_cents": int(hop_cents),
        "legs_cents": legs,
        "billed_cents": billed,
        "billed": f"${billed / 100:,.2f}",
        "winner": winners[0] if len(winners) == 1 else winners,
        "formula": "max(floor, bps + carry above hurdle, per-hop)",
        "carry": {
            "hurdle_cents": HURDLE_CLEARED_CENTS,
            "carry_bps": BPS_CARRY,
            "excess_cents": flow["excess_cents"],
            "carry_cents": flow["carry_cents"],
        },
    }


def year_scale(*, bps: int = BPS, carry_bps: int = BPS_CARRY) -> list[dict]:
    rows = []
    for row in YEAR_SCALE:
        cleared = row["cleared_cents"]
        base = bps_cents(cleared, bps=bps)
        excess = max(0, cleared - HURDLE_CLEARED_CENTS)
        carry = bps_cents(excess, bps=carry_bps)
        gate = base + carry
        rows.append(
            {
                "through": row["through"],
                "cleared_cents": cleared,
                "bps": int(bps),
                "carry_bps_on_excess": int(carry_bps),
                "gate_cents": gate,
                "gate": f"${gate / 100:,.0f}",
            }
        )
    return rows


def potential(*, welded_writes: int = 100, live_parents: int = 200) -> dict:
    """Illustrative GP register at civilization scale. Not a forecast."""
    scenarios = []
    for row in YEAR_SCALE:
        reg = register_invoice(
            cleared_cents=row["cleared_cents"],
            hop_count=0,
            welded_writes=welded_writes,
            live_parents=live_parents,
        )
        scenarios.append(
            {
                "through": row["through"],
                "register": reg["total"],
                "management": reg["management"]["total"],
                "flow": reg["flow"]["billed"],
            }
        )
    return {
        "note": "Illustrative annual register if monthly cleared equals band. Not a forecast.",
        "mouths": {"welded_writes": welded_writes, "live_parents": live_parents},
        "gp_ownership": "Nisaba LLC retains the mouth — do not dilute the GP early",
        "scenarios": scenarios,
    }


def manifest(public_url: str, contact_email: str) -> dict:
    return {
        "spec": SPEC,
        "page": f"{public_url}/register",
        "checkout": f"{public_url}/operator",
        "operator": "Nisaba LLC",
        "contact": contact_email,
        "not_a_new_engine": True,
        "not_saas": True,
        "one_write_per_weld": True,
        "their_production": False,
        "licensed_only": True,
        "thesis": {
            "asset": "default x permission x welded mouths — civilization infrastructure",
            "cash": "management + flow register (fund-style, not a subscription tier)",
            "default": "the only door on one irreversible write",
            "bps": BPS,
            "carry_bps_above_hurdle": BPS_CARRY,
            "hurdle_cleared_month": f"${HURDLE_CLEARED_CENTS // 100_000_000}/mo",
            "volume": "cleared flow through welded mouths",
            "not_the_product": "one lonely $5,000/mo line",
        },
        "register_fees": {
            "spec": REGISTER_FEES_SPEC,
            "fund_analog": {
                "management": f"{FLOOR_PRICE_LABEL} per welded write + {FLOOR_PRICE_LABEL} per LIVE license parent",
                "flow": f"{BPS} bps on cleared + {BPS_CARRY} bps on cleared above ${HURDLE_CLEARED_CENTS // 100_000_000}/mo",
                "per_hop": f"${HOP_CENTS / 100:.2f}/hop when hops win the flow leg",
            },
            "formula": "management + flow (not max — both legs apply at scale)",
            "legacy_single_door": "max(floor, bps + carry, per-hop) when one write and no parent rent",
            "committed_flow_tiers": list(COMMITTED_FLOW_TIERS),
            "example_quiet": register_invoice(cleared_cents=120_000_000, hop_count=8_000, welded_writes=1),
            "example_scale": register_invoice(
                cleared_cents=100_000_000_000,
                hop_count=1_000,
                welded_writes=10,
                live_parents=25,
            ),
            "potential": potential(welded_writes=100, live_parents=500),
        },
        "refuse": [
            "unlicensed / offshore gambling",
            "second married write in the same weld",
            "PII on the hop",
            "SaaS seat pricing as the story",
        ],
        "skus": {
            "weld": {
                "label": WELD_PRICE_LABEL,
                "amount_cents": WELD_PRICE_CENTS,
                "kind": "one_time",
                "deliverable": "one production write fail-closed in 48hr",
                "checkout_requires_management": True,
            },
            "floor_per_mouth": {
                "label": FLOOR_PRICE_LABEL,
                "amount_cents": FLOOR_PRICE_CENTS,
                "kind": "monthly",
                "unit": "per welded write + per LIVE license parent",
                "deliverable": "management leg — rent per welded path and active parent license",
            },
            "extra_write": {
                "label": WELD_PRICE_LABEL,
                "amount_cents": EXTRA_WRITE_CENTS,
                "kind": "one_time",
                "deliverable": "second socket adds another management mouth + flow path",
            },
        },
        "invoice": {
            "formula": "management + flow (fund-style register)",
            "bps": BPS,
            "carry_bps": BPS_CARRY,
            "hurdle_cleared_cents": HURDLE_CLEARED_CENTS,
            "hop_cents": HOP_CENTS,
            "floor_per_mouth_cents": FLOOR_PRICE_CENTS,
            "quiet_month": invoice(cleared_cents=120_000_000, hop_count=8_000),
            "year": year_scale(),
        },
        "writes": list(WRITES.values()),
        "first_weld": {
            "id": "withdraw_payout_clear",
            "write": "withdraw",
            "label": "Withdraw / payout — clear before wire",
            "why": "Named commercial driver edge. Prove fail-closed halt before expanding write coverage.",
            "next_after_prove": "grid_shed_reconnect",
        },
        "ads_floor": {
            "privacy": f"{public_url}/privacy",
            "terms": f"{public_url}/terms",
            "their_production": False,
            "claim": "Checkout starts delivery — not a third-party production claim until recorded L4 weld.",
        },
        "contract_json": f"{public_url}/.well-known/operator.json",
        "register_json": f"{public_url}/.well-known/register.json",
    }


def render_one_pager(public_url: str, contact_email: str) -> str:
    """Forwardable operator clearance summary for counsel / ops."""
    base = (public_url or "").rstrip("/")
    return f"""GATE — OPERATOR CLEARANCE ONE-PAGER
================================
Nisaba LLC · {contact_email} · {base}

WHAT IT IS
  Clearance before irreversible withdraw, payout, or bind.
  Fail closed under uncertainty. Independent verify. Licensed operators only.

CHECKOUT
  Weld:       {WELD_PRICE_LABEL} one-time — one irreversible write (48hr delivery)
  Management: {FLOOR_PRICE_LABEL} per welded path + per active parent license
  Flow:       {BPS} bps on cleared + {BPS_CARRY} bps above ${HURDLE_CLEARED_CENTS // 100_000_000}/mo
  Checkout:   {base}/operator
  Honesty:    their_production stays false until a recorded third-party production weld

PROOF
  Fees:    {base}/register
  Specs:   {base}/.well-known/operator.json · register.json · legal.json
  Legal:   {base}/privacy · {base}/terms
  Verify:  https://velaru.xyz/verify

REFUSE
  Unlicensed gambling · second write in same weld · PII on hop · forged production claims

Not legal advice. Licensed operators only.
"""


