"""QUSFI lookup — Model 785 credit-for-reinsurance LOC issuers, not a bank score.

Public NAIC SVO lists, dated, hashed. Confirmation by phone or email-on-the-instrument
is HALT. Off the current list means the next evergreen/renewal cannot support surplus
credit; Model 786 §11A(3) grandfathers paper that was acceptable at issuance until
expiry, extension, renewal, modification, or amendment.
"""
from __future__ import annotations

import json
import os
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
        "sources": {
            "model_785": MODEL_785,
            "model_786": MODEL_786,
            "artemis_corinthian_voice_email": ARTEMIS_CORINTHIAN,
            "airroc_spoofed_phone": AIRROC_VESTTOO,
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
        },
        "their_production": False,
    }


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
        return extra
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
    return extra
