import pytest
from app.gateways.mock import MockGateway
@pytest.mark.asyncio
async def test_gateway_success():
    r=await MockGateway("test").charge(amount=100,currency="USD",customer_id="c")
    assert r.success and r.gateway_payment_id.startswith("test_")
@pytest.mark.asyncio
async def test_gateway_failure():
    r=await MockGateway("test",fail=True).charge(amount=100,currency="USD",customer_id="c")
    assert not r.success
