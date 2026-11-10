"""Public Bind Room vertical demo (bugs 3–6, 10).

Velaru.xyz hosts the original /demo/bind-room. This module is the Gate copy:
unknown domains 400 instead of silently becoming Insurance; each vertical has
its own checks, step-2 signal, and step-3 bind JSON; every check has a title
and a description so the UI cannot self-echo the lens id.
"""
from __future__ import annotations

import uuid
from typing import Any

SPEC = "gate-bind-room-demo-v1"

# Public SKU names that all mean the same $49 Velaru item (bug 9).
FUSE_SKU = {
    "canonical": "fuse",
    "price_label": "$49",
    "aliases": ("Instant receipt", "Payout gate", "fuse", "Paper Check"),
    "note": "One SKU. Four names in the wild. Gate and Velaru both mean the $49 fuse.",
}

# Live velaru keys + plain aliases for the six labeled verticals.
ALIASES = {
    "court": "forensic",
    "reinsurance": "actuarial",
    "clinical": "biology",
    "board": "institutional",
    "fleet": "network",
    "grid": "climate",
    "counsel": "epistemics",
    "vertical": "insurance",  # Cmd+K alias lands on the room, not a fake vertical
}


def _check(check_id: str, title: str, description: str, **profile: Any) -> dict[str, Any]:
    body = {"title": title, "description": description, **profile}
    return {"lens": check_id, "ok": True, "profile": body}


