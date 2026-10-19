"""Prefinality reconstruction-as-law — meter infrastructure, not a meter.

Clay-problem (C): possession of a GO receipt is insufficient.
At the effectuation boundary the rail must independently reconstruct the
pending act + authority state. Divergence ⇒ not finality.

  Clear(transfer) ⇔ Reconstruct(descriptor, epoch, parents, sink) = presented ∧ LIVE

Blow-up (A): smooth MAY fails while the wire still clears — unauthorized finality.
Composition (B): Clear is the fail-closed *meet* over predicates — Prefinality
defines the meet, not the operators' dashboards.

First money boundary: payout / withdraw release (irreversible money-leave).
Non-PII: fingerprints and predicates only — never license_number / account raw.

Soft overrides killed:
- screenshot GO then spend forever
- trust our /evaluate oracle as the only reconstruction
- soft-yes under latency panic at the boundary
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Callable

try:
    from gate import finality_sink as sink_mod
except ImportError:
    import finality_sink as sink_mod

try:
    from gate import license_fuse as license_fuse_mod
except ImportError:
    import license_fuse as license_fuse_mod

try:
    from gate import prefinality as pf_mod
except ImportError:
    import prefinality as pf_mod

SPEC = "gate-prefinality-reconstruction-v1"
BOUNDARY_PAYOUT = "payout_release"
BOUNDARY_PEG_OUT = "peg_out_withdraw"
BOUNDARY_RTP = "rtp_before_order"
BOUNDARIES = (
    BOUNDARY_PAYOUT,
    BOUNDARY_PEG_OUT,
    "x402_before_sign",
    BOUNDARY_RTP,
)

# Hunt lock — prove → category → institutional (do not chase all three at once).
DOOR_ORDER = (
    {
        "id": BOUNDARY_PAYOUT,
        "rank": 1,
        "write": "POST /v1/payouts/{id}/release",
        "role": "prove",
        "why": "First commercial driver — DENY + reconstruct on one welded release",
    },
    {
        "id": BOUNDARY_PEG_OUT,
        "rank": 2,
        "write": "peg-out / bridge withdraw release",
        "role": "category",
        "why": (
            "Highest blow-up cousin that upgrades diligence targets "
            "(bridges · peg-outs · custody). Same Clear law; sponsor/custodian teeth."
        ),
    },
    {
        "id": BOUNDARY_RTP,
        "rank": 3,
        "write": "RTP/FedNow payment_order create",
        "role": "institutional",
        "why": "Inherits the law after prove — durable meter infrastructure, slower desks",
    },
)

REASON_FP_MISMATCH = "reconstruction_fingerprint_mismatch"
REASON_RECEIPT = "reconstruction_receipt_invalid"
REASON_NOT_GO = "reconstruction_decision_not_go"
REASON_FUSE = "reconstruction_fuse_not_live"
REASON_LICENSE = "reconstruction_license_parent_not_live"
REASON_BOUNDARY = "reconstruction_boundary_unsupported"
REASON_DESCRIPTOR = "reconstruction_descriptor_incomplete"

FuseLookup = Callable[[str], dict | None]


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def payout_write_fingerprint(*, payout_id: str | None, method: str = "POST") -> str | None:
    """Non-PII married write for the first commercial driver edge."""
    pid = (payout_id or "").strip()
    if not pid:
        return None
    path = f"/v1/payouts/{pid}/release"
    body = {"method": (method or "POST").upper(), "path": path, "boundary": BOUNDARY_PAYOUT}
    return hashlib.sha256(_canonical(body).encode("utf-8")).hexdigest()


def peg_out_write_fingerprint(
    *,
    bridge_id: str | None,
    withdraw_id: str | None,
    method: str = "POST",
) -> str | None:
    """Non-PII married write for peg-out / bridge withdraw (door #2)."""
    bridge = (bridge_id or "").strip()
    wid = (withdraw_id or "").strip()
    if not bridge or not wid:
        return None
    path = f"/v1/bridges/{bridge}/withdrawals/{wid}/release"
    body = {
        "method": (method or "POST").upper(),
        "path": path,
        "boundary": BOUNDARY_PEG_OUT,
    }
    return hashlib.sha256(_canonical(body).encode("utf-8")).hexdigest()


def reconstruct_descriptor(
    *,
    rail: str,
    transfer: dict | None,
    boundary: str = BOUNDARY_PAYOUT,
    payout_id: str | None = None,
    bridge_id: str | None = None,
    withdraw_id: str | None = None,
    fuse_id: str | None = None,
    license_id: str | None = None,
    job_id: str | None = None,
) -> dict[str, Any]:
    """Boundary-local rebuild of what is about to become irreversible.

    Does not call home. Callers supply only non-PII fields already on the wire.
    """
    rail_n = (rail or "").strip().lower()
    transfer = transfer if isinstance(transfer, dict) else {}
    t_norm = pf_mod._normalize_transfer(rail_n, transfer) if rail_n in pf_mod.RAILS else {}
    transfer_fp = (
        pf_mod.transfer_fingerprint(rail=rail_n, transfer=transfer) if rail_n in pf_mod.RAILS else None
    )
    write_fp = None
    if boundary == BOUNDARY_PAYOUT:
        write_fp = payout_write_fingerprint(payout_id=payout_id)
    elif boundary == BOUNDARY_PEG_OUT:
        write_fp = peg_out_write_fingerprint(bridge_id=bridge_id, withdraw_id=withdraw_id)
    return {
        "spec": SPEC,
        "boundary": boundary,
        "rail": rail_n or None,
        "transfer_fingerprint": transfer_fp,
        "write_fingerprint": write_fp,
        "transfer": t_norm,
        "fuse_id": (fuse_id or "").strip() or None,
        "license_id": license_fuse_mod.normalize_id(license_id),
        "job_id": (job_id or "").strip() or None,
        "payout_id": (payout_id or "").strip() or None,
        "bridge_id": (bridge_id or "").strip() or None,
        "withdraw_id": (withdraw_id or "").strip() or None,
        "their_production": False,
    }


def _predicate_receipt(*, receipt: str | None, expected_fingerprint: str | None) -> dict[str, Any]:
    if not receipt:
        return {"id": "receipt", "ok": False, "reason": REASON_RECEIPT}
    verified = pf_mod.verify_receipt_jwt(receipt, expected_fingerprint=expected_fingerprint)
    if not verified.get("valid"):
        return {
            "id": "receipt",
            "ok": False,
            "reason": verified.get("reason") or REASON_RECEIPT,
            "detail": verified,
        }
    if (verified.get("decision") or "").upper() != "GO":
        return {
            "id": "receipt",
            "ok": False,
            "reason": REASON_NOT_GO,
            "decision": verified.get("decision"),
        }
    return {"id": "receipt", "ok": True, "decision": "GO", "payload": verified.get("payload")}


def _predicate_fingerprint(*, reconstructed_fp: str | None, presented_fp: str | None) -> dict[str, Any]:
    left = (reconstructed_fp or "").strip().lower()
    right = (presented_fp or "").strip().lower()
    if not left or not right:
        return {"id": "fingerprint", "ok": False, "reason": REASON_DESCRIPTOR}
    if left != right:
        return {"id": "fingerprint", "ok": False, "reason": REASON_FP_MISMATCH}
    return {"id": "fingerprint", "ok": True, "fingerprint": left}


def _predicate_fuse(*, fuse_id: str | None, fuse_lookup: FuseLookup | None) -> dict[str, Any]:
    """Use-time sink — hop ink is not spend grant."""
    sink = sink_mod.recheck(fuse_id=fuse_id, fuse_lookup=fuse_lookup)
    return {
        "id": "fuse_sink",
        "ok": bool(sink.get("ok")),
        "reason": None if sink.get("ok") else (sink.get("reason") or REASON_FUSE),
        "sink": sink,
    }


def _predicate_license(*, license_id: str | None, welded: bool = False) -> dict[str, Any]:
    if welded:
        parent = license_fuse_mod.presented_for_weld(license_id)
    else:
        parent = license_fuse_mod.presented(license_id)
    ok = bool(parent.get("ok"))
    # Soft omit still ok only when not welded and not required — presented() encodes that.
    return {
        "id": "license_parent",
        "ok": ok,
        "reason": None if ok else (parent.get("reason") or REASON_LICENSE),
        "license": parent,
    }


def meet(predicates: list[dict[str, Any]]) -> dict[str, Any]:
    """Composition law (B): fail-closed meet over independent predicates."""
    ok = all(bool(p.get("ok")) for p in predicates)
    failed = [p for p in predicates if not p.get("ok")]
    return {
        "spec": "gate-prefinality-meet-v1",
        "ok": ok,
        "halt": not ok,
        "predicate_count": len(predicates),
        "failed": [p.get("id") for p in failed],
        "reasons": [p.get("reason") for p in failed if p.get("reason")],
        "predicates": predicates,
    }


def clear(
    *,
    rail: str,
    transfer: dict | None,
    receipt: str | None,
    boundary: str = BOUNDARY_PAYOUT,
    payout_id: str | None = None,
    bridge_id: str | None = None,
    withdraw_id: str | None = None,
    fuse_id: str | None = None,
    license_id: str | None = None,
    job_id: str | None = None,
    presented_fingerprint: str | None = None,
    fuse_lookup: FuseLookup | None = None,
    welded: bool = False,
    require_fuse: bool = True,
) -> dict[str, Any]:
    """Effectuation-boundary Clear — reconstruction-as-law.

    Receipt possession is evidence of a past evaluation, not a spend grant.
    """
    boundary_n = (boundary or BOUNDARY_PAYOUT).strip()
    out: dict[str, Any] = {
        "spec": SPEC,
        "ok": False,
        "halt": True,
        "clear": False,
        "blow_up": False,
        "boundary": boundary_n,
        "their_production": False,
        "law": "Clear ⇔ Reconstruct = presented ∧ LIVE (fail-closed meet)",
    }
    if boundary_n not in BOUNDARIES:
        out["reason"] = REASON_BOUNDARY
        return out

    descriptor = reconstruct_descriptor(
        rail=rail,
        transfer=transfer,
        boundary=boundary_n,
        payout_id=payout_id,
        bridge_id=bridge_id,
        withdraw_id=withdraw_id,
        fuse_id=fuse_id,
        license_id=license_id,
        job_id=job_id,
    )
    out["descriptor"] = descriptor

    presented_fp = (presented_fingerprint or descriptor.get("transfer_fingerprint") or "").strip() or None
    predicates: list[dict[str, Any]] = [
        _predicate_fingerprint(
            reconstructed_fp=descriptor.get("transfer_fingerprint"),
            presented_fp=presented_fp,
        ),
        _predicate_receipt(receipt=receipt, expected_fingerprint=presented_fp),
    ]
    if require_fuse or fuse_id:
        predicates.append(
            _predicate_fuse(
                fuse_id=fuse_id or descriptor.get("fuse_id"),
                fuse_lookup=fuse_lookup,
            )
        )
    if welded or license_id:
        predicates.append(_predicate_license(license_id=license_id, welded=welded))

    composition = meet(predicates)
    out["composition"] = composition
    out["ok"] = bool(composition.get("ok"))
    out["halt"] = not out["ok"]
    out["clear"] = out["ok"]
    if not out["ok"]:
        reasons = composition.get("reasons") or []
        out["reason"] = reasons[0] if reasons else "reconstruction_failed"
        # Blow-up class (A): would-be clear failure at a money boundary.
        out["authority_blow_up_class"] = True
    return out


def blow_up_report(
    *,
    write_path: str,
    clear_result: dict | None,
    spent: bool,
) -> dict[str, Any]:
    """A: unauthorized finality — spend occurred (or claimed) without Clear."""
    cleared = bool((clear_result or {}).get("clear"))
    blow = bool(spent) and not cleared
    return {
        "spec": "gate-authority-blow-up-v1",
        "blow_up": blow,
        "spent": bool(spent),
        "cleared": cleared,
        "write_path": (write_path or "").strip() or None,
        "note": (
            "Smooth MAY failed while the wire still cleared — unauthorized finality."
            if blow
            else "No blow-up: either not spent, or Clear held."
        ),
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Prefinality reconstruction-as-law",
        "what": (
            "Finality without independent reconstruction is not finality. "
            "Meter infrastructure: rails reconstruct at the effectuation boundary."
        ),
        "not": [
            "screenshot GO then spend",
            "Nisaba as sole oracle hub",
            "fraud score / SaaS dashboard",
            "PII vault",
        ],
        "law": "Clear(transfer) ⇔ Reconstruct(descriptor, parents, sink) = presented ∧ LIVE",
        "clay": {
            "A_authority_blow_up": "Smooth MAY fails while wire clears",
            "B_composition_meet": "Fail-closed meet over independent predicates",
            "C_reconstruction_as_law": "Possession insufficient; reconstruct at boundary",
        },
        "first_boundary": {
            "id": BOUNDARY_PAYOUT,
            "write": "POST /v1/payouts/{id}/release",
            "why": "Irreversible money-leave — first commercial driver edge",
        },
        "second_boundary": {
            "id": BOUNDARY_PEG_OUT,
            "write": "peg-out / bridge withdraw release",
            "why": (
                "Locked category door — highest blow-up cousin; upgrades diligence "
                "bridges/peg-outs. RTP/FedNow inherits the same law third."
            ),
        },
        "door_order": list(DOOR_ORDER),
        "post": f"{base}/v1/prefinality/reconstruct",
        "demo": f"{base}/demo/prefinality/reconstruct",
        "evaluate": f"{base}/v1/prefinality/evaluate",
        "sink": f"{base}/.well-known/finality-sink.json",
        "prefinality": f"{base}/.well-known/prefinality.json",
        "fail_closed": True,
        "their_production": False,
    }
