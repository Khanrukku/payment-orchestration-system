import uuid

from locust import HttpUser, between, task


class PaymentUser(HttpUser):
    """
    Simulates clients interacting with the Payment Orchestration API.

    Each request uses a unique idempotency key so that load testing
    measures actual payment creation rather than cached duplicate requests.
    """

    wait_time = between(0.5, 2)

    @task(5)
    def health_check(self):
        self.client.get(
            "/api/v1/health",
            name="GET /health",
        )

    @task(3)
    def create_payment(self):
        idempotency_key = f"load-test-{uuid.uuid4()}"

        self.client.post(
            "/api/v1/payments",
            headers={
                "Idempotency-Key": idempotency_key,
            },
            json={
                "amount": 1999,
                "currency": "USD",
                "customer_id": "load-test-customer",
            },
            name="POST /payments",
        )
