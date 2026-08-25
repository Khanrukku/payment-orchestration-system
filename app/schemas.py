from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class PaymentCreate(BaseModel):
    amount:int=Field(gt=0)
    currency:str=Field(min_length=3,max_length=3)
    customer_id:str=Field(min_length=1,max_length=128)
    @field_validator("currency")
    @classmethod
    def currency_upper(cls,v): return v.upper()

class PaymentResponse(BaseModel):
    id:str; customer_id:str; amount:int; currency:str; status:str
    gateway:str|None=None; gateway_payment_id:str|None=None; failure_reason:str|None=None
    created_at:datetime
    model_config={"from_attributes":True}

class WebhookPayload(BaseModel):
    event_id:str; event_type:str; payment_id:str

class HealthResponse(BaseModel):
    status:str
