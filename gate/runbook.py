"""48hr production runbook — proof → weld path without theater."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-runbook-v1"
INVENTOR = "Nisaba LLC / Gate"

STEPS = (
    {
        "hour": "0–2",
        "title": "Run proof suite",
        "do": "GET /.well-known/proof-suite.json — require all_pass",
        "path": "/.well-known/proof-suite.json",
    },
    {
        "hour": "2–4",
        "title": "Live hop + stranger verify",
        "do": "POST /demo/hop on drill fuse → open verify_url",
        "path": "/",
    },
    {
        "hour": "4–8",
        "title": "Scanner + spend protocol",
        "do": "Wire scanner face; confirm PII reject on PAS body",
        "path": "/scanner",
    },
    {
        "hour": "8–16",
        "title": "License fuse parent",
        "do": "Create LIVE parent via CHARGE; prove DEAD kills children",
        "path": "/docs",
    },
    {
        "hour": "16–32",
        "title": "Dogfood weld record",
        "do": "POST /dogfood with write_path + operator — first-party only",
        "path": "/dogfood",
    },
    {
        "hour": "32–48",
        "title": "Operator checkout / their write",
        "do": "Weld one licensed payout or bind-only write on their system",
        "path": "/operator",
    },
    {
        "hour": "48",
        "title": "Record their_production",
        "do": "POST /production-weld with confirm — only after their write cleared",
        "path": "/production-weld",
    },
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def steps(public_url: str = "") -> list[dict[str, Any]]:
    base = (public_url or "").rstrip("/")
    out: list[dict[str, Any]] = []
    for s in STEPS:
        out.append({**s, "href": f"{base}{s['path']}" if base else s["path"]})
    return out


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    try:
        from gate import proof_suite as proof_mod
        from gate import production_skin as skin_mod
    except ImportError:
        import proof_suite as proof_mod  # type: ignore[no-redef]
        import production_skin as skin_mod  # type: ignore[no-redef]

    proof = proof_mod.manifest(base)
    skin = skin_mod.manifest(base)
    return {
        "spec": SPEC,
        "name": "48hr production runbook",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "thesis": (
            "Improve proof first. Dogfood second. their_production only when "
            "someone else's irreversible write is welded."
        ),
        "steps": steps(base),
        "proof": {
            "all_pass": proof.get("all_pass"),
            "pass_count": proof.get("pass_count"),
            "total": proof.get("total"),
            "readiness": proof.get("readiness"),
        },
        "skin": {
            "their_production": skin.get("their_production"),
            "dogfood_weld": skin.get("dogfood_weld"),
            "checklist_pass": skin.get("checklist_pass"),
            "checklist_total": skin.get("checklist_total"),
        },
        "page": f"{base}/runbook",
        "their_production": skin.get("their_production"),
    }
