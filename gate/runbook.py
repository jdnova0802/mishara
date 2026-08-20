"""48hr reference weld runbook — third party can replay without revenue."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-runbook-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def steps(public_url: str) -> list[dict[str, Any]]:
    base = (public_url or "").rstrip("/")
    return [
        {
            "hour": "0–4",
            "title": "Discover public face",
            "actions": [
                f"GET {base}/.well-known/public-face.json",
                f"GET {base}/.well-known/gate.json → public_face + catalog",
                f"GET {base}/.well-known/production-skin.json",
            ],
            "done_when": "Three pillars mapped to manifests",
        },
        {
            "hour": "4–8",
            "title": "Sandbox bind-check (no API key)",
            "actions": [
                f"POST {base}/sandbox/pas/bind-check",
                'Body: {"job_id":"SANDBOX-1","fuse_id":"fuse_velaru_drill"}',
                "Open verify_url from response",
            ],
            "done_when": "Stranger verify opens without login",
        },
        {
            "hour": "8–16",
            "title": "Fail-closed drill",
            "actions": [
                f"POST {base}/demo/pas/bind-check with DEAD fuse",
                f"GET {base}/.well-known/proof-suite.json → all_pass true",
            ],
            "done_when": "BLOCK/HALT + verify_url; proof suite green",
        },
        {
            "hour": "16–24",
            "title": "CHARGE costliness",
            "actions": [
                f"GET {base}/.well-known/costliness.json",
                f"GET {base}/.well-known/license-fuse.json",
                "Run closure test: uw_approve_without_charge → not in network",
            ],
            "done_when": "CHARGE-only resurrection documented + proven",
        },
        {
            "hour": "24–32",
            "title": "Operator weld (dev or Stripe)",
            "actions": [
                f"POST {base}/operator/checkout (write=bind_only, include_floor=1)",
                "Idempotency-Key header for immovability",
                f"GET {base}/install/success?session_id=…",
            ],
            "done_when": "Weld + management checkout complete",
        },
        {
            "hour": "32–40",
            "title": "Production skin flip",
            "actions": [
                "Set GATE_PRODUCTION_WELDED=1 on deploy OR POST /ops/dogfood-weld",
                f"GET {base}/.well-known/scorecard.json → deployability ≥ 9",
            ],
            "done_when": "their_production true on production-skin manifest",
        },
        {
            "hour": "40–48",
            "title": "Post-trade cite path",
            "actions": [
                f"GET {base}/.well-known/distribution.json",
                f"GET {base}/.well-known/settlement.json",
                f"GET {base}/.well-known/pfmi-one-pager.json",
            ],
            "done_when": "FMI reader can place Gate vs finality III",
        },
    ]


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "48hr reference weld runbook",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "claim": "Third party replays weld → verify → CHARGE → distribution cite in 48hr",
        "steps": steps(base),
        "script": f"{base}/static/runbook-verify.sh",
        "officer_pack": f"{base}/bind-room/officer-pack.json",
        "page": f"{base}/runbook",
    }
