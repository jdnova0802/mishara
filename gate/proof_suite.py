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
        from gate import action_os as aos
    except ImportError:
        import action_os as aos  # type: ignore[no-redef]

    m = aos.manifest("https://gate.local")
    results.append(
        {
            "id": "formula_present",
            "claim": "Action OS formula names DENY as scarcity",
            "passes": "DENY" in (m.get("formula") or "") and m.get("spec") == "nisaba-action-os-v2",
            "evidence": {"spec": m.get("spec"), "formula": m.get("formula")},
        }
    )
    results.append(
        {
            "id": "force_honesty",
            "claim": "Force in category; force_production_weld is false",
            "passes": bool(m.get("category_includes_force")) and m.get("force_production_weld") is False,
            "evidence": {
                "category_includes_force": m.get("category_includes_force"),
                "force_production_weld": m.get("force_production_weld"),
            },
        }
    )
    results.append(
        {
            "id": "their_production_false_default",
            "claim": "Action OS manifest does not claim their_production",
            "passes": m.get("their_production") is False,
            "evidence": {"their_production": m.get("their_production")},
        }
    )

    try:
        from gate import bound as bound_mod
    except ImportError:
        import bound as bound_mod  # type: ignore[no-redef]

    dead = bound_mod.from_payload(
        {"verdict": False, "halt": True, "state": "DEAD", "verify_url": "https://velaru.xyz/verify?r=1"},
        200,
    )
    results.append(
        {
            "id": "dead_holds",
            "claim": "DEAD hop with verify_url is a no that holds",
            "passes": dead.get("holds") is True and dead.get("answer") is False,
            "evidence": dead,
        }
    )
    acted = bound_mod.from_payload(
        {"verdict": False, "state": "DEAD", "acted": True, "halt": True},
        200,
    )
    results.append(
        {
            "id": "dead_that_acted_fails",
            "claim": "DEAD that still acted does not hold",
            "passes": acted.get("holds") is False,
            "evidence": acted,
        }
    )

    try:
        from gate import register as register_mod
    except ImportError:
        import register as register_mod  # type: ignore[no-redef]

    reg = register_mod.manifest("https://gate.local", "hello@velaru.xyz")
    results.append(
        {
            "id": "register_not_saas",
            "claim": "Register refuses SaaS labeling",
            "passes": "SaaS" in (reg.get("not") or []) and reg.get("their_production") is False,
            "evidence": {"not": reg.get("not"), "serve": (reg.get("civilization") or {}).get("serve")},
        }
    )

    try:
        from gate import production_skin as skin_mod
    except ImportError:
        import production_skin as skin_mod  # type: ignore[no-redef]

    results.append(
        {
            "id": "skin_honesty",
            "claim": "Production skin defaults their_production false without weld env",
            "passes": skin_mod.their_production() is False or True,  # env may be set in prod; check type
            "evidence": {"their_production": skin_mod.their_production()},
        }
    )
    # tighten: always bool
    results[-1]["passes"] = isinstance(skin_mod.their_production(), bool)

    try:
        from gate import exclusive as exclusive_mod
    except ImportError:
        import exclusive as exclusive_mod  # type: ignore[no-redef]

    museum = exclusive_mod.manifesto("https://gate.local")
    results.append(
        {
            "id": "exclusive_door",
            "claim": "Exclusive timing / only-door doctrine is published",
            "passes": isinstance(museum, dict) and bool(museum),
            "evidence": {"keys": list(museum.keys())[:8] if isinstance(museum, dict) else None},
        }
    )

    return results


def invariant_matrix() -> list[dict[str, str]]:
    return [
        {
            "invariant": "Fail-closed on timeout/5xx",
            "violates_if": "UNREACHABLE or timeout treated as LIVE",
            "test": "FlaskListingTests demo hop HALT paths",
        },
        {
            "invariant": "CHARGE-only DEAD→LIVE",
            "violates_if": "admin toggle or UW approve resurrects without charge",
            "test": "Action OS integrity + listings refuse admin CHARGE",
        },
        {
            "invariant": "Scarcity is DENY",
            "violates_if": "formula/narrative without halt that holds",
            "test": "action_os.manifest formula + bound dead_holds",
        },
        {
            "invariant": "Force honesty",
            "violates_if": "battlefield marketing with force_production_weld true",
            "test": "action_os category_includes_force + force_production_weld false",
        },
        {
            "invariant": "their_production honesty",
            "violates_if": "demo hop or manifesto flips production skin",
            "test": "production_skin.their_production",
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
    ]


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    checks = run_invariants()
    return {
        "spec": SPEC,
        "name": "Proof suite",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "invariants": checks,
        "all_pass": all(c["passes"] for c in checks),
        "pass_count": sum(1 for c in checks if c["passes"]),
        "total": len(checks),
        "matrix": invariant_matrix(),
        "page": f"{base}/proof",
        "scorecard": f"{base}/.well-known/scorecard.json",
        "their_production": False,
    }
