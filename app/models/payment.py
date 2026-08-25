import enum, uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base

class PaymentStatus(str, enum.Enum):
    CREATED="created"
    PROCESSING="processing"
    SUCCEEDED="succeeded"
    FAILED="failed"
    REFUNDED="refunded"

class Payment(Base):
    __tablename__="payments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda:str(uuid.uuid4()))
    customer_id: Mapped[str] = mapped_column(String(128), index=True)
    idempotency_key: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    amount: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(3))
    status: Mapped[str] = mapped_column(String(32), default=PaymentStatus.CREATED.value, index=True)
    gateway: Mapped[str|None] = mapped_column(String(64), nullable=True)
    gateway_payment_id: Mapped[str|None] = mapped_column(String(128), nullable=True)
    failure_reason: Mapped[str|None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda:datetime.now(timezone.utc))
