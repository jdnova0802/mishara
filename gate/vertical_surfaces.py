"""Items 37–49. Receipt/count/stat surfaces. No CV model. No insurance product."""
from __future__ import annotations

import json
import math
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MIN_SAMPLE = 20
HEX_OK = re.compile(r"^[a-fA-F0-9]{16,64}$")
DATING_KEYS = ("dating", "catfish", "profile", "companion")
WORKER_KEYS = ("warehouse", "gig", "shift", "worker", "labor")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _path(env: str, name: str) -> Path:
    return Path(os.getenv(env) or Path(__file__).resolve().parent / "data" / name)


def _load_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return list(data.get("rows") or [])
    return []


def _save_list(path: Path, rows: list[dict[str, Any]], spec: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"spec": spec, "rows": rows[-200:]}, indent=2), encoding="utf-8")


def record_tick(*, kind: str, event_id: str, present: bool) -> None:
    path = _path("GATE_TICKER_PATH", "public_ticker.json")
    rows = _load_list(path)
    rows.append(
        {
            "kind": kind,
            "event_id": event_id,
            "receipt_present": bool(present),
            "catfish_model": False,
            "at": _now(),
        }
    )
    _save_list(path, rows, "gate-public-ticker-v1")


def ticker(bind_rows: list[dict[str, Any]]) -> dict[str, Any]:
    ticks = list(reversed(_load_list(_path("GATE_TICKER_PATH", "public_ticker.json"))))[:50]
    hops = []
    for row in bind_rows:
        blob = json.dumps(row.get("hop") or {}, default=str).lower()
        if any(k in blob for k in DATING_KEYS):
            hops.append(
                {
                    "id": row.get("id"),
                    "decision": row.get("decision"),
                    "created_at": row.get("created_at"),
                }
            )
    return {
        "spec": "gate-catfish-ticker-v1",
        "catfish_model": False,
        "plain": "Receipt-presence ticks and hops that already say dating. Not a detector.",
        "ticks": ticks,
        "hop_hits": hops,
    }


def legit_check(*, listing_id: str, row: dict[str, Any] | None) -> dict[str, Any]:
    listing_id = (listing_id or "").strip()
    present = bool(row and row.get("receipt_hash"))
    out = {
        "spec": "gate-legit-check-v1",
        "listing_id": listing_id or None,
        "cv_model": False,
        "receipt_present": present,
        "event_id": (row or {}).get("id"),
        "decision": (row or {}).get("decision"),
        "plain": (
            "A signed receipt exists for this listing claim."
            if present
            else "No signed receipt. Gate does not inspect stitching, serials, or photos (item 47)."
        ),
    }
    path = _path("GATE_LEGIT_PATH", "legit_checks.json")
    rows = _load_list(path)
    if listing_id:
        rows.append({**out, "at": _now()})
        _save_list(path, rows, "gate-legit-check-v1")
    return out


def legit_board() -> dict[str, Any]:
    rows = _load_list(_path("GATE_LEGIT_PATH", "legit_checks.json"))
    shame = [r for r in reversed(rows) if not r.get("receipt_present")][:50]
    verified = [r for r in reversed(rows) if r.get("receipt_present")][:50]
    return {
        "spec": "gate-legit-board-v1",
        "cv_model": False,
        "plain": "Hall of shame is unsigned listing claims, not a photo fail.",
        "verified": verified,
        "shame": shame,
    }


def worker_score(rows: list[dict[str, Any]], fuse_id: str) -> dict[str, Any]:
    fuse_id = (fuse_id or "").strip()
    mine = [r for r in rows if str(r.get("fuse_id") or "") == fuse_id] if fuse_id else []
    counts = {"ALLOW": 0, "BLOCK": 0, "HOLD": 0, "HALT": 0}
    for r in mine:
        d = str(r.get("decision") or "").upper()
        if d in counts:
            counts[d] += 1
    return {
        "spec": "gate-worker-score-v1",
        "fuse_id": fuse_id or None,
        "counts": counts,
        "fcra_score": False,
        "plain": (
            "Your own event counts on this mouth. Not FCRA, not CDPI 75–79, not an employer file."
        ),
    }


