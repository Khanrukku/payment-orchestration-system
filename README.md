# Payment Orchestration System

[![CI](https://github.com/Khanrukku/payment-orchestration-system/actions/workflows/ci.yml/badge.svg)](https://github.com/Khanrukku/payment-orchestration-system/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Async-009688)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)
![Tests](https://img.shields.io/badge/Tests-pytest-yellow)
![Load Test](https://img.shields.io/badge/Load_Test-Locust-2E7D32)

A backend engineering portfolio project demonstrating **reliable payment workflow orchestration** using FastAPI, PostgreSQL, asynchronous Python, idempotency, transaction state management, gateway abstraction, retries and failover, webhook deduplication, automated testing, CI, and reproducible load testing.

> **Simulation only:** Mock payment gateways are used. This project does not process real money, card numbers, or sensitive cardholder data.

---

## Architecture

```text
                         ┌─────────────────┐
                         │     Client      │
                         └────────┬────────┘
                                  │ HTTP
                                  ▼
                         ┌─────────────────┐
                         │     FastAPI     │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │   Idempotency   │
                         │     Layer       │
                         └────────┬────────┘
                                  │
                                  ▼
                     ┌─────────────────────────┐
                     │ Payment State Machine   │
                     └───────────┬─────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
          ┌──────────────────┐       ┌─────────────────┐
          │    PostgreSQL    │       │     Gateway     │
          │ Payment Storage  │       │  Orchestrator   │
          └──────────────────┘       └────────┬────────┘
                                              │
                                   ┌──────────┴──────────┐
                                   ▼                     ▼
                           ┌──────────────┐      ┌──────────────┐
                           │ Mock Gateway │      │ Mock Gateway │
                           │      A       │      │      B       │
                           └──────────────┘      └──────────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │ Webhook Processing │
                         │  + Deduplication   │
                         └────────────────────┘
```

---

## Core Engineering Features

### Idempotent Payment Creation

Payment requests use unique idempotency keys to prevent accidental duplicate payment creation when clients retry requests.

This models an important reliability requirement in real payment systems where network failures can cause clients to resend requests.

---

### Payment State Management

Payments follow explicit lifecycle transitions rather than allowing arbitrary state changes.

This prevents invalid transitions and keeps transaction state consistent throughout processing.

---

### Gateway Abstraction

Payment providers are represented through a pluggable gateway interface.

The orchestration layer therefore remains independent of any individual payment provider and can route requests between different gateway implementations.

---

### Retry & Gateway Failover

Failed gateway operations can be retried using bounded exponential backoff.

If a gateway remains unavailable, the orchestration layer can fail over to another configured gateway.

This demonstrates resilience against temporary downstream failures.

---

### Webhook Deduplication

Gateway webhook events are identified using unique event IDs.

Repeated webhook delivery can therefore be detected and handled safely without processing the same event multiple times.

---

### Asynchronous Backend

FastAPI and asynchronous SQLAlchemy are used to keep API and database operations non-blocking.

This allows the service to handle concurrent requests efficiently.

---

### Automated Testing & CI

The repository includes automated tests covering API behaviour and gateway execution.

GitHub Actions executes the test suite automatically on repository changes.

```text
Push / Pull Request
        │
        ▼
GitHub Actions
        │
        ├── Install dependencies
        ├── Start test environment
        ├── Run pytest
        │
        ▼
   CI PASS / FAIL
```

---

## API

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/v1/payments` | Create and process a simulated payment |
| `GET` | `/api/v1/payments/{id}` | Retrieve current payment state |
| `POST` | `/api/v1/payments/{id}/refund` | Refund a succeeded payment |
| `POST` | `/api/v1/webhooks/{gateway}` | Receive a simulated gateway event |
| `GET` | `/api/v1/health` | Service health check |

Payment creation requires an:

```text
Idempotency-Key
```

header.

Example:

```bash
curl -X POST http://localhost:8000/api/v1/payments \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: payment-request-001" \
  -d '{
        "amount": 1999,
        "currency": "USD",
        "customer_id": "customer-001"
      }'
```

---

## Performance Benchmark

The API includes a reproducible **Locust load-testing workflow** executed through GitHub Actions.

This allows performance testing without requiring a dedicated local benchmarking environment.

### Benchmark Configuration

| Configuration | Value |
|---|---:|
| Concurrent simulated users | 20 |
| Spawn rate | 5 users/second |
| Test duration | 30 seconds |
| Environment | GitHub Actions runner |
| Tool | Locust |
| Workload | Health checks + payment creation |

### Measured Results

| Metric | Result |
|---|---:|
| Total requests | **453** |
| Failed requests | **0** |
| Failure rate | **0%** |
| Overall throughput | **~15.64 requests/sec** |
| Median response time | **2 ms** |
| Average response time | **~8.58 ms** |
| p95 response time | **27 ms** |
| p99 response time | **48 ms** |
| Health-check requests | **293** |
| Payment requests | **160** |
| Average payment endpoint latency | **~21.30 ms** |
| Maximum payment endpoint latency | **~48.15 ms** |

The benchmark completed **453 requests with zero failures** during the measured 30-second workload.

> These measurements were produced in a GitHub Actions CI environment using 20 simulated users. They describe this controlled benchmark only and should not be interpreted as production capacity guarantees.

The load-testing workflow also generates:

- Locust CSV statistics
- HTML performance report
- GitHub Actions benchmark artifacts

The benchmark can be reproduced manually through:

```text
GitHub
  → Actions
  → Load Test
  → Run workflow
```

---

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/Khanrukku/payment-orchestration-system
cd payment-orchestration-system
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

### 3. Start the stack

```bash
docker compose up --build
```

### 4. Open the API documentation

```text
http://localhost:8000/docs
```

FastAPI automatically exposes the interactive Swagger/OpenAPI interface.

---

## Running Tests

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the test suite:

```bash
pytest -q
```

---

## Load Testing

Load testing is implemented with **Locust**.

The repository contains:

```text
load_tests/
└── locustfile.py
```

The GitHub Actions load-testing workflow:

```text
.github/workflows/load-test.yml
```

starts the API, waits for the health endpoint, executes Locust in headless mode, collects benchmark statistics, and uploads the generated reports as workflow artifacts.

---

## Project Structure

```text
payment-orchestration-system/
│
├── app/
│   ├── main.py
│   ├── api/
│   ├── gateways/
│   ├── models/
│   ├── services/
│   └── core/
│
├── tests/
│   ├── test_api.py
│   └── test_gateway.py
│
├── load_tests/
│   └── locustfile.py
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── load-test.yml
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## Reliability Model

The project demonstrates several common backend reliability patterns:

| Engineering Problem | Implementation |
|---|---|
| Duplicate client requests | Idempotency keys |
| Invalid transaction state | Explicit payment state transitions |
| Gateway outage | Retry + failover |
| Temporary downstream failure | Exponential backoff |
| Duplicate webhook delivery | Event deduplication |
| Blocking I/O | Async FastAPI + SQLAlchemy |
| Regression detection | pytest + GitHub Actions |
| Performance validation | Locust CI benchmark |
| Reproducible environment | Docker Compose |

---

## Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.12** | Core backend implementation |
| **FastAPI** | Async REST API |
| **PostgreSQL** | Persistent transaction storage |
| **SQLAlchemy** | Async database access |
| **Pydantic** | Request/response validation |
| **Docker** | Reproducible container environment |
| **Docker Compose** | Multi-service orchestration |
| **pytest** | Automated testing |
| **GitHub Actions** | Continuous integration |
| **Locust** | Concurrent API load testing |

---

## Engineering Trade-offs

This project intentionally focuses on **payment orchestration and distributed-backend reliability concepts** rather than implementing a real payment processor.

Mock gateways make it possible to test:

- gateway failures
- retries
- failover
- transaction state transitions
- webhook processing
- idempotency
- concurrent API workloads

without storing or transmitting real financial credentials.

---

## Future Hardening

For a production-oriented evolution of the architecture, useful additions would include:

- Redis-backed atomic idempotency reservations
- transactional outbox pattern
- circuit breakers
- gateway health scoring
- payment reconciliation jobs
- distributed tracing with OpenTelemetry
- structured metrics and alerting
- secrets management
- rate limiting
- chaos/failure-injection testing
- larger multi-instance performance benchmarks

---

## Important Security Note

This repository is an **engineering simulation**.

It does **not**:

- process real payments
- collect card numbers
- store cardholder information
- integrate with live banking infrastructure

Real payment infrastructure would require substantially stronger security, compliance, observability, auditing, operational controls, and PCI-DSS considerations.

---

## Author

**Rukaiya Khan**

GitHub: [@Khanrukku](https://github.com/Khanrukku)

---

## Project Goal

The goal of this project is to demonstrate practical backend engineering concepts relevant to large-scale software systems:

**API design · concurrency · reliability · idempotency · fault tolerance · data consistency · automated testing · CI/CD · performance measurement**
