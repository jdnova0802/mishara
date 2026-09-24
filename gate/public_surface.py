"""Prospect-facing surface hygiene.

Keep their_production as an internal weld truth.
Never announce their_production: false on anything a buyer can curl or open.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any

# Bump when buyer-visible surfaces change (trust / live "last updated").
SURFACE_UPDATED_AT = "2026-09-24T22:30:00+00:00"
SURFACE_UPDATED_LABEL = "24 Sep 2026"
SURFACE_NOTE = (
    "Buyer-facing credibility pass — production-claim hygiene, "
    "branded 404, security headers."
)

_FALSE_FLAG_LINE = re.compile(
    r"^.*their_production\s*(:|=)?\s*false.*$",
    re.IGNORECASE | re.MULTILINE,
)
_FALSE_FLAG_INLINE = re.compile(
    r"their_production\s*:\s*false",
    re.IGNORECASE,
)
_FALSE_FLAG_PHRASE = re.compile(
    r"their_production\s+stays\s+false[^.]*\.?",
    re.IGNORECASE,
)


def surface_clock() -> dict[str, str]:
    return {
        "updated_at": SURFACE_UPDATED_AT,
        "updated_label": SURFACE_UPDATED_LABEL,
        "note": SURFACE_NOTE,
        "served_at": datetime.now(timezone.utc).isoformat(),
    }


def omit_unwelded_production_flag(obj: Any) -> Any:
    """Recursively drop their_production when falsy. Keep when True."""
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for key, value in obj.items():
            if key == "their_production" and not value:
                continue
            out[key] = omit_unwelded_production_flag(value)
        return out
    if isinstance(obj, list):
        return [omit_unwelded_production_flag(item) for item in obj]
    return obj


def scrub_text_demo_smell(text: str) -> str:
    """Remove lines/phrases that announce their_production: false."""
    if not text or "their_production" not in text.lower():
        return text
    cleaned = _FALSE_FLAG_LINE.sub("", text)
    cleaned = _FALSE_FLAG_INLINE.sub("", cleaned)
    cleaned = _FALSE_FLAG_PHRASE.sub("", cleaned)
    # Collapse excess blank lines left by removals
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned


def scrub_json_bytes(raw: bytes) -> bytes | None:
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    scrubbed = omit_unwelded_production_flag(data)
    return json.dumps(scrubbed, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
