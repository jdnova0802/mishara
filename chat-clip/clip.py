#!/usr/bin/env python3
"""Paste-file → ≤15s phone-width chat MP4. Hash on last frames only."""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 720, 1280
FPS = 30
MAX_S = 15.0
HASH_S = 1.8
PAD = 36
BUBBLE_MAX = 560
SPEAKER = re.compile(
    r"^(user|you|human|me|assistant|chatgpt|claude|gemini|grok|ai|system|model)\s*[:\-—]\s*",
    re.I,
)
SPEAKER_ONLY = re.compile(
    r"^(user|you|human|me|assistant|chatgpt|claude|gemini|grok|ai|system|model)\s*$",
    re.I,
)
USER_ROLES = {"user", "you", "human", "me"}
FONT_PATH = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")


def parse_transcript(raw: str) -> list[dict]:
    msgs: list[dict] = []
    cur = None
    for line in raw.replace("\r\n", "\n").split("\n"):
        tagged = SPEAKER.match(line)
        if tagged:
            if cur and cur["text"].strip():
                msgs.append(cur)
            cur = {"role": tagged.group(1), "text": line[tagged.end() :]}
            continue
        if SPEAKER_ONLY.match(line.strip()):
            if cur and cur["text"].strip():
                msgs.append(cur)
            cur = {"role": line.strip(), "text": ""}
            continue
        if cur is None:
            cur = {"role": "Assistant", "text": line}
        else:
            cur["text"] += ("\n" if cur["text"] else "") + line
    if cur and cur["text"].strip():
        msgs.append(cur)
    out = []
    for m in msgs:
        text = m["text"].strip()
        if not text:
            continue
        out.append({"user": m["role"].lower() in USER_ROLES, "text": text})
    return out


def wrap(draw: ImageDraw.ImageDraw, font, text: str, max_w: int) -> list[str]:
    lines: list[str] = []
    for para in text.split("\n"):
        words = [w for w in para.split() if w]
        if not words:
            lines.append("")
            continue
        line = words[0]
        for word in words[1:]:
            trial = f"{line} {word}"
            if draw.textlength(trial, font=font) <= max_w:
                line = trial
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines or [""]


def layout(draw, font, msgs):
    line_h, vpad, hpad = 36, 20, 22
    items = []
    inner = BUBBLE_MAX - hpad * 2
    for m in msgs:
        lines = wrap(draw, font, m["text"], inner)
        text_w = max(draw.textlength(l, font=font) for l in lines) if lines else 8
        w = min(BUBBLE_MAX, int(text_w) + hpad * 2)
        h = len(lines) * line_h + vpad * 2
        items.append({**m, "lines": lines, "w": w, "h": h})
    gap = 16
    total = gap + sum(it["h"] + gap for it in items)
    y = max(PAD + 24, H - PAD - 64 - total)
    for it in items:
        it["y"] = y
        it["x"] = W - PAD - it["w"] if it["user"] else PAD
        y += it["h"] + gap
    return items


def round_rect(draw, box, r, fill):
    draw.rounded_rectangle(box, radius=r, fill=fill)


def frame_chat(items, t, appear, font):
    img = Image.new("RGB", (W, H), "#0e0e10")
    draw = ImageDraw.Draw(img)
    line_h, vpad, hpad = 36, 20, 22
    for i, it in enumerate(items):
        start = i * appear
        if t < start:
            continue
        a = min(1.0, (t - start) / 0.22)
        dy = int((1 - a) * 12)
        fill = (47, 111, 235) if it["user"] else (42, 42, 46)
        if a < 1:
            overlay = Image.new("RGB", (W, H), "#0e0e10")
            od = ImageDraw.Draw(overlay)
            round_rect(
                od,
                [it["x"], it["y"] + dy, it["x"] + it["w"], it["y"] + dy + it["h"]],
                22,
                fill,
            )
            ly = it["y"] + dy + vpad
            for line in it["lines"]:
                od.text((it["x"] + hpad, ly), line, font=font, fill="#f4f4f5")
                ly += line_h
            img = Image.blend(img, overlay, a)
            draw = ImageDraw.Draw(img)
        else:
            round_rect(
                draw,
                [it["x"], it["y"], it["x"] + it["w"], it["y"] + it["h"]],
                22,
                fill,
            )
            ly = it["y"] + vpad
            for line in it["lines"]:
                draw.text((it["x"] + hpad, ly), line, font=font, fill="#f4f4f5")
                ly += line_h
    return img


def frame_hash(hexdigest: str, font) -> Image.Image:
    img = Image.new("RGB", (W, H), "#0e0e10")
    draw = ImageDraw.Draw(img)
    label = "sha256:" + hexdigest
    w = draw.textlength(label, font=font)
    draw.text(((W - w) / 2, H / 2 - 10), label, font=font, fill="#c8c8c8")
    return img


def render(raw: str, out: Path) -> tuple[float, str]:
    msgs = parse_transcript(raw)
    if not msgs:
        raise SystemExit("No labeled turns. Start lines with User: or Assistant:")
    hexdigest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    font = ImageFont.truetype(str(FONT_PATH), 28) if FONT_PATH.exists() else ImageFont.load_default()
    hash_font = ImageFont.truetype(str(FONT_PATH), 15) if FONT_PATH.exists() else font
    probe = Image.new("RGB", (W, H))
    items = layout(ImageDraw.Draw(probe), font, msgs[-8:])
    n = max(len(items), 1)
    body_s = min(MAX_S - HASH_S, max(2.4, n * 1.6))
    total_s = body_s + HASH_S
    appear = body_s / n
    with tempfile.TemporaryDirectory() as tmp:
        tdir = Path(tmp)
        frames = int(round(total_s * FPS))
        for i in range(frames):
            t = i / FPS
            if t < body_s:
                im = frame_chat(items, t, appear, font)
            else:
                im = frame_hash(hexdigest, hash_font)
            im.save(tdir / f"{i:05d}.png")
        cmd = [
            "ffmpeg",
            "-y",
            "-framerate",
            str(FPS),
            "-i",
            str(tdir / "%05d.png"),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            "-an",
            str(out),
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    return total_s, hexdigest


def main() -> None:
    p = argparse.ArgumentParser(description="Render a ≤15s chat clip MP4.")
    p.add_argument("transcript", nargs="?", help="Path to transcript text. Stdin if omitted.")
    p.add_argument("-o", "--out", default="chat-clip.mp4")
    args = p.parse_args()
    raw = Path(args.transcript).read_text(encoding="utf-8") if args.transcript else sys.stdin.read()
    seconds, digest = render(raw, Path(args.out))
    print(f"{seconds:.1f}s {args.out}")
    print("sha256:" + digest)


if __name__ == "__main__":
    main()
