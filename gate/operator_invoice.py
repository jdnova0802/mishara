"""Operator invoice — the money machine next to the weld.

The product is the only door x 10 bps x volume through that door.
Bill max(floor, bps, per-hop) so a quiet door still pays. The floor is not the check.
One write per weld. Licensed payout / bind only. Not a second engine.
"""
from __future__ import annotations

SPEC = "gate-operator-invoice-v1"
WELD_PRICE_LABEL = "$25,000"
WELD_PRICE_CENTS = 2_500_000
FLOOR_PRICE_LABEL = "$5,000/mo"
FLOOR_PRICE_CENTS = 500_000
BPS = 10
HOP_CENTS = 10  # $0.10
EXTRA_WRITE_CENTS = WELD_PRICE_CENTS

# Annual cleared flow through the door → Gate's 10 bps cut (cents).
# The floor is a quiet-door minimum. These rows are the actual check.
YEAR_SCALE = (
    {"cleared_cents": 10_000_000_000, "through": "$100M"},       # $100k
    {"cleared_cents": 100_000_000_000, "through": "$1B"},        # $1M
    {"cleared_cents": 1_000_000_000_000, "through": "$10B"},     # $10M
    {"cleared_cents": 10_000_000_000_000, "through": "$100B"},   # $100M
    {"cleared_cents": 100_000_000_000_000, "through": "$1T"},    # $1B
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


def invoice(
    *,
    cleared_cents: int = 0,
    hop_count: int = 0,
    floor_cents: int = FLOOR_PRICE_CENTS,
    bps: int = BPS,
    hop_cents: int = HOP_CENTS,
) -> dict:
    """Bill the max of floor, bps of cleared flow, and per-hop."""
    cleared = max(0, int(cleared_cents))
    hops = max(0, int(hop_count))
    floor_amt = max(0, int(floor_cents))
    bps_amt = (cleared * int(bps)) // 10_000
    hop_amt = hops * int(hop_cents)
    billed = max(floor_amt, bps_amt, hop_amt)
    legs = {"floor": floor_amt, "bps": bps_amt, "per_hop": hop_amt}
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
        "formula": "max(floor, bps of cleared, per-hop)",
    }


def bps_cents(cleared_cents: int, bps: int = BPS) -> int:
    return (max(0, int(cleared_cents)) * int(bps)) // 10_000


def year_scale(*, bps: int = BPS) -> list[dict]:
    """How the check gets large. Not a forecast. 10 bps of what actually clears."""
    rows = []
    for row in YEAR_SCALE:
        gate = bps_cents(row["cleared_cents"], bps=bps)
        rows.append(
            {
                "through": row["through"],
                "cleared_cents": row["cleared_cents"],
                "bps": int(bps),
                "gate_cents": gate,
                "gate": f"${gate / 100:,.0f}",
            }
        )
    return rows


def manifest(public_url: str, contact_email: str) -> dict:
    return {
        "spec": SPEC,
        "page": f"{public_url}/register",
        "checkout": f"{public_url}/operator",
        "operator": "Nisaba LLC",
        "contact": contact_email,
        "not_a_new_engine": True,
        "one_write_per_weld": True,
        "their_production": False,
        "licensed_only": True,
        "thesis": {
            "default": "the only door on one irreversible write",
            "bps": BPS,
            "volume": "cleared flow through that door",
            "product": "default x bps x volume",
            "not_the_product": "the $5,000/mo quiet-door minimum",
        },
        "refuse": [
            "unlicensed / offshore gambling",
            "second married write in the same weld",
            "PII on the hop",
        ],
        "skus": {
            "weld": {
                "label": WELD_PRICE_LABEL,
                "amount_cents": WELD_PRICE_CENTS,
                "kind": "one_time",
                "deliverable": "one production write fail-closed in 48hr",
            },
            "floor": {
                "label": FLOOR_PRICE_LABEL,
                "amount_cents": FLOOR_PRICE_CENTS,
                "kind": "monthly",
                "deliverable": "usage floor so a quiet door cannot pay like a toy. Not the check.",
            },
            "extra_write": {
                "label": WELD_PRICE_LABEL,
                "amount_cents": EXTRA_WRITE_CENTS,
                "kind": "one_time",
                "deliverable": "second socket (in / middle / out) after the first weld is live",
            },
        },
        "invoice": {
            "formula": "max($5,000 floor, 10 bps of cleared flow, $0.10/hop)",
            "bps": BPS,
            "hop_cents": HOP_CENTS,
            "floor_cents": FLOOR_PRICE_CENTS,
            "quiet_month": invoice(cleared_cents=120_000_000, hop_count=8_000),
            "example": invoice(cleared_cents=120_000_000, hop_count=8_000),
            "year": year_scale(),
        },
        "writes": list(WRITES.values()),
        "checkout": f"{public_url}/operator",
        "contract_json": f"{public_url}/.well-known/operator.json",
        "register_json": f"{public_url}/.well-known/register.json",
    }
