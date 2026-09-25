"""Pre-real-USDC gates — must all pass before mainnet capital.

Claude's bar (25 Sep 2026). Code can fail a gate closed; humans own audit + legal.
"""
from __future__ import annotations

import os
from typing import Any

SPEC = "gate-escrow-preflight-v1"

# Known residual after contract harden — still needs counsel.
LEGAL_RESIDUAL = (
    "Gate's EIP-712 signing key authorizes release/liquidate when someone submits "
    "a valid signature. Gate is not msg.sender and cannot pause/sweep/upgrade, but "
    "producing the release signal may still touch money-services classification. "
    "Cheap one-time legal opinion required — not a full MTL process."
)


def _flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes", "on")


def key_path_review() -> dict[str, Any]:
    """Static claims about ClearanceEscrow.sol after harden — verify against source."""
    return {
        "gate_is_privileged_caller": False,
        "gate_can_pause": False,
        "gate_can_upgrade": False,
        "gate_can_sweep": False,
        "gate_can_rotate_signer": False,
        "release_requires_eip712_clear_sig": True,
        "liquidate_requires_eip712_never_sig": True,
        "principal_reclaim_after_expiry_without_gate": True,
        "submitter_is_anyone": True,
        "honest_residual": (
            "Valid Gate signature + submitter still moves vault USDC. "
            "That is verifier authority, not wallet custody of balances."
        ),
        "status": "code_hardened_pending_human_confirm",
        "human_confirm_env": "GATE_ESCROW_KEYPATH_REVIEWED",
        "human_confirmed": _flag("GATE_ESCROW_KEYPATH_REVIEWED"),
    }


def gates() -> list[dict[str, Any]]:
    return [
        {
            "id": 1,
            "name": "independent_smart_contract_audit",
            "required": True,
            "passed": _flag("GATE_ESCROW_AUDIT_PASSED"),
            "env": "GATE_ESCROW_AUDIT_PASSED",
            "plain": (
                "Independent audit of ClearanceEscrow.sol before any third-party USDC. "
                "Non-negotiable. Small TVL is not a waiver."
            ),
            "owner": "human — hire auditor",
        },
        {
            "id": 2,
            "name": "gate_never_had_the_keys_every_path",
            "required": True,
            "passed": _flag("GATE_ESCROW_KEYPATH_REVIEWED"),
            "env": "GATE_ESCROW_KEYPATH_REVIEWED",
            "plain": (
                "Confirm Gate cannot unilaterally move funds on any path: "
                "no admin caller, no pause, no upgrade, no sweep, no signer rotate. "
                "Release/liquidate = EIP-712 verify only; expiry reclaim = principal only."
            ),
            "owner": "human review of Sol + this key_path_review()",
            "code_claims": key_path_review(),
        },
        {
            "id": 3,
            "name": "legal_sanity_verifier_not_transmitter",
            "required": True,
            "passed": _flag("GATE_ESCROW_LEGAL_OK"),
            "env": "GATE_ESCROW_LEGAL_OK",
            "plain": (
                "One-time legal opinion: Gate as verifier/signaling layer on foreign vault "
                "is not money transmission. Not a full license process — confirm the frame."
            ),
            "owner": "counsel",
            "residual": LEGAL_RESIDUAL,
        },
        {
            "id": 4,
            "name": "testnet_full_loop_before_mainnet",
            "required": True,
            "passed": _flag("GATE_ESCROW_TESTNET_OK"),
            "env": "GATE_ESCROW_TESTNET_OK",
            "plain": (
                "Deploy testnet. Run principal-lock → breach → keeper-submit → contract-pays "
                "with test USDC. No mainnet dollar until this passes."
            ),
            "owner": "eng ops",
            "harness": "gate/escrow/testnet_loop.md",
        },
    ]


def report() -> dict[str, Any]:
    g = gates()
    passed = all(x["passed"] for x in g)
    return {
        "spec": SPEC,
        "all_passed": passed,
        "real_usdc_allowed": passed,
        "plain": (
            "All four gates green → real USDC may touch ClearanceEscrow."
            if passed
            else "BLOCKED — do not lock real USDC until every gate passes."
        ),
        "gates": g,
        "key_path_review": key_path_review(),
        "legal_residual": LEGAL_RESIDUAL,
        "standard": "verify before it's real, not after",
    }
