from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel

class WhatsAppMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    phone: str = Field(index=True)
    message: str
    direction: str  # "incoming" ou "outgoing"
    status: str = Field(default="pending")  # "pending", "sent", "delivered", "read", "failed"
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None