"""One-page bind weld offer — buyer profile, 48hr deliverables, economics.

Forwardable by counsel/ops. Product-led entry to operator checkout (bind_only write).
"""
from __future__ import annotations

try:
    from gate import operator_invoice as operator_mod
except ImportError:
    import operator_invoice as operator_mod

SPEC = "gate-bind-weld-offer-v1"

BUYER_PROFILE = {
    "title": "Who this is for",
    "fit": [
        "MGA or insurtech on Guidewire PolicyCenter or Duck Creek with live bind-only API",
        "Surplus / E&S shop where one unauthorized bind = immediate E&O exposure",
        "Cyber, GL, or small commercial lines binding $1M+ premium/month through PAS",
        "CUO or bind-desk owner who must show examiners a stop that holds (CO 10-1-1 / NYDFS CL7)",
    ],
    "not_fit": [
        "Rating / ECDIS model vendors (Gate is control, not a score)",
        "Agent x402 micropay experiments",
        "Teams without a named bind-path owner this quarter",
    ],
}

ECONOMICS = (
    {
        "label": "Modest MGA",
        "cleared_month": "$5M premium/mo through gate",
        "cleared_cents": 500_000_000,
        "welded_writes": 1,
        "live_parents": 0,
    },
    {
        "label": "Mid MGA",
        "cleared_month": "$20M premium/mo",
        "cleared_cents": 2_000_000_000,
        "welded_writes": 1,
        "live_parents": 2,
    },
    {
        "label": "Scale",
        "cleared_month": "$100M premium/mo",
        "cleared_cents": 10_000_000_000,
        "welded_writes": 1,
        "live_parents": 5,
    },
)

DELIVERABLES_48HR = [
    {
        "id": "hop",
        "title": "Pre-bind hop on your write path",
        "detail": "POST fuse hop before bind-only. DEAD → raise Manual UW issue (BlocksBind). No bind-and-issue bypass.",
    },
    {
        "id": "door",
        "title": "Exclusive door on your origin",
        "detail": "Cloudflare worker or Gosu so bind POST cannot skip the hop. One married write per ticket.",
    },
    {
        "id": "drill",
        "title": "DEAD drill + verify permalink",
        "detail": "Stranger-openable receipt per job_id. Appendix B schema for examiners on request.",
    },
    {
        "id": "register",
        "title": "Flow register armed",
        "detail": f"{operator_mod.BPS} bps on cleared bind premium + management leg live after weld.",
    },
]


def economics_rows() -> list[dict]:
    rows = []
    for row in ECONOMICS:
        reg = operator_mod.register_invoice(
            cleared_cents=row["cleared_cents"],
            hop_count=0,
            welded_writes=row["welded_writes"],
            live_parents=row["live_parents"],
        )
        upfront = operator_mod.WELD_PRICE_CENTS
        rows.append(
            {
                "label": row["label"],
                "cleared_month": row["cleared_month"],
                "upfront_weld": operator_mod.WELD_PRICE_LABEL,
                "monthly_register": reg["total"],
                "management": reg["management"]["total"],
                "flow": reg["flow"]["billed"],
                "annual_register": f"${reg['total_cents'] * 12 / 100:,.0f}/yr at steady volume",
            }
        )
    return rows


def offer(public_url: str, contact_email: str, *, bind_room_price: str, install_price: str) -> dict:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "headline": "Bind cannot complete unless the fuse is LIVE.",
        "one_liner": (
            "External clearance on PolicyCenter bind-only — the only door on one irreversible write. "
            "Not agent payments. Not a rating model."
        ),
        "pricing": {
            "weld": operator_mod.WELD_PRICE_LABEL,
            "management_per_mouth": operator_mod.FLOOR_PRICE_LABEL,
            "flow_bps": operator_mod.BPS,
            "carry_bps_above_hurdle": operator_mod.BPS_CARRY,
            "hurdle_cleared_month": f"${operator_mod.HURDLE_CLEARED_CENTS // 100_000_000}/mo",
            "entry_bind_room": bind_room_price,
            "entry_install": install_price,
        },
        "buyer": BUYER_PROFILE,
        "deliverables_48hr": DELIVERABLES_48HR,
        "economics": economics_rows(),
        "path": {
            "fast": f"{base}/bind-room → officer pack → {base}/operator?write=bind_only",
            "direct": f"{base}/operator?write=bind_only",
            "proof": [
                f"POST {base}/demo/pas/policycenter/pre-bind",
                f"POST {base}/demo/pas/bind-check",
                f"GET {base}/bind-room/officer-pack.json",
            ],
        },
        "checkout": f"{base}/operator?write=bind_only",
        "contact": contact_email,
        "operator": "Nisaba LLC",
        "patent": "64/124,027 (provisional)",
        "honesty": {
            "their_production": False,
            "note": "Checkout starts delivery — not a third-party production claim until L4 weld recorded.",
        },
    }


def render_one_pager(public_url: str, contact_email: str, *, bind_room_price: str, install_price: str) -> str:
    base = (public_url or "").rstrip("/")
    econ = economics_rows()
    lines = [
        "GATE — BIND WELD ONE-PAGER",
        "==========================",
        f"Nisaba LLC · {contact_email} · {base}",
        "",
        "ONE LINE",
        "  Bind cannot complete unless the fuse is LIVE. DEAD → BlocksBind. One door.",
        "",
        "WHO",
    ]
    for item in BUYER_PROFILE["fit"]:
        lines.append(f"  ✓ {item}")
    lines.extend(
        [
            "",
            "PRICING",
            f"  Weld (48hr):     {operator_mod.WELD_PRICE_LABEL} one-time — bind-only write",
            f"  Management:      {operator_mod.FLOOR_PRICE_LABEL} per welded path + per LIVE parent",
            f"  Flow:            {operator_mod.BPS} bps cleared (+{operator_mod.BPS_CARRY} above ${operator_mod.HURDLE_CLEARED_CENTS // 100_000_000}/mo)",
            f"  Entry (optional): {bind_room_price} Bind Room officer pack · {install_price} agent install",
            "",
            "48 HOURS AFTER CHECKOUT",
        ]
    )
    for d in DELIVERABLES_48HR:
        lines.append(f"  · {d['title']}: {d['detail']}")
    lines.extend(["", "ECONOMICS (illustrative, one bind mouth)"])
    for row in econ:
        lines.append(
            f"  {row['label']}: {row['cleared_month']} → {row['monthly_register']}/mo register "
            f"({row['management']} mgmt + {row['flow']} flow) · {row['annual_register']}"
        )
    lines.extend(
        [
            "",
            "PROOF (no key)",
            f"  curl -s -X POST {base}/demo/pas/policycenter/pre-bind -H 'Content-Type: application/json' -d '{{\"fuse_id\":\"fuse_velaru_drill\",\"job_id\":\"pc:DEMO\"}}'",
            f"  Officer pack: {base}/bind-room/officer-pack.json",
            "",
            "CHECKOUT",
            f"  {base}/operator?write=bind_only",
            "",
            "Not legal advice. Licensed operators only.",
        ]
    )
    return "\n".join(lines) + "\n"
