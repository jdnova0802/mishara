"""Dating manifests — list everywhere, weld one write path."""
from __future__ import annotations


def listings_manifest(public_url: str, contact_email: str) -> dict:
    mcp = f"{public_url}/mcp"
    return {
        "spec": "gate-listings-v1",
        "rule": "Date all. Marry one write path.",
        "operator": "Nisaba LLC",
        "patent": "64/124,027",
        "contact": contact_email,
        "public_url": public_url,
        "engine": "https://velaru.xyz",
        "dates": {
            "mcp_gateways": {
                "status": "listing",
                "endpoint": mcp,
                "discovery": f"{public_url}/.well-known/mcp.json",
                "partners": ["kong", "truefoundry", "aws-agentcore"],
                "configs": {
                    "kong": f"{public_url}/listings/kong-mcp.yaml",
                    "truefoundry": f"{public_url}/listings/truefoundry-mcp.yaml",
                    "aws_agentcore": f"{public_url}/listings/aws-agentcore.json",
                },
                "note": "One /mcp door. Gateways discover/auth. They do not bind.",
            },
            "cloudflare": {
                "status": "listing",
                "worker": f"{public_url}/listings/cloudflare-worker.js",
                "wrangler": f"{public_url}/listings/wrangler.toml",
                "note": "Weld worker in front of one origin. Fail closed if GATE_URL is localhost.",
            },
            "x402": {
                "status": "listing",
                "catalog": f"{public_url}/.well-known/x402.json",
                "note": "HTTP 402 on hop limit → Stripe /pricing. Not a crypto product.",
            },
            "guidewire": {
                "status": "application",
                "packet": f"{public_url}/listings/guidewire-partnerconnect.json",
                "apply": "https://www.guidewire.com/partners/for-guidewire-partners-partnerconnect/technology-partners/become-a-technology-partner",
                "demo": f"{public_url}/demo/pas/bind-check",
                "plate": f"{public_url}/for/carriers",
                "note": "Paperwork. Not a production weld until a carrier bind-only path is live.",
            },
            "duckcreek": {
                "status": "application",
                "packet": f"{public_url}/listings/duckcreek-partner.json",
                "apply": "https://www.duckcreek.com/become-a-partner/",
                "portal": "https://www.duckcreek.com/digin_duckcreekdev/",
                "demo": f"{public_url}/demo/pas/bind-check",
                "note": "Paperwork. Paymentus marketplace is pay ≠ allowed — do not confuse with bind.",
            },
        },
        "welds": {
            "production_pas": {
                "status": "open",
                "rule": "One production write-path at a time. Second PAS is a clone of the first receipt.",
            },
            "tpm_hsm": {
                "status": "later",
                "rule": "After one PAS is in production. Not before first invoice.",
            },
        },
        "do_not_date": ["google", "openai", "palantir"],
    }


def mcp_discovery(public_url: str) -> dict:
    return {
        "mcpVersion": "2025-03-26",
        "name": "gate-api",
        "description": "Fuse hop before commit. Fail closed on timeout. CHARGE-only resurrection.",
        "server": public_url,
        "endpoint": f"{public_url}/mcp",
        "transport": "streamable-http",
        "auth": "Authorization: Bearer gate_sk_live_... (optional for demo fuses)",
        "servers": {
            "gate-api": {
                "url": f"{public_url}/mcp",
                "headers": {"Authorization": "Bearer ${GATE_API_KEY}"},
            }
        },
        "tools": [
            {
                "name": "fuse_lookup",
                "description": "OCSP of capability. 503 halt if unreachable. Never treat timeout as LIVE.",
                "path": "/v1/fuse/lookup",
                "method": "GET",
            },
            {
                "name": "fuse_hop",
                "description": "Pre-exec hop. DEAD → verdict false + verify_url.",
                "path": "/v1/fuse/hop",
                "method": "POST",
            },
            {
                "name": "welded_act",
                "description": "Closed world. Only act path. Hop first; DEAD never acts.",
                "path": "/v1/act",
                "method": "POST",
            },
            {
                "name": "pas_bind_check",
                "description": "PAS-shaped bind ALLOW/BLOCK + restraint.",
                "path": "/v1/pas/bind-check",
                "method": "POST",
            },
        ],
    }


