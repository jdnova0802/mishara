"""Pip — standalone origin. No Gate/Velaru/Nisaba identity."""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile

from flask import Flask, Response, abort, jsonify, request, send_from_directory

HERE = os.path.dirname(os.path.abspath(__file__))
MAX_UPLOAD = 12 * 1024 * 1024
FFMPEG = shutil.which("ffmpeg") or "ffmpeg"

app = Flask(__name__, static_folder=None)


@app.after_request
def csp(resp: Response) -> Response:
    resp.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' blob: data:; "
        "media-src 'self' blob:; "
        "connect-src 'self'; "
        "worker-src 'self' blob:; "
        "frame-ancestors 'none'; "
        "base-uri 'self'"
    )
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Referrer-Policy"] = "no-referrer"
    return resp


@app.get("/")
def index():
    return send_from_directory(HERE, "index.html")


@app.get("/health")
def health():
    has_ff = shutil.which("ffmpeg") is not None
    return jsonify({"ok": True, "mp4": has_ff})


@app.post("/encode")
def encode_mp4():
    """WebM (or other) in → H.264 AAC MP4 out. No shell. Caps size and duration."""
    if shutil.which("ffmpeg") is None:
        return jsonify({"error": "ffmpeg_missing"}), 501
    length = request.content_length
    if length is not None and length > MAX_UPLOAD:
        abort(413)
    data = request.get_data(cache=False)
    if not data or len(data) > MAX_UPLOAD:
        abort(413)
    with tempfile.TemporaryDirectory(prefix="pipenc-") as td:
        src = os.path.join(td, "in.bin")
        dst = os.path.join(td, "out.mp4")
        with open(src, "wb") as f:
            f.write(data)
        cmd = [
            FFMPEG,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            src,
            "-t",
            "16",
            "-c:v",
            "libx264",
            "-vf",
            "format=yuv420p",
            "-pix_fmt",
            "yuv420p",
            "-preset",
            "veryfast",
            "-crf",
            "23",
            "-r",
            "30",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-ac",
            "2",
            "-movflags",
            "+faststart",
            dst,
        ]
        try:
            subprocess.run(cmd, check=True, timeout=45, capture_output=True)
        except subprocess.CalledProcessError:
            # Retry video-only if the capture had no usable audio.
            silent = [
                FFMPEG,
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                src,
                "-t",
                "16",
                "-c:v",
                "libx264",
                "-vf",
                "format=yuv420p",
                "-pix_fmt",
                "yuv420p",
                "-preset",
                "veryfast",
                "-crf",
                "23",
                "-r",
                "30",
                "-an",
                "-movflags",
                "+faststart",
                dst,
            ]
            try:
                subprocess.run(silent, check=True, timeout=45, capture_output=True)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                return jsonify({"error": "encode_failed"}), 422
        except subprocess.TimeoutExpired:
            return jsonify({"error": "encode_timeout"}), 504
        if not os.path.isfile(dst) or os.path.getsize(dst) < 32:
            return jsonify({"error": "encode_empty"}), 422
        with open(dst, "rb") as f:
            out = f.read()
    return Response(out, mimetype="video/mp4")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5077")))
