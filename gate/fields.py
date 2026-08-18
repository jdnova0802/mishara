"""PAS bodies are fuse_id + job identifiers only. No ECDIS, no ACORD, no PII."""
from __future__ import annotations

ALLOWED_PAS_KEYS = frozenset(
    {
        "fuse_id",
        "job_id",
        "action",
        "premium",
        "authority_limit",
        "line",
        "state",
        "country",
        "policy_number",
        "issue_type",
        "bind_path",
        "allowed_lines",
        "allowed_states",
        "charge_id",
        "ticket_id",
        "token",
        "method",
        "path",
        "spend_fingerprint",
        "spend_kind",
    }
)

PII_KEYS = frozenset(
    {
        "ssn",
        "social_security",
        "social_security_number",
        "dob",
        "date_of_birth",
        "first_name",
        "last_name",
        "full_name",
        "address",
        "street",
        "email",
        "phone",
        "phone_number",
        "acord",
        "loss_run",
        "loss_runs",
        "vin",
        "drivers_license",
        "driver_license",
        "license_number",
        "medical",
        "claimant",
        "insured_name",
        "named_insured",
        "ecdis",
    }
)


def pii_error(body: dict) -> dict | None:
    if not isinstance(body, dict):
        return {"error": {"code": "invalid_body", "message": "JSON object required"}}
    hit = sorted(k for k in body if str(k).lower() in PII_KEYS)
    if hit:
        return {
            "error": {
                "code": "no_pii",
                "message": "This path is fuse_id + job identifiers only. Do not send PII, ACORD, or ECDIS.",
                "rejected_keys": hit,
            }
        }
    return None


def allowlist_pas(body: dict) -> dict:
    cleaned = {}
    for key, value in (body or {}).items():
        if key in ALLOWED_PAS_KEYS:
            cleaned[key] = value
    return cleaned
