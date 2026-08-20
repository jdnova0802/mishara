"""Published proof suite — fail-closed invariants strangers can re-run."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-proof-suite-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_invariants() -> list[dict[str, Any]]:
    """Execute lightweight invariant checks (no network)."""
    results: list[dict[str, Any]] = []
    try:
        from gate import closure as closure_mod
    except ImportError:
        import closure as closure_mod  # type: ignore[no-redef]
    try:
        from gate import costliness as costliness_mod
    except ImportError:
        import costliness as costliness_mod  # type: ignore[no-redef]
    try:
        from gate import moat as moat_mod
    except ImportError:
        import moat as moat_mod  # type: ignore[no-redef]

    uw = closure_mod.classify_operation("uw_approve_without_charge")
    results.append(
        {
            "id": "charge_only_resurrection",
            "claim": "UW approve without CHARGE does not enter permission network",
            "passes": not uw["enters_decision_network"],
            "evidence": uw,
        }
    )
    charge_ok = costliness_mod.assay(transition="charge", charge_id="chg_proof_1")
    charge_bad = costliness_mod.assay(transition="charge", charge_id=None)
    results.append(
        {
            "id": "costliness_charge_id",
            "claim": "CHARGE transition requires charge_id",
            "passes": charge_ok["passes"] and not charge_bad["passes"],
            "evidence": {"ok": charge_ok, "bad": charge_bad},
        }
    )
    fp = moat_mod.fingerprint("https://gate.local")
    results.append(
        {
            "id": "moat_fingerprint",
            "claim": "Catalog fingerprint is stable SHA-256 over 105 specs",
            "passes": len(fp.get("fingerprint_sha256") or "") == 64 and fp.get("invention_count") == 105,
            "evidence": {
                "count": fp.get("invention_count"),
                "short": fp.get("fingerprint_short"),
            },
        }
    )
    return results


def invariant_matrix() -> list[dict[str, str]]:
    return [
        {
            "invariant": "Fail-closed on timeout/5xx",
            "violates_if": "UNREACHABLE or timeout treated as LIVE",
            "test": "test_listings FlaskListingTests demo hop HALT paths",
        },
        {
            "invariant": "CHARGE-only DEAD→LIVE",
            "violates_if": "admin toggle or UW approve resurrects without charge_id",
            "test": "closure.classify_operation + costliness.assay",
        },
        {
            "invariant": "Parent DEAD kills children",
            "violates_if": "outstanding bind tickets redeem after parent DEAD",
            "test": "LicenseFuseTests",
        },
        {
            "invariant": "No PII on PAS paths",
            "violates_if": "ssn or named insured accepted on bind-check",
            "test": "FieldAndWeldTests.test_pii_rejected",
        },
        {
            "invariant": "Stranger verify on hop",
            "violates_if": "hop response missing verify_url on HALT/BLOCK",
            "test": "BindRoomFlaskTests receipt paths",
        },
        {
            "invariant": "Idempotent operator weld",
            "violates_if": "duplicate checkout consumes two welds",
            "test": "OperatorInvoiceTests.test_dev_operator_checkout_is_idempotent",
        },
        {
            "invariant": "Partial catalog clone fails moat",
            "violates_if": "fork missing one spec still claims Gate",
            "test": "scripts/fork_fingerprint_demo.py",
        },
    ]


def fork_demo_instructions(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "script": "scripts/fork_fingerprint_demo.py",
        "usage": "python3 scripts/fork_fingerprint_demo.py",
        "claim": "Remove one invention from CATALOG → fingerprint mismatch",
        "full_catalog_url": f"{base}/.well-known/inventions.json",
        "moat_url": f"{base}/.well-known/moat.json",
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    results = run_invariants()
    all_pass = all(r["passes"] for r in results)
    return {
        "spec": SPEC,
        "name": "Proof suite",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "all_pass": all_pass,
        "results": results,
        "invariant_matrix": invariant_matrix(),
        "fork_demo": fork_demo_instructions(base),
        "re_run": f"GET {base}/.well-known/proof-suite.json",
        "unittest": "python3 -m unittest test_listings",
    }
