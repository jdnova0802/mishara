"""Streamable HTTP MCP endpoint — one door for Kong, TrueFoundry, AWS AgentCore, Cursor."""
from __future__ import annotations

import json
import uuid
from typing import Any, Callable

MCP_PROTOCOL = "2025-03-26"

TOOLS = [
    {
        "name": "fuse_lookup",
        "description": "OCSP of capability. Timeout/5xx → halt. Never treat UNREACHABLE as LIVE.",
        "inputSchema": {
            "type": "object",
            "properties": {"fuse_id": {"type": "string", "description": "Fuse id to look up"}},
            "required": ["fuse_id"],
        },
    },
    {
        "name": "fuse_hop",
        "description": "Pre-exec hop. DEAD → verdict false + verify_url. Fail closed.",
        "inputSchema": {
            "type": "object",
            "properties": {"fuse_id": {"type": "string"}},
            "required": ["fuse_id"],
        },
    },
    {
        "name": "welded_act",
        "description": "Closed world. Hop first. DEAD never acts. Only act path on Gate.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "fuse_id": {"type": "string"},
                "action": {"type": "string", "description": "What the relying party wants to do"},
            },
            "required": ["fuse_id"],
        },
    },
    {
        "name": "pas_bind_check",
        "description": "PAS-shaped bind ALLOW/BLOCK + restraint receipt. Guidewire/Duck Creek dating endpoint.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "policy_number": {"type": "string"},
                "premium": {"type": "number"},
                "job_id": {"type": "string"},
            },
        },
    },
    {
        "name": "policycenter_pre_bind",
        "description": "Hop then return PolicyCenter next step: bind-only ticket, or raise Manual UW issue. bind-and-issue is not granted. No PII.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "fuse_id": {"type": "string"},
                "job_id": {"type": "string"},
                "issue_type": {"type": "string"},
            },
            "required": ["fuse_id", "job_id"],
        },
    },
    {
        "name": "mga_authority",
        "description": "Delegated-authority check: fuse hop + premium/line/state limits. Fastest yes that is still their paper.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "fuse_id": {"type": "string"},
                "premium": {"type": "number"},
                "authority_limit": {"type": "number"},
                "line": {"type": "string"},
                "state": {"type": "string"},
            },
            "required": ["fuse_id"],
        },
    },
]


def jsonrpc_result(req_id: Any, result: Any) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def jsonrpc_error(req_id: Any, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def initialize_result(req_id: Any, public_url: str) -> dict:
    return jsonrpc_result(
        req_id,
        {
            "protocolVersion": MCP_PROTOCOL,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "gate-api", "version": "1.0.0", "websiteUrl": public_url},
            "instructions": (
                "Hop before commit. DEAD fails closed. CHARGE webhook is the only DEAD→LIVE path. "
                "Pass Authorization: Bearer gate_sk_live_... for metered tools; demo fuses work without a key."
            ),
        },
    )


def tools_list_result(req_id: Any) -> dict:
    return jsonrpc_result(req_id, {"tools": TOOLS})


def text_content(payload: Any) -> dict:
    if isinstance(payload, (dict, list)):
        text = json.dumps(payload)
    else:
        text = str(payload)
    return {"content": [{"type": "text", "text": text}], "isError": False}


def handle_message(msg: dict, *, public_url: str, call_tool: Callable[[str, dict], Any]) -> tuple[dict | None, int]:
    """Return (body, status). Notification → (None, 202)."""
    if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0":
        return jsonrpc_error(msg.get("id") if isinstance(msg, dict) else None, -32600, "Invalid Request"), 400

    method = msg.get("method")
    req_id = msg.get("id")
    params = msg.get("params") or {}

    if method == "notifications/initialized" or (isinstance(method, str) and method.startswith("notifications/")):
        return None, 202

    if method == "initialize":
        return initialize_result(req_id, public_url), 200
    if method == "ping":
        return jsonrpc_result(req_id, {}), 200
    if method == "tools/list":
        return tools_list_result(req_id), 200
    if method == "resources/list":
        return jsonrpc_result(req_id, {"resources": []}), 200
    if method == "prompts/list":
        return jsonrpc_result(req_id, {"prompts": []}), 200
    if method == "tools/call":
        name = (params.get("name") or "").strip()
        arguments = params.get("arguments") or {}
        if not name:
            return jsonrpc_error(req_id, -32602, "tools/call requires params.name"), 200
        known = {t["name"] for t in TOOLS}
        if name not in known:
            return jsonrpc_error(req_id, -32601, f"Unknown tool: {name}"), 200
        try:
            result = call_tool(name, arguments if isinstance(arguments, dict) else {})
        except Exception as e:
            err = text_content({"error": str(e)})
            err["isError"] = True
            return jsonrpc_result(req_id, err), 200
        return jsonrpc_result(req_id, text_content(result)), 200

    if req_id is None:
        return None, 202
    return jsonrpc_error(req_id, -32601, f"Method not found: {method}"), 200


def new_session_id() -> str:
    return str(uuid.uuid4())
