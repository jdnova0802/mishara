"""Nisaba family voices — research-backed, Velaru-engine, own gravity.

Erra / Verra / Mishara were under-voiced relative to Velaru and Gate.
This module is the rigorous pass: real market bites, buyers, scarcity,
citations, paste packs for sibling deploys. Reflect Velaru as engine;
do not clone Velaru's voice.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "nisaba-family-voices-v1"
INVENTOR = "Nisaba LLC"

ENGINE = {
    "name": "Velaru",
    "role": "proof engine",
    "inherits": [
        "Stranger verify instinct",
        "Fail-closed DNA",
        "Custody wall / no forge-alone",
        "Industrial ops bar",
        "Patent #64/124,027 stack",
    ],
    "not_cloned": [
        "Hero question (each sibling asks differently)",
        "Buyer ICP",
        "Scarcity object",
        "Chrome / twin coloring as substitute for voice",
    ],
}

# ---------------------------------------------------------------------------
# Research-backed voice packs
# ---------------------------------------------------------------------------

VOICES: dict[str, dict[str, Any]] = {
    "velaru": {
        "name": "Velaru",
        "role": "proof rail",
        "question": "Did we commit correctly?",
        "voice_line": "The receipt that neither side controls",
        "scarcity": "Independent verify of ALLOW/BLOCK + silence — not the classifier",
        "reflects_engine": True,
        "url": "https://velaru.xyz",
        "market_problem": (
            "Platforms prove generation. Carriers and GC need stranger-verifiable "
            "refusal, silence, and commit receipts before dispute discovery — "
            "EU AI Act Art 12 logging, FRE 707 prep, AI liability underwriting."
        ),
        "buyer": "GC · carrier counsel · HR AI vendors · compliance",
        "enemy": [
            "Trust-me dashboards",
            "Logs only the vendor controls",
            "Guardrail demos sold as court-grade artifacts",
        ],
        "one_liner_ads": (
            "Show me the receipt. Stranger verify. Neither operator nor vendor forges alone."
        ),
        "citations": [
            {
                "title": "EU AI Act Article 12 — record-keeping / logging for high-risk systems",
                "why": "Tamper-evident attempt records are mandated; vendor logs are not enough",
            },
            {
                "title": "FRE 707 prep / AI liability insurance pullbacks (Mayflower/Hadron class)",
                "why": "Insurers price on independent artifacts, not chat traces",
            },
        ],
        "shipped": [
            "Public /verify",
            "Bind-gate ALLOW/BLOCK",
            "Restraint receipts",
            "Trust Pack / BYOK",
        ],
        "paste_hero": (
            "Can this agent still act right now?\n"
            "Signed public existence. If the fuse is DEAD, capability fails closed."
        ),
    },
    "erra": {
        "name": "Erra",
        "role": "signal rail",
        "question": "Should we act?",
        "voice_line": "Show me the cluster before you bind",
        "scarcity": "Independent ACT/HOLD pattern grade before capital moves — not a Velaru twin skin",
        "reflects_engine": True,
        "url": "https://velaru.xyz/erra",
        "market_problem": (
            "Reinsurance and UW are adopting agentic AI under Solvency II / EIOPA AI opinion "
            "and EU AI Act high-risk rules. Carriers price on patterns; platforms prove on logs. "
            "Nobody ships independent fusion + actuarial-grade asymmetry before bind — "
            "HITL checkpoints without a stranger-auditable signal snapshot are theater."
        ),
        "buyer": "Reinsurance · treaty UW · claims AI · public-sector signal desks",
        "enemy": [
            "Opaque model scores with no exportable snapshot",
            "Proof-only demos that never answer 'should we act?'",
            "Actuarial grade as a slide, not a threshold-gate",
        ],
        "one_liner_ads": (
            "Before you bind: ACT or HOLD on the cluster. "
            "Independent signal snapshot — not the platform's score."
        ),
        "citations": [
            {
                "title": "EIOPA Opinion on AI governance and risk management (insurance)",
                "why": "Undertakings remain responsible; third-party AI needs complementary diligence artifacts",
                "url": "https://www.eiopa.europa.eu/",
            },
            {
                "title": "arXiv 2511.08082 — Prudential reliability of LLMs in reinsurance",
                "why": "Retrieval grounding + structured logging + HITL before prudential adoption",
                "url": "https://arxiv.org/pdf/2511.08082",
            },
            {
                "title": "ITC / industry 2026 — 'AI that can't be explained is AI that can't be adopted'",
                "why": "Auditability of UW AI is the adoption gate for capacity",
            },
            {
                "title": "Defensible data set / governed semantic layer for reinsurance AI",
                "why": "Context gap: outputs must trace to authorized definitions before bind",
            },
        ],
        "shipped": [
            "Threshold-gate demo ACT/HOLD",
            "Asymmetry grade A–D",
            "Signal verify (8 checks)",
            "Separate X-Erra-API-Key custody",
            "420 signal SKUs",
        ],
        "gaps": [
            "Live site still reads as Velaru inverse chrome — paste this voice",
            "Auto re-score post-outcome still SOW",
        ],
        "paste_hero": (
            "Should we act?\n"
            "Independent pattern fusion before bind. ACT or HOLD. "
            "Signal snapshot a stranger can audit — Velaru proves the commit after."
        ),
        "paste_nav": "Start · Demo · Signal verify · SKUs · Integrate · Health · Velaru proof →",
        "paste_not": (
            "Not a Velaru reskin. Not a classifier dashboard. "
            "Not proof of what happened — that is Velaru. Erra is whether to move."
        ),
    },
    "verra": {
        "name": "Verra",
        "role": "action session",
        "question": "Did both rails clear before bind?",
        "voice_line": "The room where both rails must clear",
        "scarcity": "One export pack (signal + proof) that leaves before capital/coverage/force — not a fourth deploy",
        "reflects_engine": True,
        "url": "https://velaru.xyz/verra",
        "market_problem": (
            "PolicyCenter bind-only is an irreversible PAS write "
            "(POST /job/v1/jobs/{id}/bind-only). Counsel and ops need Erra ACT/HOLD + "
            "Velaru ALLOW/BLOCK in one session export before that write — not two demos, "
            "a Slack thread, and a hope. Ops queue after ALLOW is SOW; the room before ALLOW is live."
        ),
        "buyer": "Carrier ops · counsel · PAS / PolicyCenter implementors · MGA authority desks",
        "enemy": [
            "Fourth-deploy marketing",
            "Action OS splash before a pilot weld",
            "Proof-only when the buyer asked for the package",
            "Hidden rail / separate Render cosplay",
        ],
        "one_liner_ads": (
            "Both rails clear before bind. One export. One verify URL. Then capital may move."
        ),
        "citations": [
            {
                "title": "Guidewire PolicyCenter — bind-only without issue",
                "why": "Irreversible commit exists as a first-class Cloud API write",
                "url": "https://docs.guidewire.com/cloud/is/202603/cloudapibf/cloudAPI/PolicyCenter/job-types/submissions/c_binding_a_submission_without_issuing.html",
            },
            {
                "title": "NAIC / state examination posture — human oversight structural on insurance AI",
                "why": "Pre-bind packet must be inspectable, not tribal knowledge",
            },
            {
                "title": "Agentic insurance ops — cancel risk when controls missing (Gartner-class warning)",
                "why": "Session that forces both rails before money/coverage is the control",
            },
        ],
        "shipped": [
            "Bind Room ~30s session",
            "Chokepoint packs (insurance, hiring, mortgage, court, …)",
            "JSON/TXT export for counsel / PAS",
            "Stranger verify URL",
        ],
        "gaps": [
            "Weakest family voice — must stop sounding like a table of contents",
            "Post-ALLOW ops queue explicitly SOW — do not pretend it's live",
        ],
        "paste_hero": (
            "Did both rails clear before bind?\n"
            "Erra reads the cluster. Velaru proves the gate. "
            "Verra is the room — one export leaves before capital, coverage, or force moves."
        ),
        "paste_nav": "Bind Room · Chokepoints · Verify · Twin SKU · Gate mouth →",
        "paste_not": (
            "Not a fourth deploy. Not Action OS marketing before pilot. "
            "Not Mishara. When they only need proof, lead Velaru — say Verra on call 2."
        ),
    },
    "gate": {
        "name": "Gate",
        "role": "Action OS mouth",
        "question": "Does the irreversible write complete?",
        "voice_line": "Scarcity is the DENY",
        "scarcity": "DENY/DEAD that holds on the welded write — 10 bps register",
        "reflects_engine": True,
        "url": None,
        "market_problem": (
            "Irreversible spend (payout, withdraw, bind-only) still completes on soft-yes "
            "dashboards. Action OS: own permission for any power that needs the door."
        ),
        "buyer": "Operators · carriers · economies · politicians · companies · any entity on the write",
        "enemy": [
            "Soft-yes resurrection",
            "Inventory theater",
            "Timeout as LIVE",
            "Narrative without a halt",
        ],
        "one_liner_ads": (
            "Own the door on irreversible acts. Scarcity is the DENY. CHARGE only."
        ),
        "citations": [
            {
                "title": "Nisaba Action OS formula (shipped)",
                "why": "Company doctrine: serve everybody; DENY is scarcity",
            }
        ],
        "shipped": [
            "/v1/act",
            "Register + weld",
            "Action OS + scorecard",
            "License fuse · restraint",
        ],
        "paste_hero": None,
    },
    "mishara": {
        "name": "Mishara",
        "role": "consumer harm path",
        "question": "Was a person harmed?",
        "voice_line": "When the act already hurt someone",
        "scarcity": "Cryptographic receipt + demand path for the harmed human — not a GP register",
        "reflects_engine": True,
        "url": "https://mishara.onrender.com",
        "market_problem": (
            "FCRA / ECOA adverse action, AI tenant/credit screening, NYC Local Law 144 hiring tools, "
            "and EU AI Act high-risk employment logs create duties — but consumers still leave "
            "with no independent receipt and no demand letter when an AI denied them. "
            "LL144 is mostly agency enforcement; individuals still need artifacts for NYCHRL / Title VII / FCRA claims."
        ),
        "buyer": "Harmed individuals · advocates · workers (not the money path)",
        "enemy": [
            "Action OS cosplay on a consumer door",
            "Vague 'the model said no' without a receipt",
            "Platform grievance forms that never produce verify URLs",
        ],
        "one_liner_ads": (
            "AI denied you. Get the receipt. Know your rights. Demand in writing."
        ),
        "citations": [
            {
                "title": "FCRA §1681m — adverse action notice for consumer reports (housing/credit/employment)",
                "why": "Systemic failure: denials without CRA name, dispute rights, free report window",
            },
            {
                "title": "ECOA / Reg B — specific principal reasons; black-box is not a defense (CFPB circulars)",
                "why": "Consumers need specific reasons; Mishara packages the independent record",
            },
            {
                "title": "CFPB Circular 2026-03 class — AI underwriting still needs specific adverse action reasons",
                "why": "Lenders cannot hide behind uninterpretable models",
            },
            {
                "title": "NYC Local Law 144 AEDT — bias audit + notice; no private right of action alone",
                "why": "Gap: consumers need receipts to leverage NYCHRL / Title VII / DCWP complaints",
                "url": "https://www.nyc.gov/site/dca/about/automated-employment-decision-tools.page",
            },
            {
                "title": "EU AI Act Art 12 + Annex III employment high-risk (Aug 2026)",
                "why": "Logging duties exist; individual still lacks a stranger-held receipt",
            },
        ],
        "shipped": [
            "Harm classify via Velaru",
            "Cryptographic receipt + verify link",
            "Rights guidance + demand letter",
            "Anonymous pattern aggregation",
        ],
        "gaps": [
            "Attorney referral still coming",
            "Economics intentionally thin — rights path not GP",
        ],
        "paste_hero": (
            "Was a person harmed?\n"
            "When an AI decision already hurt you — hiring, housing, credit, insurance — "
            "get a Velaru-signed receipt, plain-English rights, and a demand letter. "
            "Not the Action OS. The human door."
        ),
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def voice(slug: str, public_url: str = "") -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    raw = VOICES[slug]
    out = dict(raw)
    if slug == "gate":
        out["url"] = base or out.get("url")
    out["id"] = slug
    out["engine"] = ENGINE
    out["evaluated_at"] = _now()
    out["page"] = f"{base}/family/{slug}" if base else None
    out["manifest"] = f"{base}/.well-known/family/{slug}.json" if base else None
    return out


def organs(public_url: str = "") -> list[dict[str, Any]]:
    """Gate/Nisaba organs — not product siblings. Family length stays 5."""
    try:
        from gate import unison as unison_mod
    except ImportError:
        import unison as unison_mod

    base = (public_url or "").rstrip("/")
    rows = unison_mod.organs()
    for row in rows:
        row["unison"] = f"{base}/unison" if base else "/unison"
    return rows


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    family = [voice(k, base) for k in ("velaru", "erra", "verra", "gate", "mishara")]
    return {
        "spec": SPEC,
        "name": "Nisaba family voices",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "thesis": (
            "Reflect Velaru as the engine. Keep own gravity. "
            "Bite real markets. Twin chrome is not a voice."
        ),
        "engine": ENGINE,
        "family": family,
        "organs": organs(base),
        "organs_are_not_siblings": True,
        "marks": [
            {
                "id": "gate_conformant",
                "name": "Gate Conformant",
                "role": "cert / franchise mark on Gate",
                "not_a_sibling": True,
                "not_a_homepage": True,
                "attaches_to": ["gate", "velaru"],
                "sellable": False,
                "rent": True,
                "status": "planned_post_stranger_prove",
                "ghost": "DENY",
                "page": f"{base}/conformant" if base else "/conformant",
                "manifest": f"{base}/.well-known/conformant.json" if base else None,
            }
        ],
        "marks_are_not_siblings": True,
        "weakest_voice_fix": {
            "priority": ["verra", "erra", "mishara"],
            "action": "Paste hero/nav/not blocks into sibling deploys; keep Gate as Action OS money door",
        },
        "research_pass": {
            "erra": "Reinsurance / EIOPA / prudential LLM assurance / explainable UW AI",
            "verra": "PolicyCenter bind-only irreversibility / pre-bind counsel packet",
            "mishara": "FCRA/ECOA adverse action / LL144 gap / EU Art 12 individual artifact",
        },
        "links": {
            "scorecard": f"{base}/.well-known/scorecard.json",
            "action_os": f"{base}/.well-known/action-os.json",
            "unison": f"{base}/.well-known/unison.json",
            "conformant": f"{base}/.well-known/conformant.json",
            "page": f"{base}/family",
        },
        "page": f"{base}/family",
        "their_production": False,
        "gatekeep": "Family voice research. Ours.",
    }


def paste_pack(slug: str) -> str:
    """Plain-text pack for sibling site owners."""
    v = VOICES[slug]
    lines = [
        f"# {v['name']} voice pack — Nisaba family voices v1",
        f"Question: {v['question']}",
        f"Voice: {v['voice_line']}",
        f"Scarcity: {v['scarcity']}",
        "",
        "## Hero",
        v.get("paste_hero") or v["one_liner_ads"],
        "",
        "## Ads",
        v["one_liner_ads"],
        "",
        "## Market problem",
        v["market_problem"],
        "",
        "## Buyer",
        v["buyer"],
        "",
        "## Enemy",
        *[f"- {e}" for e in v["enemy"]],
        "",
        "## Not",
        v.get("paste_not") or "See family manifest.",
        "",
        "## Citations",
    ]
    for c in v.get("citations") or []:
        lines.append(f"- {c['title']} — {c['why']}")
    lines.extend(["", "## Engine (reflect, don't clone)", *[f"- {x}" for x in ENGINE["inherits"]]])
    return "\n".join(lines) + "\n"
