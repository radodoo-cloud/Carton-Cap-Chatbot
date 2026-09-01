import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.db.connection import Base

class ConversationDB(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: f"c_{uuid.uuid4().hex[:8]}")
    user_id = Column(String, nullable=False, index=True)
    entry_point = Column(String, default="home_widget")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    messages = relationship("MessageDB", back_populates="conversation", cascade="all, delete-orphan")
