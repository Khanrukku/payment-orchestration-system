import asyncio
from app.core.config import settings
from app.models.payment import PaymentStatus
from app.services.state_machine import transition

class PaymentService:
    def __init__(self,gateways):
        if not gateways: raise ValueError("At least one gateway required")
        self.gateways=gateways

    async def process(self,payment,db):
        payment.status=transition(payment.status,PaymentStatus.PROCESSING).value
        await db.commit()
        errors=[]
        for gateway in self.gateways:
            for attempt in range(settings.max_gateway_retries+1):
                try:
                    result=await asyncio.wait_for(
                        gateway.charge(amount=payment.amount,currency=payment.currency,customer_id=payment.customer_id),
                        timeout=settings.gateway_timeout_seconds)
                    if result.success:
                        payment.gateway=gateway.name
                        payment.gateway_payment_id=result.gateway_payment_id
                        payment.status=transition(payment.status,PaymentStatus.SUCCEEDED).value
                        await db.commit(); await db.refresh(payment); return payment
                    errors.append(result.error or f"{gateway.name} failed")
                except TimeoutError:
                    errors.append(f"{gateway.name} timed out")
                if attempt<settings.max_gateway_retries:
                    await asyncio.sleep(.05*(2**attempt))
        payment.status=transition(payment.status,PaymentStatus.FAILED).value
        payment.failure_reason="; ".join(errors)[-512:]
        await db.commit(); await db.refresh(payment); return payment

    async def refund(self,payment,db):
        if PaymentStatus(payment.status)!=PaymentStatus.SUCCEEDED:
            raise ValueError("Only succeeded payments can be refunded")
        gateway=next((g for g in self.gateways if g.name==payment.gateway),None)
        if not gateway or not payment.gateway_payment_id: raise ValueError("Original gateway unavailable")
        result=await gateway.refund(gateway_payment_id=payment.gateway_payment_id,amount=payment.amount)
        if not result.success: raise RuntimeError(result.error or "Refund failed")
        payment.status=transition(payment.status,PaymentStatus.REFUNDED).value
        await db.commit(); await db.refresh(payment); return payment
