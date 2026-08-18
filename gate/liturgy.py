"""Renaissance layer — three doors only. Not a museum.

Stranger Mass: proof as congregation (one DEAD receipt / week).
Refusal SKU: paid birth certificate of a non-entity.
Weld tattoo: one origin, worker burned in, bypass > compliance.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone

CANONICAL_RELICS = [
    {
        "fuse_id": "fuse_velaru_drill",
        "job_id": "pc:stranger-mass",
        "decision": "HALT",
        "state": "DEAD",
        "verify_url": "https://velaru.xyz/verify",
        "protected": "the bind that did not happen on a boring Tuesday",
        "source": "canonical",
    },
]


def mass_week_key(now: datetime | None = None) -> str:
    t = now or datetime.now(timezone.utc)
    iso = t.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def next_sunday_utc(now: datetime | None = None) -> str:
    t = now or datetime.now(timezone.utc)
    days = (6 - t.weekday()) % 7
    if days == 0 and t.weekday() != 6:
        days = 7
    if t.weekday() == 6:
        days = 0
    nxt = t.replace(hour=0, minute=0, second=0, microsecond=0)
    if days:
        from datetime import timedelta

        nxt = nxt + timedelta(days=days)
    return nxt.date().isoformat()


def relic_from_event(event: dict) -> dict | None:
    if not event.get("verify_url"):
        return None
    if event.get("decision") not in ("HALT", "BLOCK"):
        return None
    hop = event.get("hop") if isinstance(event.get("hop"), dict) else {}
    job = (event.get("job_id") or "").strip() or "unknown"
    return {
        "id": event.get("id"),
        "fuse_id": event.get("fuse_id"),
        "job_id": job,
        "decision": event.get("decision"),
        "state": hop.get("state") or "DEAD",
        "verify_url": event.get("verify_url"),
        "protected": f"job {job} — the spend that halted",
        "created_at": event.get("created_at"),
        "source": "bind_event",
    }


def relic_vault(events: list[dict], limit: int = 24) -> list[dict]:
    out: list[dict] = []
    seen: set[str] = set()
    for ev in events:
        relic = relic_from_event(ev)
        if not relic:
            continue
        key = relic.get("verify_url") or ""
        if key in seen:
            continue
        seen.add(key)
        out.append(relic)
        if len(out) >= limit:
            break
    if not out:
        out = [dict(r) for r in CANONICAL_RELICS]
    return out


def pick_mass_relic(relics: list[dict], week_key: str) -> dict:
    pool = relics or [dict(r) for r in CANONICAL_RELICS]
    idx = int(hashlib.sha256(week_key.encode()).hexdigest(), 16) % len(pool)
    chosen = dict(pool[idx])
    chosen["week"] = week_key
    return chosen


def stranger_mass(public_url: str, events: list[dict] | None = None) -> dict:
    now = datetime.now(timezone.utc)
    week = mass_week_key(now)
    vault = relic_vault(events or [], limit=48)
    relic = pick_mass_relic(vault, week)
    verify = relic.get("verify_url") or "https://velaru.xyz/verify"
    return {
        "spec": "gate-stranger-mass-v1",
        "rule": "Every Sunday, one URL. Anyone verifies one DEAD receipt together. No login. No brand.",
        "miracle": "nothing happened — and strangers can confirm it",
        "week": week,
        "sunday_utc": now.weekday() == 6,
        "next_sunday_utc": next_sunday_utc(now),
        "relic": relic,
        "verify_url": verify,
        "verify_engine": "https://velaru.xyz/verify",
        "instruction": "Open the verify link. If DEAD holds, you were in the congregation of the non-event.",
        "vault": f"{public_url}/.well-known/relics.json",
        "page": f"{public_url}/mass",
        "not_marketing": True,
    }


def relics_manifest(public_url: str, events: list[dict] | None = None) -> dict:
    vault = relic_vault(events or [])
    return {
        "spec": "gate-relic-vault-v1",
        "wunderkammer": "unicorn absences — worlds that did not get spent",
        "count": len(vault),
        "relics": vault,
        "page": f"{public_url}/mass",
    }


def refusal_pack(public_url: str, contact_email: str, price_label: str) -> dict:
    return {
        "spec": "gate-refusal-sku-v1",
        "product": "birth certificate of a non-entity",
        "price": price_label,
        "deliverable": (
            "Signed refusal: we will not build this agent. No hop. No fuse. No particular stood up. "
            "Receipt for what was never born."
        ),
        "includes": [
            "Signed PDF birth certificate of non-entity (your agent name + date)",
            "Public listing optional — illegitimate by design",
            "No Gate key, no fuse_id, no weld",
        ],
        "refuse_to_build": [
            "inventory / bias-audit SaaS dressed as safety",
            "appetite extraction on bind path",
            "PII / ACORD on PAS paths",
            "another dashboard that philosophizes instead of halting spend",
        ],
        "cta": {
            "book": f"{public_url}/refusal",
            "certificate_schema": f"{public_url}/refusal/certificate.schema.json",
            "contact": contact_email,
        },
        "honest": "Most expensive SKU because the deliverable is absence.",
    }


def refusal_certificate_schema() -> dict:
    return {
        "spec": "gate-refusal-certificate-v1",
        "entity": {
            "agent_name": "string — the agent we refused to stand up",
            "requested_by": "string — company or title",
            "refused_at": "ISO-8601 UTC",
            "signed_by": "Nisaba LLC — one name on one date",
        },
        "proof_of_absence": {
            "fuse_id": None,
            "hop": False,
            "weld": False,
            "verify_url": None,
            "particular_stood_up": False,
        },
        "note": "Illegitimate. Unphotographable. The product is the hole.",
    }


def weld_tattoo_manifest(public_url: str) -> dict:
    return {
        "spec": "gate-weld-tattoo-v1",
        "name": "stigmata on their stack",
        "rule": "One carrier. One production origin. Bypass more expensive than compliance.",
        "worker": f"{public_url}/listings/cloudflare-worker-bind.js",
        "wrangler": f"{public_url}/listings/wrangler-bind.toml",
        "gosu_ui_bind": f"{public_url}/listings/guidewire-gosu-prebind.gs",
        "gosu_renewal": f"{public_url}/listings/guidewire-renewal-prebind.gs",
        "pre_bind": f"POST {public_url}/v1/pas/policycenter/pre-bind",
        "capture": f"{public_url}/capture",
        "integrate": False,
        "brand": "The exclusive door is burned into the only origin that can bind.",
        "their_production": False,
        "page": f"{public_url}/tattoo",
    }
