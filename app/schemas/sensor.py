from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SensorDataResponse(BaseModel):
    id:        Optional[int]      = None
    temp:      Optional[float]    = None
    hum:       Optional[float]    = None
    soil:      Optional[float]    = None
    tank:      Optional[float]    = None
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True
