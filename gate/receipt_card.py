"""Counsel-forwardable halt object and no-login receipt preview.

Buyer HTML/PNG never mention their_production. Museum hops stay labeled museum.
"""
from __future__ import annotations

import hashlib
import struct
import zlib
from typing import Any

try:
    from gate import db
except ImportError:
    import db

SPEC = "gate-receipt-card-v1"
OG_WIDTH = 1200
OG_HEIGHT = 630
_ALLOW = {"AUTHORIZE", "GO", "ALLOW", "LIVE", "CLEAR", "PASS"}
_BLOCK = {"DECLINE", "BLOCK", "DENY", "DENIED", "DEAD", "NO_GO", "HALT", "NO"}


def short_hash(value: str | None) -> str:
    text = (value or "").strip()
    if len(text) <= 18:
        return text or "—"
    return text[:10] + "…" + text[-6:]


def word_for_row(row: dict | None) -> str:
    row = row if isinstance(row, dict) else {}
    decision = (row.get("decision") or "").strip().upper()
    hop = row.get("hop") if isinstance(row.get("hop"), dict) else {}
    clock = hop.get("clock") if isinstance(hop.get("clock"), dict) else {}
    if clock.get("disposition") == "open":
        due = clock.get("due_at")
        if isinstance(due, str) and due:
            try:
                from datetime import datetime, timezone

                text = due[:-1] + "+00:00" if due.endswith("Z") else due
                parsed = datetime.fromisoformat(text)
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                if datetime.now(timezone.utc) > parsed:
                    return "LATE"
            except ValueError:
                pass
    if decision in _ALLOW:
        return "AUTHORIZE"
    if decision in _BLOCK:
        return "BLOCK"
    if decision in {"HOLD", "PENDING", "OPEN", "IN_FLIGHT"}:
        return "HOLDS"
    return "HOLDS" if row.get("receipt_hash") else "MISSING"


def counsel_text(
    *,
    word: str,
    event_id: str,
    verify_url: str | None,
    public_url: str,
    museum: bool = True,
) -> str:
    base = (public_url or "").rstrip("/")
    lines = [
        "Gate halt — forward this object, not a screenshot.",
        "Museum hop. Not a production weld." if museum else "Signed receipt.",
        "",
        word,
        f"event_id: {event_id}",
        f"verify: {verify_url or '—'}",
        f"proof: {base}/.well-known/receipt/{event_id}/proof.json",
        f"receipt: {base}/.well-known/receipt/{event_id}.json",
        f"preview: {base}/receipt/{event_id}",
    ]
    return "\n".join(lines) + "\n"


def counsel_payload(
    *,
    word: str,
    event_id: str,
    verify_url: str | None,
    public_url: str,
    museum: bool = True,
) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    body = {
        "spec": SPEC,
        "word": word,
        "event_id": event_id,
        "verify_url": verify_url,
        "proof": f"{base}/.well-known/receipt/{event_id}/proof.json",
        "receipt": f"{base}/.well-known/receipt/{event_id}.json",
        "preview": f"{base}/receipt/{event_id}",
        "text": counsel_text(
            word=word,
            event_id=event_id,
            verify_url=verify_url,
            public_url=base,
            museum=museum,
        ),
        "check_url": f"{base}/?hop={event_id}",
        "museum": bool(museum),
    }
    return body


def stamp_museum_hop(data: dict, *, fuse_id: str, public_url: str) -> dict:
    """Mint a Gate receipt for a public demo hop so counsel/OG/homepage can use the id."""
    hop_in = data.get("hop") if isinstance(data.get("hop"), dict) else data
    verify = None
    if isinstance(hop_in, dict):
        url = hop_in.get("verify_url") or hop_in.get("restraint_permalink")
        if isinstance(url, str) and url.strip():
            verify = url.strip()
    halt = bool(
        data.get("halt")
        or (isinstance(hop_in, dict) and hop_in.get("halt"))
        or data.get("verdict") is False
        or (isinstance(data.get("bound_answer"), dict) and data["bound_answer"].get("no"))
    )
    word = "BLOCK" if halt else "HOLD"
    stamp_hop = {
        "state": (hop_in or {}).get("state") if isinstance(hop_in, dict) else data.get("state"),
        "halt": halt,
        "verdict": False if halt else True,
        "demo": True,
        "museum": True,
    }
    event_id = db.record_bind_event(
        fuse_id=fuse_id,
        job_id="demo:hop",
        decision="BLOCK" if halt else "HOLD",
        acted=False,
        verify_url=verify,
        hop=stamp_hop,
    )
    counsel = counsel_payload(
        word=word,
        event_id=event_id,
        verify_url=verify,
        public_url=public_url,
        museum=True,
    )
    data["event_id"] = event_id
    data["decision"] = "BLOCK" if halt else "HOLD"
    data["counsel"] = counsel
    data["check_url"] = counsel["check_url"]
    return data


