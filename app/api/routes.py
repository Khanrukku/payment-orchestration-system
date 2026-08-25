from fastapi import APIRouter,Depends,Header,HTTPException,status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.gateways.mock import MockGateway
from app.models.payment import Payment,PaymentStatus
from app.models.webhook import WebhookEvent
from app.schemas import HealthResponse,PaymentCreate,PaymentResponse,WebhookPayload
from app.services.payment_service import PaymentService

router=APIRouter()
service=PaymentService([MockGateway("gateway_a"),MockGateway("gateway_b")])

@router.get("/health",response_model=HealthResponse)
async def health(): return {"status":"ok"}

@router.post("/payments",response_model=PaymentResponse,status_code=status.HTTP_201_CREATED)
async def create_payment(body:PaymentCreate,db:AsyncSession=Depends(get_db),idempotency_key:str=Header(...,alias="Idempotency-Key")):
    existing=await db.scalar(select(Payment).where(Payment.idempotency_key==idempotency_key))
    if existing:return existing
    payment=Payment(customer_id=body.customer_id,idempotency_key=idempotency_key,amount=body.amount,currency=body.currency)
    db.add(payment)
    try: await db.commit()
    except IntegrityError:
        await db.rollback()
        existing=await db.scalar(select(Payment).where(Payment.idempotency_key==idempotency_key))
        if existing:return existing
        raise
    await db.refresh(payment)
    return await service.process(payment,db)

@router.get("/payments/{payment_id}",response_model=PaymentResponse)
async def get_payment(payment_id:str,db:AsyncSession=Depends(get_db)):
    p=await db.get(Payment,payment_id)
    if not p: raise HTTPException(404,"Payment not found")
    return p

@router.post("/payments/{payment_id}/refund",response_model=PaymentResponse)
async def refund(payment_id:str,db:AsyncSession=Depends(get_db)):
    p=await db.get(Payment,payment_id)
    if not p: raise HTTPException(404,"Payment not found")
    try:return await service.refund(p,db)
    except ValueError as e: raise HTTPException(409,str(e)) from e

@router.post("/webhooks/{gateway}",status_code=202)
async def webhook(gateway:str,payload:WebhookPayload,db:AsyncSession=Depends(get_db)):
    db.add(WebhookEvent(gateway=gateway,event_id=payload.event_id,event_type=payload.event_type))
    try:await db.commit()
    except IntegrityError:
        await db.rollback(); return {"accepted":True,"duplicate":True}
    p=await db.get(Payment,payload.payment_id)
    if p and payload.event_type=="payment.succeeded" and p.status==PaymentStatus.PROCESSING.value:
        p.status=PaymentStatus.SUCCEEDED.value; await db.commit()
    return {"accepted":True,"duplicate":False}
