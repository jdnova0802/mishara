"""Agentic stack: identity / payment / evidence. Reference page, not a SKU.

Statuses as of 16 Nov 2026. Shipping = live in production use.
Draft = published spec or WG I-D, not an RFC. Proposed = charter, announcement,
or individual draft with no shippable wire.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-evidence-layer-v1"
AS_OF = "2026-11-16"
PATH = "/evidence-layer"

# Tags allowed on the diagram.
SHIPPING = "shipping"
DRAFT = "draft"
PROPOSED = "proposed"

LANES: list[dict[str, Any]] = [
    {
        "id": "identity",
        "title": "Identity",
        "flow": "who",
        "entries": [
            {
                "name": "WIMSE",
                "tag": DRAFT,
                "note": "IETF WG. Architecture + identifier drafts; HTTP signatures with IESG.",
                "href": "https://datatracker.ietf.org/group/wimse/about/",
            },
            {
                "name": "OAuth CIMD",
                "tag": DRAFT,
                "note": "draft-ietf-oauth-client-id-metadata-document-03 (2 Nov 2026).",
                "href": "https://datatracker.ietf.org/doc/draft-ietf-oauth-client-id-metadata-document/",
            },
            {
                "name": "DAWN",
                "tag": PROPOSED,
                "note": "IETF WG chartered 22 Oct 2026. Discovery, not auth.",
                "href": "https://datatracker.ietf.org/doc/charter-ietf-dawn/",
            },
            {
                "name": "draft-klrc-aiagent-auth",
                "tag": DRAFT,
                "note": "Informational I-D -03. Expires 7 Jan 2027.",
                "href": "https://datatracker.ietf.org/doc/html/draft-klrc-aiagent-auth",
            },
        ],
    },
    {
        "id": "payment",
        "title": "Payment",
        "flow": "how it paid",
        "entries": [
            {
                "name": "ACP",
                "tag": SHIPPING,
                "note": "OpenAI/Stripe. Instant Checkout; radar still says beta/evolving.",
                "href": "https://www.agenticcommerce.dev/",
            },
            {
                "name": "UCP",
                "tag": SHIPPING,
                "note": "Google/Shopify. AI Mode / Gemini checkout, beta/evolving.",
                "href": "https://developers.google.com/merchant/ucp",
            },
            {
                "name": "AP2",
                "tag": DRAFT,
                "note": "FIDO-held spec (Apr 2026). Mandates, not a rail.",
                "href": "https://ap2-protocol.org/",
            },
            {
                "name": "x402",
                "tag": SHIPPING,
                "note": "HTTP 402. x402 Foundation; Coinbase/Stripe facilitators.",
                "href": "https://x402.org/",
            },
            {
                "name": "MPP",
                "tag": DRAFT,
                "note": "Stripe/Tempo machine payments. Beta/evolving.",
                "href": "https://docs.stripe.com/payments/machine",
            },
            {
                "name": "TAP",
                "tag": DRAFT,
                "note": "Visa Trusted Agent Protocol. Docs live; early production.",
                "href": "https://developer.visa.com/capabilities/trusted-agent-protocol/overview",
            },
            {
                "name": "Mastercard Agent Pay",
                "tag": SHIPPING,
                "note": "Network program + tokens. Not an open spec.",
                "href": "https://www.mastercard.com/us/en/business/artificial-intelligence/mastercard-agent-pay.html",
            },
        ],
    },
    {
        "id": "evidence",
        "title": "Evidence",
        "flow": "what happened",
        "entries": [
            {
                "name": "Hive Transparency Log",
                "tag": SHIPPING,
                "note": "Live RFC 9162-style log + COSE at witness.thehiveryiq.com.",
                "href": "https://thehiveryiq.com/ct/",
            },
            {
                "name": "draft-hood-agtp-log",
                "tag": DRAFT,
                "note": "AGTP-LOG-03 informational. Expires 3 May 2027.",
                "href": "https://datatracker.ietf.org/doc/draft-hood-agtp-log/",
            },
            {
                "name": "Agent Record",
                "tag": DRAFT,
                "note": "draft-maintainer-1f916-agent-record-01. Individual I-D.",
                "href": "https://datatracker.ietf.org/doc/draft-maintainer-1f916-agent-record/",
            },
            {
                "name": "Gate",
                "tag": SHIPPING,
                "note": "Live Ed25519 receipts at /v1/prefinality/verify. Not production-hardened.",
                "href": "/v1/prefinality/verify",
                "self": True,
            },
        ],
    },
]

COMPARISONS = [
    {
        "title": "ATXP — every agent payment protocol compared",
        "href": "https://atxp.ai/blog/agent-payment-protocols-compared/",
    },
    {
        "title": "ACP Info — protocol status radar",
        "href": "https://agenticcommerceprotocol.info/radar",
    },
    {
        "title": "kya.fi — standards & regulation tracker",
        "href": "https://kya.fi/standards-tracker/",
    },
]


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    lanes = []
    for lane in LANES:
        entries = []
        for it in lane["entries"]:
            href = it["href"]
            if it.get("self") and href.startswith("/"):
                href = f"{base}{href}"
            entries.append({**it, "href": href})
        lanes.append({**lane, "entries": entries})
    return {
        "spec": SPEC,
        "as_of": AS_OF,
        "path": PATH,
        "page": f"{base}{PATH}",
        "lanes": lanes,
        "comparisons": COMPARISONS,
        "not_a_sku": True,
        "production_hardened": False,
        "plain": (
            "Identity and payment are mapped in public. Evidence is the missing axis. "
            "Gate's receipts are live and stranger-verifiable; they are not a production standard."
        ),
    }
