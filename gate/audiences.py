"""Audience plates — one door per buyer type. Boring clearance language. No emoji."""
from __future__ import annotations

VELARU_PUBLIC = "https://velaru.xyz"

# slug → plate config
PLATES: dict[str, dict] = {
    "developers": {
        "emoji": "",
        "title": "Developers",
        "headline": "Can this write still execute right now?",
        "subhead": "Lab fuse hop for drills. Fail closed + verify URL. Production is a paid operator weld.",
        "pain": "You're building agent loops without a halt that strangers can verify.",
        "offer": "Hop docs · public demo · production = operator weld",
        "price": "Lab drills · weld for production",
        "cta_label": "Pricing",
        "cta_route": "pricing",
        "secondary_label": "Hop docs",
        "secondary_route": "docs",
        "proof": "Hop demo · openapi.json",
        "tags": ["api", "curl", "hn", "lab"],
    },
    "agents": {
        "emoji": "",
        "title": "Agent builders",
        "headline": "Pre-exec clearance for autonomous agents",
        "subhead": "Hop before commit. Fail closed if clearance fails. Soft prompt policy is not clearance.",
        "pain": "Your agent can still act after you thought you stopped it.",
        "offer": "Lab hop + /.well-known/gate.json · production weld for irreversible writes",
        "price": "Lab drills · weld for production",
        "cta_label": "Weld a path",
        "cta_route": "operator_page",
        "secondary_label": "Agent manifest",
        "secondary_href": "/.well-known/gate.json",
        "proof": "POST /v1/fuse/hop → verify_url in response",
        "tags": ["mcp", "x402", "agents"],
    },
    "startups": {
        "emoji": "",
        "title": "Startups",
        "headline": "48hr agent fuse wiring",
        "subhead": "One pre-exec fuse wired. Fail-closed demo with verify. Lab path only. Production = weld.",
        "pain": "You need proof of control before the board meeting — not another sprint of infra.",
        "offer": "One agent path wired + handoff · production weld separate",
        "price": "One-time wiring",
        "cta_label": "Book agent wiring",
        "cta_route": "install",
        "secondary_label": "Pricing",
        "secondary_route": "pricing",
        "proof": "Fail-closed verify demo on delivery",
        "tags": ["install", "speed", "fundraise"],
    },
    "operators": {
        "emoji": "",
        "title": "Operators",
        "headline": "Clearance before withdraw, payout, or bind",
        "subhead": "Fail closed under uncertainty. Parent license revoked blocks child spend. 10 bps of cleared flow + monthly path management. Licensed only.",
        "pain": "Calculators and agent installs do not sit on payout or bind. Narrative without a halt is not infrastructure.",
        "offer": "One production write fail-closed in 48hr. Extra write = another weld. Independent verify.",
        "price": "Fee schedule · weld + management + 10 bps",
        "cta_label": "Fee schedule",
        "cta_route": "register_page",
        "secondary_label": "Weld a path",
        "secondary_route": "operator_page",
        "proof": "Fail-closed hop on their write. Independent verify. No PII. their_production false until third-party weld.",
        "tags": ["payout", "withdraw", "bind", "bps", "floor"],
    },
    "legal": {
        "emoji": "",
        "title": "Legal & GC",
        "headline": "Prove the write could not run when you said it couldn't",
        "subhead": "Independent verify — no login, no trust-me dashboard.",
        "pain": "Board asks for proof. You have logs. They want independent verification.",
        "offer": "Bind Room assessment · pattern + gate export before bind",
        "price": "$1,750 due now",
        "cta_label": "Start Bind Room",
        "cta_route": "bind_room",
        "secondary_label": "Officer pack JSON",
        "secondary_href": "/bind-room/officer-pack.json",
        "proof": "Officer pack + appendix verify permalinks",
        "tags": ["gc", "fre707", "exhibit", "court"],
    },
    "compliance": {
        "emoji": "",
        "title": "Compliance officers",
        "headline": "Decision-point receipts — not a quarterly PDF",
        "subhead": "Signed clearance receipts at the moment of irreversible action. Bind Room and weld — not a scan product.",
        "pain": "Regulators want proof at decision time. You have policy docs from last year.",
        "offer": "Bind Room · Exhibit pack · session receipts via weld",
        "price": "Assessment from $3,500 · Bind Room $1,750",
        "cta_label": "Open Bind Room",
        "cta_route": "bind_room",
        "secondary_label": "Operator weld",
        "secondary_route": "operator_page",
        "proof": "Independent verify · fail-closed hop · NAIC / EU Art 12 shaped receipts",
        "tags": ["naic", "eu-ai-act", "art12", "audit"],
    },
    "carriers": {
        "emoji": "",
        "title": "Carriers & PAS",
        "headline": "Bind ALLOW/BLOCK with a receipt counsel can open",
        "subhead": "Clearance before irreversible bind. Fail closed. Independent verify. Same hop family as PAS bind-check.",
        "pain": "Bind went through on an agent you can't prove was cleared.",
        "offer": "Bind Room officer pack + PolicyCenter pre-bind weld. Control, not a rating model.",
        "price": "$1,750 Bind Room · $25,000 operator weld",
        "cta_label": "Open Bind Room",
        "cta_route": "bind_room",
        "secondary_label": "Operator weld",
        "secondary_route": "operator_page",
        "proof": "BLOCK → restraint receipt → independent verify",
        "tags": ["insurance", "bind", "pas", "guidewire"],
    },
    "brokers": {
        "emoji": "",
        "title": "Brokers & MGAs",
        "headline": "CG 40 / 47 renewal with proof rail",
        "subhead": "Renewal desk gets verify links — not another AI trust slide deck.",
        "pain": "Carrier wants AI controls proof at renewal. Your insured has nothing clickable.",
        "offer": "MGA delegated-authority gate — premium/line/state + fuse hop before binder",
        "price": "$25,000 operator weld",
        "cta_label": "MGA / Bind Room",
        "cta_route": "bind_room",
        "secondary_label": "Operator weld",
        "secondary_route": "operator_page",
        "proof": "Independent verify · prepaid parent license",
        "tags": ["broker", "renewal", "cg4047"],
    },
    "enterprise": {
        "emoji": "",
        "title": "Enterprise",
        "headline": "One org root — child spend cannot outlive parent",
        "subhead": "Prepaid fuse tree. Fail closed when parent is revoked. Child spend cannot outlive parent.",
        "pain": "Every team built their own kill switch. None of them verify the same way.",
        "offer": "Org root · bind rooms · on-prem option",
        "price": "Program pricing",
        "cta_label": "Enterprise inquiry",
        "cta_mailto": "subject=Enterprise%20%E2%80%94%20Org%20root",
        "secondary_label": "Trust & limits",
        "secondary_route": "trust",
        "proof": "Patent #64/124,027 · hash-chained receipts · parent→child halt",
        "tags": ["enterprise", "procurement", "soc2-path"],
    },
    "boards": {
        "emoji": "",
        "title": "Boards & directors",
        "headline": "Show clearance failed — in one link",
        "subhead": "No AI literacy required. Clearance states with independent verify.",
        "pain": "Director asks: 'Can it still run?' You need an answer in 30 seconds.",
        "offer": "Public check · board-ready verify permalink",
        "price": "Charge packs from $500",
        "cta_label": "Run public check",
        "cta_href": f"{VELARU_PUBLIC}/check",
        "secondary_label": "Trust limits",
        "secondary_route": "trust",
        "proof": "Independent verify free · fail-closed hop",
        "tags": ["board", "directors", "governance"],
    },
    "defense": {
        "emoji": "",
        "title": "Defense & gov",
        "headline": "Fail-closed clearance before irreversible release or disbursement",
        "subhead": "Independent verify. their_production stays false until a recorded third-party weld. No UI resurrection path.",
        "pain": "Delegated autonomy without a stranger-checkable halt fails closed under audit.",
        "offer": "Clearance weld inquiry on a named irreversible write. Export formats only after that weld exists.",
        "price": "Custom · weld required before any production claim",
        "cta_label": "Defense inquiry",
        "cta_mailto": "subject=Defense%20%E2%80%94%20Clearance%20weld",
        "secondary_label": "Trust & limits",
        "secondary_route": "trust",
        "proof": "Fail-closed hop · independent verify · parent→child halt · their_production false until third-party weld",
        "tags": ["dod", "3000.09", "defense", "gov"],
    },
    "hiring": {
        "emoji": "",
        "title": "HR & hiring tech",
        "headline": "Connecticut AEDT hiring proof — Oct 2027 clock",
        "subhead": "Classify + seal hiring decisions with independent verify receipts.",
        "pain": "AEDT audit asks what the agent decided and when. Spreadsheets won't cut it.",
        "offer": "Hiring domain classify · signed receipt · verify URL",
        "price": "Assessment",
        "cta_label": "Pricing",
        "cta_route": "pricing",
        "secondary_label": "CT compliance",
        "secondary_href": f"{VELARU_PUBLIC}/check",
        "proof": "velaru hiring domain · receipt per decision",
        "tags": ["hiring", "aedt", "connecticut", "hr"],
    },
    "consumers": {
        "emoji": "",
        "title": "Consumers",
        "headline": "Document AI harm with cryptographic proof",
        "subhead": "Mishara — plain English + Velaru-signed receipt for platforms and agencies.",
        "pain": "Platform wronged you. You need evidence stronger than screenshots.",
        "offer": "Harm intake · demand letter · verify link",
        "price": "Free intake",
        "cta_label": "Open Gate",
        "cta_route": "index",
        "secondary_label": "Verify engine",
        "secondary_href": f"{VELARU_PUBLIC}/verify",
        "proof": "Independent audit receipt · Exhibit A hash",
        "tags": ["consumer", "rights", "mishara"],
    },
    "investors": {
        "emoji": "",
        "title": "Investors",
        "headline": "Clearance infrastructure — not a wrapper",
        "subhead": "Metered Gate API + operator weld SKUs + patent-pending proof rail.",
        "pain": "Another 'AI safety' slide deck with no fail-closed demo.",
        "offer": "Live metrics · fee schedule · status",
        "price": "Fees on cleared flow",
        "cta_label": "View status",
        "cta_route": "status_page",
        "secondary_label": "Fee schedule",
        "secondary_route": "register_page",
        "proof": "Patent #64/124,027 · public verify · hop meter",
        "tags": ["investor", "deck", "metrics"],
    },
    "partners": {
        "emoji": "",
        "title": "Integrators & partners",
        "headline": "White-label fuse hop under your brand",
        "subhead": "Gate meters. Velaru proves. You keep the customer relationship.",
        "pain": "Your clients want agent kill switches. You don't want to build the proof rail.",
        "offer": "Partner wiring · rev share on welded paths",
        "price": "Per wiring + fee share",
        "cta_label": "Partner wiring",
        "cta_route": "install",
        "secondary_label": "Partner email",
        "secondary_mailto": "subject=Partner%20%E2%80%94%20White%20label",
        "proof": "Fail-closed hop · Velaru verify · weld economics",
        "tags": ["partner", "whitelabel", "agency"],
    },
}


