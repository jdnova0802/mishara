"""Velaru Colorado assessment clerk. Not Mishara. Not Gate."""
from __future__ import annotations

import os
import secrets

from flask import Flask, jsonify, render_template, request

from packet import CONSEQUENTIAL, KINDS, SPEC, build_packet, packet_markdown

app = Flask(__name__, template_folder="templates")
app.config["SECRET_KEY"] = os.getenv("ASSESSMENT_SECRET_KEY", secrets.token_hex(24))
CONTACT = os.getenv("ASSESSMENT_CONTACT_EMAIL", "hello@velaru.xyz")


@app.get("/")
def index():
    return render_template(
        "index.html",
        consequential=CONSEQUENTIAL,
        kinds=KINDS,
        contact=CONTACT,
        spec=SPEC,
    )


@app.get("/health")
def health():
    return jsonify(
        {
            "service": "colorado-assessment",
            "spec": SPEC,
            "statute": "C.R.S. 6-1-1703",
            "effective": "2026-06-30",
            "not_legal_advice": True,
        }
    )


@app.post("/packet")
def packet():
    src = request.get_json(silent=True) or request.form.to_dict()
    packet_obj, errors = build_packet(src)
    if errors:
        return jsonify({"ok": False, "errors": errors}), 400
    assert packet_obj is not None
    md = packet_markdown(packet_obj)
    return jsonify({"ok": True, "packet": packet_obj, "markdown": md})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5002")), debug=False)
