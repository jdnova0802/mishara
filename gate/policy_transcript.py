"""R7 (policy, not zkML) — transcript of Gate rules on public inputs.

A stranger re-runs preview() and checks the policy hash. This is not a
SNARK and not EZKL. ATLAS tagging stays unproven.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

try:
    from gate import gate_rules as gate_rules_mod
except ImportError:
    import gate_rules as gate_rules_mod

SPEC = "gate-policy-transcript-v1"


def _iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def policy_hash(rules: list[dict[str, Any]] | None = None) -> str:
    rows = rules if rules is not None else gate_rules_mod.load_rules()
    blob = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode()).hexdigest()


def evaluate(*, public_inputs: dict[str, Any], rules: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    body = public_inputs if isinstance(public_inputs, dict) else {}
    used = rules if rules is not None else gate_rules_mod.load_rules()
    preview = gate_rules_mod.preview(body, used)
    rec = {
        "spec": SPEC,
        "ok": True,
        "zk_circuit": False,
        "ezkl": False,
        "policy_hash": policy_hash(used),
        "public_inputs": body,
        "verdict": preview["action"],
        "hits": preview.get("hits") or [],
        "rule_count": preview.get("rule_count") or 0,
        "evaluated_at": _iso(),
        "plain": "Re-run preview on these inputs and this policy_hash. A neural net did not produce this.",
    }
    rec["transcript_sha256"] = hashlib.sha256(
        json.dumps(
            {"policy_hash": rec["policy_hash"], "verdict": rec["verdict"], "inputs": body},
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()
    return rec


def verify(transcript: dict[str, Any], *, rules: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    body = transcript.get("public_inputs") if isinstance(transcript.get("public_inputs"), dict) else {}
    fresh = evaluate(public_inputs=body, rules=rules)
    match = (
        fresh["policy_hash"] == transcript.get("policy_hash")
        and fresh["verdict"] == transcript.get("verdict")
        and fresh["transcript_sha256"] == transcript.get("transcript_sha256")
    )
    return {
        "spec": SPEC,
        "ok": match,
        "match": match,
        "fresh_verdict": fresh["verdict"],
        "plain": "Transcript matches a re-run." if match else "Transcript does not match the published rules.",
    }
