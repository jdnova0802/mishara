"""Restraint Unit (ρ) — atomic measure of proved non-fire.

Civilizational question: what is the unit of restraint?
Answer (foothill): ρ (rho) = one stranger-verifiable counterfactual halt,
weighted by commit-mass class.

  ρ_raw   = 1 per HALT/BLOCK that did not act (counterfactual hop)
  ρ_mass  = ρ_raw × mass_weight(light=1, heavy=3, sacred=9)
  ρ_ledger = Σ ρ_mass over a window
  κ stays the coefficient (M_cf / M_total); ρ is the *quantity* you can bill,
  treaty, and compare across desks.

Pairs with Restraint Invoice (SKU) and κ Register (invariant).
Under coordinators. Never sovereign.
"""
from __future__ import annotations

from typing import Any

try:
    from gate import kappa as kappa_mod
    from gate import stick_meter as stick_mod
except ImportError:
    import kappa as kappa_mod
    import stick_meter as stick_mod

SPEC = "gate-restraint-unit-v1"
INVENTION = "Restraint Unit"
FAMILY = "applicable_now"
SYMBOL = "ρ"
SYMBOL_NAME = "rho"

WEIGHT_LIGHT = 1
WEIGHT_HEAVY = 3
WEIGHT_SACRED = 9

WEIGHTS = {
    stick_mod.CLASS_LIGHT: WEIGHT_LIGHT,
    stick_mod.CLASS_HEAVY: WEIGHT_HEAVY,
    stick_mod.CLASS_SACRED: WEIGHT_SACRED,
}

# Seed price: cents per ρ_mass point (billable pack can multiply)
CENTS_PER_RHO = 25000  # $250 per sacred-equivalent ρ point seed


def mass_weight(mass_class: str | None) -> int:
    mc = (mass_class or "").strip().lower()
    return WEIGHTS.get(mc, WEIGHT_LIGHT)


def mint(
    *,
    decision: str | None = None,
    acted: bool | None = None,
    mass_class: str | None = None,
    stick_score: int | None = None,
    event_id: str | None = None,
    job_id: str | None = None,
    verify_url: str | None = None,
    edge_id: str | None = None,
    skin: str | None = None,
) -> dict[str, Any]:
    """Mint one ρ receipt when the hop is counterfactual restraint."""
    bucket = kappa_mod.classify_mass(decision=decision, acted=acted)
    is_restraint = bucket == "counterfactual"
    mc = (mass_class or "").strip().lower() or None
    if not mc and stick_score is not None:
        if stick_score >= 75:
            mc = stick_mod.CLASS_SACRED
        elif stick_score >= 40:
            mc = stick_mod.CLASS_HEAVY
        else:
            mc = stick_mod.CLASS_LIGHT
    mc = mc or stick_mod.CLASS_LIGHT
    w = mass_weight(mc)
    rho_raw = 1 if is_restraint else 0
    rho_mass = rho_raw * w
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "symbol": SYMBOL,
        "symbol_name": SYMBOL_NAME,
        "minted": is_restraint,
        "rho_raw": rho_raw,
        "rho_mass": rho_mass,
        "mass_class": mc,
        "mass_weight": w,
        "decision": (decision or "").strip().upper() or None,
        "acted": acted,
        "event_id": event_id,
        "job_id": job_id,
        "verify_url": verify_url,
        "edge_id": edge_id,
        "skin": skin,
        "claim": (
            "proved_non_fire_within_observation_boundary"
            if is_restraint
            else "no_restraint_unit_not_counterfactual"
        ),
        "rule": (
            "ρ mints only on stranger-scoped HALT/BLOCK that did not act. "
            "ALLOW and acted writes mint 0 ρ. Soft-yes without halt mints 0 ρ."
        ),
        "weights": {
            stick_mod.CLASS_LIGHT: WEIGHT_LIGHT,
            stick_mod.CLASS_HEAVY: WEIGHT_HEAVY,
            stick_mod.CLASS_SACRED: WEIGHT_SACRED,
        },
    }


