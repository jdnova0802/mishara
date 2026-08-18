"""Epoch lock — monotonic accountability invariant on one job.

A HALT/BLOCK for job_id is a committed non-spend. The next hop cannot
reinterpret that job as ALLOW unless the request carries a charge_id.

This is not admin CHARGE (that stays on Velaru). This is Gate refusing
the fraud of regime change without a named epoch transition.

Lineage:
- MA-Commit (2026) — permission that justified an action must not shrink
- Monotonic Accountability Invariant (2026) — epoch transitions not subject
  to MA-Commit introduce safety violations at epoch boundaries
- Closure theorem — the unique admissible transition is itself an irreversible
  commit with a witness spanning old and new regimes (here: charge_id)

UW approve without CHARGE does not resurrect. That is now enforced, not printed.
"""
from __future__ import annotations

try:
    from gate import db
except ImportError:
    import db

SPEC = "gate-epoch-v1"


def normalize_charge_id(raw) -> str | None:
    if raw is None:
        return None
    s = str(raw).strip()[:128]
    return s or None


def apply(*, job_id: str | None, hop: dict, charge_id: str | None) -> tuple[dict, dict]:
    """If the latest decision for this job is HALT/BLOCK, REQUIRE charge_id to ALLOW."""
    hop_d = dict(hop) if isinstance(hop, dict) else {}
    jid = (job_id or "").strip()
    cid = normalize_charge_id(charge_id)
    meta = {
        "spec": SPEC,
        "locked": False,
        "charge_id": cid,
        "prior_event_id": None,
        "prior_decision": None,
        "rule": "Latest HALT/BLOCK for this job_id stays HALT until charge_id is presented.",
    }
    if not jid:
        return hop_d, meta
    prior = db.latest_bind_event_for_job(jid)
    if not prior:
        return hop_d, meta
    prior_decision = (prior.get("decision") or "").upper()
    meta["prior_event_id"] = prior.get("id")
    meta["prior_decision"] = prior_decision
    if prior_decision not in ("HALT", "BLOCK"):
        return hop_d, meta
    if cid:
        meta["locked"] = False
        meta["regime_change"] = "charge_id_presented"
        hop_d["charge_id"] = cid
        hop_d["prior_event_id"] = prior.get("id")
        return hop_d, meta
    hop_d["halt"] = True
    hop_d["verdict"] = False
    hop_d["epoch_lock"] = True
    hop_d["epoch_reason"] = "prior_halt_requires_charge"
    hop_d["prior_event_id"] = prior.get("id")
    meta["locked"] = True
    meta["reason"] = "prior_halt_requires_charge"
    return hop_d, meta
