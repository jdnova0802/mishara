"""Outbound templates — no invention names in paste copy."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-outbound-templates-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def templates(public_url: str) -> dict[str, dict[str, str]]:
    base = (public_url or "").rstrip("/")
    return {
        "operators": {
            "subject": "One door on irreversible spend — register, not SaaS",
            "body": (
                f"Irreversible spend does not complete unless this layer says yes.\n\n"
                f"One welded write (bind-only or payout). Fail closed on DEAD. "
                f"Stranger verify without login. Register: 10 bps on cleared flow.\n\n"
                f"Door: {base}/for/operators\n"
                f"Register: {base}/register\n"
                f"Proof: POST {base}/demo/pas/bind-check → open verify_url"
            ),
        },
        "charge": {
            "subject": "DEAD→LIVE only via CHARGE — not admin toggle",
            "body": (
                f"Regime change on our engine is CHARGE-only. "
                f"UW approve without CHARGE does not resurrect.\n\n"
                f"Costliness spec: {base}/.well-known/costliness.json\n"
                f"Public proof: {base}/.well-known/proof-suite.json\n"
                f"Door: {base}/for/charge"
            ),
        },
        "post_trade": {
            "subject": "Clear the instruction before it becomes your exception queue",
            "body": (
                f"We do not replace your net. We clear the irreversible instruction "
                f"before it becomes your exception queue.\n\n"
                f"Distribution stack: {base}/.well-known/distribution.json\n"
                f"PFMI placement: {base}/.well-known/pfmi-one-pager.json\n"
                f"Door: {base}/for/post-trade"
            ),
        },
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Outbound templates",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "rule": "No invention catalog names in outbound paste — door, CHARGE, distribution only.",
        "templates": templates(base),
        "focus_hub": f"{base}/focus",
    }
