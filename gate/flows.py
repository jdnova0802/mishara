"""Act and flow rents — seated, priced, protocol-only, and holes.

A register, not a sixth sibling. Not a /for/ plate.
$0 until Gate 1 on every meter. Never sell may. Never run a facilitator.

Priced act rents (keep-alive · query · silence) checkout on /acts.
This page stays the map.
"""
from __future__ import annotations

from typing import Any

try:
    from gate import inventor as inventor_mod
except ImportError:
    import inventor as inventor_mod

SPEC = "gate-act-flow-rents-v1"
FAMILY_SIBLINGS_REMAIN = 5
L2_MODULE = False
CLEVERER_LAYER = None

SEATED: tuple[dict[str, Any], ...] = (
    {
        "id": "hop",
        "name": "$0.10/hop",
        "on": "irreversible hop",
        "kind": "flow",
        "door": "/operator",
        "until_gate1_usd": 0,
    },
    {
        "id": "bps",
        "name": "10 bps + 5 carry above $500M/mo",
        "on": "cleared flow",
        "kind": "flow",
        "door": "/operator",
        "until_gate1_usd": 0,
    },
    {
        "id": "floor",
        "name": "$5,000/mo floor",
        "on": "max(floor, bps, hop)",
        "kind": "flow",
        "door": "/operator",
        "until_gate1_usd": 0,
    },
    {
        "id": "qic",
        "name": "QIC max(MAR, LAQ × rate)",
        "on": "redeem consume + irreversible write",
        "kind": "act",
        "door": "/conformant",
        "until_gate1_usd": 0,
    },
    {
        "id": "standing",
        "name": "Standing Remaining",
        "on": "operated remaining kept true",
        "kind": "act_adjacent",
        "door": "/standing",
        "until_gate1_usd": 0,
    },
)

PRICED: tuple[dict[str, Any], ...] = (
    {
        "id": "prefinality_keepalive",
        "name": "Prefinality keep-alive",
        "on": "unspent may (TTL 300s)",
        "kind": "act",
        "door": "/acts",
        "label": "$1,200/mo",
        "until_gate1_usd": 0,
    },
    {
        "id": "query_remaining",
        "name": "Query of remaining",
        "on": "the ask after the act",
        "kind": "after_act",
        "door": "/acts",
        "label": "$2,000/mo",
        "until_gate1_usd": 0,
    },
    {
        "id": "silence_lease",
        "name": "Silence lease",
        "on": "named anti-act",
        "kind": "anti_act",
        "door": "/acts",
        "label": "$1,500/mo",
        "until_gate1_usd": 0,
    },
)

PROTOCOL: tuple[dict[str, Any], ...] = (
    {"id": "prefinality", "file": "prefinality.py", "missing": "per-evaluate still unpaid — keep-alive is rented"},
    {"id": "settlement", "file": "settlement.py", "missing": "per-window · per-clear · default-fund"},
    {"id": "pvp", "file": "pvp.py", "missing": "both-or-neither close fee"},
    {"id": "apostille", "file": "first.py", "missing": "per-act stranger seal"},
    {"id": "folio", "file": "remaining.py", "missing": "query is rented; prove-verify is not"},
    {"id": "x402", "file": "x402_challenge.py", "missing": "authenticity stamp — not facilitator"},
    {"id": "license_fuse", "file": "license_fuse.py", "missing": "cascade rent on LIVE children"},
    {"id": "restraint", "file": "restraint.py", "missing": "HALT-as-billable"},
    {"id": "named_may", "file": "named_may.py", "missing": "naming fee · S6 employment $/agent/mo"},
    {"id": "exclusion", "file": "exclusion.py", "missing": "exclusion folio as a priced open"},
    {"id": "epoch", "file": "epoch.py", "missing": "epoch pin / now-door rent"},
    {"id": "counterpart", "file": "counterpart.py", "missing": "dual-redeem close fee (PvP cousin)"},
)

