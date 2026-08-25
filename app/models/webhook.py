import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base

class WebhookEvent(Base):
    __tablename__="webhook_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda:str(uuid.uuid4()))
    gateway: Mapped[str] = mapped_column(String(64))
    event_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    event_type: Mapped[str] = mapped_column(String(128))
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda:datetime.now(timezone.utc))
