"""Item 122 — named assumption set on every verified claim.

A proof is exhaustive only under stated assumptions. A test is sampled.
`verified: true` alone is refused so a vacuous steelman cannot look like a real one.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-named-assumptions-v1"
PROOF = "proof"
TEST = "test"
KINDS = (PROOF, TEST)


def _names(raw: Any) -> list[str] | None:
    if raw is None:
        return None
    if isinstance(raw, str):
        text = raw.strip()
        return [text] if text else []
    if not isinstance(raw, (list, tuple)):
        return None
    out = []
    for item in raw:
        text = str(item).strip() if item is not None else ""
        if text:
            out.append(text)
    return out


def claim(
    *,
    verified: bool = False,
    under_assumptions: Any = None,
    kind: str | None = None,
    steelman_cited: bool = False,
    counterfactual_cited: bool = False,
) -> dict[str, Any]:
    kind_raw = (kind or TEST).strip().lower()
    named_kind = kind_raw if kind_raw in KINDS else TEST
    names = _names(under_assumptions)

    if verified and names is None:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "assumptions_required",
            "verified": False,
            "under_assumptions": None,
            "kind": named_kind,
            "plain": "A bare verified: true is refused. Name the assumption set.",
        }
    if verified and not names:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "assumptions_empty",
            "verified": False,
            "under_assumptions": [],
            "kind": named_kind,
            "plain": "An empty assumption list is vacuous. The breaking case may have been excluded by silence.",
        }

    vacuous_visible = bool(verified and named_kind == PROOF and not steelman_cited)
    return {
        "spec": SPEC,
        "ok": True,
        "verified": bool(verified),
        "under_assumptions": names or [],
        "kind": named_kind,
        "steelman_cited": bool(steelman_cited),
        "counterfactual_cited": bool(counterfactual_cited),
        "vacuous_visible": vacuous_visible,
        "plain": (
            "Verified under named assumptions. Vacuous if the list excludes the case that would break the property."
            if verified
            else "Not verified. Assumption set is recorded; it is not a proof."
        ),
    }


def from_row(row: dict[str, Any] | None, *, hash_matches: bool, signature_ok: bool) -> dict[str, Any]:
    hop = (row or {}).get("hop") if isinstance((row or {}).get("hop"), dict) else {}
    names = hop.get("under_assumptions") if hop.get("under_assumptions") is not None else hop.get("assumptions")
    rec = claim(
        verified=bool(hash_matches),
        under_assumptions=names,
        kind=hop.get("verify_kind") or hop.get("kind"),
        steelman_cited=bool(hop.get("steelman_cited") or hop.get("counter_case_id")),
        counterfactual_cited=bool(hop.get("counterfactual_cited") or hop.get("counterfactual")),
    )
    rec["verified"] = bool(rec.get("ok") and rec.get("verified") and signature_ok)
    return rec
