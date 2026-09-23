"""Rail settlement truth — finality + who-eats-the-loss.

Discovery atoms Stripe/Apple Pay do not publish as a clean cross-rail API:

1. Finality oracle: when is a transfer irreversible under which rail?
2. Loss allocation: if fraud/agent error, who eats the loss by default?

Not legal advice. Network rules and contracts vary. This is a machine-readable
baseline agents/states can query before autonomous spend — the PDF layer
pipes leave as lore.

Spec: gate-rail-truth-v1
"""

from __future__ import annotations

from typing import Any

SPEC = "gate-rail-truth-v1"
FINALITY_SPEC = "gate-rail-finality-v1"
LOSS_SPEC = "gate-rail-loss-v1"

# High-level US-centric baselines. `caveats` are mandatory — do not strip.
RAILS: dict[str, dict[str, Any]] = {
    "ach": {
        "name": "ACH (US)",
        "operator": "Nacha / ODFI-RDFI banks",
        "finality": {
            "provisional_at": "RDFI posts credit (often same or next banking day)",
            "recall_window": "Consumer unauthorized: up to 60 calendar days from statement; other return reasons shorter (often 2 banking days for some codes)",
            "commercially_final_after": "Return window for the relevant reason code closes",
            "irreversible_meaning": "Funds may still be recalled/returned inside Nacha windows; not wire-final",
            "typical_settle": "T+1 / T+2 banking days (Same Day ACH available for eligible)",
            "agent_safe_default": "treat_as_reversible_until_return_window_closed",
        },
        "loss": {
            "unauthorized_consumer_debit": "ODFI/originator often eats; warranty regime",
            "authorized_but_fraudulent_instruction": "Often originator/customer under agreement — not the network 'fraud score'",
            "bec_vendor_impersonation": "Typically payer/corporate customer loss absent bank negligence finding",
            "rail_default_eater": "originating customer / ODFI warranties — not Visa-like cardholder shift",
            "machine_label": "originator_heavy",
        },
        "caveats": [
            "Exact return codes and timings are Nacha operating rules + bank agreements",
            "Same Day ACH does not equal irreversibility",
        ],
    },
    "fednow": {
        "name": "FedNow",
        "operator": "Federal Reserve",
        "finality": {
            "provisional_at": "Instant credit to receiver's bank when payment accepted",
            "recall_window": "No classic ACH return set; limited dispute/request processes via banks — not a long consumer 60-day ACH clone",
            "commercially_final_after": "Acceptance / settlement on FedNow (near-real-time)",
            "irreversible_meaning": "Designed as instant; unwind is exception/ops/legal, not standard return window",
            "typical_settle": "Seconds",
            "agent_safe_default": "treat_as_hard_to_unwind_after_accept",
        },
        "loss": {
            "unauthorized": "Bank/customer agreement + UCC facts; not card chargeback",
            "authorized_but_fraudulent_instruction": "Often paying customer (Studco-shaped instruction risk)",
            "bec_vendor_impersonation": "Payer-side unless bank actual-knowledge / agreement says otherwise",
            "rail_default_eater": "paying_customer_instruction_risk",
            "machine_label": "payer_instruction_heavy",
        },
        "caveats": [
            "Participation and features vary by FI",
            "Instant ≠ immune to legal clawback",
        ],
    },
    "rtp": {
        "name": "RTP (The Clearing House)",
        "operator": "The Clearing House",
        "finality": {
            "provisional_at": "Instant credit when accepted",
            "recall_window": "Request for return / RFPs — not ACH-style broad returns",
            "commercially_final_after": "Acceptance on RTP",
            "irreversible_meaning": "Harder unwind than ACH; still legal/ops paths",
            "typical_settle": "Seconds",
            "agent_safe_default": "treat_as_hard_to_unwind_after_accept",
        },
        "loss": {
            "unauthorized": "FI + customer agreement",
            "authorized_but_fraudulent_instruction": "Often paying customer",
            "bec_vendor_impersonation": "Payer-side default pattern",
            "rail_default_eater": "paying_customer_instruction_risk",
            "machine_label": "payer_instruction_heavy",
        },
        "caveats": ["Member FI rules apply", "Not universal FI coverage"],
    },
    "wire": {
        "name": "Wire (Fedwire / CHIPS-shaped)",
        "operator": "Federal Reserve / CHIPS banks",
        "finality": {
            "provisional_at": "When beneficiary bank accepts / credits under UCC 4A",
            "recall_window": "No ACH consumer return window; recall is bank-to-bank goodwill / legal",
            "commercially_final_after": "Acceptance under UCC Article 4A",
            "irreversible_meaning": "Among hardest retail rails to reverse",
            "typical_settle": "Minutes to same day",
            "agent_safe_default": "treat_as_final_after_accept",
        },
        "loss": {
            "unauthorized": "UCC 4A security-procedure facts",
            "authorized_but_fraudulent_instruction": "Often customer if security procedures followed",
            "bec_vendor_impersonation": "Classic payer loss pattern (Studco-adjacent)",
            "rail_default_eater": "paying_customer_if_bank_followed_security_procedures",
            "machine_label": "payer_instruction_heavy",
        },
        "caveats": ["UCC 4A is fact-specific", "International wires differ"],
    },
    "card": {
        "name": "Card (Visa/Mastercard shaped)",
        "operator": "Networks + issuers + acquirers",
        "finality": {
            "provisional_at": "Authorization; clearing/settlement follow",
            "recall_window": "Chargeback / dispute windows (often 60–120 days class depending on reason)",
            "commercially_final_after": "Chargeback window closes for the reason code",
            "irreversible_meaning": "Merchant/acquirer risk until dispute windows end",
            "typical_settle": "T+1 to T+3 class to merchant",
            "agent_safe_default": "treat_as_reversible_via_chargeback_until_window_closed",
        },
        "loss": {
            "unauthorized": "Often issuer/cardholder protections; merchant may eat chargeback",
            "authorized_but_fraudulent_instruction": "Depends; CNP fraud often merchant/acquirer",
            "bec_vendor_impersonation": "Less classic than ACH/wire; still possible on push-to-card",
            "rail_default_eater": "reason_code_dependent_merchant_or_issuer",
            "machine_label": "reason_code_split",
        },
        "caveats": ["Scheme rules dominate", "Not a single global window"],
    },
    "usdc": {
        "name": "USDC (on-chain transfer)",
        "operator": "Issuer + chain + wallets",
        "finality": {
            "provisional_at": "Included in a block",
            "recall_window": "None at protocol layer; issuer freeze/blacklist is separate",
            "commercially_final_after": "N confirmations (chain-dependent) + no issuer intervention",
            "irreversible_meaning": "Ledger final ≠ fiat redeem final; issuer policy matters",
            "typical_settle": "Seconds to minutes",
            "agent_safe_default": "treat_as_ledger_final_after_N_confirmations_issuer_risk_remains",
        },
        "loss": {
            "unauthorized": "Key holder / wallet security — usually user",
            "authorized_but_fraudulent_instruction": "Signer/agent principal",
            "bec_vendor_impersonation": "Sender loss if they signed the wrong destination",
            "rail_default_eater": "key_holder_or_mandate_principal",
            "machine_label": "signer_heavy",
        },
        "caveats": ["Chain reorg risk exists at low N", "Issuer compliance actions possible"],
    },
    "x402": {
        "name": "x402-style HTTP payment",
        "operator": "Facilitator + underlying rail (often stablecoin)",
        "finality": {
            "provisional_at": "Facilitator accepts / on-chain inclusion if crypto-backed",
            "recall_window": "Inherited from underlying rail",
            "commercially_final_after": "Underlying rail finality",
            "irreversible_meaning": "x402 is a challenge layer; finality is not native — follow settlement asset",
            "typical_settle": "Underlying",
            "agent_safe_default": "resolve_underlying_rail_then_apply_that_finality",
        },
        "loss": {
            "unauthorized": "Underlying + facilitator terms",
            "authorized_but_fraudulent_instruction": "Mandate principal / agent operator",
            "bec_vendor_impersonation": "Sender/mandate side if wrong payee in challenge",
            "rail_default_eater": "inherits_underlying",
            "machine_label": "inherits_underlying",
        },
        "caveats": ["Always name the settlement asset", "Facilitator is not FedNow"],
    },
}


