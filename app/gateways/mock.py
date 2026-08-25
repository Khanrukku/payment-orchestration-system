import asyncio, uuid
from app.gateways.base import GatewayResult, PaymentGateway
class MockGateway(PaymentGateway):
    def __init__(self,name,fail=False,latency=.01):
        self.name,self.fail,self.latency=name,fail,latency
    async def charge(self,*,amount,currency,customer_id):
        await asyncio.sleep(self.latency)
        if self.fail:return GatewayResult(False,error=f"{self.name} simulated failure")
        return GatewayResult(True,f"{self.name}_{uuid.uuid4().hex[:16]}")
    async def refund(self,*,gateway_payment_id,amount):
        await asyncio.sleep(self.latency)
        if self.fail:return GatewayResult(False,error=f"{self.name} simulated refund failure")
        return GatewayResult(True,gateway_payment_id)
