"""Gate API Python SDK — thin client for fuse lookup and hop."""
from __future__ import annotations

import os
from typing import Any, Optional

import requests


class GateError(Exception):
    def __init__(self, message: str, status_code: int = 0, payload: Optional[dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload or {}


class GateClient:
    """Metered Gate API client."""

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: float = 30,
    ):
        self.api_key = api_key
        self.base_url = (base_url or os.getenv("GATE_API_URL", "http://localhost:5001")).rstrip("/")
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "gate-sdk/1.0",
        }

    def _request(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        r = requests.request(method, url, headers=self._headers(), timeout=self.timeout, **kwargs)
        try:
            data = r.json()
        except ValueError:
            data = {"error": {"message": r.text}}
        if r.status_code >= 400:
            err = data.get("error") if isinstance(data.get("error"), dict) else {}
            msg = (err or {}).get("message") or data.get("message") or f"HTTP {r.status_code}"
            raise GateError(msg, status_code=r.status_code, payload=data)
        return data

    def lookup(self, fuse_id: str) -> dict[str, Any]:
        return self._request("GET", "/v1/fuse/lookup", params={"fuse_id": fuse_id})

    def hop(self, fuse_id: str, **extra) -> dict[str, Any]:
        body = {"fuse_id": fuse_id, **extra}
        return self._request("POST", "/v1/fuse/hop", json=body)

    def act(self, fuse_id: str, action: str = "commit") -> dict[str, Any]:
        return self._request("POST", "/v1/act", json={"fuse_id": fuse_id, "action": action})

    def pas_bind_check(self, **body) -> dict[str, Any]:
        return self._request("POST", "/v1/pas/bind-check", json=body)

    def policycenter_pre_bind(self, fuse_id: str, job_id: str, **extra) -> dict[str, Any]:
        return self._request(
            "POST",
            "/v1/pas/policycenter/pre-bind",
            json={"fuse_id": fuse_id, "job_id": job_id, **extra},
        )

    def mga_authority(self, fuse_id: str, **extra) -> dict[str, Any]:
        return self._request("POST", "/v1/pas/mga-authority", json={"fuse_id": fuse_id, **extra})

    def duckcreek_pre_bind(self, fuse_id: str, job_id: str, **extra) -> dict[str, Any]:
        return self._request(
            "POST",
            "/v1/pas/duckcreek/pre-bind",
            json={"fuse_id": fuse_id, "job_id": job_id, **extra},
        )

    def prefinality_evaluate(self, **body) -> dict[str, Any]:
        return self._request("POST", "/v1/prefinality/evaluate", json=body)

    def prefinality_verify(self, **body) -> dict[str, Any]:
        return self._request("POST", "/v1/prefinality/verify", json=body)

    def prefinality_rtp_gate(self, receipt: str, payment_order: dict) -> dict[str, Any]:
        return self._request(
            "POST",
            "/v1/prefinality/rtp/gate",
            json={"receipt": receipt, "payment_order": payment_order},
        )

    def redeem_bind_ticket(
        self,
        ticket_id: str,
        token: str,
        job_id: str,
        method: str,
        path: str,
        now: str | None = None,
        spend_fingerprint: str | None = None,
        **extra,
    ) -> dict[str, Any]:
        from datetime import datetime, timezone

        body = {
            "ticket_id": ticket_id,
            "token": token,
            "job_id": job_id,
            "method": method,
            "path": path,
            "now": now or datetime.now(timezone.utc).isoformat(),
            **extra,
        }
        if spend_fingerprint:
            body["spend_fingerprint"] = spend_fingerprint
        return self._request("POST", "/v1/pas/bind-ticket/redeem", json=body)

    def license_charge(self, license_id: str, charge_id: str) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/v1/pas/licenses/{license_id}/charge",
            json={"charge_id": charge_id},
        )

    def license_dead(self, license_id: str) -> dict[str, Any]:
        return self._request("POST", f"/v1/pas/licenses/{license_id}/dead", json={})

    def license_snapshot(self, license_id: str) -> dict[str, Any]:
        return self._request("GET", f"/v1/pas/licenses/{license_id}")

    def bind_appendix(self) -> dict[str, Any]:
        return self._request("GET", "/v1/pas/bind-appendix")

    def execute_gate_demo(self, **body) -> dict[str, Any]:
        return self._request("POST", "/v1/execute-gate/demo", json=body)

    def classify(self, message: str, domain: str = "companion", **extra) -> dict[str, Any]:
        body = {"message": message, "domain": domain, **extra}
        return self._request("POST", "/v1/classify", json=body)

    def me(self) -> dict[str, Any]:
        return self._request("GET", "/v1/me")
