"""Act and flow rents — seated, protocol-only, and holes.

A register, not a new meter. Not a sixth sibling. Not a /for/ plate.
$0 until Gate 1 on every meter. Never sell may. Never run a facilitator.
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

PROTOCOL: tuple[dict[str, Any], ...] = (
    {"id": "prefinality", "file": "prefinality.py", "missing": "per-evaluate · keep-alive on unspent may"},
    {"id": "settlement", "file": "settlement.py", "missing": "per-window · per-clear · default-fund"},
    {"id": "pvp", "file": "pvp.py", "missing": "both-or-neither close fee"},
    {"id": "apostille", "file": "first.py", "missing": "per-act stranger seal"},
    {"id": "folio", "file": "remaining.py", "missing": "query of the world after"},
    {"id": "x402", "file": "x402_challenge.py", "missing": "authenticity stamp — not facilitator"},
    {"id": "license_fuse", "file": "license_fuse.py", "missing": "cascade rent on LIVE children"},
    {"id": "restraint", "file": "restraint.py", "missing": "HALT-as-billable"},
)

HOLES: tuple[dict[str, Any], ...] = (
    {"id": "scheme_assessment", "name": "Scheme assessment", "on": "act", "why": "Network % distinct from desk 10 bps. Visa stacks this."},
    {"id": "prefinality_keepalive", "name": "Prefinality keep-alive", "on": "unspent may", "why": "TTL refresh. Recurring on the act before flow."},
    {"id": "per_clear", "name": "Per-clear / window fee", "on": "flow", "why": "settlement.py unpaid."},
    {"id": "regret", "name": "Dispute / regret fee", "on": "act", "why": "Chargeback energy for machine acts."},
    {"id": "query_remaining", "name": "Query of remaining", "on": "after_act", "why": "Pay to ask what happened, not to write."},
    {"id": "interchange", "name": "May interchange (S1)", "on": "flow", "why": "bps of GMV that cannot settle without may."},
    {"id": "x402_stamp", "name": "x402 authenticity stamp", "on": "act", "why": "Remaining of the payment. Never run the facilitator."},
    {"id": "silence_lease", "name": "Silence lease", "on": "anti_act", "why": "Refusal is $7,500 once. Boards would pay yearly."},
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
)

NEVER: tuple[str, ...] = (
    "Connect splits",
    "x402 facilitator take-rate",
    "selling may",
    "Being as a SKU",
    "interest on customer float",
)

NEXT_AFTER_GATE1 = ("prefinality_keepalive", "query_remaining")


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Act and flow rents",
        "inventor": inventor_mod.stamp(),
        "thesis": (
            "We have an acquirer stub: hop + bps + floor + QIC. "
            "A network charges the same act several times. The rest is hole."
        ),
        "seated": [dict(x) for x in SEATED],
        "protocol_unpaid": [dict(x) for x in PROTOCOL],
        "holes": [dict(x) for x in HOLES],
        "never": list(NEVER),
        "next_after_gate1": list(NEXT_AFTER_GATE1),
        "family_siblings_remain": FAMILY_SIBLINGS_REMAIN,
        "l2_module": L2_MODULE,
        "cleverer_layer": CLEVERER_LAYER,
        "until_gate1_usd": 0,
        "not_museum": True,
        "cash_door": f"{base}/operator",
        "page": f"{base}/flows",
        "links": {
            "page": f"{base}/flows",
            "operator": f"{base}/operator",
            "standing": f"{base}/standing",
            "hand": f"{base}/hand",
            "prefinality": f"{base}/.well-known/prefinality.json",
        },
        "gatekeep": "Register of act/flow rents. Not a buyer plate. Cash is still /operator.",
    }