DOMAINS: dict[str, dict[str, Any]] = {
    "insurance": {
        "label": "Insurance · bind / renew",
        "chokepoint": "PAS bind before premium moves",
        "signal_reason": "Pattern grade A — bind appetite is within the declared underwriting box.",
        "bind_reason": "Premium $62,400 is $12,400 over the $50,000 agent delegation. Human sign-off required before bind.",
        "bind_gate": {
            "result": "BLOCK",
            "bind_allowed": False,
            "delegation_limit_usd": 50000,
            "premium_usd": 62400,
            "policy_number": "DEMO-PAS-2026-001",
            "source": "gate-bind-room-demo",
        },
        "lenses": [
            _check(
                "actuarial",
                "Priced-blind liability",
                "AI underwriting is Annex III high-risk. This check asks whether loss data exists before appetite is set — not whether a model exists.",
                annex_iii_trigger="EU AI Act Art. 12 logging for high-risk insurance AI.",
            ),
            _check(
                "forensic",
                "FRE 702 chain of authenticity",
                "The bind file must be hash-bound and handler-signed so a stranger can re-derive it. A filename in a share drive is not a chain.",
                applicable_rule="Federal Rule of Evidence 702",
            ),
        ],
    },
    "hiring": {
        "label": "Hiring · adverse action",
        "chokepoint": "Signal grade before adverse action",
        "signal_reason": "Score is inside the stated hiring band; adverse-action copy is ready if the human still rejects.",
        "bind_reason": "Adverse-action letter cannot go out until the scored features are on the receipt the candidate can open.",
        "bind_gate": {
            "result": "BLOCK",
            "bind_allowed": False,
            "action": "adverse_action_notice",
            "source": "gate-bind-room-demo",
        },
        "lenses": [
            _check(
                "hiring",
                "FCRA-style notice before reject",
                "If a model score is used to deny a person, the receipt has to name the inputs. A silent reject is the failure.",
            ),
        ],
    },
    "forensic": {
        "label": "Court · authenticity",
        "chokepoint": "Chain of authenticity before testimony",
        "signal_reason": "Hash of the exhibit matches the capture record. Handler list is complete.",
        "bind_reason": "Testimony is blocked until the exhibit’s hash and handler list are on one receipt.",
        "bind_gate": {
            "result": "BLOCK",
            "bind_allowed": False,
            "exhibit_id": "DEMO-EXH-14",
            "source": "gate-bind-room-demo",
        },
        "lenses": [
            _check(
                "forensic",
                "Handler-signed exhibit",
                "Every hand-off of the file is a named person plus a hash. Missing a handler is a HOLD, not a footnote.",
            ),
        ],
    },
    "actuarial": {
        "label": "Reinsurance · appetite",
        "chokepoint": "Pattern grade before bind appetite",
        "signal_reason": "Treaty box holds: ceded loss ratio still inside the signed band.",
        "bind_reason": "Appetite cannot move until the cedent’s last three bordereaux hash-match the filing copies.",
        "bind_gate": {
            "result": "BLOCK",
            "bind_allowed": False,
            "treaty": "DEMO-XOL-2026",
            "source": "gate-bind-room-demo",
        },
        "lenses": [
            _check(
                "reinsurance",
                "Bordereau hash match",
                "Appetite is a number on a treaty. This check is whether the loss file that produced it is the same file the cedent filed.",
            ),
            _check(
                "institutional",
                "UW committee two-person rule",
                "A single underwriter cannot widen appetite. Second key is a named human on the receipt, not a Slack emoji.",
            ),
        ],
    },
    "mortgage": {
        "label": "Mortgage · capital move",
        "chokepoint": "Path + pattern before capital moves",
        "signal_reason": "DTI and collateral path cleared the stated overlay.",
        "bind_reason": "Wire is blocked until the overlay receipt is attached to the closing package.",
        "bind_gate": {
            "result": "BLOCK",
            "bind_allowed": False,
            "loan_id": "DEMO-MTG-2026",
            "source": "gate-bind-room-demo",
        },
        "lenses": [
            _check(
                "mortgage",
                "Overlay before wire",
                "Capital does not move on a green dashboard. It moves when the overlay that allowed it is on a receipt.",
            ),
        ],
    },
    "defense": {
        "label": "Defense · irreversible act",
        "chokepoint": "Delegation trace before irreversible act",
        "signal_reason": "Delegation chain reaches a named human principal.",
        "bind_reason": "Act is blocked until the principal’s key is on the same receipt as the order.",
        "bind_gate": {
            "result": "BLOCK",
            "bind_allowed": False,
            "order_id": "DEMO-DEF-2026",
            "source": "gate-bind-room-demo",
        },
        "lenses": [
            _check(
                "defense",
                "Named principal",
                "An agent order with no human principal on the receipt is not an order. It is a HOLD.",
            ),
        ],
    },
    "creator": {
        "label": "Creator · publish mark",
        "chokepoint": "Mark + drift check before publish",
        "signal_reason": "Provenance mark is present; drift vs last clean publish is inside band.",
        "bind_reason": "Publish is blocked until the mark verifies against the last signed cut.",
        "bind_gate": {
            "result": "BLOCK",
            "bind_allowed": False,
            "asset_id": "DEMO-CRE-2026",
            "source": "gate-bind-room-demo",
        },
        "lenses": [
            _check(
                "creator",
                "Provenance mark before publish",
                "If the file cannot prove who cut it, it does not go out. A caption is not a mark.",
            ),
        ],
    },
    "public": {
        "label": "Public · benefit act",
        "chokepoint": "Anti-capture grade before benefit act",
        "signal_reason": "Eligibility path is inside the published rule set.",
        "bind_reason": "Benefit write is blocked until the eligibility receipt is stranger-verifiable.",
        "bind_gate": {
            "result": "BLOCK",
            "bind_allowed": False,
            "benefit_id": "DEMO-PUB-2026",
            "source": "gate-bind-room-demo",
        },
        "lenses": [
            _check(
                "public",
                "Published rule, not a private score",
                "A benefits agent cannot apply a rule that is not on the public receipt. Capture looks like a silent extra test.",
            ),
        ],
    },
    "biology": {
        "label": "Clinical · model lineage",
        "chokepoint": "Model lineage before clinical act",
        "signal_reason": "Model digest matches the locked protocol version.",
        "bind_reason": "Clinical act is blocked until lineage of weights + protocol is on one receipt. Not an insurance premium check.",
        "bind_gate": {
            "result": "BLOCK",
            "bind_allowed": False,
            "protocol_id": "DEMO-CLN-2026",
            "model_digest": "sha256:demo-clinical-weights",
            "source": "gate-bind-room-demo",
        },
        "lenses": [
            _check(
                "biology",
                "Locked protocol vs running weights",
                "The act uses the weights named in the protocol, or it does not run. A later checkpoint with the same filename is a different model.",
            ),
            _check(
                "archival",
                "Retain the inputs that were scored",
                "If the hospital cannot re-open the exact inputs, the act is not reconstructable. Reconstruction is the clinical bar here.",
            ),
        ],
    },
    "institutional": {
        "label": "Board · executive delegate",
        "chokepoint": "Executive liability before delegation",
        "signal_reason": "Board minute hash matches the delegation instrument.",
        "bind_reason": "Delegation is blocked until two directors’ keys are on the instrument. Not a $50K premium check.",
        "bind_gate": {
            "result": "BLOCK",
            "bind_allowed": False,
            "instrument_id": "DEMO-BRD-2026",
            "quorum_required": 2,
            "source": "gate-bind-room-demo",
        },
        "lenses": [
            _check(
                "institutional",
                "Two-person rule on the instrument",
                "A CEO-only click is not a board act. Two named directors, two signatures, one hash.",
            ),
            _check(
                "political",
                "Scope of the minute",
                "The minute has to name the act. ‘Management is authorized’ is not a scope.",
            ),
        ],
    },
    "network": {
        "label": "Fleet · blast radius",
        "chokepoint": "Cascade check before fleet deploy",
        "signal_reason": "Blast radius is 14 nodes; policy cap is 8. HOLD on the overflow.",
        "bind_reason": "Deploy is blocked: 14-node cascade exceeds the 8-node fleet cap. Not a PAS premium check.",
        "bind_gate": {
            "result": "BLOCK",
            "bind_allowed": False,
            "nodes_in_cascade": 14,
            "fleet_cap": 8,
            "source": "gate-bind-room-demo",
        },
        "lenses": [
            _check(
                "network",
                "Cascade vs fleet cap",
                "A rollout that can take 14 vehicles with it is over an 8-vehicle cap. The receipt names both numbers.",
            ),
            _check(
                "formal",
                "Specification adherence, not spec-correctness",
                "We prove the deploy matched the declared cap. We do not prove the cap itself is the right safety number.",
            ),
            _check(
                "reputation",
                "Cross-session collusion watch",
                "Same-pattern deploys from sibling agents in the same hour are one cascade, not twelve clean rolls.",
            ),
        ],
    },
    "climate": {
        "label": "Grid · refusal act",
        "chokepoint": "Refusal receipt before grid commit",
        "signal_reason": "Commit would drop reserve below the named floor.",
        "bind_reason": "Grid commit is blocked until a refusal receipt exists for the reserve-floor breach. Not a PAS premium check.",
        "bind_gate": {
            "result": "BLOCK",
            "bind_allowed": False,
            "reserve_floor_mw": 120,
            "projected_mw": 91,
            "source": "gate-bind-room-demo",
        },
        "lenses": [
            _check(
                "network",
                "Reserve floor is a number",
                "If projected reserve is 91 MW against a 120 MW floor, the act is a refusal, not a warning banner.",
            ),
            _check(
                "institutional",
                "Who may waive the floor",
                "A waiver is a named role on a receipt. A night operator chat is not a waiver.",
            ),
            _check(
                "formal",
                "Proof-test the trip",
                "The block has to have been drill-tested. An untested trip is assumed failed.",
            ),
        ],
    },
    "epistemics": {
        "label": "Counsel · falsifiability",
        "chokepoint": "External witness under impossibility limits",
        "signal_reason": "Claim is stated as a bounded adherence proof, not as universal safety.",
        "bind_reason": "Filing is blocked until the assumption set is named. A bare ‘verified: true’ is rejected.",
        "bind_gate": {
            "result": "BLOCK",
            "bind_allowed": False,
            "assumptions_required": True,
            "source": "gate-bind-room-demo",
        },
        "lenses": [
            _check(
                "philosophy",
                "Named assumptions",
                "A proof that hides its assumptions is vacuous. Counsel needs the list on the receipt.",
            ),
            _check(
                "formal",
                "Per-instance certificate",
                "Each act gets its own certificate. There is no universal ‘the system is safe’ stamp.",
            ),
            _check(
                "forensic",
                "Stranger can re-derive the hash",
                "Opposing counsel does not need our database. They need the hash and the bytes.",
            ),
        ],
    },
}


