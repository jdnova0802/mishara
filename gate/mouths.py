"""Extra Apple mouths — unlock, Scenario 3, UAPA, ADMT, trusted-contact,
FedNow pre-push, Nacha False Pretenses, CL7 handoff, Stair, DSP reject-report.

Visa agentic chargebacks: PARKED (see PARKED_MOUTHS).
their_production stays false on manifests; HTTP scrub omits when false.
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


def _seal_mouth(
    *,
    mouth_id: str,
    body: dict[str, Any],
    inputs: dict,
    logs: list[str] | None = None,
    counterparties: list[str] | None = None,
    advisory: bool = True,
) -> dict[str, Any]:
    """Attach signed claim_scope + write_state on mouth responses."""
    try:
        from gate import claim_scope as claim_scope_mod
    except ImportError:
        import claim_scope as claim_scope_mod
    try:
        from gate import write_state as write_state_mod
    except ImportError:
        import write_state as write_state_mod

    out = dict(body)
    if advisory and "write_state" not in out:
        out["write_state"] = write_state_mod.for_advisory_mouth(mouth_id=mouth_id)
    scope = claim_scope_mod.for_mouth(
        mouth_id=mouth_id,
        word=str(out.get("word") or ""),
        inputs=inputs,
        logs=logs,
        counterparties=counterparties,
    )
    # Sign every decisive word (including PROCEED/CLEAR/MATCHES) so scope is always
    # stranger-verifiable; negative words are the critical case.
    return claim_scope_mod.attach(out, scope=scope, force=True)


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


def evaluate_stair(body: dict) -> dict[str, Any]:
    kind = str(body.get("kind") or "").strip()
    src = "https://up.codes/s/sensor-release-of-electrically-locked-egress-doors"
    if kind == "egress_lock":
        return _pack(
            "gate-stair-v1",
            "NEVER",
            "Occupied egress. Power loss and alarm shall unlock. We will not weld fail-closed on that door.",
            cite="IBC sensor-release of electrically locked egress doors",
            source=src,
        )
    if kind == "money_or_bind":
        return _pack(
            "gate-stair-v1",
            "NOT THIS",
            "Not a stair. Fail-closed still applies. Use Clear / Go.",
            cite="IBC sensor-release of electrically locked egress doors",
            source=src,
        )
    return _pack(
        "gate-stair-v1",
        "HOLD",
        "Name the write. Empty is not a no.",
        cite="IBC sensor-release of electrically locked egress doors",
        source=src,
    )


def evaluate_fednow_prepush(body: dict) -> dict[str, Any]:
    """FedNow/RTP irrevocable credit-push — pre-transaction Never mouth.

    Cite: U.S. Faster Payments Council, Instant Payments Fraud Dispute Resolution
    Guiding Principles (May 15, 2026). Directional industry guidance — not a Fed order.
    """
    src = (
        "https://fasterpaymentscouncil.org/blog/17139/"
        "U-S-Faster-Payments-Council-Releases-Guiding-Principles-for-Instant-Payments-Fraud-Dispute-Resolution"
    )
    rail = str(body.get("rail") or "").strip().lower()
    payee_sealed = str(body.get("payee_sealed") or "").strip().lower()
    first_time = str(body.get("first_time_payee") or "").strip().lower()
    suspected = str(body.get("fraud_suspected") or "").strip().lower()
    if rail not in ("fednow", "rtp"):
        return _pack(
            "gate-fednow-prepush-v1",
            "HOLD",
            "Name the rail: FedNow or RTP. Empty is not a no.",
            cite="U.S. Faster Payments Council — Instant Payments Fraud Dispute Resolution (May 15, 2026)",
            source=src,
        )
    if payee_sealed not in ("yes", "no") or first_time not in ("yes", "no") or suspected not in (
        "yes",
        "no",
    ):
        return _pack(
            "gate-fednow-prepush-v1",
            "HOLD",
            "Need: payee sealed?, first-time payee?, fraud suspected? Unknown fails closed.",
            rail=rail,
            cite="U.S. Faster Payments Council — Instant Payments Fraud Dispute Resolution (May 15, 2026)",
            source=src,
        )
    if suspected == "yes":
        return _pack(
            "gate-fednow-prepush-v1",
            "NEVER",
            "Fraud suspected on an irrevocable credit-push. FPC Principle 6: sending FI may slow, limit, or reject.",
            rail=rail,
            cite="U.S. Faster Payments Council — Instant Payments Fraud Dispute Resolution (May 15, 2026)",
            source=src,
        )
    if payee_sealed != "yes":
        return _pack(
            "gate-fednow-prepush-v1",
            "NEVER",
            "Irrevocable push without a sealed payee/mandate check. Pre-transaction control missing (FPC Principle 5).",
            rail=rail,
            cite="U.S. Faster Payments Council — Instant Payments Fraud Dispute Resolution (May 15, 2026)",
            source=src,
        )
    if first_time == "yes":
        return _pack(
            "gate-fednow-prepush-v1",
            "HOLD",
            "First-time payee on irrevocable rail. Confirm of payee / risk prompt before push.",
            rail=rail,
            cite="U.S. Faster Payments Council — Instant Payments Fraud Dispute Resolution (May 15, 2026)",
            source=src,
        )
    return _pack(
        "gate-fednow-prepush-v1",
        "CLEAR",
        "Payee sealed, not first-time, no fraud flag — may this FedNow/RTP push proceed under that seal.",
        rail=rail,
        cite="U.S. Faster Payments Council — Instant Payments Fraud Dispute Resolution (May 15, 2026)",
        source=src,
        note="FPC principles are directional — not a binding Fed mandate.",
    )


def evaluate_nacha_false_pretenses(body: dict) -> dict[str, Any]:
    """ACH credit under Nacha False Pretenses risk — sibling of Scenario 3.

    Cite: Nacha Risk Management Phase 1 (Mar 20, 2026) / Phase 2 (Jun 19, 2026).
    Monitoring duty — not a mandatory pre-push Never rule; Gate still fail-closes on blank.
    """
    src = "https://www.nacha.org/news/new-nacha-risk-management-rules-now-effect"
    role = str(body.get("role") or "").strip().lower()
    suspected = str(body.get("false_pretenses_suspected") or "").strip().lower()
    who_checked = str(body.get("who_what_payee_sealed") or "").strip().lower()
    if role not in ("odfi", "rdfi", "originator"):
        return _pack(
            "gate-nacha-false-pretenses-v1",
            "HOLD",
            "Name the role: ODFI, RDFI, or Originator. Empty is not a no.",
            cite="Nacha Risk Management — False Pretenses (Phase 1 Mar 20 2026 / Phase 2 Jun 19 2026)",
            source=src,
        )
    if suspected not in ("yes", "no") or who_checked not in ("yes", "no"):
        return _pack(
            "gate-nacha-false-pretenses-v1",
            "HOLD",
            "Need: False Pretenses suspected?, who/what/payee sealed? Unknown fails closed.",
            role=role,
            cite="Nacha Risk Management — False Pretenses (Phase 1 Mar 20 2026 / Phase 2 Jun 19 2026)",
            source=src,
        )
    if suspected == "yes" and who_checked != "yes":
        return _pack(
            "gate-nacha-false-pretenses-v1",
            "NEVER",
            "False Pretenses suspected (identity / authority / account ownership lie) without sealed who/what/payee.",
            role=role,
            cite="Nacha Risk Management — False Pretenses (Phase 1 Mar 20 2026 / Phase 2 Jun 19 2026)",
            source=src,
            definition=(
                "Inducement by misrepresenting identity, association/authority, "
                "or ownership of the account to be credited."
            ),
        )
    if suspected == "yes":
        return _pack(
            "gate-nacha-false-pretenses-v1",
            "HOLD",
            "Suspected False Pretenses with a sealed check on file — human review before ACH credit.",
            role=role,
            cite="Nacha Risk Management — False Pretenses (Phase 1 Mar 20 2026 / Phase 2 Jun 19 2026)",
            source=src,
        )
    return _pack(
        "gate-nacha-false-pretenses-v1",
        "CLEAR",
        "No False Pretenses flag and who/what/payee sealed — may this ACH credit proceed under that seal.",
        role=role,
        cite="Nacha Risk Management — False Pretenses (Phase 1 Mar 20 2026 / Phase 2 Jun 19 2026)",
        source=src,
        note="Nacha requires risk-based monitoring; it does not itself mandate a pre-posting Never.",
    )


def evaluate_cl7_handoff(body: dict) -> dict[str, Any]:
    """NYDFS CL7 — AIS/ECDIS path → manual underwriting handoff notice Seal.

    AIS = Artificial Intelligence Systems. ECDIS = External Consumer Data and
    Information Sources (insurance — not maritime ECDIS).
    Cite: NYDFS Insurance Circular Letter No. 7 (2024), July 11, 2024.
    """
    src = "https://www.dfs.ny.gov/industry-guidance/circular-letters/cl2024-07"
    handoff = str(body.get("ais_ecdis_handoff") or "").strip().lower()
    noticed = str(body.get("written_notice_15d") or "").strip().lower()
    if handoff not in ("yes", "no"):
        return _pack(
            "gate-cl7-handoff-v1",
            "HOLD",
            "Did an AIS/ECDIS path hand the applicant to non-AIS underwriting? Empty is not a no.",
            cite="NYDFS Insurance Circular Letter No. 7 (2024)",
            source=src,
            expand="AIS=Artificial Intelligence Systems; ECDIS=External Consumer Data and Information Sources (insurance).",
        )
    if handoff == "no":
        return _pack(
            "gate-cl7-handoff-v1",
            "NOT THIS",
            "No AIS/ECDIS → manual handoff. CL7 15-day notice clause does not attach.",
            cite="NYDFS Insurance Circular Letter No. 7 (2024)",
            source=src,
        )
    if noticed not in ("yes", "no"):
        return _pack(
            "gate-cl7-handoff-v1",
            "HOLD",
            "Handoff happened. Was written notice given within 15 days with reasons?",
            cite="NYDFS Insurance Circular Letter No. 7 (2024)",
            source=src,
        )
    if noticed == "yes":
        return _pack(
            "gate-cl7-handoff-v1",
            "SEALED",
            "AIS/ECDIS handoff noticed in writing within 15 days. Seal holds; continue non-AIS process.",
            cite="NYDFS Insurance Circular Letter No. 7 (2024)",
            source=src,
        )
    return _pack(
        "gate-cl7-handoff-v1",
        "NEVER",
        "Silent drop from AIS/ECDIS path to manual — no written 15-day notice. CL7 says that may be an unfair trade practice.",
        cite="NYDFS Insurance Circular Letter No. 7 (2024)",
        source=src,
    )


# Countries of concern under EO 14117 / 28 CFR Part 202 (DSP) — as listed in the final rule.
DSP_COUNTRIES_OF_CONCERN = (
    "china",
    "cuba",
    "iran",
    "north_korea",
    "russia",
    "venezuela",
)

DSP_NSD_EMAIL = "NSD.FIRS.datasecurity@usdoj.gov"
DSP_OPERATIVE_DATE = "2025-10-06"
DSP_SOURCE = (
    "https://www.ecfr.gov/current/title-28/chapter-I/part-202/subpart-K/section-202.1104"
)
DSP_FR = (
    "https://www.federalregister.gov/documents/2025/01/08/2024-31486/"
    "preventing-access-to-us-sensitive-personal-data-and-government-related-data-by-countries-of-concern"
)


def _dsp_due_at(rejected_at_iso: str) -> str:
    from datetime import datetime, timedelta, timezone

    raw = (rejected_at_iso or "").strip()
    try:
        if len(raw) == 10 and raw[4] == "-" and raw[7] == "-":
            dt = datetime.fromisoformat(raw).replace(tzinfo=timezone.utc)
        else:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
    except ValueError:
        dt = datetime.now(timezone.utc)
    return (dt + timedelta(days=14)).replace(microsecond=0).isoformat()


def evaluate_dsp_reject(body: dict) -> dict[str, Any]:
    """DOJ Data Security Program — § 202.1104 rejected prohibited data-brokerage report.

    Live duty (on/after Oct 6, 2025): U.S. person who affirmatively rejects (including
    via software) an offer for a prohibited data-brokerage transaction must report to
    NSD within 14 days. Gate classifies + packs; Gate never files.
    """
    try:
        from gate import write_state as write_state_mod
    except ImportError:
        import write_state as write_state_mod

    brokerage = str(body.get("data_brokerage_offer") or "").strip().lower()
    bulk = str(body.get("bulk_sensitive_or_gov_data") or "").strip().lower()
    covered = str(body.get("counterparty_covered_or_coc") or "").strip().lower()
    rejected = str(body.get("affirmatively_rejected") or "").strip().lower()
    operative = str(body.get("rejected_on_or_after_2025_10_06") or "").strip().lower()
    reject_date = str(body.get("reject_date") or "").strip()

    cite = "28 CFR § 202.1104 — Reports on rejected prohibited transactions"
    common = dict(cite=cite, source=DSP_SOURCE, fr=DSP_FR, operative_date=DSP_OPERATIVE_DATE)

    if brokerage not in ("yes", "no") or bulk not in ("yes", "no") or covered not in (
        "yes",
        "no",
        "unknown",
    ):
        return _pack(
            "gate-dsp-reject-v1",
            "HOLD",
            "Need: data-brokerage offer?, bulk sensitive/gov data?, counterparty covered/CoC? Unknown fails closed.",
            **common,
        )
    if rejected not in ("yes", "no") or operative not in ("yes", "no"):
        return _pack(
            "gate-dsp-reject-v1",
            "HOLD",
            "Need: affirmatively rejected (incl. auto)?, on/after Oct 6 2025? Empty is not a no.",
            **common,
        )

    if brokerage != "yes" or bulk != "yes":
        return _pack(
            "gate-dsp-reject-v1",
            "NOT THIS",
            "§ 202.1104 attaches to rejected prohibited data-brokerage offers involving "
            "government-related or bulk U.S. sensitive personal data. This face does not match.",
            write_state=write_state_mod.for_advisory_mouth(mouth_id="dsp-reject"),
            **common,
        )
    if covered == "unknown":
        return _pack(
            "gate-dsp-reject-v1",
            "HOLD",
            "Counterparty covered-person / country-of-concern status unknown. "
            "Covered Persons List is non-exhaustive for § 202.211(a)(1)–(4) — fail closed.",
            covered_persons_list_exhaustive=False,
            **common,
        )
    if covered != "yes":
        return _pack(
            "gate-dsp-reject-v1",
            "NOT THIS",
            "No covered person / country of concern on this face — not a prohibited DSP "
            "data-brokerage offer as presented. Still do your own diligence.",
            write_state=write_state_mod.for_advisory_mouth(mouth_id="dsp-reject"),
            **common,
        )
    if operative != "yes":
        return _pack(
            "gate-dsp-reject-v1",
            "NOT THIS",
            "§ 202.1104 reporting applies to rejections on or after October 6, 2025. "
            "Earlier rejects are outside this mouth.",
            write_state=write_state_mod.for_advisory_mouth(mouth_id="dsp-reject"),
            **common,
        )
    if rejected != "yes":
        return _pack(
            "gate-dsp-reject-v1",
            "HOLD",
            "Duty attaches after affirmative reject (including automated reject). "
            "If you accepted a prohibited deal, that is a different DSP violation — not this mouth.",
            **common,
        )

    from datetime import datetime, timezone

    rejected_at = reject_date or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    due_at = _dsp_due_at(rejected_at)
    report_pack = {
        "spec": "gate-dsp-1104-report-pack-v1",
        "cfr": "28 CFR 202.1104(c)",
        "submit_to": DSP_NSD_EMAIL,
        "submit_via": "email per 28 CFR 202.1201 (or official NSD electronic option)",
        "gate_files_for_you": False,
        "fields": {
            "us_person_name_and_address": None,
            "contact_name_phone_email": None,
            "date_rejected": rejected_at,
            "types_and_volumes_of_data": None,
            "method_of_data_transfer": None,
            "persons_attempting_and_locations": None,
            "covered_persons_and_countries_of_concern": None,
            "relevant_documentation": None,
            "legal_authority_for_rejection": "28 CFR Part 202 — prohibited data brokerage",
        },
        "mailto": (
            f"mailto:{DSP_NSD_EMAIL}"
            f"?subject=DSP%20%C2%A7%20202.1104%20rejected%20prohibited%20transaction%20report"
            f"&body=U.S.%20person%20report%20under%2028%20CFR%20202.1104%0A"
            f"Date%20rejected%3A%20{rejected_at}%0A"
            f"Due%20by%3A%20{due_at}%0A"
            f"%0A%5BAttach%20or%20paste%20%C2%A7%20202.1104(c)%20fields%5D%0A"
        ),
        "due_at": due_at,
        "days": 14,
    }
    return _pack(
        "gate-dsp-reject-v1",
        "REPORT DUE",
        "Affirmative reject of a prohibited data-brokerage offer on/after Oct 6 2025. "
        "File with DOJ NSD within 14 days. Gate packs the fields — you send the email.",
        report_pack=report_pack,
        write_state=write_state_mod.for_report_clock(
            due_at=due_at,
            rejected_at=rejected_at,
            filed=False,
        ),
        covered_persons_list_exhaustive=False,
        **common,
    )


# Parked — verified gap, not ready as a dispute SKU.
# Visa Core Rules Apr 2026 §4.1.24 defines Agentic Payment Provider transactions and
# cardholder responsibility for APP actions. §11 has no agentic dispute condition.
# Do not ship a "Visa agentic chargeback" mouth on liability text alone.
PARKED_MOUTHS = (
    {
        "id": "visa-agentic-chargebacks",
        "status": "parked",
        "reason": (
            "Visa Core Rules (April 2026) §4.1.24 covers agentic payment providers and "
            "cardholder responsibility; no agent-specific dispute/chargeback evidence "
            "spec in §11. Park until a primary compelling-evidence dig lands — then "
            "ship as pre-auth mandate Seal, not a fake Visa reason code."
        ),
        "cite": "Visa Core Rules / Product & Service Rules, Edition Apr 2026, effective 18 April 2026",
        "source": "https://usa.visa.com/content/dam/VCOM/download/about-visa/visa-rules-public.pdf",
    },
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
    {
        "id": "fednow-prepush",
        "route": "/fednow-prepush",
        "api": "/v1/fednow-prepush",
        "wk": "/.well-known/fednow-prepush.json",
        "fn": "evaluate_fednow_prepush",
        "spec": "gate-fednow-prepush-v1",
        "title": "FedNow / RTP Pre-push",
        "brand": "FedNow Pre-push",
        "lede": "May this irrevocable FedNow or RTP credit-push proceed?",
        "legend": (
            ("CLEAR", "Payee sealed, not first-time, no fraud flag."),
            ("NEVER", "Suspected fraud or no sealed payee — do not push."),
            ("HOLD", "First-time payee or missing fields. Fail closed."),
        ),
        "words": ["CLEAR", "NEVER", "HOLD"],
        "submit": "Ask",
        "fields": [
            {
                "name": "rail",
                "label": "Rail",
                "type": "chips",
                "options": [
                    {"id": "fednow", "label": "FedNow"},
                    {"id": "rtp", "label": "RTP"},
                ],
            },
            {
                "name": "payee_sealed",
                "label": "Payee / mandate sealed?",
                "type": "chips",
                "options": [
                    {"id": "yes", "label": "Yes"},
                    {"id": "no", "label": "No"},
                ],
            },
            {
                "name": "first_time_payee",
                "label": "First-time payee?",
                "type": "chips",
                "options": [
                    {"id": "yes", "label": "Yes"},
                    {"id": "no", "label": "No"},
                ],
            },
            {
                "name": "fraud_suspected",
                "label": "Fraud suspected?",
                "type": "chips",
                "options": [
                    {"id": "yes", "label": "Yes"},
                    {"id": "no", "label": "No"},
                ],
            },
        ],
        "source": (
            "U.S. Faster Payments Council — Instant Payments Fraud Dispute Resolution "
            "Guiding Principles (May 15, 2026). Directional — not a Fed order."
        ),
        "source_url": (
            "https://fasterpaymentscouncil.org/blog/17139/"
            "U-S-Faster-Payments-Council-Releases-Guiding-Principles-for-Instant-Payments-Fraud-Dispute-Resolution"
        ),
    },
    {
        "id": "nacha-false-pretenses",
        "route": "/nacha-false-pretenses",
        "api": "/v1/nacha-false-pretenses",
        "wk": "/.well-known/nacha-false-pretenses.json",
        "fn": "evaluate_nacha_false_pretenses",
        "spec": "gate-nacha-false-pretenses-v1",
        "title": "Nacha False Pretenses",
        "brand": "False Pretenses",
        "lede": "May this ACH credit proceed under False Pretenses risk?",
        "legend": (
            ("CLEAR", "No FP flag; who/what/payee sealed."),
            ("NEVER", "FP suspected without sealed who/what/payee."),
            ("HOLD", "Suspected with seal — review, or missing fields."),
        ),
        "words": ["CLEAR", "NEVER", "HOLD"],
        "submit": "Ask",
        "fields": [
            {
                "name": "role",
                "label": "Role",
                "type": "chips",
                "options": [
                    {"id": "odfi", "label": "ODFI"},
                    {"id": "rdfi", "label": "RDFI"},
                    {"id": "originator", "label": "Originator"},
                ],
            },
            {
                "name": "false_pretenses_suspected",
                "label": "False Pretenses suspected?",
                "type": "chips",
                "options": [
                    {"id": "yes", "label": "Yes"},
                    {"id": "no", "label": "No"},
                ],
            },
            {
                "name": "who_what_payee_sealed",
                "label": "Who / what / payee sealed?",
                "type": "chips",
                "options": [
                    {"id": "yes", "label": "Yes"},
                    {"id": "no", "label": "No"},
                ],
            },
        ],
        "source": (
            "Nacha Risk Management — False Pretenses. Phase 1 live Mar 20 2026; "
            "Phase 2 Jun 19 2026. Monitoring duty — not itself a pre-push mandate."
        ),
        "source_url": "https://www.nacha.org/news/new-nacha-risk-management-rules-now-effect",
    },
    {
        "id": "cl7-handoff",
        "route": "/cl7-handoff",
        "api": "/v1/cl7-handoff",
        "wk": "/.well-known/cl7-handoff.json",
        "fn": "evaluate_cl7_handoff",
        "spec": "gate-cl7-handoff-v1",
        "title": "CL7 AIS/ECDIS Handoff",
        "brand": "CL7 Handoff",
        "lede": "Was the AIS/ECDIS → manual handoff noticed in writing within 15 days?",
        "legend": (
            ("SEALED", "Written notice within 15 days — seal holds."),
            ("NEVER", "Silent drop to manual — notice missing."),
            ("NOT THIS", "No AIS/ECDIS handoff."),
            ("HOLD", "Missing fields. Fail closed."),
        ),
        "words": ["SEALED", "NEVER", "NOT THIS", "HOLD"],
        "submit": "Ask",
        "fields": [
            {
                "name": "ais_ecdis_handoff",
                "label": "AIS/ECDIS path handed off to manual?",
                "type": "chips",
                "options": [
                    {"id": "yes", "label": "Yes"},
                    {"id": "no", "label": "No"},
                ],
            },
            {
                "name": "written_notice_15d",
                "label": "Written notice within 15 days?",
                "type": "chips",
                "options": [
                    {"id": "yes", "label": "Yes"},
                    {"id": "no", "label": "No"},
                ],
            },
        ],
        "source": (
            "NYDFS Insurance Circular Letter No. 7 (2024). "
            "AIS=Artificial Intelligence Systems; ECDIS=External Consumer Data and "
            "Information Sources (insurance — not maritime)."
        ),
        "source_url": "https://www.dfs.ny.gov/industry-guidance/circular-letters/cl2024-07",
    },
    {
        "id": "stair",
        "route": "/stair",
        "api": "/v1/stair",
        "wk": "/.well-known/stair.json",
        "fn": "evaluate_stair",
        "spec": "gate-stair-v1",
        "title": "Stair",
        "brand": "Stair",
        "lede": "Occupied egress is not a Gate write. We will not weld fail-closed on a door the code says shall unlock.",
        "legend": (
            ("NEVER", "This is the stair. Gate stays off the path."),
            ("NOT THIS", "Money or bind. Fail-closed still applies."),
            ("HOLD", "Name the write."),
        ),
        "words": ["NEVER", "NOT THIS", "HOLD"],
        "submit": "Ask",
        "fields": [
            {
                "name": "kind",
                "label": "What write",
                "type": "chips",
                "options": [
                    {"id": "egress_lock", "label": "Means-of-egress electric lock"},
                    {"id": "money_or_bind", "label": "Money / bind / payout"},
                ],
            }
        ],
        "source": "IBC: loss of power and fire alarm shall unlock. PUSH TO EXIT cuts lock power with no other electronics in the way.",
        "source_url": "https://up.codes/s/sensor-release-of-electrically-locked-egress-doors",
    },
    {
        "id": "dsp-reject",
        "route": "/dsp-reject",
        "api": "/v1/dsp-reject",
        "wk": "/.well-known/dsp-reject.json",
        "fn": "evaluate_dsp_reject",
        "spec": "gate-dsp-reject-v1",
        "title": "DSP Reject Report",
        "brand": "DSP Reject",
        "lede": "Did you reject a prohibited data-brokerage offer? Is a DOJ NSD report due in 14 days?",
        "legend": (
            ("REPORT DUE", "Rejected prohibited offer on/after Oct 6 2025 — file within 14 days."),
            ("NOT THIS", "Face does not attach § 202.1104."),
            ("HOLD", "Missing fields or unknown covered-person status. Fail closed."),
        ),
        "words": ["REPORT DUE", "NOT THIS", "HOLD"],
        "submit": "Ask",
        "fields": [
            {
                "name": "data_brokerage_offer",
                "label": "Offer was data brokerage (buy/sell/license/transfer data)?",
                "type": "chips",
                "options": [
                    {"id": "yes", "label": "Yes"},
                    {"id": "no", "label": "No"},
                ],
            },
            {
                "name": "bulk_sensitive_or_gov_data",
                "label": "Bulk U.S. sensitive personal data or government-related data?",
                "type": "chips",
                "options": [
                    {"id": "yes", "label": "Yes"},
                    {"id": "no", "label": "No"},
                ],
            },
            {
                "name": "counterparty_covered_or_coc",
                "label": "Counterparty a covered person / country of concern?",
                "type": "chips",
                "options": [
                    {"id": "yes", "label": "Yes"},
                    {"id": "no", "label": "No"},
                    {"id": "unknown", "label": "Unknown"},
                ],
            },
            {
                "name": "affirmatively_rejected",
                "label": "Affirmatively rejected (incl. automated reject)?",
                "type": "chips",
                "options": [
                    {"id": "yes", "label": "Yes"},
                    {"id": "no", "label": "No"},
                ],
            },
            {
                "name": "rejected_on_or_after_2025_10_06",
                "label": "Rejected on or after Oct 6, 2025?",
                "type": "chips",
                "options": [
                    {"id": "yes", "label": "Yes"},
                    {"id": "no", "label": "No"},
                ],
            },
        ],
        "source": (
            "28 CFR § 202.1104 — DOJ Data Security Program. Affirmative reject of a "
            "prohibited data-brokerage offer → report to NSD within 14 days. Gate does not file."
        ),
        "source_url": DSP_SOURCE,
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
        "fednow-prepush": evaluate_fednow_prepush,
        "nacha-false-pretenses": evaluate_nacha_false_pretenses,
        "cl7-handoff": evaluate_cl7_handoff,
        "stair": evaluate_stair,
        "dsp-reject": evaluate_dsp_reject,
    }[mid]
    raw_body = body if isinstance(body, dict) else {}
    result = fn(raw_body)
    # Strip PII-ish free text from scope inputs — flags/chips only.
    safe_inputs = {
        k: v
        for k, v in raw_body.items()
        if isinstance(v, (str, bool, int, float)) and k not in ("account_id", "email", "name")
    }
    logs = {
        "positive-clear": [
            "presented kind + authority_live chips",
            "no PAS/ledger scanned — Positive Clear is advisory unlock check",
        ],
        "scenario-3": [
            "presented FinCEN Scenario 3 flag chips",
            "FIN-2016-A003 classification only — no wire log scanned",
        ],
        "fednow-prepush": [
            "presented rail/payee_sealed/first_time_payee/fraud_suspected chips",
            "FPC May 15 2026 guiding principles — pre-push advisory, no FedNow API call",
        ],
        "nacha-false-pretenses": [
            "presented role/false_pretenses_suspected/who_what_payee_sealed chips",
            "Nacha Risk Management Phase 1/2 — monitoring duty advisory, no ACH log scanned",
        ],
        "cl7-handoff": [
            "presented ais_ecdis_handoff + written_notice_15d chips",
            "NYDFS CL7 (2024) notice Seal — no underwriting system scanned",
        ],
        "uapa-seal": [
            "presented already_sent/authorized/induced/rtp_native chips",
            "TCH UAPA post-send classification — no RTP ledger scanned",
        ],
        "admt": [
            "presented decision_class/uses_admt/pre_use_notice chips",
            "11 CCR § 7200(b) notice Seal — no ADMT inventory scanned",
        ],
        "trusted-contact": [
            "presented trusted-contact chips",
            "advisory hold check — local trusted_holds db only when sealed",
        ],
        "stair": [
            "presented kind chip (egress vs money/bind)",
            "IBC egress refusal — Gate stays off the stair path",
        ],
        "dsp-reject": [
            "presented data_brokerage_offer / bulk_sensitive_or_gov_data / "
            "counterparty_covered_or_coc / affirmatively_rejected / "
            "rejected_on_or_after_2025_10_06 chips",
            "28 CFR 202.1104 classification only — Covered Persons List not scanned; "
            "list is non-exhaustive for § 202.211(a)(1)–(4); Gate never emails NSD",
        ],
    }.get(mid)
    return _seal_mouth(
        mouth_id=mid,
        body=result,
        inputs=safe_inputs,
        logs=logs,
        counterparties=None,
        advisory=True,
    )


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
