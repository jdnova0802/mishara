"""Slim OpenAPI for x402scan / agent discovery — payable routes only."""


def spec(public_url: str, *, contact_email: str, payto: str | None) -> dict:
    base = (public_url or "").rstrip("/")
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "Gate Pre-finality API",
            "version": "1.0.0",
            "description": (
                "Pre-finality GO/NO-GO before irreversible commit. "
                "Pay $0.002 USDC on Base via x402."
            ),
            "contact": {"email": contact_email, "url": base},
        },
        "servers": [{"url": base, "description": "Gate API"}],
        "x-discovery": {
            "ownershipProofs": [payto] if payto else [],
            "prefinality": f"{base}/.well-known/prefinality.json",
        },
        "paths": {
            "/v1/prefinality/evaluate": {
                "post": {
                    "summary": "Pre-finality GO/NO-GO + signed JWT receipt",
                    "description": (
                        "Rail-agnostic clearance before irreversible commit. "
                        "Pay $0.002 USDC on Base via x402, or use Gate API key."
                    ),
                    "x-payment-info": {
                        "protocols": ["x402"],
                        "price": {"mode": "fixed", "currency": "USDC", "amount": "0.002"},
                    },
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["rail", "transfer"],
                                    "properties": {
                                        "rail": {"type": "string", "enum": ["x402", "rtp"]},
                                        "transfer": {
                                            "type": "object",
                                            "properties": {
                                                "amount": {"type": "string"},
                                                "currency": {"type": "string"},
                                                "counterparty": {"type": "string"},
                                            },
                                        },
                                        "mandate": {"type": "object"},
                                        "context": {"type": "object"},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {"description": "GO + signed receipt JWT"},
                        "402": {"description": "x402 USDC payment required on Base"},
                        "403": {"description": "NO_GO — fail closed"},
                    },
                }
            },
            "/demo/prefinality/evaluate": {
                "post": {
                    "summary": "Free pre-finality demo (no payment)",
                    "security": [],
                    "responses": {"200": {"description": "Evaluate result"}},
                }
            },
        },
    }