def x402_catalog(public_url: str) -> dict:
    hop = f"{public_url}/v1/fuse/hop"
    act = f"{public_url}/v1/act"
    bind = f"{public_url}/v1/pas/bind-check"
    return {
        "x402Version": 2,
        "name": "Gate API",
        "description": "Metered fuse hop. HTTP 402 on hop limit (Stripe). Agents: discover here, not Google.",
        "baseUrl": public_url,
        "payment": {
            "scheme": "stripe",
            "upgrade_url": f"{public_url}/pricing",
            "note": "402 means hop quota, not USDC. Do not list a fake payTo address.",
        },
        "resources": [
            {
                "resource": hop,
                "type": "http",
                "x402Version": 2,
                "description": "Pre-exec fuse hop",
                "extensions": {
                    "bazaar": {
                        "info": {
                            "input": {"type": "http", "method": "POST"},
                            "output": {"type": "json", "example": {"verdict": False, "state": "DEAD"}},
                        }
                    }
                },
            },
            {
                "resource": act,
                "type": "http",
                "x402Version": 2,
                "description": "Welded closed-world act",
                "extensions": {
                    "bazaar": {
                        "info": {
                            "input": {"type": "http", "method": "POST"},
                            "output": {"type": "json", "example": {"acted": False, "halt": True}},
                        }
                    }
                },
            },
            {
                "resource": bind,
                "type": "http",
                "x402Version": 2,
                "description": "PAS bind gate demo",
                "extensions": {
                    "bazaar": {
                        "info": {
                            "input": {"type": "http", "method": "POST"},
                            "output": {"type": "json", "example": {"bind_allowed": False, "result": "BLOCK"}},
                        }
                    }
                },
            },
            {
                "resource": f"{public_url}/mcp",
                "type": "mcp",
                "x402Version": 2,
                "description": "MCP tools: fuse_lookup, fuse_hop, welded_act, pas_bind_check",
                "extensions": {
                    "bazaar": {
                        "info": {
                            "input": {
                                "type": "mcp",
                                "toolName": "welded_act",
                                "transport": "streamable-http",
                                "description": "Closed-world act. Hop first.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "fuse_id": {"type": "string"},
                                        "action": {"type": "string"},
                                    },
                                    "required": ["fuse_id"],
                                },
                            }
                        }
                    }
                },
            },
        ],
    }


def kong_mcp_yaml(public_url: str) -> str:
    return f"""# Kong declarative — date Gate as an MCP upstream. Not a PAS weld.
_format_version: "3.0"
services:
  - name: gate-mcp
    url: {public_url}
    routes:
      - name: gate-mcp
        paths:
          - /gate-mcp
        strip_path: true
    plugins:
      - name: request-transformer
        config:
          replace:
            uri: /mcp
# Point Kong AI / MCP gateway at:
#   {public_url}/mcp
# Auth header to Gate:
#   Authorization: Bearer gate_sk_live_...
# Discovery:
#   {public_url}/.well-known/mcp.json
"""


def truefoundry_mcp_yaml(public_url: str) -> str:
    return f"""# TrueFoundry MCP server registry entry — paste URL + auth.
name: gate-api
type: mcp
transport: streamable-http
url: {public_url}/mcp
discovery: {public_url}/.well-known/mcp.json
auth:
  type: bearer
  header: Authorization
  secret_env: GATE_API_KEY
tools:
  - fuse_lookup
  - fuse_hop
  - welded_act
  - pas_bind_check
notes: Discovery and auth only. DEAD verify is Gate, not TrueFoundry.
"""