HOLES: tuple[dict[str, Any], ...] = (
    {"id": "scheme_assessment", "name": "Scheme assessment", "on": "act", "why": "Network % distinct from desk 10 bps. Visa stacks this."},
    {"id": "per_clear", "name": "Per-clear / window fee", "on": "flow", "why": "settlement.py unpaid."},
    {"id": "regret", "name": "Dispute / regret fee", "on": "act", "why": "Chargeback energy for machine acts."},
    {"id": "interchange", "name": "May interchange (S1)", "on": "flow", "why": "bps of GMV that cannot settle without may. Do not sell from Bind."},
    {"id": "x402_stamp", "name": "x402 authenticity stamp", "on": "act", "why": "Remaining of the payment. Never run the facilitator."},
    {"id": "halt_billable", "name": "HALT-as-billable", "on": "anti_act", "why": "The no is free today."},
    {"id": "index_license", "name": "May reference rate (T2)", "on": "after_act", "why": "SOFR-class cite on E&O / SLA / credit."},
    {"id": "attest_franchise", "name": "Attestation franchise (T4)", "on": "after_act", "why": "Royalty on SOC / 10-K agent posture + feed seats."},
    {"id": "must_mouth", "name": "Must-mouth (T3)", "on": "attach", "why": "Multiplier, not a SKU. Language until a rule."},
    {"id": "trinity_close", "name": "Trinity close", "on": "act", "why": "Paid + said + wrote as one priced close."},
    {"id": "edition_pin", "name": "Edition pin of record", "on": "act", "why": "Every act cites a version."},
    {"id": "now_door", "name": "Exclusive now / only-door", "on": "act", "why": "/only is a page. Not a rent."},
    {"id": "fuse_cascade", "name": "Fuse cascade", "on": "flow", "why": "LIVE children unpaid."},
    {"id": "rehearsal_cut", "name": "Rehearsal ≠ spend cut", "on": "act", "why": "Labs pay for the ontological cut."},
    {"id": "ccp_default_fund", "name": "CCP default fund", "on": "flow", "why": "Waterfall exists. Contribution does not."},
    {"id": "named_may_employment", "name": "Named may employment (S6)", "on": "fleet", "why": "$/agent/mo. Doctrine named; missed on the first 18."},
    {"id": "multi_rail", "name": "Prefinality multi-rail (S2)", "on": "act", "why": "Second-rail surcharge. One mouth in front of every pay protocol."},
    {"id": "auth_capture_settle", "name": "Authorize / capture / settle", "on": "act", "why": "Visa bills the same payment three times. We have one hop."},
    {"id": "cross_rail_fx", "name": "Cross-rail / FX spread", "on": "flow", "why": "Named in stacked doctrine. Not a hole id until now."},
    {"id": "retry_surcharge", "name": "Retry / fail LIVE surcharge", "on": "act", "why": "A LIVE hop that fails still costs energy."},
    {"id": "unwind", "name": "Refund / void / unwind", "on": "act", "why": "The reverse of the hop. No fee on taking it back."},
    {"id": "priority_window", "name": "Priority / same-window premium", "on": "flow", "why": "Same-day energy. settlement.py has windows, no rush price."},
    {"id": "custody_stock_bps", "name": "Custody bps on stock (T1)", "on": "stock", "why": "DTCC of remaining. Recurring on immobilized one-wayness, not flow."},
    {"id": "hyperscaler_sheath", "name": "Hyperscaler sheath default (T5)", "on": "act", "why": "Write gate before irreversible I/O on AWS / Azure / GCP."},
    {"id": "prove_verify", "name": "Prove verification", "on": "after_act", "why": "Stranger opens the stock. Query rents the ask; verify is the open."},
    {"id": "death_certificate", "name": "Capability death certificate", "on": "anti_act", "why": "This may died unused. first.py names it. Nobody pays the certificate."},
    {"id": "named_may_fee", "name": "Naming fee", "on": "act", "why": "Bearer → named. The act of naming is unpaid."},
)

NOT_SKU: tuple[dict[str, Any], ...] = (
    {"id": "u7_estate", "name": "Estate of remaining (U7)", "why": "Probate of one-wayness. Unification, not an act rent."},
    {"id": "u12_duty", "name": "Duty-remaining (U12)", "why": "May-spend creates obligation stock. Correspondent duty, not a hop."},
    {"id": "u14_sealed", "name": "Sealed-time redeem (U14)", "why": "May that burns if not spent at T. Name only until Gate 1."},
    {"id": "u15_veto", "name": "Inhabitant veto stock (U15)", "why": "Those who live in the remaining hold the no. Not Being."},
    {"id": "u4_market", "name": "Anti-act market (U4)", "why": "Silence lease is one named no. The market is class-ban stock."},
)

NEVER: tuple[str, ...] = (
    "Connect splits",
    "x402 facilitator take-rate",
    "selling may",
    "Being as a SKU",
    "interest on customer float",
)

NEXT_AFTER_GATE1 = ("scheme_assessment", "per_clear")


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Act and flow rents",
        "inventor": inventor_mod.stamp(),
        "thesis": (
            "We have an acquirer stub: hop + bps + floor + QIC. "
            "Keep-alive, query, and silence lease now have a mouth. "
            "A network still charges the same act several more times."
        ),
        "seated": [dict(x) for x in SEATED],
        "priced": [dict(x) for x in PRICED],
        "protocol_unpaid": [dict(x) for x in PROTOCOL],
        "holes": [dict(x) for x in HOLES],
        "not_a_sku": [dict(x) for x in NOT_SKU],
        "never": list(NEVER),
        "next_after_gate1": list(NEXT_AFTER_GATE1),
        "family_siblings_remain": FAMILY_SIBLINGS_REMAIN,
        "l2_module": L2_MODULE,
        "cleverer_layer": CLEVERER_LAYER,
        "until_gate1_usd": 0,
        "not_museum": True,
        "cash_door": f"{base}/acts",
        "page": f"{base}/flows",
        "links": {
            "page": f"{base}/flows",
            "acts": f"{base}/acts",
            "operator": f"{base}/operator",
            "standing": f"{base}/standing",
            "hand": f"{base}/hand",
            "prefinality": f"{base}/.well-known/prefinality.json",
        },
        "gatekeep": "Register of act/flow rents. Not a buyer plate. Priced three checkout on /acts.",
    }
