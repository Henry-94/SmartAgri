from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class ActionLog(Base):
    __tablename__ = "action_log"

    id        = Column(Integer, primary_key=True, index=True)
    pump_a    = Column(Boolean, default=False)
    pump_b    = Column(Boolean, default=False)
    mode      = Column(String, default="auto")        # "auto" | "manuel" | "manuelA" | "manuelB"
    action    = Column(String, nullable=True)            # Description lisible
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
