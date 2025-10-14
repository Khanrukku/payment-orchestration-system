from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uuid
import random
from datetime import datetime

from database import engine, get_db, Base
from models import Transaction, Merchant
from schemas import (
    TransactionCreate, 
    TransactionResponse, 
    MerchantCreate, 
    MerchantResponse,
    TransactionStats
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Payment Orchestration System",
    description="Multi-gateway payment processing platform",
    version="1.0.0"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simulated payment gateway processing
def process_payment_gateway(gateway: str, amount: float) -> dict:
    """
    Simulates payment processing through different gateways
    In production, this would call actual gateway APIs
    """
    # 90% success rate simulation
    success = random.random() > 0.1
    
    gateway_responses = {
        "razorpay": {
            "gateway_id": f"razorpay_{uuid.uuid4().hex[:12]}",
            "status": "success" if success else "failed",
            "message": "Payment processed successfully" if success else "Insufficient funds"
        },
        "stripe": {
            "gateway_id": f"stripe_{uuid.uuid4().hex[:12]}",
            "status": "success" if success else "failed",
            "message": "Payment completed" if success else "Card declined"
        },
        "paytm": {
            "gateway_id": f"paytm_{uuid.uuid4().hex[:12]}",
            "status": "success" if success else "failed",
            "message": "Transaction successful" if success else "Payment failed"
        },
        "phonepe": {
            "gateway_id": f"phonepe_{uuid.uuid4().hex[:12]}",
            "status": "success" if success else "failed",
            "message": "UPI payment successful" if success else "UPI transaction failed"
        }
    }
    
    return gateway_responses.get(gateway.lower(), gateway_responses["razorpay"])

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "active",
        "message": "Payment Orchestration System API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow()
    }

@app.post("/merchants", response_model=MerchantResponse)
def create_merchant(merchant: MerchantCreate, db: Session = Depends(get_db)):
    """Create a new merchant account"""
    
    # Check if merchant email already exists
    existing_merchant = db.query(Merchant).filter(Merchant.email == merchant.email).first()
    if existing_merchant:
        raise HTTPException(status_code=400, detail="Merchant with this email already exists")
    
    # Generate unique merchant ID and API key
    new_merchant = Merchant(
        merchant_id=f"MERCH_{uuid.uuid4().hex[:10].upper()}",
        merchant_name=merchant.merchant_name,
        email=merchant.email,
        api_key=f"sk_live_{uuid.uuid4().hex}",
        preferred_gateway=merchant.preferred_gateway
    )
    
    db.add(new_merchant)
    db.commit()
    db.refresh(new_merchant)
    
    return new_merchant

@app.get("/merchants", response_model=List[MerchantResponse])
def get_merchants(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all merchants"""
    merchants = db.query(Merchant).offset(skip).limit(limit).all()
    return merchants

@app.post("/transactions", response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    """Process a new payment transaction"""
    
    # Verify merchant exists
    merchant = db.query(Merchant).filter(Merchant.merchant_id == transaction.merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    if not merchant.is_active:
        raise HTTPException(status_code=403, detail="Merchant account is inactive")
    
    # Generate unique transaction ID
    transaction_id = f"TXN_{uuid.uuid4().hex[:16].upper()}"
    
    # Process payment through gateway
    gateway_response = process_payment_gateway(transaction.gateway, transaction.amount)
    
    # Create transaction record
    new_transaction = Transaction(
        merchant_id=transaction.merchant_id,
        transaction_id=transaction_id,
        amount=transaction.amount,
        currency=transaction.currency,
        gateway=transaction.gateway,
        status=gateway_response["status"],
        customer_email=transaction.customer_email,
        customer_phone=transaction.customer_phone,
        gateway_response=str(gateway_response)
    )
    
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    
    return new_transaction

@app.get("/transactions", response_model=List[TransactionResponse])
def get_transactions(
    merchant_id: str = None,
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all transactions with optional filters"""
    query = db.query(Transaction)
    
    if merchant_id:
        query = query.filter(Transaction.merchant_id == merchant_id)
    if status:
        query = query.filter(Transaction.status == status)
    
    transactions = query.order_by(Transaction.created_at.desc()).offset(skip).limit(limit).all()
    return transactions

@app.get("/transactions/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: str, db: Session = Depends(get_db)):
    """Get a specific transaction by ID"""
    transaction = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@app.get("/analytics/stats", response_model=TransactionStats)
def get_transaction_stats(merchant_id: str = None, db: Session = Depends(get_db)):
    """Get transaction statistics"""
    query = db.query(Transaction)
    
    if merchant_id:
        query = query.filter(Transaction.merchant_id == merchant_id)
    
    all_transactions = query.all()
    
    total = len(all_transactions)
    successful = len([t for t in all_transactions if t.status == "success"])
    failed = len([t for t in all_transactions if t.status == "failed"])
    pending = len([t for t in all_transactions if t.status == "pending"])
    
    total_volume = sum([t.amount for t in all_transactions if t.status == "success"])
    success_rate = (successful / total * 100) if total > 0 else 0
    
    return TransactionStats(
        total_transactions=total,
        successful_transactions=successful,
        failed_transactions=failed,
        pending_transactions=pending,
        total_volume=total_volume,
        success_rate=round(success_rate, 2)
    )

@app.get("/analytics/gateway-performance")
def get_gateway_performance(db: Session = Depends(get_db)):
    """Get performance metrics by gateway"""
    transactions = db.query(Transaction).all()
    
    gateway_stats = {}
    for txn in transactions:
        if txn.gateway not in gateway_stats:
            gateway_stats[txn.gateway] = {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "volume": 0
            }
        
        gateway_stats[txn.gateway]["total"] += 1
        if txn.status == "success":
            gateway_stats[txn.gateway]["successful"] += 1
            gateway_stats[txn.gateway]["volume"] += txn.amount
        elif txn.status == "failed":
            gateway_stats[txn.gateway]["failed"] += 1
    
    # Calculate success rates
    for gateway, stats in gateway_stats.items():
        if stats["total"] > 0:
            stats["success_rate"] = round((stats["successful"] / stats["total"]) * 100, 2)
        else:
            stats["success_rate"] = 0
    
    return gateway_stats

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)