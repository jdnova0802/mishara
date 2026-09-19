"""Release MAY — may this named agent open the gate for this named bill.

Not delivery. Not P&I cover. Not an eBL platform. Not Gate remaining CHARGE.
The machine cannot wear the agent mouth, the charterer mouth, or the telex email.
"""
from __future__ import annotations

import hashlib
import json
import secrets
from typing import Any

from rel import receipt as receipt_mod

SPEC = "rel-v1"
INVARIANT = (
    "Release is not delivery. "
    "The machine cannot wear the agent mouth, the charterer mouth, or the telex email."
)
DECISIONS = ("EXIST", "HOLD", "NONEXIST", "GAP")
INSTRUMENT = ("SURRENDERED", "OUTSTANDING", "EBL_CONTROL", "GAP")
MOUTH_KEYS = (
    "released",
    "telex_ok",
    "authorized",
    "gate_open",
    "may_release",
    "delivery_ok",
    "switch_ok",
    "loi_covers",
    "p_and_i_ok",
    "clean_release",
    "release_granted",
    "ok_to_release",
)
NOT = (
    "delivery, P&I cover, Kayhan, WaveBL, CargoSmart, SuretyBind, "
    "or the machine wearing the agent, charterer, or telex mouth."
)


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _present(raw: Any) -> bool:
    if raw is None:
        return False
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, str):
        return bool(raw.strip())
    if isinstance(raw, dict):
        return any(_present(v) for v in raw.values())
    if isinstance(raw, (list, tuple, set)):
        return any(_present(v) for v in raw)
    return True


def _as_dict(raw: Any) -> dict[str, Any]:
    return raw if isinstance(raw, dict) else {}


def _truthy(raw: Any) -> bool:
    if raw is True:
        return True
    if raw is False or raw is None:
        return False
    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        return raw != 0
    s = str(raw).strip().lower()
    return s in {"1", "true", "yes", "on", "trip", "hit", "live"}


def _norm(raw: Any) -> str:
    return str(raw or "").strip()


def _norm_upper(raw: Any) -> str:
    return _norm(raw).upper()


def _mouth_keys_in(obj: Any, found: set[str] | None = None) -> set[str]:
    acc = found if found is not None else set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            lk = str(k).strip().lower()
            if lk in MOUTH_KEYS:
                acc.add(lk)
            _mouth_keys_in(v, acc)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            _mouth_keys_in(item, acc)
    return acc


def instrument_hash(bill: Any, control: Any = None) -> str | None:
    b = _as_dict(bill)
    c = _as_dict(control)
    if not _present(b) and not _present(c):
        return None
    body = {
        "spec": SPEC,
        "bill_id": _norm(b.get("id") or b.get("bill_id") or b.get("bl")) or None,
        "set": _norm(b.get("set") or b.get("originals")) or None,
        "platform": _norm(c.get("platform") or b.get("platform")) or None,
        "party": _norm(c.get("party") or b.get("party")) or None,
    }
    return hashlib.sha256(_canonical_json(body).encode("utf-8")).hexdigest()


def authority_hash(authority: Any) -> str | None:
    a = _as_dict(authority)
    h = _norm(a.get("instruction_hash") or a.get("hash") or a.get("written_hash"))
    if h:
        return h
    written = a.get("written_instruction") or a.get("instruction")
    if isinstance(written, dict) and _present(written):
        return hashlib.sha256(_canonical_json(written).encode("utf-8")).hexdigest()
    if isinstance(written, str) and written.strip():
        return hashlib.sha256(written.strip().encode("utf-8")).hexdigest()
    return None


def _instrument_state(bill: dict, control: dict) -> str:
    raw = _norm_upper(
        bill.get("state") or bill.get("instrument") or bill.get("originals_state")
    )
    if raw in INSTRUMENT:
        return raw
    if raw in {"CANCELLED", "SURRENDER"}:
        return "SURRENDERED"
    if _present(control.get("platform")):
        return "EBL_CONTROL"
    if not _present(bill):
        return "GAP"
    return "GAP"


def _telex_reply_to(telex: dict) -> bool:
    if not telex:
        return False
    channel = _norm(telex.get("channel") or telex.get("via") or telex.get("confirm_via")).lower()
    if channel in {"reply", "reply_to", "reply-to", "inbound_reply", "reply_button"}:
        return True
    inbound = _norm(telex.get("inbound_from") or telex.get("from")).lower()
    confirm = _norm(telex.get("confirm_to") or telex.get("to")).lower()
    if inbound and confirm and inbound == confirm:
        return True
    return False


def _control_mismatch(control: dict, instruction: dict) -> bool:
    left = _norm(control.get("platform")).lower()
    right = _norm(
        instruction.get("platform")
        or instruction.get("mouth_platform")
        or instruction.get("release_platform")
    ).lower()
    if left and right and left != right:
        return True
    return False


def _two_live_sets(switch: bool, first_set: str) -> bool:
    if not switch:
        return False
    return first_set not in {"CANCELLED", "SURRENDERED"}


def _charterer_only(authority: dict) -> bool:
    kind = _norm(authority.get("kind") or authority.get("principal_kind")).lower()
    if _present(authority.get("owner")) or _present(authority.get("master")):
        return False
    if _truthy(authority.get("charterer_only")):
        return True
    return kind in {"charterer", "charter", "c/p"}


