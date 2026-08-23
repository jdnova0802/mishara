"""Issue≠Bind Splitter — QuoteRelease is not a bind stop.

Invention (NORTH_STAR foothill): forces PAS to separate QuoteRelease / Issue
from bind-and-issue. QuoteRelease mistaken for bind stop is a real Ghost Bind
haunt — this splitter names the leak on the PolicyCenter weld.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-issue-bind-splitter-v1"
INVENTION = "Issue≠Bind Splitter"
FAMILY = "foothill"

QUOTE_RELEASE = "UWManagerReviewBlocksQuoteRelease"
BINDING_POINT = "Binding"
BLOCKS_BIND = "blocksBind"
REASON_QUOTE_NOT_BIND = "quote_release_not_bind_stop"
REASON_BIND_OK = "blocks_bind_configured"


def evaluate(
    *,
    issue_type: str | None = None,
    blocking_point: str | None = None,
    bind_path: str | None = None,
) -> dict[str, Any]:
    """Split issue semantics from bind semantics."""
    it = (issue_type or "").strip()
    bp = (blocking_point or "").strip()
    path = (bind_path or "").strip().lower()
    quote_only = it == QUOTE_RELEASE or bp.lower() in ("quoterelease", "quote")
    blocks_bind = bp == BINDING_POINT or bp.lower() == BLOCKS_BIND.lower() or "blocksbinding" in bp.lower()
    bind_and_issue = "bind-and-issue" in path
    bind_only = "bind-only" in path or (path.endswith("/bind") if path else False)

    leak = quote_only and not blocks_bind
    verdict = "LEAK" if leak else ("SPLIT_OK" if blocks_bind else "UNCONFIGURED")

    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "verdict": verdict,
        "issue_type": it or None,
        "blocking_point": bp or None,
        "quote_release_only": quote_only,
        "blocks_bind": blocks_bind,
        "bind_path": bind_path,
        "bind_and_issue": bind_and_issue,
        "bind_only": bind_only,
        "leak": leak,
        "reason": REASON_QUOTE_NOT_BIND if leak else (REASON_BIND_OK if blocks_bind else "configure_blocksBind"),
        "detail": (
            "QuoteRelease blocks quote — not bind. Issue type must block Binding (blocksBind)."
            if leak
            else "Issue and bind paths are split correctly."
            if blocks_bind
            else "Configure UW issue with blocking point Binding."
        ),
        "fix": {
            "blocking_point_required": BINDING_POINT,
            "insufficient_issue_type": QUOTE_RELEASE,
            "do_not_wrap_only": "bind-and-issue without bind-only",
        },
        "rule": "QuoteRelease ≠ bind stop. blocksBind on Binding is the weld.",
    }


def attach(plan: dict, *, issue_type: str | None = None, blocking_point: str | None = None) -> dict:
    sw = plan.get("spend_protocol", {}).get("write") if isinstance(plan.get("spend_protocol"), dict) else {}
    path = None
    if isinstance(sw, dict):
        path = sw.get("path")
    elif isinstance(plan.get("next"), dict):
        path = plan["next"].get("path")
    split = evaluate(
        issue_type=issue_type or plan.get("issue_type"),
        blocking_point=blocking_point or plan.get("blocking_point"),
        bind_path=path,
    )
    plan["issue_bind_splitter"] = split
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "QuoteRelease is not a bind stop — split issue from bind-and-issue.",
        "demo": f"POST {base}/demo/pas/issue-bind-splitter",
        "well_known": f"{base}/.well-known/issue-bind-splitter.json",
        "policycenter": f"{base}/v1/pas/policycenter/pre-bind",
        "bind_room": f"{base}/bind-room",
        "north_star": "gate/NORTH_STAR.md#inventions-forge-catalog",
        "posture": "Under coordinators. PolicyCenter weld invention.",
    }
