"""Items 141 / 147 — STIX 2.1 bundle export and ATT&CK↔DISARM SROs.

Serialization over 136/137 labels. Not a TAXII server, not a new detector.
Relationship types are facilitates | compromises | precedes and need evidence.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from gate import atlas as atlas_mod
except ImportError:
    import atlas as atlas_mod

try:
    from gate import campaign as campaign_mod
except ImportError:
    import campaign as campaign_mod

try:
    from gate import sanitize as sanitize_mod
except ImportError:
    import sanitize as sanitize_mod

SPEC = "gate-stix-export-v1"
REL_SPEC = "gate-cross-domain-rel-v1"
STIX_VERSION = "2.1"
TAXII = False
NS = uuid.UUID("6ba7b811-9dad-11d1-80b4-00c04fd430c8")  # URL namespace
REL_TYPES = ("facilitates", "compromises", "precedes")

# Documented enterprise ATT&CK id used in the 147 worked example. Not a catalog dump.
ATTACK_TECHNIQUES = {
    "T1566": {"name": "Phishing", "source_name": "mitre-attack"},
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _now()).astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _path() -> Path:
    return Path(os.getenv("GATE_STIX_PATH") or Path(__file__).resolve().parent / "data" / "stix.json")


def _load() -> dict[str, Any]:
    path = _path()
    if not path.exists():
        return {"spec": SPEC, "bundles": [], "relationships": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"spec": SPEC, "bundles": [], "relationships": []}
    if not isinstance(data, dict):
        return {"spec": SPEC, "bundles": [], "relationships": []}
    data.setdefault("bundles", [])
    data.setdefault("relationships", [])
    return data


def _save(store: dict[str, Any]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")


def _ids(raw: Any) -> list[str]:
    if not isinstance(raw, list):
        return []
    out: list[str] = []
    for x in raw:
        s = str(x).strip()
        if s and s not in out:
            out.append(s)
    return out


def stix_id(kind: str, key: str) -> str:
    return kind + "--" + str(uuid.uuid5(NS, "https://gate.velaru.xyz/stix/" + kind + "/" + key))


def list_bundles() -> list[dict[str, Any]]:
    return list(_load().get("bundles") or [])


def list_relationships() -> list[dict[str, Any]]:
    return list(_load().get("relationships") or [])


def _attack_pattern(*, external_id: str, name: str, source_name: str, created: str) -> dict[str, Any]:
    return {
        "type": "attack-pattern",
        "spec_version": STIX_VERSION,
        "id": stix_id("attack-pattern", source_name + ":" + external_id),
        "created": created,
        "modified": created,
        "name": name,
        "external_references": [{"source_name": source_name, "external_id": external_id}],
    }


def link(
    *,
    source_ref: str,
    target_ref: str,
    relationship_type: str,
    evidence_receipt_ids: Any,
) -> dict[str, Any]:
    rel = (relationship_type or "").strip().lower()
    if rel not in REL_TYPES:
        return {
            "spec": REL_SPEC,
            "ok": False,
            "error": "relationship_type_unknown",
            "allowed": list(REL_TYPES),
            "plain": "facilitates, compromises, or precedes.",
        }
    src = (source_ref or "").strip().upper()
    tgt = (target_ref or "").strip().upper()
    evidence = _ids(evidence_receipt_ids)
    if not evidence:
        return {
            "spec": REL_SPEC,
            "ok": False,
            "error": "evidence_required",
            "plain": "A cross-domain SRO with nothing under it is a guess. evidence_receipt_ids required.",
        }
    attack = ATTACK_TECHNIQUES.get(src) or atlas_mod.TECHNIQUES.get(src)
    disarm = campaign_mod.TECHNIQUES.get(tgt)
    if attack is None:
        return {
            "spec": REL_SPEC,
            "ok": False,
            "error": "source_unknown",
            "plain": "source_ref is a named ATLAS id or the documented ATT&CK id T1566. This mouth does not invent TTPs.",
        }
    if disarm is None:
        return {
            "spec": REL_SPEC,
            "ok": False,
            "error": "target_unknown",
            "plain": "target_ref must be a named DISARM technique already in 137.",
        }
    rec = {
        "spec": REL_SPEC,
        "ok": True,
        "relationship_id": "xdr_" + uuid.uuid4().hex[:12],
        "source_ref": src,
        "target_ref": tgt,
        "relationship_type": rel,
        "evidence_receipt_ids": evidence,
        "logged_at": _iso(),
        "plain": src + " " + rel + " " + tgt + ". Soft-binding; not a detector.",
    }
    store = _load()
    store["relationships"].append(rec)
    _save(store)
    return rec


def export_bundle(
    *,
    source_receipt_ids: Any,
    atlas_technique_ids: Any = None,
    disarm_technique_ids: Any = None,
    attack_technique_ids: Any = None,
    relationship_ids: Any = None,
    shared_with: Any = None,
) -> dict[str, Any]:
    receipts = _ids(source_receipt_ids)
    if not receipts:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "receipts_required",
            "plain": "A STIX bundle without receipts is empty interchange, not fusion.",
        }
    atlas_ids = [x.strip().upper() for x in _ids(atlas_technique_ids)]
    disarm_ids = [x.strip().upper() for x in _ids(disarm_technique_ids)]
    attack_ids = [x.strip().upper() for x in _ids(attack_technique_ids)]
    for aid in atlas_ids:
        if aid not in atlas_mod.TECHNIQUES:
            return {
                "spec": SPEC,
                "ok": False,
                "error": "atlas_unknown",
                "plain": "Only named ATLAS ids from item 136.",
            }
    for did in disarm_ids:
        if did not in campaign_mod.TECHNIQUES:
            return {
                "spec": SPEC,
                "ok": False,
                "error": "disarm_unknown",
                "plain": "Only named DISARM ids from item 137.",
            }
    for tid in attack_ids:
        if tid not in ATTACK_TECHNIQUES:
            return {
                "spec": SPEC,
                "ok": False,
                "error": "attack_unknown",
                "plain": "Enterprise ATT&CK here is the documented T1566 example, not a scraped matrix.",
            }
    if not atlas_ids and not disarm_ids and not attack_ids:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "technique_required",
            "plain": "Export wraps 136/137 labels. Name at least one ATLAS, DISARM, or ATT&CK id.",
        }

    created = _iso()
    objects: list[dict[str, Any]] = []
    identity_id = stix_id("identity", "gate")
    objects.append(
        {
            "type": "identity",
            "spec_version": STIX_VERSION,
            "id": identity_id,
            "created": created,
            "modified": created,
            "name": "Gate / Nisaba",
            "identity_class": "organization",
        }
    )
    receipt_obj_ids = []
    for rid in receipts:
        oid = stix_id("x-gate-receipt", rid)
        receipt_obj_ids.append(oid)
        objects.append(
            {
                "type": "x-gate-receipt",
                "spec_version": STIX_VERSION,
                "id": oid,
                "created": created,
                "modified": created,
                "receipt_id": rid,
            }
        )
    objects.append(
        {
            "type": "observed-data",
            "spec_version": STIX_VERSION,
            "id": stix_id("observed-data", "|".join(receipts)),
            "created": created,
            "modified": created,
            "first_observed": created,
            "last_observed": created,
            "number_observed": len(receipts),
            "object_refs": receipt_obj_ids,
        }
    )
    pattern_ids: dict[str, str] = {}
    for aid in atlas_ids:
        tech = atlas_mod.TECHNIQUES[aid]
        ap = _attack_pattern(
            external_id=tech["atlas_technique_id"],
            name=tech["name"],
            source_name="mitre-atlas",
            created=created,
        )
        pattern_ids[aid] = ap["id"]
        objects.append(ap)
    for did in disarm_ids:
        tech = campaign_mod.TECHNIQUES[did]
        ap = _attack_pattern(
            external_id=tech["disarm_technique_id"],
            name=tech["name"],
            source_name="disarm",
            created=created,
        )
        pattern_ids[did] = ap["id"]
        objects.append(ap)
    for tid in attack_ids:
        tech = ATTACK_TECHNIQUES[tid]
        ap = _attack_pattern(
            external_id=tid,
            name=tech["name"],
            source_name=tech["source_name"],
            created=created,
        )
        pattern_ids[tid] = ap["id"]
        objects.append(ap)

    wanted = set(_ids(relationship_ids))
    included_rels = []
    for rel in list_relationships():
        take = rel.get("relationship_id") in wanted if wanted else bool(
            set(rel.get("evidence_receipt_ids") or []) & set(receipts)
        )
        if not take:
            continue
        src = rel["source_ref"]
        tgt = rel["target_ref"]
        if src not in pattern_ids or tgt not in pattern_ids:
            continue
        sro = {
            "type": "relationship",
            "spec_version": STIX_VERSION,
            "id": stix_id("relationship", rel["relationship_id"]),
            "created": rel["logged_at"],
            "modified": rel["logged_at"],
            "relationship_type": rel["relationship_type"],
            "source_ref": pattern_ids[src],
            "target_ref": pattern_ids[tgt],
        }
        objects.append(sro)
        included_rels.append(rel["relationship_id"])

    bundle_id = stix_id("bundle", created + "|" + "|".join(receipts))
    bundle_object = {
        "type": "bundle",
        "id": bundle_id,
        "spec_version": STIX_VERSION,
        "objects": objects,
    }
    partners = [sanitize_mod.strip_agent(x, limit=120) for x in (shared_with or []) if str(x).strip()]
    rec = {
        "spec": SPEC,
        "ok": True,
        "bundle_id": bundle_id,
        "source_receipt_ids": receipts,
        "stix_version": STIX_VERSION,
        "taxii": TAXII,
        "bundle_object": bundle_object,
        "generated_at": created,
        "shared_with": partners,
        "relationship_ids": included_rels,
        "plain": "STIX 2.1 interchange over existing 136/137 labels. Not a TAXII server.",
    }
    store = _load()
    store["bundles"].append(rec)
    _save(store)
    return rec
