from app.models.payment import PaymentStatus
ALLOWED={
 PaymentStatus.CREATED:{PaymentStatus.PROCESSING},
 PaymentStatus.PROCESSING:{PaymentStatus.SUCCEEDED,PaymentStatus.FAILED},
 PaymentStatus.SUCCEEDED:{PaymentStatus.REFUNDED},
 PaymentStatus.FAILED:set(), PaymentStatus.REFUNDED:set()
}
def transition(current,target):
    current,target=PaymentStatus(current),PaymentStatus(target)
    if target not in ALLOWED[current]:
        raise ValueError(f"Invalid payment transition: {current.value} -> {target.value}")
    return target
