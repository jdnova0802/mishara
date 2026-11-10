"""Items 87–90 — wire ticker, docket context, monitor, dateline.

External rows are the named dockets this mouth already cites (NAIC, HMT, GAAIA,
EU AI Act). This is not a Reuters/Bloomberg scrape and does not invent a filing.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SPEC = "gate-wire-ticker-v1"
MONITOR_SPEC = "gate-docket-monitor-v1"
DATELINE_SPEC = "gate-wire-dateline-v1"

# Wire-copy month abbreviations (Reuters/AP style).
_MONTHS = (
    "Jan.",
    "Feb.",
    "March",
    "April",
    "May",
    "June",
    "July",
    "Aug.",
    "Sept.",
    "Oct.",
    "Nov.",
    "Dec.",
)

# Reason / rule → named docket already in this repo. Unmapped rules stay null.
RULE_DOCKET = {
    "premium_exceeds_authority": "naic_v5_written",
    "LIMIT": "naic_v5_written",
    "line_not_in_authority": "naic_v5_written",
    "state_not_in_authority": "naic_v5_written",
    "model_225_30_day_commissioner_notice_missing": "naic_v5_written",
    "NOTICE": "naic_v5_written",
    "annex_iii": "eu_ai_act",
    "eu_ai_act": "eu_ai_act",
    "agentic_payments": "hmt_q15",
    "rtp": "hmt_q15",
    "fednow": "hmt_q15",
    "gaaia": "gaaia",
}

DOCKET_VERTICAL = {
    "naic_v5_written": "insurance",
    "naic_oct8_verbal": "insurance",
    "naic_bdaiwg": "insurance",
    "hmt_q15": "payments",
    "hmt_payments": "payments",
    "gaaia": "ai",
    "eu_ai_act": "ai",
    "regulator_page": "insurance",
}

DOCKET_DATELINE = {
    "naic_v5_written": ("KANSAS CITY", "NAIC"),
    "naic_oct8_verbal": ("KANSAS CITY", "NAIC"),
    "naic_bdaiwg": ("KANSAS CITY", "NAIC"),
    "hmt_q15": ("LONDON", "HMT"),
    "hmt_payments": ("LONDON", "HMT"),
    "gaaia": ("WASHINGTON", "House"),
    "eu_ai_act": ("BRUSSELS", "EU"),
    "regulator_page": ("NEW YORK", "Gate"),
}

WATCHES = (
    {
        "id": "eu_ai_act",
        "label": "EU AI Act — Annex III high-risk logging",
        "url": "https://artificialintelligenceact.eu/",
        "vertical": "ai",
        "status": "named",
        "plain": "Annex III high-risk logging. Named citation, not a live scrape.",
    },
    {
        "id": "naic_bdaiwg",
        "label": "NAIC Big Data and Artificial Intelligence (H) WG",
        "url": "https://content.naic.org/committees/h/big-data-artificial-intelligence-wg",
        "vertical": "insurance",
        "status": "named",
        "plain": "BDAIWG docket this mouth already cites.",
    },
    {
        "id": "hmt_payments",
        "label": "HM Treasury — modernising payment services",
        "url": "https://www.gov.uk/government/consultations/modernising-payment-services-regulation",
        "vertical": "payments",
        "status": "named",
        "plain": "Q15 agentic payments consultation this mouth already cites.",
    },
)


def _now(now: datetime | None = None) -> datetime:
    return now or datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _watch_path() -> Path:
    return Path(os.getenv("GATE_DOCKET_WATCH_PATH") or Path(__file__).resolve().parent / "data" / "docket_watch.json")


def dateline(
    *,
    jurisdiction: str,
    source: str,
    when: datetime | str | None,
    text: str,
) -> str:
    """Item 90 — jurisdiction + source + timestamp, wire-copy style."""
    if isinstance(when, str):
        s = when.strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        try:
            when = datetime.fromisoformat(s)
        except ValueError:
            when = _now()
    dt = when if isinstance(when, datetime) else _now()
    dt = dt.astimezone(timezone.utc)
    month = _MONTHS[dt.month - 1]
    stamp = f"{month} {dt.day}, {dt.year}"
    body = (text or "").strip() or "No copy."
    place = (jurisdiction or "UNSPECIFIED").strip().upper()
    src = (source or "Gate").strip()
    return f"{place} ({src}) — {stamp} — {body}"


def _vertical_of_row(row: dict[str, Any]) -> str:
    hop = row.get("hop") if isinstance(row.get("hop"), dict) else {}
    return str(hop.get("vertical") or hop.get("line") or hop.get("domain") or hop.get("rail") or "").lower()


def _reason_of_row(row: dict[str, Any]) -> str:
    hop = row.get("hop") if isinstance(row.get("hop"), dict) else {}
    return str(hop.get("reason") or hop.get("epoch_reason") or row.get("reason") or "").strip()


def _jurisdiction_of_row(row: dict[str, Any]) -> tuple[str, str]:
    hop = row.get("hop") if isinstance(row.get("hop"), dict) else {}
    state = str(hop.get("state") or hop.get("jurisdiction") or "").strip()
    if len(state) == 2:
        return (state.upper(), "Gate")
    if state:
        return (state.upper(), "Gate")
    return ("NEW YORK", "Gate")


def _docket_index(dockets: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for item in WATCHES:
        out[item["id"]] = dict(item)
    for d in dockets:
        if not isinstance(d, dict) or not d.get("id"):
            continue
        rec = dict(d)
        rec.setdefault("vertical", DOCKET_VERTICAL.get(str(d["id"]), "unlabeled"))
        out[str(d["id"])] = rec
    return out


def context_for_rule(rule: str | None, dockets: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Item 88 — actual docket/bulletin tied to the triggering rule, or none."""
    key = (rule or "").strip()
    docket_id = RULE_DOCKET.get(key)
    if not docket_id:
        return None
    idx = _docket_index(dockets)
    rec = idx.get(docket_id)
    if not rec:
        return {
            "docket_id": docket_id,
            "present": False,
            "plain": "Mapped docket is not in this mouth's named list.",
        }
    return {
        "docket_id": rec.get("id"),
        "label": rec.get("label"),
        "url": rec.get("url"),
        "status": rec.get("status"),
        "path": rec.get("path"),
        "vertical": rec.get("vertical") or DOCKET_VERTICAL.get(str(rec.get("id")), "unlabeled"),
        "present": True,
        "scraped": False,
        "plain": rec.get("plain") or rec.get("label"),
    }


