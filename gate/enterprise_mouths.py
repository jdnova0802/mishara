"""Enterprise atomic gaps — Nvidia / IBM / Microsoft (on-card map).

NOT sister companies. Same mouth: where a claim or agent tool can authorize
an irreversible write without Clear / stranger-openable may.

Surfaces:
  GET /.well-known/enterprise-mouths.json
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-enterprise-mouths-v0"
FIRM = "Nisaba LLC"
CARD = (
    "On-card opportunity map for Primary Gate + H1 diligence. "
    "Does not rename the firm. No bounty gym."
)


def nvidia() -> dict[str, Any]:
    return {
        "firm": "NVIDIA",
        "stack_atom": "GPU/runtime factory where inference + tool calls become action",
        "verified_shaped": [
            {
                "gap": "Inference-as-oracle",
                "atom": "Model output treated as authority for the next tool write",
                "evidence": "NIM / Agent Toolkit / Secure Agent Workspace exist because prompt≠bound authority",
                "nisaba_angle": "Classify inference claim via Oracle Compiler; deny leave on UNSIGNED/ungrounded",
            },
            {
                "gap": "Tool-call mouth without stranger Clear",
                "atom": "Delegation/sandbox can exist while irreversible tool still lacks reconstructable may",
                "evidence": "OpenShell / SAW: credential proxy + signed policies — still enterprise-local proof",
                "nisaba_angle": "Mouth map: which tool classes are irreversible; Bind-style stranger receipt",
            },
            {
                "gap": "Four-identity chain breaks at act",
                "atom": "User/workspace/agent/call identities attributed ≠ Clear before write",
                "evidence": "SAW four-identity + delegation record model",
                "nisaba_angle": "Prefinality: delegation LIVE ∧ Clear at T or NO_GO",
            },
        ],
        "buildables": [
            "inference_oracle_gate",
            "tool_class_irreversibility_map",
            "delegation_clear_bind",
        ],
        "h1_fit": "medium — sell to enterprises running NVIDIA agent factories on payout/ops tools",
        "primary_fit": "high — agent mortality / exclusive door on tool plane",
    }


def ibm() -> dict[str, Any]:
    return {
        "firm": "IBM",
        "stack_atom": "Z as settlement truth + cloud/AI as subledger/oracle for agents",
        "verified_shaped": [
            {
                "gap": "Dual-ledger hybrid (Z vs cloud copy)",
                "atom": "Synchronized cloud/lakehouse copy is not the irreversible post on Z",
                "evidence": "Data Gate / watsonx sync patterns; agents powered from Z data off-platform",
                "nisaba_angle": "Dual-Ledger Clear: owner/action on Z ⇔ copy used as may",
            },
            {
                "gap": "Conversational/agent layer over deterministic COBOL",
                "atom": "AI triage must not become silent write authority on settlement jobs",
                "evidence": "Symphony + Granite demos: AI reads breaks; risk is when agents gain write tools",
                "nisaba_angle": "Oracle class on agent recommendations; write stays fail-closed",
            },
            {
                "gap": "Agentforce / zero-copy activation",
                "atom": "Mainframe facts feed external agents that can act in CRM/payout worlds",
                "evidence": "IBM Z + Salesforce Data Cloud zero-copy agent announcements",
                "nisaba_angle": "Mouth: Z-oracle → external irreversible act without Clear",
            },
        ],
        "buildables": [
            "z_dual_ledger_clear",
            "settlement_job_write_fuse",
            "cross_platform_agent_mouth_map",
        ],
        "h1_fit": "high for banks/carriers on Z leave paths",
        "primary_fit": "high — weld on irreversible Z/post paths",
    }


def microsoft() -> dict[str, Any]:
    return {
        "firm": "Microsoft",
        "stack_atom": "Copilot/Azure agents with tool calling inside Entra-governed enterprises",
        "verified_shaped": [
            {
                "gap": "FAIL_OPEN tool gate (1s timeout → allow)",
                "atom": "Missing Clear treated as may",
                "evidence": (
                    "Copilot Studio external threat detection: if no allow/block within ~1s, "
                    "default proceeds to allow tool execution"
                ),
                "nisaba_angle": "Oracle Compiler FAIL_OPEN — primary commercial exhibit",
                "severity": "critical",
            },
            {
                "gap": "Prompt/policy may vs deterministic tool fuse",
                "atom": "Instructions are not stranger-openable halt",
                "evidence": "Human approval-for-tool feature shipping because prompt guardrails insufficient",
                "nisaba_angle": "Bind irreversible tools to Clear receipt, not prompt text",
            },
            {
                "gap": "Entra identity ≠ act Clear",
                "atom": "Agent identity / Conditional Access can be live while write lacks may",
                "evidence": "Agent 365 / Entra agent identities + tool invocation telemetry",
                "nisaba_angle": "Prefinality hop before payment/ticket/close/delete tools",
            },
            {
                "gap": "Computer-use / hosted PC act surface",
                "atom": "GUI actuation is irreversible write without API mouth visibility",
                "evidence": "Copilot Studio computer-use tool on Cloud PC / BYO",
                "nisaba_angle": "Mouth diligence on actuation class; fail-closed on unmapped acts",
            },
        ],
        "buildables": [
            "fail_open_timeout_fuse",
            "copilot_tool_clear_adapter",
            "entra_agent_act_receipt",
        ],
        "h1_fit": "high — enterprise security / payments / ops tool mouths",
        "primary_fit": "very high — external security provider slot wants fail-closed Clear",
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "firm": FIRM,
        "card": CARD,
        "job": "Atomic mouths in hyperscaler / enterprise AI stacks that authorize irreversible writes",
        "compilers": {
            "finality": "gate-finality-compiler-v0",
            "oracle": "gate-oracle-compiler-v0",
        },
        "targets": {
            "nvidia": nvidia(),
            "ibm": ibm(),
            "microsoft": microsoft(),
        },
        "ranking_note": (
            "Microsoft FAIL_OPEN (timeout→allow) is the cleanest public exhibit of "
            "write-without-may. IBM is dual-ledger+agent. NVIDIA is inference/tool factory."
        ),
        "urls": {
            "well_known": f"{base}/.well-known/enterprise-mouths.json",
            "oracle_compiler": f"{base}/.well-known/oracle-compiler.json",
            "finality_compiler": f"{base}/.well-known/finality-compiler.json",
            "diligence": f"{base}/diligence",
        },
        "not": [
            "Not a sister company",
            "Not a bounty / pentest gym",
            "Not partnership theater — mouths only",
        ],
    }
