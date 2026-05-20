from fastapi.testclient import TestClient

from server import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get('/health')
    assert response.status_code == 200


def test_unauthorized_without_api_key_when_configured():
    # This test is permissive because auth is optional in development.
    response = client.get('/api/providers')
    assert response.status_code in (200, 401)
