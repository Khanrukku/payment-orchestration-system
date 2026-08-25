import pytest

from app.gateways.mock import MockGateway
from app.models.payment import PaymentStatus
from app.services.state_machine import transition


@pytest.mark.asyncio
async def test_gateway_success():
    gateway = MockGateway("test")

    result = await gateway.charge(
        amount=100,
        currency="USD",
        customer_id="customer-1",
    )

    assert result.success is True
    assert result.gateway_payment_id is not None
    assert result.gateway_payment_id.startswith("test_")


@pytest.mark.asyncio
async def test_gateway_failure():
    gateway = MockGateway(
        "test",
        fail=True,
    )

    result = await gateway.charge(
        amount=100,
        currency="USD",
        customer_id="customer-1",
    )

    assert result.success is False
    assert result.gateway_payment_id is None
    assert result.error is not None


@pytest.mark.asyncio
async def test_gateway_refund_success():
    gateway = MockGateway("test")

    result = await gateway.refund(
        gateway_payment_id="gateway-payment-123",
        amount=500,
    )

    assert result.success is True
    assert result.gateway_payment_id == "gateway-payment-123"


@pytest.mark.asyncio
async def test_gateway_refund_failure():
    gateway = MockGateway(
        "test",
        fail=True,
    )

    result = await gateway.refund(
        gateway_payment_id="gateway-payment-123",
        amount=500,
    )

    assert result.success is False
    assert result.error is not None


def test_payment_state_machine_valid_transitions():
    assert (
        transition(
            PaymentStatus.CREATED,
            PaymentStatus.PROCESSING,
        )
        == PaymentStatus.PROCESSING
    )

    assert (
        transition(
            PaymentStatus.PROCESSING,
            PaymentStatus.SUCCEEDED,
        )
        == PaymentStatus.SUCCEEDED
    )

    assert (
        transition(
            PaymentStatus.SUCCEEDED,
            PaymentStatus.REFUNDED,
        )
        == PaymentStatus.REFUNDED
    )


def test_payment_state_machine_rejects_invalid_transition():
    with pytest.raises(ValueError):
        transition(
            PaymentStatus.CREATED,
            PaymentStatus.REFUNDED,
        )