def og_fields(row: dict, *, public_url: str) -> dict[str, str]:
    event_id = row.get("id") or ""
    word = word_for_row(row)
    digest = short_hash(row.get("receipt_hash"))
    base = (public_url or "").rstrip("/")
    title = f"{word} · {digest}"
    description = "Receipt anyone can open. No login."
    if is_museum_row(row):
        description = "Museum hop. Receipt anyone can open. Not a production weld."
    return {
        "title": title,
        "description": description,
        "url": f"{base}/receipt/{event_id}",
        "image": f"{base}/receipt/{event_id}/og.png",
        "canonical": f"{base}/.well-known/receipt/{event_id}.json",
        "word": word,
        "hash_short": digest,
    }


def is_museum_row(row: dict | None) -> bool:
    row = row if isinstance(row, dict) else {}
    hop = row.get("hop") if isinstance(row.get("hop"), dict) else {}
    fuse = (row.get("fuse_id") or "").strip()
    return fuse == "fuse_velaru_drill" or bool(hop.get("demo") or hop.get("museum") or row.get("demo"))


def _glyph_rows(ch: str) -> list[int]:
    table = {
        " ": [0, 0, 0, 0, 0, 0, 0],
        "A": [0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
        "B": [0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E],
        "C": [0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E],
        "D": [0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E],
        "E": [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F],
        "F": [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10],
        "H": [0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
        "I": [0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x1F],
        "K": [0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11],
        "L": [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F],
        "N": [0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11],
        "O": [0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
        "R": [0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11],
        "S": [0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E],
        "T": [0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04],
        "U": [0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
        "W": [0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11],
        "Z": [0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F],
        "0": [0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E],
        "1": [0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E],
        "2": [0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F],
        "3": [0x1F, 0x01, 0x02, 0x06, 0x01, 0x11, 0x0E],
        "4": [0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02],
        "5": [0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E],
        "6": [0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E],
        "7": [0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08],
        "8": [0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E],
        "9": [0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C],
        "-": [0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00],
        "·": [0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00],
        ".": [0x00, 0x00, 0x00, 0x00, 0x00, 0x06, 0x06],
        "…": [0x00, 0x00, 0x00, 0x00, 0x15, 0x00, 0x00],
    }
    return table.get(ch.upper() if ch.isalpha() else ch, table["·"])


def _fill(buf: bytearray, width: int, color: tuple[int, int, int]) -> None:
    r, g, b = color
    for i in range(0, len(buf), 3):
        buf[i] = r
        buf[i + 1] = g
        buf[i + 2] = b


def _blit_text(
    buf: bytearray,
    width: int,
    x: int,
    y: int,
    text: str,
    color: tuple[int, int, int],
    scale: int,
) -> None:
    r, g, b = color
    cursor = x
    for ch in text:
        rows = _glyph_rows(ch)
        for gy, bits in enumerate(rows):
            for gx in range(5):
                if bits & (1 << (4 - gx)):
                    for dy in range(scale):
                        for dx in range(scale):
                            px = cursor + gx * scale + dx
                            py = y + gy * scale + dy
                            if 0 <= px < width and 0 <= py < OG_HEIGHT:
                                idx = (py * width + px) * 3
                                buf[idx] = r
                                buf[idx + 1] = g
                                buf[idx + 2] = b
        cursor += 6 * scale


def _png_rgb(width: int, height: int, rgb: bytes) -> bytes:
    raw = bytearray()
    row = width * 3
    for y in range(height):
        raw.append(0)
        start = y * row
        raw.extend(rgb[start : start + row])
    compressed = zlib.compress(bytes(raw), 9)

    def chunk(tag: bytes, data: bytes) -> bytes:
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", compressed) + chunk(b"IEND", b"")


def render_og_png(*, word: str, hash_short: str, museum: bool) -> bytes:
    buf = bytearray(OG_WIDTH * OG_HEIGHT * 3)
    _fill(buf, OG_WIDTH, (10, 11, 15))
    label = "MUSEUM HOP" if museum else "GATE RECEIPT"
    _blit_text(buf, OG_WIDTH, 72, 90, label, (139, 146, 168), 4)
    tone = (248, 113, 113) if word == "BLOCK" else (74, 222, 128) if word in ("HOLDS", "AUTHORIZE") else (251, 191, 36)
    _blit_text(buf, OG_WIDTH, 72, 200, word, tone, 10)
    _blit_text(buf, OG_WIDTH, 72, 400, hash_short, (232, 234, 240), 5)
    return _png_rgb(OG_WIDTH, OG_HEIGHT, bytes(buf))


def empty_root_hex() -> str:
    return hashlib.sha256(b"gate-evidence-empty").hexdigest()
