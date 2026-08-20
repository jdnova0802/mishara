"""Post-trade distribution stack — how Gate propagates from FMI apex to welded mouths.

Not cliche 'disrupt DTCC'. The mouth sits where settlement pain actually starts:
the irreversible instruction that becomes a fail, an exception, or a skip-clear
before the CSD ever reaches finality III.

Distribution matches the register: management at the weld, bps on cleared flow,
doctrine by reference at the top, implementation obligation at the bottom.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-distribution-v1"
INVENTOR = "Nisaba LLC / Gate"

# Apex → base. Peers at top reference PFMI; revenue at bottom on cleared flow.
TIERS = (
    {
        "tier": 0,
        "id": "fmi_apex",
        "who": "DTCC · NSCC · DTC · FICC · Euroclear · Clearstream · CLS peers",
        "relationship": "reference_architecture",
        "buys": "nothing — sets the gravity well",
        "gate_role": (
            "PFMI-shaped manifests: finality moments, DvP mouth, P17 receipts, "
            "ISO-20022-friendly JSON — interoperable, not competitive cosplay"
        ),
        "their_pain_we_address": [
            "T+1 / 24x5 compresses exception time — manual SSIs and email confirmations break",
            "ISO 20022 migration needs machine-readable instruction surfaces",
            "Operational risk at decision time, not quarterly attestation",
        ],
        "not": "replace CNS or ALERT — instruction layer before their net",
    },
    {
        "tier": 1,
        "id": "clearing_members",
        "who": "Clearing members · custodian banks · CSD participants",
        "relationship": "settlement_members",
        "buys": "mutualized mouth requirement on gross instructions they admit to windows",
        "gate_role": "Pre-net clearance · margin/waterfall skin · settlement window finality hash",
        "manifests": ["settlement.json", "settlement-members.json", "pre-net-clearance.json"],
        "economics": "Mutualized default fund + Gate capital in waterfall — not SaaS seat tax",
    },
    {
        "tier": 2,
        "id": "intermediaries",
        "who": "Broker-dealers · introducing brokers · MGAs · PAS carriers · Guidewire/Duck Creek shops",
        "relationship": "propagate_requirement",
        "buys": "bind-only / payout weld · officer pack · delegated-authority gate",
        "gate_role": "SSI-preauth equivalent on the hop · PERMIT/DENY before PAS commit",
        "manifests": ["ssi-preauth.json", "instruction-finality.json", "commit-auth.json"],
        "economics": "Weld + per-parent rent — they pass mouth cost as infrastructure, not margin",
    },
    {
        "tier": 3,
        "id": "operators",
        "who": "Licensed operators on one irreversible write (payout · bind-only · withdraw)",
        "relationship": "welded_mouth",
        "buys": "register: management leg + 10 bps on cleared flow",
        "gate_role": "Exclusive door · CHARGE-only LIVE · stranger verify · restraint inventory",
        "manifests": ["register.json", "operator.json", "restraint.json"],
        "economics": "10 bps + carry on cleared — civilization default asset, GP keeps mouth",
    },
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def stack(public_url: str = "") -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Post-Trade Distribution Stack",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "thesis": (
            "DTCC-shaped at the top as reference. Revenue at the bottom on cleared flow. "
            "Everyone below the apex implements the mouth because exceptions are expensive at T+1."
        ),
        "one_sentence_for_dtcc_peer": (
            "We do not replace your net. We clear the irreversible instruction before it "
            "becomes your exception queue."
        ),
        "one_sentence_for_anyone_below": (
            "If your bind or wire can fire without a fail-closed hop and a fetchable receipt, "
            "you are their operational risk — not Gate's."
        ),
        "propagation_model": "register_tiers",
        "propagation": {
            "doctrine": "Published at apex tier as PFMI-aligned manifests — cite, do not rebrand",
            "obligation": "Cascades down as welded requirement on gross instructions",
            "economics": "Management at weld · bps on cleared at operator · mutualized skin at member",
            "not_saas": "No per-seat dashboard. Infrastructure register.",
        },
        "tiers": [
            {
                **t,
                "manifests": [
                    f"{base}/.well-known/{m}" if base and not m.startswith("http") else m
                    for m in t.get("manifests", [])
                ],
            }
            for t in TIERS
        ],
        "dtcc_peer_alignment": {
            "t1_automation": "Instruction finality + pre-auth path removes email/SSI exception cycles",
            "iso_20022": "Well-known JSON surfaces — same interoperability instinct, not mainframe cosplay",
            "treasury_clearing_2026": "Fail-closed mouth on irreversible release before CCP sees gross",
            "cns_modernization": "Pre-net clearance — gross passes mouth before your net collapses it",
        },
        "below_the_line": [
            "MGAs inherit mouth requirement from carrier weld",
            "Renewal midnight bind inherits pre-bind gate from Guidewire listing",
            "Agents inherit DEAD from license fuse — children cannot outlive parent",
        ],
        "gatekeep": "Proprietary stack distribution. Ours.",
        "their_production": False,
        "live": f"{base}/.well-known/distribution.json" if base else None,
        "register": f"{base}/.well-known/register.json" if base else None,
        "settlement": f"{base}/.well-known/settlement.json" if base else None,
    }


def manifest(public_url: str) -> dict[str, Any]:
    return stack(public_url)
