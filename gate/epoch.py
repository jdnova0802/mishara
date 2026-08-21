"""Epoch lock — monotonic accountability invariant on one job.

A HALT/BLOCK for job_id is a committed non-spend. The next hop cannot
reinterpret that job as ALLOW unless the request carries verified charge
authority (see charge_authority.py).

This is not admin CHARGE (that stays on Velaru). This is Gate refusing
the fraud of regime change without a named epoch transition.
"""
from __future__ import annotations

try:
    from gate import db
except ImportError:
    import db

try:
    from gate import charge_authority as charge_mod
except ImportError:
    import charge_authority as charge_mod

SPEC = "gate-epoch-v1"


def normalize_charge_id(raw) -> str | None:
    return charge_mod.normalize(raw)


def apply(*, job_id: str | None, hop: dict, charge_id: str | None) -> tuple[dict, dict]:
    """If the latest decision for this job is HALT/BLOCK, REQUIRE verified charge_id to ALLOW."""
    hop_d = dict(hop) if isinstance(hop, dict) else {}
    jid = (job_id or "").strip()
    cid = normalize_charge_id(charge_id)
    meta = {
        "spec": SPEC,
        "locked": False,
        "charge_id": cid,
        "prior_event_id": None,
        "prior_decision": None,
        "rule": "Latest HALT/BLOCK for this job_id stays HALT until verified charge authority is presented.",
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
        auth = charge_mod.verify(charge_id=cid, purpose="epoch", subject=jid)
        meta["charge_authority"] = auth
        if auth.get("ok"):
            charge_mod.consume(charge_id=cid, purpose="epoch", subject=jid)
            meta["locked"] = False
            meta["regime_change"] = "charge_authority_accepted"
            hop_d["charge_id"] = cid
            hop_d["prior_event_id"] = prior.get("id")
            return hop_d, meta
        hop_d["halt"] = True
        hop_d["verdict"] = False
        hop_d["epoch_lock"] = True
        hop_d["epoch_reason"] = auth.get("reason") or "charge_authority_invalid"
        hop_d["prior_event_id"] = prior.get("id")
        meta["locked"] = True
        meta["reason"] = hop_d["epoch_reason"]
        return hop_d, meta
    hop_d["halt"] = True
    hop_d["verdict"] = False
    hop_d["epoch_lock"] = True
    hop_d["epoch_reason"] = "prior_halt_requires_charge"
    hop_d["prior_event_id"] = prior.get("id")
    meta["locked"] = True
    meta["reason"] = "prior_halt_requires_charge"
    return hop_d, meta
