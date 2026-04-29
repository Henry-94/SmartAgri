from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.sensor_data import SensorData
from app.models.action_log import ActionLog
from app.models.security_event import SecurityEvent

router = APIRouter()

# ── GET ────────────────────────────────────────────────────

@router.get("/sensors")
def get_sensor_history(db: Session = Depends(get_db), limit: int = 50):
    return db.query(SensorData).order_by(SensorData.timestamp.desc()).limit(limit).all()

@router.get("/actions")
def get_action_history(db: Session = Depends(get_db), limit: int = 50):
    return db.query(ActionLog).order_by(ActionLog.timestamp.desc()).limit(limit).all()

@router.get("/security")
def get_security_history(db: Session = Depends(get_db), limit: int = 50):
    return db.query(SecurityEvent).order_by(SecurityEvent.timestamp.desc()).limit(limit).all()

# ── DELETE — Effacement réel en base de données ───────────

@router.delete("/sensors")
def delete_sensor_history(db: Session = Depends(get_db)):
    """Efface toutes les données capteurs de la base PostgreSQL"""
    count = db.query(SensorData).delete()
    db.commit()
    return {"status": "ok", "deleted": count, "table": "sensor_data"}

@router.delete("/actions")
def delete_action_history(db: Session = Depends(get_db)):
    """Efface tout l'historique des actions irrigation de la base PostgreSQL"""
    count = db.query(ActionLog).delete()
    db.commit()
    return {"status": "ok", "deleted": count, "table": "action_log"}

@router.delete("/security")
def delete_security_history(db: Session = Depends(get_db)):
    """Efface tout l'historique sécurité de la base PostgreSQL"""
    count = db.query(SecurityEvent).delete()
    db.commit()
    return {"status": "ok", "deleted": count, "table": "security_event"}

@router.delete("/all")
def delete_all_history(db: Session = Depends(get_db)):
    """Efface toutes les tables historique de la base PostgreSQL"""
    c1 = db.query(SensorData).delete()
    c2 = db.query(ActionLog).delete()
    c3 = db.query(SecurityEvent).delete()
    db.commit()
    return {
        "status": "ok",
        "deleted": {
            "sensor_data": c1,
            "action_log": c2,
            "security_event": c3,
        }
    }
