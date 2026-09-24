"""Five extra Apple mouths — unlock, Scenario 3, UAPA, ADMT, trusted-contact.

Sourced. One word. their_production stays false.
"""

from __future__ import annotations

import hashlib
import os
import sqlite3
import threading
from datetime import date
from typing import Any

ADMT_DEADLINE = date(2027, 1, 1)

POSITIVE_KINDS = (
    ("mga_bind", "MGA bind"),
    ("payroll", "Payroll"),
    ("access", "Access / keys"),
    ("benefits", "Benefits release"),
)

SCENARIO3_FLAGS = (
    ("known_supplier", "Known supplier asked to change where they get paid"),
    ("email_only", "That ask arrived only by email"),
    ("new_account", "New account number and/or location"),
    ("name_mismatch", "Wire names a beneficiary who is not the account holder"),
)

ADMT_CLASSES = (
    ("financial", "Financial or lending"),
    ("housing", "Housing"),
    ("education", "Education"),
    ("employment", "Employment or contracting"),
    ("compensation", "Compensation"),
    ("healthcare", "Healthcare services (statute lists it)"),
    ("ads", "Advertising only"),
    ("none", "Not a significant decision"),
)

_LOCK = threading.Lock()


def _hold_db() -> str:
    base = os.getenv("GATE_DB_PATH", "").strip()
    if base:
        if base.endswith(".db"):
            return base[:-3] + ".trusted-hold.db"
        return base + ".trusted-hold.db"
    return os.path.join("/tmp", "gate-trusted-hold.db")


