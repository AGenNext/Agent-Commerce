from fastapi.testclient import TestClient

from protocol_service.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_schema_endpoint() -> None:
    response = client.get("/schema")
    assert response.status_code == 200
    schema = response.json()
    assert schema["title"] == "Foundation Agent-Commerce Protocol Profile"
    assert "oneOf" in schema


def test_examples_are_valid() -> None:
    examples = client.get("/examples").json()
    for payload in examples.values():
        response = client.post("/validate", json={"payload": payload})
        assert response.status_code == 200
        body = response.json()
        assert body["valid"] is True
        assert body["errors"] == []


def test_invalid_payload_is_rejected() -> None:
    response = client.post("/validate", json={"payload": {"type": "unknown"}})
    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is False
    assert body["errors"]


def test_invalid_date_time_format_is_rejected() -> None:
    payload = client.get("/examples").json()["ap2_mandate_create"]
    payload["constraints"]["expires_at"] = "not-a-date"

    response = client.post("/validate", json={"payload": payload})

    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is False
    assert body["errors"]


def test_invalid_agent_card_uri_is_rejected() -> None:
    payload = client.get("/examples").json()["a2a_agent_card"]
    payload["endpoint"] = "not-a-uri"

    response = client.post("/validate", json={"payload": payload})

    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is False
    assert body["errors"]


def test_invalid_payment_execution_response_is_rejected() -> None:
    payload = {
        "ap2_version": "0.1-profile",
        "type": "payment.execute.response",
        "payment_id": "pay_001",
        "mandate_id": "mandate_001",
        "status": "paid",
        "amount": -1,
        "currency": "",
        "trace_id": "trace_001",
    }

    response = client.post("/validate", json={"payload": payload})

    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is False
    assert body["errors"]
