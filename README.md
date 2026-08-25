# Payment Orchestration System

[![CI](https://github.com/Khanrukku/payment-orchestration-system/actions/workflows/ci.yml/badge.svg)](https://github.com/Khanrukku/payment-orchestration-system/actions/workflows/ci.yml)

A backend engineering portfolio project demonstrating reliable payment workflow orchestration with FastAPI, PostgreSQL, async Python, idempotency, transaction state management, gateway abstraction, retries/failover, webhook deduplication, Docker, tests, and CI.

> **Simulation only:** mock gateways are used; the project does not process real money or card data.

## Architecture

```text
Client -> FastAPI -> Idempotency -> Payment State Machine -> PostgreSQL
                                      |
                                      v
                              Gateway Orchestrator
                               /             \
                         Mock Gateway A   Mock Gateway B
                                      |
                                      v
                            Webhook Deduplication
```

## Key engineering concepts

- Unique idempotency keys prevent duplicate payment creation.
- Explicit state transitions reject invalid payment lifecycle changes.
- Pluggable gateway interface separates orchestration from provider logic.
- Failed gateway calls are retried with bounded exponential backoff before failover.
- Webhook event IDs are unique, making duplicate delivery safe.
- Async SQLAlchemy supports non-blocking persistence.
- pytest + GitHub Actions provide automated regression checks.
- Docker Compose supplies PostgreSQL and Redis for local infrastructure.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/payments` | Create and process a simulated payment |
| GET | `/api/v1/payments/{id}` | Retrieve payment state |
| POST | `/api/v1/payments/{id}/refund` | Refund a succeeded payment |
| POST | `/api/v1/webhooks/{gateway}` | Receive simulated gateway event |
| GET | `/api/v1/health` | Health check |

`POST /payments` requires an `Idempotency-Key` header.

## Run

```bash
cp .env.example .env
docker compose up --build
```

Swagger: `http://localhost:8000/docs`

## Test

```bash
pip install -r requirements.txt
pytest -q
```

## Important design note

This is deliberately a **payment-system simulation**, not a payment processor. It focuses on the software-engineering problems around orchestration and reliability without handling sensitive cardholder data.

## Next hardening steps

Redis atomic idempotency reservations, transactional outbox, circuit breakers, gateway health scoring, reconciliation, OpenTelemetry, and measured load/chaos tests.
