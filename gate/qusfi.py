"""QUSFI lookup — Model 785 credit-for-reinsurance LOC issuers, not a bank score.

Public NAIC SVO lists, dated, hashed. Confirmation by phone or email-on-the-instrument
is HALT. Off the current list means the next evergreen/renewal cannot support surplus
credit; Model 786 §11A(3) grandfathers paper that was acceptable at issuance until
expiry, extension, renewal, modification, or amendment.
"""
from __future__ import annotations

import calendar
import json
import os
from datetime import date
from typing import Any

SPEC = "gate-qusfi-v1"
CURRENT_AS_OF = "2026-09-30"
PRIOR_AS_OF = "2025-12-31"
CCB_NY_ABA = "26014685"
BOC_NY_ABA = "26003269"
ABC_NY_ABA = "133951245"

CURRENT_URL = "https://staspoprodcus01.blob.core.windows.net/svo/svo_qusfi_list.pdf"
PRIOR_URL = (
    "https://content.naic.org/sites/default/files/"
    "svo-archive-2025-qualified-us-financial-institutions-qufsi.pdf"
)
MODEL_785 = "https://content.naic.org/sites/default/files/model-law-785.pdf"
MODEL_786 = "https://content.naic.org/sites/default/files/model-law-786.pdf"
ARTEMIS_CORINTHIAN = (
    "https://www.artemis.bm/news/"
    "vesttoo-collateral-loc-issues-werent-spotted-by-multiple-parties-involved/"
)
AIRROC_VESTTOO = (
    "https://www.airrocupdate.org/letters-of-credit-the-good-the-bad-and-the-vesttoo"
)
Y5410 = (
    "https://assets.lloyds.com/media/37cc57c7-df41-4058-a085-628c4b0ad478/Y5410.pdf"
)
Y5410_DATED = "2023-10-03"
Y5410_SPEC = "lloyds-y5410-v1"

SCOPE = (
    "NAIC Credit for Reinsurance Model Law (#785) section 3C(1) and section 4A — "
    "issuers of letters of credit as collateral in reinsurance arrangements. "
    "Not a general bank creditworthiness score. The SVO list footer forbids other uses."
)
GRANDFATHER = (
    "Letters of credit meeting applicable standards of issuer acceptability as of "
    "the dates of their issuance (or confirmation) shall, notwithstanding the "
    "issuing (or confirming) institution's subsequent failure to meet applicable "
    "standards of issuer acceptability, continue to be acceptable as security until "
    "their expiration, extension, renewal, modification or amendment, whichever "
    "first occurs. (NAIC Model 786 §11A(3).)"
)
CLAIM_OFF_LIST = (
    "This issuer is off the current list, so the next evergreen/renewal cannot "
    "support surplus credit."
)
NOT_A_CLAIM = (
    "Existing letters issued while the issuer was qualified are not automatically dead."
)
CLAIM_Y5410 = (
    "Issuing-bank six-month confirm is missing or overdue. Lloyd's Y5410 "
    "(3 Oct 2023) may discount this LOC in the member's Funds at Lloyd's until "
    "the bank confirms."
)
NOT_A_CLAIM_Y5410 = (
    "Y5410 is a Lloyd's FAL discount right. It is not NAIC Model 785 surplus credit "
    "and it does not by itself kill a grandfathered US credit-for-reinsurance letter."
)

DEAD_CHANNELS = frozenset(
    {
        "phone",
        "voice",
        "call",
        "call_to_confirm",
        "voice_confirm",
        "email_on_instrument",
        "email",
        "domain_email",
        "fax",
    }
)
OWN_BANK_CHANNELS = frozenset(
    {
        "advised_mt760_via_own_bank",
        "mt760",
        "swift_advised_own_bank",
    }
)
RENEWAL_EVENTS = frozenset(
    {
        "renewal",
        "extension",
        "modification",
        "amendment",
        "evergreen",
        "new_issuance",
    }
)

def _parse_date(raw: str | None) -> date | None:
    s = (raw or "").strip()[:10]
    if not s:
        return None
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