def aws_agentcore_json(public_url: str) -> dict:
    return {
        "name": "gate-api",
        "description": "Velaru fuse hop via Gate. Fail closed. CHARGE-only resurrection.",
        "protocol": "MCP",
        "transport": "streamable-http",
        "endpoint": f"{public_url}/mcp",
        "discovery": f"{public_url}/.well-known/mcp.json",
        "authentication": {
            "type": "bearer",
            "header": "Authorization",
            "secretParameter": "GATE_API_KEY",
        },
        "tools": ["fuse_lookup", "fuse_hop", "welded_act", "pas_bind_check"],
        "note": "AWS MCP Gateway / AgentCore registers this URL. They do not become the bind path.",
    }


def guidewire_packet(public_url: str, contact_email: str) -> dict:
    return {
        "form": "Guidewire PartnerConnect Technology Partner — paste into the application",
        "apply_url": "https://www.guidewire.com/partners/for-guidewire-partners-partnerconnect/technology-partners/become-a-technology-partner",
        "company": "Nisaba LLC",
        "product_name": "Velaru Gate — bind-only pre-commit mortality fuse",
        "patent": "64/124,027",
        "website": public_url,
        "contact_email": contact_email,
        "category": "Policy administration / bind-and-issue control",
        "integration_target": "Guidewire InsuranceSuite PolicyCenter — bind-only / bind-and-issue",
        "one_liner": "Agent cannot bind if the fuse is DEAD. ALLOW/BLOCK + stranger-verifiable restraint receipt.",
        "problem": "Bind can complete on an agent the carrier cannot prove was live.",
        "solution": (
            "Pre-commit hop on the bind path. Timeout or DEAD → halt (never LIVE). "
            "CHARGE webhook is the only DEAD→LIVE path. Independent verify at velaru.xyz/verify."
        ),
        "demo": {
            "plate": f"{public_url}/for/carriers",
            "no_key": f"POST {public_url}/demo/pas/bind-check",
            "metered": f"POST {public_url}/v1/pas/bind-check",
            "expected": "bind_allowed: false, result: BLOCK, verify_url present",
        },
        "what_this_is_not": "Not a listing of 343 SKUs. Not a production weld until a carrier's bind-only path is in their PAS.",
        "status": "Application / dating. Exclusive PolicyCenter weld is one at a time.",
    }


def duckcreek_packet(public_url: str, contact_email: str) -> dict:
    return {
        "form": "Duck Creek Partner Ecosystem / duckcreek.dev — paste into the partnership request",
        "apply_url": "https://www.duckcreek.com/become-a-partner/",
        "portal": "https://www.duckcreek.com/digin_duckcreekdev/",
        "company": "Nisaba LLC",
        "product_name": "Velaru Gate — bind ALLOW/BLOCK with restraint receipt",
        "patent": "64/124,027",
        "website": public_url,
        "contact_email": contact_email,
        "marketplace": "Content Exchange (after validation) — not Payments Marketplace",
        "one_liner": "Same bind-check family as Guidewire. DEAD fuse cannot issue. Receipt legal can open.",
        "integration_pattern": "Pre-commit hook on bind / issue. Fail closed on timeout. Independent verify.",
        "demo": {
            "plate": f"{public_url}/for/carriers",
            "no_key": f"POST {public_url}/demo/pas/bind-check",
            "expected": "BLOCK + restraint permalink",
        },
        "do_not_confuse": "Paymentus / Payments Marketplace is pay ≠ allowed. This packet is bind, not payments.",
        "status": "Application / dating. One production PAS weld at a time.",
    }


def wrangler_toml(public_url: str) -> str:
    return f"""# Cloudflare Worker weld — attach to ONE origin.
# wrangler secret put GATE_KEY
# Set GATE_URL to the LIVE https origin, never localhost.

name = "gate-weld"
main = "cloudflare-worker.js"
compatibility_date = "2026-08-18"

[vars]
GATE_URL = "{public_url}"
FUSE_ID = "fuse_velaru_drill"
ALLOW_LOCAL = "0"
"""