def normalize_domain(raw: str | None) -> str | None:
    key = (raw or "").strip().lower()
    if not key:
        return None
    key = ALIASES.get(key, key)
    if key in DOMAINS:
        return key
    return None


def _attach_v1(domain: str, bind_gate: dict[str, Any]) -> dict[str, Any]:
    try:
        from gate import v1 as v1_mod
    except ImportError:
        import v1 as v1_mod

    inputs = dict(bind_gate)
    inputs.setdefault("remaining_seconds", 300)
    inputs.setdefault("ttl_seconds", 300)
    snap = v1_mod.compute(domain, inputs)
    out = dict(bind_gate)
    out.update({k: v for k, v in snap["derived"].items() if v is not None})
    out["finality_event"] = snap["finality_event"]
    out["v1_distance"] = snap["v1_distance"]
    out["undo_open"] = snap["undo_open"]
    out["lookup_table"] = False
    return out


def catalog() -> list[dict[str, str]]:
    rows = []
    for key, spec in DOMAINS.items():
        rows.append(
            {
                "id": key,
                "label": spec["label"],
                "chokepoint": spec["chokepoint"],
            }
        )
    return rows


def run(*, domain: str | None, company: str | None, public_url: str) -> tuple[int, dict[str, Any]]:
    resolved = normalize_domain(domain)
    if resolved is None:
        return 400, {
            "ok": False,
            "error": "unknown_domain",
            "message": "domain is required and must be a known vertical — unknown values do not become Insurance.",
            "allowed": sorted(DOMAINS.keys()),
            "aliases": dict(ALIASES),
        }
    spec = DOMAINS[resolved]
    company_name = (company or "").strip() or "Demo operator"
    session_id = "bind-" + uuid.uuid4().hex[:12]
    base = (public_url or "").rstrip("/")
    bind_gate = _attach_v1(resolved, {**spec["bind_gate"], "reason": spec["bind_reason"]})
    signal = {
        "gate_result": "ACT",
        "asymmetry_grade": "A",
        "asymmetry_score": 90,
        "decision_id": session_id + "-signal",
        "reason": spec["signal_reason"],
        "domain": resolved,
        "vertical_label": spec["label"],
        "signal_verify_url": f"{base}/verify",
    }
    proof = {
        "bind_gate": bind_gate,
        "verify_url": f"{base}/verify",
        "permalink": f"{base}/demo/bind-room?domain={resolved}",
        "restraint": True,
    }
    try:
        from gate import readback as readback_mod
    except ImportError:
        import readback as readback_mod

    hb_status, hb = readback_mod.hearback(domain=resolved, company=company_name)
    hearback = hb if hb_status == 200 else {"ok": False, "confirmed": False, "gated": False}
    body = {
        "ok": True,
        "spec": SPEC,
        "session_id": session_id,
        "company": company_name,
        "domain": resolved,
        "domain_label": spec["label"],
        "chokepoint": spec["chokepoint"],
        "domain_lenses": spec["lenses"],
        "signal": signal,
        "proof": proof,
        "step2_json": signal,
        "step3_json": bind_gate,
        "mishara_handoff": False,
        "demo": True,
        "their_production": False,
        "hearback": hearback,
        "gated": False,
        "hearback_confirmed": False,
        "plain": "Pattern is paraphrased. Gate does not fire until hearback is confirmed.",
    }
    return 200, body
