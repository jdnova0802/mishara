"""Colorado C.R.S. 6-1-1703(3) impact-assessment packet.

Clerk, not remaining. Not legal advice. A third party contracted by the
deployer may complete this file; the deployer keeps it three years after
final deployment. SB25B-004 moved the duty to 30 June 2026.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timezone
from typing import Any

SPEC = "nisaba-co-6101703-v1"
STATUTE = "C.R.S. 6-1-1703"
EFFECTIVE = "2026-06-30"

CONSEQUENTIAL = (
    "education",
    "employment",
    "lending",
    "government_service",
    "healthcare",
    "housing",
    "insurance",
    "legal",
)

KINDS = ("initial", "annual", "modification")

# Map form keys → statute cites. Empty values fail closed.
REQUIRED = (
    ("deployer_name", "6-1-1701(6) deployer"),
    ("system_name", "6-1-1703(3) high-risk system"),
    ("consequential_decision", "6-1-1701(3) consequential decision"),
    ("purpose", "6-1-1703(3)(b)(I) purpose"),
    ("intended_uses", "6-1-1703(3)(b)(I) intended use cases"),
    ("deployment_context", "6-1-1703(3)(b)(I) deployment context"),
    ("benefits", "6-1-1703(3)(b)(I) benefits"),
    ("discrimination_risks", "6-1-1703(3)(b)(II) known or reasonably foreseeable risks"),
    ("discrimination_mitigations", "6-1-1703(3)(b)(II) steps taken to mitigate"),
    ("inputs", "6-1-1703(3)(b)(III) input categories"),
    ("outputs", "6-1-1703(3)(b)(III) outputs"),
    ("metrics_limitations", "6-1-1703(3)(b)(V) metrics and known limitations"),
    ("transparency", "6-1-1703(3)(b)(VI) transparency / consumer disclosure"),
    ("monitoring_safeguards", "6-1-1703(3)(b)(VII) post-deployment monitoring and user safeguards"),
    ("discrimination_review", "6-1-1703(3)(g) annual review that the system is not causing algorithmic discrimination"),
    ("kind", "6-1-1703(3)(a) initial / annual / modification"),
    ("assessment_date", "packet date"),
    ("third_party_name", "6-1-1703(3) third party contracted by the deployer (or the deployer if self-completed)"),
)


def _s(v: Any) -> str:
    return str(v or "").strip()


def validate(src: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key, cite in REQUIRED:
        if not _s(src.get(key)):
            errors.append(f"missing: {cite}")
    kind = _s(src.get("kind")).lower()
    if kind and kind not in KINDS:
        errors.append("kind must be initial, annual, or modification")
    decision = _s(src.get("consequential_decision")).lower()
    if decision and decision not in CONSEQUENTIAL:
        errors.append("consequential_decision must be one of: " + ", ".join(CONSEQUENTIAL))
    if _s(src.get("used_customization_data")).lower() in {"1", "true", "yes", "on"}:
        if not _s(src.get("customization_data")):
            errors.append("missing: 6-1-1703(3)(b)(IV) customization data categories")
    if kind == "modification" and not _s(src.get("use_vs_developer_intent")):
        errors.append("missing: 6-1-1703(3)(c) consistency with or variance from developer intended uses")
    date_s = _s(src.get("assessment_date"))
    if date_s:
        try:
            date.fromisoformat(date_s)
        except ValueError:
            errors.append("assessment_date must be YYYY-MM-DD")
    return errors


def build_packet(src: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    errors = validate(src)
    if errors:
        return None, errors

    kind = _s(src.get("kind")).lower()
    customized = _s(src.get("used_customization_data")).lower() in {"1", "true", "yes", "on"}
    sections = [
        {
            "cite": "6-1-1703(3)(b)(I)",
            "title": "Purpose, intended uses, context, benefits",
            "purpose": _s(src.get("purpose")),
            "intended_uses": _s(src.get("intended_uses")),
            "deployment_context": _s(src.get("deployment_context")),
            "benefits": _s(src.get("benefits")),
        },
        {
            "cite": "6-1-1703(3)(b)(II)",
            "title": "Algorithmic discrimination risks and mitigations",
            "risks": _s(src.get("discrimination_risks")),
            "mitigations": _s(src.get("discrimination_mitigations")),
        },
        {
            "cite": "6-1-1703(3)(b)(III)",
            "title": "Inputs and outputs",
            "inputs": _s(src.get("inputs")),
            "outputs": _s(src.get("outputs")),
        },
        {
            "cite": "6-1-1703(3)(b)(IV)",
            "title": "Customization data",
            "used": customized,
            "categories": _s(src.get("customization_data")) if customized else "Not used to customize.",
        },
        {
            "cite": "6-1-1703(3)(b)(V)",
            "title": "Performance metrics and known limitations",
            "text": _s(src.get("metrics_limitations")),
        },
        {
            "cite": "6-1-1703(3)(b)(VI)",
            "title": "Transparency measures",
            "text": _s(src.get("transparency")),
        },
        {
            "cite": "6-1-1703(3)(b)(VII)",
            "title": "Post-deployment monitoring and user safeguards",
            "text": _s(src.get("monitoring_safeguards")),
        },
        {
            "cite": "6-1-1703(3)(g)",
            "title": "Review that the system is not causing algorithmic discrimination",
            "text": _s(src.get("discrimination_review")),
        },
    ]
    if kind == "modification":
        sections.append(
            {
                "cite": "6-1-1703(3)(c)",
                "title": "Use versus developer intended uses",
                "text": _s(src.get("use_vs_developer_intent")),
            }
        )

    packet: dict[str, Any] = {
        "spec": SPEC,
        "statute": STATUTE,
        "effective_date": EFFECTIVE,
        "not_legal_advice": True,
        "not_remaining": True,
        "not_may": True,
        "built_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "kind": kind,
        "assessment_date": _s(src.get("assessment_date")),
        "deployer_name": _s(src.get("deployer_name")),
        "system_name": _s(src.get("system_name")),
        "comparable_set": _s(src.get("comparable_set")),
        "consequential_decision": _s(src.get("consequential_decision")).lower(),
        "third_party_name": _s(src.get("third_party_name")),
        "other_law_similar": _s(src.get("other_law_similar")),
        "retention": (
            "Deployer shall maintain this assessment, all records concerning it, "
            "and all prior assessments for at least three years following the "
            "final deployment of the high-risk artificial intelligence system "
            "(6-1-1703(3)(f))."
        ),
        "ag_demand": (
            "On and after 30 June 2026 the Attorney General may require the "
            "deployer or contracted third party to disclose this assessment "
            "within ninety days (6-1-1703(9); date as amended by SB25B-004)."
        ),
        "sections": sections,
        "evidence_index": [
            item
            for item in (
                _s(src.get("evidence_1")),
                _s(src.get("evidence_2")),
                _s(src.get("evidence_3")),
            )
            if item
        ],
    }
    raw = json.dumps(packet, sort_keys=True, separators=(",", ":")).encode("utf-8")
    packet["packet_sha256"] = hashlib.sha256(raw).hexdigest()
    return packet, []


def packet_markdown(packet: dict[str, Any]) -> str:
    lines = [
        f"# Impact assessment — {packet['system_name']}",
        "",
        f"**Statute:** {packet['statute']} (effective {packet['effective_date']}).",
        f"**Kind:** {packet['kind']}. **Date:** {packet['assessment_date']}.",
        f"**Deployer:** {packet['deployer_name']}.",
        f"**Third party (or self):** {packet['third_party_name']}.",
        f"**Consequential decision:** {packet['consequential_decision']}.",
        f"**SHA-256:** `{packet['packet_sha256']}`",
        "",
        "Draft / not legal advice. Completing this form does not sell remaining, "
        "does not sell may, and does not bind the State. The deployer keeps the file.",
        "",
    ]
    if packet.get("comparable_set"):
        lines += [f"**Comparable set (6-1-1703(3)(d)):** {packet['comparable_set']}", ""]
    if packet.get("other_law_similar"):
        lines += [f"**Other-law assessment (6-1-1703(3)(e)):** {packet['other_law_similar']}", ""]
    for sec in packet["sections"]:
        lines.append(f"## {sec['cite']} — {sec['title']}")
        for k, v in sec.items():
            if k in {"cite", "title"}:
                continue
            lines.append(f"- **{k}:** {v}")
        lines.append("")
    lines += ["## Evidence index", ""]
    if packet["evidence_index"]:
        for i, item in enumerate(packet["evidence_index"], 1):
            lines.append(f"{i}. {item}")
    else:
        lines.append("(none listed)")
    lines += ["", "## Retention", packet["retention"], "", "## AG demand", packet["ag_demand"], ""]
    return "\n".join(lines) + "\n"
