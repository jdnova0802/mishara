"""Item 96 — ATC readback/hearback before the bind demo gates."""
from __future__ import annotations

import hashlib
from typing import Any

try:
    from gate import bind_room_demo as demo
except ImportError:
    import bind_room_demo as demo

try:
    from gate import sanitize as sanitize_mod
except ImportError:
    import sanitize as sanitize_mod

SPEC = "gate-atc-hearback-v1"


def _token(domain: str, paraphrase: str) -> str:
    return hashlib.sha256(f"{domain}|{paraphrase}".encode("utf-8")).hexdigest()[:24]


def hearback(*, domain: str | None, company: str | None) -> tuple[int, dict[str, Any]]:
    resolved = demo.normalize_domain(domain)
    if resolved is None:
        return 400, {
            "ok": False,
            "spec": SPEC,
            "error": "unknown_domain",
            "message": "Cannot paraphrase an unknown vertical. Unknown values do not become Insurance.",
        }
    spec = demo.DOMAINS[resolved]
    company_name = sanitize_mod.strip_agent((company or "").strip() or "Demo operator", limit=120)
    paraphrase = sanitize_mod.strip_agent(
        (
            f"I heard {spec['label']} for {company_name}. "
            f"Chokepoint: {spec['chokepoint']}. "
            f"Proposed bind: {spec['bind_reason']}"
        )
    )
    token = _token(resolved, paraphrase)
    return 200, {
        "ok": True,
        "spec": SPEC,
        "confirmed": False,
        "gated": False,
        "domain": resolved,
        "company": company_name,
        "detected": {
            "label": spec["label"],
            "chokepoint": spec["chokepoint"],
            "bind_reason": sanitize_mod.strip_agent(spec["bind_reason"]),
        },
        "paraphrase": paraphrase,
        "confirm_token": token,
        "plain": "Say back whether this is the pattern. Gate does not fire until you confirm.",
    }


def confirm(
    *,
    domain: str | None,
    company: str | None,
    confirm_token: str | None,
    public_url: str,
) -> tuple[int, dict[str, Any]]:
    status, hb = hearback(domain=domain, company=company)
    if status != 200:
        return status, hb
    got = (confirm_token or "").strip()
    if got != hb["confirm_token"]:
        return 409, {
            "ok": False,
            "spec": SPEC,
            "error": "hearback_mismatch",
            "plain": "That is not the paraphrase Gate just read back. No gate.",
            "gated": False,
            "confirmed": False,
        }
    run_status, body = demo.run(domain=hb["domain"], company=hb["company"], public_url=public_url)
    if run_status != 200:
        return run_status, body
    body["hearback"] = {**hb, "confirmed": True, "gated": True}
    body["gated"] = True
    body["hearback_confirmed"] = True
    return run_status, body
