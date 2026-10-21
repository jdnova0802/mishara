"""Checkable agent doors — already built in this process, not a roadmap."""
from __future__ import annotations

from typing import Any


def doors(public_url: str = "") -> list[dict[str, Any]]:
    """MCP + OpenAPI + x402 + CLI. Status is `built` because the code exists.

    This is not a weld, not their_production, not a chatbot UI.
    """
    base = (public_url or "").rstrip("/")

    def href(path: str) -> str:
        return f"{base}{path}" if base else path

    return [
        {
            "id": "mcp",
            "label": "MCP",
            "status": "built",
            "href": href("/.well-known/mcp.json"),
            "endpoint": href("/mcp"),
            "plain": "Native tool server. Agents call POST /mcp. Not REST-only.",
        },
        {
            "id": "openapi",
            "label": "OpenAPI",
            "status": "built",
            "href": href("/openapi.json"),
            "endpoint": href("/openapi.json"),
            "plain": "Generated OpenAPI 3.1 at /openapi.json. Not a stub.",
        },
        {
            "id": "x402",
            "label": "x402",
            "status": "built",
            "href": href("/.well-known/x402.json"),
            "endpoint": href("/.well-known/x402.json"),
            "plain": "Payment rail with reserve, settle, and release in the DB.",
        },
        {
            "id": "cli",
            "label": "CLI",
            "status": "built",
            "href": href("/floor"),
            "endpoint": href("/floor"),
            "plain": (
                "offline_verify.py — argparse, --json, stdout/stderr/exit-code. "
                "Dead-hand check without fetching the server."
            ),
        },
    ]


def manifest(public_url: str = "") -> dict[str, Any]:
    return {
        "spec": "gate-already-built-v1",
        "note": (
            "These doors exist in this process. Not a production weld. "
            "No chatbot front-end. Agents use MCP and OpenAPI."
        ),
        "doors": doors(public_url),
    }
