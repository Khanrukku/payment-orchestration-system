from abc import ABC, abstractmethod
from dataclasses import dataclass
@dataclass(frozen=True)
class GatewayResult:
    success:bool
    gateway_payment_id:str|None=None
    error:str|None=None
class PaymentGateway(ABC):
    name:str
    @abstractmethod
    async def charge(self,*,amount:int,currency:str,customer_id:str)->GatewayResult: ...
    @abstractmethod
    async def refund(self,*,gateway_payment_id:str,amount:int)->GatewayResult: ...