def _add_calendar_months(d: date, months: int) -> date:
    total = d.month - 1 + months
    y = d.year + total // 12
    m = total % 12 + 1
    return date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def clocks() -> dict[str, Any]:
    return {
        "next_svo_list": (
            "QUSFI membership is the dated PDF. A later list replaces the set; "
            "it does not by itself kill paper grandfathered under Model 786 §11A(3)."
        ),
        "next_786_event": (
            "Grandfather ends at expiry, extension, renewal, modification, or "
            "amendment — whichever first occurs."
        ),
        "publication": {
            "cadence": "monthly",
            "live_url": CURRENT_URL,
            "note": (
                "SVO updates the list in real time internally and publishes the PDF "
                "monthly (QUSFI FAQ). Gate vendors the dated PDF hash. "
                "python3 gate/watch_qusfi.py hashes the live PDF and fails if it moved."
            ),
            "watch": "/watch/qusfi.py",
            "faq": "https://content.naic.org/sites/default/files/svo-qusfi-faq.pdf",
        },
        "lloyds_six_month_confirm": {
            "spec": Y5410_SPEC,
            "bulletin": "Y5410",
            "dated": Y5410_DATED,
            "months": 6,
            "scope": (
                "Member Funds at Lloyd's / ECA Tier 2 letters of credit, bank "
                "guarantees and life policies. Not NAIC Model 785 surplus credit."
            ),
            "rule": (
                "Lloyd's require all issuing banks to confirm the validity of each "
                "LOC issued on behalf of members on a six-monthly basis. If this "
                "confirmation is not provided, Lloyd's reserves the right to discount "
                "the value of the LOC as part of a member's FAL until the bank "
                "confirms. (Y5410, 3 Oct 2023.)"
            ),
            "lodging": (
                "LOCs supporting an Economic Capital Assessment must be lodged in "
                "accordance with the May/November FAL timetable."
            ),
            "source": Y5410,
            "apply": (
                "POST /v1/qusfi/check with lloyds_fal=yes and "
                "issuing_bank_confirm_at=YYYY-MM-DD"
            ),
            "not_a_claim": NOT_A_CLAIM_Y5410,
        },
    }


def lloyds_confirm(body: dict[str, Any]) -> dict[str, Any]:
    """Six-month issuing-bank confirm. FAL only. Opt-in via lloyds_fal=yes."""
    as_of = _parse_date(str(body.get("as_of") or "")) or date.today()
    out: dict[str, Any] = {
        "spec": Y5410_SPEC,
        "applied": False,
        "as_of": as_of.isoformat(),
        "not_naic_surplus_credit": True,
        "not_a_claim": NOT_A_CLAIM_Y5410,
        "source": Y5410,
    }
    flag = str(body.get("lloyds_fal") or "").strip().lower()
    if flag not in {"yes", "true", "1", "fal"}:
        out["hint"] = (
            "Set lloyds_fal=yes to apply the six-month issuing-bank confirm. "
            "This clock is Funds at Lloyd's, not Model 785 surplus credit."
        )
        return out
    out["applied"] = True
    confirm = _parse_date(
        str(body.get("issuing_bank_confirm_at") or body.get("lloyds_six_month_confirm_at") or "")
    )
    if confirm is None:
        out["ok"] = False
        out["confirm_at"] = None
        out["due"] = None
        out["reason"] = CLAIM_Y5410
        return out
    due = _add_calendar_months(confirm, 6)
    out["confirm_at"] = confirm.isoformat()
    out["due"] = due.isoformat()
    out["ok"] = as_of <= due
    if not out["ok"]:
        out["reason"] = CLAIM_Y5410
    return out


_DATA: dict[str, Any] | None = None


def _data_path() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "data", "qusfi_lists.json")


def load_lists() -> dict[str, Any]:
    global _DATA
    if _DATA is None:
        with open(_data_path(), encoding="utf-8") as fh:
            _DATA = json.load(fh)
    return _DATA


def _list_by_as_of(as_of: str) -> dict[str, Any]:
    for row in load_lists()["lists"]:
        if row["as_of"] == as_of:
            return row
    raise KeyError(as_of)


def _index(as_of: str) -> dict[str, dict[str, Any]]:
    return {inst["id"]: inst for inst in _list_by_as_of(as_of)["institutions"]}