def wati(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by: dict[str, dict[str, int]] = {}
    for row in rows:
        hop = row.get("hop") if isinstance(row.get("hop"), dict) else {}
        company = str(hop.get("company") or hop.get("employer") or "").strip()
        if not company:
            blob = json.dumps(hop, default=str).lower()
            if not any(k in blob for k in WORKER_KEYS):
                continue
            company = str(row.get("fuse_id") or "unlabeled")
        slot = by.setdefault(company, {"company": company, "allow": 0, "block": 0, "hold": 0, "halt": 0})
        d = str(row.get("decision") or "").upper()
        if d == "ALLOW":
            slot["allow"] += 1
        elif d == "BLOCK":
            slot["block"] += 1
        elif d == "HOLD":
            slot["hold"] += 1
        elif d == "HALT":
            slot["halt"] += 1
    agents = sorted(by.values(), key=lambda a: a["block"] + a["halt"], reverse=True)
    return {
        "spec": "gate-wati-v1",
        "plain": "Transparency index from hops that already name a company/employer. Empty is honest.",
        "companies": agents,
    }


def radar(dockets: list[dict[str, Any]]) -> dict[str, Any]:
    watches = [
        {
            "id": "eu_ai_act",
            "label": "EU AI Act — Annex III high-risk logging",
            "url": "https://artificialintelligenceact.eu/",
            "scraped": False,
        },
        {
            "id": "naic_bdaiwg",
            "label": "NAIC Big Data and Artificial Intelligence (H) WG",
            "url": "https://content.naic.org/committees/h/big-data-artificial-intelligence-wg",
            "scraped": False,
        },
        {
            "id": "hmt_payments",
            "label": "HM Treasury — modernising payment services",
            "url": "https://www.gov.uk/government/consultations/modernising-payment-services-regulation",
            "scraped": False,
        },
    ]
    return {
        "spec": "gate-regulatory-radar-v1",
        "scraped": False,
        "as_of": "2026-11-10",
        "plain": "Named dockets this mouth already cites. Not a live scrape of every AI bill.",
        "watches": watches,
        "dockets": dockets,
    }


def _series_flags(values: list[float], *, metric: str) -> dict[str, Any]:
    if len(values) < MIN_SAMPLE:
        return {
            "spec": "gate-series-anomaly-v1",
            "metric": metric,
            "flags": [],
            "reason": "no_samples",
            "sample_size": len(values),
            "min_sample_size": MIN_SAMPLE,
            "never_auto_acted": True,
        }
    avg = sum(values) / len(values)
    std = math.sqrt(sum((v - avg) ** 2 for v in values) / len(values))
    flags = []
    if std > 0:
        for i, v in enumerate(values):
            z = (v - avg) / std
            if abs(z) >= 3:
                flags.append({"index": i, "value": v, "z": round(z, 3)})
    return {
        "spec": "gate-series-anomaly-v1",
        "metric": metric,
        "mean": avg,
        "stddev": std,
        "sample_size": len(values),
        "min_sample_size": MIN_SAMPLE,
        "flags": flags,
        "never_auto_acted": True,
        "plain": "Flags only. A severe outlier can inflate stddev and mask a milder one.",
    }


def shift_anomaly(hours: list[Any]) -> dict[str, Any]:
    vals: list[float] = []
    for h in hours:
        try:
            vals.append(float(h))
        except (TypeError, ValueError):
            continue
    return _series_flags(vals, metric="shift_hours")


def listing_price_anomaly(prices: list[Any]) -> dict[str, Any]:
    vals: list[float] = []
    for p in prices:
        try:
            vals.append(float(p))
        except (TypeError, ValueError):
            continue
    out = _series_flags(vals, metric="listing_price")
    out["cv_model"] = False
    out["plain"] = (
        "Price sigma vs the posted series. Not market-manipulation proof and not item 47 vision."
    )
    return out


def add_shadow(*, employer_hash: str, feature: str, outcome: str) -> dict[str, Any]:
    employer_hash = (employer_hash or "").strip().lower()
    feature = (feature or "").strip()[:80]
    outcome = (outcome or "").strip().upper()
    if not HEX_OK.match(employer_hash):
        raise ValueError("employer_hash_must_be_hex")
    if "@" in feature or " " in employer_hash:
        raise ValueError("pii_rejected")
    if outcome not in {"ALLOW", "BLOCK", "HOLD", "HALT"}:
        raise ValueError("unknown_outcome")
    path = _path("GATE_SHADOW_PATH", "shadow_audit.json")
    rows = _load_list(path)
    rows.append(
        {
            "employer_hash": employer_hash,
            "feature": feature,
            "outcome": outcome,
            "at": _now(),
        }
    )
    _save_list(path, rows, "gate-shadow-audit-v1")
    return reconstruct(employer_hash)


def reconstruct(employer_hash: str) -> dict[str, Any]:
    employer_hash = (employer_hash or "").strip().lower()
    rows = [
        r
        for r in _load_list(_path("GATE_SHADOW_PATH", "shadow_audit.json"))
        if r.get("employer_hash") == employer_hash
    ]
    by_feature: dict[str, dict[str, int]] = {}
    for r in rows:
        feat = str(r.get("feature") or "unspecified")
        slot = by_feature.setdefault(feat, {"feature": feat, "n": 0, "block": 0})
        slot["n"] += 1
        if str(r.get("outcome") or "").upper() in {"BLOCK", "HALT"}:
            slot["block"] += 1
    reconstructed = [
        {**s, "block_rate": (s["block"] / s["n"]) if s["n"] else 0}
        for s in sorted(by_feature.values(), key=lambda x: x["n"], reverse=True)
    ]
    return {
        "spec": "gate-shadow-audit-v1",
        "employer_hash": employer_hash,
        "n": len(rows),
        "reconstructed": reconstructed,
        "plain": "Crowdsourced feature→outcome rates. Not the employer's filed policy.",
    }


def research_stub(item: int, name: str) -> dict[str, Any]:
    return {
        "spec": "gate-research-stub-v1",
        "item": item,
        "name": name,
        "built": False,
        "needs": "trained_computer_vision_model",
        "plain": f"Item {item} is a research track, not a detector on this mouth.",
    }


def parametric_stub() -> dict[str, Any]:
    return {
        "spec": "gate-parametric-v1",
        "product": False,
        "needs": "outside_underwriter",
        "munich_re": False,
        "endorsement": False,
        "plain": (
            "No parametric product. Item 49 needs an underwriter at the table "
            "for trigger/payout terms. BLOCK receipts are not a policy."
        ),
    }
