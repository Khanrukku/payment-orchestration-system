import pytest
from app.models.payment import PaymentStatus
from app.services.state_machine import transition
def test_valid():
    assert transition("created","processing")==PaymentStatus.PROCESSING
    assert transition("processing","succeeded")==PaymentStatus.SUCCEEDED
def test_invalid():
    with pytest.raises(ValueError):transition("created","refunded")