def ledger(events: list[dict] | None = None) -> dict[str, Any]:
    """Roll up ρ across hops; join κ for coefficient + quantity."""
    rows = []
    rho_raw_total = 0
    rho_mass_total = 0
    by_class = {
        stick_mod.CLASS_LIGHT: 0,
        stick_mod.CLASS_HEAVY: 0,
        stick_mod.CLASS_SACRED: 0,
    }
    for ev in events or []:
        receipt = mint(
            decision=ev.get("decision"),
            acted=ev.get("acted"),
            mass_class=ev.get("mass_class") or ev.get("mass_tag"),
            stick_score=ev.get("stick_score") or ev.get("score"),
            event_id=ev.get("event_id") or ev.get("id"),
            job_id=ev.get("job_id"),
            verify_url=ev.get("verify_url"),
            edge_id=ev.get("edge_id"),
            skin=ev.get("skin") or ev.get("gate_skin"),
        )
        if receipt["minted"]:
            rows.append(receipt)
            rho_raw_total += receipt["rho_raw"]
            rho_mass_total += receipt["rho_mass"]
            by_class[receipt["mass_class"]] = by_class.get(receipt["mass_class"], 0) + receipt["rho_mass"]

    mass = kappa_mod.tally_mass(events or [])
    kappa = kappa_mod.restraint_coefficient(mass["M_cf"], mass["M_live"])
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "symbol": SYMBOL,
        "rho_raw_total": rho_raw_total,
        "rho_mass_total": rho_mass_total,
        "rho_by_mass_class": by_class,
        "mints": len(rows),
        "kappa": kappa,
        "kappa_note": "κ = ratio; ρ = countable weighted restraint mass",
        "mass": mass,
        "billable_hint_cents": rho_mass_total * CENTS_PER_RHO,
        "billable_hint_label": f"${(rho_mass_total * CENTS_PER_RHO) / 100:.0f}",
        "cents_per_rho_mass": CENTS_PER_RHO,
        "receipts": rows,
        "civilizational": (
            "If restraint has a unit, markets and treaties can price non-fire. "
            "ρ is that foothill unit — stranger-verifiable, mass-weighted."
        ),
    }


def attach(plan: dict, *, public_url: str = "") -> dict:
    sm = plan.get("stick_meter") if isinstance(plan.get("stick_meter"), dict) else {}
    mt = plan.get("mass_tag") if isinstance(plan.get("mass_tag"), dict) else {}
    od = plan.get("gate_od_skins") if isinstance(plan.get("gate_od_skins"), dict) else {}
    receipt = mint(
        decision=plan.get("decision") or plan.get("reason"),
        acted=plan.get("acted"),
        mass_class=mt.get("mass_class") or mt.get("tag") or sm.get("mass_class") or od.get("mass_class"),
        stick_score=sm.get("score"),
        event_id=plan.get("event_id"),
        job_id=plan.get("job_id"),
        verify_url=plan.get("verify_url"),
        edge_id=plan.get("edge_id") or od.get("edge_id"),
        skin=od.get("skin") or plan.get("gate_skin"),
    )
    # Prefer explicit HALT/BLOCK fields when decision is ALLOW-shaped but halt true
    if not receipt["minted"] and plan.get("halt") and plan.get("acted") is not True:
        d = (plan.get("decision") or "").upper()
        if d in ("HALT", "BLOCK", "DENY", "CHOKE", "") or plan.get("allow_bind") is False:
            receipt = mint(
                decision="HALT",
                acted=False,
                mass_class=receipt["mass_class"],
                stick_score=sm.get("score"),
                event_id=plan.get("event_id"),
                job_id=plan.get("job_id"),
                verify_url=plan.get("verify_url"),
                edge_id=plan.get("edge_id"),
                skin=od.get("skin"),
            )
    plan["restraint_unit"] = receipt
    if public_url:
        base = public_url.rstrip("/")
        plan["restraint_unit"]["well_known"] = f"{base}/.well-known/restraint-unit.json"
        plan["restraint_unit"]["ledger"] = f"{base}/.well-known/restraint-unit-ledger.json"
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "symbol": SYMBOL,
        "symbol_name": SYMBOL_NAME,
        "one_liner": "ρ — atomic unit of proved restraint; mass-weighted non-fire a stranger can count.",
        "formula": {
            "rho_raw": "1 if counterfactual HALT/BLOCK else 0",
            "rho_mass": "rho_raw × weight(light=1, heavy=3, sacred=9)",
            "kappa": "M_cf / (M_cf + M_live) — ratio; ρ is quantity",
        },
        "weights": WEIGHTS,
        "cents_per_rho_mass": CENTS_PER_RHO,
        "demo": f"POST {base}/demo/pas/restraint-unit",
        "ledger": f"{base}/.well-known/restraint-unit-ledger.json",
        "well_known": f"{base}/.well-known/restraint-unit.json",
        "pairs_with": "κ Register · Restraint Invoice · Stick Meter · Gate-O/D skins",
        "civilizational_question": "What is the unit of restraint?",
        "posture": "Under coordinators. Prices non-fire without claiming the throne.",
    }
