from sqlalchemy import Column, Integer, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base

class SensorData(Base):
    __tablename__ = "sensor_data"

    id        = Column(Integer, primary_key=True, index=True)
    temp      = Column(Float, nullable=True)   # Température °C (DHT22)
    hum       = Column(Float, nullable=True)   # Humidité air % (DHT22)
    soil      = Column(Float, nullable=True)   # Humidité sol %
    tank      = Column(Float, nullable=True)   # Niveau réservoir % (ultrason)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
