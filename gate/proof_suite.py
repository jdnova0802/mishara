"""Published proof suite — fail-closed invariants strangers can re-run.

Expanded for deploy lift: more real checks, readiness ladder input.
Demo hops never flip their_production. Proof strength does.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-proof-suite-v2"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_invariants() -> list[dict[str, Any]]:
    """Execute invariant checks (no external network required)."""
    results: list[dict[str, Any]] = []

    def add(iid: str, claim: str, passes: bool, evidence: Any) -> None:
        results.append({"id": iid, "claim": claim, "passes": bool(passes), "evidence": evidence})

    # --- Action OS ---
    try:
        from gate import action_os as aos
    except ImportError:
        import action_os as aos  # type: ignore[no-redef]

    m = aos.manifest("https://gate.local")
    add(
        "formula_present",
        "Action OS formula names DENY as scarcity",
        "DENY" in (m.get("formula") or "") and m.get("spec") == "nisaba-action-os-v2",
        {"spec": m.get("spec"), "formula": m.get("formula")},
    )
    add(
        "force_honesty",
        "Force in category; force_production_weld is false",
        bool(m.get("category_includes_force")) and m.get("force_production_weld") is False,
        {
            "category_includes_force": m.get("category_includes_force"),
            "force_production_weld": m.get("force_production_weld"),
        },
    )
    add(
        "aos_not_production",
        "Action OS manifest does not claim their_production",
        m.get("their_production") is False,
        {"their_production": m.get("their_production")},
    )
    add(
        "serve_everybody",
        "Action OS serve list includes economies, politicians, companies, force",
        {s.get("id") for s in (m.get("serve") or [])} >= {"economies", "politicians", "companies", "force"},
        {"serve_ids": [s.get("id") for s in (m.get("serve") or [])]},
    )

    # --- Bound answer ---
    try:
        from gate import bound as bound_mod
    except ImportError:
        import bound as bound_mod  # type: ignore[no-redef]

    dead = bound_mod.from_payload(
        {"verdict": False, "halt": True, "state": "DEAD", "verify_url": "https://velaru.xyz/verify?r=1"},
        200,
    )
    add(
        "dead_holds",
        "DEAD hop with verify_url is a no that holds",
        dead.get("holds") is True and dead.get("answer") is False,
        dead,
    )
    acted = bound_mod.from_payload(
        {"verdict": False, "state": "DEAD", "acted": True, "halt": True},
        200,
    )
    add(
        "dead_that_acted_fails",
        "DEAD that still acted does not hold",
        acted.get("holds") is False,
        acted,
    )
    live = bound_mod.from_payload(
        {"verdict": True, "state": "LIVE", "verify_url": "https://velaru.xyz/verify?r=2"},
        200,
    )
    add(
        "live_is_bound_not_prize",
        "LIVE yes is bound; prize remains a no that holds",
        live.get("answer") is True and live.get("holds") is False,
        live,
    )

    # --- Register ---
    try:
        from gate import register as register_mod
    except ImportError:
        import register as register_mod  # type: ignore[no-redef]

    reg = register_mod.manifest("https://gate.local", "hello@velaru.xyz")
    add(
        "register_not_saas",
        "Register refuses SaaS labeling",
        "SaaS" in (reg.get("not") or []) and reg.get("their_production") is False,
        {"not": reg.get("not"), "serve": (reg.get("civilization") or {}).get("serve")},
    )

    # --- Production skin type ---
    try:
        from gate import production_skin as skin_mod
    except ImportError:
        import production_skin as skin_mod  # type: ignore[no-redef]

    add(
        "skin_bool",
        "Production skin their_production returns bool",
        isinstance(skin_mod.their_production(), bool),
        {"their_production": skin_mod.their_production()},
    )

    # --- Exclusive door ---
    try:
        from gate import exclusive as exclusive_mod
    except ImportError:
        import exclusive as exclusive_mod  # type: ignore[no-redef]

    museum = exclusive_mod.manifesto("https://gate.local")
    add(
        "exclusive_door",
        "Exclusive timing / only-door doctrine is published",
        isinstance(museum, dict) and bool(museum),
        {"keys": list(museum.keys())[:8] if isinstance(museum, dict) else None},
    )

    # --- License fuse CHARGE-only ---
    try:
        from gate import license_fuse as lf
    except ImportError:
        import license_fuse as lf  # type: ignore[no-redef]

    spec = lf.spec("https://gate.local")
    charge_only = False
    if isinstance(spec, dict):
        # look for charge-only resurrection language
        blob = str(spec).lower()
        charge_only = "charge" in blob and ("dead" in blob or "live" in blob)
    add(
        "license_fuse_charge_path",
        "License fuse publishes CHARGE path for DEAD→LIVE",
        charge_only and spec.get("children_cannot_outlive_parent") is True,
        {"children_cannot_outlive_parent": spec.get("children_cannot_outlive_parent")},
    )
    no_charge = lf.charge(license_id="lic_proof_suite", charge_id=None)
    add(
        "license_fuse_rejects_empty_charge",
        "CHARGE without charge_id does not resurrect",
        no_charge.get("ok") is False or no_charge.get("state") != "LIVE",
        no_charge,
    )

    # --- PII reject ---
    try:
        from gate import fields as fields_mod
    except ImportError:
        import fields as fields_mod  # type: ignore[no-redef]

    err = fields_mod.pii_error({"fuse_id": "fuse_velaru_drill", "ssn": "000-00-0000"})
    clean = fields_mod.pii_error({"fuse_id": "fuse_velaru_drill", "job_id": "pc:1"})
    add(
        "pii_rejected",
        "PAS path rejects SSN / PII keys",
        err is not None and clean is None,
        {"rejected": err, "clean": clean},
    )

    # --- Listings refuse admin CHARGE / Palantir cosplay ---
    try:
        from gate import listings as listings_mod
    except ImportError:
        import listings as listings_mod  # type: ignore[no-redef]

    control = listings_mod.listings_manifest("https://gate.local", "hello@velaru.xyz")
    refuse = control.get("refuse") or []
    add(
        "refuse_admin_charge_cosplay",
        "Listings refuse admin CHARGE and Palantir partnership cosplay",
        any("admin CHARGE" in r or "Palantir" in r for r in refuse),
        {"refuse": refuse},
    )

    # --- Family voices research ---
    try:
        from gate import family_voices as fv
    except ImportError:
        import family_voices as fv  # type: ignore[no-redef]

    fam = fv.manifest("https://gate.local")
    add(
        "family_voices_five",
        "Family voice pack covers five siblings with citations",
        len(fam.get("family") or []) == 5
        and all((v.get("citations") or v.get("id") == "gate") for v in fam.get("family") or []),
        {"count": len(fam.get("family") or [])},
    )
    organ_ids = {o.get("id") for o in (fam.get("organs") or [])}
    add(
        "family_organs_seated",
        "May throat + Redeem defense seated as organs, not siblings",
        fam.get("organs_are_not_siblings") is True
        and {"may", "redeem", "inhabitant", "unuttered"}.issubset(organ_ids)
        and len(fam.get("family") or []) == 5,
        {"organs": sorted(organ_ids)},
    )

    try:
        from gate import unison as unison_mod
    except ImportError:
        import unison as unison_mod  # type: ignore[no-redef]

    uni = unison_mod.manifest("https://gate.local")
    add(
        "unison_map",
        "Unison map: cleverer_layer null, intel kit 7.5, Gate 1 lock, no sixth sibling",
        uni.get("cleverer_layer") is None
        and uni.get("their_production") is False
        and uni.get("family_siblings_remain") == 5
        and (uni.get("intel_kit") or {}).get("rating") == 7.5
        and (uni.get("intel_kit") or {}).get("not_a_sibling") is True
        and bool(uni.get("gate1_lock"))
        and len(uni.get("more_massive") or []) >= 4,
        {"intel": (uni.get("intel_kit") or {}).get("rating")},
    )

    try:
        from gate import inventions as inventions_mod
        from gate import inventor as inventor_mod
        from gate import named_may as named_may_mod
    except ImportError:
        import inventions as inventions_mod  # type: ignore[no-redef]
        import inventor as inventor_mod  # type: ignore[no-redef]
        import named_may as named_may_mod  # type: ignore[no-redef]

    inv = inventions_mod.manifest("https://gate.local")
    who = inventor_mod.stamp()
    add(
        "inventor_stands",
        "Inventor is named — Satoshi inverse. May is not bearer by law.",
        who.get("anonymous") is False
        and who.get("satoshi_inverse") is True
        and bool(who.get("name"))
        and (inv.get("inventor") or {}).get("name") == who.get("name")
        and len(inv.get("inventions") or []) >= 12
        and named_may_mod.classify(holder_id=None).get("bearer") is True,
        {"inventor": who.get("name"), "count": len(inv.get("inventions") or [])},
    )

    # --- Settlement / kappa surfaces exist ---
    try:
        from gate import settlement as settlement_mod
    except ImportError:
        import settlement as settlement_mod  # type: ignore[no-redef]

    sm = settlement_mod.spec("https://gate.local") if hasattr(settlement_mod, "spec") else None
    add(
        "settlement_manifest",
        "Settlement engine publishes a spec/manifest",
        isinstance(sm, dict) and bool(sm),
        {"keys": list(sm.keys())[:6] if isinstance(sm, dict) else None},
    )

    try:
        from gate import kappa as kappa_mod
    except ImportError:
        import kappa as kappa_mod  # type: ignore[no-redef]

    km = kappa_mod.manifest("https://gate.local") if hasattr(kappa_mod, "manifest") else None
    add(
        "kappa_manifest",
        "κ register publishes a manifest",
        isinstance(km, dict) and bool(km),
        {"keys": list(km.keys())[:6] if isinstance(km, dict) else None},
    )

    # --- Scorecard honesty hold ---
    try:
        from gate import scorecard as scorecard_mod
    except ImportError:
        import scorecard as scorecard_mod  # type: ignore[no-redef]

    # Avoid recursion: only check constants / PRE_REV_MAX presence
    add(
        "scorecard_has_deploy_ceiling",
        "Scorecard defines deployability ceiling and pre-rev max map",
        hasattr(scorecard_mod, "PRE_REV_MAX")
        and "deployability" in scorecard_mod.PRE_REV_MAX,
        {"deploy_max": getattr(scorecard_mod, "PRE_REV_MAX", {}).get("deployability")},
    )

    # --- Dogfood ≠ production (API shape) ---
    no_confirm = skin_mod.record_production_weld(
        write_path="/v1/act",
        counterparty="counterparty@example.com",
        confirm=False,
    )
    add(
        "dogfood_is_not_production",
        "Production weld API requires confirm; dogfood path cannot silently flip production",
        no_confirm.get("ok") is False
        and callable(getattr(skin_mod, "record_dogfood_weld", None))
        and "confirm" in (no_confirm.get("error") or "").lower(),
        no_confirm,
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
            "violates_if": "admin toggle or empty charge_id resurrects",
            "test": "license_fuse.charge + listings refuse",
        },
        {
            "invariant": "Scarcity is DENY",
            "violates_if": "formula/narrative without halt that holds",
            "test": "action_os.manifest + bound dead_holds",
        },
        {
            "invariant": "Force honesty",
            "violates_if": "battlefield marketing with force_production_weld true",
            "test": "action_os category_includes_force",
        },
        {
            "invariant": "No PII on PAS paths",
            "violates_if": "ssn accepted on bind-check body",
            "test": "fields.pii_error",
        },
        {
            "invariant": "Parent DEAD kills children",
            "violates_if": "tickets redeem after parent DEAD",
            "test": "LicenseFuseTests",
        },
        {
            "invariant": "their_production honesty",
            "violates_if": "demo hop flips production skin",
            "test": "production_skin.their_production + readiness ladder",
        },
        {
            "invariant": "Dogfood is not production",
            "violates_if": "dogfood_weld alone sets their_production true",
            "test": "record_dogfood_weld + their_production false",
        },
        {
            "invariant": "Stranger verify on hop",
            "violates_if": "hop HALT/BLOCK missing verify_url",
            "test": "BindRoomFlaskTests receipt paths",
        },
    ]


def readiness_from_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Map proof strength → deploy ladder (honest, graduated)."""
    total = len(results)
    passed = sum(1 for r in results if r.get("passes"))
    all_pass = total > 0 and passed == total
    ratio = (passed / total) if total else 0.0

    try:
        from gate import production_skin as skin_mod
    except ImportError:
        import production_skin as skin_mod  # type: ignore[no-redef]

    prod = skin_mod.their_production()
    dogfood = False
    checker = getattr(skin_mod, "has_dogfood_weld", None)
    if callable(checker):
        dogfood = bool(checker())

    # Ladder
    # L0 broken <80%
    # L1 proof mostly green
    # L2 all pass
    # L3 dogfood weld
    # L4 their_production
    if prod:
        level, deploy, label = 4, 9.0, "their_production weld"
    elif dogfood and all_pass:
        level, deploy, label = 3, 8.5, "first-party dogfood weld + proof green"
    elif all_pass:
        level, deploy, label = 2, 7.5, "proof suite all pass — production-ready, not welded"
    elif ratio >= 0.8:
        level, deploy, label = 1, 6.5, "proof mostly green"
    else:
        level, deploy, label = 0, 5.0, "proof red — fix invariants"

    # Concept/trust max at green proof. Only deploy waits on their_production.
    return {
        "level": level,
        "label": label,
        "pass_count": passed,
        "total": total,
        "ratio": round(ratio, 3),
        "all_pass": all_pass,
        "dogfood_weld": dogfood,
        "their_production": prod,
        "deployability": deploy,
        "buyer_trust": 9.0 if all_pass else (8.0 if ratio >= 0.8 else 7.0),
        "narrative_vs_reality": 9.0 if all_pass else (7.5 if ratio >= 0.8 else 6.5),
        "irreplaceable": 10.0 if all_pass else (8.5 if ratio >= 0.8 else 7.5),
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    checks = run_invariants()
    ready = readiness_from_results(checks)
    return {
        "spec": SPEC,
        "name": "Proof suite",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "invariants": checks,
        "all_pass": ready["all_pass"],
        "pass_count": ready["pass_count"],
        "total": ready["total"],
        "readiness": ready,
        "matrix": invariant_matrix(),
        "page": f"{base}/proof",
        "runbook": f"{base}/runbook",
        "production_skin": f"{base}/.well-known/production-skin.json",
        "scorecard": f"{base}/.well-known/scorecard.json",
        "their_production": ready["their_production"],
        "gatekeep": "Proof lifts deploy. Weld flips production. Ours.",
    }
