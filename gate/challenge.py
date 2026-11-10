"""Items 109–111 — Erra counter-case, harm syndromic, Verra joint-freshness."""
from __future__ import annotations

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from gate import receipt as receipt_mod
except ImportError:
    import receipt as receipt_mod

try:
    from gate import sanitize as sanitize_mod
except ImportError:
    import sanitize as sanitize_mod

COUNTER_SPEC = "gate-erra-counter-case-v1"
HARM_SPEC = "gate-harm-syndromic-v1"
FRESH_SPEC = "gate-joint-freshness-v1"

# Schema floor for 109, not a traffic-tuned number.
ENGAGEMENT_FLOOR = 0.5
# Confirmed cluster size before auto-tighten. Named, not a live baseline.
CLUSTER_REPEAT_N = 3

VERDICTS = ("ACT", "HOLD")
GATE_VERDICTS = ("ALLOW", "BLOCK", "HOLD")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _now()).astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _path(env: str, name: str) -> Path:
    return Path(os.getenv(env) or Path(__file__).resolve().parent / "data" / name)


def _load(path: Path, spec: str, key: str) -> dict[str, Any]:
    if not path.exists():
        return {"spec": spec, key: []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"spec": spec, key: []}
    if not isinstance(data, dict):
        return {"spec": spec, key: []}
    data.setdefault(key, [])
    return data


