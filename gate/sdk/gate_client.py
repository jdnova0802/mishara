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
            err = data.get("error", {})
            raise GateError(
                err.get("message") or f"HTTP {r.status_code}",
                status_code=r.status_code,
                payload=data,
            )
        return data

    def lookup(self, fuse_id: str) -> dict[str, Any]:
        return self._request("GET", "/v1/fuse/lookup", params={"fuse_id": fuse_id})

    def hop(self, fuse_id: str, **extra) -> dict[str, Any]:
        body = {"fuse_id": fuse_id, **extra}
        return self._request("POST", "/v1/fuse/hop", json=body)

    def execute_gate_demo(self, **body) -> dict[str, Any]:
        return self._request("POST", "/v1/execute-gate/demo", json=body)

    def classify(self, message: str, domain: str = "companion", **extra) -> dict[str, Any]:
        body = {"message": message, "domain": domain, **extra}
        return self._request("POST", "/v1/classify", json=body)

    def me(self) -> dict[str, Any]:
        return self._request("GET", "/v1/me")
