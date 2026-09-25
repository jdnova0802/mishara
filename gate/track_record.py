"""Public track record — incidents, cadence, uptime, evidence-watch protocol.

Closed in code is not a track record. This module is the buyer-facing log.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

try:
    from gate import db
except ImportError:
    import db

try:
    from gate import evidence_log as evidence_log_mod
except ImportError:
    import evidence_log as evidence_log_mod

SPEC = "gate-track-record-v1"
CONTACT = "hello@velaru.xyz"

INCIDENTS: tuple[dict[str, Any], ...] = (
    {
        "id": "2026-09-24-x402-header-paid",
        "opened_at": "2026-09-24T20:00:00+00:00",
        "closed_at": "2026-09-24T23:18:01+00:00",
        "severity": "high",
        "status": "closed",
        "title": "x402 treated a payment header as paid",
        "found_by": "SCVD weekly crawl + internal red-team",
        "found_how": (
            "A crawler (and then a red-team pass) posted Payment-Signature: not-a-real-payment "
            "to POST /v1/prefinality/evaluate. Presence of the header unlocked the paid route."
        ),
        "broke": (
            "Paid x402 evaluate could return 200 as if facilitator verify had succeeded. "
            "A forged header was enough."
        ),
        "fix": (
            "payment_verified() fail-closed. Header presence is never paid. Until facilitator "
            "verify is wired, every paid x402 call stays HTTP 402 — including non-empty X-Payment. "
            "Dev-only escape requires GATE_X402_ACCEPT_UNVERIFIED=1 AND GATE_DEV_MODE=1."
        ),
        "fix_pr": "https://github.com/jdnova0802/mishara/pull/103",
        "verify_live": (
            "curl POST /v1/prefinality/evaluate with Payment-Signature: not-a-real-payment "
            "must return HTTP 402."
        ),
        "still_open": (
            "CDP facilitator verify+settle is wired in payment_verified(); unlock still needs "
            "CDP_API_KEY_ID/SECRET on Render and one real $0.002 USDC buyer settle on "
            "POST /v1/prefinality/evaluate. Forged headers must keep returning 402."
        ),
    },
    {
        "id": "2026-09-24-spend-map-race",
        "opened_at": "2026-09-24T20:00:00+00:00",
        "closed_at": "2026-09-24T23:18:01+00:00",
        "severity": "high",
        "status": "closed",
        "title": "Two tickets could spend the same job_id",
        "found_by": "internal red-team",
        "found_how": (
            "Concurrent redeem of two bind tickets for one job_id could both pass before "
            "consumed_at was visible to the other writer."
        ),
        "broke": "Spend-map invariant 'one job_id, one spend' was not serialized.",
        "fix": (
            "consume_bind_ticket opens BEGIN IMMEDIATE, then rejects a second consumed ticket "
            "for the same job_id with reason job_already_spent."
        ),
        "fix_pr": "https://github.com/jdnova0802/mishara/pull/103",
        "verify_live": "Second consume of the same job_id returns job_already_spent.",
        "still_open": "Automated sqlite backup of /var/data/gate.db is still not shipped.",
    },
)

RED_TEAM = {
    "spec": "gate-red-team-cadence-v1",
    "cadence": "monthly",
    "day_of_month": 24,
    "next": "2026-10-24",
    "public_results": True,
    "contact": CONTACT,
    "passes": (
        {
            "id": "2026-09-24",
            "date": "2026-09-24",
            "status": "published",
            "scope": (
                "x402 paid-route unlock, spend-map race, mouth fail-closed cases "
                "(FedNow / Nacha / CL7), buyer-surface demo smell."
            ),
            "findings": [
                "x402 header-as-paid — closed in PR #103, live-verified 402",
                "spend-map race — closed in PR #103 (BEGIN IMMEDIATE + job_already_spent)",
            ],
            "parked": [
                "Visa agentic chargebacks mouth — no agent-specific dispute spec in Visa §11",
            ],
            "results": "/record",
        },
    ),
}

SHARED_FAILURE = {
    "question": "What's the single failure mode that would take down every mouth at once?",
    "answer": (
        "One Flask process + one sqlite file on one Render disk + one deploy of gate-api. "
        "Mouths are routes on the same app, not isolated services. If the sqlite host, "
        "the Render service, DNS/TLS for gate.velaru.xyz, or a bad deploy of app.py dies, "
        "all mouths 404/5xx together. The receipt signing key is the other shared class: "
        "compromise does not take pages down; it makes every new receipt untrustworthy."
    ),
    "category_tested": False,
    "category_tested_note": (
        "Per-mouth cases were red-teamed. Shared-host / shared-key / shared-pipeline "
        "failure has not been chaos-tested as a category. No replica, no multi-region."
    ),
}

FIRST_BOTTLENECK = {
    "question": "If a real customer signed tomorrow, what would actually break first?",
    "answer": (
        "Sqlite single-writer under concurrent redeem on one Render starter instance, "
        "with no automated backup of /var/data/gate.db. Bind Room redeem is the money path; "
        "a disk wipe or lock storm is the first honest break. Paid x402 now has a facilitator "
        "path but has not taken real USDC volume yet. One operator, no on-call rotation."
    ),
}

THIRTY_SECOND_TRUST = {
    "question": "What's the cheapest thing that would make a skeptical buyer trust this in 30 seconds, that doesn't exist yet?",
    "answer": (
        "This page, filled in: named incidents with found/fixed/verify curls, plus an "
        "independent party caching evidence-head.json. Not a badge, not a fake customer. "
        "The missing 30-second signal was a public log a stranger can curl. Shipping it now. "
        "Second-party watch is invited, not claimed."
    ),
    "now_exists": [
        "/record",
        "/.well-known/incidents.json",
        "/.well-known/evidence-head.json",
        "/.well-known/evidence-consistency.json",
    ],
    "still_missing": [
        "named independent watcher of the evidence head",
        "automated sqlite backup",
        "reference customer",
    ],
}

SCVD_INVITE = {
    "to": "SCVD",
    "from": CONTACT,
    "ask": (
        "Gate invites SCVD to treat https://gate.velaru.xyz as a standing weekly crawl "
        "target. Last week's header-as-paid catch was real. We want it repeated, unpaid, "
        "and public — not a one-time luck."
    ),
    "pasteable": (
        "Subject: Standing weekly crawl target — gate.velaru.xyz\n\n"
        "You caught Gate treating an x402 payment header as paid. That is now fail-closed "
        "HTTP 402 (PR #103, live-verified). Thank you.\n\n"
        "Ask: keep Gate as a standing invited target of the weekly crawl, publicly. "
        "We will post what you find on https://gate.velaru.xyz/record.\n\n"
        "Contact: hello@velaru.xyz\n"
        "Health: https://gate.velaru.xyz/health\n"
        "Evidence head: https://gate.velaru.xyz/.well-known/evidence-head.json\n"
    ),
}

WATCH_PROTOCOL = {
    "spec": "gate-evidence-watch-v1",
    "what": "Tree only grows. Root at size N must match merkle(leaves[:N]).",
    "first_party": {
        "who": "this repo's GitHub Action gate-watch.yml",
        "independent": False,
        "cadence": "every 15 minutes",
    },
    "independent_watchers": [],
    "independent_watchers_note": (
        "Zero independent watchers recorded. A second party running the watch script "
        "is what turns samples into checkable history. Invite: hello@velaru.xyz."
    ),
    "how": [
        "GET /.well-known/evidence-head.json — cache tree_size + root_hash",
        "Later GET /.well-known/evidence-consistency.json?old_size={cached_size}&old_root={cached_root}",
        "FAIL if tree_size shrank",
        "FAIL if size equal and root changed",
        "FAIL if consistency old_root does not match cache",
    ],
    "script": "/watch/evidence-head.py",
    "head": "/.well-known/evidence-head.json",
    "leaves": "/.well-known/evidence-leaves.json",
    "consistency": "/.well-known/evidence-consistency.json",
}


def incident_by_id(incident_id: str) -> dict | None:
    wanted = (incident_id or "").strip()
    for row in INCIDENTS:
        if row["id"] == wanted:
            return dict(row)
    return None


def maybe_sample_pulse(*, health_ok: bool, velaru_ok: bool, force: bool = False) -> dict | None:
    tree_size = None
    root_hash = None
    try:
        rows = db.list_bind_events_chronological()
        leaves = evidence_log_mod.log_from_rows(rows)
        tree_size = len(leaves)
        root_hash = evidence_log_mod.merkle_root(leaves)
    except Exception:
        pass
    try:
        return db.record_pulse_sample(
            health_ok=health_ok,
            velaru_ok=velaru_ok,
            tree_size=tree_size,
            root_hash=root_hash,
            force=force,
        )
    except Exception:
        return None


def check_cached_head(current: dict, cached: dict | None) -> dict:
    """Pure check a watcher can run without Gate internals."""
    size = int(current.get("tree_size") or 0)
    root = current.get("root_hash") or ""
    if not cached:
        return {
            "ok": True,
            "event": "first_sample",
            "tree_size": size,
            "root_hash": root,
        }
    old_size = int(cached.get("tree_size") or 0)
    old_root = cached.get("root_hash") or ""
    if size < old_size:
        return {
            "ok": False,
            "event": "tree_shrunk",
            "old_size": old_size,
            "new_size": size,
        }
    if size == old_size and root != old_root:
        return {
            "ok": False,
            "event": "root_rewritten_same_size",
            "tree_size": size,
            "old_root": old_root,
            "new_root": root,
        }
    if size == old_size:
        return {"ok": True, "event": "unchanged", "tree_size": size, "root_hash": root}
    return {
        "ok": True,
        "event": "grew",
        "old_size": old_size,
        "new_size": size,
        "old_root": old_root,
        "new_root": root,
        "next": "GET evidence-consistency.json?old_size={old}&old_root={old_root}",
    }


def manifest(public_url: str) -> dict:
    base = public_url.rstrip("/")
    uptime = db.pulse_summary()
    last = db.last_pulse_sample()
    return {
        "spec": SPEC,
        "name": "Gate track record",
        "not": [
            "Cloudflare/AWS/Stripe status clone with fake 90-day 99.9%",
            "closed-in-code as proof",
            "independent watcher already on payroll",
        ],
        "contact": CONTACT,
        "page": f"{base}/record",
        "incidents": [dict(x) for x in INCIDENTS],
        "incidents_json": f"{base}/.well-known/incidents.json",
        "red_team": dict(RED_TEAM),
        "red_team_json": f"{base}/.well-known/red-team.json",
        "uptime": uptime,
        "uptime_json": f"{base}/.well-known/uptime.json",
        "last_pulse": last,
        "shared_failure": dict(SHARED_FAILURE),
        "first_bottleneck": dict(FIRST_BOTTLENECK),
        "thirty_second_trust": dict(THIRTY_SECOND_TRUST),
        "scvd_invite": dict(SCVD_INVITE),
        "evidence_watch": {
            **dict(WATCH_PROTOCOL),
            "head": f"{base}/.well-known/evidence-head.json",
            "leaves": f"{base}/.well-known/evidence-leaves.json",
            "consistency": f"{base}/.well-known/evidence-consistency.json",
            "script": f"{base}/watch/evidence-head.py",
            "watch_json": f"{base}/.well-known/evidence-watch.json",
        },
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }
