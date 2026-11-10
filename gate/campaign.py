"""Items 137, 144, 149 — DISARM cluster, confounder gate, FIMI actor tier.

A cluster is a label on 132/133 correlation, not a new detector. CONFIRMED
requires a causal_edge_review with confounder_ruled_out true. FIMI tiers
above unattributed reuse that same 144 gate. Empty TTP evidence is refused.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from gate import sanitize as sanitize_mod
except ImportError:
    import sanitize as sanitize_mod

SPEC = "gate-campaign-cluster-v1"
TTP_SPEC = "gate-disarm-ttp-v1"
CAUSAL_SPEC = "gate-causal-edge-review-v1"
FIMI_SPEC = "gate-fimi-tier-v1"
EVIDENTIARY_WEIGHT = "CORROBORATING_ONLY"
HARD_BINDING = False

STATUSES = ("SUSPECTED", "CONFIRMED", "DISMISSED")
RELATIONS = ("causal", "correlational", "unresolved")
CLASSIFIERS = ("rule", "llm", "human_analyst")
FIMI_TIERS = (
    "official_state",
    "overt_state_controlled",
    "undisclosed_state_linked",
    "covert_state_aligned",
)
DEFAULT_FIMI_TIER = "unattributed"

# Documented DISARM red-framework ids. Not a detector.
TECHNIQUES = {
    "T0013": {
        "disarm_tactic_id": "TA01",
        "disarm_technique_id": "T0013",
        "name": "Create Inauthentic Social Media Pages / Groups / Chat Groups",
    },
    "T0049": {
        "disarm_tactic_id": "TA08",
        "disarm_technique_id": "T0049",
        "name": "Flooding the information space",
    },
    "T0097": {
        "disarm_tactic_id": "TA06",
        "disarm_technique_id": "T0097",
        "name": "Delete Opposing Content",
    },
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _now()).astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _path() -> Path:
    return Path(os.getenv("GATE_CAMPAIGN_PATH") or Path(__file__).resolve().parent / "data" / "campaigns.json")


def _load() -> dict[str, Any]:
    path = _path()
    if not path.exists():
        return {"spec": SPEC, "clusters": [], "reviews": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"spec": SPEC, "clusters": [], "reviews": []}
    if not isinstance(data, dict):
        return {"spec": SPEC, "clusters": [], "reviews": []}
    data.setdefault("clusters", [])
    data.setdefault("reviews", [])
    return data


def _save(store: dict[str, Any]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")


def _ids(raw: Any) -> list[str]:
    if not isinstance(raw, list):
        return []
    return [str(x).strip() for x in raw if str(x).strip()]


def list_clusters() -> list[dict[str, Any]]:
    return list(_load().get("clusters") or [])


def list_reviews() -> list[dict[str, Any]]:
    return list(_load().get("reviews") or [])


def open_cluster(
    *,
    cohort_vertical: str,
    member_operator_ids: Any,
    source_anomaly_flag_ids: Any = None,
    source_link_graph_query_id: str | None = None,
) -> dict[str, Any]:
    members = _ids(member_operator_ids)
    flags = _ids(source_anomaly_flag_ids)
    qid = (source_link_graph_query_id or "").strip() or None
    if len(members) < 2:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "members_required",
            "plain": "A campaign is a pattern across operators, not one actor. Need at least two member_operator_ids.",
        }
    if not flags and not qid:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "source_required",
            "plain": "Label a 132 graph query or 133 flags. This is not a new detector.",
        }
    rec = {
        "spec": SPEC,
        "ok": True,
        "campaign_cluster_id": "camp_" + uuid.uuid4().hex[:12],
        "cohort_vertical": sanitize_mod.strip_agent(cohort_vertical, limit=80) or "unspecified",
        "member_operator_ids": members,
        "source_anomaly_flag_ids": flags,
        "source_link_graph_query_id": qid,
        "first_detected_at": _iso(),
        "status": "SUSPECTED",
        "disarm_ttp_refs": [],
        "causal_edge_review_ids": [],
        "fimi_attribution": {
            "actor_tier": DEFAULT_FIMI_TIER,
            "confounders_cleared": False,
            "tier_rationale": None,
            "set_by": None,
            "set_at": None,
        },
        "hard_binding": HARD_BINDING,
        "evidentiary_weight": EVIDENTIARY_WEIGHT,
        "plain": "SUSPECTED. Correlation only. CONFIRMED waits on a confounder review (item 144). FIMI stays unattributed until then.",
    }
    store = _load()
    store["clusters"].append(rec)
    _save(store)
    return rec


def attach_ttp(
    *,
    campaign_cluster_id: str,
    disarm_technique_id: str,
    evidence_receipt_ids: Any,
    classified_by: str = "human_analyst",
) -> dict[str, Any]:
    tech = (disarm_technique_id or "").strip().upper()
    catalog = TECHNIQUES.get(tech)
    if catalog is None:
        return {
            "spec": TTP_SPEC,
            "ok": False,
            "error": "unknown_technique",
            "allowed": sorted(TECHNIQUES),
            "plain": "Only named DISARM ids. This mouth does not invent a TTP.",
        }
    evidence = _ids(evidence_receipt_ids)
    if not evidence:
        return {
            "spec": TTP_SPEC,
            "ok": False,
            "error": "evidence_required",
            "plain": "A DISARM label with nothing under it is a guess. evidence_receipt_ids required.",
        }
    who = (classified_by or "human_analyst").strip().lower()
    if who not in CLASSIFIERS:
        who = "human_analyst"
    store = _load()
    cluster = next(
        (c for c in store["clusters"] if c.get("campaign_cluster_id") == (campaign_cluster_id or "").strip()),
        None,
    )
    if not cluster:
        return {"spec": TTP_SPEC, "ok": False, "error": "cluster_not_found", "plain": "Unknown campaign_cluster_id."}
    ref = {
        "spec": TTP_SPEC,
        "ref_id": "disarm_" + uuid.uuid4().hex[:12],
        "campaign_cluster_id": cluster["campaign_cluster_id"],
        "disarm_tactic_id": catalog["disarm_tactic_id"],
        "disarm_technique_id": catalog["disarm_technique_id"],
        "name": catalog["name"],
        "evidence_receipt_ids": evidence,
        "classified_by": who,
        "classified_at": _iso(),
        "hard_binding": HARD_BINDING,
        "evidentiary_weight": EVIDENTIARY_WEIGHT,
    }
    cluster.setdefault("disarm_ttp_refs", []).append(ref)
    _save(store)
    return {**ref, "ok": True}


def review_edge(
    *,
    link_graph_edge_id: str,
    claimed_relationship: str,
    confounder_considered: Any,
    confounder_ruled_out: bool,
    reviewed_by: str,
    campaign_cluster_id: str | None = None,
) -> dict[str, Any]:
    rel = (claimed_relationship or "").strip().lower()
    if rel not in RELATIONS:
        return {
            "spec": CAUSAL_SPEC,
            "ok": False,
            "error": "relationship_unknown",
            "plain": "claimed_relationship is causal, correlational, or unresolved.",
        }
    considered = [sanitize_mod.strip_agent(x, limit=200) for x in (confounder_considered or []) if str(x).strip()]
    if confounder_ruled_out and not considered:
        return {
            "spec": CAUSAL_SPEC,
            "ok": False,
            "error": "vacuous_confounder",
            "plain": "Ruling out a confounder with an empty list is the 122 vacuous-proof failure. Name what you checked.",
        }
    who = (reviewed_by or "").strip()
    edge = (link_graph_edge_id or "").strip()
    if not who or not edge:
        return {"spec": CAUSAL_SPEC, "ok": False, "error": "fields_required", "plain": "Need an edge id and a reviewer."}
    rec = {
        "spec": CAUSAL_SPEC,
        "ok": True,
        "review_id": "cedge_" + uuid.uuid4().hex[:12],
        "link_graph_edge_id": edge,
        "campaign_cluster_id": (campaign_cluster_id or "").strip() or None,
        "claimed_relationship": rel,
        "confounder_considered": considered,
        "confounder_ruled_out": bool(confounder_ruled_out),
        "reviewed_by": who,
        "reviewed_at": _iso(),
        "hard_binding": HARD_BINDING,
        "plain": (
            "Confounder named and ruled out. This is still a review, not hash proof."
            if confounder_ruled_out
            else "Confounder not ruled out. Cluster stays correlational."
        ),
    }
    store = _load()
    store["reviews"].append(rec)
    cid = rec["campaign_cluster_id"]
    if cid:
        cluster = next((c for c in store["clusters"] if c.get("campaign_cluster_id") == cid), None)
        if cluster:
            cluster.setdefault("causal_edge_review_ids", []).append(rec["review_id"])
    _save(store)
    return rec


def _confirmable(cluster: dict[str, Any], reviews: list[dict[str, Any]]) -> bool:
    ids = set(cluster.get("causal_edge_review_ids") or [])
    for rev in reviews:
        if rev.get("review_id") not in ids and rev.get("campaign_cluster_id") != cluster.get("campaign_cluster_id"):
            continue
        if (
            rev.get("confounder_ruled_out")
            and rev.get("claimed_relationship") == "causal"
            and rev.get("confounder_considered")
        ):
            return True
    return False


def set_status(*, campaign_cluster_id: str, status: str) -> dict[str, Any]:
    st = (status or "").strip().upper()
    if st not in STATUSES:
        return {"spec": SPEC, "ok": False, "error": "status_unknown", "plain": "SUSPECTED, CONFIRMED, or DISMISSED."}
    store = _load()
    cluster = next(
        (c for c in store["clusters"] if c.get("campaign_cluster_id") == (campaign_cluster_id or "").strip()),
        None,
    )
    if not cluster:
        return {"spec": SPEC, "ok": False, "error": "cluster_not_found", "plain": "Unknown campaign_cluster_id."}
    if st == "CONFIRMED" and not _confirmable(cluster, store.get("reviews") or []):
        return {
            "spec": SPEC,
            "ok": False,
            "error": "confounder_gate",
            "plain": "SUSPECTED cannot become CONFIRMED on correlation alone. Need a causal_edge_review with confounder_ruled_out true.",
        }
    cluster["status"] = st
    cluster["plain"] = (
        "CONFIRMED after confounder review. Still soft-binding, not hash proof."
        if st == "CONFIRMED"
        else ("DISMISSED." if st == "DISMISSED" else cluster.get("plain"))
    )
    _save(store)
    return {**cluster, "ok": True}


def set_fimi_tier(
    *,
    campaign_cluster_id: str,
    actor_tier: str,
    tier_rationale: str,
    set_by: str,
) -> dict[str, Any]:
    tier = (actor_tier or "").strip()
    if tier not in FIMI_TIERS:
        return {
            "spec": FIMI_SPEC,
            "ok": False,
            "error": "tier_unknown",
            "allowed": list(FIMI_TIERS),
            "plain": "EEAS four-tier ladder only. unattributed is the default, not a promotion.",
        }
    why = sanitize_mod.strip_agent(tier_rationale)
    who = (set_by or "").strip()
    if not why or not who:
        return {
            "spec": FIMI_SPEC,
            "ok": False,
            "error": "rationale_required",
            "plain": "A FIMI tier needs who set it and the indicator that justified it. Not a bare label.",
        }
    store = _load()
    cluster = next(
        (c for c in store["clusters"] if c.get("campaign_cluster_id") == (campaign_cluster_id or "").strip()),
        None,
    )
    if not cluster:
        return {"spec": FIMI_SPEC, "ok": False, "error": "cluster_not_found", "plain": "Unknown campaign_cluster_id."}
    cleared = _confirmable(cluster, store.get("reviews") or [])
    if not cleared:
        return {
            "spec": FIMI_SPEC,
            "ok": False,
            "error": "confounders_not_cleared",
            "plain": "Tiers above unattributed wait on item 144. DISARM names the TTP; FIMI names actor-confidence after confounders.",
        }
    rec = {
        "spec": FIMI_SPEC,
        "ok": True,
        "tier_id": "fimi_" + uuid.uuid4().hex[:12],
        "campaign_cluster_id": cluster["campaign_cluster_id"],
        "actor_tier": tier,
        "tier_rationale": why,
        "confounders_cleared": True,
        "set_by": who,
        "set_at": _iso(),
        "plain": "FIMI " + tier + ". Soft-binding attribution-confidence, not a sanctions finding.",
    }
    cluster["fimi_attribution"] = rec
    _save(store)
    return rec