def normalize_id(raw: str) -> str:
    text = (raw or "").strip().upper().replace("-", "").replace(" ", "")
    if text.isdigit():
        return text.lstrip("0") or "0"
    return text


def _list_meta(as_of: str) -> dict[str, Any]:
    row = _list_by_as_of(as_of)
    return {
        "as_of": row["as_of"],
        "title": row["title"],
        "source_url": row["source_url"],
        "pdf_sha256": row["pdf_sha256"],
        "institution_count": row["institution_count"],
    }


def _membership(as_of: str, ident: str) -> dict[str, Any]:
    inst = _index(as_of).get(ident)
    meta = _list_meta(as_of)
    out = dict(meta)
    out["on_list"] = inst is not None
    if inst:
        out["institution"] = inst
    return out


def head(public_url: str = "") -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    current = _list_meta(CURRENT_AS_OF)
    prior = _list_meta(PRIOR_AS_OF)
    return {
        "spec": SPEC,
        "scope": SCOPE,
        "purpose": "Credit for reinsurance letters of credit. Not a bank score.",
        "current": current,
        "prior": prior,
        "grandfather": GRANDFATHER,
        "claim_when_off_current_list": CLAIM_OFF_LIST,
        "not_a_claim": NOT_A_CLAIM,
        "clocks": clocks(),
        "sources": {
            "model_785": MODEL_785,
            "model_786": MODEL_786,
            "artemis_corinthian_voice_email": ARTEMIS_CORINTHIAN,
            "airroc_spoofed_phone": AIRROC_VESTTOO,
            "lloyds_y5410": Y5410,
        },
        "confirmation": {
            "phone_or_email_on_instrument": "HALT",
            "advised_mt760_via_own_bank": "required_channel_for_any_clear",
            "call_to_confirm_path": False,
        },
        "urls": {
            "head": f"{base}/.well-known/qusfi.json" if base else "/.well-known/qusfi.json",
            "lookup": f"{base}/v1/qusfi" if base else "/v1/qusfi",
            "check": f"{base}/v1/qusfi/check" if base else "/v1/qusfi/check",
            "diff": f"{base}/v1/qusfi/diff" if base else "/v1/qusfi/diff",
            "watch": f"{base}/watch/qusfi.py" if base else "/watch/qusfi.py",
        },
        "their_production": False,
    }


def available_as_of() -> list[str]:
    return [row["as_of"] for row in load_lists()["lists"]]


def diff(from_as_of: str | None = None, to_as_of: str | None = None) -> dict[str, Any]:
    """Set difference of two dated QUSFI lists. Search as a drop list, not a database."""
    start = (from_as_of or PRIOR_AS_OF).strip()
    end = (to_as_of or CURRENT_AS_OF).strip()
    known = available_as_of()
    if start not in known or end not in known:
        return {
            "spec": SPEC,
            "error": "unknown_list_date",
            "known_as_of": known,
            "scope": SCOPE,
        }
    old = _index(start)
    new = _index(end)
    dropped_ids = sorted(set(old) - set(new), key=lambda i: (len(i), i))
    added_ids = sorted(set(new) - set(old), key=lambda i: (len(i), i))
    dropped = [old[i] for i in dropped_ids]
    added = [new[i] for i in added_ids]
    body: dict[str, Any] = {
        "spec": SPEC,
        "from": _list_meta(start),
        "to": _list_meta(end),
        "dropped": dropped,
        "added": added,
        "dropped_count": len(dropped),
        "added_count": len(added),
        "scope": SCOPE,
        "not_a_score": (
            "A dropped ABA is off the later list. That is not a credit rating. "
            "Model 786 §11A(3) still grandfathers paper that was acceptable at issuance."
        ),
        "claim_when_dropped": CLAIM_OFF_LIST,
        "not_a_claim": NOT_A_CLAIM,
        "their_production": False,
    }
    if CCB_NY_ABA in dropped_ids:
        body["example"] = {
            "id": CCB_NY_ABA,
            "label": old[CCB_NY_ABA]["label"],
            "claim": CLAIM_OFF_LIST,
        }
    return body


