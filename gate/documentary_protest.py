"""Documentary Protest v0 — LC + notarial protest applied to irreversible writes.

THE RARE COMBO:
  Irreversibility × documentary compliance (UCP-shaped) × notarial PROTEST.

History:
  - Letters of credit: banks deal in documents, not goods. Honour only on complying presentation.
  - Notarial protest (Bills of Exchange Act era): formal instrument proving presentment + dishonour.
    Rare even in modern banking — but carries public-document force across borders.

Today:
  AI/agent stacks sell allow/deny dashboards.
  Trade-finance AI examines LC docs for banks — it does NOT productize PROTEST of a failed Clear
  on payout/peg-out/bind/agent-tool leave as a stranger-authenticable commodity.

Invent:
  1) Documentary Clear — irreversible leave only against complying Clear presentation
  2) Protest — when leave is refused / Clear dishonours, issue PROTEST as first-class object
     (feeds DENY Meter unit PROTEST)

NOT a sister company. On-card under Gate / Bind Room / Refusal adjacency.
Surfaces:
  GET /.well-known/documentary-protest.json
  POST /demo/documentary/present
  POST /demo/documentary/protest
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

SPEC = "gate-documentary-protest-v0"
FIRM = "Nisaba LLC"
CARD = (
    "On-card invent. Documentary Clear + notarial PROTEST for irreversible writes. "
    "Does not rename the firm. Extremely rare as productized agent/money-leave law."
)

REQUIRED_DOCS = (
    "ACT_DIGEST",  # amount/beneficiary/rail/purpose/epoch/sink binding
    "ORACLE_CLASS",  # claim that tried to authorize (oracle compiler)
    "FINALITY_CLASS",  # what success would mean on rail (finality compiler)
    "POLICY_EPOCH",  # version of may
    "STRANGER_VERIFY_HINT",  # diplomatics challenge or verify URL
)


def _utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _canon(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "firm": FIRM,
        "name": "Documentary Clear + Notarial Protest",
        "version": "0",
        "card": CARD,
        "job": (
            "Honour irreversible leave only on complying Clear presentation; "
            "on dishonour, issue a stranger-authenticable PROTEST instrument."
        ),
        "historical_roots": [
            "Documentary credits / UCP — banks deal in documents, not goods",
            "Notarial protest of bills of exchange — public proof of presentment + refusal",
            "Irrevocable LC ≠ automatic pay — compliance still gates honour",
        ],
        "why_rare_now": (
            "Agent control planes gate tools. Payout engines run velocity rules. "
            "Almost nobody issues a mercantile PROTEST object when Clear refuses an "
            "irreversible leave — priced, stranger-verifiable, portable across examiners."
        ),
        "laws": [
            "Deal in Clear documents, not vibes / screenshots",
            "Missing or non-complying presentation → no leave (fail closed)",
            "Dishonour → PROTEST receipt (DENY Meter unit)",
            "Protest is issuer-incomplete where diplomatics requires stranger finish",
        ],
        "required_presentation": list(REQUIRED_DOCS),
        "pairs_with": [
            "gate-deny-meter-v0",
            "gate-diplomatics-v0",
            "gate-finality-compiler-v0",
            "gate-oracle-compiler-v0",
            "gate-prefinality-v1",
        ],
        "urls": {
            "well_known": f"{base}/.well-known/documentary-protest.json",
            "demo_present": f"{base}/demo/documentary/present",
            "demo_protest": f"{base}/demo/documentary/protest",
            "diligence": f"{base}/diligence",
            "bind_room": f"{base}/bind-room",
        },
        "civilizational": True,
        "novelty_honest": (
            "LC + protest are centuries old. Applying them as the default law-object for "
            "agent/money irreversible writes — with DENY Meter + issuer-incomplete diplomatics — "
            "is the underbuilt combination."
        ),
        "not": [
            "Trade-doc OCR SaaS",
            "Pentest gym",
            "Sister company",
            "Automatic honour without complying Clear",
        ],
    }


def present(body: dict[str, Any] | None = None) -> dict[str, Any]:
    """Examine a Clear presentation. Complying → HONOUR_CANDIDATE; else DISCREPANT."""
    b = body if isinstance(body, dict) else {}
    docs = b.get("documents") if isinstance(b.get("documents"), dict) else b
    missing = [k for k in REQUIRED_DOCS if not str((docs or {}).get(k) or "").strip()]
    discrepancies = [{"code": "MISSING_DOC", "doc": m} for m in missing]

    # Soft checks
    if str((docs or {}).get("ORACLE_CLASS") or "").upper() in (
        "STALE",
        "UNSIGNED",
        "FAIL_OPEN",
        "MANIPULABLE_LOCAL",
        "UNKNOWN",
    ):
        discrepancies.append(
            {
                "code": "ORACLE_NOT_LIVE_HARD",
                "doc": "ORACLE_CLASS",
                "detail": "Oracle class cannot authorize leave",
            }
        )

    complying = len(discrepancies) == 0
    presentation_id = hashlib.sha256(_canon({"docs": docs, "t": _utc()}).encode()).hexdigest()[:32]
    return {
        "spec": SPEC,
        "firm": FIRM,
        "presentation_id": presentation_id,
        "examined_at": _utc(),
        "verdict": "HONOUR_CANDIDATE" if complying else "DISCREPANT",
        "complying": complying,
        "discrepancies": discrepancies,
        "note": (
            "HONOUR_CANDIDATE is not settlement. Sink must still consume Clear "
            "(Prefinality / exclusive door). Banks deal in documents — Gate deals in Clear."
        ),
        "card_note": "Documentary invent. Not a sister co.",
    }


def protest(body: dict[str, Any] | None = None) -> dict[str, Any]:
    """Issue notarial-shaped PROTEST after dishonour / refused leave."""
    b = body if isinstance(body, dict) else {}
    presentation = present(b)
    if presentation["complying"] and not b.get("force_protest"):
        return {
            "spec": SPEC,
            "firm": FIRM,
            "error": "no_dishonour",
            "message": "Complying presentation — protest not issued. Use sink Clear path.",
            "presentation": presentation,
        }

    act = {
        "presentation_id": presentation.get("presentation_id"),
        "discrepancies": presentation.get("discrepancies"),
        "refused_act": b.get("refused_act") or b.get("act_digest") or "irreversible_leave",
        "reason": b.get("reason") or "Clear dishonour / non-complying presentation",
        "protested_at": _utc(),
    }
    protest_id = hashlib.sha256(_canon(act).encode()).hexdigest()[:32]
    return {
        "spec": SPEC,
        "firm": FIRM,
        "instrument": "PROTEST",
        "protest_id": protest_id,
        "deny_meter_unit": "PROTEST",
        "act": act,
        "diplomatics": "issuer_incomplete_recommended",
        "stranger_verify": "https://velaru.xyz/verify",
        "legal_analogy": (
            "Notarial protest: public-shaped record that presentment occurred and honour was refused. "
            "Preserves recourse / examiner force without trusting operator screenshot."
        ),
        "card_note": "Mercantile DENY instrument for irreversible-write era.",
    }
