#!/usr/bin/env python3
"""Deploy / refresh Mishara on mishara.onrender.com (service mishara-public).

Requires RENDER_API_KEY in env or Cloud Agent secrets.
Gate lives on a separate service (gate-api / gate.velaru.xyz) — never point
this script at Gate, and never rename this service to the bare name "mishara"
(that name is taken by mishara-bu8k).
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.render.com/v1"
# mishara-public → https://mishara.onrender.com (separate from gate-api).
SERVICE_ID = os.getenv("RENDER_MISHARA_SERVICE_ID", "srv-d9romc2jnfac7385gn80")
PUBLIC_URL = os.getenv("MISHARA_PUBLIC_URL", "https://mishara.onrender.com").rstrip("/")

BUILD = "pip install -r requirements_mishara.txt"
START = "gunicorn mishara_app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120"


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


def _request(method: str, path: str, body: dict | None = None):
    key = os.getenv("RENDER_API_KEY", "").strip()
    if not key:
        raise SystemExit(
            "RENDER_API_KEY missing in this Cloud Agent VM.\n"
            "Local Windows .env is gitignored and never syncs here.\n"
            "One-time fix: add RENDER_API_KEY as a Cursor Cloud Agent environment secret\n"
            "(Dashboard → Cloud Agents → this environment → Secrets),\n"
            "then start a new agent or re-run after secrets inject.\n"
            "Do not paste keys into chat every run."
        )
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


def main() -> None:
    for p in (
        os.path.join(os.path.dirname(__file__), ".env"),
        os.path.join(os.path.dirname(__file__), "gate", ".env"),
        os.path.expanduser("~/DocumentsVelaru/.env"),
        os.path.join(os.getcwd(), ".env"),
    ):
        _load_dotenv(os.path.abspath(p))

    print(f"GET service {SERVICE_ID}")
    svc = _request("GET", f"/services/{SERVICE_ID}")
    service = svc.get("service") or svc
    print(f"  name={service.get('name')} type={service.get('type')}")

    # Do not rename to "mishara" — that name is already taken by another
    # Render service (mishara-bu8k). Keep current name; only cut build/root.
    print("PATCH rootDir='' (repo root) + Mishara build/start (keep service name)")
    _request(
        "PATCH",
        f"/services/{SERVICE_ID}",
        {
            "rootDir": "",
            "serviceDetails": {
                "envSpecificDetails": {
                    "buildCommand": BUILD,
                    "startCommand": START,
                },
                "healthCheckPath": "/health",
            },
        },
    )

    print("env vars")
    fixed = {
        "PYTHON_VERSION": "3.13.0",
        "VELARU_API_URL": os.getenv("VELARU_API_URL", "https://velaru.onrender.com"),
        "VELARU_VERIFY_URL": os.getenv("VELARU_VERIFY_URL", "https://velaru.xyz/verify"),
        "MISHARA_DB_PATH": "/var/data/mishara.db",
        "MISHARA_PAYMENTS": os.getenv("MISHARA_PAYMENTS", "stripe"),
        "MISHARA_PUBLIC_URL": PUBLIC_URL,
        "MISHARA_CONTACT_EMAIL": os.getenv("MISHARA_CONTACT_EMAIL", "hello@velaru.xyz"),
    }
    for k, v in fixed.items():
        set_env(SERVICE_ID, k, v)

    for k in (
        "STRIPE_SECRET_KEY",
        "STRIPE_PUBLISHABLE_KEY",
        "OPENAI_API_KEY",
        "MISHARA_SECRET_KEY",
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
    print(f"After green: curl -s {PUBLIC_URL}/health")
    print('Expect: "service":"mishara" + products harm_receipt/demand_pack/advocate_bundle')


if __name__ == "__main__":
    main()
