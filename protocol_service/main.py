from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from protocol_service.validator import validate_payload

ROOT = Path(__file__).resolve().parents[1]
PROFILE_DOC = ROOT / "docs" / "foundation-agent-commerce-protocol-profile.md"
PROFILE_SCHEMA = ROOT / "schemas" / "foundation-agent-commerce-protocol-profile.schema.json"


class ValidationRequest(BaseModel):
    payload: dict[str, Any] = Field(..., description="Protocol payload to validate")


class ValidationResponse(BaseModel):
    valid: bool
    schema_id: str
    errors: list[str]


def load_schema() -> dict[str, Any]:
    if not PROFILE_SCHEMA.exists():
        raise HTTPException(status_code=500, detail="Protocol schema not found")
    return json.loads(PROFILE_SCHEMA.read_text(encoding="utf-8"))


def load_profile_doc() -> str:
    if not PROFILE_DOC.exists():
        raise HTTPException(status_code=500, detail="Protocol profile document not found")
    return PROFILE_DOC.read_text(encoding="utf-8")


app = FastAPI(
    title="Foundation Agent-Commerce Protocol Service",
    description="Deployable validator API for UCP, AP2, A2A, and x402 Agent-Commerce protocol payloads.",
    version="0.1.1",
)


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "name": "Foundation Agent-Commerce Protocol Service",
        "version": "0.1.1",
        "protocols": ["UCP", "AP2", "A2A", "x402"],
        "endpoints": {
            "health": "/health",
            "profile": "/profile",
            "schema": "/schema",
            "examples": "/examples",
            "validate": "/validate",
        },
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/profile", response_class=PlainTextResponse)
def profile() -> str:
    return load_profile_doc()


@app.get("/schema")
def schema() -> dict[str, Any]:
    return load_schema()


@app.post("/validate", response_model=ValidationResponse)
def validate_protocol(request: ValidationRequest) -> ValidationResponse:
    schema_data = load_schema()
    errors = validate_payload(schema_data, request.payload)
    return ValidationResponse(
        valid=not errors,
        schema_id=schema_data.get("$id", "foundation-agent-commerce-protocol-profile"),
        errors=errors,
    )


@app.get("/examples")
def examples() -> dict[str, Any]:
    return {
        "ucp_product_create": {
            "ucp_version": "0.1-profile",
            "type": "commerce.action.request",
            "action": "product.create",
            "actor": {"type": "agent", "id": "agent_store_helper"},
            "resource": {"type": "product"},
            "input": {"name": "Notebook", "price": 99, "currency": "INR", "stock": 50},
            "trace_id": "trace_001",
        },
        "ap2_mandate_create": {
            "ap2_version": "0.1-profile",
            "type": "payment.mandate.create",
            "mandate_id": "mandate_001",
            "grantor": {"type": "user", "id": "cust_001"},
            "grantee": {"type": "agent", "id": "agent_checkout_helper"},
            "constraints": {
                "max_amount": 198,
                "currency": "INR",
                "merchant_id": "store_001",
                "purpose": "checkout_payment",
                "expires_at": "2026-07-01T21:00:00+05:30",
                "single_use": True,
            },
            "context": {"checkout_id": "chk_001"},
            "nonce": "nonce_001",
            "signature": "profile_signature_placeholder",
        },
        "a2a_agent_card": {
            "a2a_version": "0.1-profile",
            "type": "agent.card",
            "agent_id": "agent_checkout_helper",
            "name": "Checkout Helper Agent",
            "endpoint": "https://example.com/agents/checkout-helper",
            "capabilities": ["checkout.create", "payment.mandate.request"],
            "accepted_protocols": ["UCP", "AP2", "A2A"],
        },
        "x402_challenge": {
            "x402_version": "0.1-profile",
            "type": "payment.challenge",
            "resource": "/premium-price-feed",
            "amount": 1,
            "currency": "USD",
            "network": "base",
            "pay_to": "merchant_wallet_placeholder",
            "expires_at": "2026-07-01T21:00:00+05:30",
            "challenge_id": "x402_challenge_001",
        },
    }
