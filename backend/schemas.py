from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class TransactionCreate(BaseModel):
    """Schema for creating a new transaction"""
    merchant_id: str
    amount: float
    currency: str = "INR"
    gateway: str
    customer_email: EmailStr
    customer_phone: Optional[str] = None

class TransactionResponse(BaseModel):
    """Schema for transaction response"""
    id: int
    merchant_id: str
    transaction_id: str
    amount: float
    currency: str
    gateway: str
    status: str
    customer_email: str
    customer_phone: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class MerchantCreate(BaseModel):
    """Schema for creating a new merchant"""
    merchant_name: str
    email: EmailStr
    preferred_gateway: str = "razorpay"

class MerchantResponse(BaseModel):
    """Schema for merchant response"""
    id: int
    merchant_id: str
    merchant_name: str
    email: str
    api_key: str
    preferred_gateway: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class TransactionStats(BaseModel):
    """Schema for transaction statistics"""
    total_transactions: int
    successful_transactions: int
    failed_transactions: int
    pending_transactions: int
    total_volume: float
    success_rate: float