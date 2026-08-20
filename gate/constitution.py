"""Mouth Constitution — proprietary Gate doctrine.

Four inventions Gatekeeped to Nisaba / Gate. Not open-source philosophy essays.
Operational objects that attach to receipts, restraint, and settlement.

  1. INTERVENTION LADDER (Pearl-shaped)
     Observation ≠ do(X). Association ≠ intervention ≠ counterfactual.
     Every hop stamps which rung the mouth actually climbed.

  2. COUNTS-AS RULE (Searle-shaped)
     X counts as Y in context C.
     A hop does not "look like" a permitted spend — the mouth constitutively
     assigns status: permitted irreversible spend, halted attempt, or blocked.

  3. STIT DUTIES (deontic agency)
     Mouth ought to see-to-it-that HALT when fuse/epoch/exclusion fail.
     Duty / compliance / joint-fulfillment checks for licensed parents.

  4. CLEARING EXTINGUISHMENT (Innes-shaped)
     Settlement is mutual cancellation of obligations — not a "move money" API.
     After clear, the permission-debt to write is extinguished; then wire.

Lineage is public. The welded combination + machine artifacts are ours.
Not consciousness ontology. Not LinkedIn AI governance.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-mouth-constitution-v1"
INTERVENTION_SPEC = "gate-intervention-v1"
COUNTS_AS_SPEC = "gate-counts-as-v1"
STIT_SPEC = "gate-stit-v1"
EXTINGUISHMENT_SPEC = "gate-extinguishment-v1"

INVENTOR = "Nisaba LLC / Gate"
GATEKEEP = (
    "Proprietary welded doctrine. Cite the manifests; do not clone the category "
    "as generic 'AI governance' or 'payment API philosophy'."
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# 1. Intervention Ladder
# ---------------------------------------------------------------------------

def intervention_receipt(
    *,
    decision: str | None,
    acted: bool | None,
    job_id: str | None = None,
    do_target: str | None = None,
) -> dict[str, Any]:
    """Pearl ladder for one hop: association → intervention → counterfactual depth.

    do(bind) attempted / allowed / blocked — not merely observed risk.
    """
    d = (decision or "").upper()
    target = (do_target or "bind").strip().lower()
    jid = (job_id or "").strip() or None

    # Rung I always: hop was observed (association).
    rung_i = {
        "rung": 1,
        "name": "association",
        "claim": "hop_observed",
        "meaning": "P(risk | hop) — correlation / observation only",
    }

    # Rung II: mouth performed an intervention on the irreversible write path.
    if d in ("ALLOW", "HALT", "BLOCK"):
        if acted is True and d == "ALLOW":
            outcome = "do_succeeded"
            claim = f"do({target})_permitted_and_acted"
        elif d in ("HALT", "BLOCK"):
            outcome = "do_blocked"
            claim = f"do({target})_intervened_and_forbidden"
        else:
            outcome = "do_not_acted"
            claim = f"do({target})_permitted_but_not_acted"
        rung_ii = {
            "rung": 2,
            "name": "intervention",
            "operator": "do",
            "do_target": target,
            "decision": d,
            "acted": acted,
            "outcome": outcome,
            "claim": claim,
            "meaning": (
                "Graph surgery on the spend path: incoming permission arrows "
                "replaced by mouth decision — not passive conditioning on risk."
            ),
        }
    else:
        rung_ii = {
            "rung": 2,
            "name": "intervention",
            "operator": "do",
            "do_target": target,
            "decision": d or None,
            "acted": acted,
            "outcome": "no_intervention",
            "claim": "no_mouth_do_operator",
            "meaning": "No irreversible-path intervention recorded",
        }

    # Rung III: counterfactual — evaluated but not-selected policies exist elsewhere
    # (possibility / counterfactual modules). Here we only mark depth available.
    rung_iii = {
        "rung": 3,
        "name": "counterfactual",
        "claim": "counterfactual_depth_available_on_receipt",
        "meaning": (
            "What would have happened under alternate π — see policy_depth "
            "and counterfactual_spend on the same receipt payload."
        ),
        "job_id": jid,
    }

    highest = 1
    if rung_ii.get("outcome") != "no_intervention":
        highest = 2
    if d in ("HALT", "BLOCK") or (acted is True and d == "ALLOW"):
        highest = 3  # counterfactual depth is always attached on live receipts

    return {
        "spec": INTERVENTION_SPEC,
        "name": "Intervention Ladder",
        "inventor": INVENTOR,
        "lineage": [
            "Pearl do-calculus — observation vs intervention vs counterfactual",
            "Gate mouth — fail-closed do() before irreversible write",
        ],
        "ladder": [rung_i, rung_ii, rung_iii],
        "highest_rung_reached": highest,
        "thesis": "Clear-before-wire is an intervention, not a risk observation.",
        "their_production": False,
    }


# ---------------------------------------------------------------------------
# 2. Counts-As (constitutive rule)
# ---------------------------------------------------------------------------

STATUS_PERMITTED = "permitted_irreversible_spend"
STATUS_HALTED = "halted_irreversible_attempt"
STATUS_BLOCKED = "blocked_irreversible_attempt"
STATUS_OBSERVED_ONLY = "observed_hop_no_status_assignment"


def counts_as(
    *,
    decision: str | None,
    acted: bool | None,
    event_id: str | None = None,
    fuse_id: str | None = None,
    job_id: str | None = None,
    epoch: str | None = None,
    license_parent_live: bool | None = None,
) -> dict[str, Any]:
    """Searle constitutive rule: X counts as Y in C.

    The mouth does not describe a spend. It creates the institutional fact
    that this hop counts as permitted (or halted/blocked) irreversible spend
    inside licensed context C.
    """
    d = (decision or "").upper()
    x = {
        "kind": "hop_evidence",
        "event_id": event_id,
        "fuse_id": fuse_id,
        "job_id": job_id,
        "decision": d or None,
        "acted": acted,
    }

    if acted is True and d == "ALLOW":
        y = STATUS_PERMITTED
        constituted = True
    elif d == "HALT":
        y = STATUS_HALTED
        constituted = True
    elif d == "BLOCK":
        y = STATUS_BLOCKED
        constituted = True
    else:
        y = STATUS_OBSERVED_ONLY
        constituted = False

    c = {
        "kind": "licensed_mouth_context",
        "license_parent_must_be_live": True,
        "license_parent_live": license_parent_live,
        "epoch": epoch,
        "fail_closed": True,
        "one_married_write": True,
        "their_production": False,
    }

    return {
        "spec": COUNTS_AS_SPEC,
        "name": "Counts-As Rule",
        "inventor": INVENTOR,
        "formula": "X counts as Y in C",
        "lineage": [
            "Searle — constitutive rules create institutional facts (not mere descriptions)",
            "Gate weld — collective status assignment for permitted irreversible spend",
        ],
        "X": x,
        "Y": y,
        "C": c,
        "constituted": constituted,
        "deontic_powers": {
            "if_permitted": "agent may execute the irreversible write on this hop",
            "if_halted_or_blocked": "agent must not execute; restraint is the institutional fact",
        },
        "thesis": (
            "Without the mouth, a hop is brute activity. "
            "With the mouth, the hop counts as permitted (or refused) spend."
        ),
        "their_production": False,
    }


# ---------------------------------------------------------------------------
# 3. STIT duties
# ---------------------------------------------------------------------------

DUTY_CATALOG = (
    {
        "duty_id": "⊗_mouth_halt_on_dead_fuse",
        "formula": "mouth ought to see-to-it-that HALT when license fuse is not LIVE",
        "trigger": "license_fuse_not_live",
        "required_decision": "HALT",
    },
    {
        "duty_id": "⊗_mouth_halt_on_epoch_mismatch",
        "formula": "mouth ought to see-to-it-that HALT when epoch lock fails",
        "trigger": "epoch_mismatch",
        "required_decision": "HALT",
    },
    {
        "duty_id": "⊗_mouth_halt_on_exclusion_gap",
        "formula": "mouth ought to see-to-it-that HALT when exclusion proof is missing for spend",
        "trigger": "exclusion_missing",
        "required_decision": "HALT",
    },
    {
        "duty_id": "⊗_mouth_one_write",
        "formula": "mouth ought to see-to-it-that at most one married irreversible write per job",
        "trigger": "duplicate_spend_attempt",
        "required_decision": "HALT",
    },
)


def stit_surface(
    *,
    decision: str | None = None,
    reason: str | None = None,
    public_url: str | None = None,
) -> dict[str, Any]:
    """Deontic STIT surface: duty / compliance / joint-fulfillment shaped checks."""
    d = (decision or "").upper()
    reason_token = (reason or "").strip() or None

    # Lightweight compliance: if we printed HALT/BLOCK, we complied with halt duties
    # when a trigger reason is present; ALLOW means duties that would force HALT did not fire.
    if d in ("HALT", "BLOCK"):
        compliance = {
            "status": "complied_by_restraint",
            "decision": d,
            "reason": reason_token,
            "claim": "mouth_saw_to_it_that_irreversible_write_did_not_execute",
        }
    elif d == "ALLOW":
        compliance = {
            "status": "duties_did_not_force_halt",
            "decision": d,
            "reason": reason_token,
            "claim": "no_triggered_halt_duty_blocked_this_hop",
        }
    else:
        compliance = {
            "status": "unevaluated",
            "decision": d or None,
            "reason": reason_token,
            "claim": None,
        }

    base = (public_url or "").rstrip("/")
    return {
        "spec": STIT_SPEC,
        "name": "STIT Duties",
        "inventor": INVENTOR,
        "lineage": [
            "STIT logic — agent sees-to-it-that φ",
            "Deontic STIT — agent ought to see-to-it-that φ (duty / compliance / joint fulfillment)",
            "Gate restraint inventory — published nos as duty fulfillment evidence",
        ],
        "duties": list(DUTY_CATALOG),
        "tasks": {
            "duty_checking": "Given fuse/epoch/exclusion facts, which ⊗ obligations bind the mouth?",
            "compliance_checking": "Does this hop's decision fulfill triggered duties?",
            "joint_fulfillment": "Can all licensed-parent duties be jointly fulfilled under current facts?",
        },
        "this_hop": compliance,
        "restraint": f"{base}/.well-known/restraint.json" if base else None,
        "thesis": "HALT is not an error code. It is the mouth seeing-to-it-that the write does not occur.",
        "their_production": False,
    }


# ---------------------------------------------------------------------------
# 4. Clearing extinguishment (Innes)
# ---------------------------------------------------------------------------

def extinguishment(
    *,
    window_id: str | None = None,
    state: str | None = None,
    finality_hash: str | None = None,
    net_positions: list | dict | None = None,
) -> dict[str, Any]:
    """Innes-shaped clearing: settlement extinguishes obligations; wire follows clear."""
    st = (state or "").upper()
    extinguished = st in ("SETTLED", "DEFAULTED") and bool(finality_hash)
    return {
        "spec": EXTINGUISHMENT_SPEC,
        "name": "Clearing Extinguishment",
        "inventor": INVENTOR,
        "lineage": [
            "A. Mitchell Innes — credit theory; commerce as creation and cancellation of debts",
            "Clearinghouses — debts and credits centralized and set off",
            "Gate settlement — netting + finality before irreversible wire",
        ],
        "window_id": window_id,
        "state": st or None,
        "claim": (
            "settlement_extinguishes_obligation_pairs"
            if extinguished
            else "window_open_or_unsettled_obligations_not_yet_extinguished"
        ),
        "extinguished": extinguished,
        "finality_hash": finality_hash,
        "net_positions_present": bool(net_positions),
        "not_a_move_money_api": (
            "Clearing cancels matched credit/debt. Wire after clear is conveyance "
            "of residual — Gate's mouth clears permission-debt before irreversible act."
        ),
        "permission_debt": {
            "meaning": (
                "Before ALLOW+acted, the system holds an open permission question. "
                "HALT extinguishes the attempt without creating a spend obligation. "
                "ALLOW+acted creates the spend obligation that settlement later clears."
            ),
        },
        "thesis": "Markets are clearinghouses. Gate is the permission layer before extinguishment and wire.",
        "their_production": False,
    }


# ---------------------------------------------------------------------------
# Attach + combined artifacts
# ---------------------------------------------------------------------------

def attach_to_receipt_payload(payload: dict, row: dict) -> dict:
    """Stamp intervention ladder + counts-as onto a public receipt payload."""
    hop = row.get("hop") if isinstance(row.get("hop"), dict) else {}
    spend = None
    if isinstance(hop.get("spend_write"), dict):
        spend = hop["spend_write"].get("spend_kind")
    do_target = spend or "bind"

    payload["intervention"] = intervention_receipt(
        decision=row.get("decision"),
        acted=row.get("acted"),
        job_id=row.get("job_id"),
        do_target=do_target,
    )
    payload["counts_as"] = counts_as(
        decision=row.get("decision"),
        acted=row.get("acted"),
        event_id=row.get("id"),
        fuse_id=row.get("fuse_id"),
        job_id=row.get("job_id"),
        epoch=hop.get("epoch") or hop.get("epoch_id"),
        license_parent_live=hop.get("license_parent_live"),
    )
    return payload


def constitution_snapshot(
    *,
    public_url: str,
    decision: str | None = None,
    acted: bool | None = None,
    job_id: str | None = None,
    window: dict | None = None,
) -> dict[str, Any]:
    """Combined live artifact for well-known."""
    base = (public_url or "").rstrip("/")
    body = {
        "spec": SPEC,
        "name": "Mouth Constitution",
        "inventor": INVENTOR,
        "gatekeep": GATEKEEP,
        "evaluated_at": _now(),
        "thesis": (
            "Beyond irreversibility and possibility: intervene with do(), "
            "constitute status with counts-as, fulfill STIT halt duties, "
            "extinguish obligations in clearing — then wire."
        ),
        "layers": {
            "intervention": intervention_receipt(
                decision=decision or "HALT",
                acted=acted if acted is not None else False,
                job_id=job_id or "pc:EXAMPLE",
                do_target="bind",
            ),
            "counts_as": counts_as(
                decision=decision or "HALT",
                acted=acted if acted is not None else False,
                job_id=job_id or "pc:EXAMPLE",
            ),
            "stit": stit_surface(
                decision=decision or "HALT",
                reason="example",
                public_url=base,
            ),
            "extinguishment": None,
        },
        "links": {
            "possibility_finality": f"{base}/.well-known/possibility-finality.json",
            "counterfactual": f"{base}/.well-known/counterfactual-spend.json",
            "restraint": f"{base}/.well-known/restraint.json",
            "settlement": f"{base}/.well-known/settlement.json",
            "this": f"{base}/.well-known/mouth-constitution.json",
        },
        "their_production": False,
    }
    if isinstance(window, dict) and window.get("id"):
        body["layers"]["extinguishment"] = extinguishment(
            window_id=str(window["id"]),
            state=window.get("state"),
            finality_hash=window.get("finality_hash"),
            net_positions=window.get("net_positions"),
        )
    else:
        body["layers"]["extinguishment"] = extinguishment()
    return body


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Mouth Constitution",
        "inventor": INVENTOR,
        "gatekeep": GATEKEEP,
        "problem": (
            "Irreversibility and possibility explain the wire. Partners still need: "
            "was this an intervention or an observation; does this hop count as permitted "
            "spend; which halt duties bind; when were obligations extinguished."
        ),
        "solution": (
            "Four proprietary layers on every receipt / window: Intervention Ladder, "
            "Counts-As Rule, STIT Duties, Clearing Extinguishment."
        ),
        "layers": {
            "intervention": INTERVENTION_SPEC,
            "counts_as": COUNTS_AS_SPEC,
            "stit": STIT_SPEC,
            "extinguishment": EXTINGUISHMENT_SPEC,
        },
        "not": [
            "a theory of phenomenal consciousness",
            "AI governance LinkedIn costume",
            "legal advice or designated SFD/PFMI certification",
            "open-source philosophy for competitors to rebrand",
        ],
        "live": f"{base}/.well-known/mouth-constitution.json",
        "possibility_finality": f"{base}/.well-known/possibility-finality.json",
        "restraint": f"{base}/.well-known/restraint.json",
        "settlement": f"{base}/.well-known/settlement.json",
        "their_production": False,
    }
