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
                "bind_worker": f"{public_url}/listings/cloudflare-worker-bind.js",
                "wrangler": f"{public_url}/listings/wrangler.toml",
                "wrangler_bind": f"{public_url}/listings/wrangler-bind.toml",
                "note": "Generic worker or bind-only worker. Fail closed if GATE_URL is localhost.",
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
        "bound_answer": {
            "page": f"{public_url}/bound",
            "manifest": f"{public_url}/.well-known/bound-answer.json",
            "prize": "a no that holds",
            "tests": ["narrow", "enforced", "provable"],
        },
        "exclusive_timing": {
            "page": f"{public_url}/only",
            "manifest": f"{public_url}/.well-known/exclusive-timing.json",
            "worth_more": "the act that never happens — because there was no other door",
            "receipt_is_not_the_product": True,
            "their_production": False,
        },
        "bind_room": {
            "url": f"{public_url}/bind-room",
            "officer_pack": f"{public_url}/bind-room/officer-pack.json",
            "appendix": f"{public_url}/bind-room/appendix.schema.json",
            "price": "$1,750",
        },
        "welds": {
            "policycenter": {
                "status": "code_ready",
                "pre_bind": f"{public_url}/v1/pas/policycenter/pre-bind",
                "demo": f"{public_url}/demo/pas/policycenter/pre-bind",
                "rule": "Hop first. DEAD → raise Manual UW issue. Do not call bind-and-issue.",
            },
            "mga_authority": {
                "status": "code_ready",
                "path": f"{public_url}/v1/pas/mga-authority",
                "demo": f"{public_url}/demo/pas/mga-authority",
            },
            "production_pas": {
                "status": "open",
                "two_yeses": [
                    "Bind-path owner with a live job API this quarter",
                    "Else CUO / Colorado 10-1-1 owner or NAIC pilot domestic",
                    "Else GC Bind Room pack",
                    "MCP never wins a slot",
                ],
            },
            "tpm_hsm": {
                "status": "later",
                "rule": "After one PAS is in production. Not before first invoice.",
            },
        },
        "contract": f"{public_url}/listings/control-not-model.json",
        "do_not_date": ["google", "openai", "palantir"],
        "refuse": [
            "inventory / bias-audit SaaS",
            "appetite extraction",
            "free workshops",
            "PII / ACORD / ECDIS on Gate PAS paths",
            "L12 / admin CHARGE / Google-Palantir partnerships",
            "price $0",
            "filing Gate as a rating/UW model",
        ],
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
            {
                "name": "policycenter_pre_bind",
                "description": "Hop then PolicyCenter next step. DEAD → raise Manual UW issue. No PII.",
                "path": "/v1/pas/policycenter/pre-bind",
                "method": "POST",
            },
            {
                "name": "mga_authority",
                "description": "Delegated-authority check: hop + premium/line/state. Fastest yes that is still their paper.",
                "path": "/v1/pas/mga-authority",
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
                "description": "MCP tools: fuse_lookup, fuse_hop, welded_act, pas_bind_check, policycenter_pre_bind, mga_authority",
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
  - policycenter_pre_bind
  - mga_authority
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
        "tools": [
            "fuse_lookup",
            "fuse_hop",
            "welded_act",
            "pas_bind_check",
            "policycenter_pre_bind",
            "mga_authority",
        ],
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
            "bind_room": f"{public_url}/bind-room",
            "no_key": f"POST {public_url}/demo/pas/bind-check",
            "pre_bind": f"POST {public_url}/demo/pas/policycenter/pre-bind",
            "metered": f"POST {public_url}/v1/pas/policycenter/pre-bind",
            "expected": "allow_bind: false + raise_uw_issue body; do not call bind-and-issue",
        },
        "weld": {
            "hop": f"POST {public_url}/v1/act",
            "pre_bind": f"POST {public_url}/v1/pas/policycenter/pre-bind",
            "create_uw_issue": "POST /job/v1/jobs/{jobId}/uw-issues (Manual checking set)",
            "bind_and_issue": "POST /job/v1/jobs/{jobId}/bind-and-issue — only if allow_bind true",
            "charge": "UW approve without CHARGE does not resurrect.",
        },
        "what_this_is_not": "Not ProNavigator. Not appetite extraction. Control plane on bind-and-issue.",
        "status": "Application / dating. Code for the weld is live. Exclusive production path is one at a time.",
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
            "bind_room": f"{public_url}/bind-room",
            "no_key": f"POST {public_url}/demo/pas/bind-check",
            "pre_bind": f"POST {public_url}/demo/pas/duckcreek/pre-bind",
            "expected": "allow_bind: false — do not call issue",
        },
        "do_not_confuse": "Paymentus / Payments Marketplace is pay ≠ allowed. This packet is bind, not payments.",
        "status": "Application / dating. One production PAS weld at a time.",
    }


def control_not_model(public_url: str, contact_email: str) -> dict:
    return {
        "spec": "gate-control-not-model-v1",
        "vendor": "Nisaba LLC",
        "product": "Gate API / Velaru fuse hop",
        "patent": "64/124,027",
        "classification": "Control plane. Not ECDIS. Not a rating or underwriting model. Not a third-party pricing vendor for the NAIC TPDMWG docket.",
        "data": {
            "accepted": ["fuse_id", "job_id", "premium", "authority_limit", "line", "state", "policy_number"],
            "rejected": "PII, ACORD, loss runs, named insured, SSN, ECDIS",
            "path": f"{public_url}/v1/pas/policycenter/pre-bind",
        },
        "carrier_duties": "Insurer remains responsible (CO 10-1-1 §5.B, NAIC third-party draft). This contract does not shift that.",
        "audit_rights": "Carrier and regulator may request hop + verify_url for any job_id we processed. Appendix B via GET /v1/pas/bind-appendix.",
        "charge": "DEAD→LIVE only via Velaru CHARGE webhook. PAS approval is not resurrection.",
        "contact": contact_email,
        "dpa": "No personal data processed on PAS paths if the client honors the allowlist. If they send PII, Gate returns 400 no_pii and does not store it.",
    }


def wrangler_toml(public_url: str) -> str:
    return f"""# Cloudflare Worker weld — attach to ONE origin.
# wrangler secret put GATE_KEY
# Set GATE_URL to the LIVE https origin, never localhost.
# Bind-only intercept: use wrangler-bind.toml + cloudflare-worker-bind.js

name = "gate-weld"
main = "cloudflare-worker.js"
compatibility_date = "2026-08-18"

[vars]
GATE_URL = "{public_url}"
FUSE_ID = "fuse_velaru_drill"
ALLOW_LOCAL = "0"
"""


def wrangler_bind_toml(public_url: str) -> str:
    return f"""# Bind-path only. Intercept bind-and-issue / issue. Everything else passes through.
# wrangler secret put GATE_KEY
# GATE_URL = live https Gate — never localhost.

name = "gate-bind-weld"
main = "cloudflare-worker-bind.js"
compatibility_date = "2026-08-18"

[vars]
GATE_URL = "{public_url}"
FUSE_ID = "fuse_velaru_drill"
ALLOW_LOCAL = "0"
"""
