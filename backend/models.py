from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from datetime import datetime
from database import Base

class Transaction(Base):
    """Database model for payment transactions"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(String, index=True)
    transaction_id = Column(String, unique=True, index=True)
    amount = Column(Float)
    currency = Column(String, default="INR")
    gateway = Column(String)  # razorpay, stripe, paytm, etc.
    status = Column(String)  # pending, success, failed
    customer_email = Column(String)
    customer_phone = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    gateway_response = Column(String, nullable=True)
    is_reconciled = Column(Boolean, default=False)

class Merchant(Base):
    """Database model for merchants"""
    __tablename__ = "merchants"
    
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(String, unique=True, index=True)
    merchant_name = Column(String)
    email = Column(String, unique=True)
    api_key = Column(String, unique=True)
    preferred_gateway = Column(String, default="razorpay")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)