def _base(decision: str, reason: str | None, **extra: Any) -> dict[str, Any]:
    halt = decision in {"HOLD", "NONEXIST"}
    out = {
        "spec": SPEC,
        "decision": decision,
        "status": decision,
        "halt": halt,
        "gap": decision == "GAP",
        "gap_reason": extra.pop("gap_reason", None),
        "reason": reason,
        "instrument_hash": extra.pop("instrument_hash", None),
        "authority_hash": extra.pop("authority_hash", None),
        "instrument_state": extra.pop("instrument_state", None),
        "control_platform": extra.pop("control_platform", None),
        "mouth_keys": extra.pop("mouth_keys", []),
        "required": extra.pop("required", False),
        "invariant": INVARIANT,
        "not": NOT,
    }
    out.update(extra)
    return out


def witness(
    *,
    bill: Any = None,
    authority: Any = None,
    control: Any = None,
    instruction: Any = None,
    telex: Any = None,
    loi: Any = None,
    switch: bool = False,
    first_set: Any = None,
    require: bool = False,
    mouth_keys: set[str] | None = None,
) -> dict[str, Any]:
    """EXIST = this file may open the gate. Never = the cargo is out."""
    b = _as_dict(bill)
    a = _as_dict(authority)
    c = _as_dict(control)
    ins = _as_dict(instruction)
    t = _as_dict(telex)
    l = _as_dict(loi)
    mouths = set(mouth_keys or ())
    inh = instrument_hash(b, c)
    ah = authority_hash(a)
    state = _instrument_state(b, c)
    platform = _norm(c.get("platform")) or None
    first = _norm_upper(first_set or b.get("first_set"))

    common = {
        "instrument_hash": inh,
        "authority_hash": ah,
        "instrument_state": state,
        "control_platform": platform,
        "required": require,
    }

    if mouths:
        return _base(
            "NONEXIST",
            "mouth_substitution",
            mouth_keys=sorted(mouths),
            **common,
        )

    if not _present(b) and not _present(c) and not require:
        return _base("GAP", None, gap_reason="missing_bill", mouth_keys=[], **common)

    if _telex_reply_to(t):
        return _base("NONEXIST", "telex_reply_to", mouth_keys=[], **common)

    if _two_live_sets(bool(switch) or _truthy(b.get("switch")), first):
        return _base("NONEXIST", "two_live_sets", mouth_keys=[], **common)

    if _control_mismatch(c, ins):
        return _base("NONEXIST", "control_platform_mismatch", mouth_keys=[], **common)

    switching = bool(switch) or _truthy(b.get("switch"))
    if switching and _charterer_only(a):
        return _base("NONEXIST", "charterer_only", mouth_keys=[], **common)

    if not _present(b) and not _present(c):
        return _base("HOLD", "missing_bill", mouth_keys=[], **common)

    if not ah:
        return _base("HOLD", "missing_principal", mouth_keys=[], **common)

    if state == "GAP":
        return _base("HOLD", "missing_instrument", mouth_keys=[], **common)

    if state == "OUTSTANDING" and not _present(l.get("hash") or l.get("form") or l.get("ig_form")):
        return _base("HOLD", "missing_loi", mouth_keys=[], **common)

    if state == "EBL_CONTROL" and not platform:
        return _base("HOLD", "missing_control", mouth_keys=[], **common)

    return _base("EXIST", None, mouth_keys=[], **common)


def from_body(
    body: dict | None,
    context: dict | None = None,
    policy: dict | None = None,
) -> dict[str, Any]:
    b = body if isinstance(body, dict) else {}
    ctx = context if isinstance(context, dict) else {}
    pol = policy if isinstance(policy, dict) else {}
    blob = b.get("release") or b.get("rel") or ctx.get("release") or {}
    if not isinstance(blob, dict):
        blob = {}
    bill = blob.get("bill") or b.get("bill") or ctx.get("bill")
    authority = blob.get("authority") or b.get("authority") or ctx.get("authority")
    control = blob.get("control") or b.get("control") or ctx.get("control")
    instruction = blob.get("instruction") or b.get("instruction") or ctx.get("instruction")
    telex = blob.get("telex") or b.get("telex")
    loi = blob.get("loi") or b.get("loi")
    switch = _truthy(blob.get("switch") or b.get("switch"))
    first_set = blob.get("first_set") or b.get("first_set")
    require = bool(pol.get("require_release") or blob.get("required") or b.get("require_release"))
    mouths = (
        _mouth_keys_in(blob)
        | _mouth_keys_in(bill)
        | _mouth_keys_in(authority)
        | _mouth_keys_in(telex)
        | _mouth_keys_in(instruction)
        | _mouth_keys_in(loi)
    )
    return witness(
        bill=bill,
        authority=authority,
        control=control,
        instruction=instruction,
        telex=telex,
        loi=loi,
        switch=switch,
        first_set=first_set,
        require=require,
        mouth_keys=mouths,
    )


def evaluate(body: dict | None, context: dict | None = None) -> dict[str, Any]:
    w = from_body(body, context=context)
    signals = [w["reason"]] if w.get("reason") else []
    evaluation_id = secrets.token_hex(16)
    token = receipt_mod.mint_receipt_jwt(
        evaluation_id=evaluation_id,
        decision=w["decision"],
        reason=w.get("reason"),
        instrument_hash=w.get("instrument_hash"),
        authority_hash=w.get("authority_hash"),
        control_platform=w.get("control_platform"),
        instrument_state=w.get("instrument_state"),
        signals=signals,
    )
    release_id = secrets.token_hex(8) if w["decision"] == "EXIST" else None
    return {
        "spec": SPEC,
        "decision": w["decision"],
        "halt": w["halt"],
        "release": w,
        "receipt": token,
        "release_id": release_id,
        "signals": signals,
        "evaluation_id": evaluation_id,
        "invariant": INVARIANT,
    }