def _fingerprint(rec: dict[str, Any]) -> str:
    body = {
        "id": rec.get("id"),
        "status": rec.get("status"),
        "deadline": rec.get("deadline"),
        "plain": rec.get("plain"),
        "label": rec.get("label"),
        "url": rec.get("url"),
    }
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _load_snapshot() -> dict[str, str]:
    path = _watch_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    rows = data.get("fingerprints") if isinstance(data, dict) else None
    if not isinstance(rows, dict):
        return {}
    return {str(k): str(v) for k, v in rows.items()}


def _save_snapshot(fps: dict[str, str]) -> None:
    path = _watch_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"spec": MONITOR_SPEC, "fingerprints": fps}, indent=2),
        encoding="utf-8",
    )


def monitor(
    dockets: list[dict[str, Any]],
    *,
    persist: bool = True,
    previous: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Item 89 — flag when a watched docket's named record changes, and which vertical it touches.

    Compares the in-repo docket fields. Does not scrape the remote URL.
    """
    idx = _docket_index(dockets)
    current = {did: _fingerprint(rec) for did, rec in idx.items()}
    prior = previous if previous is not None else _load_snapshot()
    flags = []
    for did, rec in idx.items():
        old = prior.get(did)
        new = current[did]
        if old is None:
            kind = "baseline"
        elif old != new:
            kind = "changed"
        else:
            continue
        if kind == "changed" or (kind == "baseline" and not prior):
            flags.append(
                {
                    "id": did,
                    "kind": kind if prior else "baseline",
                    "vertical": rec.get("vertical") or DOCKET_VERTICAL.get(did, "unlabeled"),
                    "label": rec.get("label"),
                    "scraped": False,
                }
            )
    if persist:
        _save_snapshot(current)
    changed = [f for f in flags if f["kind"] == "changed"]
    return {
        "spec": MONITOR_SPEC,
        "scraped": False,
        "as_of": _iso(_now()),
        "watched": len(current),
        "changed": changed,
        "flags": flags,
        "plain": (
            "Flags when a named docket record in this mouth changes. "
            "Not a live scrape of the remote bulletin."
        ),
    }


def feed(
    bind_rows: list[dict[str, Any]],
    dockets: list[dict[str, Any]],
    *,
    vertical: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Item 87 — mix BLOCK/HOLD/ALLOW with named external dockets, filter by vertical."""
    now = _now(now)
    want = (vertical or "").strip().lower() or None
    rows: list[dict[str, Any]] = []

    for row in bind_rows:
        decision = str(row.get("decision") or "").upper()
        if decision not in ("BLOCK", "HOLD", "ALLOW", "HALT"):
            continue
        vert = _vertical_of_row(row) or "unlabeled"
        if want and want not in vert and vert != want:
            continue
        reason = _reason_of_row(row)
        place, source = _jurisdiction_of_row(row)
        when = row.get("created_at") or _iso(now)
        ctx = context_for_rule(reason, dockets)
        copy = reason or f"{decision} on this mouth."
        rows.append(
            {
                "kind": "internal",
                "event_id": row.get("id"),
                "decision": decision,
                "vertical": vert,
                "at": when,
                "reason": reason or None,
                "reason_text": dateline(jurisdiction=place, source=source, when=when, text=copy),
                "regulatory_context": ctx,
                "scraped": False,
            }
        )

    idx = _docket_index(dockets)
    for rec in idx.values():
        vert = str(rec.get("vertical") or DOCKET_VERTICAL.get(str(rec.get("id")), "unlabeled"))
        if want and want not in vert:
            continue
        did = str(rec.get("id"))
        place, source = DOCKET_DATELINE.get(did, ("UNSPECIFIED", "docket"))
        when = rec.get("deadline") or rec.get("session") or _iso(now)
        text = rec.get("plain") or rec.get("label") or did
        rows.append(
            {
                "kind": "external",
                "event_id": did,
                "decision": None,
                "vertical": vert,
                "at": when if isinstance(when, str) else _iso(now),
                "reason": None,
                "reason_text": dateline(
                    jurisdiction=place,
                    source=source,
                    when=now,
                    text=str(text),
                ),
                "regulatory_context": {
                    "docket_id": did,
                    "label": rec.get("label"),
                    "url": rec.get("url"),
                    "status": rec.get("status"),
                    "path": rec.get("path"),
                    "vertical": vert,
                    "present": True,
                    "scraped": False,
                    "plain": rec.get("plain") or rec.get("label"),
                },
                "scraped": False,
            }
        )

    rows.sort(key=lambda r: str(r.get("at") or ""), reverse=True)
    return {
        "spec": SPEC,
        "scraped": False,
        "reuters": False,
        "bloomberg": False,
        "vertical": want,
        "plain": (
            "Internal BLOCK/HOLD/ALLOW mixed with named dockets this mouth already cites. "
            "Not a Reuters or Bloomberg wire."
        ),
        "rows": rows[:100],
    }


def drilldown(
    event_id: str,
    bind_rows: list[dict[str, Any]],
    dockets: list[dict[str, Any]],
) -> dict[str, Any] | None:
    event_id = (event_id or "").strip()
    if not event_id:
        return None
    payload = feed(bind_rows, dockets)
    hit = next((r for r in payload["rows"] if str(r.get("event_id")) == event_id), None)
    if not hit:
        return None
    return {
        "spec": SPEC,
        "scraped": False,
        "row": hit,
        "regulatory_context": hit.get("regulatory_context"),
        "plain": "Docket tied to the triggering rule, or none if no named map exists.",
    }
