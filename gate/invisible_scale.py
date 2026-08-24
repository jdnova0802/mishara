"""Invisible Staple Scale — full diet of unskippable boredom.

From coolest still-invisible (Bone Law) to chicken-broccoli-rice (Act Serial).
Doctrine: gate/INVISIBLE_SCALE.md. Not outbound. Not L2 throat spam.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-invisible-staple-scale-v1"
INVENTION = "Invisible Staple Scale"
FAMILY = "forge_mandate_metrology"
POSTURE = (
    "Full diet of invisible power: cool quiet terror down to paperwork that bores the dead. "
    "Chicken broccoli rice builds the body. Under coordinators. Never private Omega."
)

# score 0 = blandest staple · 10 = coolest still-invisible
STAPLES: tuple[dict[str, Any], ...] = (
    {
        "slug": "act_serial",
        "title": "Act Serial",
        "score": 0,
        "zone": "cbr",
        "job": "Every irreversible write earns a dull unique serial — or it's a ghost act.",
    },
    {
        "slug": "refuse_line",
        "title": "Refuse Line",
        "score": 0,
        "zone": "cbr",
        "job": "Line item of what did not bind/pay/fire — non-event as accounting.",
    },
    {
        "slug": "verify_stub",
        "title": "Verify Stub",
        "score": 1,
        "zone": "cbr",
        "job": "Ugly stranger permalink is the product. No stub ⇒ club log.",
    },
    {
        "slug": "title_seat",
        "title": "Title Seat",
        "score": 1,
        "zone": "cbr",
        "job": "Named human (or guardian) title owns the halt — examiner paperwork with teeth.",
    },
    {
        "slug": "who_field",
        "title": "Who-Field",
        "score": 2,
        "zone": "cbr",
        "job": "Empty principal slot ⇒ write impossible. Existence condition, not UX.",
    },
    {
        "slug": "when_stamp",
        "title": "When-Stamp",
        "score": 2,
        "zone": "cbr",
        "job": "Ordering as law. Soft clocks forge LIVE.",
    },
    {
        "slug": "mass_number",
        "title": "Mass Number (μ)",
        "score": 3,
        "zone": "cbr",
        "job": "Undo-cost as a shared scalar. Boring metrology; cosmic when Kardashev-scaled.",
    },
    {
        "slug": "may_window_clock",
        "title": "May Window Clock",
        "score": 3,
        "zone": "cbr",
        "job": "May on a schedule — budgets, cool-offs, sabbaths, jubilees.",
    },
    {
        "slug": "funeral_bit",
        "title": "Funeral Bit",
        "score": 4,
        "zone": "steak",
        "job": "Prove the mouth is dead — decommission may-hooks.",
        "existing": "mouth_density",
    },
    {
        "slug": "bind_genealogy",
        "title": "Bind Genealogy",
        "score": 4,
        "zone": "steak",
        "job": "Serial lineage stamp across hops.",
        "existing": "mouth_density",
    },
    {
        "slug": "principal_continuity",
        "title": "Principal Continuity",
        "score": 5,
        "zone": "steak",
        "job": "Death/substrate without stranger handoff ⇒ may-hooks die.",
        "existing": "mandate_layer",
    },
    {
        "slug": "mouth_registry",
        "title": "Mouth Registry",
        "score": 5,
        "zone": "steak",
        "job": "Attested directory — serial, semver, funeral state.",
        "existing": "mandate_layer",
    },
    {
        "slug": "oath_compiler",
        "title": "Oath Compiler",
        "score": 6,
        "zone": "steak",
        "job": "ROE/oath clauses → executable inhibit graph.",
        "existing": "oath_compiler",
    },
    {
        "slug": "restraint_clearing",
        "title": "Restraint Clearing (ρ)",
        "score": 6,
        "zone": "steak",
        "job": "Non-fire settles as clearing mass.",
        "existing": "mandate_layer",
    },
    {
        "slug": "stranger_black_box",
        "title": "Stranger Black Box",
        "score": 7,
        "zone": "steak",
        "job": "Prove-after object anyone opens without trusting the actor.",
        "existing": "receipt_stone",
    },
    {
        "slug": "silence_deny",
        "title": "Deadman / Silence DENY",
        "score": 7,
        "zone": "steak",
        "job": "Loss of contact ⇒ DENY (SCRAM culture).",
        "existing": "mouth_density",
    },
    {
        "slug": "consent_lattice",
        "title": "Consent Lattice",
        "score": 8,
        "zone": "dfwm",
        "job": "Multi-sovereign LIVE mesh — treaty-room invisible.",
        "mountain": True,
    },
    {
        "slug": "senate_socket",
        "title": "Senate Socket",
        "score": 8,
        "zone": "dfwm",
        "job": "N-of-M LIVE as object on the path.",
        "existing": "foothill_max",
        "forge": True,
    },
    {
        "slug": "sheath_cell",
        "title": "Sheath Cell / May Fuse",
        "score": 9,
        "zone": "dfwm",
        "job": "Physical mouth on the irreversible write path.",
        "forge": True,
        "mountain": True,
    },
    {
        "slug": "bone_law",
        "title": "Bone Law",
        "score": 10,
        "zone": "dfwm",
        "job": "May unextractable — extract ⇒ amputate; outside cycle = forgery.",
        "existing": "bone_law",
    },
)


def zone_for(score: int) -> str:
    if score <= 3:
        return "cbr"
    if score <= 7:
        return "steak"
    return "dfwm"


def evaluate_staple(
    *,
    slug: str | None = None,
    act_serial: str | None = None,
    who_field: str | None = None,
    when_stamp: str | None = None,
    mass_number: float | int | None = None,
    verify_stub: str | None = None,
    would_irreversible_write: bool | None = None,
) -> dict[str, Any]:
    """CBR existence checks — blank staples forge the write."""
    missing = []
    if would_irreversible_write:
        if not (act_serial or "").strip():
            missing.append("act_serial")
        if not (who_field or "").strip():
            missing.append("who_field")
        if not (when_stamp or "").strip():
            missing.append("when_stamp")
        if mass_number is None:
            missing.append("mass_number")
        if not (verify_stub or "").strip():
            missing.append("verify_stub")

    if missing and would_irreversible_write:
        return {
            "spec": "gate-cbr-staple-check-v1",
            "invention": "CBR Staple Check",
            "verdict": "STAPLE_STARVED",
            "may_proceed": False,
            "missing": missing,
            "detail": (
                "Irreversible write without chicken-broccoli-rice staples — "
                "ghost act. Fill Act Serial · Who-Field · When-Stamp · Mass Number · Verify Stub."
            ),
            "rule": "CBR zone is existence condition, not paperwork theater.",
            "slug": slug,
        }
    return {
        "spec": "gate-cbr-staple-check-v1",
        "invention": "CBR Staple Check",
        "verdict": "STAPLE_FED",
        "may_proceed": True,
        "missing": [],
        "detail": "Invisible staples present — write may exist inside the diet.",
        "act_serial": act_serial,
        "who_field": who_field,
        "when_stamp": when_stamp,
        "mass_number": mass_number,
        "verify_stub": verify_stub,
        "slug": slug,
    }


def attach(plan: dict, *, public_url: str = "") -> dict:
    """Starve soft irreversible plans that lack CBR staples when explicitly checked."""
    if not (
        plan.get("cbr_check")
        or plan.get("staple_check")
        or plan.get("invisible_scale_check")
    ):
        return plan
    base = (public_url or "").rstrip("/")
    result = evaluate_staple(
        act_serial=plan.get("act_serial") or plan.get("event_id"),
        who_field=plan.get("who_field")
        or plan.get("principal_id")
        or plan.get("from_principal"),
        when_stamp=plan.get("when_stamp") or plan.get("created_at"),
        mass_number=plan.get("mass_number")
        if plan.get("mass_number") is not None
        else (plan.get("mass_tag") or {}).get("score")
        if isinstance(plan.get("mass_tag"), dict)
        else None,
        verify_stub=plan.get("verify_stub") or plan.get("verify_url"),
        would_irreversible_write=bool(
            plan.get("would_irreversible_write")
            or plan.get("allow_bind")
            or plan.get("would_bind")
            or plan.get("acted")
        ),
    )
    if base:
        result["well_known"] = f"{base}/.well-known/invisible-scale.json"
        result["doc"] = "gate/INVISIBLE_SCALE.md"
    plan["invisible_scale"] = result
    if result.get("may_proceed") is False:
        plan["allow_bind"] = False
        if "bind_allowed" in plan:
            plan["bind_allowed"] = False
        plan["halt"] = True
        if not plan.get("decision") or plan.get("decision") in ("ALLOW", "LIVE"):
            plan["decision"] = "HALT"
        plan["reason"] = plan.get("reason") or "invisible_scale:STAPLE_STARVED"
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    by_zone = {"cbr": [], "steak": [], "dfwm": []}
    for s in STAPLES:
        by_zone[s["zone"]].append(s)
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": (
            "Invisible Staple Scale — full diet from Bone Law (10) to Act Serial (0). "
            "Chicken broccoli rice of unskippable boredom."
        ),
        "zones": {
            "cbr": "chicken broccoli rice — scores 0–3 — existence staples",
            "steak": "quiet steak — scores 4–7 — working invisible machinery",
            "dfwm": "don't-fuck-with-me invisible — scores 8–10 — bone / sheath / lattice",
        },
        "staples": list(STAPLES),
        "counts": {z: len(by_zone[z]) for z in by_zone},
        "demo": f"POST {base}/demo/pas/invisible-scale",
        "well_known": f"{base}/.well-known/invisible-scale.json",
        "doc": "gate/INVISIBLE_SCALE.md",
        "bone_law": f"{base}/.well-known/bone-law.json",
        "not_outbound": True,
        "posture": POSTURE,
    }
