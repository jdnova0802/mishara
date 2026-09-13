#!/usr/bin/env python3
"""Point Render mishara service at gate/ and deploy scanner build."""
from __future__ import annotations

import base64
import json
import os
import secrets
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# Prices always read from gate/commerce/ladder.json — never retyped here.
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from gate import commerce as commerce_mod
except ImportError:
    import commerce as commerce_mod  # type: ignore

API = "https://api.render.com/v1"
SERVICE_ID = os.getenv("RENDER_GATE_SERVICE_ID", "srv-dai3n0u1egvs73dbd94g")
GATE_PUBLIC = os.getenv("GATE_PUBLIC_URL", "https://gate.velaru.xyz").rstrip("/")

START = (
    'python -c "from public_url import assert_prod_public; assert_prod_public()" '
    "&& gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60"
)


def _load_dotenv(path: str) -> None:
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k and v:
                os.environ.setdefault(k, v)


def _request(method: str, path: str, body: dict | None = None) -> dict | list:
    key = os.getenv("RENDER_API_KEY", "").strip()
    if not key:
        raise SystemExit("Set RENDER_API_KEY")
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"{API}{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"Render {method} {path} -> {exc.code}: {exc.read().decode()}") from exc


def set_env(service_id: str, key: str, value: str) -> None:
    _request(
        "PUT",
        f"/services/{service_id}/env-vars/{urllib.parse.quote(key, safe='')}",
        {"value": value},
    )
    print(f"  env {key}")


def receipt_keys() -> tuple[str, str]:
    priv = os.getenv("GATE_RECEIPT_PRIVATE_KEY", "").strip()
    pub = os.getenv("GATE_RECEIPT_PUBLIC_KEY", "").strip()
    if priv and pub:
        return priv, pub
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import (
        Encoding,
        NoEncryption,
        PrivateFormat,
        PublicFormat,
    )

    key = Ed25519PrivateKey.generate()
    priv_b = base64.b64encode(
        key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    ).decode()
    pub_b = base64.b64encode(
        key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    ).decode()
    return priv_b, pub_b


def main() -> None:
    for p in (
        os.path.join(os.path.dirname(__file__), ".env"),
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        os.path.expanduser("~/DocumentsVelaru/.env"),
        os.path.join(os.getcwd(), ".env"),
    ):
        _load_dotenv(os.path.abspath(p))

    print(f"PATCH service {SERVICE_ID} rootDir=gate")
    _request(
        "PATCH",
        f"/services/{SERVICE_ID}",
        {
            "name": "gate-api",
            "rootDir": "gate",
            "serviceDetails": {
                "envSpecificDetails": {
                    "buildCommand": "pip install -r requirements.txt",
                    "startCommand": START,
                },
                "healthCheckPath": "/health",
            },
        },
    )

    priv, pub = receipt_keys()
    # Never invent receipt keys into production: if local env lacks them, skip overwrite.
    have_receipts = bool(
        os.getenv("GATE_RECEIPT_PRIVATE_KEY", "").strip()
        and os.getenv("GATE_RECEIPT_PUBLIC_KEY", "").strip()
    )
    fixed = {
        "PYTHON_VERSION": "3.13.0",
        "GATE_DB_PATH": "/var/data/gate.db",
        "VELARU_API_URL": "https://velaru.onrender.com",
        "GATE_DEV_MODE": "0",
        "GATE_ALLOW_LOCAL": "0",
        "GATE_OCSP_TIMEOUT": "5",
        "GATE_INSTALL_SLOTS": "2",
        # Mirror ladder.json into env for ops visibility; runtime also falls back to commerce.
        "GATE_BIND_ROOM_PRICE_LABEL": commerce_mod.price_label("bind_room"),
        "GATE_BIND_ROOM_PRICE_CENTS": str(commerce_mod.price_cents("bind_room")),
        "GATE_DILIGENCE_DEPOSIT_LABEL": commerce_mod.price_label("diligence_deposit"),
        "GATE_DILIGENCE_DEPOSIT_CENTS": str(commerce_mod.price_cents("diligence_deposit")),
        "GATE_REFUSAL_PRICE_LABEL": commerce_mod.price_label("refusal"),
        "GATE_REFUSAL_PRICE_CENTS": str(commerce_mod.price_cents("refusal")),
        "GATE_WELD_PRICE_LABEL": commerce_mod.price_label("operator_weld"),
        "GATE_WELD_PRICE_CENTS": str(commerce_mod.price_cents("operator_weld")),
        "GATE_FLOOR_PRICE_LABEL": commerce_mod.price_label("operator_floor"),
        "GATE_FLOOR_PRICE_CENTS": str(commerce_mod.price_cents("operator_floor")),
        "GATE_CONTACT_EMAIL": commerce_mod.support_email(),
        "GATE_BIND_TICKET_TTL": "15",
        "GATE_PUBLIC_URL": GATE_PUBLIC,
    }
    if os.getenv("GATE_SECRET_KEY", "").strip():
        fixed["GATE_SECRET_KEY"] = os.environ["GATE_SECRET_KEY"].strip()
    if os.getenv("GATE_OPS_TOKEN", "").strip():
        fixed["GATE_OPS_TOKEN"] = os.environ["GATE_OPS_TOKEN"].strip()
    if have_receipts:
        fixed["GATE_RECEIPT_PRIVATE_KEY"] = priv
        fixed["GATE_RECEIPT_PUBLIC_KEY"] = pub
    else:
        print("  skip GATE_RECEIPT_* (not in env — leaving Render values alone)")
    print("env vars")
    for k, v in fixed.items():
        set_env(SERVICE_ID, k, v)

    for k in (
        "STRIPE_SECRET_KEY",
        "STRIPE_PUBLISHABLE_KEY",
        "STRIPE_WEBHOOK_SECRET",
        "STRIPE_PRICE_ID",
        "STRIPE_INSTALL_PRICE_ID",
        "STRIPE_BIND_ROOM_PRICE_ID",
        "STRIPE_REFUSAL_PRICE_ID",
        "STRIPE_WELD_PRICE_ID",
        "STRIPE_FLOOR_PRICE_ID",
        "GATE_NOTIFY_WEBHOOK",
        "GATE_GA_ID",
        "GATE_META_PIXEL_ID",
    ):
        v = (os.getenv(k) or "").strip()
        if v:
            set_env(SERVICE_ID, k, v)
        else:
            print(f"  skip {k} (not in env)")

    print("deploy")
    out = _request("POST", f"/services/{SERVICE_ID}/deploys", {"clearCache": "clear"})
    deploy = out.get("deploy") or out
    print(f"deploy id: {deploy.get('id', deploy)}")
    print()
    print(f"After green (~3 min): ./verify-public.sh {GATE_PUBLIC}")


if __name__ == "__main__":
    main()
