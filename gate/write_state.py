"""Explicit IN_FLIGHT / PENDING write phases — do not collapse liminal into binary.

Irreversible-write paths are not {reversible, final}. Between those sits PENDING /
IN_FLIGHT with real questions: can it still be cancelled? Does a Never issued in
this window mean something different than one issued before or after?

Spend phases for Gate's exclusive door:
  ABSENT     — no ticket, no redeemed leaf
  IN_FLIGHT  — unconsumed bind ticket exists (issued, not yet redeemed; may expire)
  SPENT      — redeemed leaf on the spend map (irreversible for this job_id)
  CLEARANCE  — prefinality/mouth said GO/NO_GO; no write executed by Gate
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-write-state-v1"

PHASES = ("ABSENT", "IN_FLIGHT", "SPENT", "CLEARANCE", "N_A")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def snapshot(
    *,
    phase: str,
    cancellable: bool | None,
    never_means: str,
    plain: str,
    detail: dict | None = None,
) -> dict[str, Any]:
    p = (phase or "N_A").strip().upper()
    if p not in PHASES:
        p = "N_A"
    out: dict[str, Any] = {
        "spec": SPEC,
        "phase": p,
        "cancellable": cancellable,
        "never_during_this_phase": never_means,
        "plain": plain,
        "as_of": _utc_now_iso(),
    }
    if detail:
        out["detail"] = detail
    return out


def for_spend_map(*, spent: bool, in_flight: bool, ticket_ids: list[str] | None = None) -> dict:
    """Map redeemed vs unconsumed ticket state → explicit phase."""
    if spent:
        return snapshot(
            phase="SPENT",
            cancellable=False,
            never_means=(
                "A Never here is false — redeemed leaf exists. "
                "Second consume returns job_already_spent."
            ),
            plain="Job has a redeemed bind-ticket leaf. Spend is final on Gate's map.",
            detail={"ticket_ids_consumed_probe": True},
        )
    if in_flight:
        return snapshot(
            phase="IN_FLIGHT",
            cancellable=True,
            never_means=(
                "Never (no redeemed leaf) is still true, but a live unconsumed ticket "
                "can still redeem until not_after / consume — not the same as ABSENT."
            ),
            plain=(
                "Unconsumed bind ticket(s) exist for this job_id. "
                "Not spent yet; not absent either. May expire or redeem."
            ),
            detail={"unconsumed_ticket_ids": list(ticket_ids or [])},
        )
    return snapshot(
        phase="ABSENT",
        cancellable=None,
        never_means="Never means no redeemed leaf and no live ticket — stronger than IN_FLIGHT Never.",
        plain="No redeemed leaf and no unconsumed ticket for this job_id on Gate's map.",
    )


def for_clearance_mouth(*, decision: str, rail: str | None = None) -> dict:
    """Prefinality / Issuing / Sink — Gate never executes the write."""
    dec = (decision or "").strip().upper()
    return snapshot(
        phase="CLEARANCE",
        cancellable=True if dec in ("GO", "HOLD") else None,
        never_means=(
            "A Never/NO_GO here is clearance refusal — no authorization was granted. "
            "It does not prove the underlying rail did not later move money outside Gate."
        ),
        plain=(
            f"Gate clearance only (decision={dec}"
            + (f", rail={rail}" if rail else "")
            + "). write_executed stays false. Stripe/bank settlement is a separate phase."
        ),
        detail={"write_executed": False, "clearance_only": True},
    )


def for_advisory_mouth(*, mouth_id: str) -> dict:
    """Flag-classification mouths — no irreversible write path to collapse."""
    return snapshot(
        phase="N_A",
        cancellable=None,
        never_means=(
            "Never/NO on this mouth classifies presented flags only — "
            "there is no Gate write to put IN_FLIGHT."
        ),
        plain=f"Mouth {mouth_id} is advisory classification. No spend-map state machine.",
        detail={"advisory": True},
    )


def for_report_clock(
    *,
    due_at: str,
    rejected_at: str,
    filed: bool = False,
) -> dict:
    """Federal report owed after reject — liminal until filed or overdue."""
    if filed:
        return snapshot(
            phase="SPENT",
            cancellable=False,
            never_means="Report already characterized as filed — this mouth does not re-file.",
            plain="§ 202.1104 report marked filed. Gate never emails DOJ for you.",
            detail={"due_at": due_at, "rejected_at": rejected_at, "filed": True},
        )
    return snapshot(
        phase="IN_FLIGHT",
        cancellable=False,
        never_means=(
            "A Never/NOT THIS during the 14-day clock after reject is wrong if the "
            "offer was a prohibited data-brokerage deal — the report is still owed."
        ),
        plain=(
            "Rejected. Report due to DOJ NSD within 14 days of reject. "
            "Clock is running. Gate packs the fields; you send the email."
        ),
        detail={
            "due_at": due_at,
            "rejected_at": rejected_at,
            "filed": False,
            "cfr": "28 CFR 202.1104",
            "submit_to": "NSD.FIRS.datasecurity@usdoj.gov",
        },
    )


def for_seal_verify() -> dict:
    return snapshot(
        phase="N_A",
        cancellable=None,
        never_means="Seal verifies an existing receipt; it does not open a write window.",
        plain="Seal is custody verification over bind_events + evidence log — not a write path.",
    )
