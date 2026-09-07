"""Hustle 1 — Mouth / finality diligence.

One-pager + deposit SKU. Finds where an irreversible write can complete without may.
Not a weld. Not Bind Room. Not production clearance.
"""
from __future__ import annotations

SPEC = "gate-diligence-offer-v1"
INVENTOR = "Nisaba LLC / Gate"

# Display defaults (app.py may override via env for checkout cents)
REVIEW_PRICE_LABEL = "$5,000"
DEPOSIT_PRICE_LABEL = "$2,500"
RETAINER_BAND = "$10,000–$40,000/mo"
REVIEW_BAND = "$5,000–$8,000"


def offer(
    public_url: str,
    contact_email: str,
    *,
    review_price: str = REVIEW_PRICE_LABEL,
    deposit_price: str = DEPOSIT_PRICE_LABEL,
) -> dict:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "inventor": INVENTOR,
        "name": "Mouth / finality diligence",
        "headline": "Where can an irreversible write complete without may?",
        "subhead": (
            "72-hour edge review for payout, peg-out/bridge, settlement finality, "
            "custody quorum, and nested payment rails. Deposit starts the clock. "
            "Not a weld. Not production clearance."
        ),
        "price": {
            "review": review_price,
            "review_band": REVIEW_BAND,
            "deposit": deposit_price,
            "deposit_note": "50% deposit due now · remainder on delivery",
            "retainer_band": RETAINER_BAND,
            "delivery": "72 hours from cleared deposit",
        },
        "surfaces": [
            "payout / withdraw release",
            "peg-out / bridge finality",
            "settlement edge (DvP / PvP-shaped)",
            "custody quorum / key ceremony",
            "correspondent nesting / payable-through / BaaS sponsor edges",
            "industrial MAY literacy (PTW / LOTO / SIS / MOC) when relevant",
        ],
        "deliverables": [
            "Edge map: where irreversible writes can complete without may",
            "Fail-closed gaps (omit paths, TOCTOU, parallel doors)",
            "Ranked fixes → exclusive door / fuse / CHARGE posture",
            "Stranger-verifiable receipt pointers where Gate already proves",
            "Optional Bind Room upsell path for examiner packs",
        ],
        "not": [
            "Not a production weld (see /operator)",
            "Not an insurance binder or standing write",
            "Not a self-bounty / grey disclosure stunt",
            "Not agent-gateway SaaS theater",
        ],
        "cta": {
            "page": f"{base}/diligence",
            "deposit_checkout": f"{base}/diligence/checkout",
            "one_pager": f"{base}/diligence/one-pager.txt",
            "manifest": f"{base}/diligence/offer.json",
            "bind_room": f"{base}/bind-room",
            "contact": contact_email,
        },
        "their_production": False,
    }


def render_one_pager(
    public_url: str,
    contact_email: str,
    *,
    review_price: str = REVIEW_PRICE_LABEL,
    deposit_price: str = DEPOSIT_PRICE_LABEL,
) -> str:
    o = offer(
        public_url,
        contact_email,
        review_price=review_price,
        deposit_price=deposit_price,
    )
    surfaces = "\n".join(f"  - {s}" for s in o["surfaces"])
    delivers = "\n".join(f"  - {d}" for d in o["deliverables"])
    nots = "\n".join(f"  - {n}" for n in o["not"])
    return f"""GATE — MOUTH / FINALITY DILIGENCE
{o["headline"]}

{o["subhead"]}

PRICE
  Review:  {o["price"]["review"]} (band {o["price"]["review_band"]})
  Deposit: {o["price"]["deposit"]} due now — {o["price"]["deposit_note"]}
  Retainer:{o["price"]["retainer_band"]}
  Delivery:{o["price"]["delivery"]}

SURFACES
{surfaces}

YOU GET
{delivers}

NOT
{nots}

START
  Page:    {o["cta"]["page"]}
  Deposit: {o["cta"]["deposit_checkout"]} (POST email)
  Pack:    {o["cta"]["bind_room"]} (Bind Room · separate SKU)
  Contact: {contact_email}

Nisaba LLC / Gate — DENY that holds. Proof lifts deploy. Weld flips production.
"""


def manifest(
    public_url: str,
    contact_email: str,
    *,
    review_price: str = REVIEW_PRICE_LABEL,
    deposit_price: str = DEPOSIT_PRICE_LABEL,
) -> dict:
    return offer(
        public_url,
        contact_email,
        review_price=review_price,
        deposit_price=deposit_price,
    )
