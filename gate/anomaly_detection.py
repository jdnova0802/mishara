"""Item 133 — population anomaly flags vs a cohort baseline.

Flags; never dispositions. MIN_SAMPLE_SIZE gates eligibility.
Mean/stddev is the specced baseline. A severe outlier inflates stddev and
can mask a milder one (same shape as item 139). Median+MAD is a follow-on.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

try:
    from gate.link_graph import ReceiptRecord
except ImportError:
    from link_graph import ReceiptRecord

SPEC = "gate-anomaly-v1"
MIN_SAMPLE_SIZE = 20
DEVIATION_THRESHOLD_SIGMA = 3.0
METRICS = ("brier_score", "block_rate", "severity_weighted_load")


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def _stddev(values: list[float], avg: float) -> float:
    var = _mean([(v - avg) ** 2 for v in values])
    return math.sqrt(var)


def operator_values(records: list[ReceiptRecord], metric: str) -> dict[str, float]:
    buckets: dict[str, list[float]] = {}
    for rec in records:
        if rec.metrics.get(metric) is None:
            continue
        buckets.setdefault(rec.operator_id, []).append(float(rec.metrics[metric]))
    return {op: _mean(vals) for op, vals in buckets.items() if vals}


def compute_baseline(
    records: list[ReceiptRecord],
    *,
    cohort_vertical: str,
    metric: str,
    period_start: str = "",
    period_end: str = "",
) -> dict[str, Any] | None:
    if metric not in METRICS:
        raise ValueError("unknown_metric")
    windowed = [
        r
        for r in records
        if r.cohort_vertical == cohort_vertical
        and (not period_start or r.created_at >= period_start)
        and (not period_end or r.created_at <= period_end)
    ]
    values = list(operator_values(windowed, metric).values())
    if not values:
        return None
    avg = _mean(values)
    return {
        "spec": SPEC,
        "baseline_id": f"baseline:{cohort_vertical}:{metric}:{period_start}:{period_end}",
        "cohort_vertical": cohort_vertical,
        "metric": metric,
        "period_start": period_start or None,
        "period_end": period_end or None,
        "mean": avg,
        "stddev": _stddev(values, avg),
        "sample_size": len(values),
        "min_sample_size": MIN_SAMPLE_SIZE,
        "note": "mean/stddev; a severe outlier can inflate stddev and mask a milder one",
    }


def flag_anomalies(records: list[ReceiptRecord], baseline: dict[str, Any]) -> list[dict[str, Any]]:
    if int(baseline.get("sample_size") or 0) < MIN_SAMPLE_SIZE:
        return []
    if float(baseline.get("stddev") or 0) == 0:
        return []
    metric = baseline["metric"]
    cohort = baseline["cohort_vertical"]
    windowed = [
        r
        for r in records
        if r.cohort_vertical == cohort
        and (not baseline.get("period_start") or r.created_at >= baseline["period_start"])
        and (not baseline.get("period_end") or r.created_at <= baseline["period_end"])
    ]
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    flags: list[dict[str, Any]] = []
    for operator_id, value in operator_values(windowed, metric).items():
        sigma = abs(value - float(baseline["mean"])) / float(baseline["stddev"])
        if sigma < DEVIATION_THRESHOLD_SIGMA:
            continue
        flags.append(
            {
                "flag_id": f"flag:{baseline['baseline_id']}:{operator_id}",
                "operator_id": operator_id,
                "baseline_id": baseline["baseline_id"],
                "observed_value": value,
                "deviation_sigma": sigma,
                "flagged_at": now,
                "reviewed": False,
                "disposition": None,
            }
        )
    flags.sort(key=lambda f: f["deviation_sigma"], reverse=True)
    return flags
