from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class SecurityEvent(Base):
    __tablename__ = "security_event"

    id          = Column(Integer, primary_key=True, index=True)
    event_type  = Column(String, nullable=False)          # "PIR" | "wire" | "UNKNOWN"
    description = Column(String, nullable=True)
    timestamp   = Column(DateTime(timezone=True), server_default=func.now())
