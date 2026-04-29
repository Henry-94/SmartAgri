from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.sensor_data import SensorData
from app.schemas.sensor import SensorDataResponse

router = APIRouter()

@router.get("/latest", response_model=SensorDataResponse)
def get_latest_sensor_data(db: Session = Depends(get_db)):
    """Récupère la dernière donnée des capteurs"""
    data = db.query(SensorData).order_by(SensorData.timestamp.desc()).first()
    if not data:
        raise HTTPException(status_code=404, detail="Aucune donnée de capteurs trouvée")
    return data

@router.get("/all", response_model=list[SensorDataResponse])
def get_all_sensor_data(db: Session = Depends(get_db), limit: int = 100):
    """Récupère toutes les données (avec limite)"""
    return db.query(SensorData).order_by(SensorData.timestamp.desc()).limit(limit).all()