def list_rails() -> dict[str, Any]:
    return {
        "spec": SPEC,
        "rails": sorted(RAILS.keys()),
        "their_production": False,
        "not": "legal advice / bank warranty / scheme rulebook replacement",
        "use": "Agent/state pre-spend query: finality + default loss eater by rail",
    }


def finality(rail: str) -> dict[str, Any] | None:
    key = (rail or "").strip().lower()
    row = RAILS.get(key)
    if not row:
        return None
    return {
        "spec": FINALITY_SPEC,
        "rail": key,
        "name": row["name"],
        "operator": row["operator"],
        **row["finality"],
        "caveats": row["caveats"],
        "their_production": False,
    }


def loss_allocation(rail: str) -> dict[str, Any] | None:
    key = (rail or "").strip().lower()
    row = RAILS.get(key)
    if not row:
        return None
    return {
        "spec": LOSS_SPEC,
        "rail": key,
        "name": row["name"],
        "operator": row["operator"],
        **row["loss"],
        "caveats": row["caveats"],
        "their_production": False,
    }


def lookup(rail: str) -> dict[str, Any] | None:
    key = (rail or "").strip().lower()
    if key not in RAILS:
        return None
    return {
        "spec": SPEC,
        "rail": key,
        "finality": finality(key),
        "loss": loss_allocation(key),
        "their_production": False,
        "not_legal_advice": True,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Rail settlement truth",
        "atoms": [
            "finality_oracle — when is this irreversible on this rail?",
            "loss_allocation — who eats fraud/agent-error loss by default?",
        ],
        "why_pipes_skip": (
            "Gardens hide finality/liability as ops lore; agents need a queryable map "
            "before autonomous spend"
        ),
        "rails": sorted(RAILS.keys()),
        "urls": {
            "manifest": f"{base}/.well-known/rail-truth.json",
            "lookup": f"{base}/v1/rail-truth/{{rail}}",
            "finality": f"{base}/v1/rail-truth/{{rail}}/finality",
            "loss": f"{base}/v1/rail-truth/{{rail}}/loss",
        },
        "their_production": False,
        "not_legal_advice": True,
    }