def lookup(ident: str) -> dict[str, Any]:
    aba = normalize_id(ident)
    if not aba:
        return {
            "spec": SPEC,
            "error": "missing_id",
            "hint": "GET /v1/qusfi?aba=26014685",
            "scope": SCOPE,
        }
    current = _membership(CURRENT_AS_OF, aba)
    prior = _membership(PRIOR_AS_OF, aba)
    body: dict[str, Any] = {
        "spec": SPEC,
        "id": aba,
        "current": current,
        "prior": prior,
        "scope": SCOPE,
        "grandfather": GRANDFATHER,
        "their_production": False,
    }
    if not current["on_list"]:
        body["claim"] = CLAIM_OFF_LIST
        body["not_a_claim"] = NOT_A_CLAIM
    return body


def _halt(reason: str, extra: dict[str, Any]) -> dict[str, Any]:
    out = {
        "spec": SPEC,
        "word": "HALT",
        "halt": True,
        "reason": reason,
        "scope": SCOPE,
        "their_production": False,
    }
    out.update(extra)
    return _apply_y5410(out)


def _apply_y5410(out: dict[str, Any]) -> dict[str, Any]:
    """Empty/overdue six-month confirm HALTs FAL treatment. Does not override an earlier HALT reason."""
    y = out.get("lloyds_y5410") or {}
    if y.get("applied") and y.get("ok") is False and not out.get("halt"):
        out["word"] = "HALT"
        out["halt"] = True
        out["reason"] = CLAIM_Y5410
        out["not_a_claim_y5410"] = NOT_A_CLAIM_Y5410
    return out


def check(body: dict[str, Any]) -> dict[str, Any]:
    ident = normalize_id(str(body.get("aba") or body.get("id") or ""))
    channel = str(body.get("confirmation_channel") or "").strip().lower()
    event = str(body.get("event") or "").strip().lower()
    found = lookup(ident) if ident else lookup("")
    extra = {
        "id": ident or None,
        "confirmation_channel": channel or None,
        "event": event or None,
        "current": found.get("current"),
        "prior": found.get("prior"),
        "grandfather": GRANDFATHER,
        "sources": {
            "artemis_corinthian_voice_email": ARTEMIS_CORINTHIAN,
            "airroc_spoofed_phone": AIRROC_VESTTOO,
        },
        "call_to_confirm_path": False,
        "clocks": clocks(),
        "lloyds_y5410": lloyds_confirm(body),
    }
    if not ident:
        return _halt("Name the issuer ABA/LEI. Empty is not qualified.", extra)
    if not channel or channel in DEAD_CHANNELS or channel not in OWN_BANK_CHANNELS:
        return _halt(
            "Phone, voice, or email-on-the-instrument confirmation is HALT. "
            "Corinthian voice- and email-confirmed CCB letters; AIRROC describes a "
            "fictitious employee and a spoofed bank phone. Only an MT760 advised "
            "through the beneficiary's own bank is an allowed channel — and that "
            "still does not make an off-list issuer qualified for the next renewal.",
            extra,
        )
    on_current = bool(found.get("current", {}).get("on_list"))
    if not on_current and (not event or event in RENEWAL_EVENTS):
        extra["claim"] = CLAIM_OFF_LIST
        extra["not_a_claim"] = NOT_A_CLAIM
        return _halt(CLAIM_OFF_LIST, extra)
    if not on_current and event in {"existing", "grandfathered"}:
        extra["claim"] = CLAIM_OFF_LIST
        extra["not_a_claim"] = NOT_A_CLAIM
        extra["word"] = "HOLD"
        extra["halt"] = False
        extra["reason"] = (
            "Issuer is off the current list. Model 786 §11A(3) may still cover this "
            "letter until expiry, extension, renewal, modification, or amendment. "
            "The next evergreen/renewal cannot support surplus credit."
        )
        extra["spec"] = SPEC
        extra["scope"] = SCOPE
        extra["their_production"] = False
        return _apply_y5410(extra)
    extra["word"] = "CLEAR"
    extra["halt"] = False
    extra["reason"] = (
        "Issuer is on the current QUSFI list and confirmation is advised MT760 via "
        "the beneficiary's own bank. This is not a production weld and is not a "
        "bank-quality score."
    )
    extra["spec"] = SPEC
    extra["scope"] = SCOPE
    extra["their_production"] = False
    return _apply_y5410(extra)
