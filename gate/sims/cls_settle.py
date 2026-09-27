"""Z2 CLS FX Settlement Instruction Gate — lab mouth: matched ≠ settled PvP.

Lab only. their_production is always False.
Not a trading venue. Not FX risk dashboard.
Gates settle of matched payment instructions behind risk tests.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from gate.sims.lab_invariant import stamp_lab_flag
from gate.sims.logos import canonical


SPEC = "nisaba-cls-settle-lab-v1"
THEIR_PRODUCTION = False

SUPPORTED_CURRENCIES = frozenset(
    {"USD", "EUR", "GBP", "JPY", "CAD", "CHF", "AUD", "NZD", "SGD", "HKD"}
)


@dataclass
class Member:
    member_id: str
    suspended: bool = False


@dataclass
class Instruction:
    instruction_id: str
    member_id: str
    buy_ccy: str
    sell_ccy: str
    buy_amount: str
    sell_amount: str
    counter_instruction_id: str | None
    matched: bool = False
    settled: bool = False


@dataclass
class Store:
    members: dict[str, Member] = field(default_factory=dict)
    instructions: dict[str, Instruction] = field(default_factory=dict)
    receipts: dict[str, dict[str, Any]] = field(default_factory=dict)


STORE = Store()


def reset() -> None:
    STORE.members.clear()
    STORE.instructions.clear()
    STORE.receipts.clear()


def _receipt(
    decision: str,
    reason_code: str,
    *,
    instruction_id: str | None = None,
    member_id: str | None = None,
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rid = str(uuid.uuid4())
    payload = {
        "spec": SPEC,
        "receipt_id": rid,
        "receipt_class": "clearance",
        "decision": decision,
        "reason_code": reason_code,
        "instruction_id": instruction_id,
        "member_id": member_id,
        "result": result,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="cls_settle"),
        "ts": time.time(),
    }
    payload["receipt_hash"] = hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()
    STORE.receipts[rid] = payload
    return {**payload, "receipt_url": f"/v1/cls-settle/receipts/{rid}"}


def register_member(member_id: str) -> dict[str, Any]:
    STORE.members[member_id] = Member(member_id=member_id)
    return {
        "member_id": member_id,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="cls_settle"),
    }


def suspend_member(member_id: str) -> None:
    m = STORE.members.get(member_id)
    if m:
        m.suspended = True


def submit_instruction(
    *,
    member_id: str,
    buy_ccy: str,
    sell_ccy: str,
    buy_amount: str,
    sell_amount: str,
) -> dict[str, Any]:
    if member_id not in STORE.members:
        return _receipt("DENY", "no_member", member_id=member_id)
    if STORE.members[member_id].suspended:
        return _receipt("DENY", "member_suspended", member_id=member_id)
    buy_ccy = buy_ccy.upper()
    sell_ccy = sell_ccy.upper()
    if buy_ccy not in SUPPORTED_CURRENCIES or sell_ccy not in SUPPORTED_CURRENCIES:
        return _receipt(
            "DENY",
            "currency_unsupported",
            member_id=member_id,
            result={"buy_ccy": buy_ccy, "sell_ccy": sell_ccy},
        )
    if buy_ccy == sell_ccy:
        return _receipt("DENY", "same_currency", member_id=member_id)
    iid = str(uuid.uuid4())
    STORE.instructions[iid] = Instruction(
        instruction_id=iid,
        member_id=member_id,
        buy_ccy=buy_ccy,
        sell_ccy=sell_ccy,
        buy_amount=str(buy_amount),
        sell_amount=str(sell_amount),
        counter_instruction_id=None,
    )
    return {
        "instruction_id": iid,
        "member_id": member_id,
        "matched": False,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="cls_settle"),
    }


def match_instructions(a_id: str, b_id: str) -> dict[str, Any]:
    a = STORE.instructions.get(a_id)
    b = STORE.instructions.get(b_id)
    if a is None or b is None:
        return _receipt("DENY", "instruction_missing", result={"a": a_id, "b": b_id})
    # PvP mirror: A's buy == B's sell and amounts mirror
    if not (
        a.buy_ccy == b.sell_ccy
        and a.sell_ccy == b.buy_ccy
        and a.buy_amount == b.sell_amount
        and a.sell_amount == b.buy_amount
    ):
        return _receipt(
            "DENY",
            "match_failed",
            instruction_id=a_id,
            result={"counter": b_id},
        )
    a.matched = True
    b.matched = True
    a.counter_instruction_id = b_id
    b.counter_instruction_id = a_id
    return {
        "matched": True,
        "instructions": [a_id, b_id],
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="cls_settle"),
    }


def settle(
    instruction_id: str,
    *,
    risk_ok: bool = True,
    counterparty_funded: bool = True,
) -> dict[str, Any]:
    """Mouth: settle only matched instructions that pass risk tests. Final & irrevocable (sim)."""
    inst = STORE.instructions.get(instruction_id)
    if inst is None:
        return _receipt("DENY", "no_instruction", instruction_id=instruction_id)

    m = STORE.members.get(inst.member_id)
    if m is None or m.suspended:
        return _receipt(
            "DENY",
            "member_suspended",
            instruction_id=instruction_id,
            member_id=inst.member_id,
        )

    if not inst.matched or not inst.counter_instruction_id:
        return _receipt(
            "DENY",
            "unmatched",
            instruction_id=instruction_id,
            member_id=inst.member_id,
            result={"matched_trade_is_not_settled": True},
        )

    counter = STORE.instructions.get(inst.counter_instruction_id)
    if counter is None:
        return _receipt("DENY", "counter_missing", instruction_id=instruction_id)

    if not risk_ok:
        return _receipt(
            "DENY",
            "risk_test_failed",
            instruction_id=instruction_id,
            member_id=inst.member_id,
            result={"pvp": True, "real_cls": False},
        )

    if not counterparty_funded:
        return _receipt(
            "DENY",
            "pay_in_shortage",
            instruction_id=instruction_id,
            member_id=inst.member_id,
            result={"pvp": True, "herstatt_guard": True},
        )

    if inst.settled:
        return _receipt(
            "ALLOW",
            "already_settled",
            instruction_id=instruction_id,
            member_id=inst.member_id,
            result={"final": True, "irrevocable": True},
        )

    inst.settled = True
    counter.settled = True
    settle_id = str(uuid.uuid4())
    return _receipt(
        "ALLOW",
        "settled_pvp",
        instruction_id=instruction_id,
        member_id=inst.member_id,
        result={
            "settle_id": settle_id,
            "counter_instruction_id": inst.counter_instruction_id,
            "buy_ccy": inst.buy_ccy,
            "sell_ccy": inst.sell_ccy,
            "final": True,
            "irrevocable": True,
            "real_cls": False,
            "fixture": True,
        },
    )


def get_receipt(receipt_id: str) -> dict[str, Any] | None:
    r = STORE.receipts.get(receipt_id)
    if r is None:
        return None
    return {**r, "receipt_url": f"/v1/cls-settle/receipts/{receipt_id}"}
