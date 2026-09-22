"""Threat model for Gate clearance — assets, adversaries, abuse cases.

Institutional diligence artifact. Paired with chaos_fail_closed tests that
prove required denies. Not a marketing page.
"""

from __future__ import annotations

SPEC = "gate-threat-model-v1"

ASSETS = (
    {
        "id": "clearance_decision",
        "name": "Allow/deny on an irreversible write",
        "hurt_if_lost": "Wrong LIVE lets money/coverage move; wrong silence is less bad than wrong LIVE",
    },
    {
        "id": "receipt_chain",
        "name": "Signed, hash-chained bind receipts + Merkle/seal",
        "hurt_if_lost": "History rewrite hides a bad allow or erases a halt",
    },
    {
        "id": "signing_custody",
        "name": "Ed25519 receipt signing material (env/file/KMS)",
        "hurt_if_lost": "Attacker mints trustworthy-looking false evidence",
    },
    {
        "id": "staple",
        "name": "Published verifying public key / fingerprint",
        "hurt_if_lost": "Strangers verify against the wrong key",
    },
    {
        "id": "charge_path",
        "name": "DEAD→LIVE only via Velaru CHARGE",
        "hurt_if_lost": "Admin or app resurrect without authority",
    },
)

ADVERSARIES = (
    {
        "id": "insider_ops",
        "name": "Operator with Gate host / DB / env access",
        "goal": "Rewrite receipts, mint LIVE, or hide a halt after the fact",
    },
    {
        "id": "network_attacker",
        "name": "On-path attacker between Gate and Velaru / client",
        "goal": "Timeout theater, forged upstream, drop denials",
    },
    {
        "id": "forger",
        "name": "Stranger with no keys",
        "goal": "Forge a signature or staple that passes cold verify",
    },
    {
        "id": "confused_deputy",
        "name": "Welded PAS/worker that treats absence as allow",
        "goal": "Bind proceeds when Gate is down or UNREACHABLE",
    },
)

ABUSE_CASES = (
    {
        "id": "forge_signature",
        "adversary": "forger",
        "asset": "receipt_chain",
        "attack": "Present a receipt_hash with an invented signature",
        "required_deny": "verify_receipt_signature → false",
        "chaos_id": "forge_signature",
    },
    {
        "id": "tamper_hash",
        "adversary": "forger",
        "asset": "receipt_chain",
        "attack": "Keep signature, flip a canonical field / hash",
        "required_deny": "signature verify over claimed hash fails; or hash≠canonical",
        "chaos_id": "tamper_receipt_hash",
    },
    {
        "id": "unsigned_as_evidence",
        "adversary": "insider_ops",
        "asset": "signing_custody",
        "attack": "Issue bind_event with no signature outside DEV",
        "required_deny": "unsigned_halt; RuntimeError on record",
        "chaos_id": "custody_unavailable",
    },
    {
        "id": "truncate_seal",
        "adversary": "insider_ops",
        "asset": "receipt_chain",
        "attack": "Shorten or rewrite evidence seal file",
        "required_deny": "evidence_seal.verify_seal ok=false",
        "chaos_id": "seal_tamper",
    },
    {
        "id": "velaru_down_as_live",
        "adversary": "network_attacker",
        "asset": "clearance_decision",
        "attack": "Timeout / 5xx from fuse upstream",
        "required_deny": "HTTP 503; state UNREACHABLE; verdict false; acted false",
        "chaos_id": "velaru_unreachable",
    },
    {
        "id": "gate_down_as_allow",
        "adversary": "confused_deputy",
        "asset": "clearance_decision",
        "attack": "Worker/PAS continues bind when Gate cannot be reached",
        "required_deny": "weld must fail closed in their runtime (attested; not claimed from Gate alone)",
        "chaos_id": "gate_down_policy",
        "their_production_required": True,
    },
    {
        "id": "admin_resurrect",
        "adversary": "insider_ops",
        "asset": "charge_path",
        "attack": "Gate admin flips DEAD→LIVE without CHARGE",
        "required_deny": "No Gate admin resurrect; CHARGE-only on Velaru",
        "chaos_id": "no_admin_resurrect",
    },
    {
        "id": "staple_swap",
        "adversary": "insider_ops",
        "asset": "staple",
        "attack": "Publish a new public key while old receipts keep old signatures",
        "required_deny": "fingerprint_ok fails across mismatch; rotation must be explicit",
        "chaos_id": "staple_mismatch",
    },
)


def threat_model(*, public_url: str | None = None) -> dict:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "product": "Gate — clearance before irreversible write",
        "default": "DENY under uncertainty",
        "their_production": False,
        "assets": list(ASSETS),
        "adversaries": list(ADVERSARIES),
        "abuse_cases": list(ABUSE_CASES),
        "urls": {
            "threat_model": f"{base}/.well-known/threat-model.json" if base else None,
            "chaos_pack": f"{base}/.well-known/chaos-pack.json" if base else None,
            "fail_closed_matrix": f"{base}/.well-known/fail-closed-matrix.json" if base else None,
            "custody": f"{base}/.well-known/custody.json" if base else None,
        },
    }