def all_plates() -> dict[str, dict]:
    return PLATES


def get_plate(slug: str) -> dict | None:
    return PLATES.get(slug)


def plate_list() -> list[dict]:
    items = []
    for slug, p in PLATES.items():
        items.append({"slug": slug, **p})
    return items


def core_gtm_plates() -> list[dict]:
    """High-intent ICPs for immediate GTM focus."""
    slugs = ("operators", "carriers", "compliance")
    out = []
    for slug in slugs:
        p = PLATES.get(slug)
        if not p:
            continue
        out.append({"slug": slug, **p})
    return out


def opportunities_manifest(public_url: str, contact_email: str) -> dict:
    entries = []
    for slug, p in PLATES.items():
        entries.append(
            {
                "slug": slug,
                "title": p["title"],
                "headline": p["headline"],
                "price": p["price"],
                "url": f"{public_url}/for/{slug}",
                "pitch_url": f"{public_url}/pitch/{slug}",
                "tags": p.get("tags", []),
            }
        )
    return {
        "name": "Gate + Velaru opportunity surfaces",
        "version": "1.2.0",
        "not_saas": True,
        "hub": f"{public_url}/start",
        "primary_money": f"{public_url}/operator",
        "economics": f"{public_url}/pricing",
        "opportunities": entries,
        "contact": contact_email,
        "engine": VELARU_PUBLIC,
        "gatekeep": "Audience doors point at weld and fee schedule. Lab is footnote.",
    }
