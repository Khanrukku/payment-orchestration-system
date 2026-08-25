import pytest
from fastapi.testclient import TestClient

from app.main import app


def test_health():
    with TestClient(app) as client:
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_docs_available():
    with TestClient(app) as client:
        response = client.get("/docs")

        assert response.status_code == 200


def test_create_payment_requires_idempotency_key():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/payments",
            json={
                "amount": 1299,
                "currency": "USD",
                "customer_id": "customer-test",
            },
        )

        assert response.status_code == 422


def test_create_payment_with_idempotency_key():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/payments",
            headers={
                "Idempotency-Key": "test-payment-create-1",
            },
            json={
                "amount": 1299,
                "currency": "usd",
                "customer_id": "customer-test",
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["amount"] == 1299
        assert data["currency"] == "USD"
        assert data["customer_id"] == "customer-test"
        assert data["status"] in {
            "processing",
            "succeeded",
            "failed",
        }


def test_duplicate_idempotency_key_returns_same_payment():
    with TestClient(app) as client:
        headers = {
            "Idempotency-Key": "duplicate-payment-test-1",
        }

        body = {
            "amount": 2500,
            "currency": "USD",
            "customer_id": "customer-duplicate",
        }

        first_response = client.post(
            "/api/v1/payments",
            headers=headers,
            json=body,
        )

        second_response = client.post(
            "/api/v1/payments",
            headers=headers,
            json=body,
        )

        assert first_response.status_code == 201
        assert second_response.status_code == 201

        first_payment = first_response.json()
        second_payment = second_response.json()

        assert first_payment["id"] == second_payment["id"]


def test_get_unknown_payment_returns_404():
    with TestClient(app) as client:
        response = client.get(
            "/api/v1/payments/non-existent-payment"
        )

        assert response.status_code == 404


def test_duplicate_webhook_is_idempotent():
    with TestClient(app) as client:
        payload = {
            "event_id": "webhook-event-test-1",
            "event_type": "payment.succeeded",
            "payment_id": "non-existent-payment",
        }

        first_response = client.post(
            "/api/v1/webhooks/gateway_a",
            json=payload,
        )

        second_response = client.post(
            "/api/v1/webhooks/gateway_a",
            json=payload,
        )

        assert first_response.status_code == 202
        assert second_response.status_code == 202

        assert first_response.json()["duplicate"] is False
        assert second_response.json()["duplicate"] is True
