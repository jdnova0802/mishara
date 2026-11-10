"""Item 99 — strip/escape agent-authored reason and chain text before render."""
from __future__ import annotations

import html
import re
from typing import Any

try:
    from markupsafe import Markup, escape
except ImportError:  # pragma: no cover
    Markup = str  # type: ignore[misc, assignment]

    def escape(s: Any) -> str:  # type: ignore[misc]
        return html.escape(str(s), quote=True)

SPEC = "gate-agent-text-v1"
_TAG = re.compile(r"<[^>]*>")
_JS = re.compile(r"javascript:", re.I)
_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def strip_agent(value: Any, *, limit: int = 2000) -> str:
    """Plain text only. Tags and javascript: URLs are removed, not rendered."""
    if value is None:
        return ""
    s = html.unescape(str(value))
    s = _TAG.sub("", s)
    s = _JS.sub("", s)
    s = _CTRL.sub("", s)
    return s.strip()[:limit]


def html_agent(value: Any) -> Markup:
    """Jinja-safe HTML for agent-authored strings."""
    return escape(strip_agent(value))


def walk(obj: Any) -> Any:
    """Sanitize reason/chain-shaped fields in a nested payload."""
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            key = str(k).lower()
            if key in {
                "reason",
                "reason_text",
                "reason_raw",
                "reason_dateline",
                "title",
                "claim",
                "plain",
                "harm_description",
            } and isinstance(v, str):
                out[k] = strip_agent(v)
            else:
                out[k] = walk(v)
        return out
    if isinstance(obj, list):
        return [walk(x) for x in obj]
    return obj