def _hold_conn() -> sqlite3.Connection:
    path = _hold_db()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    c = sqlite3.connect(path, check_same_thread=False)
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS trusted_holds (
            account_key TEXT PRIMARY KEY,
            sealed_at TEXT NOT NULL
        )
        """
    )
    c.commit()
    return c


def _account_key(account_id: str) -> str:
    raw = (account_id or "").strip().lower().encode()
    return hashlib.sha256(raw).hexdigest() if raw else ""


def _base(public_url: str) -> str:
    return (public_url or "").rstrip("/")


def _pack(
    spec: str,
    word: str,
    plain: str,
    **extra: Any,
) -> dict[str, Any]:
    body = {
        "spec": spec,
        "word": word,
        "plain": plain,
        "their_production": False,
    }
    body.update(extra)
    return body


def evaluate_positive_clear(body: dict) -> dict[str, Any]:
    kind = str(body.get("kind") or "").strip()
    live = str(body.get("authority_live") or "").strip().lower()
    kinds = {k for k, _ in POSITIVE_KINDS}
    if kind not in kinds:
        return _pack(
            "gate-positive-clear-v1",
            "HOLD",
            "Pick what would unlock. Then say whether the sealed authority is live.",
        )
    if live not in ("yes", "no"):
        return _pack(
            "gate-positive-clear-v1",
            "HOLD",
            "Is the sealed authority still live? Yes or no. Unknown fails closed.",
            kind=kind,
        )
    if live == "no":
        return _pack(
            "gate-positive-clear-v1",
            "NO",
            "Do not unlock. The pen / hold / key is not live.",
            kind=kind,
        )
    return _pack(
        "gate-positive-clear-v1",
        "PROCEED",
        "May this irreversible unlock proceed — only while that sealed authority stays live.",
        kind=kind,
    )


def evaluate_scenario3(body: dict) -> dict[str, Any]:
    flags = {k: bool(body.get(k)) for k, _ in SCENARIO3_FLAGS}
    core = flags["known_supplier"] and flags["email_only"] and flags["new_account"]
    if not any(flags.values()):
        return _pack(
            "gate-scenario-3-v1",
            "HOLD",
            "Mark what you actually saw. Empty is not a no.",
            flags=flags,
            advisory="FIN-2016-A003",
            source="https://www.fincen.gov/resources/advisories/fincen-advisory-fin-2016-a003",
        )
    if core:
        extra = (
            " Receiving bank also sees the Scenario 3 red flag: beneficiary ≠ account holder."
            if flags["name_mismatch"]
            else ""
        )
        return _pack(
            "gate-scenario-3-v1",
            "MATCHES",
            "This is FinCEN Scenario 3: criminal impersonates a supplier." + extra,
            flags=flags,
            advisory="FIN-2016-A003",
            headline="SCENARIO 3 – CRIMINAL IMPERSONATES A SUPPLIER",
            source="https://www.fincen.gov/resources/advisories/fincen-advisory-fin-2016-a003",
        )
    return _pack(
        "gate-scenario-3-v1",
        "DOES NOT MATCH",
        "Not Scenario 3 as FinCEN wrote it. Other fraud can still be live.",
        flags=flags,
        advisory="FIN-2016-A003",
        source="https://www.fincen.gov/resources/advisories/fincen-advisory-fin-2016-a003",
    )


def evaluate_uapa(body: dict) -> dict[str, Any]:
    sent = str(body.get("already_sent") or "").strip().lower()
    authorized = str(body.get("authorized") or "").strip().lower()
    induced = str(body.get("induced") or "").strip().lower()
    rtp = str(body.get("rtp_native") or "").strip().lower()
    if sent != "yes":
        return _pack(
            "gate-uapa-seal-v1",
            "HOLD",
            "This mouth is post-send. If it has not gone, do not classify it as UAPA yet.",
            code="UAPA",
            source="https://www.neach.org/Solutions/Trends-Research/new-rtp174-fraud-codes-and-reporting-timelines",
        )
    if authorized == "no":
        return _pack(
            "gate-uapa-seal-v1",
            "FRAD",
            "Unauthorized. TCH uses FRAD here — not UAPA.",
            code="FRAD",
            source="https://www.neach.org/Solutions/Trends-Research/new-rtp174-fraud-codes-and-reporting-timelines",
        )
    if authorized != "yes" or induced not in ("yes", "no") or rtp not in ("yes", "no"):
        return _pack(
            "gate-uapa-seal-v1",
            "HOLD",
            "Need: already sent, authorized?, deceived?, RTP-native?",
            code="UAPA",
        )
    if rtp != "yes":
        return _pack(
            "gate-uapa-seal-v1",
            "NOT UAPA",
            "UAPA is a TCH RTP v5 reason code. This transfer is not RTP-native.",
            code="UAPA",
        )
    if induced == "yes":
        return _pack(
            "gate-uapa-seal-v1",
            "REPORTABLE",
            "Authorized but deceived (impersonation / BEC / romance / social engineering). TCH UAPA.",
            code="UAPA",
            effective="2026-03-31",
            source="https://www.neach.org/Solutions/Trends-Research/new-rtp174-fraud-codes-and-reporting-timelines",
        )
    return _pack(
        "gate-uapa-seal-v1",
        "NOT UAPA",
        "Sender authorized it and was not fraudulently induced. Not UAPA.",
        code="UAPA",
    )


def evaluate_admt(body: dict) -> dict[str, Any]:
    klass = str(body.get("decision_class") or "").strip()
    used = str(body.get("uses_admt") or "").strip().lower()
    notice = str(body.get("pre_use_notice") or "").strip().lower()
    today = date.today()
    clock = (
        f"Must comply with Article 11 by {ADMT_DEADLINE.isoformat()}."
        if today < ADMT_DEADLINE
        else "The § 7200(b) clock has already hit."
    )
    src = "https://govt.westlaw.com/calregs/Document/I038754709FAB11F08837960D0A0033B1"
    if klass == "ads":
        return _pack(
            "gate-admt-v1",
            "NOT ADMT",
            "Significant decision does not include advertising to a consumer. 11 CCR § 7001(ddd)(6).",
            clock=clock,
            source=src,
            cite="11 CCR § 7200(b)",
        )
    if klass == "none" or not klass:
        if not klass:
            return _pack(
                "gate-admt-v1",
                "HOLD",
                "Name the decision class. Empty is not a no.",
                clock=clock,
                source=src,
                cite="11 CCR § 7200(b)",
            )
        return _pack(
            "gate-admt-v1",
            "NOT ADMT",
            "Not a significant decision under 11 CCR § 7001(ddd). Article 11 does not attach.",
            clock=clock,
            source=src,
            cite="11 CCR § 7200(b)",
        )
    if used != "yes":
        return _pack(
            "gate-admt-v1",
            "NOT ADMT",
            "No automated decisionmaking technology on this significant decision.",
            clock=clock,
            source=src,
            cite="11 CCR § 7200(b)",
        )
    if notice == "yes":
        return _pack(
            "gate-admt-v1",
            "NOTICED",
            "Pre-use notice is on. Still bound by 11 CCR § 7200(b). " + clock,
            clock=clock,
            source=src,
            cite="11 CCR § 7200(b)",
        )
    return _pack(
        "gate-admt-v1",
        "NOTICE DUE",
        "Significant decision + ADMT, no pre-use notice. Seal this before Jan 1, 2027. " + clock,
        clock=clock,
        source=src,
        cite="11 CCR § 7200(b)",
    )


def evaluate_trusted_contact(body: dict) -> dict[str, Any]:
    account = str(body.get("account_id") or "").strip()
    action = str(body.get("action") or "check").strip().lower()
    if not account:
        return _pack(
            "gate-trusted-contact-v1",
            "MISSING",
            "Name the account. Unlock without a sealed trusted-contact hold is the miss.",
            cite="FINRA Rule 4512",
        )
    key = _account_key(account)
    with _LOCK:
        conn = _hold_conn()
        try:
            if action == "seal":
                conn.execute(
                    "INSERT OR REPLACE INTO trusted_holds(account_key, sealed_at) VALUES (?, datetime('now'))",
                    (key,),
                )
                conn.commit()
                return _pack(
                    "gate-trusted-contact-v1",
                    "HOLD",
                    "Trusted-contact hold is sealed on this account. Unlock has a person to call.",
                    account_key=key,
                    cite="FINRA Rule 4512",
                )
            row = conn.execute(
                "SELECT sealed_at FROM trusted_holds WHERE account_key = ?",
                (key,),
            ).fetchone()
        finally:
            conn.close()
    if row:
        return _pack(
            "gate-trusted-contact-v1",
            "HOLD",
            "A sealed trusted-contact hold is on file. Do not unlock around it.",
            account_key=key,
            sealed_at=row[0],
            cite="FINRA Rule 4512",
        )
    return _pack(
        "gate-trusted-contact-v1",
        "NO HOLD",
        "Unlock without a sealed trusted-contact hold. That is the miss.",
        account_key=key,
        cite="FINRA Rule 4512",
    )


MOUTHS = (
    {
        "id": "positive-clear",
        "route": "/positive-clear",
        "api": "/v1/positive-clear",
        "wk": "/.well-known/positive-clear.json",
        "fn": "evaluate_positive_clear",
        "spec": "gate-positive-clear-v1",
        "title": "Positive Clear",
        "brand": "Positive Clear",
        "lede": "May this irreversible unlock proceed?",
        "legend": (
            ("PROCEED", "Yes — the sealed authority is live."),
            ("NO", "Do not unlock."),
            ("HOLD", "Not enough. Fail closed."),
        ),
        "words": ["PROCEED", "NO", "HOLD"],
        "submit": "Ask",
        "fields": [
            {
                "name": "kind",
                "label": "What would unlock",
                "type": "chips",
                "options": [{"id": a, "label": b} for a, b in POSITIVE_KINDS],
            },
            {
                "name": "authority_live",
                "label": "Sealed authority still live?",
                "type": "chips",
                "options": [
                    {"id": "yes", "label": "Yes"},
                    {"id": "no", "label": "No"},
                ],
            },
        ],
        "source": "Inverse of Clear: proceed, not deny.",
    },
    {
        "id": "scenario-3",
        "route": "/scenario-3",
        "api": "/v1/scenario-3",
        "wk": "/.well-known/scenario-3.json",
        "fn": "evaluate_scenario3",
        "spec": "gate-scenario-3-v1",
        "title": "Scenario 3",
        "brand": "Scenario 3",
        "lede": "FIN-2016-A003 Scenario 3 — criminal impersonates a supplier.",
        "legend": (
            ("MATCHES", "This is Scenario 3 as FinCEN wrote it."),
            ("DOES NOT MATCH", "Not that fact pattern."),
            ("HOLD", "You have not marked what you saw."),
        ),
        "words": ["MATCHES", "DOES NOT MATCH", "HOLD"],
        "submit": "Check",
        "fields": [
            {
                "name": "flags",
                "label": "What you saw",
                "type": "checks",
                "options": [{"id": a, "label": b} for a, b in SCENARIO3_FLAGS],
            }
        ],
        "source": "FinCEN FIN-2016-A003 (Sept. 6, 2016).",
        "source_url": "https://www.fincen.gov/resources/advisories/fincen-advisory-fin-2016-a003",
    },
    {
        "id": "uapa-seal",
        "route": "/uapa-seal",
        "api": "/v1/uapa-seal",
        "wk": "/.well-known/uapa-seal.json",
        "fn": "evaluate_uapa",
        "spec": "gate-uapa-seal-v1",
        "title": "UAPA Seal",
        "brand": "UAPA Seal",
        "lede": "Was this transfer reportable under TCH UAPA? Post-send. Not a pre-push.",
        "legend": (
            ("REPORTABLE", "Authorized but deceived. UAPA."),
            ("FRAD", "Unauthorized. Use FRAD, not UAPA."),
            ("NOT UAPA", "Does not take the UAPA code."),
            ("HOLD", "Not enough, or it has not sent yet."),
        ),
        "words": ["REPORTABLE", "FRAD", "NOT UAPA", "HOLD"],
        "submit": "Classify",
        "fields": [
            {
                "name": "already_sent",
                "label": "Already sent?",
                "type": "chips",
                "options": [{"id": "yes", "label": "Yes"}, {"id": "no", "label": "No"}],
            },
            {
                "name": "authorized",
                "label": "Sender authorized it?",
                "type": "chips",
                "options": [{"id": "yes", "label": "Yes"}, {"id": "no", "label": "No"}],
            },
            {
                "name": "induced",
                "label": "Deceived into sending it?",
                "type": "chips",
                "options": [{"id": "yes", "label": "Yes"}, {"id": "no", "label": "No"}],
            },
            {
                "name": "rtp_native",
                "label": "RTP-native?",
                "type": "chips",
                "options": [{"id": "yes", "label": "Yes"}, {"id": "no", "label": "No"}],
            },
        ],
        "source": "TCH RTP reason code UAPA (authorized-but-deceived). Effective Mar 31, 2026.",
        "source_url": "https://www.neach.org/Solutions/Trends-Research/new-rtp174-fraud-codes-and-reporting-timelines",
    },
    {
        "id": "admt",
        "route": "/admt",
        "api": "/v1/admt",
        "wk": "/.well-known/admt.json",
        "fn": "evaluate_admt",
        "spec": "gate-admt-v1",
        "title": "ADMT",
        "brand": "ADMT",
        "lede": "Significant-decision notice Seal. 11 CCR § 7200(b). Clock: Jan 1, 2027.",
        "legend": (
            ("NOTICE DUE", "ADMT on a significant decision, no pre-use notice."),
            ("NOTICED", "Pre-use notice is on."),
            ("NOT ADMT", "Article 11 does not attach."),
            ("HOLD", "Name the class."),
        ),
        "words": ["NOTICE DUE", "NOTICED", "NOT ADMT", "HOLD"],
        "submit": "Seal",
        "fields": [
            {
                "name": "decision_class",
                "label": "Decision class",
                "type": "chips",
                "options": [{"id": a, "label": b} for a, b in ADMT_CLASSES],
            },
            {
                "name": "uses_admt",
                "label": "Using ADMT?",
                "type": "chips",
                "options": [{"id": "yes", "label": "Yes"}, {"id": "no", "label": "No"}],
            },
            {
                "name": "pre_use_notice",
                "label": "Pre-use notice already given?",
                "type": "chips",
                "options": [{"id": "yes", "label": "Yes"}, {"id": "no", "label": "No"}],
            },
        ],
        "source": "11 CCR § 7200(b). Compliance no later than January 1, 2027.",
        "source_url": "https://govt.westlaw.com/calregs/Document/I038754709FAB11F08837960D0A0033B1",
    },
    {
        "id": "trusted-contact",
        "route": "/trusted-contact",
        "api": "/v1/trusted-contact",
        "wk": "/.well-known/trusted-contact.json",
        "fn": "evaluate_trusted_contact",
        "spec": "gate-trusted-contact-v1",
        "title": "Trusted Contact",
        "brand": "Trusted Contact",
        "lede": "Unlock without a sealed trusted-contact hold?",
        "legend": (
            ("NO HOLD", "No sealed hold. That is the miss."),
            ("HOLD", "Sealed. Do not unlock around it."),
            ("MISSING", "Name the account."),
        ),
        "words": ["NO HOLD", "HOLD", "MISSING"],
        "submit": "Check",
        "alt_submit": {"action": "seal", "label": "Seal hold"},
        "fields": [
            {
                "name": "account_id",
                "label": "Account",
                "type": "text",
                "placeholder": "account id (hashed here — not stored raw)",
            }
        ],
        "source": "FINRA Rule 4512 trusted contact person. Same hold shape as a bind ticket.",
    },
)


def mouth_by_id(mid: str) -> dict | None:
    for m in MOUTHS:
        if m["id"] == mid:
            return m
    return None


def evaluate(mid: str, body: dict) -> dict[str, Any]:
    fn = {
        "positive-clear": evaluate_positive_clear,
        "scenario-3": evaluate_scenario3,
        "uapa-seal": evaluate_uapa,
        "admt": evaluate_admt,
        "trusted-contact": evaluate_trusted_contact,
    }[mid]
    return fn(body if isinstance(body, dict) else {})


def manifest(mid: str, public_url: str) -> dict[str, Any]:
    m = mouth_by_id(mid)
    if not m:
        return {"error": "unknown_mouth"}
    base = _base(public_url)
    return {
        "spec": m["spec"],
        "name": m["title"],
        "promise": m["lede"],
        "words": list(m["words"]),
        "page": f"{base}{m['route']}",
        "api": f"{base}{m['api']}",
        "source": m.get("source"),
        "their_production": False,
    }
