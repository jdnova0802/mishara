#!/usr/bin/env python3
"""One file a desk can read. The mandate, then two swipes.

The yes is written first. A swipe inside it is GO. A swipe that edits the
cap on the card is NO_GO. Each decision gets a receipt the stranger checks
with a public key they already hold. The server does not have to be on.

This is not the dollar, and it is not a witness who was in the room.
Clearance is not settlement. Gate does not hold the funds.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat

try:
    from gate import issuing_mouth as mouth
    from gate import receipt as receipt_mod
    from gate import spend_mandate as mandate_mod
except ImportError:
    import issuing_mouth as mouth
    import receipt as receipt_mod
    import spend_mandate as mandate_mod

SPEC = "gate-desk-file-v1"
CAP = "25.00"
MERCHANT = "Acme Supplies"
AGENT = "desk_agent"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _keys() -> tuple[str, str]:
    priv = Ed25519PrivateKey.generate()
    priv_b = priv.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    pub_b = priv.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    return base64.b64encode(priv_b).decode("utf-8"), base64.b64encode(pub_b).decode("utf-8")


def _eval(body: dict) -> dict:
    cap = body.get("mandate", {}).get("max_amount")
    amount = body.get("transfer", {}).get("amount")
    try:
        over = float(amount) > float(cap)
    except (TypeError, ValueError):
        over = True
    if over:
        return {
            "decision": "NO_GO",
            "signals": ["amount_exceeds_cap"],
            "message": "Amount is over the bound cap.",
        }
    return {"decision": "GO", "signals": [], "message": "Amount is inside the bound cap."}


def _issue(
    *,
    event_id: str,
    mandate_id: str,
    decision: str,
    acted: bool,
    prev: str | None,
    signal: str | None,
) -> dict[str, Any]:
    issued = receipt_mod.issue_receipt(
        event_id=event_id,
        fuse_id="desk-file",
        job_id=mandate_id,
        decision=decision,
        acted=acted,
        verify_url=f"desk-file:{mandate_id}",
        created_at=_utc_now(),
        hop={
            "state": "clearance",
            "halt": decision != "GO",
            "verdict": decision,
        },
        prev_receipt_hash=prev,
    )
    canonical = json.loads(issued["canonical_receipt_json"])
    return {
        "spec": "gate-receipt-payload-v1",
        "canonical_receipt": canonical,
        "canonical_receipt_json": issued["canonical_receipt_json"],
        "receipt_hash": issued["receipt_hash"],
        "receipt_signature": issued["receipt_signature"],
        "receipt_public_key_fingerprint": issued["receipt_public_key_fingerprint"],
        "verify_url": f"desk-file:{mandate_id}",
        "signal": signal,
    }


def _page(*, bound: dict, within: dict, edited: dict, within_receipt: dict, edited_receipt: dict) -> str:
    terms = bound["terms"]
    edited_bind = edited.get("mandate_bind") or {}
    within_bind = within.get("mandate_bind") or {}
    diverged = ", ".join(edited_bind.get("diverged") or []) or "none"
    return "\n".join(
        [
            "GATE DESK FILE",
            f"spec: {SPEC}",
            "",
            "The yes was written before either swipe.",
            "A swipe inside the yes is GO.",
            "A swipe that changes the cap on the card is NO_GO.",
            "Each line has a receipt. Check it with public.key. The server can be off.",
            "",
            "This file is not the dollar.",
            "This file is not a person who was in the room.",
            "Clearance is not settlement. Gate does not hold the funds.",
            "",
            "MANDATE",
            f"id: {bound['mandate_id']}",
            f"fingerprint: {bound['fingerprint']}",
            f"agent: {terms['agent_id']}",
            f"max: {terms['max_amount']} {terms['currency']}",
            f"counterparty: {terms['expected_counterparty']}",
            f"not_after: {terms['not_after']}",
            f"status: {bound['status']}",
            "",
            "SWIPE INSIDE THE YES",
            "amount: 20.00 USD",
            f"decision: {within['decision']}",
            f"mandate: {within_bind.get('mandate_id')}",
            f"receipt: {within_receipt['receipt_hash']}",
            "file: within.json",
            "",
            "SWIPE THAT EDITS THE CAP",
            "card metadata max: 500.00 USD",
            f"decision: {edited['decision']}",
            f"signal: {edited_bind.get('signal')}",
            f"diverged: {diverged}",
            f"receipt: {edited_receipt['receipt_hash']}",
            "file: edited.json",
            "",
            "CHECK",
            "python offline_verify.py within.json --public-key public.key",
            "python offline_verify.py edited.json --public-key public.key",
            "stdout is valid, or invalid.",
            "",
        ]
    )


def build(directory: str, *, agent_id: str | None = None) -> dict[str, str]:
    """Write the desk file and the two receipts. Returns the paths."""
    os.makedirs(directory, exist_ok=True)
    agent = (agent_id or AGENT).strip() or AGENT
    bound = mandate_mod.bind(
        {
            "agent_id": agent,
            "max_amount": CAP,
            "expected_counterparty": MERCHANT,
            "allowed_categories": ["computer_software_stores"],
            "ttl_seconds": 86400,
            "card_id": "ic_desk",
        },
        demo=True,
    )
    if not bound.get("ok"):
        raise RuntimeError(bound.get("error") or "mandate_bind_failed")

    within_auth = mouth.dogfood_authorization(
        amount_cents=2000,
        merchant=MERCHANT,
        agent_id=agent,
        max_amount=CAP,
        expected_merchant=MERCHANT,
        allowed_categories=["computer_software_stores"],
        mandate_id=bound["mandate_id"],
        card_id="ic_desk",
    )
    within = mouth.decide(within_auth, evaluate_fn=_eval)

    edited_auth = mouth.dogfood_authorization(
        amount_cents=2000,
        merchant=MERCHANT,
        agent_id=agent,
        max_amount="500.00",
        expected_merchant=MERCHANT,
        allowed_categories=["computer_software_stores"],
        mandate_id=bound["mandate_id"],
        card_id="ic_desk",
    )
    edited = mouth.decide(edited_auth, evaluate_fn=_eval)

    priv, pub = _keys()
    previous_priv = os.environ.get("GATE_RECEIPT_PRIVATE_KEY")
    previous_pub = os.environ.get("GATE_RECEIPT_PUBLIC_KEY")
    os.environ["GATE_RECEIPT_PRIVATE_KEY"] = priv
    os.environ["GATE_RECEIPT_PUBLIC_KEY"] = pub
    try:
        within_receipt = _issue(
            event_id=f"desk-within-{bound['mandate_id']}",
            mandate_id=bound["mandate_id"],
            decision=within["decision"],
            acted=False,
            prev=None,
            signal=(within.get("mandate_bind") or {}).get("signal"),
        )
        edited_receipt = _issue(
            event_id=f"desk-edited-{bound['mandate_id']}",
            mandate_id=bound["mandate_id"],
            decision=edited["decision"],
            acted=False,
            prev=within_receipt["receipt_hash"],
            signal=(edited.get("mandate_bind") or {}).get("signal"),
        )
    finally:
        if previous_priv is None:
            os.environ.pop("GATE_RECEIPT_PRIVATE_KEY", None)
        else:
            os.environ["GATE_RECEIPT_PRIVATE_KEY"] = previous_priv
        if previous_pub is None:
            os.environ.pop("GATE_RECEIPT_PUBLIC_KEY", None)
        else:
            os.environ["GATE_RECEIPT_PUBLIC_KEY"] = previous_pub

    page_path = os.path.join(directory, "desk-file.txt")
    mandate_path = os.path.join(directory, "mandate.json")
    within_path = os.path.join(directory, "within.json")
    edited_path = os.path.join(directory, "edited.json")
    key_path = os.path.join(directory, "public.key")

    with open(page_path, "w", encoding="utf-8") as handle:
        handle.write(
            _page(
                bound=bound,
                within=within,
                edited=edited,
                within_receipt=within_receipt,
                edited_receipt=edited_receipt,
            )
        )
    with open(mandate_path, "w", encoding="utf-8") as handle:
        json.dump(bound, handle, indent=2)
        handle.write("\n")
    with open(within_path, "w", encoding="utf-8") as handle:
        json.dump(within_receipt, handle, indent=2)
        handle.write("\n")
    with open(edited_path, "w", encoding="utf-8") as handle:
        json.dump(edited_receipt, handle, indent=2)
        handle.write("\n")
    with open(key_path, "w", encoding="utf-8") as handle:
        handle.write(pub + "\n")

    return {
        "dir": directory,
        "page": page_path,
        "mandate": mandate_path,
        "within": within_path,
        "edited": edited_path,
        "public_key": key_path,
        "mandate_id": bound["mandate_id"],
        "within_decision": within["decision"],
        "edited_decision": edited["decision"],
        "edited_signal": (edited.get("mandate_bind") or {}).get("signal"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write the Gate desk file")
    parser.add_argument("directory", nargs="?", default="desk-file")
    args = parser.parse_args(argv)
    out = build(args.directory)
    print(out["page"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