def _save(path: Path, store: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")


def hop_signals(hop: dict[str, Any] | None) -> list[str]:
    hop = hop if isinstance(hop, dict) else {}
    refs = []
    for key in ("reason", "epoch_reason", "signal_id", "pattern_grade", "state", "vertical", "line"):
        val = hop.get(key)
        if val is None or val is False:
            continue
        refs.append(str(val).strip())
    extra = hop.get("signals")
    if isinstance(extra, list):
        refs.extend(str(x).strip() for x in extra if x)
    erra = hop.get("erra") if isinstance(hop.get("erra"), dict) else {}
    if erra.get("signal_id"):
        refs.append(str(erra["signal_id"]))
    return [r for r in refs if r]


def _opposite(verdict: str) -> str:
    return "HOLD" if verdict == "ACT" else "ACT"


def grade_counter_case(
    *,
    evidence_cited: list[str],
    hop: dict[str, Any] | None,
    now: datetime | None = None,
) -> dict[str, Any]:
    cited = [sanitize_mod.strip_agent(x, limit=200) for x in evidence_cited if str(x).strip()]
    available = {s.lower() for s in hop_signals(hop)}
    hits = [c for c in cited if c.lower() in available]
    engagement = (len(hits) / len(cited)) if cited else 0.0
    strawman = not cited or engagement <= 0.0
    return {
        "engagement_score": round(engagement, 3),
        "strawman_flag": strawman,
        "grader": "rule",
        "graded_at": _iso(now),
        "hits": hits,
        "available": sorted(available),
    }


def lock_decision(
    *,
    verdict: str,
    hop: dict[str, Any] | None,
    claim: str | None = None,
    evidence_cited: list[str] | None = None,
    rejection_reason: str | None = None,
    constructed_at: str | None = None,
    decision_id: str | None = None,
    now: datetime | None = None,
    persist: bool = True,
) -> dict[str, Any]:
    now = now or _now()
    locked = _iso(now)
    v = (verdict or "").strip().upper()
    if v not in VERDICTS:
        v = "HOLD"
    cited = list(evidence_cited) if evidence_cited is not None else hop_signals(hop)
    opposite = _opposite(v)
    auto_claim = claim or f"Strongest case for {opposite}: the hop does not compel {v}."
    constructed = constructed_at or locked
    if constructed > locked:
        constructed = locked
    score = grade_counter_case(evidence_cited=cited, hop=hop, now=now)
    review = score["engagement_score"] < ENGAGEMENT_FLOOR or score["strawman_flag"]
    rec = {
        "spec": COUNTER_SPEC,
        "decision_id": decision_id or "erra-" + uuid.uuid4().hex[:12],
        "verdict": v,
        "verdict_locked_at": locked,
        "counter_case": {
            "claim": sanitize_mod.strip_agent(auto_claim),
            "evidence_cited": cited,
            "rejection_reason": sanitize_mod.strip_agent(
                rejection_reason or f"{v} still wins on the cited hop fields."
            ),
            "constructed_at": constructed,
        },
        "counter_case_score": {
            "engagement_score": score["engagement_score"],
            "strawman_flag": score["strawman_flag"],
            "grader": score["grader"],
            "graded_at": score["graded_at"],
        },
        "review": review,
        "engagement_floor": ENGAGEMENT_FLOOR,
        "plain": (
            "Review regardless of verdict."
            if review
            else "Counter-case engaged real hop evidence."
        ),
    }
    if persist:
        path = _path("GATE_COUNTER_PATH", "counter_cases.json")
        store = _load(path, COUNTER_SPEC, "rows")
        store["rows"].append(rec)
        _save(path, store)
    return rec


def list_counter_cases() -> list[dict[str, Any]]:
    return list(_load(_path("GATE_COUNTER_PATH", "counter_cases.json"), COUNTER_SPEC, "rows")["rows"])


def _cluster_id(fingerprints: list[str]) -> str:
    blob = "|".join(sorted(fingerprints))
    return "clus_" + hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def report_harm(
    *,
    harm_description: str,
    preceding_signals: list[dict[str, Any]],
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or _now()
    signals = []
    fps = []
    for raw in preceding_signals or []:
        if not isinstance(raw, dict):
            continue
        fp = str(raw.get("signal_fingerprint") or "").strip()
        if not fp:
            continue
        verdict = str(raw.get("gate_verdict_at_time") or "ALLOW").upper()
        if verdict not in GATE_VERDICTS:
            verdict = "ALLOW"
        try:
            sub = float(raw.get("sub_threshold_score") or 0)
        except (TypeError, ValueError):
            sub = 0.0
        sub = max(0.0, min(1.0, sub))
        rec = {
            "signal_id": str(raw.get("signal_id") or fp[:12]),
            "observed_at": str(raw.get("observed_at") or _iso(now)),
            "gate_verdict_at_time": verdict,
            "signal_fingerprint": fp,
            "sub_threshold_score": sub,
        }
        signals.append(rec)
        fps.append(fp)
    cluster = _cluster_id(fps) if fps else "clus_empty"
    report = {
        "spec": HARM_SPEC,
        "harm_report_id": "harm_" + uuid.uuid4().hex[:12],
        "reported_at": _iso(now),
        "harm_description": sanitize_mod.strip_agent(harm_description),
        "preceding_signals": signals,
        "fingerprint_cluster_id": cluster,
    }
    path = _path("GATE_HARM_PATH", "harm_reports.json")
    store = _load(path, HARM_SPEC, "rows")
    store["rows"].append(report)
    _save(path, store)
    return report


def cluster_counts(reports: list[dict[str, Any]] | None = None) -> dict[str, int]:
    reports = reports if reports is not None else list_harms()
    counts: dict[str, int] = {}
    for r in reports:
        cid = str(r.get("fingerprint_cluster_id") or "")
        if cid and cid != "clus_empty":
            counts[cid] = counts.get(cid, 0) + 1
    return counts


def list_harms() -> list[dict[str, Any]]:
    return list(_load(_path("GATE_HARM_PATH", "harm_reports.json"), HARM_SPEC, "rows")["rows"])


def list_adjustments() -> list[dict[str, Any]]:
    return list(_load(_path("GATE_HARM_ADJ_PATH", "threshold_adjustments.json"), HARM_SPEC, "adjustments")["adjustments"])


def propose_adjustment(
    *,
    erra_rule_id: str,
    old_threshold: float,
    new_threshold: float,
    cluster_id: str,
    approved: bool = False,
    verify_url: str = "",
) -> dict[str, Any]:
    reports = [r for r in list_harms() if r.get("fingerprint_cluster_id") == cluster_id]
    n = len(reports)
    tighten = new_threshold < old_threshold
    if not tighten and not approved:
        return {
            "ok": False,
            "spec": HARM_SPEC,
            "error": "loosen_needs_human",
            "plain": "Loosening always needs human approval. Tightening may auto-apply fail-closed.",
        }
    if tighten and n < CLUSTER_REPEAT_N:
        return {
            "ok": False,
            "spec": HARM_SPEC,
            "error": "cluster_below_n",
            "cluster_repeat_count": n,
            "n": CLUSTER_REPEAT_N,
        }
    hop = {
        "kind": "threshold_adjustment",
        "erra_rule_id": erra_rule_id,
        "old_threshold": old_threshold,
        "new_threshold": new_threshold,
        "cluster_id": cluster_id,
        "tighten": tighten,
    }
    issued = receipt_mod.issue_receipt(
        event_id="thresh:" + cluster_id,
        fuse_id="erra-threshold",
        job_id=None,
        decision="HOLD" if tighten else "ALLOW",
        acted=tighten or approved,
        verify_url=verify_url or None,
        created_at=_iso(),
        hop=hop,
        prev_receipt_hash=None,
    )
    adj = {
        "spec": HARM_SPEC,
        "ok": True,
        "erra_rule_id": erra_rule_id,
        "old_threshold": old_threshold,
        "new_threshold": new_threshold,
        "cluster_repeat_count": n,
        "adjusted_at": _iso(),
        "adjustment_receipt_id": issued.get("receipt_hash"),
        "receipt_hash": issued.get("receipt_hash"),
        "auto_applied": tighten,
        "approved": approved or tighten,
        "fingerprint_cluster_id": cluster_id,
        "plain": "Tightening auto-applied fail-closed." if tighten else "Loosening applied after human approval.",
    }
    path = _path("GATE_HARM_ADJ_PATH", "threshold_adjustments.json")
    store = _load(path, HARM_SPEC, "adjustments")
    store["adjustments"].append(adj)
    _save(path, store)
    return adj


def staleness_window_ms() -> int | None:
    """Item 111 — must be tuned on live Erra/Velaru latency. Never guess a demo number."""
    raw = os.getenv("GATE_STALENESS_WINDOW_MS", "").strip()
    if not raw:
        return None
    try:
        val = int(raw)
    except ValueError:
        return None
    return val if val > 0 else None


def parse_hlc(value: Any) -> dict[str, int] | None:
    """Hybrid logical clock: (logical, wall_ms). Wall-clock alone is rejected."""
    if isinstance(value, dict):
        try:
            logical = int(value.get("logical"))
            wall = int(value.get("wall_ms") if value.get("wall_ms") is not None else value.get("wall"))
        except (TypeError, ValueError):
            return None
        return {"logical": logical, "wall_ms": wall}
    return None


def hlc_delta_ms(a: dict[str, int], b: dict[str, int]) -> int:
    """Physical component first; logical ticks break ties without pretending they are wall time."""
    dw = abs(a["wall_ms"] - b["wall_ms"])
    if dw:
        return dw
    return abs(a["logical"] - b["logical"])


def freshness_check(
    *,
    bind_id: str,
    erra_signal: dict[str, Any] | None,
    velaru_proof: dict[str, Any] | None,
) -> dict[str, Any]:
    window = staleness_window_ms()
    erra_hlc = parse_hlc((erra_signal or {}).get("hlc_timestamp") or (erra_signal or {}).get("hlc"))
    vel_hlc = parse_hlc((velaru_proof or {}).get("hlc_timestamp") or (velaru_proof or {}).get("hlc"))
    if erra_hlc is None or vel_hlc is None:
        return {
            "spec": FRESH_SPEC,
            "bind_id": bind_id,
            "staleness_window_ms": window,
            "window_tuned": window is not None,
            "freshness_check": {"delta_ms": None, "within_window": None},
            "bind_result": "DEFERRED",
            "plain": "HLC timestamps required on both sides. Wall-clock pairing is unproven.",
        }
    delta = hlc_delta_ms(erra_hlc, vel_hlc)
    if window is None:
        within = None
        result = "DEFERRED"
        plain = (
            "staleness_window_ms is unset until live Erra/Velaru latency is measured. "
            "Unproven pairing is DEFERRED, not BLOCK."
        )
    else:
        within = delta <= window
        result = "ALLOW" if within else "DEFERRED"
        plain = (
            "Pairing is inside the tuned window."
            if within
            else "Stale pairing is unproven — DEFERRED, not auto-BLOCK."
        )
    return {
        "spec": FRESH_SPEC,
        "bind_id": bind_id,
        "erra_signal": {"value": (erra_signal or {}).get("value"), "hlc_timestamp": erra_hlc},
        "velaru_proof": {"value": (velaru_proof or {}).get("value"), "hlc_timestamp": vel_hlc},
        "staleness_window_ms": window,
        "window_tuned": window is not None,
        "freshness_check": {"delta_ms": delta, "within_window": within},
        "bind_result": result,
        "plain": plain,
    }


def attach_to_receipt(row: dict[str, Any]) -> dict[str, Any]:
    hop = row.get("hop") if isinstance(row.get("hop"), dict) else {}
    erra = hop.get("erra") if isinstance(hop.get("erra"), dict) else {}
    vel = hop.get("velaru") if isinstance(hop.get("velaru"), dict) else {}
    verdict = str(erra.get("verdict") or hop.get("pattern_verdict") or "").upper()
    if verdict not in VERDICTS:
        verdict = "HOLD" if str(row.get("decision") or "").upper() in {"BLOCK", "HOLD", "HALT"} else "ACT"
    counter = None
    if erra:
        counter = lock_decision(
            verdict=verdict,
            hop=hop,
            claim=erra.get("counter_claim"),
            evidence_cited=erra.get("evidence_cited") if isinstance(erra.get("evidence_cited"), list) else hop_signals(hop),
            rejection_reason=erra.get("rejection_reason"),
            constructed_at=erra.get("constructed_at"),
            decision_id=erra.get("decision_id") or str(row.get("id")),
            persist=False,
        )
    fresh = None
    if erra.get("hlc") or erra.get("hlc_timestamp") or vel.get("hlc") or vel.get("hlc_timestamp"):
        fresh = freshness_check(
            bind_id=str(row.get("id") or ""),
            erra_signal=erra if erra else hop.get("erra_signal"),
            velaru_proof=vel if vel else hop.get("velaru_proof"),
        )
    return {
        "counter_case": counter,
        "freshness": fresh,
        "in_signed_canonical": False,
    }
